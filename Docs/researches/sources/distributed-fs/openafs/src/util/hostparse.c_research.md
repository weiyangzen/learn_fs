# sources/distributed-fs/openafs/src/util/hostparse.c

Purpose: Provides host/address parsing utilities, reverse lookup formatting, dotted-quad extraction, and temporary-directory discovery.

Important APIs: `hostutil_GetHostByName()` accepts names and numeric dotted IPv4 strings. `hostutil_GetNameByINet()` returns a static hostname or dotted address. `extractAddr()` parses a dotted IPv4 address from a line and returns network byte order or invalid sentinel values. `afs_inet_ntoa_r()` formats an address into caller storage. `gettmpdir()` returns a persistent temp directory string.

Control flow and state: Numeric hostname parsing builds a fake static `hostent` backed by static address storage. Non-numeric lookup calls `gethostbyname()` after Winsock init on Windows. `extractAddr()` tokenizes each byte field manually, validates digit-only fields, and uses `strtol()` before composing with `htonl()`. Windows `gettmpdir()` lazily allocates a directory string and publishes it with `InterlockedCompareExchangePointer`.

Dependencies and integration: Depends on roken, AFS integer types, Winsock init on Windows, and `FilepathNormalize()` for temp paths. Used by network config parsing and address display.

Risks and test signals: Several APIs return static storage and are not reentrant. `hostutil_GetHostByName()` does not check numeric octets are <= 255 before storing in `char`. `extractAddr()` similarly composes parsed byte values without upper-bound checks. Tests are indirect through NetInfo/NetRestrict parsing and host display behavior.
