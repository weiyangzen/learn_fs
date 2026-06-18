<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/slab.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/slab.h

## Purpose
This header declares the tools slab and kmalloc compatibility API, including cache objects and sheaf bulk-allocation helpers.

## APIs And Flow
It defines slab flags, `kzalloc_node`, `struct kmem_cache`, `struct kmem_cache_args`, `struct slab_sheaf`, `kzalloc()`, `kmalloc()`, `kfree()`, `kmalloc_array()`, cache allocation/free APIs, cache creation variants selected by `_Generic`, bulk alloc/free, sheaf prefill/refill/return helpers, `kmem_cache_sheaf_size()`, `__alloc_objs()`, and `kzalloc_obj()`. Inline flow mostly adapts arguments, adds `__GFP_ZERO`, or computes overflow-checked object sizes.

## State, Dependencies, Risks, Tests
State persists in `kmem_cache` fields: pthread mutex, object size, alignment, constructor, free-object storage, counters, non-kernel allocation tracking, callbacks, and private data. Dependencies include `linux/types.h`, `linux/gfp.h`, `pthread.h`, list types, and overflow helpers. Risks include divergence from kernel slab semantics, constructor/freeptr constraints, pthread locking requirements, `SLAB_TYPESAFE_BY_RCU` semantics in user space, and overflow handling in object allocation. Tests should cover kmalloc/kzalloc, arrays, cache create variants, ctor invocation, bulk/sheaf paths, counters, locking, and failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/slab.h -->
