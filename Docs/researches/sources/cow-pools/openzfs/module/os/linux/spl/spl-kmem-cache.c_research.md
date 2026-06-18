# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-kmem-cache.c

Read completely: 1444 lines.

This implements the Linux SPL `kmem_cache_*` compatibility layer. It chooses between Linux slab-backed caches for smaller objects and a custom SPL virtual-memory slab implementation with per-CPU magazines for larger or explicitly kvmem-backed objects.

Key responsibilities:
- Provides cache creation, destruction, allocation, free, reaping, and introspection helpers.
- Maintains a global cache list protected by `spl_kmem_cache_sem`.
- Implements custom slabs with `spl_kmem_slab_t`, `spl_kmem_obj_t`, partial/full lists, per-CPU magazines, and emergency allocations.
- Uses Linux `kmem_cache_create_usercopy()` for caches selected as `KMC_SLAB`.
- Uses a taskq to grow custom slab caches asynchronously.

Important implementation details:
- Tunables control magazine size, target objects per slab, maximum slab size, small-object Linux slab cutoff, and number of cache worker threads.
- Custom slabs allocate a page-aligned virtual region containing slab metadata, object storage, and per-object metadata.
- Per-CPU magazines avoid taking the cache spinlock on most allocations/frees. Refill drains objects from partial slabs; free returns objects to the local CPU magazine and flushes when full.
- Empty slabs move to the tail of the partial list and are reclaimed outside the cache spinlock.
- `KM_NOSLEEP` growth can allocate emergency objects from pages, tracked in an rb-tree because they do not belong to a normal virtual slab.
- If asynchronous slab growth appears deadlocked, the cache sets `KMC_BIT_DEADLOCKED` and uses emergency objects until the grow task completes.
- Linux slab-backed caches rely on the kernel allocator and track active objects through a percpu counter for debug/proc reporting.
- Cache destruction removes the cache from the global list, cancels pending grow tasks, waits for active references, destroys magazines/slabs or Linux cache, and asserts all object/slab counters are zero.
- `spl_kmem_reap()` reaps all registered custom caches.

Dependencies and interactions:
- Depends on SPL kmem/vmem, taskq, Linux slab/page APIs, percpu counters, wait queues, rb-trees, and memory reclaim accounting.
- Statistics are consumed by `spl-proc.c` slab proc output.
- Exported symbols back Solaris `kmem_cache_create`, alloc/free, reap, and cache inspection APIs.

Reliability notes:
- Correctness depends on local IRQ disabling around magazine access, spinlock protection for slab lists/counters, and careful avoidance of freeing virtual memory while holding the cache spinlock.
- Constructors run after allocation and destructors before free; the custom slab reclaim path currently asserts object metadata but does not call per-object destructors there because destructors are run when objects are freed to the cache.
- Emergency allocation exists to preserve forward progress under memory pressure but is intentionally rare and more expensive.
