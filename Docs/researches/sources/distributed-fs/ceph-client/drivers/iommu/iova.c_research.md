# sources/distributed-fs/ceph-client/drivers/iommu/iova.c

## Purpose
`iova.c` implements the kernel I/O virtual address allocator used by IOMMU DMA paths. It manages allocated and reserved PFN ranges in an `iova_domain` rbtree and provides a fast path with per-CPU magazine caches for recently freed power-of-two sized ranges. The module is generic IOMMU infrastructure rather than a hardware driver.

## Important APIs, Types, and Functions
Key exported APIs are `init_iova_domain()`, `alloc_iova()`, `find_iova()`, `__free_iova()`, `free_iova()`, `alloc_iova_fast()`, `free_iova_fast()`, `reserve_iova()`, `put_iova_domain()`, `iova_domain_init_rcaches()`, `iova_cache_get()`, and `iova_cache_put()`. The code depends on `struct iova_domain` and `struct iova` from `<linux/iova.h>`, with local cache types `struct iova_magazine`, `struct iova_cpu_rcache`, and `struct iova_rcache`.

`__alloc_and_insert_iova_range()` is the core allocator. It walks the rbtree from a cached node downward, computes a top-down gap below `limit_pfn`, applies natural alignment when requested, inserts the new range, and updates cached search nodes. `private_find_iova()`, `remove_iova()`, and `iova_insert_rbtree()` implement lookup, deletion, and insertion under `iova_rbtree_lock`. `iova_rcache_get()` and `iova_rcache_insert()` route fast allocations through size-classed magazines, while `iova_depot_work_func()` drains excess global cache entries asynchronously.

## Control Flow and State
Domain initialization creates an anchor node at `IOVA_ANCHOR`, initializes rbtree locks, start PFN, granule, 32-bit DMA PFN boundary, cached nodes, and allocation-size hints. Slow allocation allocates an `iova` object from the slab cache, searches for a gap, inserts the node, and returns the object. Fast allocation rounds small sizes up to powers of two, tries the per-CPU rcache, then falls back to `alloc_iova()`. Fast free tries to push the PFN into the rcache and falls back to rbtree removal if the cache is unsuitable or full.

Persistent runtime state is all in memory: the rbtree, cached rbtree cursors, `max32_alloc_size`, per-CPU loaded/previous magazines, global depot lists, delayed work items, CPU hotplug hlist node, and two slab caches. There is no disk persistence. CPU hotplug teardown calls `free_cpu_cached_iovas()` to return cached ranges to the rbtree allocator. `put_iova_domain()` drains rcaches and postorder-frees the rbtree.

## Dependencies and Integration Points
The file integrates with Linux rbtree, slab, percpu allocation, CPU hotplug (`CPUHP_IOMMU_IOVA_DEAD`), delayed work, spinlocks, and kmemleak. IOMMU DMA code relies on the exported allocator APIs to reserve and recycle IOVA ranges. It also depends on `iova_shift()` and the `iova_domain` layout from the public IOVA header.

## Risks and Test Signals
Primary risks are allocator off-by-one errors around `limit_pfn + 1`, incorrect 32-bit boundary handling, stale cached rbtree cursors after deletion, and concurrency bugs between per-CPU magazines, depot work, CPU hotplug, and domain teardown. The rcache deliberately only caches small power-of-two ranges; callers freeing mismatched sizes can cause fragmentation or reuse failures. Test signals include allocation/free stress with randomized ranges, 32-bit-limited devices, high CPU hotplug churn, delayed work cancellation during domain destruction, reserve overlap cases, and IOMMU DMA workloads that exercise both slow and fast paths.
