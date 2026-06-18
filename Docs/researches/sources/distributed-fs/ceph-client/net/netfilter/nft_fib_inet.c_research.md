# sources/distributed-fs/ceph-client/net/netfilter/nft_fib_inet.c

Purpose: registers the inet-family `fib` expression and dispatches runtime evaluation to IPv4 or IPv6 FIB helpers based on packet family.

Important APIs/types/functions: `nft_fib_inet_eval()` inspects `nft_pf(pkt)` and `priv->result`, then calls `nft_fib4_eval()`, `nft_fib4_eval_type()`, `nft_fib6_eval()`, or `nft_fib6_eval_type()`. The expression ops reuse shared `nft_fib_init()`, `nft_fib_dump()`, and `nft_fib_validate()`.

Control flow: module init registers `nft_fib_inet_type` for `NFPROTO_INET`. Eval only handles `NFPROTO_IPV4` and `NFPROTO_IPV6`; unknown packet families set verdict `NF_DROP`. Result dispatch separates output-interface/name lookups from address-type lookups.

State/persistence: state is the shared `struct nft_fib`; no inet-specific allocation. Dependencies are the generic `nft_fib.c` helpers and IPv4/IPv6 backend modules. Risks include dropping packets with unexpected family instead of breaking, backend availability/config differences, and result enum drift between generic init and dispatch. Test signals: inet table rules matching IPv4 and IPv6 traffic, addrtype vs oif/oifname results, unknown family behavior, module registration, and validation inherited from generic FIB helpers.
