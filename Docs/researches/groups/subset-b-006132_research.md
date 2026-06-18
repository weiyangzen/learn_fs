# subset-b-006132 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/ksm.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/ksm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/list_lru.c -->
# sources/distributed-fs/ceph-client/mm/list_lru.c

## Purpose

`list_lru.c` provides generic per-NUMA-node and optional per-memcg LRU-list infrastructure used by shrinkers and cache-like kernel subsystems. It centralizes add/delete/count/walk/isolate behavior, maintains shrinker notification bits, and handles memcg allocation and reparenting when memory cgroups are destroyed.

## Important APIs, types, and functions

The public API includes `list_lru_add()`, `list_lru_add_obj()`, `list_lru_del()`, `list_lru_del_obj()`, `list_lru_isolate()`, `list_lru_isolate_move()`, `list_lru_count_one()`, `list_lru_count_node()`, `list_lru_walk_one()`, `list_lru_walk_one_irq()`, `list_lru_walk_node()`, `__list_lru_init()`, and `list_lru_destroy()`. Most externally consumed symbols are exported GPL. Core data structures come from `linux/list_lru.h`: `struct list_lru`, `struct list_lru_node`, `struct list_lru_one`, and, under `CONFIG_MEMCG`, `struct list_lru_memcg`.

Memcg support adds `memcg_list_lrus`, `list_lrus_mutex`, XArray storage in `lru->xa`, `memcg_list_lru_alloc()`, and `memcg_reparent_list_lrus()`. The helper `lock_list_lru_of_memcg()` maps a memcg/nid pair to a live `list_lru_one`, falling back to a parent cgroup during reparenting unless the caller asked to skip empty/dead lists.

## Control flow

Initialization via `__list_lru_init()` allocates one `list_lru_node` per NUMA node, initializes each base list and spinlock, configures memcg awareness, records a shrinker id when available, and registers the LRU on the global memcg-aware list. Add and delete operations choose a node from either explicit `nid`/`memcg` parameters or from the object address (`page_to_nid(virt_to_page(item))` and `mem_cgroup_from_virt()`), lock the target `list_lru_one`, and update both local `nr_items` and node-wide atomic counts.

Walking is performed by `__list_lru_walk_one()`, which iterates while `nr_to_walk` permits and interprets callback `enum lru_status` results: retry restarts traversal after a dropped lock, removed statuses update isolation and node counts, rotate moves an item to the tail, skip leaves it in place, and stop exits. `list_lru_walk_node()` walks the root list and then, for memcg-aware LRUs, iterates all allocated memcg LRUs from the XArray with safe memcg references.

Memcg allocation (`memcg_list_lru_alloc()`) ensures each cgroup and missing ancestors have `list_lru_memcg` arrays allocated before use. Reparenting removes the dying cgroup's XArray entry under lock, splices each node list into the parent list, marks the source list dead with `LONG_MIN`, and frees the old per-memcg storage through RCU.

## State and persistence behavior

State persists in the caller-owned `struct list_lru`: per-node list heads, spinlocks, local item counts, aggregate node counts, optional shrinker id, optional memcg XArray, and registration on `memcg_list_lrus`. Items themselves are caller-owned `struct list_head`s and must be initialized/empty before `list_lru_add()` succeeds. Dead memcg LRUs use `nr_items == LONG_MIN` as a sentinel so lock acquisition can reject concurrent add/delete/isolate during reparenting. Destruction unregisters, frees all memcg arrays, frees the node array, and clears `lru->node`.

## Dependencies and integration points

This file integrates with shrinkers through `set_shrinker_bit()`, with memcg through `mem_cgroup_from_virt()`, `mem_cgroup_tryget()`, `mem_cgroup_put()`, `memcg_kmem_id()`, and cgroup death state, with XArray for per-memcg storage, with RCU for lookup/free safety, and with NUMA node enumeration. Users include slab/vfs/inode/dentry and other reclaimable caches that need shrinker-visible LRU lists.

## Risks and edge cases

Callers must preserve item lifetime and ensure memcg lifetime for explicit `list_lru_add()`/`list_lru_del()` calls. Count correctness depends on callbacks returning the right `LRU_*` status when they remove or move items. Reparenting races are subtle: the XArray entry is cleared before lists are spliced, and source lists are marked dead so future operations climb to a parent or skip. Negative `nr_items` values are clamped in count paths but indicate a dead list. Interrupt-safe walking must use the `_irq` path consistently with callbacks that may run in IRQ-off contexts.

## Test signals

Test coverage should exercise add/delete idempotence, object-based node/memcg selection, shrinker bit setting when transitioning from zero to nonzero, walk callbacks for every `LRU_*` status, `nr_to_walk` exhaustion, memcg allocation failure and ancestor allocation, concurrent memcg reparenting while adding/deleting, destroy after partial initialization, and lockdep with nested source/destination locks during reparenting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/list_lru.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/maccess.c -->
# sources/distributed-fs/ceph-client/mm/maccess.c

## Purpose

`maccess.c` implements best-effort kernel and user memory access helpers that do not take normal page faults. These helpers are used by tracing, diagnostics, probes, and other contexts where a fault must be converted into an error rather than handled through the normal fault path.

## Important APIs, types, and functions

Kernel-source helpers are `copy_from_kernel_nofault_allowed()` (weak arch/security override), `copy_from_kernel_nofault()`, `copy_to_kernel_nofault()`, and `strncpy_from_kernel_nofault()`. User-source helpers are `copy_from_user_nofault()`, `copy_to_user_nofault()`, `strncpy_from_user_nofault()`, and `strnlen_user_nofault()`. `__copy_overflow()` reports compile-time/object-size copy overflow detections. Exported symbols include `copy_from_kernel_nofault`, `copy_from_user_nofault`, `copy_to_user_nofault`, and `__copy_overflow`.

The typed loop macros use `__get_kernel_nofault()` and `__put_kernel_nofault()` in decreasing word sizes (`u64`, `u32`, `u16`, `u8`) when alignment permits. KMSAN and instrumentation hooks are present so nofault operations still participate in memory checking and write instrumentation.

## Control flow

Kernel reads first reject disallowed ranges through `copy_from_kernel_nofault_allowed()`, disable page faults, copy in aligned chunks, then re-enable page faults and return `0` or `-EFAULT`. Kernel writes similarly disable faults and use `__put_kernel_nofault()`, returning `-EFAULT` if any store faults.

`strncpy_from_kernel_nofault()` copies byte-by-byte until NUL or count, always terminates the destination on success, returns bytes consumed including the terminating NUL when found, returns `count` for truncation, and returns `-EFAULT` with `dst[0] = '\0'` on fault. User copies validate `access_ok()` or `__access_ok()` and, for user reads, `nmi_uaccess_okay()` before using inatomic copy helpers inside a pagefault-disabled section. User string helpers wrap `strncpy_from_user()` and `strnlen_user()` with page faults disabled, then normalize truncation and success return values.

## State and persistence behavior

The file maintains no persistent data. All state is on the stack or in caller-provided buffers. The important process-wide side effect is transient `pagefault_disable()`/`pagefault_enable()` nesting around unsafe access. `__copy_overflow()` emits a warning but does not maintain state.

## Dependencies and integration points

The implementation depends on architecture-provided nofault get/put primitives, user access validation, pagefault disable accounting, KMSAN, compiler object-size checking, and low-level `__copy_*_user_inatomic()` helpers. Architecture code can override `copy_from_kernel_nofault_allowed()` to reject ranges such as user aliases, firmware holes, or other unsafe kernel addresses.

## Risks and edge cases

These helpers do not pin memory and provide no stability guarantee: a successful copy only means the bytes were readable/writable at that moment. They must not be used as permission checks or to access arbitrary user memory without higher-level validation. Return conventions differ between raw copy helpers (`0` or negative errno) and string helpers (length/truncation or fault code). Missing destination space for forced NUL termination would be a caller bug. NMI and IRQ contexts require architecture support; the user-read path explicitly rejects when `nmi_uaccess_okay()` fails.

## Test signals

Useful tests cover valid and invalid kernel addresses, architecture-specific disallowed ranges returning `-ERANGE`, unaligned source/destination copies on platforms without efficient unaligned access, user addresses failing `access_ok()`, faulting user pages returning `-EFAULT`, string truncation and termination behavior, NMI-context rejection where applicable, KMSAN/instrumentation reports, and compile-time overflow warnings routed through `__copy_overflow()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/maccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/madvise.c -->
# sources/distributed-fs/ceph-client/mm/madvise.c

## Purpose

`madvise.c` implements `madvise(2)`, `process_madvise(2)`, anonymous VMA naming, and the kernel-side dispatch for memory advice behaviors. It translates user ranges and behavior codes into VMA flag updates, page-cache or swap readahead, page deactivation/pageout, lazy free, discard/zap, THP collapse policy, KSM policy, guard-page marker install/removal, population faults, and memory-failure injection.

## Important APIs, types, and functions

The core state carrier is `struct madvise_behavior`, containing the target `mm_struct`, behavior code, optional `mmu_gather`, selected lock mode, optional anonymous name, current range, current/previous VMA, and a `lock_dropped` flag. `struct madvise_behavior_range` tracks the active subrange, and `enum madvise_lock_mode` chooses no lock, mmap read/write lock, or per-VMA read lock.

Public entry points are `do_madvise()`, `SYSCALL_DEFINE3(madvise)`, `SYSCALL_DEFINE5(process_madvise)`, and, under `CONFIG_ANON_VMA_NAME`, `set_anon_vma_name()`, `anon_vma_name_alloc()`, `anon_vma_name_free()`, and `anon_vma_name()`. Major internal handlers include `madvise_vma_behavior()`, `madvise_walk_vmas()`, `madvise_willneed()`, `madvise_cold()`, `madvise_pageout()`, `madvise_free_single_vma()`, `madvise_dontneed_free()`, `madvise_populate()`, `madvise_remove()`, `madvise_guard_install()`, `madvise_guard_remove()`, `madvise_inject_error()`, and `vector_madvise()`.

## Control flow

`do_madvise()` validates alignment, length overflow, and behavior, acquires the lock selected by `get_lock_mode()`, optionally starts batched TLB gathering for discard/free operations, and dispatches through `madvise_do_behavior()`. Memory-failure behaviors bypass normal VMA walking. Populate behaviors call `faultin_page_range()` directly. Other behaviors call `madvise_walk_vmas()`, which applies `madvise_vma_behavior()` to each overlapping VMA and records `-ENOMEM` for holes while still processing mapped parts.

`madvise_vma_behavior()` first rejects prohibited modifications of sealed mappings, then either performs immediate operations (`MADV_REMOVE`, `WILLNEED`, `COLD`, `PAGEOUT`, `FREE`, `DONTNEED`, `COLLAPSE`, guard install/remove) or computes new VMA flags for policy-style advice and applies them with `madvise_update_vma()`. KSM advice delegates to `ksm_madvise()`, THP advice delegates to `hugepage_madvise()`/`madvise_collapse()`, and anonymous naming modifies VMA metadata through `vma_modify_name()`.

Page-table walkers handle the heavy page operations. `madvise_cold_or_pageout_pte_range()` clears young state, deactivates pages, or isolates pages for reclaim while respecting shared mappings, file-pageout permissions, large folio splitting rules, and THP PMDs. `madvise_free_pte_range()` handles `MADV_FREE` by clearing swap entries, clearing dirty/young PTE bits, freeing swapcache where possible, and marking folios lazyfree. `madvise_dontneed_single_vma()` zaps ranges with batched TLB work. Guard install tries to install `PTE_MARKER_GUARD` markers optimistically and zaps/retries when populated PTEs or huge entries race in; guard removal clears only guard markers.

`process_madvise()` imports an iovec, resolves a pidfd, checks ptrace access, restricts remote behaviors to non-destructive advice (`COLD`, `PAGEOUT`, `WILLNEED`, `COLLAPSE`), requires `CAP_SYS_NICE` for remote influence, then calls `vector_madvise()`.

## State and persistence behavior

Persistent effects depend on behavior. Flag advice changes `vma->flags` and may split/merge VMAs. KSM and THP advice updates VMA policy bits and may enroll an mm in KSM. `DONTNEED` zaps PTEs and releases pages/swap resources; `FREE` lazily marks anonymous pages discardable; `PAGEOUT` can reclaim pages; `WILLNEED` schedules I/O or swapin. Guard install persists not-present PTE markers and sets `VMA_MAYBE_GUARD_BIT`. Anonymous naming stores reference-counted `struct anon_vma_name` objects in VMAs. Population creates page tables/pages. Memory-failure injection changes page hardware-poison/offline state.

## Dependencies and integration points

This file is a hub for MM subsystems: VMA maple-tree modification, mmap and VMA locks, pagewalk, mmu_gather/TLB flushing, MMU notifiers, userfaultfd remove events, swap and shmem swapin, file `fadvise`/`fallocate`, reclaim/LRU, folio splitting, THP, hugetlb validation, KSM, mseal checks, mempolicy/page isolation, pidfd/task/mm access checks, ptrace permissions, capabilities, and anonymous VMA name reference counting.

## Risks and edge cases

Lock mode selection is central: write-lock behaviors may split/merge VMAs, read-lock behaviors may drop and reacquire the mmap lock around filesystem/userfaultfd work, and VMA read-lock fast paths are allowed only for local single-VMA ranges without userfaultfd or required anon-vma preparation. Operations that drop `mmap_lock` must not reuse stale VMA pointers. Large folio/THP handling avoids dirty tracking loss but can leave ranges partially untreated if splitting fails. Remote `process_madvise()` must not allow destructive operations or leak address-space metadata. Guard install can restart to resolve races. Sealed anonymous mappings reject discard-like operations when the user lacks write access. `MADV_DONTNEED` on hugetlb ranges rounds end down to hugepage size to avoid unexpected data loss.

## Test signals

Test signals include syscall ABI validation for alignment, overflow, empty ranges, unknown behaviors, VMA holes, and return values; per-behavior tests for flag changes and VMA splitting/merging; KSM/THP delegation tests; `MADV_FREE` and `DONTNEED` PTE/swap accounting; file-backed `REMOVE` and `WILLNEED` with lock dropping; remote `process_madvise()` permission and behavior filtering; guard marker install/remove including races with faults and THP; userfaultfd remove event sequencing; sealed VMA permission tests; anonymous VMA naming validation and refcounts; and lockdep/MMU-notifier/TLB stress under concurrent mmap, fork, reclaim, and signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/madvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mapping_dirty_helpers.c -->
# sources/distributed-fs/ceph-client/mm/mapping_dirty_helpers.c

## Purpose

`mapping_dirty_helpers.c` provides exported helpers for write-protecting and dirty-bit harvesting over all VMAs that map a shared `address_space` range. It supports filesystem/device dirty tracking use cases that need to protect PTEs, clean dirty PTEs, and record exactly which page offsets were dirty.

## Important APIs, types, and functions

The exported APIs are `wp_shared_mapping_range()` and `clean_record_shared_mapping_range()`. Internal walk state is `struct wp_walk`, which stores an MMU notifier range, the minimal TLB flush subrange, and a modified-PTE count. `struct clean_walk` extends it with a page-offset bitmap, bitmap base offset, and first/last touched bit range.

Pagewalk callbacks are `wp_pte()` for write-protecting PTEs, `clean_record_pte()` for cleaning dirty PTEs and recording offsets, `wp_clean_pmd_entry()` and `wp_clean_pud_entry()` for huge-entry handling, `wp_clean_pre_vma()` for notifier/cache/TLB setup, `wp_clean_post_vma()` for TLB flush and notifier completion, and `wp_clean_test_walk()` for VMA filtering.

## Control flow

Both exported helpers take `i_mmap_lock_read(mapping)`, call `walk_page_mapping()` across `first_index..first_index + nr`, and release the mapping lock. `wp_shared_mapping_range()` uses `wp_walk_ops`; for each applicable PTE, `wp_pte()` converts writable PTEs to read-only with `ptep_modify_prot_start()`/`commit()`, counts them, and expands the flush subrange.

`clean_record_shared_mapping_range()` uses `clean_walk_ops`; `clean_record_pte()` checks dirty PTEs, computes the address-space page offset from VMA start and `vm_pgoff`, cleans the PTE, records the corresponding bitmap bit, updates the touched bit interval, and counts the cleaned PTE. Pre/post VMA callbacks wrap each VMA walk in MMU notifier invalidation, cache flushing, and pending TLB-flush accounting. If nested TLB flushes are pending, the post callback flushes the full notifier range; otherwise it flushes only the modified subrange.

## State and persistence behavior

Persistent effects are page-table changes in processes mapping the address space: writable PTEs become write-protected and dirty PTEs become clean. `clean_record_shared_mapping_range()` also mutates the caller-provided bitmap and `start`/`end` output range. The helpers do not store state after returning. They explicitly warn but skip transparent huge PMD/PUD entries to avoid dirty information loss from splitting huge mappings in this helper path.

## Dependencies and integration points

The file depends on reverse mapping through `walk_page_mapping()`, `i_mmap_lock_read()`, pagewalk callbacks, VMA flags, MMU notifier APIs, architecture cache/TLB flush APIs, PTE modification primitives, and bit operations. `wp_clean_test_walk()` limits work to shared, may-write, non-hugetlb VMAs, so private/COW, read-only, PFN-only by exclusion, and hugetlb mappings are not dirty-tracked here.

## Risks and edge cases

The dirty-recording guarantees are race-aware but not exclusive: PTEs dirtied after the walk begins may remain dirty, be recorded, or both. Callers needing a closed dirty snapshot must first write-protect the range and block new writers in `page_mkwrite()`/`pfn_mkwrite()`, then harvest after the TLB flush. Bitmap bounds are caller-owned: `bitmap_pgoff` and allocation must cover the walked range. Huge PMD/PUD entries are skipped with warnings if dirty/write-enabled, so callers must account for that limitation. Correct notifier and TLB ordering is required for secondary MMUs and CPUs to observe protection/dirty-bit transitions.

## Test signals

Tests should map a shared file into multiple processes, dirty selected offsets, call `clean_record_shared_mapping_range()`, and verify bitmap bits and start/end compaction. Write-protect tests should confirm later writes fault through the filesystem/device write path and that already read-only PTEs are not counted. Stress should include concurrent writers, nested TLB flush conditions, secondary MMU notifier consumers, non-applicable VMAs, huge PMD/PUD mappings, empty ranges, and bitmap base offsets that do not equal `first_index`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mapping_dirty_helpers.c -->
