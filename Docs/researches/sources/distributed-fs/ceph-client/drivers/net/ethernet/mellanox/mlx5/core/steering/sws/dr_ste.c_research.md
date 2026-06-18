# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste.c

## Purpose
`dr_ste.c` provides format-independent STE and hash-table services: hash-index calculation, STE address helpers, miss-list deletion behavior, hash table allocation/free, action wrapper calls, match-parameter parsing, prechecks, generic STE-array construction, and dispatch to version-specific STE contexts.

## Important APIs, Types, And Functions
Important exported functions include `mlx5dr_ste_calc_hash_index()`, `mlx5dr_ste_conv_bit_to_byte_mask()`, `mlx5dr_ste_set_bit_mask()`, `mlx5dr_ste_get_icm_addr()`, `mlx5dr_ste_get_mr_addr()`, `mlx5dr_ste_get_hw_ste()`, `mlx5dr_ste_get_miss_list()`, `mlx5dr_ste_free()`, `mlx5dr_ste_htbl_alloc()`, `mlx5dr_ste_htbl_free()`, `mlx5dr_ste_create_next_htbl()`, `mlx5dr_ste_htbl_init_and_postsend()`, `mlx5dr_ste_copy_param()`, `mlx5dr_ste_build_ste_arr()`, and `mlx5dr_ste_get_ctx()`. It also exposes wrapper builders such as `mlx5dr_ste_build_eth_l2_src_dst()` and `mlx5dr_ste_build_tnl_gtpu_flex_parser_0()`.

## Control Flow
Matcher creation calls wrapper builders, which set `rx`, `inner`, capabilities/domain fields, then dispatch to `ste_ctx->build_*_init()`. Rule creation calls `mlx5dr_ste_build_ste_arr()`, which initializes each STE, copies the builder bit mask, invokes the builder tag function to encode concrete values, and connects each STE to the next lookup type and byte mask.

Table allocation obtains a `struct mlx5dr_ste_htbl` and ICM chunk, initializes every STE and miss-list head, and stores lookup metadata. `mlx5dr_ste_create_next_htbl()` allocates and posts a next table for non-last STEs, sets the hit address in the current hardware STE, and records `next_htbl` / `pointing_ste`.

## State And Persistence
STE state is split: reduced hardware STE bytes live in `chunk->hw_ste_arr`, software metadata lives in `chunk->ste_arr`, and collision chains live in per-index `miss_list`. `mlx5dr_ste_free()` updates hardware differently for three deletion cases: only head becomes always-miss, head with collisions is replaced by the next collision STE, and middle collision updates the previous miss address. Hash table refcounts gate `mlx5dr_ste_htbl_free()`.

## Dependencies And Integration Points
This file depends on Linux CRC32, mlx5 IFC field helpers, ICM pool helpers, send posting, rule last-member repair, and the version-specific STE contexts declared in `dr_ste.h`. It parses user match buffers in the hardware FTE layout into `struct mlx5dr_match_param` and optionally clears consumed source bytes to let matcher creation detect unsupported fields.

## Risks
The hash function masks tag bytes according to `byte_mask`; any builder mask bug changes collision behavior and lookup correctness. STE deletion mutates list topology and hardware in tandem, so errors can orphan collision entries or leave stale rule last STEs. `mlx5dr_ste_copy_param()` supports truncated match buffers by copying tails into a temporary buffer; boundary mistakes here can corrupt match interpretation. Prechecks only enforce a few partial-mask constraints, so unsupported semantics must be caught by residual-mask checks.

## Test Signals
Test signals include deterministic hash indexes for known tags/masks, correct byte-mask conversion, STE-array construction consuming all value fields, partial source-port/IP mask rejection, next-table allocation and posts, deletion of only/head/middle collision entries, and version selection for ConnectX-5/6DX/7/8. Runtime signals are clean hash-table refcounts and no stale `pointing_ste` after delete or rehash.
