from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_hex
from datetime import datetime, timezone
from colorama import *
import asyncio, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class GPU:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://token.gpu.net",
            "Refrer": "https://token.gpu.net",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://quest-api.gpu.net/api"
        self.ref_code = "4LGEHS" # U can change it with yours.
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}GPU.net - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def generate_address(self, private_key: str):
        try:
            account = Account.from_key(private_key)
            address = account.address
            
            return address
        except Exception as e:
            return None
    
    def generate_payload(self, account: str, address: str, nonce: int):
        try:
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            message = f"token.gpu.net wants you to sign in with your Ethereum account:\n{address}\n\nSign in with Ethereum to the app.\n\nURI: https://token.gpu.net\nVersion: 1\nChain ID: 4048\nNonce: {nonce}\nIssued At: {timestamp}"
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)

            data = {
                "message":message,
                "signature":signature,
                "referralCode": self.ref_code
            }

            return data
        except Exception as e:
            return None
    
    def extract_cookies(self, raw_cookies: list):
        cookies_dict = {}
        try:
            skip_keys = ['expires', 'path', 'domain', 'samesite', 'secure', 'httponly', 'max-age']

            for cookie_str in raw_cookies:
                cookie_parts = cookie_str.split(';')

                for part in cookie_parts:
                    cookie = part.strip()

                    if '=' in cookie:
                        name, value = cookie.split('=', 1)

                        if name and value and name.lower() not in skip_keys:
                            cookies_dict[name] = value

            cookie_header = "; ".join([f"{key}={value}" for key, value in cookies_dict.items()])
            
            return cookie_header
        except Exception as e:
            return None
    
    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Monosans Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def check_connection(self, proxy=None):
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url="https://token.gpu.net", headers={}) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            return None
        
    async def generate_nonce(self, proxy=None, retries=5):
        url = f"{self.BASE_API}/auth/eth/nonce"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=self.headers) as response:
                        response.raise_for_status()
                        result = await response.text()

                        raw_cookies = response.headers.getall('Set-Cookie', [])
                        if raw_cookies:
                            cookie_header = self.extract_cookies(raw_cookies)

                            if cookie_header:
                                return result, cookie_header
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None, None

    async def user_verify(self, account: str, address: str, nonce: str, nonce_cookie: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/auth/eth/verify"
        data = json.dumps(self.generate_payload(account, address, nonce))
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Cookie": nonce_cookie
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()

                        raw_cookies = response.headers.getall('Set-Cookie', [])
                        if raw_cookies:
                            cookie_header = self.extract_cookies(raw_cookies)

                            if cookie_header:
                                return cookie_header
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def user_exp(self, token_cookie: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/users/exp"
        headers = {
            **self.headers,
            "Cookie": token_cookie
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.text()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def streak_info(self, token_cookie: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/users/streak"
        headers = {
            **self.headers,
            "Cookie": token_cookie
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def perform_streak(self, token_cookie: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/users/streak"
        headers = {
            **self.headers,
            "Content-Length": "0",
            "Cookie": token_cookie
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return True
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def task_lists(self, token_cookie: str, category: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/users/{category}/tasks"
        headers = {
            **self.headers,
            "Cookie": token_cookie
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def verify_tasks(self, token_cookie: str, category: str, task_id: int, proxy=None, retries=5):
        url = f"{self.BASE_API}/users/{category}/tasks/{str(task_id)}/verify"
        headers = {
            **self.headers,
            "Cookie": token_cookie
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def verify_intro_tasks(self, token_cookie: str, task_id: int, proxy=None, retries=5):
        url = f"{self.BASE_API}/users/gpunet/tasks/{str(task_id)}/verify"
        headers = {
            **self.headers,
            "Content-Length": "0",
            "Cookie": token_cookie
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def claim_multiplier(self, token_cookie: str, category: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/users/quests/{category}/multiplexer"
        headers = {
            **self.headers,
            "Cookie": token_cookie
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None

    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        message = "Checking Connection, Wait..."
        if use_proxy:
            message = "Checking Proxy Connection, Wait..."

        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT}{message}{Style.RESET_ALL}",
            end="\r",
            flush=True
        )

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if rotate_proxy:
            is_valid = None
            while is_valid is None:
                is_valid = await self.check_connection(proxy)
                if not is_valid:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Not 200 OK, {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Rotating Proxy...{Style.RESET_ALL}"
                    )
                    proxy = self.rotate_proxy_for_account(address) if use_proxy else None
                    await asyncio.sleep(5)
                    continue

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} 200 OK {Style.RESET_ALL}                  "
                )

                return True

        is_valid = await self.check_connection(proxy)
        if not is_valid:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Not 200 OK {Style.RESET_ALL}          "
            )
            return False
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} 200 OK {Style.RESET_ALL}                  "
        )

        return True
    
    async def process_generate_nonce(self, address: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        nonce, nonce_cookie = await self.generate_nonce(proxy)
        if not nonce or not nonce_cookie:
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} GET Nonce Failed {Style.RESET_ALL}"
            )
            return None

        return nonce, nonce_cookie
        
    async def process_user_verify(self, account: str, address: str, use_proxy: bool):
        nonce, nonce_cookie = await self.process_generate_nonce(address, use_proxy)
        if nonce and nonce_cookie:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            
            token_cookie = await self.user_verify(account, address, nonce, nonce_cookie, proxy)
            if not token_cookie:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                )
                return None

            return token_cookie
            
    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            token_cookie = await self.process_user_verify(account, address, use_proxy)
            if token_cookie:
                proxy = self.get_next_proxy_for_account(address) if use_proxy else None
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT} Login Success {Style.RESET_ALL}"
                )

                balance = "N/A"

                points = await self.user_exp(token_cookie, proxy)
                if points:
                    balance = points.strip('"')

                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Balance   :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {balance} GXP {Style.RESET_ALL}"
                )


                streak = await self.streak_info(token_cookie, proxy)
                if streak:
                    last_perform = streak.get("lastVisitDate")

                    now = int(datetime.now(timezone.utc).timestamp())
                    next_perform = int(datetime.fromisoformat(last_perform.replace("Z", "+00:00")).timestamp()) + 86400

                    if now >= next_perform:
                        perform = await self.perform_streak(token_cookie, proxy)
                        if perform:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Say GM    :{Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT} Success {Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Say GM    :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Failed {Style.RESET_ALL}"
                            )
                    else:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}Say GM    :{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} Already Performed {Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Say GM    :{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} GET Data Failed {Style.RESET_ALL}"
                    )

                self.log(f"{Fore.CYAN + Style.BRIGHT}Task Lists:{Style.RESET_ALL}")
                
                displayed = "Unknown"
                for category in ["social", "gpunet", "onchain", "dev", "partner", "solana", "twitter", "dapp"]:
                    if category == "social":
                        displayed = "Social"
                    elif category == "Gpunet":
                        displayed = "Intro GPU.net"
                    elif category == "onchain":
                        displayed = "Onchain"
                    elif category == "dev":
                        displayed = "Dev"
                    elif category == "partner":
                        displayed = "Partner"
                    elif category == "solana":
                        displayed = "Solana"
                    elif category == "twitter":
                        displayed = "Twitter"
                    elif category == "dapp":
                        displayed = "Dapp"

                    tasks = await self.task_lists(token_cookie, category, proxy)
                    if tasks:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT} ● {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}{displayed}{Style.RESET_ALL}"
                        )
                        for task in tasks:
                            if task:
                                task_id = task["id"]
                                title = task["name"]
                                reward = task["experience"]
                                is_completed = task["completed"]

                                if is_completed:
                                    self.log(
                                        f"{Fore.CYAN + Style.BRIGHT}    >{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {title} {Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT}Already Completed{Style.RESET_ALL}"
                                    )
                                    continue
                                
                                if category in ["social", "onchain", "dev", "partner", "solana", "twitter", "dapp"]:
                                    verify = await self.verify_tasks(token_cookie, category, task_id, proxy)
                                    if verify and verify.get("message") == "Task verified":
                                        self.log(
                                            f"{Fore.CYAN + Style.BRIGHT}    >{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} {title} {Style.RESET_ALL}"
                                            f"{Fore.GREEN + Style.BRIGHT}Is Completed{Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT}Reward{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} {reward} GXP {Style.RESET_ALL}"
                                        )
                                    else:
                                        self.log(
                                            f"{Fore.CYAN + Style.BRIGHT}    >{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} {title} {Style.RESET_ALL}"
                                            f"{Fore.RED + Style.BRIGHT}Not Completed{Style.RESET_ALL}"
                                        )
                                elif category == "gpunet":
                                    verify = await self.verify_intro_tasks(token_cookie, task_id, proxy)
                                    if verify and verify.get("message") == "Task verified":
                                        self.log(
                                            f"{Fore.CYAN + Style.BRIGHT}    >{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} {title} {Style.RESET_ALL}"
                                            f"{Fore.GREEN + Style.BRIGHT}Is Completed{Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT}Reward{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} {reward} GXP {Style.RESET_ALL}"
                                        )
                                    else:
                                        self.log(
                                            f"{Fore.CYAN + Style.BRIGHT}    >{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} {title} {Style.RESET_ALL}"
                                            f"{Fore.RED + Style.BRIGHT}Not Completed{Style.RESET_ALL}"
                                        )

                        if category == "social":
                            claim_multiplier = await self.claim_multiplier(token_cookie, category, proxy)
                            if claim_multiplier and claim_multiplier.get("message") == "Multiplexer bonus awarded":
                                self.log(
                                    f"{Fore.CYAN + Style.BRIGHT}    >{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {displayed} Multiplier {Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT}Is Claimed{Style.RESET_ALL}"
                                )
                            elif claim_multiplier and claim_multiplier.get("message") == "Not all tasks completed":
                                self.log(
                                    f"{Fore.CYAN + Style.BRIGHT}    >{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {displayed} Multiplier {Style.RESET_ALL}"
                                    f"{Fore.YELLOW + Style.BRIGHT}Not Eligible{Style.RESET_ALL}"
                                )
                            elif claim_multiplier and claim_multiplier.get("message") == "Multiplexer bonus already awarded for this quest type":
                                self.log(
                                    f"{Fore.CYAN + Style.BRIGHT}    >{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {displayed} Multiplier {Style.RESET_ALL}"
                                    f"{Fore.YELLOW + Style.BRIGHT}Already Claimed{Style.RESET_ALL}"
                                )
                            else:
                                self.log(
                                    f"{Fore.CYAN + Style.BRIGHT}    >{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {displayed} Multiplier {Style.RESET_ALL}"
                                    f"{Fore.RED + Style.BRIGHT}Not Claimed{Style.RESET_ALL}"
                                )

                    else:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT} ● {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}{displayed}{Style.RESET_ALL}"
                        )

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            use_proxy_choice, rotate_proxy = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)

                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )
                        await self.process_accounts(account, address, use_proxy, rotate_proxy)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                
                delay = 12 * 60 * 60
                while delay > 0:
                    formatted_time = self.format_seconds(delay)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)
                    delay -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = GPU()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] GPU.net - BOT{Style.RESET_ALL}                                       "                              
        )