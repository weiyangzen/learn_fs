<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ndisc.h -->
# sources/distributed-fs/ceph-client/include/net/ndisc.h

## Purpose
`ndisc.h` defines IPv6 Neighbor Discovery message layouts, option parsing hooks, link-layer address option helpers, neighbour lookup helpers, multicast mapping, send/update entry points, and MLD/IGMP6 lifecycle declarations.

## Important APIs, types, and functions
Important types are ND/RS/RA/RD message structs, `struct nd_opt_hdr`, `struct ndisc_options`, and `struct ndisc_ops`. Inline helpers dispatch device-specific `ndisc_ops`, compute option padding/space, extract LL address data, hash IPv6 neighbour keys, look up/confirm/create neighbours, and compute gateway neighbours. Declarations cover NDISC init/cleanup, receive, NS/NA/RS/redirect send, multicast mapping, and update paths.

## Control flow
Receive code parses options into `ndisc_options`, allows device-specific option parsers such as 6LoWPAN, updates neighbour cache entries, and handles router/prefix information. Send paths calculate link-layer option space, fill optional device data, and emit ICMPv6 NDISC packets. Lookup helpers use the global IPv6 neighbour table under RCU and refcount neighbours only when requested.

## State and persistence
State lives in the global `nd_tbl`, per-device `ndisc_ops`, neighbour entries, IPv6 device config, and parsed skb option structures. The header defines no persistent state of its own.

## Dependencies and integration points
It depends on IPv6, ICMPv6, netdevice, neighbour core, hashing, sysctl, and optional 802.15.4 6LoWPAN support. It integrates IPv6 neighbour discovery, SLAAC prefix processing, and link-layer-specific address option behavior.

## Risks and test signals
Risks include option length and padding bugs, device ops changing decisions between space calculation and fill, RCU/refcount misuse in no-ref lookup helpers, creating neighbours from fast paths, IPv6-disabled stub behavior, and hash collision assumptions. Tests should cover option parsing, InfiniBand padding, 6LoWPAN options, redirect option data, neighbour lookup/create/confirm, truncated packets, and sysctl change notifications.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/ndisc.h` completely for this pass (454 lines, 13796 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ndisc.h -->
