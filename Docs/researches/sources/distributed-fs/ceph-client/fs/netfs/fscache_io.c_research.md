<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/fscache_io.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_io.c

## Purpose
Provides FS-Cache cache-object IO helpers for netfs read/write operations. It begins cache operations once a cookie reaches a usable state, writes page-cache/xarray data to the cache, clears deprecated `PG_private_2` bits after copy-to-cache completion, and resizes cached objects under netfs inode serialization.

## Important APIs, Types, And Functions
Exports `fscache_wait_for_operation()`, `__fscache_begin_read_operation()`, `__fscache_begin_write_operation()`, `__fscache_clear_page_bits()`, `__fscache_write_to_cache()`, and `__fscache_resize_cookie()`. Internal `fscache_begin_operation()` pins cookie access and binds a `netfs_cache_resources` to the cache backend. `struct fscache_write_request` carries async write completion context.

## Control Flow
`fscache_begin_operation()` initializes cache resources, calls `fscache_begin_cookie_access()`, examines the cookie state under lock, waits through lookup/create/invalidate/LRU-discard states, and then calls backend `begin_operation()`. If the cookie is dropped/relinquishing/not live, it tears down resources and returns `-ENOBUFS`. `__fscache_write_to_cache()` allocates a write request, begins a `FSCACHE_WANT_WRITE` operation, lets the backend adjust write range via `prepare_write()`, constructs an xarray iterator over mapping pages, and dispatches `fscache_write()` with completion callback `fscache_wreq_done()`.

## State And Persistence
State lives in `netfs_cache_resources` (`ops`, `cache_priv`, `cache_priv2`, `debug_id`, `inval_counter`) and in backend private state attached by `begin_operation()`. Persistent data changes are delegated to cache backend `read/write/resize` operations. `__fscache_resize_cookie()` sets `FSCACHE_COOKIE_NEEDS_UPDATE` and invokes backend `resize_cookie()` synchronously.

## Dependencies And Integration Points
Integrates `struct fscache_cookie`, netfs cache resource operations, xarray iterators, folio private bits, and backend FS-Cache ops. It is used by read/write paths that need a cache operation token before touching cache storage.

## Risks
Risks include deadlock or long waits if cookie state does not progress, stale IO after invalidation if `inval_counter` is ignored by callers, incorrect range truncation from backend `prepare_write()`, and missing `fscache_end_operation()` on error paths. Deprecated `PG_private_2` handling is explicitly transitional.

## Test Signals
Test cache read/write begin during lookup, invalidate, dropped cookie, backend offline, and cache resize. Verify async write completion clears private bits and always ends operations. Fault injection around allocation and backend `prepare_write()` should preserve callbacks and page bit cleanup.
