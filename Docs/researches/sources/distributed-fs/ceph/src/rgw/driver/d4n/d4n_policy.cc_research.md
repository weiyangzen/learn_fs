# sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_policy.cc

## Purpose

`d4n_policy.cc` implements the D4N cache replacement and dirty-object write-back policies declared in `d4n_policy.h`. The main implementation is `LFUDAPolicy`, which tracks cached blocks in an LFUDA-like heap, keeps refcounted and dirty blocks out of eviction, synchronizes LFUDA age/weight metadata through Redis, restores state from the cache backend on startup, and runs a background cleaner that writes dirty cached objects back to the underlying RGW store. The file also provides a simpler `LRUPolicy` implementation for non-LFU use.

## Important APIs and functions

- Local `async_exec()`/`redis_exec()` mirror the Redis async wrapper pattern used in `d4n_directory.cc`, but operate only on the policy's shared Redis connection.
- `LFUDAPolicy::init()` restores cached objects/blocks through `cacheDriver->restore_blocks_objects()`, optionally starts the cleaner thread, initializes Redis LFUDA metadata, and spawns periodic Redis synchronization.
- `age_sync()` reads and updates the Redis `lfuda.age` field so local policy age follows the maximum known age across D4N nodes.
- `local_weight_sync()` compares local `weightSum` with the posted sum and Redis minimum local weight record, updates Redis when this node has a lower average, and posts this node's average under the local RGW address key.
- `redis_sync()` is an Asio coroutine that periodically calls `age_sync()` and `local_weight_sync()` using `rgw_lfuda_sync_frequency`.
- `invalidate_dirty_object()` marks a dirty object as `State::INVALID` unless cleaning is already in progress, and persists invalid state to the cache driver xattr `RGW_CACHE_ATTR_INVALID`.
- `get_victim_block()` picks the top LFUDA heap entry, decodes its cache key into a `CacheBlock`, and rejects dirty or refcounted entries.
- `eviction()` deletes clean, unreferenced victim data until enough cache space is available, updates LFUDA in-memory state, removes the local host from the block directory, deletes data via `CacheDriver`, and increments `l_rgw_d4n_cache_evictions`.
- `update_refcount_if_key_exists()` increments or decrements a block refcount and updates its heap ordering.
- `update()` creates or updates an `LFUDAEntry`, adjusts local weight, preserves dirty state when needed, updates refcount, and writes `RGW_CACHE_ATTR_LOCAL_WEIGHT`.
- `update_dirty_object()` enqueues dirty objects in an object heap ordered by creation time and records their state in `o_entries_map`.
- `_erase()`, `erase()`, and `erase_dirty_object()` remove block or dirty-object entries from maps/heaps.
- `delete_data_blocks()` deletes all chunk objects for an invalid dirty object after checking block refcounts.
- `cleaning()` is the long-running dirty-object cleaner and write-back loop.
- `LRUPolicy` implements `exist_key()`, `eviction()`, `update()`, dirty-object bookkeeping, and erase methods using an intrusive list and maps.

## Control flow

Initialization starts by registering callbacks with `cacheDriver->restore_blocks_objects()`. Restored objects call `update_dirty_object()` and restored blocks call `update()` with `RefCount::NOOP`, letting policy state rebuild from persisted cache metadata. If `d4n_writecache_enabled` is set, `init()` starts `tc`, a thread running `CachePolicy::cleaning()` polymorphically. It then writes initial LFUDA metadata into Redis with a `MULTI` containing `HSET lfuda minLocalWeights_*` and `HSETNX lfuda age`, and finally schedules `redis_sync()` on the RGW Asio context.

`redis_sync()` loops forever until terminal cancellation. Each tick synchronizes age and average local weight, waits `rgw_lfuda_sync_frequency` seconds, and logs non-cancellation errors before continuing.

Block updates are guarded by `lfuda_lock`. `update()` computes a local weight from current age, existing entry weight, or a restored xattr value. It updates an existing heap handle or pushes a new `LFUDAEntry`. If this was a normal access rather than restore or cleaner dirty reset, it writes the local weight back to cache xattrs. Reads and active operations use `update_refcount_if_key_exists()` to keep blocks with positive refcounts from eviction.

Eviction loops while free space is below the requested size. It locks the LFUDA state, picks the top heap entry, refuses if the top is dirty/refcounted, updates age and weight bookkeeping, erases the in-memory entry, unlocks, then removes the local host from the Redis block directory and deletes the cached block through `cacheDriver->delete_data()`. The remote-push/global-weight adjustment code is compiled out with `#if 0`.

Dirty-object cleaning is controlled by `lfuda_cleaning_lock`, `cond`, and `state_cond`. The cleaner takes the oldest dirty object from `object_heap`, waits until its age exceeds `rgw_d4n_cache_cleaning_interval`, then either deletes invalid cache data or writes data to the backend store:

- If the object state is `INVALID`, the cleaner checks refcounts, defers by increasing creation time when busy, deletes the head and data blocks from the cache when possible, and removes the dirty object entry.
- If the object is valid, the cleaner loads the target bucket/object through the underlying SAL driver, prepares an atomic writer or delete op, streams cached data blocks from `CacheDriver` into the writer, completes the RGW write, then marks head and block cache xattrs/directory entries clean.
- For non-versioned objects, it updates latest/null head directory entries if they still match the cleaned version and removes the dirty object score from the object directory.
- For versioned objects, it updates instance block dirty state, may remove stale latest entries, removes bucket/object directory entries, and retries selected directory cleanup operations.

`invalidate_dirty_object()` coordinates with `cleaning()`: `INIT` dirty objects become `INVALID`, while `IN_PROGRESS` objects cause the caller to wait until the dirty object disappears from `o_entries_map`.

The LRU policy is much simpler: update erases any old entry and pushes a new one at the back; eviction pops from the front and deletes cache data until enough space is available. It does not implement dirty invalidation or refcount-aware eviction.

## State and persistence behavior

`LFUDAPolicy` keeps in-memory state in:

- `entries_heap` and `entries_map` for cached block entries keyed by cache object id.
- `object_heap` and `o_entries_map` for dirty objects keyed by head cache id.
- `age`, `weightSum`, and `postedSum` for LFUDA scoring.
- `quit`, `cond`, `state_cond`, and two mutexes for lifecycle and cleaning coordination.

It persists or synchronizes policy state through several channels:

- Redis key `lfuda` fields: `age`, `minLocalWeights_sum`, `minLocalWeights_size`, and `minLocalWeights_address`.
- Redis key named by `rgw_d4n_local_rgw_address`, fields `avgLocalWeight_sum` and `avgLocalWeight_size`.
- Cache-driver xattrs such as `RGW_CACHE_ATTR_LOCAL_WEIGHT`, `RGW_CACHE_ATTR_INVALID`, and `RGW_CACHE_ATTR_DIRTY`.
- Redis block/object/bucket directories through `BlockDirectory`, `ObjectDirectory`, and `BucketDirectory`.
- The underlying object store via SAL writer/delete operations in `cleaning()`.

Dirty-object state has a small state machine: `INIT` means queued for later write-back, `IN_PROGRESS` means cleaner is actively writing or deleting it, and `INVALID` means a later delete superseded the dirty cached object and cleaner should delete cache data instead of writing it back.

## Dependencies and integration points

The implementation depends on `d4n_policy.h`, Ceph yield contexts, blocked async completions, `common/split.h`, RGW performance counters, Boost.Redis, Boost.Asio coroutines/timers, Boost heap handles, and the D4N directory classes.

Main integration points:

- `PolicyDriver` constructs `LFUDAPolicy` or `LRUPolicy` for `D4NFilterDriver`.
- `rgw_sal_d4n.cc` calls policy methods during reads, writes, deletes, multipart completion, copy handling, cache hits/misses, and cache population.
- `rgw::cache::CacheDriver` supplies local cache storage, free-space accounting, xattr persistence, and restore callbacks.
- The underlying `rgw::sal::Driver` supplies users, buckets, objects, atomic writers, and delete operations for write-back.
- `rgw_perf_counters` records D4N cache evictions from LFUDA eviction.

## Risks and edge cases

- `if (int ret = age_sync(dpp, y) < 0)` and the same pattern for `local_weight_sync()` assign a boolean comparison result to `ret`, so logs report `0` or `1` rather than the real negative error.
- `local_weight_sync()` can divide by Redis `minLocalWeights_size`; if the stored size is zero or missing, this can fail or produce invalid values.
- `weightSum` is updated by adding the new local weight on every `update()` but only subtracts on erase. Updating an existing entry can overcount unless the old weight is subtracted first.
- `eviction()` divides by `entries_map.size()` without checking nonzero after victim selection. It is likely nonzero if a victim exists, but the invariant is implicit.
- `get_victim_block()` allocates a `CacheBlock` and returns `nullptr` on malformed key without deleting the allocation.
- The cleaner reads data with `cacheDriver->get()` but checks `op_ret` without assigning the return value in that call, so cache read failures can be missed.
- `LFUDAPolicy::update_dirty_object()` always allocates and `emplace()`s a new entry; duplicate keys can leave an allocated heap entry not referenced by `o_entries_map` if `emplace()` fails.
- `invalidate_dirty_object()` waits for `IN_PROGRESS` objects with no timeout; if the cleaner stalls, delete callers can block indefinitely.
- The LFUDA destructor calls `rthread_stop()`, deletes directories, sets static `quit`, and joins the cleaner. Because `quit` is `inline static`, multiple LFUDA instances share one stop flag.
- `PolicyDriver` in the header does not initialize `cachePolicy` if the policy name is unknown; deleting or dereferencing it is undefined.
- LRU dirty-object support is incomplete relative to LFUDA: refcount update returns false, invalidation returns false, cleaning is empty, and dirty object erasure leaks the allocated `ObjEntry` because it erases the map without deleting the pointer.
- Eviction in both policies can loop for a long time if `CacheDriver::get_free_space()` does not increase after deletes.
- Dirty write-back has many multi-system updates that are not transactional across cache data, Redis directories, cache xattrs, and backend object store. Crashes can leave mixed clean/dirty metadata.

## Test signals

Tests should exercise LFUDA and LRU behavior under controlled fake `CacheDriver`, fake Redis, and fake SAL driver conditions:

- Restore callbacks rebuild expected block and dirty-object state.
- LFUDA `update()` changes heap priority, refcount, dirty state, and local-weight xattr as expected.
- Dirty or refcounted entries are not evicted, and clean entries remove local host directory state and cache data.
- `age_sync()` and `local_weight_sync()` handle missing, zero, lower, and higher Redis values.
- `invalidate_dirty_object()` transitions `INIT` to `INVALID`, persists the invalid xattr, and waits/returns correctly for `IN_PROGRESS`.
- Cleaner writes a dirty object's cached chunks to a backend writer, clears dirty xattrs and block directory dirty flags, and removes object directory score entries.
- Cleaner invalid-object path deletes head and data blocks and defers when block refcount is positive.
- Versioned/null-instance directory cleanup paths preserve the latest entry only when version matches.
- LRU eviction deletes oldest entries and frees all intrusive-list nodes.

No standalone unit tests for `d4n_policy.cc` were found in the local source subset. Integration coverage should be inferred from D4N SAL read/write/delete tests if present outside this subset and from runtime counters/logs: `d4n_cache_hits`, `d4n_cache_misses`, and `d4n_cache_evictions`.
