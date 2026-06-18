<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mempool.h -->
# sources/distributed-fs/ceph-client/include/linux/mempool.h

## Purpose
This header defines the generic kernel memory pool interface that guarantees forward progress by keeping a minimum number of preallocated elements.

## Important APIs, types, and functions
`mempool_alloc_t` and `mempool_free_t` are element callbacks. `mempool_t` contains lock, minimum/current element counts, element array, pool data, callbacks, and wait queue. APIs include `mempool_init`, `mempool_init_node`, `mempool_exit`, create/destroy, resize, single and bulk allocation/free, preallocated-only allocation, and helper callback pairs for slab caches, kmalloc sizes, and page orders.

## Control flow
Consumers initialize or create a pool with a minimum reserve. Allocation first tries the underlying allocator and can fall back to preallocated elements; freeing replenishes the reserve or returns elements to the underlying allocator and wakes waiters. Resize adjusts reserve depth.

## State and persistence
State is runtime-only in the pool lock, element array, counts, and wait queue. Preallocated memory persists until pool exit/destroy.

## Dependencies and integration points
It depends on scheduler, allocation hooks/profiling, wait queues, slabs, kmalloc, and page allocator callbacks. It is widely used by block/filesystem paths that need allocations under memory pressure.

## Risks and test signals
Risks include incorrect `min_nr`, sleeping allocation contexts, callback mismatch between alloc/free, resize races, double free, and draining pools while users remain. Test allocation under simulated memory pressure, bulk operations, resize up/down, slab/kmalloc/page pools, `mempool_initialized`, and destroy after all elements are returned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mempool.h -->
