# sources/distributed-fs/ceph-client/include/linux/rmap.h

## Purpose
`rmap.h` declares the kernel reverse-mapping interfaces used by memory-management code to find and manipulate every VMA/PTE mapping a folio has. It covers anonymous VMA ancestry, folio mapcount accounting, COW/exclusive-anon transitions, page-table mapped-walk state, migration/unmap/mkclean operations, and rmap walker callbacks.

## Important APIs, types, and functions
Core types are `struct anon_vma`, `struct anon_vma_chain`, `enum ttu_flags`, `rmap_t`, `struct page_vma_mapped_walk`, and `struct rmap_walk_control`. Important APIs include `folio_add_anon_rmap_ptes()`, `folio_add_anon_rmap_pmd()`, `folio_add_new_anon_rmap()`, `folio_add_file_rmap_ptes()`, `folio_add_file_rmap_pmd()`, `folio_remove_rmap_ptes()`, `folio_remove_rmap_pmd()`, hugetlb rmap helpers, `folio_try_dup_anon_rmap_ptes()`, `folio_try_share_anon_rmap_pte()`, `folio_referenced()`, `try_to_unmap()`, `try_to_migrate()`, `page_vma_mapped_walk()`, `folio_mkclean()`, `remove_migration_ptes()`, `rmap_walk()`, and `folio_lock_anon_vma_read()`.

## Control flow, state, and persistence
Anonymous pages point to `anon_vma` rather than directly to VMAs, and `anon_vma_chain` links each VMA to related anon-vmas through both VMA lists and anon-vma interval trees. Mapping add/remove helpers adjust per-page, large-folio, entire-map, and optional per-MM mapcounts while sanity checks reject zeropage, hugetlb misuse, wrong page ranges, and stale anon-vma references. COW duplication may return `-EBUSY` when a possibly DMA-pinned exclusive anon folio cannot be safely shared. Mapped-walk callers initialize `page_vma_mapped_walk`, iterate PTE/PMD locations, then release PTE mappings and PTLs with `page_vma_mapped_walk_done()` or restart after page-table changes.

## Dependencies and integration points
The header depends on `mm.h`, `rwsem.h`, memcg, highmem, pagemap, memremap, bit spinlocks, folio/page helpers, THP/hugetlb configuration, optional `CONFIG_MM_ID`, GUP-fast barriers, and page-table lock discipline. It is used by fork, COW fault handling, KSM, reclaim, migration, compaction, writeback cleaning, hwpoison, and device-private/exclusive-page flows.

## Risks and test signals
Risks include mapcount underflow/overflow, clearing `PageAnonExclusive` while GUP-fast or DMA pins can still observe writability, missing final TLB flushes for batched unmap, anon-vma lifetime races, wrong `TTU_*` flag combinations, and leaked PTLs/PTE mappings when mapped walks abort. Test signals include fork/COW stress with pinned pages, THP split/migration, KSM sharing, reclaim reference sampling, `folio_mkclean()` writeback tests, hugetlb COW, memory hotplug/device-private migration, and debug-VM mapcount warnings staying silent.
