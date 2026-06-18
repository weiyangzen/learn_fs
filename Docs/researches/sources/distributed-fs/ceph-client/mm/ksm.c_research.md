# sources/distributed-fs/ceph-client/mm/ksm.c

## Purpose

`ksm.c` implements Kernel Samepage Merging: a background scanner (`ksmd`) that finds identical anonymous pages in VMAs marked `VM_MERGEABLE`, write-protects them, and replaces duplicate mappings with one KSM page. It also provides the KSM control plane used by `madvise(MADV_MERGEABLE/MADV_UNMERGEABLE)`, per-process merge-any mode, `/sys/kernel/mm/ksm` tunables/statistics, reverse-map walking for reclaim/migration/memory-failure, and memory-hotremove cleanup.

The file is not Ceph-specific; in this source tree it is core Linux MM infrastructure that distributed-fs clients depend on indirectly through generic virtual memory behavior.

## Important APIs, types, and functions

Key internal types are `struct ksm_mm_slot` (one tracked `mm_struct` plus its `ksm_rmap_item` list), `struct ksm_scan` (global scan cursor), `struct ksm_rmap_item` (reverse mapping for one mergeable virtual page), and `struct ksm_stable_node` (stable-tree node, duplicate node, or duplicate chain). The two main indexes are `root_stable_tree[]` for write-protected KSM pages and `root_unstable_tree[]` for candidate pages that were unchanged across scans. `mm_slots_hash` and `ksm_mm_head` track participating address spaces.

Externally relevant entry points include `ksm_madvise()`, `ksm_vma_flags()`, `ksm_enable_merge_any()`, `ksm_disable_merge_any()`, `ksm_disable()`, `__ksm_enter()`, `__ksm_exit()`, `ksm_might_need_to_copy()`, `rmap_walk_ksm()`, `folio_migrate_ksm()`, `ksm_process_mergeable()`, and `ksm_process_profit()`. `ksm_madvise()` is exported GPL for madvise integration. Sysfs attributes expose control and accounting: `run`, `pages_to_scan`, `sleep_millisecs`, `merge_across_nodes`, `use_zero_pages`, `max_page_sharing`, smart scan controls, advisor settings, and counters such as `pages_shared`, `pages_sharing`, `pages_unshared`, `pages_volatile`, `full_scans`, and `general_profit`.

## Control flow

Initialization (`ksm_init`) computes the zero-page checksum, allocates slab caches, starts the `ksmd` kthread, creates the sysfs group when configured, and registers a memory-hotremove notifier. `ksm_scan_thread()` loops until stopped: under `ksm_thread_mutex` it waits for offlining to finish, runs `ksm_do_scan()` when `KSM_RUN_MERGE` is active and the mm list is non-empty, then sleeps on `ksm_iter_wait` or `ksm_thread_wait`.

`ksm_do_scan()` repeatedly calls `scan_get_next_rmap_item()` to walk mergeable VMAs and return one anonymous page plus its rmap item. The scanner handles full-scan boundaries by draining LRU additions, pruning migrated stable nodes, clearing unstable trees, advancing the mm cursor, removing stale rmap items, and incrementing `ksm_scan.seqnr`. `should_skip_rmap_item()` implements smart-scan backoff for pages that repeatedly fail to deduplicate.

`cmp_and_merge_page()` is the merge decision hub. It removes stale tree placement, checks page checksums to avoid unstable pages, optionally merges zero-filled pages into zero-page PTEs, searches the stable tree, and otherwise searches/inserts the unstable tree. Stable matches are merged by `try_to_merge_with_ksm_page()` and appended to a stable node. Unstable matches are merged by `try_to_merge_two_pages()`, then inserted into the stable tree by `stable_tree_insert()` and linked with `stable_tree_append()`.

`write_protect_page()` and `replace_page()` are the low-level page-table transitions. They use page locks, PTE locks, TLB/cache flushing, MMU notifier ranges, anonymous-rmap updates, dirty accounting, and zero-page special PTE handling. `break_ksm()` walks VMAs and faults KSM mappings with `FAULT_FLAG_UNSHARE | FAULT_FLAG_REMOTE` until no KSM mapping remains, allowing unmerge and cleanup paths to restore private anonymous pages.

## State and persistence behavior

State is in kernel memory only: slab objects for slots/rmaps/stable nodes, red-black trees, hlist chains, per-mm counters (`ksm_rmap_items`, `ksm_merging_pages`, zero-page counts), global counters, sysfs tunables, and the scan cursor. KSM pages identify their stable node through `folio->mapping | FOLIO_MAPPING_KSM`; `ksm_get_folio()` uses a keyhole reference instead of pinning every stable page. The unstable tree is intentionally rebuilt every full scan because candidate page contents are not write-protected. Stable nodes persist until all mappings disappear, unmerge is requested, memory hotremove invalidates PFNs, migration moves a node to the right NUMA tree, or stale-node pruning observes that the page no longer maps back to the node.

The sysfs `run` store can stop scanning, enable merging, or perform global unmerge via `unmerge_and_remove_all_rmap_items()`. Changing `merge_across_nodes` or `max_page_sharing` is refused with `-EBUSY` if stable pages cannot be removed.

## Dependencies and integration points

KSM depends heavily on MM primitives: maple-tree VMA iteration, pagewalk, rmap, anon_vma, swap, migration, memory hotplug, memcg charging through fault/copy paths, mmu_notifiers, TLB/cache flush APIs, LRU drain/reclaim interactions, and sysfs/procfs. `madvise.c` calls `ksm_madvise()`. VMA creation can call `ksm_vma_flags()` when `MMF_VM_MERGE_ANY` is set. Swap-in calls `ksm_might_need_to_copy()` to decide whether a swapped KSM/anonymous folio must be copied. Rmap walkers, migration, and memory failure paths call KSM-specific helpers to find mappings, update PFNs, or collect affected processes.

## Risks and edge cases

The highest-risk areas are concurrency and accounting: `ksm_mmlist_lock`, `ksm_thread_mutex`, mmap locks, anon_vma locks, PTE locks, folio locks, and MMU notifier ordering must remain consistent. The stable-node keyhole reference is subtle; missing memory barriers around migration would make stale-node detection unsafe. Duplicate chains must respect `ksm_max_page_sharing` while preserving rmap walk correctness. Zero-page merging changes anonymous accounting and uses dirty special PTEs to count KSM-placed zero pages. Unmerge may return `-ENOMEM` when COW faults fail, and VMA flags must not be cleared while KSM mappings remain. NUMA mode changes require empty stable trees. Huge-page splitting, GUP/O_DIRECT races, migration entries, swapcache pages, memory hotremove, and exiting `mm_struct`s are all explicitly handled but remain regression-prone.

## Test signals

Useful tests include LTP/KSM tests for merge/unmerge and deterministic `pages_volatile` behavior, sysfs round trips for every tunable, `madvise(MADV_MERGEABLE/UNMERGEABLE)` over anonymous ranges, merge-any enable/disable via process controls, zero-page merging counters, NUMA `merge_across_nodes` toggling while pages are shared, memory hotremove/migration stress, THP split scenarios, swap-in of KSM pages, memory-failure collection over KSM mappings, and lockdep/KCSAN/KASAN runs over concurrent exit, fork, mmap, and unmerge.
