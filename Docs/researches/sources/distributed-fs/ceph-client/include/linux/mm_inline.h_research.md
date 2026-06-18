# sources/distributed-fs/ceph-client/include/linux/mm_inline.h

## Purpose
This header contains hot-path inline memory-management helpers that are too small or performance-sensitive for out-of-line calls. It focuses on LRU list classification/accounting, multi-generational LRU integration, anonymous VMA names, pending TLB flush tracking, userfaultfd write-protect marker handling, recency checks, and contiguous page-array detection.

## Important APIs, Types, And Data
- `folio_is_file_lru()` classifies folios for file versus anonymous LRU accounting by testing `folio_test_swapbacked()`.
- `__update_lru_size()` and `update_lru_size()` update lruvec and zone LRU counters, with memcg updates under `CONFIG_MEMCG`.
- `__folio_clear_lru_flags()` clears LRU/active/unevictable flags during release.
- `folio_lru_list()` selects the correct LRU list from file/anon and active/unevictable folio flags.
- Under `CONFIG_LRU_GEN`, helpers expose feature static keys, sequence-to-generation/hist conversion, tier calculation, reference extraction, generation extraction, active generation checks, size updates, generation sequence selection, add/delete paths, and migration of reference bits.
- Non-`CONFIG_LRU_GEN` stubs return disabled/false and keep callers simple.
- `lruvec_add_folio()`, `lruvec_add_folio_tail()`, and `lruvec_del_folio()` update list membership and LRU counters, delegating to MGLRU when active.
- Anonymous VMA name helpers get/put/reuse/duplicate/free/compare `anon_vma_name` values under `CONFIG_ANON_VMA_NAME`; stubs make the feature optional.
- TLB flush helpers initialize, increment, decrement, and query `mm->tlb_flush_pending`, including nested flush detection.
- `copy_pte_marker()` and `pte_install_uffd_wp_if_needed()` preserve or install special PTE markers for userfaultfd write-protect and poisoned/guard metadata.
- `vma_has_recency()` filters VMAs that should contribute recency signals.
- `num_pages_contiguous()` returns how many entries in a page pointer array are contiguous as `struct page` entries and sparsemem sections.

## Control Flow
LRU add/delete callers classify a folio, try the MGLRU path, and fall back to classic list insertion/removal and counter updates. MGLRU add computes a sequence, encodes the generation in folio flags, updates generation and LRU counters, and inserts at head or tail depending on reclaim context. Delete clears generation bits, may restore `PG_active` for migration, updates counters, and unlinks. TLB flush tracking increments before PTE updates under PTL ordering assumptions and decrements after flush completion. UFFD marker installation occurs only when a PTE has already been cleared and the VMA/file-backed write-protect conditions match.

## State And Persistence
State lives in folio flags (`PG_lru`, `PG_active`, `PG_unevictable`, MGLRU bits, reference bits), `lruvec` lists/counters, memcg LRU counters, `mm_struct.tlb_flush_pending`, VMA anonymous names, and PTE marker entries. The header mutates these structures inline but owns no independent global state except referenced static keys declared elsewhere.

## Dependencies And Integration Points
It includes atomic, huge MM, MM type, swap, string, userfaultfd, and leafops headers. It integrates with reclaim, page cache release, memcg accounting, MGLRU, migration, userfaultfd, page-table zapping/copying, and sparsemem section handling.

## Risks
LRU helpers require `lruvec->lru_lock`; `__update_lru_size()` asserts it. Wrong LRU classification or missed counter updates corrupt reclaim accounting. MGLRU flag encoding must stay aligned with page flag definitions. TLB flush pending relies on page-table-lock ordering and architecture TLB invalidation ordering, so misuse outside the documented PTL scope is unsafe. `pte_install_uffd_wp_if_needed()` must only run on cleared PTEs under the page-table lock. `num_pages_contiguous()` reports struct-page contiguity, not guaranteed PFN contiguity in all sparsemem configs.

## Test Signals
Signals include LRU counter balance tests during folio add/delete/isolate/release, memcg LRU accounting checks, MGLRU enabled and disabled builds, folio migration preserving reference bits, reclaim rotations, userfaultfd write-protect fork/zap tests, TLB flush pending assertions under concurrent faults, anonymous VMA name refcount tests, and sparsemem page-array contiguity tests.
