<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_cwksp.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_cwksp.h

## Purpose
`zstd_cwksp.h` implements Zstd's private compression workspace arena. It packs static objects, reusable fixed objects, matchfinder tables, aligned buffers, init-once buffers, and general buffers into one caller-owned or allocated contiguous region.

## Important APIs, Types, and Functions
Key types are `ZSTD_cwksp`, `ZSTD_cwksp_alloc_phase_e`, and `ZSTD_cwksp_static_alloc_e`. Important helpers include `ZSTD_cwksp_init()`, `ZSTD_cwksp_create()`, `ZSTD_cwksp_free()`, `ZSTD_cwksp_move()`, `ZSTD_cwksp_reserve_object()`, `ZSTD_cwksp_reserve_object_aligned()`, `ZSTD_cwksp_reserve_table()`, `ZSTD_cwksp_reserve_aligned_init_once()`, `ZSTD_cwksp_reserve_aligned64()`, `ZSTD_cwksp_reserve_buffer()`, `ZSTD_cwksp_clean_tables()`, `ZSTD_cwksp_mark_tables_dirty()`, `ZSTD_cwksp_mark_tables_clean()`, `ZSTD_cwksp_clear_tables()`, `ZSTD_cwksp_clear()`, `ZSTD_cwksp_available_space()`, `ZSTD_cwksp_used()`, `ZSTD_cwksp_sizeof()`, and oversized-workspace checks.

## Control Flow
Workspace allocation proceeds in strict phases: objects first, then init-once/tables, then aligned/tables, then buffers/tables. Objects and tables grow upward from the beginning of the workspace, while aligned/buffer allocations grow downward from an aligned end pointer. Advancing into table allocation aligns the table start to 64 bytes. Table validity is tracked separately from table reservation so reused tables can avoid clearing when their values are already bounded.

## State and Persistence
`ZSTD_cwksp` persists the workspace bounds, object/table ends, valid-table end, downward allocation start, init-once boundary, allocation failure flag, static/dynamic ownership mode, phase, and oversized duration counter. Object allocations survive `ZSTD_cwksp_clear()`, while tables and temporary buffers are invalidated between parameter sets or compression runs as needed. Init-once buffers are zeroed only the first time a region becomes exposed to memory checkers.

## Dependencies and Integration Points
The allocator depends on custom allocation hooks, Zstd internals, compiler helpers, and portability macros. `ZSTD_CCtx_s` embeds a `ZSTD_cwksp`; reset and dictionary creation code use it to allocate block states, entropy workspaces, match tables, sequence buffers, LDM state, and temporary block-split buffers.

## Risks
The main risks are out-of-order allocations, alignment mistakes, stale table values after table/temporary overlap, and misuse of init-once buffers that may contain prior data. Assertions enforce many invariants, but release builds rely on callers obeying phase and size contracts. Static allocation ownership must be correct so custom free does not double-free or leak.

## Test Signals
Tests should cover dynamic and static workspaces, repeated context resets with changing compression parameters, table reuse without memset, dirty/clean table transitions, allocation failure paths, oversized-duration shrink decisions, ASAN/MSAN behavior around init-once memory, alignment of 64-byte buffers/tables, and custom allocator failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_cwksp.h -->
