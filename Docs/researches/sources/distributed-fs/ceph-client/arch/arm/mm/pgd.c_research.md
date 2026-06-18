# sources/distributed-fs/ceph-client/arch/arm/mm/pgd.c

## Purpose
This file allocates and frees ARM per-mm top-level page tables. It copies kernel mappings into new address spaces, handles low-vector mappings when vectors are not high, and contains LPAE-specific allocation/free handling for module, pkmap, identity, and KASAN shadow tables.

## Important APIs, Types, and Functions
`pgd_alloc(struct mm_struct *mm)` allocates a zeroed PGD through `_pgd_alloc()`, copies kernel PGD entries above `USER_PTRS_PER_PGD`, cleans the PGD cache lines, allocates LPAE module/pkmap PMDs, copies KASAN shadow PMDs when enabled, and optionally allocates the low-vector PTE page. `pgd_free()` unwinds the low-vector page-table hierarchy, then for LPAE walks remaining PGD entries and frees non-swapper PMD/PUD/P4D tables.

## Control Flow
Allocation proceeds top down: PGD allocation, kernel mapping copy, LPAE module table allocation, optional KASAN copy, optional low-vector table allocation, and final low-vector PTE copy from `init_mm`. Error labels free the partially allocated hierarchy in reverse. Freeing validates and clears each level before returning page-table pages to the allocator.

## State and Persistence Behavior
The persistent state is the new `mm_struct` page-table root and page-table pages. Kernel mappings are copied into each new mm and remain shared by convention. The low-vector entries are duplicated into non-high-vector address spaces. Accounting counters such as `mm_dec_nr_pmds()` and `mm_dec_nr_ptes()` are updated during free paths.

## Dependencies and Integration Points
It depends on Linux page-table allocation helpers, ARM vector placement via `vectors_high()`, cache maintenance through `clean_dcache_area()`, and LPAE/KASAN configuration. It integrates with process creation, `mm` teardown, context switching through CPU `switch_mm` hooks, and exception vector mapping.

## Risks
Partial allocation cleanup is delicate; missing one level leaks page-table pages or corrupts mm accounting. Low-vector handling must preserve `DOMAIN_VECTORS` on non-LPAE systems or vectors can be unmapped for user processes. LPAE free logic must avoid freeing swapper-owned tables marked with `L_PGD_SWAPPER`. Cache cleaning is necessary before hardware page-table walks see copied entries.

## Test Signals
Run process fork/exec/exit stress on ARM classic and LPAE builds. Boot with high and low vectors, with and without KASAN. Enable page-table debugging and memory leak checks. Runtime signals include stable exception handling in user processes, no bad page-table warnings on exit, and no LPAE table leaks after process churn.
