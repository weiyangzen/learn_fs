<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_icmpv6.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_icmpv6.c

## Purpose
Implements IPv6 ICMPv6 conntrack tuple handling, echo and node-information tracking, ICMPv6 error/redirect correlation, untracked handling for local control messages, and timeout/netlink support.

## Important APIs, Types, and Functions
Important functions are `icmpv6_pkt_to_tuple()`, `nf_conntrack_invert_icmpv6_tuple()`, `nf_conntrack_icmpv6_packet()`, `nf_conntrack_icmpv6_error()`, and `nf_conntrack_icmpv6_redirect()`. `nf_conntrack_l4proto_icmpv6` provides tuple netlink and timeout policy callbacks.

## Control Flow
New tracked ICMPv6 flows require echo request or NI query. The error path validates header length and checksum, marks selected neighbor discovery/MLD/router discovery control messages as `IP_CT_UNTRACKED`, handles redirects with hop-limit/link-local/options validation, and correlates true errors to embedded tuples using `nf_conntrack_inet_error()`.

## State and Persistence
Persistent state is the per-net ICMPv6 timeout. Packets can be explicitly marked untracked for control message types that should not create conntrack entries. No extra per-connection ICMPv6 private state is kept.

## Dependencies and Integration Points
Depends on IPv6/ICMPv6 headers, IPv6 checksum, neighbor discovery redirect structures, conntrack zones/core, netlink attributes, and timeout extension. Initialized from `nf_conntrack_proto_pernet_init()` and exposed through standalone sysctls.

## Risks
Redirect validation is subtle because only redirects with a redirect-header option should be correlated to an inner connection. Type index arithmetic subtracts 128 or 130 and must guard bounds. The descriptor uses timeout max constants that must match ICMPv6 userspace ABI expectations.

## Test Signals
Test echo/NI request flows, invalid new reply-only types, MLD/ND messages becoming untracked, bad checksum logs, valid and invalid redirects, related destination-unreachable/time-exceeded errors, and ctnetlink ICMPv6 tuple filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_icmpv6.c -->
