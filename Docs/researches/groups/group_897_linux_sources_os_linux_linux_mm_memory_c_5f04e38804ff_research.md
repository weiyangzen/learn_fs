# Group Research: group_897_linux_sources_os_linux_linux_mm_memory_c_5f04e38804ff

Scope: `Docs/research_subset_a.md` / Linux `mm/memory.c`. The listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/memory.c -->
# File Research: sources/os/linux/linux/mm/memory.c

## Role

Linux core virtual-memory mapping and page-fault implementation. This file owns the generic machinery for page-table allocation and teardown, fork-time page-table copying, PTE/PMD/PUD fault dispatch, anonymous and file-backed fault completion, copy-on-write, swap-in, NUMA hinting faults, userfaultfd marker handling, PFN/page insertion APIs for drivers, page-table range application, remote process memory access, and helper routines for large-folio user copying/zeroing.

## Key Behavior

- Handles page-table free/allocation, fork-time page-table copy, zap/unmap, COW, swap-in, anonymous/file faults, hugepage fallback, NUMA hinting, and fault accounting.
- Exposes driver mapping APIs including `vm_insert_page(s)`, `vm_map_pages*()`, `vmf_insert_pfn*()`, `vmf_insert_mixed*()`, `remap_pfn_range()`, and `vm_iomap_memory()`.
- Implements `handle_mm_fault()` as the main generic page-fault entry below architecture handlers.
- Preserves userfaultfd semantics for missing and write-protected mappings, including non-present PTE markers during zaps.
- Coordinates COW/fork/unmap with MMU notifiers, TLB gather/flush, rmap, RSS counters, memcg, swap cache, KSM, THP, hugetlb, DAX, and device-private/exclusive memory.
- Supports large-folio batching for copy, zap, anonymous allocation, swap-in, and fault completion when semantics allow it.
- Provides address-space invalidation helpers `unmap_mapping_folio()`, `unmap_mapping_pages()`, and `unmap_mapping_range()` for truncation and page-cache invalidation.
- Implements PFNMAP lookup/access through `follow_pfnmap_start/end()` and `generic_access_phys()`.
- Implements remote process memory helpers `access_remote_vm()`, `access_process_vm()`, and BPF-only `copy_remote_vm_str()`.
- Provides large-folio helpers `folio_zero_user()`, `copy_user_large_folio()`, and `copy_folio_from_user()`.

## Public Interfaces And Exports

Important externally visible interfaces include page-table teardown/allocation (`free_pgd_range()`, `free_pgtables()`, `pmd_install()`, `__pte_alloc*()`), mapping classification (`vm_normal_page*()`, `vm_normal_folio*()`), zap/unmap helpers, driver insertion/remap helpers, page-range walkers, fault helpers (`do_swap_page()`, `finish_fault()`, `handle_mm_fault()`), PFNMAP helpers, and process memory access helpers.

The central normal-fault flow is `handle_mm_fault()` -> `__handle_mm_fault()` -> huge PMD/PUD handling or `handle_pte_fault()` -> `do_pte_missing()`, `do_swap_page()`, `do_numa_page()`, `do_wp_page()`, or access-bit update.

## Dependencies

Depends on `mm_struct`, `vm_area_struct`, folios/pages, page-table accessors, rmap, anon_vma, KSM, swap, memcg, LRU, hugetlb, THP, DAX, userfaultfd, MMU notifiers, TLB APIs, address-space interval trees, NUMA migration, perf fault counters, debugfs, and architecture cache/TLB hooks.

## Research Notes

`mm/memory.c` is the generic Linux VM fault and mapping coordinator rather than a narrow page-fault file. Its core pattern is optimistic work with strict revalidation: allocate or fault outside locks where needed, retake the page-table lock, compare the original entry, then commit PTE/PMD state plus rmap/RSS/memcg accounting.

<!-- END FILE RESEARCH: sources/os/linux/linux/mm/memory.c -->