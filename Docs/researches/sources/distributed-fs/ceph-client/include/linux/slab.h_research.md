<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/slab.h -->
# sources/distributed-fs/ceph-client/include/linux/slab.h

## Purpose
`slab.h` is the public kernel memory allocation API for slab caches, `kmalloc()` families, typed object allocation helpers, `kvmalloc()` fallbacks, and corresponding free/barrier functions. It abstracts allocator implementation details behind a stable interface used by nearly every kernel subsystem, including networking and filesystem clients.

## Important APIs, Types, and Functions
The file defines slab flag bits and public flags such as `SLAB_CONSISTENCY_CHECKS`, `SLAB_RED_ZONE`, `SLAB_POISON`, `SLAB_HWCACHE_ALIGN`, `SLAB_CACHE_DMA`, `SLAB_CACHE_DMA32`, `SLAB_STORE_USER`, `SLAB_PANIC`, `SLAB_TYPESAFE_BY_RCU`, `SLAB_TRACE`, `SLAB_NOLEAKTRACE`, `SLAB_NO_MERGE`, `SLAB_ACCOUNT`, `SLAB_KASAN`, `SLAB_SKIP_KFENCE`, `SLAB_RECLAIM_ACCOUNT`, `SLAB_NO_OBJ_EXT`, and `SLAB_OBJ_EXT_IN_OBJ`. It defines `ZERO_SIZE_PTR` and `ZERO_OR_NULL_PTR()` for zero-sized allocation behavior.

`struct kmem_cache_args` carries modern cache creation parameters: object alignment, usercopy region, custom free pointer offset, constructor, and optional sheaf capacity. Cache APIs include `__kmem_cache_create_args()`, `kmem_cache_create()`, `kmem_cache_create_usercopy()`, `KMEM_CACHE()`, `KMEM_CACHE_USERCOPY()`, `kmem_cache_destroy()`, `kmem_cache_shrink()`, `kmem_cache_alloc()`, `kmem_cache_alloc_lru()`, `kmem_cache_charge()`, `kmem_cache_free()`, bulk alloc/free functions, NUMA allocation, and sheaf prefill/refill/return helpers.

General allocation APIs include `kmalloc()`, `kmalloc_node()`, `kmalloc_array()`, `krealloc()`, `krealloc_array()`, `kcalloc()`, `kzalloc()`, `kvmalloc()`, `kvzalloc()`, `kvmalloc_array()`, `kvcalloc()`, `kvrealloc()`, `kmalloc_track_caller()`, `kmem_buckets_alloc()`, `kfree()`, `kfree_sensitive()`, `kvfree()`, `kvfree_atomic()`, and `kvfree_sensitive()`. Typed helpers include `kmalloc_obj()`, `kmalloc_objs()`, `kmalloc_flex()`, and zeroed/vmalloc-backed aliases.

## Control Flow
Cache creation routes through `kmem_cache_create()` macro dispatch. `_Generic()` selects either the modern four-argument form with `struct kmem_cache_args`, the default-args wrapper for `NULL`, or the legacy align/flags/ctor form. Allocations from named caches use `kmem_cache_alloc*()` wrappers around non-profiling functions via `alloc_hooks()`.

`kmalloc()` uses a fast inline constant-size path. If the size is compile-time constant and exceeds `KMALLOC_MAX_CACHE_SIZE`, it calls the large page allocator path. Otherwise it maps the size to a bucket index using `kmalloc_index()`, selects a cache type with `kmalloc_type()` based on GFP flags and optional randomization, and calls `__kmalloc_cache_noprof()`. Dynamic sizes fall back to `__kmalloc_noprof()`. Array helpers perform overflow checks with `check_mul_overflow()` before allocating. `kvmalloc()` routes to vmalloc-capable allocation for large or fallback allocations.

## State and Persistence Behavior
Slab caches are persistent in-kernel allocator state until destroyed. Allocated objects persist until freed by the matching free API; zero-sized allocation returns `ZERO_SIZE_PTR`, which is freeable but not dereferenceable. Cache flags influence debugging, memory accounting, reclaim grouping, KASAN/KFENCE behavior, cache merging, DMA zones, and RCU-safe page lifetime. Sheaf settings add per-CPU/per-node object batching for configured caches.

## Dependencies and Integration Points
The header depends on GFP flags, overflow helpers, RCU, workqueues, percpu refcounting, cleanup attributes, hashing, KASAN, allocation tags, NUMA constants, and architecture alignment definitions. It integrates with memcg, KASAN, KFENCE, kmemleak, SLUB debug, fault injection, slab buckets, page allocator large allocation paths, and RCU delayed free barriers.

## Risks and Test Signals
Common risks are integer overflow in object arrays, using `GFP_KERNEL` from atomic context, assuming zero-sized allocations return `NULL`, freeing with the wrong cache, misuse of `SLAB_TYPESAFE_BY_RCU` without independent object validation, incorrect usercopy whitelists, sensitive data not cleared before free, and hidden behavior changes from cache merging or debug flags. Test signals include KASAN/KFENCE/KMSAN reports, memcg charge failures, slabinfo anomalies, kmemleak, fault-injection tests, lockdep around allocation contexts, KUnit slab tests, and targeted tests for overflow-safe allocation helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/slab.h -->
