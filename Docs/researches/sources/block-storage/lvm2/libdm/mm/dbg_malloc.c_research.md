# File Research: sources/block-storage/lvm2/libdm/mm/dbg_malloc.c

## Summary
Implements libdm heap allocation wrappers with optional debug-memory tracking. In debug mode it records allocation metadata, guard bytes, leak reports, and bounds checks; in normal mode it delegates to libc allocation functions with a large-allocation guard.

## Main Responsibilities
- Provides malloc, zalloc, aligned malloc, strdup, realloc, free, memory dump, and bounds-check wrappers.
- Tracks debug allocations in a doubly linked list of `memblock` headers.
- Stomps allocated and freed memory with recognizable byte patterns in debug mode.
- Adds far-end guard bytes and validates them on free and explicit bounds checks.
- Integrates with Valgrind pool macros when `VALGRIND_POOL` is enabled.

## Key APIs
- Low-level helpers: `dm_malloc_aux()`, `dm_malloc_aux_debug()`, `dm_zalloc_aux()`, `dm_zalloc_aux_debug()`, `dm_realloc_aux()`, `dm_free_aux()`, `dm_strdup_aux()`.
- Debug reporting: `dm_dump_memory_debug()`, `dm_bounds_check_debug()`.
- Public wrapper layer: `dm_malloc_wrapper()`, `dm_malloc_aligned_wrapper()`, `dm_zalloc_wrapper()`, `dm_strdup_wrapper()`, `dm_free_wrapper()`, `dm_realloc_wrapper()`, `dm_dump_memory_wrapper()`, `dm_bounds_check_wrapper()`.

## Important Behavior
Allocations larger than 50,000,000 bytes are rejected as likely metadata corruption. Debug allocations reserve space for a `memblock` header and trailing guard bytes whose value is based on the allocation ID.

`dm_free_aux()` asserts that the pointer matches the block's magic pointer, verifies trailing guard bytes, checks for double free by ID, unlinks the block, overwrites freed memory with `0xad/0xde`, and frees the full block.

`dm_realloc_aux()` allocates a new debug block, copies the smaller of old and new sizes, then frees the old block.

Normal aligned allocation uses `posix_memalign()`, defaulting to page alignment when alignment is zero. Under `DEBUG_MEM`, aligned allocation is not truly aligned and falls back to debug malloc.

## State and Lifetime
Debug mode keeps global `_head`, `_tail`, and `_mem_stats` state for all active allocations. Normal mode has no tracking state.

## Risks
The debug allocator uses assertions for corruption detection, so failures abort the process. It is not visibly synchronized, so debug allocation tracking is not thread-safe. Normal `dm_strdup_wrapper()` calls libc `strdup()` directly and inherits its null-input behavior.
