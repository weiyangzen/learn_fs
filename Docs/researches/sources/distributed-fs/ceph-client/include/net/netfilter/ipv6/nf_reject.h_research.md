<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_reject.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_reject.h

## Purpose
`ipv6/nf_reject.h` declares IPv6 reject helpers for ICMPv6 unreachable and TCP reset responses.

## Important APIs, types, and functions
It declares `nf_send_unreach6`, `nf_send_reset6`, `nf_reject_skb_v6_tcp_reset`, and `nf_reject_skb_v6_unreach`.

## Control flow
Reject rules call these helpers to generate immediate responses or response skbs based on original packet, device, hook, and ICMPv6 code.

## State and persistence
No persistent state is stored.

## Dependencies and integration points
It depends on ICMPv6 and common nf_reject logic. It integrates IPv6 netfilter reject expressions with protocol-compliant error generation.

## Risks and test signals
Risks include extension-header parsing, reset sequence correctness, ICMPv6 rate/eligibility rules, hook routing context, and namespace handling. Tests should cover TCP reset, unreachable codes, extension headers, multicast/non-unicast suppression, and local/forward paths.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_reject.h` completely for this pass (21 lines, 696 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_reject.h -->
