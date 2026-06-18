# Research: subset-b-006147

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/sparse-vmemmap.c -->
# sources/distributed-fs/ceph-client/mm/sparse-vmemmap.c

Purpose: implements generic SPARSEMEM VMEMMAP backing for `struct page` arrays. It allocates and populates kernel page tables for the virtual memmap, supports early boot and memory hotplug population, handles altmap-backed device memory, and contains generic support for hugetlb/device vmemmap deduplication.

Important APIs and functions: `vmemmap_alloc_block()`, `vmemmap_alloc_block_buf()`, `vmemmap_pte_populate()`, `vmemmap_populate_basepages()`, `vmemmap_populate_hugepages()`, `__populate_section_memmap()`, `sparse_init_subsection_map()`, `online_mem_sections()`, `offline_mem_sections()`, `sparse_add_section()`, and `sparse_remove_section()` are the major externally visible or cross-file entry points. Weak hooks `vmemmap_set_pmd()` and `vmemmap_check_pmd()` let architectures install or validate PMD-sized vmemmap mappings.

Control flow: base-page population walks PGD/P4D/PUD/PMD/PTE levels, allocating zeroed page-table pages as needed and then mapping a page of backing storage with `PAGE_KERNEL`. Hugepage population first tries architecture PMD mappings, falls back to base pages, and treats altmap failure as fatal because altmap sizing is part of the device-memory contract. `__populate_section_memmap()` converts PFN ranges into vmemmap virtual addresses and chooses compound-page deduplication when `vmemmap_can_optimize()` allows it. Hotplug add initializes sparse indexes, activates subsection bits, populates the memmap, poisons uninitialized page structs, marks the section present, and initializes the section; hotplug remove clears subsection bits, frees or preserves usage maps depending on early-section status, and depopulates vmemmap.

State and persistence: state is kernel memory-management metadata, not persistent storage. It mutates `mem_section`, `mem_section_usage.subsection_map`, `section_mem_map` flags such as `SECTION_HAS_MEM_MAP` and `SECTION_IS_ONLINE`, zone `vmemmap_tails[]` for hugetlb optimization, altmap allocation counters, and vmstat memmap page counters. Hotplug removal uses RCU freeing for usage maps and must leave early boot shared usage-map pages intact.

Dependencies and integration points: depends on `memblock`, slab/page allocators, architecture page-table primitives, `vmem_altmap`, `dev_pagemap`, memory hotplug, hugetlb vmemmap optimization, `pfn_to_page()` layout, TLB flush expectations from callers, and sparse section helpers from `mmzone`/`internal.h`. It is called from sparse initialization, memory hotplug, and device-memory onboarding paths.

Risks and test signals: high-risk areas include off-node vmemmap allocation warnings, altmap alignment/accounting mistakes, freeing tables while readers can still dereference section metadata, subsection bitmap double-add/double-remove, PMD huge mapping fallback, and deduplicated tail-page reference handling. Test signals include memory hotplug add/remove at subsection granularity, dev_pagemap with altmap and compound pages, hugetlb vmemmap optimization boot paths, NUMA boot with sparse ranges, debug VM warnings, and architecture builds with and without `CONFIG_MEMORY_HOTPLUG`, `CONFIG_SPARSEMEM_VMEMMAP_PREINIT`, and `CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/sparse-vmemmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/sparse.c -->
# sources/distributed-fs/ceph-client/mm/sparse.c

Purpose: initializes and maintains the generic SPARSEMEM section table during boot. It records which physical memory sections are present, allocates `mem_section` roots and section usage maps, allocates or requests backing `struct page` arrays, and finalizes section initialization per NUMA node.

Important APIs and functions: exports `mem_section` and, when node IDs are not encoded in page flags, `memdesc_nid()`. `sparse_index_init()` allocates section root arrays for `CONFIG_SPARSEMEM_EXTREME`. `memory_present()`, `memblocks_present()`, `sparse_init_early_section()`, `sparse_init_nid()`, and `sparse_init()` drive boot initialization. `mem_section_usage_size()`, `section_map_size()`, and `sparse_buffer_alloc()` are shared allocation helpers used by VMEMMAP and non-VMEMMAP configurations.

Control flow: `sparse_init()` first marks memblock PFN ranges present, storing early NUMA IDs in `section_mem_map`. It then groups consecutive present sections by early node ID, initializes pageblock order, and calls `sparse_init_nid()` per range. Per-node initialization allocates a packed usage-map buffer and a section-map backing buffer, gives preinit hooks a chance to populate vmemmap, populates each non-preinitialized section memmap, accounts boot memmap pages, and calls `sparse_init_early_section()`. On allocation failure, sections not already preinitialized are marked not present so memory is not later exposed with missing memmap.

State and persistence: state is boot-time memory topology. It updates the global sparse section table, optional `section_to_node_table`, `__highest_present_section_nr`, temporary `sparsemap_buf` and `sparse_usagebuf`, section usage bitmaps, and boot memmap counters. The data persists for the lifetime of the kernel as physical-to-page metadata, but it is not persisted across boots.

Dependencies and integration points: integrates with memblock physical range enumeration, NUMA node IDs, VMEMMAP hooks from `sparse-vmemmap.c`, non-VMEMMAP `__populate_section_memmap()`, bootmem accounting, pageblock order setup, `mminit` diagnostics, and architecture limits via `DIRECT_MAP_PHYSMEM_END`. It feeds all later PFN validity, page allocator, and memory hotplug logic.

Risks and test signals: risks include section root allocation races during hotplug, early node encoding mistakes, overflow or truncation against sparsemem physical limits, freeing the preallocated sparse buffer incorrectly after alignment, and failed memmap allocation silently removing memory. Test with sparse NUMA memblock layouts, `CONFIG_SPARSEMEM_EXTREME`, VMEMMAP and non-VMEMMAP builds, very high PFNs near architecture limits, simulated memmap allocation failure, and boot logs for `mminit`/off-node warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/sparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/swap.c -->
# sources/distributed-fs/ceph-client/mm/swap.c

Purpose: despite the filename, this file primarily manages folio reference release and LRU batching behavior for the VM. It defines default `page_cluster` sysctl setup, per-CPU folio batches for LRU add/move/deactivate/lazyfree/activate paths, batched folio release, LRU drain coordination, and memcg LRU reparenting.

Important APIs and functions: exported entry points include `__folio_put()`, `folio_mark_accessed()`, `folio_add_lru()`, `folio_add_lru_vma()`, `release_pages()`, and `__folio_batch_release()`. Other important global functions are `folio_rotate_reclaimable()`, `lru_note_cost_unlock_irq()`, `lru_note_cost_refault()`, `folio_activate()`, `lru_add_drain_cpu()`, `deactivate_file_folio()`, `folio_deactivate()`, `folio_mark_lazyfree()`, `lru_add_drain()`, `lru_add_drain_all()`, `lru_cache_disable()`, `folios_put_refs()`, `folio_batch_remove_exceptionals()`, `lru_reparent_memcg()`, and `swap_setup()`.

Control flow: callers queue folios into per-CPU batches under `local_lock` or `local_lock_irq`, taking a temporary reference. Drains move each batch under the correct `lruvec` lock, update active/referenced/unevictable/swapbacked flags, adjust VM and memcg counters, then drop the queued references. Access marking either updates multi-gen LRU reference bits or promotes referenced inactive folios. Batched release subtracts references, removes last-reference folios from LRU, uncharges memcg, and frees them in groups. SMP global drain uses a generation counter, memory barriers, and `mm_percpu_wq` work items to avoid missing CPU-local batches under concurrent drain requests.

State and persistence: state is transient VM runtime state: `page_cluster`, per-CPU `cpu_fbatches`, `lru_disable_count`, lruvec cost counters, folio flags, LRU list membership, memcg LRU counters, and sysctl registration under `vm/page-cluster`. No disk persistence exists, but these choices strongly affect reclaim behavior and swap readahead sizing in other files.

Dependencies and integration points: depends on folio APIs, `lruvec`, memcg charging, workingset activation, multi-gen LRU, mlock draining, buffer-head LRU invalidation, page allocator free paths, hugetlb/zone-device freeing, sysctl, and tracepoints. It is a shared service for page cache, anonymous memory, reclaim, migration, truncation, and swap cache paths.

Risks and test signals: risks include missing LRU drains before migration/isolation, incorrect local lock or IRQ context selection, racing remote batch activation, LRU flag/accounting mismatches, deadlocks from global drain under hotplug locks, memcg reparent counter drift, and freeing folios with stale LRU or private state. Test signals include LRU debug assertions, memcg reclaim tests, multi-gen LRU enabled/disabled matrices, CPU hotplug with pending batches, mlock/unevictable transitions, page-cache truncation and release stress, and sysctl `page-cluster` bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/swap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/swap.h -->
# sources/distributed-fs/ceph-client/mm/swap.h

Purpose: provides the MM-internal swap interface shared by swap allocation, swap cache, page I/O, and readahead code. It defines swap cluster sizing, the cluster metadata structure, cluster flags, locking helpers, swap cache prototypes, swap I/O prototypes, and no-op stubs for `CONFIG_SWAP=n`.

Important APIs and types: `struct swap_cluster_info` contains the per-cluster spinlock, used-slot count, list flag, order, RCU-protected swap table pointer, optional extended count table, and list node. `enum swap_cluster_flags` classifies free, nonfull, fragmented, full, discard, and temporary off-list states. Key helpers include `swp_cluster_offset()`, `__swap_entry_to_info()`, `__swap_offset_to_cluster()`, `swap_cluster_lock()`, `swap_cluster_get_and_lock()`, `folio_alloc_swap()`, `folio_dup_swap()`, `folio_put_swap()`, `swap_read_folio()`, `swap_writeout()`, `swap_address_space()`, `swap_dev_pos()`, `folio_matches_swap_entry()`, `swap_cache_has_folio()`, `swap_cache_get_folio()`, `swap_cache_alloc_folio()`, `swapin_readahead()`, `swap_update_readahead()`, `folio_swap_flags()`, `swap_zeromap_batch()`, and `non_swapcache_batch()`.

Control flow: users of swap entries first stabilize a swap device by a `get_swap_device()` reference, a locked swap-cache folio, a page-table lock, or equivalent synchronization. Cluster helpers map a swap offset to a cluster and lock it before modifying swap table, count, or list state. Swapout calls `folio_alloc_swap()` to allocate slots and pin them with swap cache, later `folio_dup_swap()` when PTEs are installed, and `folio_put_swap()` or direct put helpers when mappings are removed. Swapin/readahead callers allocate or find swap-cache folios and trigger page I/O.

State and persistence: this header declares shared in-memory state rather than owning it. The main state is `swap_info[]`, each `swap_cluster_info`, swap tables, per-folio `folio->swap`, swap cache flags, and zeromap bits. On-disk persistence is represented indirectly by swap offsets and block positions; the header’s contracts protect the metadata that makes those disk slots safe to reuse.

Dependencies and integration points: includes `swapops.h`, block I/O types, folio and mempolicy declarations, page I/O implementation in `page_io.c`, swap cache implementation in `swap_state.c`, and swap allocator implementation in `swapfile.c`. The stubs let generic MM code compile without swap support.

Risks and test signals: risks include callers using helpers without stabilizing the swap device, locking a cluster for an unlocked or non-swapcache folio, large-folio entries crossing cluster boundaries, mismatch between `SWAPFILE_CLUSTER` and THP swap order, and `CONFIG_SWAP=n` stubs hiding behavior differences. Test with swapoff races, THP swap enabled/disabled, swap cache split/replace paths, zeromap batch queries, and compile coverage for no-swap builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/swap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/swap_cgroup.c -->
# sources/distributed-fs/ceph-client/mm/swap_cgroup.c

Purpose: records and looks up memory cgroup IDs for swap entries, primarily for swap accounting. It stores compact per-swap-slot cgroup IDs in arrays allocated at swapon and freed at swapoff.

Important APIs and functions: `swap_cgroup_record()` records one folio’s cgroup ID across all swap entries it occupies. `swap_cgroup_clear()` clears a contiguous entry range and returns the prior ID. `lookup_swap_cgroup_id()` reads an entry’s ID. `swap_cgroup_swapon()` allocates the per-type map, and `swap_cgroup_swapoff()` unpublishes and frees it. Internals `__swap_cgroup_id_lookup()` and `__swap_cgroup_id_xchg()` pack two `unsigned short` IDs into one atomic word and update one field with `atomic_try_cmpxchg()`.

Control flow: swapon allocates a zeroed map sized by `max_pages`, then publishes it under `swap_cgroup_mutex`. Swapout records an ID for a folio’s slots and asserts that the old IDs were zero. Swapin or slot freeing clears IDs and asserts all entries in the range had the same previous ID. Lookups skip all work when memcg is disabled.

State and persistence: state lives in `swap_cgroup_ctrl[MAX_SWAPFILES]`, where each swap type holds a vmalloc-backed packed ID array. IDs are in-memory accounting metadata and are not persisted in the swap device; they are discarded on swapoff. Atomic packing prevents torn updates when adjacent slots in the same word are modified.

Dependencies and integration points: depends on `linux/swap_cgroup.h`, memcg enablement, swap entry type/offset helpers, vmalloc, and the swapon/swapoff lifecycle in `swapfile.c`. It is consumed by memcg swap accounting and by swap table shadow encoding paths that need cgroup attribution.

Risks and test signals: risks include ID overflow beyond `unsigned short`, publishing or clearing maps while swap entries are still visible, inconsistent old IDs across a folio range, and atomic packing mistakes corrupting the neighboring slot. Test with memcg swap accounting enabled/disabled, folios larger than one page, repeated swapon/swapoff, concurrent swapout/swapin under cgroups, and debug assertions for nonzero old IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/swap_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/swap_state.c -->
# sources/distributed-fs/ceph-client/mm/swap_state.c

Purpose: manages the swap cache and swapin readahead policy. In this tree, swap cache lookup is backed by per-cluster atomic swap tables rather than a traditional address-space XArray, while `swap_space` remains as a synthetic mapping for reclaim and migration integration.

Important APIs and functions: `show_swap_cache_info()`, `swap_cache_get_folio()`, `swap_cache_has_folio()`, `swap_cache_get_shadow()`, `__swap_cache_add_folio()`, `swap_cache_del_folio()`, `__swap_cache_del_folio()`, `__swap_cache_replace_folio()`, `free_swap_cache()`, `free_folio_and_swap_cache()`, `free_pages_and_swap_cache()`, `swap_update_readahead()`, `swap_cache_alloc_folio()`, `swapin_folio()`, `read_swap_cache_async()`, `swap_cluster_readahead()`, and `swapin_readahead()` form the main surface. Sysfs exposes `mm/swap/vma_ra_enabled` when `CONFIG_SYSFS` is enabled.

Control flow: swap cache lookup reads the cluster table under RCU and takes a folio reference only after seeing a PFN entry. Adding a folio locks the cluster, verifies all covered slots exist and have nonzero swap counts, preserves any shadow, writes PFN entries, sets `SwapCache`, updates `folio->swap`, and accounts `NR_FILE_PAGES`/`NR_SWAPCACHE`. Deletion replaces PFN entries with shadow placeholders carrying the same counts, clears folio swap state, frees slots whose count is zero, and updates counters. Swapin allocates or finds a folio, charges memcg, inserts into swap cache, handles workingset refault shadows, adds it to LRU, and starts `swap_read_folio()` if newly allocated. Readahead selects either cluster-adjacent offsets or VMA-neighboring PTE swap entries, batches I/O with blk plugs, marks non-target folios as readahead, and updates hit/window heuristics.

State and persistence: state includes `swap_space`, per-slot swap table entries, folio `SwapCache` and `swap` fields, swap-cache page counters, shadow entries carrying workingset/memcg metadata, global `swapin_readahead_hits`, per-VMA `swap_readahead_info`, and `enable_vma_readahead`. Disk swap contents are read or written by page I/O, but this file owns the volatile cache that prevents duplicate reads and controls slot lifetime while cached.

Dependencies and integration points: depends on `swap_table.h`, `swap.h`, memcg swap charge/uncharge, workingset refault, folio allocation policy, block plugging, `softleaf` PTE decoding, page I/O, migration aops, shmem, zswap-invalidated slots through lower layers, and LRU drain from `swap.c`. Fault handling calls `swapin_readahead()` and later validates PTEs under page-table locks.

Risks and test signals: risks include stale PFN entries after folio free, racing duplicate swapin, large-folio fallback when smaller cache folios exist, wrong shadow/count preservation on deletion, readahead dereferencing PTEs without proper unmap, memcg charge failure cleanup, and swapoff races when no device reference is held. Test signals include swap fault stress, THP/mTHP swapin fallback, workingset refault accounting, VMA readahead sysfs toggling, swapoff during fault/readahead, KSM and migration interactions, and debug VM checks for locked folios and swap entry matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/swap_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/swap_table.h -->
# sources/distributed-fs/ceph-client/mm/swap_table.h

Purpose: defines the compact atomic per-slot table used by each swap cluster. The table records whether a slot is free, bad, cached by a folio PFN, or represented by a shadow value, and embeds a small swap reference count into the high bits.

Important APIs and types: `struct swap_table` is an array of `atomic_long_t entries[SWAPFILE_CLUSTER]`. Encoding helpers include `null_to_swp_tb()`, `pfn_to_swp_tb()`, `folio_to_swp_tb()`, and `shadow_to_swp_tb()`. Classifiers include `swp_tb_is_null()`, `swp_tb_is_folio()`, `swp_tb_is_shadow()`, `swp_tb_is_bad()`, and `swp_tb_is_countable()`. Extractors include `swp_tb_to_folio()`, `swp_tb_to_shadow()`, `swp_tb_get_count()`, and `__swp_tb_mk_count()`. Cluster-table accessors are `__swap_table_set()`, `__swap_table_xchg()`, `__swap_table_get()`, and RCU-safe `swap_table_get()`.

Control flow: swap allocator, swap cache, and swapoff code lock a cluster and use the double-underscore helpers to mutate entries. Lockless readers use `swap_table_get()` inside an RCU read-side critical section; freed page-backed tables are RCU-delayed. Counts sit in the upper bits and either fit directly or, when saturated at `SWP_TB_COUNT_MAX`, are extended by `swap_cluster_info.extend_table` in `swapfile.c`.

State and persistence: each entry is a single machine word. Null means allocatable, shadow means swapped out without cache and may carry an `xa_value`, PFN means the slot is cached by a folio and carries the same count bits, and bad reserves header/hole/bad-page slots. The table is volatile kernel metadata rebuilt on swapon and freed on swapoff; it describes persistent swap slots but is not itself stored on disk.

Dependencies and integration points: depends on `swap.h` for cluster metadata and cluster size, XArray value encoding for shadows, PFN width macros, RCU, and atomics. It is central to `swap_state.c` cache lookup and `swapfile.c` allocation/count/free logic.

Risks and test signals: risks include bit-layout overlap between PFNs and count bits on high-physical-address systems, mistaking `xa_value` shadows for PFN markers, count underflow/overflow, reading a table after free without RCU protection, and storing bad entries where countable entries are expected. Test with large physical address configs, `SWP_TABLE_USE_PAGE` true/false, swap count overflow into extend tables, bad-page swap headers, lockdep for cluster-held mutations, and RCU/KASAN stress during swapoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/swap_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/swapfile.c -->
# sources/distributed-fs/ceph-client/mm/swapfile.c

Purpose: implements swap device lifecycle, swap extent mapping, swap slot allocation/freeing, swap count management, swapoff unuse, `/proc/swaps`, hibernation swap helpers, discard/reclaim work, and global swap accounting. It is the central allocator and owner of `swap_info_struct` state.

Important APIs and functions: public or cross-file entry points include `folio_alloc_swap()`, `folio_dup_swap()`, `folio_put_swap()`, `get_swap_device()`, `__swap_cluster_free_entries()`, `__swap_count()`, `swap_entry_swapped()`, `swp_swapcount()`, `folio_free_swap()`, `swap_put_entries_direct()`, `add_swap_extent()`, `swapon`, `swapoff`, `si_swapinfo()`, `swap_dup_entry_direct()`, hibernation helpers `swap_alloc_hibernation_slot()`, `swap_free_hibernation_slot()`, `swap_type_of()`, `find_first_swap()`, `swapdev_block()`, and `count_swap_pages()`. Internal core helpers include cluster list movement, table allocation/freeing, discard, reclaim, allocation scanning, count overflow handling, `try_to_unuse()`, `setup_swap_extents()`, `setup_swap_clusters_info()`, and `read_swap_header()`.

Control flow: swapon allocates or reuses a `swap_info_struct`, opens and claims the file/block device, rejects unsuitable files, reads and validates the swap header, builds extent mappings, initializes cluster metadata and bad slots, allocates memcg/zeromap/zswap state, configures discard and rotational flags, marks `S_SWAPFILE`, assigns priority, resurrects the percpu reference, and publishes the device to active/available lists. Swap allocation first tries the current CPU’s order-specific cached cluster, then rotates through the priority-ordered available device list, scanning free, nonfull, fragmented, or reclaimed full clusters according to device flags and folio order. Allocation inserts the folio into swap cache with count zero; later duplicate paths increment counts when PTEs reference slots. Put/free paths decrement counts, batch free noncached count-one entries, reclaim cache when appropriate, invalidate zswap/arch/zeromap state, return clusters to free/nonfull/discard lists, and update global free counts. Swapoff removes the device from allocation lists, waits for in-flight allocation, walks shmem and every mm to fault swap entries back in, reclaims leftover swap cache, kills the percpu ref, flushes work and per-CPU cluster caches, frees extent/cluster/cgroup/zswap state, clears `S_SWAPFILE`, and releases `SWP_USED`.

State and persistence: global state includes `swap_info[]`, `nr_swapfiles`, `nr_swap_pages`, `total_swap_pages`, active and available priority lists, `swap_lock`, `swap_avail_lock`, per-CPU cluster cursors, `nr_rotate_swap`, procfs poll event state, and optional `swap_table_cachep`. Per-device state includes flags, priority, extents, cluster lists by order/state, cluster tables, overflow count tables, zeromap, work items, block device/file references, and percpu ref `users`. Persistent data is the swap area contents and header; this file protects when disk slots can be reused and prevents ordinary file writes through `S_SWAPFILE`.

Dependencies and integration points: integrates with block devices, filesystem `swap_activate`/`swap_deactivate`, generic swapfile activation, zswap, memcg swap accounting, swap cgroup maps, swap cache in `swap_state.c`, page table softleaf encoding, KSM, rmap, shmem, hibernation, blkcg throttling, procfs, security/capability checks, OOM accounting, discard workqueues, and architecture swap invalidation/restore hooks.

Risks and test signals: high-risk areas include list/flag consistency for clusters, deadlocks across `swap_lock`, `swap_avail_lock`, `si->lock`, cluster locks, and per-CPU local locks; swapoff races with lockless table readers; count overflow table allocation rollback; large-order allocation crossing cluster/order constraints; discard clusters visible to stale per-CPU cursors; swapon error unwinding leaks; swapoff retry behavior under memory pressure; and bad-slot/header accounting. Test signals include swapon/swapoff stress with concurrent faults and reclaim, THP swap on block devices and rejection on swapfiles, bad-page headers, discard-once/discard-pages policies, zswap invalidation, memcg swap accounting, hibernation slot allocation/free, `/proc/swaps` polling, swap count overflow, KSM swapoff, and lockdep/KASAN/RCU debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/swapfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/tests/lazy_mmu_mode_kunit.c -->
# sources/distributed-fs/ceph-client/mm/tests/lazy_mmu_mode_kunit.c

Purpose: provides a small KUnit test suite for lazy MMU mode state transitions exported from page-table code. It verifies active/inactive behavior, nested enable/disable handling, and pause/resume behavior.

Important APIs and functions: test helpers `expect_not_active()` and `expect_active()` assert `is_lazy_mmu_mode_active()`. The single test case `lazy_mmu_mode_active()` exercises `lazy_mmu_mode_enable()`, `lazy_mmu_mode_disable()`, `lazy_mmu_mode_pause()`, and `lazy_mmu_mode_resume()`. The suite is registered with `kunit_test_suite(lazy_mmu_mode_test_suite)` and imports the `EXPORTED_FOR_KUNIT_TESTING` namespace.

Control flow: the test starts inactive, enables lazy MMU mode, enters a nested enable/disable region and verifies the outer enable remains active, pauses the mode and verifies nested enable/disable and nested pause/resume do not reactivate while paused, resumes and verifies the original active state returns, then disables and verifies inactive state.

State and persistence: no persistent state is owned by the test. It observes and mutates the current task or CPU-local lazy MMU mode state provided by `<linux/pgtable.h>` APIs and expects cleanup to restore inactive state by test end.

Dependencies and integration points: depends on KUnit, page-table lazy MMU APIs, and namespace-exported testing symbols. It is a regression signal for architecture/generic MMU batching code that uses lazy page-table update modes.

Risks and test signals: risk is narrow coverage: it checks logical nesting and pause semantics but not concurrent tasks, preemption, architecture TLB side effects, or error paths. Useful signals are KUnit pass/fail on configs exposing the lazy MMU helpers, namespace import failures, and regressions where pause incorrectly drops nesting state or enable leaks across test completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/tests/lazy_mmu_mode_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/truncate.c -->
# sources/distributed-fs/ceph-client/mm/truncate.c

Purpose: implements page-cache truncation and invalidation for address spaces. It removes or invalidates folios and exceptional entries over byte or page ranges, handles partial-folio zeroing/splitting, coordinates mapped page unmapping, and provides filesystem-facing helpers for truncate, hole punch, inode eviction, and stronger invalidate operations.

Important APIs and functions: exported functions include `folio_invalidate()`, `truncate_inode_pages_range()`, `truncate_inode_pages()`, `truncate_inode_pages_final()`, `invalidate_mapping_pages()`, `invalidate_inode_pages2_range()`, `invalidate_inode_pages2()`, `truncate_pagecache()`, `truncate_setsize()`, `pagecache_isize_extended()`, `truncate_pagecache_range()`, plus `generic_error_remove_folio()`. Important internal helpers are `clear_shadow_entries()`, `truncate_folio_batch_exceptionals()`, `truncate_cleanup_folio()`, `truncate_inode_folio()`, `try_folio_split_or_unmap()`, `truncate_inode_partial_folio()`, `mapping_evict_folio()`, `mapping_try_invalidate()`, `folio_launder()`, and `folio_unmap_invalidate()`.

Control flow: range truncation first performs a nonblocking locked-entry pass over fully covered indices, removes exceptional entries, cleans folios, and deletes them in batches. It then handles partial start/end folios by waiting for writeback, zeroing invalidated bytes, calling filesystem invalidation hooks, and splitting or unmapping large folios as needed. A second pass waits on writeback and locks remaining folios to force removal. Invalidation paths are less destructive: `mapping_try_invalidate()` removes clean unused folios and shadow entries without blocking heavily, while `invalidate_inode_pages2_range()` unmaps mapped folios, launders dirty data through filesystem hooks, releases private state, and returns `-EBUSY` if guarantees cannot be met.

State and persistence: state includes `mapping->i_pages` XArray entries, folio dirty/writeback/mapped/private/LRU state, inode shrinker-list membership, address-space exiting state, and page-table mappings. The file does not persist data itself, but ordering is critical because filesystems rely on page cache being coherent before disk blocks are freed or after file size changes.

Dependencies and integration points: depends on XArray page cache, `filemap` removal helpers, filesystem `address_space_operations` (`invalidate_folio`, `launder_folio`, `free_folio`), DAX exceptional entries, shmem special handling, rmap unmapping, LRU deactivation from `swap.c`, writeback state, inode locks and invalidate locks held by callers, and `mapping_min_folio_order()` for large folio splitting constraints.

Risks and test signals: risks include leaving dirty or writeback data beyond EOF, DAX exceptional entries causing truncate loops, partial large folios failing to split and violating SIGBUS expectations, racing reclaim or tmpfs swapper-space remapping, incorrect private-data release, invalidating COW pages during hole punch, and missing the second unmap in truncate. Test signals include filesystem truncate/hole-punch/fsx tests, mmap-after-truncate SIGBUS behavior, DAX invalidation tests, shmem large-folio truncation, dirty writeback races, memory-failure page removal, inode eviction with AS_EXITING, and lockdep around page-cache XArray and inode locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/truncate.c -->
