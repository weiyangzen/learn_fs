# Group Research: group_908_linux_sources_os_linux_linux_mm_sparse_vmemmap_c_sources_os_linux_li_55c8b1a90e9a

Scope: `Docs/research_subset_a.md` / Linux `mm` sparse memory, swap, swap cache, swapfile, lazy MMU KUnit, and page-cache truncation. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/sparse-vmemmap.c -->
# File Research: sources/os/linux/linux/mm/sparse-vmemmap.c

## Purpose
Implements SPARSEMEM VMEMMAP backing for `struct page` arrays. It allocates memory and page tables for the virtual memmap, supports base-page and huge-PMD mappings, handles alternate memmap storage for device memory, optimizes hugetlb/devmap compound-page tails, and supports memory hotplug section activation/removal.

## Main Interfaces
- Allocation helpers: `vmemmap_alloc_block()`, `vmemmap_alloc_block_buf()`, `altmap_alloc_block_buf()`.
- Page-table population: `vmemmap_pgd_populate()`, `vmemmap_p4d_populate()`, `vmemmap_pud_populate()`, `vmemmap_pmd_populate()`, `vmemmap_pte_populate()`.
- Mapping entry points: `vmemmap_populate_basepages()`, `vmemmap_populate_hugepages()`, `__populate_section_memmap()`.
- Hugetlb optimized vmemmap support: `vmemmap_wrprotect_hvo()`, `vmemmap_populate_hvo()`.
- Sparse section state: `sparse_init_subsection_map()`, `sparse_add_section()`, `sparse_remove_section()`.
- Hotplug section state: `online_mem_sections()`, `offline_mem_sections()`.

## Control Flow
Early boot allocations use memblock via `memmap_alloc()`, while later allocation uses `alloc_pages_node()` with retry/no-warn semantics. VMEMMAP population walks the kernel page-table hierarchy and installs PTEs for `struct page` backing, optionally using a supplied physical page frame when deduplicating tail page structs.

Hugepage population first tries PMD-sized vmemmap backing through arch hooks, then falls back to base PTE mappings. Hugetlb optimized vmemmap maps head page structs normally and reuses one tail `struct page` backing page for the rest. Device compound-page population similarly maps head/tail pages and reuses tail backing across sections when appropriate.

Memory hotplug activates subsections by allocating section usage metadata, setting subsection bitmaps, populating memmap backing unless an early section can be reused, poisoning uninitialized page structs, and marking the section present. Removal clears subsection bits, frees vmemmap backing when safe, and releases non-boot usage metadata via RCU.

## State And Synchronization
Uses `mem_section->usage->subsection_map`, `SECTION_HAS_MEM_MAP`, `SECTION_IS_ONLINE`, early-section flags, and per-zone `vmemmap_tails`. PTE page references are incremented for specific ZONE_DEVICE compound reuse paths so later page-table freeing pairs with `put_page_testzero()`.

## Dependencies
Depends on sparsemem section helpers, memblock/slab allocation, kernel page-table APIs, altmap/device pagemap metadata, hugetlb vmemmap optimization, memory hotplug, and architecture-provided `vmemmap_populate()`, `vmemmap_set_pmd()`, `vmemmap_check_pmd()`, and `vmemmap_free()` behavior.

## Risks And Review Focus
- Altmap sizing/alignment failures are treated as hard failures in hugepage paths.
- Tail-page deduplication relies on strict population ordering and correct page ref ownership.
- Hotplug subsection bitmap transitions must stay consistent with `valid_section()` and RCU freeing of usage maps.
- Early sections are special because their memmap is assumed fully populated and boot-allocated usage maps may be shared.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/sparse-vmemmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/sparse.c -->
# File Research: sources/os/linux/linux/mm/sparse.c

## Purpose
Provides generic SPARSEMEM initialization. It records present physical memory sections, allocates `mem_section` roots for extreme sparsemem, allocates per-section usage metadata and memmap backing, initializes sections by NUMA node, and exposes sparsemem sizing helpers.

## Main Interfaces
- Global section storage: `mem_section`.
- Section index setup: `sparse_index_init()`.
- Section presence: `memory_present()`, `memblocks_present()`.
- Sizing helpers: `mem_section_usage_size()`, `section_map_size()`.
- Boot allocation buffer: `sparse_buffer_init()`, `sparse_buffer_alloc()`, `sparse_buffer_fini()`.
- Section init: `sparse_init_early_section()`, `sparse_init_nid()`, `sparse_init()`.

## Control Flow
Boot memory ranges are enumerated by `for_each_mem_pfn_range()` and rounded to section boundaries. Each present section gets an index initialized, a node id recorded, and early presence flags stored in `section_mem_map`.

`sparse_init()` groups contiguous present sections by early NUMA node id, initializes pageblock order, and calls `sparse_init_nid()` per node range. Per-node initialization allocates a contiguous usage buffer, prepares a memmap backing buffer aligned for the selected sparsemem mode, allows VMEMMAP preinit hooks, then populates and initializes each non-preinitialized section.

If allocation fails partway through a node range, later uninitialized present sections are cleared so unavailable memory is not exposed.

## State And Synchronization
Before real memmap installation, `section_mem_map` temporarily stores encoded NUMA node information. For `NODE_NOT_IN_PAGE_FLAGS`, `section_to_node_table` maps section numbers to node ids. `__highest_present_section_nr` tracks the highest present section so section iteration can stop early.

## Dependencies
Uses memblock, sparsemem section helpers, NUMA memory ranges, vmstat memmap accounting, VMEMMAP hooks from `sparse-vmemmap.c`, and boot-time pageblock setup.

## Risks And Review Focus
- `section_mem_map` has dual early/real meaning, so ordering of node-id clearing and section initialization matters.
- Allocation failure handling intentionally hides remaining sections; partial initialization must not leave invalid present sections.
- VMEMMAP and non-VMEMMAP modes have different memmap backing alignment requirements.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/sparse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/swap.c -->
# File Research: sources/os/linux/linux/mm/swap.c

## Purpose
Implements core folio LRU batching, activation/deactivation/lazyfree transitions, batched folio release, memcg LRU reparenting, and VM swap clustering sysctl setup. Despite the filename, this is primarily LRU/page-cache folio lifecycle code rather than swap slot allocation.

## Main Interfaces
- Folio release: `__folio_put()`, `folios_put_refs()`, `release_pages()`, `__folio_batch_release()`.
- LRU operations: `folio_add_lru()`, `folio_add_lru_vma()`, `folio_mark_accessed()`, `folio_activate()`, `folio_deactivate()`, `deactivate_file_folio()`, `folio_mark_lazyfree()`, `folio_rotate_reclaimable()`.
- Drain operations: `lru_add_drain()`, `lru_add_drain_cpu()`, `lru_add_drain_all()`, `lru_cache_disable()`.
- Cost accounting: `lru_note_cost_unlock_irq()`, `lru_note_cost_refault()`.
- Setup: `swap_setup()` and the `vm/page-cluster` sysctl.

## Control Flow
Per-CPU `cpu_fbatches` collect folios for LRU add, activation, file deactivation, anonymous deactivation, lazyfree, and tail rotation. Operations take a folio reference, queue it into the current CPU batch, and drain when the batch fills or LRU caching is disabled.

Draining locks the target `lruvec`, performs the requested move, updates folio LRU flags and VM/memcg counters, then drops queued folio references in bulk. SMP global draining uses a generation counter and per-CPU workqueue to avoid missed batches under concurrent callers.

Folio release removes folios from LRU, handles zone-device and hugetlb special cases, uncharges memcg, frees deferred split state, and returns pages in batches to the allocator.

## State And Synchronization
Uses local locks for per-CPU folio batches, IRQ-disabling local lock for reclaimable tail rotation, lruvec locks for list mutation, RCU for LRU disable synchronization, and memcg LRU state for reparenting. Multi-gen LRU builds use reference-generation bits instead of classic active/referenced transitions.

## Dependencies
Depends on memcg, workingset, mlock, buffer-head LRU draining, page idle tracking, folio batching, page allocator freeing, and tracepoints from `trace/events/pagemap.h`.

## Risks And Review Focus
- LRU batch draining has subtle barriers and generation logic to prevent missed remote batches.
- Activation of folios still in a local add batch must avoid modifying remote batches and accounting incorrectly.
- `lru_cache_disable()` depends on RCU/preemption guarantees before migration or isolation.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/swap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/swap.h -->
# File Research: sources/os/linux/linux/mm/swap.h

## Purpose
Internal MM swap header defining swap cluster metadata, cluster flags, locking helpers, swap cache APIs, swap I/O hooks, readahead APIs, and no-op stubs for non-`CONFIG_SWAP` builds.

## Main Interfaces
- Cluster structure: `struct swap_cluster_info`.
- Cluster flags: `CLUSTER_FLAG_FREE`, `NONFULL`, `FRAG`, `FULL`, `DISCARD`.
- Lookup helpers: `__swap_type_to_info()`, `__swap_entry_to_info()`, `__swap_offset_to_cluster()`.
- Locking helpers: `swap_cluster_lock()`, `swap_cluster_get_and_lock()`, IRQ variants, unlock variants.
- Swap slot APIs: `folio_alloc_swap()`, `folio_dup_swap()`, `folio_put_swap()`.
- Swap cache APIs: `swap_cache_get_folio()`, `swap_cache_has_folio()`, `swap_cache_get_shadow()`, `swap_cache_del_folio()`, `__swap_cache_add_folio()`, `__swap_cache_replace_folio()`.
- Swap I/O and readahead: `swap_read_folio()`, `swap_writeout()`, `swap_cluster_readahead()`, `swapin_readahead()`, `swapin_folio()`.

## Control Flow
The header codifies the core synchronization contract: callers must validate entries and stabilize the swap device by holding a swap device reference, holding a locked swap-cache folio, or holding another lock protecting a swap entry such as a page-table lock.

Cluster locks protect cluster metadata and corresponding swap table entries. Locked swap-cache folios pin their swap slots, and folio-level swap APIs require locked folios to prevent entries from changing while counts or cache state are updated.

## State And Synchronization
`struct swap_cluster_info` owns a spinlock, slot count, cluster order, list flag, RCU-protected swap table pointer, optional overflow count table, and list linkage. Helpers warn on races with swapoff via `percpu_ref_is_zero(&si->users)`.

## Dependencies
Used by `swapfile.c`, `swap_state.c`, `page_io.c`, reclaim, fault, and migration code. Depends on `swapops`, folios, mempolicy, block I/O, and the per-cluster swap table declared in `swap_table.h`.

## Risks And Review Focus
- The documented stabilization rules are critical; using swap cache helpers without a device ref or equivalent lock can race with swapoff.
- Large folios must stay within one cluster for `swap_cluster_get_and_lock()` assumptions.
- Non-`CONFIG_SWAP` stubs intentionally return inert values and must match caller expectations.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/swap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/swap_cgroup.c -->
# File Research: sources/os/linux/linux/mm/swap_cgroup.c

## Purpose
Tracks the memory cgroup id associated with swap entries. It stores compact per-swap-slot cgroup IDs so swap accounting can identify the charged memcg after a folio has been swapped out.

## Main Interfaces
- `swap_cgroup_record()` records one folio’s cgroup id across its swap entries.
- `swap_cgroup_clear()` clears and returns the old id across a range.
- `lookup_swap_cgroup_id()` reads the id for one swap entry.
- `swap_cgroup_swapon()` allocates the per-swap-device map.
- `swap_cgroup_swapoff()` frees the map.

## Control Flow
Each `struct swap_cgroup` is an `atomic_t` packing multiple `unsigned short` ids. Lookup shifts and masks the packed word. Updates use an atomic compare-exchange loop so two ids sharing the same packed word can be changed safely.

Swapon allocates a zeroed vmalloc map sized for the swap area, then publishes it under `swap_cgroup_mutex`. Swapoff clears the pointer under the same mutex and vfree’s the map.

## State And Synchronization
State is held in `swap_cgroup_ctrl[MAX_SWAPFILES]`. Packed id updates are atomic; map pointer publication/removal is mutex-protected. Functions become no-ops or return zero when memcg is disabled.

## Dependencies
Depends on memcg swap accounting, `swp_type()`/`swp_offset()` from swapops, vmalloc allocation, and swapfile lifecycle hooks.

## Risks And Review Focus
- `swap_cgroup_record()` assumes entries for the folio were not already charged and asserts old ids are zero.
- `swap_cgroup_clear()` assumes all entries in the cleared range share the same id.
- ID width is `unsigned short`, so it depends on memcg id allocation fitting that representation.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/swap_cgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/swap_state.c -->
# File Research: sources/os/linux/linux/mm/swap_state.c

## Purpose
Implements the swap cache and swapin readahead. It maps swap entries to cached folios via per-cluster swap tables, manages swap-cache shadows for workingset refaults, prepares folios for swapin/zswap writeback, and provides cluster-based or VMA-based swap readahead.

## Main Interfaces
- Swap cache lookup: `swap_cache_get_folio()`, `swap_cache_has_folio()`, `swap_cache_get_shadow()`.
- Cache mutation: `__swap_cache_add_folio()`, `swap_cache_del_folio()`, `__swap_cache_del_folio()`, `__swap_cache_replace_folio()`.
- Free helpers: `free_swap_cache()`, `free_folio_and_swap_cache()`, `free_pages_and_swap_cache()`.
- Swapin allocation/read: `swap_cache_alloc_folio()`, `swapin_folio()`, `read_swap_cache_async()`.
- Readahead: `swap_update_readahead()`, `swap_cluster_readahead()`, `swapin_readahead()`.
- Sysfs: `mm/swap/vma_ra_enabled`.

## Control Flow
Swap-cache lookups read the per-cluster swap table under RCU and try to take a folio reference if the table entry encodes a PFN. Adding a folio validates the slots are present and not already cached, preserves any shadow, installs PFN entries, sets folio swapcache state, and accounts `NR_SWAPCACHE`.

Deleting a folio replaces PFN entries with shadow entries that preserve swap count, clears folio swapcache state, updates stats, and frees slots whose count is zero. Replacement updates PFN entries to point at a new folio while preserving counts.

Swapin first checks cache, verifies the slot is still swapped, allocates an order-0 folio under NUMA policy, charges memcg, adds it to swap cache, accounts memcg v1 swapin, handles workingset refault from a shadow, and starts swap I/O if it created the folio.

Readahead either reads a physical swap cluster based on `page_cluster` and recent hit counts, or scans neighboring PTEs in the faulting VMA and swaps in nearby entries. Readahead folios are marked with `PG_readahead` for later hit accounting.

## State And Synchronization
`swap_space` is a synthetic address space for swap cache writeback/reclaim paths. Swap cache entries are stored in `struct swap_table`, not the address-space XArray. Folio locks stabilize folio swap entries; cluster locks serialize table mutation; swap device references protect against swapoff.

## Dependencies
Uses swap table encoding, memcg swapin charging, workingset shadows, swap I/O plugs, NUMA mempolicy, fault VMA/PTE walking, shmem/migration address-space operations, and sysfs kobjects.

## Risks And Review Focus
- Large folio swapin intentionally falls back on races because aligned entries can conflict with smaller cached folios.
- Swap-cache deletion must preserve counts and free only truly unreferenced slots.
- VMA readahead walks lockless PTEs and must grab swap device refs for entries from non-target devices.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/swap_state.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/swap_table.h -->
# File Research: sources/os/linux/linux/mm/swap_table.h

## Purpose
Defines the per-cluster swap table format and helpers. The table is a 1:1 atomic entry array for slots in one `SWAPFILE_CLUSTER`, encoding free, shadow, cached folio PFN, reserved pointer marker, and bad-slot states with embedded swap counts.

## Main Interfaces
- Table type: `struct swap_table`.
- Encoders: `null_to_swp_tb()`, `pfn_to_swp_tb()`, `folio_to_swp_tb()`, `shadow_to_swp_tb()`.
- Type checks: `swp_tb_is_null()`, `swp_tb_is_folio()`, `swp_tb_is_shadow()`, `swp_tb_is_bad()`, `swp_tb_is_countable()`.
- Decoders: `swp_tb_to_folio()`, `swp_tb_to_shadow()`, `swp_tb_get_count()`.
- Locked table access: `__swap_table_set()`, `__swap_table_xchg()`, `__swap_table_get()`.
- RCU read access: `swap_table_get()`.

## Control Flow
A null entry is free. A shadow entry uses the XArray value encoding and carries a swap count plus optional workingset/memcg shadow value. A PFN entry points to the cached folio backing the slot and carries a swap count. A bad entry reserves unusable slots such as the swap header or holes.

Counts occupy high bits and can represent normal countable states up to `SWP_TB_COUNT_MAX`; overflow counts are stored externally in the cluster extension table owned by `swapfile.c`.

## State And Synchronization
The table pointer is RCU-protected through `swap_cluster_info->table`. Mutating helpers require the cluster lock. `swap_table_get()` safely reads through RCU and returns null if a cluster table is absent.

## Dependencies
Used by `swapfile.c` for allocation/count/free and by `swap_state.c` for cache lookup/mutation. Depends on folio PFN conversion, XArray value encoding, atomic longs, RCU, and cluster locking from `swap.h`.

## Risks And Review Focus
- Bit layout must fit PFN width plus marker bits plus count bits on every architecture.
- Shadow encoding relies on XArray value representation matching `SWP_TB_SHADOW_MARK`.
- Readers must verify the decoded folio is still refcountable and still matches the swap entry after locking.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/swap_table.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/swapfile.c -->
# File Research: sources/os/linux/linux/mm/swapfile.c

## Purpose
Implements swap device lifecycle, swap slot allocation/freeing/counting, swapoff unuse, swap extent mapping, discard/reclaim handling, hibernation swap helpers, `/proc/swaps`, and swapon/swapoff syscalls.

## Main Interfaces
- Allocation/counting: `folio_alloc_swap()`, `folio_dup_swap()`, `folio_put_swap()`, `swap_dup_entry_direct()`, `swap_put_entries_direct()`.
- Device refs: `get_swap_device()`, `put_swap_device()` via percpu refs.
- Cache freeing: `folio_free_swap()`, `__swap_cluster_free_entries()`.
- Swapoff: `try_to_unuse()`, `SYSCALL_DEFINE1(swapoff)`.
- Swapon: `SYSCALL_DEFINE2(swapon)`, `setup_swap_extents()`, `setup_swap_clusters_info()`.
- Extents and sectors: `add_swap_extent()`, `swap_folio_sector()`, `swapdev_block()`.
- Hibernation: `swap_alloc_hibernation_slot()`, `swap_free_hibernation_slot()`, `swap_type_of()`, `count_swap_pages()`.
- Accounting/output: `si_swapinfo()`, `/proc/swaps`.
- Initialization: `swapfile_init()`.

## Control Flow
Swapon allocates or reuses a `swap_info_struct`, opens the file/device, rejects unsupported files, reads and validates the swap header, builds swap extents, initializes cluster metadata and bad slots, allocates cgroup and zeromap state, configures discard/SSD/synchronous flags, initializes zswap, marks the inode `S_SWAPFILE`, sets priority, resurrects the percpu ref, and exposes the device on active/available priority lists.

Swap allocation first tries the current CPU’s cached cluster for the folio order, then rotates through priority-ordered available devices. HDD swap uses a per-device global cluster cursor; SSD swap uses per-CPU cursors. Clusters are kept on free, nonfull, fragmented, full, and discard lists. Allocation installs swap-cache PFN entries for folio-backed swapout or shadow placeholders for hibernation slots, updates usage counters, and removes full devices from the available list.

Counts are embedded in swap table entries up to `SWP_TB_COUNT_MAX`; larger counts use a per-cluster extension table. Decrementing counts batch-frees noncached slots and can reclaim cached slots when unmapped or swap is full.

Swapoff removes the device from allocation lists, waits for in-flight allocation locks, walks shmem and all process address spaces to replace swap PTEs with folios, drains residual swap-cache-only entries, kills the device percpu ref, waits for RCU and users, flushes discard/reclaim work, frees extents/cluster info/cgroup/zeromap/zswap state, clears `S_SWAPFILE`, and finally clears `SWP_USED`.

## State And Synchronization
Global `swap_lock` protects `swap_info`, active list, `SWP_USED`, `SWP_WRITEOK`, and total swap pages. `swap_avail_lock` protects the available priority list. Each cluster has its own lock for swap table/count/list-flag state. Per-device percpu refs prevent swapoff while entries are in use. Per-CPU cluster caches are protected by a local lock.

## Dependencies
Interacts with `swap_state.c` for cache entries, `swap_table.h` for slot encoding, `swap_cgroup.c`, zswap, memcg, shmem, KSM, rmap, PTE walking, block discard, filesystem `swap_activate`/`swap_deactivate`, security memory accounting, hibernation, procfs, and architecture swap hooks.

## Risks And Review Focus
- Lock ordering across `swap_lock`, `swap_avail_lock`, `si->lock`, cluster locks, and per-CPU local locks is central to correctness.
- Swapoff must prevent new allocations, handle reinserted entries under pressure, and wait for RCU/refcount users before freeing tables.
- Count overflow allocation can fail in atomic contexts and must roll back partial increments.
- Discard clusters are intentionally isolated from allocation until discard completes.
- Large folio allocation is restricted to block-device swap and same-order clusters.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/swapfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/tests/lazy_mmu_mode_kunit.c -->
# File Research: sources/os/linux/linux/mm/tests/lazy_mmu_mode_kunit.c

## Purpose
KUnit coverage for lazy MMU mode state tracking. It verifies activation, nested activation, pause/resume behavior, and disabled state restoration.

## Main Interfaces
- Test helpers: `expect_not_active()`, `expect_active()`.
- Test case: `lazy_mmu_mode_active()`.
- Suite: `lazy_mmu_mode_test_suite`.

## Control Flow
The test starts with lazy MMU mode inactive, enables it, verifies nested enable/disable keeps it active until the outer disable, pauses it and verifies it appears inactive, confirms enable/disable/pause/resume calls have no effect while paused, resumes to restore active state, then disables to return inactive.

## State And Synchronization
Exercises exported lazy MMU mode state via `is_lazy_mmu_mode_active()`, `lazy_mmu_mode_enable()`, `lazy_mmu_mode_disable()`, `lazy_mmu_mode_pause()`, and `lazy_mmu_mode_resume()`.

## Dependencies
Imports the `EXPORTED_FOR_KUNIT_TESTING` namespace and depends on `<linux/pgtable.h>` lazy MMU mode helpers plus KUnit.

## Risks And Review Focus
- The test validates nesting and pause masking semantics but does not cover concurrent use.
- Correctness depends on balanced enable/disable and pause/resume state transitions.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/tests/lazy_mmu_mode_kunit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/truncate.c -->
# File Research: sources/os/linux/linux/mm/truncate.c

## Purpose
Implements page-cache truncation and invalidation for address spaces. It removes folios and exceptional entries, handles partial folios on truncate/hole-punch, supports stronger invalidation for direct I/O and filesystem coherency, and updates page cache when file size changes.

## Main Interfaces
- Exceptional cleanup: `clear_shadow_entries()`, `truncate_folio_batch_exceptionals()`.
- Folio invalidation/removal: `folio_invalidate()`, `truncate_inode_folio()`, `truncate_inode_partial_folio()`, `mapping_evict_folio()`, `folio_unmap_invalidate()`.
- Truncation: `truncate_inode_pages_range()`, `truncate_inode_pages()`, `truncate_inode_pages_final()`.
- Invalidation: `mapping_try_invalidate()`, `invalidate_mapping_pages()`, `invalidate_inode_pages2_range()`, `invalidate_inode_pages2()`.
- Page-cache size helpers: `truncate_pagecache()`, `truncate_setsize()`, `pagecache_isize_extended()`, `truncate_pagecache_range()`.
- Memory failure helper: `generic_error_remove_folio()`.

## Control Flow
Range truncation first removes fully covered locked folios in a nonblocking pass, processes partial start/end folios by zeroing invalidated ranges and splitting large folios when necessary, then performs a second pass that waits on writeback and removes remaining folios. Exceptional XArray entries are cleared except for shmem-managed entries and DAX-specific handling.

Partial folios are zeroed where accessible, invalidated through filesystem callbacks if needed, and split at truncation boundaries to preserve SIGBUS and hole semantics. If splitting fails, non-shmem mappings are unmapped so future faults occur at PTE granularity.

Invalidate paths differ by strength. `invalidate_mapping_pages()` removes clean, unlocked, evictable folios and shadow entries without blocking on I/O. `invalidate_inode_pages2_range()` unmaps mapped folios, waits for writeback, launders dirty folios through filesystem callbacks, releases private data, and returns `-EBUSY` if invalidation cannot complete.

File-size helpers unmap and truncate pagecache before filesystem block release, handle extension over sub-page block boundaries by write-protecting/dirtying the straddling folio, and zero newly exposed post-EOF ranges.

## State And Synchronization
Uses the mapping XArray, folio locks, inode `i_lock`, `mapping->i_pages` xarray lock, writeback waits, and filesystem `a_ops` callbacks. Final truncation marks the mapping exiting and cycles the XArray lock to avoid reclaim installing eviction state during inode teardown.

## Dependencies
Depends on filemap, folio batches, workingset shadow updates, shmem and DAX special cases, rmap unmapping, filesystem address-space operations, inode LRU shrinkability, and page-cache size management.

## Risks And Review Focus
- Large folio splitting and unmapping around partial truncation is subtle and affects SIGBUS/hole-punch semantics.
- DAX exceptional entries require filesystem coordination before truncation.
- Strong invalidation intentionally ignores transient references but must not remove dirty/private folios unsafely.
- `truncate_pagecache()` performs a second unmap for correctness with private COW pages racing truncation.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/truncate.c -->