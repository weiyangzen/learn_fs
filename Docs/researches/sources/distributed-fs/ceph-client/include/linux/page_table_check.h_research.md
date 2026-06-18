<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_table_check.h -->
# sources/distributed-fs/ceph-client/include/linux/page_table_check.h

## Purpose
This header declares page table check instrumentation that validates page-table mappings and page allocation/free transitions to catch illegal aliasing or mapping state.

## Important APIs, types, and functions
With `CONFIG_PAGE_TABLE_CHECK`, it exports `page_table_check_disabled`, `page_table_check_ops`, implementation hooks for zeroing page metadata, clearing PTE/PMD/PUD mappings, setting batches of PTEs/PMDs/PUDs, and clearing PTE ranges. Inline wrappers are `page_table_check_alloc()`, `page_table_check_free()`, `page_table_check_pte_clear()`, `page_table_check_pmd_clear()`, `page_table_check_pud_clear()`, `page_table_check_ptes_set()`, `page_table_check_pmds_set()`, `page_table_check_puds_set()`, and `page_table_check_pte_clear_range()`. Convenience macros handle single PMD/PUD set.

## Control flow
Allocation/free and page-table manipulation paths call wrappers. If the static key says checks are disabled, wrappers return immediately; otherwise they call the validating implementation. Disabled `CONFIG_PAGE_TABLE_CHECK` compiles every wrapper to no-op.

## State and persistence
Check metadata persists in page_ext client storage. Static key state controls runtime enable/disable. No state is stored in the header itself.

## Dependencies and integration points
It depends on page_ext, jump labels, mm/page table types (`pte_t`, `pmd_t`, `pud_t`), allocation/free paths, and architecture page table update hooks.

## Risks and test signals
Risks include missing architecture hook coverage, false positives from legitimate aliasing, static key polarity misunderstandings, stale page_ext metadata after free, and batching count mistakes. Test `CONFIG_PAGE_TABLE_CHECK`, mapping/unmapping PTE/PMD/PUD ranges, huge mappings, fork/munmap/mremap, allocation/free zeroing, disabled runtime path, and architecture-specific page table helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_table_check.h -->
