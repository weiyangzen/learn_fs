<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page_32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page_32.h

## Purpose
This header supplies 32-bit PowerPC page-type details, PTE size calculation, and cacheline-based page clear/copy primitives.

## Important APIs, Types, And Functions
It validates `CONFIG_PHYSICAL_START` alignment, defines `VMA_DATA_DEFAULT_FLAGS`, `PTE_SHIFT`, `pte_basic_t`, `clear_page()`, `copy_page()`, `PGD_T_LOG2`, and `PTE_T_LOG2`. `pte_basic_t` is 64-bit when `CONFIG_PTE_64BIT` is enabled.

## Control Flow
`clear_page()` loops over cache lines and issues `dcbz` for each line, warning if the address is not L1-cacheline aligned. `copy_page()` is implemented out of line.

## State And Persistence Behavior
No independent persistent state. The PTE geometry determines page-table storage size, including quarter-page PTE tables for 256K pages and 8xx 16K-page mode.

## Dependencies And Integration Points
It depends on `asm/cache.h`, `asm/bug.h`, and generic getorder. It integrates with MM page allocation, zeroing, copying, and pgtable type definitions.

## Risks And Edge Cases
`dcbz` is valid only for cacheable memory. Miscomputed `PTE_SHIFT` corrupts page-table layout. Physical start alignment is enforced at compile time.

## Test Signals
Cross-build 32-bit page-size variants, run page allocation zeroing/copying tests, boot with `CONFIG_PTE_64BIT`, and validate page-table sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page_32.h -->
