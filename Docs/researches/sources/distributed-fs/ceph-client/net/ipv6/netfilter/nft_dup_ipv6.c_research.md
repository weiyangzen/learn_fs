# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nft_dup_ipv6.c

Purpose: Registers the IPv6 nftables `dup` expression. The expression duplicates packets to an IPv6 gateway and optional output interface by calling the shared `nf_dup_ipv6()` helper.

Important APIs, types, and functions: `struct nft_dup_ipv6` stores source register numbers for the gateway address and optional device index. `nft_dup_ipv6_eval()` reads registers and invokes `nf_dup_ipv6()`. `nft_dup_ipv6_init()` validates and parses register loads. `nft_dup_ipv6_dump()` serializes expression state. `nft_dup_ipv6_type` registers family `NFPROTO_IPV6`, name `dup`, and netlink policy.

Control flow: Module init registers the expression type. Rule creation requires `NFTA_DUP_SREG_ADDR`; optional `NFTA_DUP_SREG_DEV` is parsed as an integer register. Packet evaluation casts register data to `struct in6_addr`, reads optional oif or `-1`, and duplicates the packet without setting a verdict. Module exit unregisters the expression.

State and persistence: Per-expression state is only the register selectors stored in nftables rule memory. Runtime packet copies are handled by `nf_dup_ipv6()`.

Dependencies and integration: Depends on nftables expression APIs, netlink register encoding, and `nf_dup_ipv6`. Integrates with nft rulesets and uses nft packet info for net namespace and hook number.

Risks and test signals: Risks are register size/type validation, endian/interface index interpretation, and propagation of duplication errors that are intentionally not reflected in verdict. Tests should create rules with/without device register, invalid netlink attributes, link-local gateways requiring oif, and verify original packet verdict flow continues.
