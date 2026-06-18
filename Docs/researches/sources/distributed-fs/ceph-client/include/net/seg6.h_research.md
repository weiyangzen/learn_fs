# sources/distributed-fs/ceph-client/include/net/seg6.h

## Purpose
This header declares core IPv6 Segment Routing (SRv6) helpers, per-net state, checksum adjustment helpers, initialization hooks, SRH validation/extraction, encapsulation/inline insertion, ICMP handling, and nexthop lookup.

## Important APIs, Types, And Functions
`update_csum_diff4()` and `update_csum_diff16()` update skb checksums after 32-bit or IPv6-address changes. `struct seg6_pernet_data` stores the per-net lock, RCU tunnel source address, and optional HMAC rhashtable. `seg6_pernet()` fetches per-net SR data when IPv6 is enabled. Init/exit functions cover core, lwtunnel, and local actions with stubs when disabled. Runtime APIs include `seg6_validate_srh()`, `seg6_get_srh()`, `seg6_icmp_srh()`, `seg6_do_srh_encap()`, `seg6_do_srh_inline()`, `seg6_lookup_nexthop()`, and `seg6_get_daddr()`.

## Control Flow
SRv6 tunnel/local code validates or locates SRHs, updates headers/checksums during inline or encapsulation operations, and resolves next hops. ICMP paths can recover the true destination from an SRH via skb IPv6 control block flags.

## State And Persistence
Per-net SRv6 state persists in `net->ipv6.seg6_data`, with tunnel source protected by RCU and configuration updates serialized by a mutex.

## Dependencies And Integration Points
It integrates with IPv6, lightweight tunnels, SRH UAPI, rhashtable HMAC storage, sk_buffs, and routing lookups.

## Risks And Test Signals
Risks include malformed SRH parsing, checksum update errors, RCU tunnel-source lifetime, feature-stub mismatches, and ICMP destination confusion. Test signals include SRH validation, lwtunnel encapsulation/inline routes, HMAC-enabled configs, ICMP errors containing SRH, and IPv6-disabled builds.
