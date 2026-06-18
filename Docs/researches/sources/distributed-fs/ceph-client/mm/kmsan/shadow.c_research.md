# sources/distributed-fs/ceph-client/mm/kmsan/shadow.c

## Purpose
`shadow.c` implements KMSAN shadow/origin address translation and page metadata setup. It maps kernel, module, vmalloc, vmap, and page-backed addresses to metadata storage, provides dummy metadata for untracked accesses, and maintains per-page shadow/origin associations.

## Important APIs, Types, And Functions
Page helpers include `shadow_ptr_for()`, `origin_ptr_for()`, `page_has_metadata()`, and `set_no_shadow_origin_page()`. `vmalloc_meta()` computes metadata virtual addresses for vmalloc and module regions. `kmsan_get_shadow_origin_ptr()` returns metadata pairs for compiler instrumentation, falling back to dummy load/store pages. `kmsan_get_metadata()` resolves one shadow or origin pointer for an address. Page operations include `kmsan_copy_page_meta()`, `kmsan_alloc_page()`, `kmsan_free_page()`, `kmsan_vmap_pages_range_noflush()`, `kmsan_init_alloc_meta_for_range()`, and `kmsan_setup_meta()`.

## Control Flow
Instrumentation asks for metadata through `kmsan_get_shadow_origin_ptr()`. If KMSAN is disabled or metadata is unavailable, loads use a zero-filled dummy page and stores use a separate dummy page. For direct-mapped memory, `kmsan_get_metadata()` checks architecture metadata first, then resolves the backing `struct page` and its shadow/origin pages. For vmalloc/module addresses, metadata addresses are computed from fixed KMSAN metadata ranges. Page allocation poisons or clears metadata according to `__GFP_ZERO` and runtime state; freeing poisons memory with the UAF flag. Vmap maps metadata pages for each mapped data page into the vmalloc metadata ranges.

## State And Persistence
Per-page `kmsan_shadow` and `kmsan_origin` fields hold persistent metadata associations. `dummy_load_page` and `dummy_store_page` provide stable fallback metadata. Boot-time `kmsan_init_alloc_meta_for_range()` allocates and assigns metadata for existing ranges, while `kmsan_setup_meta()` assigns metadata for pages entering the allocator.

## Dependencies And Integration Points
The file depends on architecture KMSAN helpers, TLB/cache flush APIs, memblock, vmalloc metadata address constants, page allocator internals, and core poisoning/origin functions. It is the backing layer for `core.c`, `instrumentation.c`, `hooks.c`, and `init.c`.

## Risks
Returning dummy metadata avoids crashes but can hide real initialization state for untracked regions. Origin addresses require `KMSAN_ORIGIN_SIZE` alignment. Vmap metadata mapping must flush TLB/cache ranges and clean up allocations on errors. Page allocation assumes shadow/origin pages are contiguous for the order being initialized.

## Test Signals
KUnit cases covering uninitialized pages, page UAF, vmalloc initialization, vmap/vunmap, guarded vmalloc buffers, and metadata copy behavior indirectly validate this file. Metadata contiguity warnings from `core.c` are strong signals of bad shadow mapping.
