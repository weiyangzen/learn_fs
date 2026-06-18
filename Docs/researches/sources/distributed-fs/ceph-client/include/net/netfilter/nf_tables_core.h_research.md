# sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_core.h

Purpose: Declares built-in nftables core expression and set implementations plus fast-path expression layouts and evaluator entry points.

Important APIs/types/functions: Extern expression types include immediate, cmp, counter, lookup, bitwise, byteorder, payload, dynset, range, meta, rt, exthdr, last, objref, inner, and optional secmark object. Fast private layouts include `nft_bitwise_fast_expr`, `nft_cmp_fast_expr`, `nft_cmp16_fast_expr`, `nft_immediate_expr`, `nft_ct`, and `nft_payload`. It declares built-in set types, lookup dispatchers, core module init/exit, evaluator functions, inner tunnel context, payload inner helpers, object reference evaluation, and `nft_dynset_new`.

Control flow: Core module registration installs common expressions and sets. Datapath evaluation calls the declared `*_eval` functions from expression ops, with optional retpoline mitigation wrappers selecting set lookup implementations.

State and persistence: State is expression-private data embedded in rules and set-private data owned by set implementations. Static keys gate counters and tracing.

Dependencies/integration: Depends on `nf_tables.h`, indirect-call wrappers, conntrack keys, payload/meta uapi keys, and set backend modules.

Risks/test signals: Test fast expression register sizes, payload offsets, retpoline lookup parity, static key enablement, inner tunnel offsets, and module init/exit registration symmetry.
