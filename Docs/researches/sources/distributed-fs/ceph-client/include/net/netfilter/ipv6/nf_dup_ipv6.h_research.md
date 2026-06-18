<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_dup_ipv6.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_dup_ipv6.h

## Purpose
`ipv6/nf_dup_ipv6.h` declares the IPv6 packet duplication helper used by netfilter dup actions.

## Important APIs, types, and functions
It declares `nf_dup_ipv6(struct net *, struct sk_buff *, unsigned int hooknum, const struct in6_addr *gw, int oif)`.

## Control flow
Netfilter rules call the helper to route and transmit a duplicate IPv6 skb toward an optional gateway/output interface.

## State and persistence
No persistent state is defined.

## Dependencies and integration points
It depends on skb and IPv6 address declarations. It integrates nftables/iptables dup semantics with IPv6 routing.

## Risks and test signals
Risks include recursion, scope/oif selection, route failures, and skb ownership. Tests should cover link-local/global gateways, hook contexts, and oif-only duplication.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_dup_ipv6.h` completely for this pass (10 lines, 262 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_dup_ipv6.h -->
