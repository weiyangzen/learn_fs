# sources/distributed-fs/ceph-client/mm/khugepaged.c

## Purpose

`khugepaged.c` implements the background Transparent Huge Page collapse daemon and the forced `MADV_COLLAPSE` path. It tracks eligible address spaces, scans VMAs for PMD-sized ranges, collapses anonymous PTE pages into PMD-mapped anonymous folios, collapses file/shmem page-cache ranges into order-PMD folios, retracts PTE page tables for pte-mapped THPs, exposes sysfs tuning, and starts/stops the daemon according to THP policy.

## Important APIs, Types, and Functions

Important state includes `khugepaged_thread`, `khugepaged_mutex`, scan and allocation sleep tunables, `khugepaged_pages_to_scan`, `khugepaged_pages_collapsed`, `khugepaged_full_scans`, `khugepaged_mm_lock`, `khugepaged_wait`, PTE threshold tunables, `mm_slots_hash`, `mm_slot_cache`, and global `khugepaged_scan`. Main public functions are `hugepage_madvise()`, `khugepaged_init()`, `khugepaged_destroy()`, `__khugepaged_enter()`, `khugepaged_enter_vma()`, `__khugepaged_exit()`, `collapse_pte_mapped_thp()`, `start_stop_khugepaged()`, `khugepaged_min_free_kbytes_update()`, `current_is_khugepaged()`, and `madvise_collapse()`. Core collapse helpers include `collapse_scan_pmd()`, `collapse_huge_page()`, `__collapse_huge_page_isolate()`, `__collapse_huge_page_copy()`, `collapse_scan_file()`, `collapse_file()`, `try_collapse_pte_mapped_thp()`, `retract_page_tables()`, and `collapse_scan_mm_slot()`.

## Control Flow

Eligible VMAs enter through `khugepaged_enter_vma()` or `MADV_HUGEPAGE`, which allocate an `mm_slot`, insert it into the scan list/hash, grab an mm reference, and wake the daemon. The daemon drains LRU additions, scans up to `pages_to_scan`, iterates VMAs under trylocked `mmap_lock`, aligns ranges to PMD boundaries, and calls `collapse_single_pmd()`. Anonymous collapse first scans PTEs for present/young/anon/LRU/refcount/userfaultfd/swap constraints, optionally swaps in missing pages, allocates and charges a huge folio, invalidates notifiers, unlinks the PMD, isolates and copies source pages, installs a huge PMD, then frees old PTE pages. File/shmem collapse scans the page cache, locks and isolates folios, handles holes and swap entries, copies into a new huge folio, stores it as a multi-index xarray entry, retracts PTE tables from mappings, and frees old folios. Existing pte-mapped THPs can be collapsed by verifying all PTEs point at the same huge folio, removing the PTE page table, and optionally installing a huge PMD. `MADV_COLLAPSE` reuses this machinery with forced-collapse policy and returns actionable errno values mapped from `enum scan_result`.

## State and Persistence Behavior

The daemon persists mm scan state through `mm_slot` objects and the global scan cursor. Sysfs tunables persist until changed or rebooted. Page-cache and page-table transformations are persistent kernel memory state changes: successful collapse replaces many base pages or PTE mappings with a PMD-sized folio/mapping and increments counters. Failed scans leave page tables/page cache restored or unchanged.

## Dependencies and Integration Points

This file integrates with THP policy, sysfs attributes under `khugepaged`, mm slot helpers, VMA iteration, rmap, LRU isolation, memcg charging, page table locks, mmu notifiers, swap fault handling, userfaultfd, KSM zero-page handling, shmem, filemap/xarray, DAX exclusion, writeback, tracepoints in `trace/events/huge_memory.h`, kthreads/freezer, NUMA allocation policy, and min-free-kbytes watermarks.

## Risks and Edge Cases

The code is concurrency-heavy. Important risks include racing with mm exit, VMA changes while dropping `mmap_lock` for allocation/writeback, userfaultfd markers, GUP pins and elevated refcounts, dirty/writeback file pages, memory poison during copy, NUMA locality under node reclaim distance, page-table retraction without mmap lock for file mappings, and preserving lazyfree or droppable semantics. Many paths return precise `scan_result` values to avoid corrupting memory and to guide retries.

## Test Signals

Signals include THP/khugepaged tracepoints, sysfs counters (`pages_collapsed`, `full_scans`), vmstat THP scan/allocation events, `MADV_COLLAPSE` errno behavior, anon and shmem collapse tests, read-only file THP tests, userfaultfd exclusion tests, swap-in collapse, dirty/writeback retry behavior, pte-mapped THP retraction, mm exit races, and stress tests with GUP pins, KSM, memcg limits, NUMA, and concurrent truncate/hole-punch.
