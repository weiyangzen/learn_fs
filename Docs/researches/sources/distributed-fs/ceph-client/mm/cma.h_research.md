# sources/distributed-fs/ceph-client/mm/cma.h

## Purpose
`cma.h` defines private data structures and helpers for the Contiguous Memory Allocator implementation. It captures multi-range CMA metadata, allocation bitmaps, debug/sysfs integration fields, flags, and shared accounting declarations.

## Important APIs, types, and functions
Important types are `struct cma_kobject`, `struct cma_memrange`, `struct cma`, and `enum cma_flags`. Constants include `CMA_MAX_RANGES`. It declares global `cma_areas` and `cma_area_count`, defines `cma_bitmap_maxno`, and declares or stubs `cma_sysfs_account_success_pages`, `cma_sysfs_account_fail_pages`, and `cma_sysfs_account_release_pages`.

## Control flow
The header contains only inline/stub behavior. `cma_bitmap_maxno` converts a range page count into bitmap bits using `order_per_bit`; sysfs accounting calls either link to real functions when `CONFIG_CMA_SYSFS` is enabled or compile away.

## State and persistence
The structures defined here describe persistent runtime CMA state: per-range base/count and early-PFN-or-bitmap union, per-area counts and locks, optional debugfs bitmap views, sysfs counters, activation/validation flags, and NUMA node ownership.

## Dependencies and integration points
It depends on debugfs and kobject definitions and is shared by `cma.c`, `cma_debug.c`, and `cma_sysfs.c`. It connects private CMA internals to optional observability layers while keeping public CMA users on `<linux/cma.h>`.

## Risks and test signals
Risks include misuse of the `early_pfn`/`bitmap` union before or after activation, bitmap sizing mismatches, stale sysfs/debugfs pointers, and assumptions that a CMA area has only one range. Test signals include builds with and without `CONFIG_CMA_DEBUGFS` and `CONFIG_CMA_SYSFS`, multi-range reservations, `cma_get_base` warning behavior, sysfs accounting updates, and bitmap boundary tests.
