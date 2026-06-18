# sources/distributed-fs/openafs/src/WINNT/afsreg/syscfg.c

## Purpose
Retrieves IPv4 interface configuration for OpenAFS on Windows: addresses, subnet masks, MTUs, and flags. It supports modern `GetAdaptersAddresses`/`GetIpAddrTable` discovery and a fallback path for older Windows 2000-style registry layout.

## Important APIs, Types, And Functions
Public APIs are `syscfg_GetIFInfo` and fallback `syscfg_GetIFInfo_2000`. Private helpers include `GetMTUForAddress`, `IsLoopback`, `GetInterfaceList`, `GetNextInterface`, and `GetIP`. `syscfg_GetIFInfo` dynamically loads `iphlpapi` and resolves `GetAdaptersAddresses`, while still using `GetIpAddrTable` to map adapter indexes to IPv4 addresses and masks.

## Control Flow
The modern path probes `GetIpAddrTable` for size, reads the IP address table, probes `GetAdaptersAddresses` for size, reads adapter data, skips software loopback and down interfaces, performs an additional registry-based loopback check, then matches IP table entries by interface index. For each accepted entry it stores host-order address/mask, MTU as the minimum of adapter MTU and registry MTU, and flags as zero until the caller-provided capacity is reached; the return value still counts configured entries. If `GetAdaptersAddresses` is unavailable, `syscfg_GetIFInfo_2000` opens the TCP/IP services key, reads the `Tcpip\Linkage\Bind` multistring, iterates adapter names, filters loopback devices, reads static or DHCP IP/mask values, and assigns default MTU 1500.

## State And Persistence
The module only reads state: IP helper API data plus registry keys under `SYSTEM\CurrentControlSet\Services`, adapter `IpConfig`, interface `MTU`, TCP/IP `Bind`, DHCP/static address values, and network adapter enum data used to identify Microsoft loopback adapters. It fills caller-owned arrays and updates `*count` to the number of returned entries.

## Dependencies And Integration Points
It depends on WinSock/IP Helper APIs, registry helpers from `afsreg.c`, TCP/IP key constants from `afsreg.h`, and `syscfg.h`. It is a system configuration provider for network-address initialization in OpenAFS networking code and has a test utility in `test/getifinfo.c`.

## Risks And Test Signals
Risks include manual memory management around multi-pass IP helper calls, handling systems with no addresses, registry MTU fallback value `0xFFFFFFFF`, old registry schemas, fixed default MTU in the fallback path, and `GetNextInterface` pointer arithmetic over multistrings. Modern and fallback paths should be tested on hosts with multiple NICs, DHCP/static addresses, down interfaces, loopback adapters, nondefault MTUs, and caller arrays smaller than the interface count.
