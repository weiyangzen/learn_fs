<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_conntrack_ipv6.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_conntrack_ipv6.h

## Purpose
`ipv6/nf_conntrack_ipv6.h` declares the IPv6 ICMPv6 conntrack L4 protocol tracker.

## Important APIs, types, and functions
It exposes `nf_conntrack_l4proto_icmpv6`.

## Control flow
Conntrack protocol registration uses this object to track ICMPv6 packets and embedded errors.

## State and persistence
No state is stored in the header.

## Dependencies and integration points
It depends on conntrack L4 protocol definitions through consumers. It integrates IPv6 ICMP tracking with conntrack.

## Risks and test signals
Risks are build/link mismatches and ICMPv6 error tuple handling in implementation. Tests should include IPv6 conntrack with echo and error packets.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_conntrack_ipv6.h` completely for this pass (7 lines, 202 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_conntrack_ipv6.h -->
