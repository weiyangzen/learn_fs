# sources/distributed-fs/ceph-client/drivers/gpu/buddy.c

## Purpose
`buddy.c` implements the common GPU page-based buddy allocator used by DRM/TTM VRAM managers and other GPU memory users. It manages a byte-addressed aperture split into power-of-two blocks, supports allocations constrained by range, alignment, top-down preference, contiguity, and clear/dirty state, and returns allocated block lists to callers.

## Important APIs, types, and functions
Exported APIs are `gpu_buddy_init()`, `gpu_buddy_fini()`, `gpu_buddy_alloc_blocks()`, `gpu_buddy_block_trim()`, `gpu_buddy_reset_clear()`, `gpu_buddy_free_block()`, `gpu_buddy_free_list()`, `gpu_buddy_block_print()`, and `gpu_buddy_print()`. Internal helpers include `split_block()`, `__gpu_buddy_free()`, `__force_merge()`, `alloc_from_freetree()`, `__gpu_buddy_alloc_range_bias()`, `gpu_buddy_offset_aligned_allocation()`, `__gpu_buddy_alloc_range()`, and `__alloc_contig_try_harder()`. Blocks are allocated from a `kmem_cache`, and free blocks are stored in per-order red-black trees for clear and dirty memory.

## Control flow
Initialization validates size and chunk size, rounds size to chunk units, creates free-tree arrays, splits non-power-of-two apertures into root blocks, and inserts roots into dirty free trees. Allocation validates alignment and range, rounds or preserves size depending on flags, computes order/min-order, then repeatedly selects a block from a range-biased DFS, offset-aligned search, or free tree. Larger blocks are split until the target order is reached, chosen blocks are marked allocated, availability counters are updated, and oversized rounded allocations may be trimmed back with `gpu_buddy_block_trim()`. Freeing marks blocks clear or dirty according to flags, merges with a compatible free buddy where possible, and reinserts the merged block. Forced merge can coalesce dissimilar clear/dirty buddies when needed for larger allocations or teardown.

## State and persistence behavior
Allocator state lives in `struct gpu_buddy`: total size, available bytes, clear-available bytes, chunk size, max order, root block list, and `[clear|dirty][order]` free trees. Each `gpu_buddy_block` encodes offset, state, clear flag, and order in its header and stores parent/child, list, temporary DFS, and RB-tree links. State is volatile in kernel memory; callers persist any higher-level resource ownership outside this allocator.

## Dependencies and integration points
The implementation depends on `include/linux/gpu_buddy.h`, Linux RB-tree augmented callbacks, slab caches, bitmap/order helpers, `kmemleak_update_trace()`, KUnit failure hooks when enabled, and exported symbols consumed by DRM buddy wrappers, amdgpu VRAM management, i915/xe TTM managers, and GPU allocator tests.

## Risks and edge cases
Key risks are accounting drift in `avail`/`clear_avail`, merge behavior when buddies have dissimilar clear state, allocation rollback after partial splits, off-by-one range handling, `roundup_pow_of_two()` for large contiguous allocations, alignment search correctness for offset-zero blocks, mutation while iterating RB trees during forced merge, and callers freeing lists with the wrong clear/dirty flag. The allocator itself does not lock, so callers must serialize access. `gpu_buddy_fini()` assumes all allocations have been returned.

## Test signals
KUnit should cover init/fini with non-power-of-two sizes, invalid chunk sizes, simple and ranged allocations, top-down placement, contiguous fallback, offset-aligned small allocations, trimming, free-list clear/dirty marking, forced merge paths, allocation failure rollback, clear-available accounting, and final teardown assertions that all memory is available.
