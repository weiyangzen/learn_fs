# sources/distributed-fs/ceph/src/osd/ECExtentCache.h

## Purpose

Declares the modern EC extent cache API and data model. The cache improves small/overlapping EC partial writes by retaining recently read/written shard extents while preserving IO order and exposing a backend read callback interface.

## Important APIs, Types, and Functions

Public types are `ECExtentCache`, `ECExtentCache::LRU`, `ECExtentCache::Op`, `ECExtentCache::OpRef`, and `BackendReadListener`. Public methods include `prepare()`, `execute()`, `read_done()`, `write_done()`, `on_change()`, `on_change2()`, `contains_object()`, `get_projected_size()`, `idle()`, and `add_on_write()`. Internal types `Object` and `Line` model active per-object cache ownership and line-sized shard extent maps.

## Control Flow and Data Flow

The intended client protocol is documented in the header: prepare all cache ops for one parent operation, execute them, satisfy any backend reads through `BackendReadListener::backend_read()`, call `read_done()` when the backend returns shard extents, accept the cache-ready callback, generate/write EC data, then call `write_done()`. `Op` exposes requested writes, resulting cached read data, object id, and on-write callbacks. `LRU` stores cache lines by `(oid, offset)` and uses a mutex because it is shared at OSD-shard scope.

## State and Persistence Behavior

The header declares volatile cache state only. Active cache lines live under `objects`; recent inactive lines live in `LRU`; line sizes are accounted to the EC extent cache mempool. No on-disk metadata is produced by this class. The destructor calls `on_change()` and `on_change2()` to force cleanup in failed tests or abnormal lifetimes.

## Dependencies and Integration Points

It depends on `ECUtil.h`, `Context`, Ceph mempool, `hobject_t`, `extent_set`, and shard extent set/map helpers. It is embedded in `ECCommon::RMWPipeline` and requires the backend to provide reconstructed shard reads for cache misses.

## Risks and Edge Cases

The API permits reentrant cache-ready callbacks from `execute()`, so callers must build all cache op lists before execution and tolerate immediate completion. `Op::cancel()` deletes a released context; ownership is manual. `add_on_write()` immediately invokes callbacks if there is no waiting op, otherwise attaches to the latest op. `MIN_LINE_SIZE` and chunk-size-derived line sizing determine cache granularity and can affect memory pressure.

## Test Signals

API-level tests should verify immediate versus deferred completion, callback reentrancy, cancel behavior, on-write callback ordering, LRU max-size enforcement under mutex, projected size queries, object containment before/after op destruction, and destructor cleanup with outstanding/canceled ops.
