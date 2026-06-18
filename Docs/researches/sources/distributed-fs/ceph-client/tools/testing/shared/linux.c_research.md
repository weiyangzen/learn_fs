<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux.c -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux.c

## Purpose

`linux.c` implements userspace stand-ins for selected Linux memory-allocation and slab-cache APIs used by radix tree, xarray, maple tree, and related tests.

## Important APIs, Types, and Functions

It defines globals `nr_allocated`, `preempt_count`, and `test_verbose`. Key APIs include `kmem_cache_set_callback()`, `kmem_cache_set_private()`, `kmem_cache_set_non_kernel()`, allocation counters, `kmem_cache_alloc_lru()`, `kmem_cache_free()`, `kmem_cache_alloc_bulk()`, `kmem_cache_free_bulk()`, `__kmem_cache_create_args()`, sheaf helpers `kmem_cache_prefill_sheaf()`, `kmem_cache_refill_sheaf()`, `kmem_cache_return_sheaf()`, `kmem_cache_alloc_from_sheaf()`, and `test_kmem_cache_bulk()`.

## Control Flow and State

Allocations use a mutex-protected freelist stored through `struct radix_tree_node::parent` for small unaligned caches, or `malloc`/`posix_memalign` for fresh and aligned objects. Counters are updated with `uatomic`. Nonblocking allocation behavior is simulated through `non_kernel` and optional callbacks. Bulk operations reuse cached objects when possible and unwind partial failure.

## Dependencies and Integration Points

The file depends on pthreads, malloc, Userspace RCU atomic operations, kernel slab/radix-tree headers, and shared compatibility headers. It is linked by `shared.mk` into xarray, radix-tree, maple-tree, idr, and VMA test binaries.

## Risks and Test Signals

Risks include diverging from kernel slab semantics, freelist corruption through reused object fields, missing constructor or zeroing behavior, and counter mismatches. `test_kmem_cache_bulk()` asserts expected freelist reuse and aligned-cache behavior; sanitizers from `shared.mk` provide additional signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux.c -->
