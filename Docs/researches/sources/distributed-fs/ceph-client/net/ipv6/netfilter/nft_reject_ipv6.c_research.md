# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nft_reject_ipv6.c

Purpose: Registers the IPv6 nftables `reject` expression and maps nft reject actions to the IPv6 reject core.

Important APIs, types, and functions: `nft_reject_ipv6_eval()` dispatches based on `struct nft_reject` type. It calls `nf_send_unreach6()` for `NFT_REJECT_ICMP_UNREACH` and `nf_send_reset6()` for `NFT_REJECT_TCP_RST`. The expression type uses generic `nft_reject_init()`, `nft_reject_dump()`, and `nft_reject_validate()`.

Control flow: Module init registers the expression. On packet evaluation, the helper sends the appropriate reject packet when the type is supported, then always sets `regs->verdict.code = NF_DROP`. Unsupported types fall through to drop-only behavior. Module exit unregisters the expression.

State and persistence: Per-expression nft rule state stores reject type/code. No additional module state is kept.

Dependencies and integration: Depends on nftables expression APIs and `nf_reject_ipv6.c`. It integrates with nft chain hooks by using `nft_net()`, `nft_sk()`, `nft_hook()`, and the packet skb.

Risks and test signals: Risks are validation gaps for unsupported reject types, ensuring generated rejects are sent before drop, and correct hook/sk context. Tests should cover ICMPv6 unreachable codes, TCP reset from input/forward/local-output, invalid expression attributes, and packet drop verdict even when reject generation fails.
