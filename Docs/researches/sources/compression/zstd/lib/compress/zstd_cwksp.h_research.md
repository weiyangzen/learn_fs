# sources/compression/zstd/lib/compress/zstd_cwksp.h

## Purpose
Implements zstd's compression workspace arena. The workspace packs context objects, entropy workspaces, hash/chain tables, aligned buffers, init-once buffers, and unaligned buffers into one contiguous allocation or caller-provided static buffer while supporting reuse across compressions and parameter changes.

## Important APIs, Types, And Functions
`ZSTD_cwksp` tracks `workspace`, `workspaceEnd`, `objectEnd`, `tableEnd`, `tableValidEnd`, `allocStart`, `initOnceStart`, allocation failure, oversized duration, current phase, and static/dynamic ownership. Allocation phases are `ZSTD_cwksp_alloc_objects`, `ZSTD_cwksp_alloc_aligned_init_once`, `ZSTD_cwksp_alloc_aligned`, and `ZSTD_cwksp_alloc_buffers`; ownership mode is `ZSTD_cwksp_dynamic_alloc` or `ZSTD_cwksp_static_alloc`.

Sizing/alignment helpers include `ZSTD_cwksp_align()`, `ZSTD_cwksp_alloc_size()`, `ZSTD_cwksp_aligned_alloc_size()`, `ZSTD_cwksp_aligned64_alloc_size()`, `ZSTD_cwksp_slack_space_required()`, and `ZSTD_cwksp_bytes_to_align_ptr()`. Reservation APIs include `ZSTD_cwksp_reserve_object()`, `ZSTD_cwksp_reserve_object_aligned()`, `ZSTD_cwksp_reserve_table()`, `ZSTD_cwksp_reserve_aligned_init_once()`, `ZSTD_cwksp_reserve_aligned64()`, and `ZSTD_cwksp_reserve_buffer()`.

Lifecycle and validation helpers include `ZSTD_cwksp_init()`, `ZSTD_cwksp_create()`, `ZSTD_cwksp_free()`, `ZSTD_cwksp_move()`, `ZSTD_cwksp_clear()`, `ZSTD_cwksp_clear_tables()`, `ZSTD_cwksp_clean_tables()`, `ZSTD_cwksp_mark_tables_dirty()`, `ZSTD_cwksp_mark_tables_clean()`, `ZSTD_cwksp_assert_internal_consistency()`, `ZSTD_cwksp_sizeof()`, `ZSTD_cwksp_used()`, `ZSTD_cwksp_available_space()`, and waste checks for oversized workspaces.

## Control Flow
Workspace layout grows objects/tables forward from the beginning and buffers/aligned allocations backward from the end: `[objects][tables ->] free [<- buffers][<- aligned][<- init once]`. Allocation must proceed by phase. Moving into the table/init-once phase aligns the start of tables to 64 bytes and sets initial validity markers. Object allocations are only valid in the first phase. Tables are forward allocations with 64-byte alignment and U32-sized byte counts. Aligned and buffer allocations reserve space from the high end and may reduce `tableValidEnd` if they overlap previously valid table space.

Clearing invalidates tables and high-end allocations but preserves object allocations; table cleaning zeros only the portion between `tableValidEnd` and `tableEnd`; dirty/clean markers let match tables be reused without full clearing when their values remain bounded.

## State And Persistence
The workspace persists for the lifetime of a compression context or CDict. Static objects and some init-once buffers can carry data across compressions by design. Table memory can be considered valid, dirty, or cleared based on `tableValidEnd`. `workspaceOversizedDuration` persists to help callers decide when a workspace is wastefully large. ASAN/MSAN hooks poison and unpoison regions to make misuse visible under sanitizers.

## Dependencies And Integration Points
The file depends on zstd custom allocation wrappers, common internals, portability/compiler macros, and power-of-two checks. `ZSTD_CCtx` and `ZSTD_CDict` allocation/reset code use it to allocate all compression-side data structures. Match finders rely on the table-validity contract to avoid unnecessary clears, and entropy/literal/sequence code relies on aligned scratch buffers.

## Risks And Edge Cases
Phase ordering is strict; reserving the wrong category after advancing too far fails. Pointer comparisons and alignment assumptions are central to internal consistency. Under ASAN, allocation sizes include redzones and dynamic workspaces are poisoned/unpoisoned; static workspaces cannot always be poisoned at teardown. Init-once memory intentionally may contain prior data, so users must avoid leaking or semantically depending on old contents.

Integer overflow and underflow in size estimation are risks when calculating workspace requirements. Table allocations are not redzoned, and they require byte counts to be multiples of both `sizeof(U32)` and 64. `ZSTD_cwksp_free()` clears the descriptor before freeing the captured pointer, so ownership must be initialized correctly.

## Test Signals
Sanitizer builds are especially valuable: ASAN for redzones, MSAN for uninitialized reads, and fuzzing with repeated context reuse and parameter changes. Unit-style tests should cover static and dynamic workspaces, allocation phase violations, table dirty/clean transitions, clear versus clear_tables behavior, workspace move/free, estimated-space bounds, and oversized-duration tracking.
