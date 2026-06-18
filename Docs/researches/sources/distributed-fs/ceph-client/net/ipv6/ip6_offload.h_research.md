# sources/distributed-fs/ceph-client/net/ipv6/ip6_offload.h

Purpose: declares IPv6 offload initialization/exit hooks shared by the IPv6 offload compilation units.

Important APIs, types, and functions: declares `ipv6_exthdrs_offload_init()`, `udpv6_offload_init()`, `udpv6_offload_exit()`, and `tcpv6_offload_init()`.

Control flow: no runtime control flow is implemented here. The header is included by `ip6_offload.c`, which calls TCP and extension-header initialization during `fs_initcall`.

State and persistence: none.

Dependencies and integration points: bridges `ip6_offload.c` with TCPv6, UDPv6, and extension-header offload implementation files. Include guards prevent repeated declarations.

Risks: declarations must match implementations exactly, especially return type for `udpv6_offload_exit()` which is declared `int`. Missing declarations for exit paths can hide unregister asymmetry in module or init error handling.

Test signals: compile coverage with IPv6 offload enabled, symbol mismatch checks, and init/exit path coverage for UDP/TCP/extension-header offloads.
