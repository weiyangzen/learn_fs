# sources/distributed-fs/ceph-client/lib/cache_maint.c

## Purpose

`sources/distributed-fs/ceph-client/lib/cache_maint.c` is a small registration framework for memory-system cache coherency maintenance operations. Drivers register invalidation providers; callers request writeback/invalidate for physical memory regions without knowing provider instances.

## Important APIs, Types, and Functions

Exports include `cache_coherency_ops_instance_put`, `_cache_coherency_ops_instance_alloc`, `cache_coherency_ops_instance_register`, `cache_coherency_ops_instance_unregister`, `cpu_cache_invalidate_memregion`, and `cpu_cache_has_invalidate_memregion`. Internal helpers are `__cache_coherency_ops_instance_free`, `cache_inval_one`, `cache_inval_done_one`, and `cache_invalidate_memregion`.

## Control Flow

Allocation validates that ops and `ops->wbinv` exist, zero-allocates a caller-sized `cache_coherency_ops_inst`, initializes its list and kref, and stores ops. Register/unregister adds or removes instances under a write semaphore. `cpu_cache_invalidate_memregion()` builds `cc_inval_params`, takes the read semaphore, calls each provider's `wbinv`, then calls each optional `done` method to wait for completion.

## State and Persistence Behavior

Registered providers live on the global `cache_ops_instance_list` and are protected by `cache_ops_instance_list_lock`. Instance memory is kref-managed and freed when the final put drops. There is no persistence beyond driver registration lifetime.

## Dependencies and Integration Points

The file depends on `linux/cache_coherency.h`, krefs, lists, rwsems, `memregion`, and namespace exports `CACHE_COHERENCY` and `DEVMEM`. It integrates with device memory and platform cache maintenance drivers that implement `wbinv` and optional completion.

## Risks and Edge Cases

`cpu_cache_has_invalidate_memregion()` is explicitly advisory and can race unregister. Invalidation stops on the first provider error, which can leave later providers uncalled. Providers must keep instance lifetime valid while registered and must not sleep or fail in contexts callers cannot tolerate.

## Test Signals

Signals include provider alloc/register/unregister/put lifecycle, one and multiple providers, `wbinv` parameter propagation, optional `done`, error propagation, empty-list behavior, race-sensitive unregister tests, and namespace export build checks.

## Read Coverage

Source read size: 138 lines, 3782 bytes.
