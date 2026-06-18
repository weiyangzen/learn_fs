# sources/distributed-fs/ceph-client/net/ipv6/exthdrs_offload.c

## Purpose
Registers IPv6 routing, destination-options, and hop-by-hop extension headers with the IPv6 offload table so GSO/GRO code recognizes them as extension headers during segmentation processing.

## Important APIs, Types, and Functions
Defines three `struct net_offload` instances, `rthdr_offload`, `dstopt_offload`, and `hbh_offload`, all with `INET6_PROTO_GSO_EXTHDR`. The sole function is `ipv6_exthdrs_offload_init()`, which registers offloads for `IPPROTO_ROUTING`, `IPPROTO_DSTOPTS`, and `IPPROTO_HOPOPTS`.

## Control Flow
Initialization registers routing-header offload first, destination-options second, and hop-by-hop third. On failure, it unwinds already registered entries in reverse dependency order and returns the registration error. There is no explicit exit function in this file; it is part of the IPv6 offload initialization lifecycle.

## State and Persistence
State is limited to entries installed in the global IPv6 offload registry. No per-packet or persistent storage is created here.

## Dependencies and Integration Points
Depends on `inet6_add_offload()`, `inet6_del_offload()`, `net/protocol.h`, and local `ip6_offload.h`. It integrates indirectly with transport GSO/GRO and XFRM offload paths that must step across IPv6 extension headers.

## Risks and Test Signals
Risks are mostly registration-order and cleanup bugs; missing registration would make segmentation treat extension headers incorrectly. Test signals include GSO packets carrying hop-by-hop, destination, and routing headers, module/init failure injection around each registration step, and offload table inspection through packet behavior.
