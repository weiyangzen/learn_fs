# sources/distributed-fs/ceph-client/net/netfilter/nft_cmp.c

## Purpose
`nft_cmp.c` implements the nftables `cmp` expression. It compares register data with immediate nft data using equality, inequality, and lexicographic ordering operations. It selects specialized fast expression layouts for common equality/inequality cases and provides hardware-offload translation into flow dissector key/mask matches.

## Important APIs, Types, and Functions
Full expression state is `struct nft_cmp_expr`; fast states are `struct nft_cmp_fast_expr` and `struct nft_cmp16_fast_expr`. Evaluation entry point is `nft_cmp_eval()`, while fast evaluators are inlined by `nf_tables_core.c`. Initialization/dump functions are `nft_cmp_init()`, `nft_cmp_fast_init()`, `nft_cmp16_fast_init()`, `nft_cmp_dump()`, `nft_cmp_fast_dump()`, and `nft_cmp16_fast_dump()`.

Offload helpers are `nft_payload_n2h()`, `__nft_cmp_offload()`, `nft_cmp_offload()`, `nft_cmp_fast_offload()`, and `nft_cmp16_fast_offload()`. Op selection is `nft_cmp_select_ops()`.

## Control Flow, State, and Persistence
Selection requires source register, operation, and data. It validates operation codes, parses the data once to discover length, and chooses the fast one-word op for EQ/NEQ up to u32, the 16-byte fast op for aligned eligible registers up to `struct nft_data`, or the generic op for ordering and other cases.

Generic evaluation uses `memcmp()` over `len` bytes and maps comparison result to nft semantics. Mismatches set `regs->verdict.code = NFT_BREAK`, causing the interpreter to skip the current rule. Fast initialization builds little-endian masks for partial u32 or 16-byte comparisons and records an inversion flag for NEQ. Dumps reconstruct the original netlink operation and immediate data.

Offload supports equality matches only. It locates the tracked offload register, optionally converts payload data and masks from network to host order, copies key/mask bytes into the flow rule at the recorded offset, marks the flow dissector key as used, rejects non-Ethernet ingress-iftype metadata, and updates dependency state for later payload/protocol checks.

Expression state persists in immutable rule private data. No dynamic resources are held after initialization.

## Dependencies and Integration Points
The expression depends on nft data parsing/dumping, register validation, core interpreter fast-op inlining, flow offload context register tracking, Linux flow dissector key layout, and payload/meta expressions that establish offload register offsets and masks.

## Risks and Test Signals
Risks include memcmp lexicographic ordering semantics, endian handling for partial masks, fast-op selection for aligned registers, offload accepting only equality, dependency propagation, and metadata iftype restrictions. Tests should cover all comparison operators, EQ/NEQ fast and generic paths, partial-length masks on big and little endian, 16-byte comparisons, dump round-trips, offload success after payload extraction, offload rejection for NEQ/range/unsupported metadata, and interpreter `NFT_BREAK` behavior on mismatch.
