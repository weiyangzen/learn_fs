<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_dup_ipv4.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_dup_ipv4.h

## Purpose
`ipv4/nf_dup_ipv4.h` declares the IPv4 packet duplication helper used by nftables/iptables dup actions.

## Important APIs, types, and functions
It declares `nf_dup_ipv4(struct net *, struct sk_buff *, unsigned int hooknum, const struct in_addr *gw, int oif)`.

## Control flow
Rules call the helper with a cloned or owned skb, hook number, optional gateway, and output interface; the implementation routes and emits the duplicate.

## State and persistence
The header has no state. Packet clone/routing state is transient in skb and route lookup.

## Dependencies and integration points
It depends on skb and IPv4 address UAPI. It integrates netfilter rule actions with IPv4 output.

## Risks and test signals
Risks include recursion, wrong hook context, route/oif lookup failures, and skb ownership confusion. Tests should duplicate packets from each relevant hook, with and without gateway/oif.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_dup_ipv4.h` completely for this pass (11 lines, 288 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_dup_ipv4.h -->
