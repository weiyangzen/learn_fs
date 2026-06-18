# sources/distributed-fs/ceph-client/net/netfilter/nft_bitwise.c

## Purpose
`nft_bitwise.c` implements the nftables `bitwise` expression. It transforms register data with mask/xor, left shift, right shift, and boolean AND/OR/XOR operations using either immediate data or a second source register. It also provides a compact one-word fast op and limited hardware-offload support for masks.

## Important APIs, Types, and Functions
The full expression state is `struct nft_bitwise`; the fast state is `struct nft_bitwise_fast_expr` from nftables core headers. Evaluation entry points are `nft_bitwise_eval()` and the inlined fast evaluator in `nf_tables_core.c`. Full-op helpers include `nft_bitwise_eval_mask_xor()`, `nft_bitwise_eval_lshift()`, `nft_bitwise_eval_rshift()`, `nft_bitwise_eval_and()`, `nft_bitwise_eval_or()`, and `nft_bitwise_eval_xor()`.

Initialization/dump paths are `nft_bitwise_init()`, `nft_bitwise_init_mask_xor()`, `nft_bitwise_init_shift()`, `nft_bitwise_init_bool()`, `nft_bitwise_dump()`, and fast variants. Operation selection is `nft_bitwise_select_ops()`.

## Control Flow, State, and Persistence
Select ops requires source, destination, and length. A four-byte mask/xor expression selects the fast op; other lengths or non-mask/xor ops use the full op. Initialization parses register load/store constraints and validates per-op attribute combinations: mask/xor requires mask and xor with no data or second source; shifts require immediate u32 shift between 1 and 31; boolean ops require exactly one immediate data operand or second source register.

Evaluation reads from the source register and writes to destination for `len` bytes rounded to u32 words. Shift operations propagate carry across u32 words. Boolean register operations use `sreg2` when provided; otherwise they use parsed immediate data. Offload is supported only for mask-only operations where xor is zero, source and destination are identical, and length matches the tracked offload register.

State persists only in expression private data inside nft rules. Parsed `nft_data` values are dumped back through netlink; mask/xor data are released on partial initialization errors.

## Dependencies and Integration Points
This file depends on nft register parsing, nft data parser/dumper, the core interpreter's inlined fast evaluator, and flow offload context register masks. It is registered as expression type `bitwise` by the nftables core module.

## Risks and Test Signals
Risks include shift carry behavior across partial lengths, endian expectations for u32-word operations, invalid attribute combinations, register overlap, missing data release on errors, and offload accepting only true masks. Tests should cover every op, immediate versus second-register boolean ops, one-byte/unaligned lengths, zero/32-bit shift rejection, fast-op selection and dump equivalence, invalid netlink attributes, and offload mask propagation/rejection.
