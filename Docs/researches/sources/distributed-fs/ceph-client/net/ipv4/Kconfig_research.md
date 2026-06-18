# sources/distributed-fs/ceph-client/net/ipv4/Kconfig

## Purpose
`net/ipv4/Kconfig` defines build-time feature selection for the IPv4 networking stack, including multicast/routing, tunnels, IPsec transforms, diagnostics, TCP congestion control algorithms, and TCP authentication/signature support.

## Important APIs, types, and functions
Major symbols include `IP_MULTICAST`, `IP_ADVANCED_ROUTER`, `IP_MULTIPLE_TABLES`, `IP_ROUTE_MULTIPATH`, `IP_PNP` and its DHCP/BOOTP/RARP suboptions, `NET_IPIP`, `NET_IPGRE_DEMUX`, `NET_IP_TUNNEL`, `NET_IPGRE`, `IP_MROUTE`, `SYN_COOKIES`, `NET_IPVTI`, `NET_UDP_TUNNEL`, `NET_FOU`, `INET_AH`, `INET_ESP`, `INET_ESP_OFFLOAD`, `INET_ESPINTCP`, `INET_IPCOMP`, `INET_DIAG` and protocol-specific diag symbols, `TCP_CONG_ADVANCED` with many congestion-control algorithms, `DEFAULT_TCP_CONG`, `TCP_AO`, and `TCP_MD5SIG`.

## Control flow
Kconfig dependency and selection rules determine which source files are compiled by `net/ipv4/Makefile` and which runtime features exist. The congestion-control section either presents an advanced menu with multiple algorithms and a default-choice block, or defaults to CUBIC when advanced selection is disabled. IPsec and tunnel symbols select shared XFRM/tunnel support needed by their implementations.

## State and persistence
The durable output is `.config` state and generated `CONFIG_*` macros. Runtime defaults such as selected TCP congestion control are derived from these values but are not stored here directly.

## Dependencies and integration points
The file integrates with the IPv4 Makefile, crypto/XFRM subsystems, FIB rules, proc/sysctl features, socket diagnostic tooling, tunnel drivers, TCP congestion-control modules, and documentation referenced by help text.

## Risks and invariants
Dependency drift can create build failures or unusable configs, especially around IPsec symbols that require XFRM/crypto support and BPF TCP congestion control that is additionally gated by the Makefile on `CONFIG_BPF_JIT`. Duplicate `TCP_CONG_CUBIC` definitions intentionally cover advanced and non-advanced modes; changes must preserve default selection semantics. Security-sensitive options such as SYN cookies, TCP-AO, and TCP-MD5 have operational tradeoffs that are documented in help text.

## Test signals
Useful signals include `allnoconfig`, `defconfig`, and targeted configs for IPsec, tunnels, diagnostics, and each congestion-control algorithm. Verify `DEFAULT_TCP_CONG` strings match selected choices and that Kconfig dependencies pull required support without unexpected symbols.
