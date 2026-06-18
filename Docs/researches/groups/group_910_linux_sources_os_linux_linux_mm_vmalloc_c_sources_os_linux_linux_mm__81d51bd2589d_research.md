# Group Research: group_910_linux_sources_os_linux_linux_mm_vmalloc_c_sources_os_linux_linux_mm__81d51bd2589d

Scope: `Docs/research_subset_a.md` / Linux `mm/vmalloc.c` and `mm/vmpressure.c`. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/vmalloc.c -->
# File Research: sources/os/linux/linux/mm/vmalloc.c

## Role

Linux kernel virtual mapping allocator and vmalloc implementation. This file owns kernel virtual address reservation, page-table population and teardown for vmalloc/vmap/ioremap-style mappings, lazy vmap-area purging, `vm_map_ram()` fast mappings, public `vmalloc()`/`vfree()` APIs, userspace remapping helpers, `/proc/vmallocinfo`, and boot-time vmalloc initialization.

## Key Behavior

- Provides low-level kernel page-table mapping helpers for physical ranges and page arrays:
  - `vmap_page_range()` and `ioremap_page_range()` map physical ranges, with optional huge vmap/ioremap mappings.
  - `vmap_pages_range()` maps arrays of `struct page *`, falling back to small-page mappings when huge vmalloc is unavailable or unsuitable.
  - `vunmap_range()` and no-flush variants tear down mappings and synchronize architecture kernel page tables when needed.
- Implements address translation helpers:
  - `is_vmalloc_addr()` and `is_vmalloc_or_module_addr()` classify vmalloc/module-space addresses.
  - `vmalloc_to_page()` walks kernel page tables, including huge p4d/pud/pmd mappings, to return the backing `struct page`.
  - `vmalloc_to_pfn()` derives PFNs from `vmalloc_to_page()`.
- Maintains the global kernel virtual address allocator:
  - Free space is represented by an augmented red-black tree plus an address-sorted list.
  - Busy and lazy areas are sharded across `vmap_node` instances to reduce contention on large systems.
  - Allocation finds the lowest matching free block, accounts for alignment, splits free areas into full/left/right/no-edge fits, and populates KASAN vmalloc shadow.
  - Freeing unlinks from busy state, lazily queues virtual ranges, batches TLB flushes, and eventually returns ranges to per-node pools or the global free tree.
- Provides small-allocation acceleration for `vm_map_ram()`:
  - Per-CPU `vmap_block_queue` objects hold block-sized vmalloc areas.
  - Suballocations are tracked by bitmaps in `struct vmap_block`.
  - Dirty freed subranges are lazily unmapped and flushed; fully dirty blocks are freed back through the vmap-area path.
- Exposes alias-flush control:
  - `vm_unmap_aliases()` purges outstanding lazy mappings so pages no longer have stale vmap TLB aliases.
  - Fragmented blocks and lazy areas are drained under `vmap_purge_lock`.
- Implements public mapping APIs:
  - `vm_map_ram()` / `vm_unmap_ram()` for short-lived linear mappings of page arrays.
  - `vmap()` / `vunmap()` for long-lived mappings of page arrays.
  - Optional `vmap_pfn()` for non-RAM PFN arrays.
  - `get_vm_area()`, `find_vm_area()`, `remove_vm_area()`, and `free_vm_area()` for reserved vmalloc-area management.
- Implements public allocation APIs:
  - `__vmalloc_node_range_noprof()` reserves virtual space, allocates physical pages, maps them, handles KASAN tagging/unpoisoning, and clears `VM_UNINITIALIZED`.
  - `vmalloc_noprof()`, `vzalloc_noprof()`, `vmalloc_user_noprof()`, NUMA variants, `vmalloc_32_noprof()`, and `vmalloc_32_user_noprof()` are wrappers around the core allocator.
  - `vmalloc_huge_node_noprof()` allows huge vmalloc mappings and falls back to base pages if huge mapping setup fails.
  - `vrealloc_node_align_noprof()` preserves contents while shrinking in place, reusing unused reserved space, or allocating/copying/freeing on growth or node mismatch.
- Handles freeing and safety:
  - `vfree()` removes the vm area, poisons KASAN vmalloc memory, optionally resets direct-map permissions for `VM_FLUSH_RESET_PERMS`, frees backing pages, and frees metadata.
  - `vfree_atomic()` defers freeing through per-CPU lockless lists and workqueues when called from atomic context.
  - `vm_reset_perms()` invalidates direct-map aliases, flushes aliases, and restores default direct-map permissions.
- Supports safe inspection/remapping:
  - `vread_iter()` safely reads arbitrary vmalloc ranges for debug users such as `/proc/kcore`, zero-filling holes, sparse areas, and ioremap areas.
  - `remap_vmalloc_range_partial()` and `remap_vmalloc_range()` validate `VM_USERMAP` or `VM_DMA_COHERENT` areas and insert backing pages into user VMAs.
- Supports percpu allocator virtual-area needs:
  - `pcpu_get_vm_areas()` allocates multiple congruent vmalloc areas top-down while preserving offsets.
  - `pcpu_free_vm_areas()` frees the returned area set.
- Exposes diagnostics:
  - `/proc/vmallocinfo` reports active vmalloc/vmap/ioremap/sparse/user/dma-coherent areas, NUMA page counts, and unpurged lazy areas.
  - `vmalloc_dump_obj()` prints allocation origin for objects inside vmalloc regions when printk support is enabled.
- Initializes the subsystem:
  - Early boot APIs register fixed vm areas before `vmalloc_init()`.
  - `vmalloc_init()` creates the `vmap_area` cache, initializes per-CPU block queues and deferred frees, imports early `vmlist` entries, builds the free tree, enables allocation, and registers a shrinker for pooled vmap nodes.

## Dependencies

Uses Linux MM page-table APIs, architecture huge-vmap/ioremap hooks, TLB/cache flush hooks, KASAN/KMSAN vmalloc integration, kmemleak, debugobjects/pagealloc, memcg/lruvec accounting, slab/kmalloc/vmalloc recursion, xarray, rbtrees with augmentation, per-CPU data, workqueues, notifiers, shrinkers, seq/procfs, iov iterators, NUMA helpers, and percpu allocator interfaces.

## Research Notes

This file is both the virtual address allocator and the public vmalloc allocation layer. The central design tradeoff is batching: freed mappings are removed from the active trees quickly but their TLB cleanup and virtual address reuse are delayed to amortize global flush cost. The allocator has several layers of caching and sharding: augmented global free space for general allocation, per-node busy/lazy trees, small-size per-node pools, and per-CPU vmap blocks for `vm_map_ram()`.

Correctness depends on careful sequencing between page-table updates, cache/TLB flushing, KASAN shadow population/release, and visibility of initialized `vm_struct` state. The code is also defensive about contexts: normal `vfree()` can sleep, interrupt-context freeing is deferred, NMI freeing is rejected, and page-table allocation scopes are adjusted to avoid violating caller GFP constraints.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/vmalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/vmpressure.c -->
# File Research: sources/os/linux/linux/mm/vmpressure.c

## Role

Memory-cgroup VM pressure accounting and notification implementation. It converts reclaim scan/reclaim efficiency and reclaim priority into low/medium/critical pressure levels, signals registered eventfd listeners, propagates legacy subtree notifications up the memcg hierarchy, and informs in-kernel users such as socket memory pressure handling.

## Key Behavior

- Defines pressure thresholds:
  - A scan window of `SWAP_CLUSTER_MAX * 16` pages rate-limits low-level notifications and smooths medium/critical decisions.
  - Medium pressure begins at 60% reclaim inefficiency.
  - Critical pressure begins at 95% reclaim inefficiency.
  - Reclaim priority at or below `vmpressure_level_critical_prio` is treated as critical pressure.
- Calculates pressure from scanned and reclaimed pages:
  - Reclaimed pages greater than or equal to scanned pages produce low pressure.
  - Otherwise pressure is the percentage of scanning work that failed to reclaim memory.
- Maintains event registrations:
  - `vmpressure_register_event()` parses `low`, `medium`, or `critical`, plus optional `default`, `hierarchy`, or `local` mode, then links an eventfd to the memcg vmpressure object.
  - `vmpressure_unregister_event()` removes the matching eventfd registration.
- Delivers notifications:
  - `vmpressure_event()` filters events by level, ancestor/local mode, and default pass-through semantics before calling `eventfd_signal()`.
  - `vmpressure_work_fn()` drains accumulated tree counters, computes pressure, signals the current memcg, then walks ancestors until the root.
- Accounts reclaim pressure:
  - `vmpressure()` ignores disabled memcg, unsupported legacy non-tree in-kernel accounting, unsuitable GFP contexts, and zero-scanned events.
  - In legacy tree mode it accumulates subtree scanned/reclaimed counters and schedules work once the scan window is reached.
  - In default cgroup/in-kernel mode it tracks local memcg reclaim efficiency and sets socket pressure when pressure exceeds low.
- Accounts reclaim priority:
  - `vmpressure_prio()` injects a critical tree pressure event when reclaim priority is deep enough, using a full scan window with zero reclaimed pages.
- Initializes and cleans up per-memcg structures:
  - `vmpressure_init()` initializes locks, event list, and deferred work.
  - `vmpressure_cleanup()` flushes pending work before the containing memcg object is destroyed.

## Dependencies

Uses memcg and cgroup hierarchy helpers, eventfd, workqueues, spinlocks/mutexes, reclaim GFP masks, swap/vmscan constants, printk debug tracing, and socket pressure integration through memory cgroup helpers.

## Research Notes

`vmpressure.c` is a policy bridge from reclaim behavior to notifications. It intentionally reports only pressure that userspace can plausibly help with, filtering out reclaim constrained to zones such as DMA-only pressure. Legacy userspace notifications use subtree accounting and eventfd propagation, while cgroup v2 in-kernel users use local reclaim efficiency and do not signal root-level pressure.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/vmpressure.c -->