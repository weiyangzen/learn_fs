<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_reject.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_reject.h

## Purpose
`ipv4/nf_reject.h` declares IPv4 reject helpers for ICMP unreachable and TCP reset responses.

## Important APIs, types, and functions
It declares `nf_send_unreach`, `nf_send_reset`, `nf_reject_skb_v4_unreach`, and `nf_reject_skb_v4_tcp_reset`.

## Control flow
Netfilter reject expressions either send responses directly or build reject skbs for later emission based on hook, device, code, and original skb.

## State and persistence
No persistent state is defined; generated response skb state is transient.

## Dependencies and integration points
It depends on skb, IPv4, ICMP, and common nf_reject helpers. It integrates netfilter reject rules with IPv4 protocol response generation.

## Risks and test signals
Risks include malformed reset sequence/ack numbers, ICMP code selection, hook/device route context, fragmentation/DF handling, and responding to invalid packets. Tests should cover TCP reset, ICMP unreachable codes, local/forward hooks, invalid input packets, and namespace routing.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_reject.h` completely for this pass (23 lines, 792 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_reject.h -->
