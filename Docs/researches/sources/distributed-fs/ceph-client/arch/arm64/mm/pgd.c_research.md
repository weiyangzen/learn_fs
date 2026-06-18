# sources/distributed-fs/ceph-client/arch/arm64/mm/pgd.c

## Purpose
This file allocates and frees user PGD tables on ARM64, accounting for runtime-folded page-table levels. When the effective PGD size is one page it delegates to the generic page-table allocator; otherwise it uses a dedicated slab cache with architecture-required alignment.

## Important APIs, Types, and Functions
The primary functions are `pgd_alloc()`, `pgd_free()`, and `pgtable_cache_init()`. The internal helper `pgdir_is_page_size()` determines whether `PGD_SIZE == PAGE_SIZE` or whether configured 4/5-level paging has folded at runtime. Persistent state is `static struct kmem_cache *pgd_cache`.

## Control Flow
`pgd_alloc()` selects `__pgd_alloc(mm, 0)` for page-sized directories and `kmem_cache_alloc(pgd_cache, GFP_PGTABLE_USER)` otherwise. `pgd_free()` mirrors that choice. `pgtable_cache_init()` returns early for page-sized directories, validates 64-byte alignment under 52-bit physical addressing, and creates `pgd_cache` with object size and alignment equal to `PGD_SIZE`.

## State and Persistence
The slab cache persists after initialization when needed. Individual PGDs persist as part of `mm_struct` address-space state and are freed through the matching allocator path.

## Dependencies and Integration Points
This file integrates with generic MM PGD allocation hooks, ARM64 runtime page-table folding (`pgtable_l4_enabled()`, `pgtable_l5_enabled()`), slab allocation, and architecture alignment requirements for 52-bit physical addressing.

## Risks
Allocator mismatch between folded and non-folded cases would corrupt memory. Alignment is architecturally required for top-level tables, so the cache alignment must match `PGD_SIZE`. Runtime folding decisions must remain consistent between allocation and free.

## Test Signals
Process creation/destruction under different VA-level configurations exercises these hooks. Booting 4-level and 5-level kernels on hardware with and without the corresponding runtime support validates folding. Slab diagnostics or page-table allocation failures would expose allocator issues.
