# sources/distributed-fs/ceph-client/mm/vmalloc.c

## Purpose

`vmalloc.c` implements the kernel virtual-address mapping allocator for the Ceph client kernel tree snapshot. It provides the backing machinery for `vmalloc()`, `vzalloc()`, `vmap()`, `vm_map_ram()`, `ioremap_page_range()`, sparse vmalloc mappings, user remapping of vmalloc memory, vmalloc introspection through `/proc/vmallocinfo`, and early boot registration/import of fixed vmalloc areas. Its central job is to reserve virtually contiguous ranges in the kernel vmalloc region, populate or tear down kernel page-table entries for those ranges, allocate and free the underlying physical pages when the API owns them, and amortize expensive cache/TLB work through lazy purge paths.

The file is not Ceph-specific; it is shared Linux MM infrastructure that Ceph client code and its dependencies can indirectly rely on whenever they use vmalloc-backed buffers, vmap mappings, kvmalloc fallbacks, proc/kcore reads, or driver-style user remapping helpers. It is performance-sensitive and concurrency-heavy because vmalloc is used by many subsystems, can be called under memory pressure, and must coordinate with architecture page-table formats, KASAN/KMSAN/KMEMLEAK, memory reclaim, NUMA, percpu allocation, module memory, and proc diagnostics.

## Important APIs, Types, and Functions

Public/exported address classification and translation:

- `is_vmalloc_addr()` checks whether a tagged pointer falls in `[VMALLOC_START, VMALLOC_END)`.
- `is_vmalloc_or_module_addr()` also accepts the architecture module range when `CONFIG_EXECMEM` and `MODULES_VADDR` are active.
- `vmalloc_to_page()` walks the kernel page tables and returns the mapped `struct page`, including tail-page offsets for huge vmap mappings.
- `vmalloc_to_pfn()` wraps `vmalloc_to_page()` into a PFN.

Page-table mapping and unmapping APIs:

- `vmap_page_range()` and `ioremap_page_range()` map a physical range into an already reserved vmalloc area. `ioremap_page_range()` verifies that the requested range exactly matches a `VM_IOREMAP` `vm_struct`.
- `vmap_pages_range_noflush()`, `vmap_pages_range()`, and `__vmap_pages_range_noflush()` map an array of `struct page *` into a virtual range, optionally using huge vmalloc page sizes.
- `vunmap_range_noflush()` and `vunmap_range()` clear vmalloc page tables and perform the required cache/TLB work.
- `vm_area_map_pages()` and `vm_area_unmap_pages()` support page-by-page sparse mappings inside a `VM_SPARSE` area after `check_sparse_vm_area()` validates flags and bounds.

Virtual-address reservation and tracking:

- `struct vmap_area` is the allocator record for a virtual interval. It is stored in busy, lazy, free, pool, and block structures depending on lifecycle stage.
- `struct vm_struct` is the public descriptor for a reserved vmalloc area and carries flags, caller, requested size, page array, page order, and physical metadata.
- `struct vmap_node` partitions vmalloc bookkeeping into per-node busy/lazy trees and small-size pools to reduce contention.
- `struct rb_list` combines an rb-tree, sorted list, and lock for address-ordered interval lookup and coalescing.
- `struct vmap_pool` caches small free `vmap_area` objects by size.
- `alloc_vmap_area()` reserves a virtual interval, inserts it into the appropriate busy tree, populates KASAN shadow, and handles reclaim/purge retry.
- `free_vmap_area()`, `free_vmap_area_noflush()`, and `free_unmap_vmap_area()` return areas to free or lazy-purge structures.
- `find_vmap_area()`, `find_vm_area()`, `remove_vm_area()`, and `free_vm_area()` locate, unlink, unmap, and release descriptors.

Core vmalloc/vmap allocation APIs:

- `__vmalloc_node_range_noprof()` is the main allocator: it chooses a virtual range, optionally chooses a huge mapping shift, reserves a `vm_struct`, allocates physical pages, maps them, clears `VM_UNINITIALIZED`, and registers with kmemleak.
- `__vmalloc_node_noprof()`, `__vmalloc_noprof()`, `vmalloc_noprof()`, `vzalloc_noprof()`, `vmalloc_user_noprof()`, `vmalloc_node_noprof()`, `vzalloc_node_noprof()`, `vmalloc_huge_node_noprof()`, `vmalloc_32_noprof()`, and `vmalloc_32_user_noprof()` are policy wrappers around the range allocator.
- `vfree()`, `vfree_atomic()`, `vunmap()`, and the deferred `delayed_vfree_work()` path release vmalloc/vmap memory from sleepable or atomic contexts.
- `vmap()` maps caller-provided pages and optionally takes ownership of page references when `VM_MAP_PUT_PAGES` is set.
- `vmap_pfn()` maps non-RAM PFNs into a vmalloc area when `CONFIG_VMAP_PFN` is enabled.
- `vrealloc_node_align_noprof()` reallocates vmalloc memory, preserving contents and supporting in-place requested-size changes when capacity permits.

Fast short-lived mapping APIs:

- `struct vmap_block_queue` and `struct vmap_block` implement `vm_map_ram()`'s small-allocation fast path.
- `vm_map_ram()` maps an array of pages into vmalloc space; for counts up to `VMAP_MAX_ALLOC` it uses `vb_alloc()` from per-CPU vmap blocks, and for larger counts it uses a full `vmap_area`.
- `vm_unmap_ram()` releases mappings from `vm_map_ram()` using `vb_free()` for small block allocations or `free_unmap_vmap_area()` for large mappings.
- `vm_unmap_aliases()` flushes outstanding lazy aliases so pages cannot retain stale vmalloc TLB aliases.

Auxiliary APIs:

- `memalloc_apply_gfp_scope()` and `memalloc_restore_scope()` temporarily scope page-table allocations to no-reclaim/no-fs/no-io semantics based on the caller GFP flags.
- `register_vmap_purge_notifier()` and `unregister_vmap_purge_notifier()` allow other code to free address space when vmalloc area allocation overflows.
- `remap_vmalloc_range_partial()` and `remap_vmalloc_range()` insert vmalloc-backed pages into a user VMA for areas flagged `VM_USERMAP` or `VM_DMA_COHERENT`.
- `pcpu_get_vm_areas()` and `pcpu_free_vm_areas()` allocate congruent vmalloc regions for the percpu allocator on SMP.
- `vread_iter()` safely reads vmalloc ranges for debug consumers such as `/proc/kcore`, zero-filling holes and ignoring ioremap/sparse areas.
- `vmalloc_dump_obj()` reports allocation origin for printk object-dump paths.
- `vmalloc_init()` initializes caches, per-CPU queues, vmap nodes, early vmalloc imports, free space, and the vmap-node shrinker.
- `proc_vmalloc_init()` creates `/proc/vmallocinfo` when procfs is enabled.

## Control Flow and Lifecycle

The mapping layer starts with `vmap_range_noflush()` or `vmap_pages_range_noflush()`. Physical range mappings descend through `pgd -> p4d -> pud -> pmd -> pte` helpers. At each level the code tries architecture-supported huge mappings (`vmap_try_huge_p4d()`, `vmap_try_huge_pud()`, `vmap_try_huge_pmd()`) when alignment, size, protection, and physical address allow it. If a huge mapping is not possible, the code allocates lower-level kernel page tables with tracked helpers from `pgalloc-track.h` and fills PTEs in lazy MMU mode. Unmapping is symmetric through `vunmap_p4d_range()` down to `vunmap_pte_range()`, clearing huge or normal entries and synchronizing kernel mappings when the architecture requests it. Flush responsibility is explicit: noflush helpers leave cache/TLB work to the caller, while public wrappers perform `flush_cache_vmap()`, `flush_cache_vunmap()`, or `flush_tlb_kernel_range()` as needed.

The virtual-address allocator maintains a global augmented rb-tree/list of free ranges and per-vmap-node busy/lazy trees. Allocation through `alloc_vmap_area()` validates size/alignment, tries the per-node small-size pool for whole-size reusable areas, otherwise allocates a `vmap_area`, preloads a split helper for no-edge splits, locks `free_vmap_area_lock`, finds the lowest fitting free range with the augmented `subtree_max_size`, clips the free range with `va_clip()`, and inserts the allocated interval into the selected node's busy tree. If no space is found and the caller can block, it purges lazy areas, invokes purge notifiers, and retries before warning and failing with `-EBUSY`.

Freeing an ordinary vmap area first unlinks it from the busy tree. `free_unmap_vmap_area()` flushes caches, unmaps page-table entries without a full TLB flush in the normal case, optionally flushes for debug page allocation, then hands the interval to `free_vmap_area_noflush()`. That function inserts the range into a per-node lazy tree and increments `vmap_lazy_nr`; once lazy pages exceed `lazy_max_pages()`, it schedules `drain_vmap_work`. Purging under `vmap_purge_lock` drains per-node lazy trees, flushes the union TLB range once, releases KASAN vmalloc metadata, decays per-node pools, optionally parallelizes purge work across nodes, and merges final ranges back into the global free tree.

The `vmalloc()` family follows a larger lifecycle. `__vmalloc_node_range_noprof()` checks size against `totalram_pages()`, optionally picks a huge vmap shift when `VM_ALLOW_HUGE_VMAP` and architecture support are present, reserves a `VM_ALLOC | VM_UNINITIALIZED` `vm_struct`, adjusts KASAN tagging/protection, calls `__vmalloc_area_node()` to allocate physical pages and populate page tables, unpoisons the final allocation, clears `VM_UNINITIALIZED` with a write barrier, and registers kmemleak metadata. `__vmalloc_area_node()` allocates the `area->pages` pointer array, possibly by recursive vmalloc for large arrays, allocates backing pages with high-order and bulk attempts before falling back to single pages, applies a memalloc scope for page-table allocation, and maps the pages. On failure it defers cleanup to a work item to avoid recursive cleanup hazards.

The `vfree()` lifecycle removes the vm area, poisons it for KASAN, unmaps it, and frees every backing page tracked in `area->pages`. If called in interrupt context, `vfree()` delegates to `vfree_atomic()`, which appends the pointer to a per-CPU lockless list and schedules a work item that later calls `vfree()` in process context. `vunmap()` is similar but frees only the mapping descriptor because ownership of backing pages remains with the caller.

The `vm_map_ram()` lifecycle optimizes small, short-lived mappings. `vb_alloc()` scans the current CPU's free vmap-block list under RCU, marks a power-of-two page run used under the block lock, and removes full blocks from the free list. If no block fits, `new_vmap_block()` reserves a full `VMAP_BLOCK_SIZE` area, indexes it in a hashed xarray, and attaches it to a per-CPU queue. `vb_free()` clears the used bitmap, unmaps the pages without immediate global TLB purge, grows the dirty range, and frees the whole block when all pages are dirty. Fragmented blocks are purged by `_vm_unmap_aliases()` or full purge paths when free and dirty space cover the block and policy allows it.

Early boot uses a separate linked `vmlist` until the allocator is initialized. `vm_area_add_early()` and `vm_area_register_early()` insert fixed/reserved regions before `vmalloc_init()`. During `vmalloc_init()`, existing early regions become busy `vmap_area` entries, `vmap_init_free_space()` creates free ranges for gaps, per-CPU queues and deferred free lists are initialized, scalable vmap nodes are set up on 64-bit systems, and a shrinker is registered for cached node pools.

## State and Persistence Behavior

All state is in kernel memory; this file persists nothing to disk. Long-lived in-memory state includes:

- `vmap_area_cachep`, the slab cache for allocator interval records.
- `free_vmap_area_root` and `free_vmap_area_list`, the global augmented free-space index.
- `vmap_nodes`, `nr_vmap_nodes`, and `vmap_zone_size`, which partition busy/lazy state and small reusable pools.
- Per-node `busy` trees for live allocated ranges, `lazy` trees for unmapped but not yet TLB-purged ranges, `pool[]` lists for small reusable areas, and transient `purge_list`/`purge_work`.
- Per-CPU `vmap_block_queue` lists and xarrays for `vm_map_ram()` block lookup/free lists.
- Per-CPU `vfree_deferred` lockless lists for atomic-context `vfree()`.
- `vmap_lazy_nr`, which counts lazily freed pages and triggers purge work when the threshold is exceeded.
- `vmlist`, an `__initdata` early boot list consumed during initialization.

Synchronization uses a mix of global and sharded locks. The free-tree/list is protected by `free_vmap_area_lock`. Each vmap node has independent busy/lazy locks and a pool lock. Purging is serialized by `vmap_purge_lock` to reduce redundant TLB flushes and stabilize percpu area allocation behavior. Vmap-block free lists are RCU-walked and protected by per-queue/per-block spinlocks, while block lookup uses xarray locking internally. `VM_UNINITIALIZED` publication uses an explicit `smp_wmb()` in `clear_vm_uninitialized_flag()` paired with `smp_rmb()` in readers such as `vread_iter()` and `/proc/vmallocinfo`.

## Dependencies and Integration Points

The file depends deeply on architecture MM hooks: page-table allocation/traversal macros, huge vmap support, `arch_sync_kernel_mappings()`, cache/TLB flush hooks, direct-map permission helpers, module address ranges, and early boot virtual layout constants. It integrates with:

- KASAN and KMSAN through vmalloc shadow population/release, tag-aware pointer reset/unpoisoning, and noflush mapping wrappers.
- KMEMLEAK through allocation scans, vmalloc registration, and free notifications.
- memcg/vmstat through `NR_VMALLOC` page state accounting for backing pages.
- the page allocator through high-order, bulk, node-specific, mempolicy, DMA/DMA32, and retry/nofail GFP behavior.
- workqueues for lazy purge, deferred atomic free, and deferred failed-allocation cleanup.
- notifier chains through vmap purge notifications.
- procfs/seq_file through `/proc/vmallocinfo`.
- user memory management through `vm_insert_page()` in `remap_vmalloc_range_partial()`.
- the percpu allocator through `pcpu_get_vm_areas()`.
- debug infrastructure through tracepoints, `WARN*`, `BUG_ON`, `debug_check_no_locks_freed()`, `debug_check_no_obj_freed()`, printk object dump, and debug pagealloc.

## Risks and Edge Cases

Allocator correctness depends on interval-tree/list consistency. Overlap detection in `find_va_links()` warns and rejects impossible insertions, while many internal invariants use `BUG_ON()` because corruption of vmalloc interval state can otherwise lead to aliasing or page-table corruption. The augmented `subtree_max_size` must be updated after every split, insert, or merge; stale values could cause false allocation failures or invalid fits.

TLB/cache ordering is a major risk. Noflush helpers require callers to issue the right flushes. Lazy free intentionally defers TLB invalidation, so code that needs alias-free pages must call `vm_unmap_aliases()`. Direct-map permission resets for `VM_FLUSH_RESET_PERMS` must invalidate aliases before returning the direct map to default permissions.

Huge vmalloc mappings are opportunistic and must fall back to base pages when architecture support, protection, alignment, size, or high-order allocation fails. Callers and diagnostics such as `vmalloc_to_page()` must handle huge leaf entries by computing the correct tail page. `__vmalloc_node_range_noprof()` explicitly retries with `PAGE_SHIFT` when a huge mapping attempt cannot complete.

GFP semantics are constrained. Unsupported flags are masked with a warning; page-table allocations apply separate memalloc scopes and may fail under moderate pressure for `__GFP_NORETRY`/`__GFP_RETRY_MAYFAIL`. `__GFP_NOFAIL` is honored only in sleepable contexts and is deliberately disabled for nonblocking paths.

Atomic free is deferred and cannot run in NMI. Misusing `vfree()`/`vunmap()` on nonexistent or unaligned addresses triggers warnings or bugs. `vm_map_ram()` is documented as unsuitable for long-lived mixed-size objects because small-block fragmentation can consume virtual address space, especially on 32-bit systems.

User remapping requires `VM_USERMAP` or `VM_DMA_COHERENT`; otherwise `remap_vmalloc_range_partial()` fails. Sparse and ioremap areas are treated as holes by `vread_iter()` to avoid unsafe reads.

Scalability behavior depends on the vmap-node partitioning and pool decay. Pooling improves allocation speed but can hide free ranges until shrink/purge/decay returns them to the global tree. The shrinker only decays pools; it does not free live mappings.

## Test Signals and Validation Hooks

Useful validation signals include:

- Kernel selftests or module tests gated by `CONFIG_TEST_VMALLOC_MODULE`, especially vmalloc/vfree stress, alignment, huge vmalloc fallback, and map/unmap cycles.
- Boot-time smoke coverage of `vmalloc_init()`, early vm area import, `/proc/vmallocinfo`, and KASAN vmalloc shadow setup.
- Tracepoints `alloc_vmap_area`, `free_vmap_area_noflush`, and `purge_vmap_area_lazy` for allocation failure, lazy growth, and purge behavior.
- Runtime warnings for overlapping vmap areas, bad page-table entries, unsupported GFP flags, nonexistent `vfree()`/`vunmap()`, invalid ioremap ranges, and sparse-area misuse.
- `/proc/vmallocinfo` contents showing expected callers, flags, NUMA distribution, `vm_map_ram` areas, and unpurged lazy areas.
- Memory debugging signals from KASAN/KMSAN/KMEMLEAK, debug pagealloc, lockdep, and page owner around vmalloc map/unmap/frees.
- Stress tests that combine many CPUs, short-lived `vm_map_ram()` mappings, long-lived vmalloc allocations, direct-map permission reset paths, `vm_unmap_aliases()`, and memory pressure to exercise purge, shrinker, notifier, and pool-decay behavior.
