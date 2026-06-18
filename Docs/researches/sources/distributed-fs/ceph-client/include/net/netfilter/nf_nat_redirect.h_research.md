# sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat_redirect.h

Purpose: Declares redirect NAT helpers for translating traffic to local addresses in IPv4 and IPv6.

Important APIs/types/functions: `nf_nat_redirect_ipv4(struct sk_buff *skb, const struct nf_nat_range2 *range, unsigned int hooknum)` and `nf_nat_redirect_ipv6(struct sk_buff *skb, const struct nf_nat_range2 *range, unsigned int hooknum)`.

Control flow: REDIRECT rules pass packet context and the user range to these helpers; implementations choose the local target address based on hook and family and then delegate to NAT setup/manipulation.

State and persistence: Redirect state is per conntrack through the normal NAT extension. No independent persistent state is declared here.

Dependencies/integration: Depends on skbuffs, uapi NAT ranges, IPv4/IPv6 local address selection, and core NAT setup.

Risks/test signals: Test local output vs prerouting hook behavior, loopback/local address selection, port range handling, IPv6 enabled/disabled builds, and interaction with conntrack zones.
