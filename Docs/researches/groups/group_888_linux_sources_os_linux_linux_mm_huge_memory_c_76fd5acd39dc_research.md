# Group Research: group_888_linux_sources_os_linux_linux_mm_huge_memory_c_76fd5acd39dc

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/huge_memory.c -->
# File Research: sources/os/linux/linux/mm/huge_memory.c

## Scope And Role

This file is Linux MM's main Transparent Huge Page implementation. It covers PMD-sized anonymous THP, multi-size anonymous THP policy, read-only file THP support, huge zero folio management, huge PMD/PUD page-table operations, THP splitting, deferred split queues, THP shrinkers, debugfs split controls, and PMD-level migration entries.

It is in subset A through `sources/os/linux/linux`, the OS/VFS and kernel memory-management source tree.

## Major Responsibilities

- THP policy and sysfs controls:
  - Global `transparent_hugepage_flags`.
  - `/sys/kernel/mm/transparent_hugepage/enabled`, `defrag`, `use_zero_page`, `hpage_pmd_size`, and `shrink_underused`.
  - Per-size THP kobjects such as `hugepages-<size>kB`, with per-order `enabled` and `stats`.
  - Boot parameters `transparent_hugepage=` and `thp_anon=`.

- THP eligibility:
  - `__thp_vma_allowable_orders()` filters requested hugepage orders by VMA type, flags, DAX/special mappings, shmem policy, global THP policy, madvise state, file THP rules, temporary stacks, and VMA suitability.
  - `file_thp_enabled()` permits read-only regular file THPs when configured.
  - `vma_is_special_huge()` excludes PFNMAP/MIXEDMAP except DAX.

- Huge zero folio:
  - Lazily allocates a PMD-sized zero folio via `get_huge_zero_folio()`.
  - Tracks users with `huge_zero_refcount`, `huge_zero_folio`, and `huge_zero_pfn`.
  - Reclaims the zero folio through `huge_zero_folio_shrinker` unless `CONFIG_PERSISTENT_HUGE_ZERO_FOLIO` is enabled.
  - Used on read faults when zero-page THP is enabled and the mapping permits it.

- Fault-time huge PMD creation:
  - `do_huge_pmd_anonymous_page()` handles anonymous THP faults.
  - Read faults may install a huge zero PMD.
  - Write faults allocate a charged anonymous large folio through `vma_alloc_anon_folio_pmd()`, install it with `map_anon_folio_pmd_pf()`, update rmap/LRU/mm counters, and queue it for deferred split.
  - `vma_thp_gfp_mask()` translates defrag policy into allocation flags.

- Huge PMD/PUD insertion APIs:
  - `vmf_insert_pfn_pmd()` and `vmf_insert_folio_pmd()` insert PMD-sized PFNs or folios for special/file mappings.
  - With architecture support, `vmf_insert_pfn_pud()` and `vmf_insert_folio_pud()` perform similar PUD-sized insertion.
  - Insert paths enforce PFNMAP/MIXEDMAP constraints and update rmap, mm counters, and MMU cache.

- Fork/copy handling:
  - `copy_huge_pmd()` copies anonymous huge PMDs during fork, handling huge zero PMDs, migration/device-private soft entries, rmap duplication, write-protection, userfaultfd write-protect state, and fallback splitting when pinned pages prevent COW-safe sharing.
  - `copy_huge_pud()` handles PUD-sized huge entries, mainly file/DAX style because anonymous PUD THP is not fully supported.

- Access, write-protect, and NUMA paths:
  - `touch_pmd()` and `huge_pmd_set_accessed()` update accessed/dirty state.
  - `do_huge_pmd_wp_page()` handles write-protect faults, reusing exclusive anonymous THPs when safe, replacing huge zero PMDs with real THPs, or splitting on fallback.
  - `do_huge_pmd_numa_page()` handles NUMA hinting faults and misplaced THP migration.

- Range modification and unmapping:
  - `madvise_free_huge_pmd()` implements PMD-sized `MADV_FREE`.
  - `zap_huge_pmd()` removes a huge PMD, updates rmap/mm counters, withdraws deposited page tables, and queues TLB removal.
  - `move_huge_pmd()` supports huge PMD movement during remap.
  - `change_huge_pmd()` changes huge PMD protections, including NUMA, soft-dirty, and userfaultfd write-protect handling.
  - PUD equivalents exist behind `CONFIG_HAVE_ARCH_TRANSPARENT_HUGEPAGE_PUD`.

- Splitting:
  - `__split_huge_pmd_locked()` converts a huge PMD into PTEs or migration/device-private PTE entries while preserving dirty, young, soft-dirty, uffd-wp, anon-exclusive, and rmap state.
  - `__split_huge_zero_page_pmd()` splits a huge zero PMD into zero PTEs.
  - `vma_adjust_trans_huge()` splits huge PMDs at VMA boundary changes.
  - `__folio_split()` and helpers split large folios into smaller folios, including uniform and non-uniform split modes.
  - Splitting integrates anon-vma locks, page-cache xarray updates, swap cache replacement, memcg accounting, page owner state, pgalloc tags, LRU placement, and shmem EOF trimming.
  - Public split helpers include `folio_split_unmapped()`, `__split_huge_page_to_list_to_order()`, `folio_split()`, `min_order_for_split()`, and `split_folio_to_list()`.

- Deferred splitting and reclaim:
  - Large folios can be queued with `deferred_split_folio()`, optionally marked partially mapped.
  - `deferred_split_shrinker` scans per-node or memcg deferred split queues.
  - `thp_underused()` detects mostly-zero THPs for underused splitting.
  - `deferred_split_scan()` pins queued folios, attempts split, and requeues partially mapped folios when needed.
  - `reparent_deferred_split_queue()` moves queued folios from dying memcgs to parent memcgs.

- Debug and migration:
  - Under `CONFIG_DEBUG_FS`, `split_huge_pages` lets developers split all THPs, THPs in a process range, or file-backed THPs in a file offset range.
  - Under `CONFIG_ARCH_ENABLE_THP_MIGRATION`, `set_pmd_migration_entry()` installs PMD migration entries and `remove_migration_pmd()` restores PMD mappings after migration.

## Important State

- `transparent_hugepage_flags`: global THP enablement, defrag, and zero-page policy bitset.
- `huge_anon_orders_always`, `huge_anon_orders_madvise`, `huge_anon_orders_inherit`: per-order anonymous THP policy bitmaps.
- `huge_zero_folio`, `huge_zero_pfn`, `huge_zero_refcount`: global huge zero folio state.
- `deferred_split_shrinker`: shrinker for deferred split queues.
- `split_underused_thp`: controls whether underused THPs are queued for shrinking.
- `mthp_stats`: per-CPU, per-order multi-size THP stats exported through sysfs.

## Concurrency And Locking

- Page-table operations use PMD/PUD locks and carefully avoid replacing huge and small TLB entries without required invalidation.
- MMU notifier ranges wrap operations that clear or replace huge mappings.
- Anonymous folio splitting serializes through anon-vma write locks.
- File-backed splitting uses mapping `i_mmap` locking and page-cache xarray locking.
- Deferred split queues use per-node or per-memcg spinlocks, with special handling for dying memcgs.
- Folio refcount freeze/unfreeze protects split operations from concurrent GUP, page-cache lookup, LRU, reclaim, and migration races.
- Split code preserves architecture constraints around deposited page tables, especially for platforms that require page-table deposit/withdraw ordering.

## External Interfaces

- Exported symbols:
  - `thp_get_unmapped_area`
  - `vmf_insert_pfn_pmd`
  - `vmf_insert_folio_pmd`
  - `vmf_insert_pfn_pud`
  - `vmf_insert_folio_pud`

- Kernel init hooks:
  - `subsys_initcall(hugepage_init)`
  - `late_initcall(split_huge_pages_debugfs)` when debugfs support is enabled.

- Boot parameters:
  - `transparent_hugepage=always|madvise|never`
  - `thp_anon=<size/range>:always|inherit|madvise|never;...`

- User-visible runtime controls:
  - THP sysfs tree under `transparent_hugepage`.
  - Debugfs `split_huge_pages` write-only control when enabled.

## Error Paths And Fallbacks

- Allocation failures usually count fallback events and return `VM_FAULT_FALLBACK` or `VM_FAULT_OOM`.
- If huge PMD copy cannot safely duplicate rmap due to pins, it splits and retries on PTEs.
- Splitting can return:
  - `-EAGAIN` for unexpected references, concurrent page-cache removal, or races.
  - `-EBUSY` for writeback, unreleasable filesystem private state, missing anon-vma, truncation-like races, or huge zero folio.
  - `-EINVAL` for unsupported split orders or incompatible folio/mapping constraints.
  - `-ENOMEM` for xarray allocation failures, with non-uniform split possibly partially completed.
- Debugfs parsing rejects malformed process/file split requests with `-EINVAL`.

## Key Invariants

- Huge zero folio is never treated as a regular large rmappable folio.
- Anonymous order-1 THP split targets are disallowed because anon THP metadata uses subpage storage unavailable at that order.
- Swapcache folios can only be uniformly split to order 0.
- File-backed large folio splitting respects `mapping_min_folio_order()`.
- PMD splitting must make PTEs visible before installing the non-huge PMD.
- Present THP zaps and splits must synchronize with MMU notifiers and TLB flushing.
- `PageAnonExclusive` handling is central to safe COW, migration, write-protect reuse, and PMD splitting.

## Research Notes

This file is a central crossroad for Linux THP behavior. It connects VMA policy, sysfs policy, page fault handling, page-table manipulation, rmap, memcg, reclaim, migration, shmem/file page cache, userfaultfd, NUMA balancing, and debug tooling. The most delicate parts are the split and migration paths, where the implementation must preserve mapping metadata while converting between PMD/PUD leaves, PTE tables, migration entries, device-private entries, and smaller folios without racing page faults, GUP-fast, reclaim, or secondary MMUs.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/huge_memory.c -->