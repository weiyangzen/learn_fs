# sources/distributed-fs/ceph-client/lib/test_meminit.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_meminit.c` validates allocator initialization and cleanup behavior for page allocator, `kmalloc`, `vmalloc`, `kmem_cache`, bulk slab allocation, and `SLAB_TYPESAFE_BY_RCU` caches. It is aimed at detecting stale data exposure after allocation/free cycles. The source was read as a complete 440-line file.

## Important APIs, Types, and Functions

Core helpers are `count_nonzero_bytes`, `fill_with_garbage_skip`, `fill_with_garbage`, `do_alloc_pages_order`, `test_pages`, `do_kmalloc_size`, `do_vmalloc_size`, `test_kvmalloc`, `test_ctor`, `check_buf`, `do_kmem_cache_size`, `do_kmem_cache_rcu_persistent`, `do_kmem_cache_size_bulk`, `test_kmemcache`, `test_rcu_persistent`, and `test_meminit_init`. Constants include `GARBAGE_INT`, `GARBAGE_BYTE`, `CTOR_BYTES`, `CTOR_PATTERN`, and `BULK_SIZE`.

## Control Flow

`test_meminit_init` runs four groups: page allocations for every `NR_PAGE_ORDERS` order, `kmalloc`/`vmalloc` sizes from `1` through `1 << 19`, slab cache combinations across size, constructor, RCU, and `__GFP_ZERO`, and RCU persistence checks. Each test usually allocates, fills freed memory with garbage, frees it, reallocates, and counts whether bytes are zero when zeroing is expected. Slab tests also exercise `kmem_cache_alloc_bulk` and `kmem_cache_free_bulk`. RCU cache tests compare freed object contents under `rcu_read_lock()` and reallocation behavior.

## State and Persistence Behavior

The module has no persistent state beyond static `bulk_array`. It creates temporary slab caches named `test_cache`, temporary heap buffers, page allocations, and vmalloc mappings, then frees/destroys them in each helper. The tests intentionally write recognizable garbage patterns to memory before freeing so subsequent allocation behavior can be checked.

## Dependencies and Integration Points

Direct includes cover init, kernel, mm, module, slab, string, and vmalloc headers. Integration points are page allocator initialization policy, slab cache constructors, `SLAB_TYPESAFE_BY_RCU`, `__GFP_ZERO`, bulk slab operations, `kmalloc`, `vmalloc`, `rcu_read_lock`, and allocator debug/hardening options that control memory initialization on alloc/free.

## Risks and Edge Cases

This test is sensitive to kernel configuration: if allocator zero-on-alloc/free policy is disabled or differs by cache type, failures may indicate configuration mismatch rather than a code bug. Large orders may fail due to memory pressure and are counted as failures. Constructor and `__GFP_ZERO` combinations are intentionally skipped when incompatible. RCU-type-safe cache behavior differs from normal cache zeroing and is handled specially.

## Test Signals

Each test group logs either all tests passed or failures out of total. Module init returns `0` only when the aggregate failure count is zero; otherwise it logs the failure count and returns `-EINVAL`.
