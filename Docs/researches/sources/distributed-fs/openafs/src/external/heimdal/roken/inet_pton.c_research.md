# sources/distributed-fs/openafs/src/external/heimdal/roken/inet_pton.c

Purpose: fallback implementation of `inet_pton()`.

Important APIs/types/functions: `inet_pton(int af, const char *src, void *dst)`.

Control flow: on Winsock, duplicates the input string, dispatches to `WSAStringToAddress()` for IPv4 or IPv6, copies parsed address bytes, maps invalid input to 0 and other errors to -1 with errno. On non-Winsock fallback, only `AF_INET` is supported and delegated to `inet_aton()`.

State and persistence behavior: writes parsed address bytes to caller storage; temporary duplicated string is freed.

Dependencies and integration points: companion to fallback address-resolution code. Uses Winsock APIs on Windows and `inet_aton()` elsewhere.

Risks: non-Windows fallback lacks IPv6 parsing even if other code has IPv6 conditionals, so configure selection must avoid this fallback where IPv6 is needed. Windows path returns 0 for allocation failure after setting ENOMEM, which differs from usual -1 error semantics.

Test signals: valid/invalid IPv4, valid/invalid IPv6 on Winsock, unsupported family, null source, and errno mapping.
