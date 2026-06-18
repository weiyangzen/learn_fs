# sources/distributed-fs/ceph-client/net/netfilter/nft_fib_netdev.c

Purpose: registers the netdev-family `fib` expression and dispatches routing lookups based on the skb Ethernet protocol.

Important APIs/types/functions: `nft_fib_netdev_eval()` switches on `ntohs(pkt->skb->protocol)` for `ETH_P_IP` and `ETH_P_IPV6`, checks `ipv6_mod_enabled()` for IPv6, and calls the same IPv4/IPv6 backend functions used by inet. Ops reuse `nft_fib_init()`, `nft_fib_dump()`, and `nft_fib_validate()`.

Control flow: module init registers `nft_fib_netdev_type` for `NFPROTO_NETDEV`. Eval handles IPv4 and enabled IPv6; unsupported protocols or disabled IPv6 set `NFT_BREAK`, allowing rule traversal to stop without forcing a drop. Result dispatch mirrors inet: oif/oifname versus addrtype.

State/persistence: no dynamic state beyond `struct nft_fib` expression data. Dependencies include netdev hooks, IPv6 module state, shared FIB helpers, and skb protocol classification. Risks include protocol parsing after VLAN/encapsulation if packet info was not normalized, result semantics differing from inet on unsupported protocols (`NFT_BREAK` vs drop), and hook validation inherited from generic helpers. Test signals: netdev ingress/egress rules for IPv4, IPv6 enabled/disabled, non-IP frames, all result types, present flag behavior, and module unload cleanup.
