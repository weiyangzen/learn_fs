# sources/distributed-fs/ceph-client/mm/cma.c

## Purpose
`cma.c` implements the Contiguous Memory Allocator. It reserves boot-time physical memory areas, activates them as migratable CMA pageblocks, allocates physically contiguous ranges at runtime, supports multi-range CMA areas, and releases allocated ranges back to CMA.

## Important APIs, types, and functions
Public APIs include `cma_get_base`, `cma_get_size`, `cma_get_name`, `cma_validate_zones`, `cma_reserve_pages_on_error`, `cma_init_reserved_mem`, `cma_declare_contiguous_multi`, `cma_declare_contiguous_nid`, `cma_alloc_frozen`, `cma_alloc_frozen_compound`, `cma_alloc`, `cma_release`, `cma_release_frozen`, `cma_for_each_area`, `cma_intersects`, and `cma_reserve_early`. Core internal helpers include bitmap alignment helpers, `cma_activate_area`, `cma_new_area`, `cma_alloc_mem`, `cma_range_alloc`, `__cma_alloc_frozen`, and `find_cma_memrange`.

## Control flow
Early declaration reserves memory through memblock, validates size/alignment/order constraints, creates a `struct cma`, and records one or more PFN ranges. `core_initcall(cma_init_reserved_areas)` allocates bitmaps, validates that ranges do not cross zones, marks early-reserved bits, initializes CMA pageblocks, locks, and debug state. Runtime allocation scans range bitmaps for an aligned free area, marks bits under spinlock, calls `alloc_contig_frozen_range` under `alloc_mutex`, clears bits on retryable failure, and returns frozen or refcounted pages. Release verifies the pages belong to one CMA range, drops page refs for normal allocations, frees the frozen range, clears bitmap bits, and updates accounting.

## State and persistence
Global `cma_areas`, `cma_area_count`, and `totalcma_pages` persist after boot. Each CMA area stores total and available page counts, order-per-bit, locks, flags, NUMA node, sysfs/debugfs accounting, and up to `CMA_MAX_RANGES` physical ranges. Bitmap bits persist allocation state; `early_pfn` tracks pre-activation bottom-up reservations until activation replaces it with bitmaps.

## Dependencies and integration points
It depends on memblock, pageblock migration types, `alloc_contig_frozen_range`, `free_contig_frozen_range`, KASAN tag reset, kmemleak, tracepoints, sysfs/debugfs accounting hooks, NUMA-aware free range iteration, and exported CMA APIs used by DMA, hugetlb CMA, device drivers, and architecture setup code.

## Risks and test signals
Risks include zone-crossing ranges, bitmap/count imbalance, multi-range rollback bugs, alignment/order mistakes, early reservations not represented in bitmaps, contiguity failures from memory holes, alloc/release refcount misuse, and error handling that either leaks reserved memory or frees memory that callers own. Test signals include fixed and dynamic reservation, highmem and above-4G placement, multi-range fallback, CMA sysfs/debugfs accounting, concurrent allocations, `-EBUSY` retry paths, release of invalid pages, `cma_reserve_early`, memory hotplug interactions, and tracepoint/VM event counts.
