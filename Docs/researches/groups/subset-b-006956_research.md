# Research: subset-b-006956 D4N directory and policy files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_directory.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_directory.cc

## Purpose

`d4n_directory.cc` implements the Redis-backed metadata directories used by the RGW D4N filter. The file turns `CacheObj` and `CacheBlock` records from `d4n_directory.h` into Redis hashes and sorted sets, provides optional connection-pool execution, and exposes bucket/object/block directory primitives that `rgw_sal_d4n.cc` and `d4n_policy.cc` use to find cached objects, list cache-visible bucket contents, update dirty and host metadata, and remove stale cache entries.

The implementation is not a generic Redis wrapper. It encodes D4N-specific key formats, field ordering, pipelined command behavior, and Ceph error conventions. Most methods return `0` on success, negative errno-style values on failures, and log through `ldpp_dout()`.

## Important APIs and functions

- `async_exec()` and `initiate_exec` dispatch Boost.Redis `connection::async_exec()` on the connection executor while keeping the shared connection alive through `boost::asio::consign()`.
- `redis_exec()` runs a Redis request either under an RGW `optional_yield` yield context or synchronously through `ceph::async::use_blocked`.
- `redis_exec_cp()` acquires a connection from `RedisPool`, executes the request, releases it, and rethrows after release on exceptions.
- `redis_exec_connection_pool()` chooses between a directory-specific `redis_pool` and the legacy shared connection, logging when the shared connection is used.
- `check_bool()` normalizes string boolean representations accepted by directory setters and update paths.
- `BucketDirectory` wraps bucket-level sorted-set keys. Its methods use Redis `EXISTS`, `ZADD`, `ZREM`, lexicographic `ZRANGE`, `ZSCAN`, `ZRANK`, and `UNLINK`.
- `ObjectDirectory` wraps object-level hash metadata and per-object/version sorted-set state. It implements `build_index()`, `exist_key()`, `set()`, `get()`, `copy()`, vector and single `del()`, `update_field()`, sorted-set helpers, and `incr()` for a `_versioned_epoch` key.
- `BlockDirectory` wraps cache-block hashes and block-local sorted-set helpers. It implements single and vector `set()`, single and vector `get()` variants, `copy()`, deletion, host removal, field update, and sorted-set helpers.
- `Pipeline::execute()` runs a queued Boost.Redis request built by directory methods in pipeline mode.

## Control flow

All directory operations follow the same broad flow: build a D4N key, construct a Boost.Redis `request`, execute it through a shared connection or pool, check `boost::system::error_code`, parse typed or generic Redis responses, then return `0`, Redis-derived negative error, `-ENOENT`, or `-EINVAL`.

Bucket operations are simple sorted-set calls. `BucketDirectory::zadd()` ignores the caller-provided `score` and always writes a `ZADD ... CH 0 member`, indicating bucket membership is stored lexicographically rather than by a meaningful numeric score. `zrange()` uses `ZRANGE key start stop BYLEX` and optionally `LIMIT offset count`. `zscan()` parses the generic RESP3 aggregate response manually, filling members from alternating member/score positions. One important control-flow issue is that `next_cursor` is passed by value, so callers do not receive the parsed cursor even though the method assigns it internally.

Object hash operations use `bucketName + "_" + objName` as the key. `set()` writes all object metadata fields with `HSET`: object and bucket names, creation time, dirty flag, underscore-delimited hosts, etag, object size, user id, and display name. `get()` uses `HMGET` with the same field order and assigns by `ObjectFields`. The sorted-set methods on `ObjectDirectory` operate against the same object index; D4N uses these sets for object versions or creation-time ordered dirty entries depending on call site.

Block hash operations use `bucketName + "_" + objName + "_" + blockID + "_" + size` as the key. `set_values()` serializes the block fields in `BlockFields` order, including block id, version, delete marker, size, global LFUDA weight, embedded object metadata, dirty flag, hosts, etag, object size, user id, and display name. `set()` and vector `set()` write hashes through `HSET`, optionally batching commands. Single `get()` uses `HMGET` into a typed optional vector. The templated vector `get<N>()` builds a response type with `N` optional vector slots, executes a batch of `HMGET`s, and parses tuple slots with compile-time iteration. The non-template vector `get()` issues `HGETALL` commands and manually walks the generic RESP3 stream.

`BlockDirectory::remove_host()` performs a read-modify-write on the underscore-delimited `hosts` field: it reads the field, erases a substring matching the requested host, trims leading or trailing underscores, deletes the whole block hash if no host remains, and otherwise writes the modified host string back. This is not atomic across concurrent clients.

`Pipeline` is a lightweight batching helper. Directory methods with a `Pipeline*` parameter append commands to its request when `pipeline_mode` is active and skip response validation until `execute()`.

## State and persistence behavior

The persistent state is Redis metadata, not Ceph objects themselves. The cache data blocks live behind `rgw::cache::CacheDriver`; this file stores the directory that lets RGW find those blocks.

Redis key layouts are embedded directly:

- Bucket directory: the bucket id string itself is a Redis sorted set key.
- Object directory hash: `bucketName_objName`.
- Object version epoch: `bucketName_objName_versioned_epoch`.
- Block directory hash: `bucketName_objName_blockID_size`.
- Hosts fields: underscore-delimited host strings, later split into `std::unordered_set<std::string>`.

Object and block hashes overwrite all stored fields on `set()`. `update_field()` can append to `hosts` or normalize `dirty`, then writes one field. `copy()` uses Redis `COPY` and `HSET` in a `MULTI`/`EXEC` sequence to duplicate metadata and rewrite object/bucket identity fields, but comments note that the method is not compatible with Ubuntu systems, likely because of Redis command/version availability.

Deletion uses Redis `UNLINK`, so removal is asynchronous on the Redis server. Vector deletion and vector set are pipelined but do not validate per-key effects.

## Dependencies and integration points

The file depends on Boost.Asio, Boost.Redis, Boost.Algorithm string splitting, Ceph async blocked completions, Ceph logging, and `optional_yield`. The data types and class declarations come from `d4n_directory.h`.

Primary consumers are:

- `rgw_sal_d4n.cc`, which uses `BucketDirectory`, `ObjectDirectory`, and `BlockDirectory` for D4N filter operations such as list, read, write, delete, copy, multipart completion, and bucket cleanup.
- `d4n_policy.cc`, which uses `BlockDirectory` during LFUDA eviction and dirty-object cleaning, uses `ObjectDirectory` to remove cleaned object/version entries, and uses `BucketDirectory` to remove bucket index entries.
- `D4NFilterDriver::initialize()` creates the directories, creates or configures a Redis connection/pool, and passes these objects to the policy/filter layer.

The Boost version conditional in `RedisPool::acquire()` lives in the header but affects this implementation because directory methods may run against pooled connections initialized lazily there.

## Risks and edge cases

- Redis key construction is delimiter based and unescaped. Bucket names, object names, or host strings containing underscores can collide or parse incorrectly. Host removal uses substring erase, so removing `host1` can affect `host10` or any occurrence embedded in another host token.
- `BucketDirectory::zscan()` accepts `next_cursor` by value, so scan pagination state is lost.
- `ObjectDirectory::del()` and `BlockDirectory::del()` check response values before checking `ec`; an errored response can be inspected before the error branch.
- Several paths use `.value().value()` on optional Redis responses without checking `has_value()`, so missing hashes/fields can throw and be mapped to `-EINVAL` rather than `-ENOENT`.
- `BlockDirectory::get(const std::vector<CacheBlock>&)` non-template overload bypasses `redis_exec_connection_pool()` and directly uses `redis_exec(conn, ...)`, so it ignores the configured connection pool.
- The templated `BlockDirectory::get<N>()` is explicitly instantiated for `N=100`; callers with other batch sizes need a visible instantiation or header definition. It also assumes `responses.size()` covers `blocks.size()`.
- `update_field()` performs an existence test then a separate update. Concurrent deletion or updates between those calls can race.
- `remove_host()` is a non-atomic read-modify-write and does not use Redis transactions or Lua, so two clients can lose each other's host updates.
- `BucketDirectory::zadd()` ignores its `score` argument, unlike object/block `zadd()`, which may surprise call sites expecting score semantics.
- Empty responses are treated inconsistently: some methods return `-ENOENT`, others return `-EINVAL`, and `zrevrange()` returns success with an empty vector.
- `CacheObj::size` is declared without an initializer in the header; callers must initialize it before `set()` serializes it.

## Test signals

Useful tests should cover Redis command semantics with a real or fake Redis endpoint:

- Round-trip `ObjectDirectory::set()`/`get()` and `BlockDirectory::set()`/`get()` for all fields, including dirty/delete marker parsing and host-list splitting.
- Key-collision cases for object names and host strings containing underscores.
- `BucketDirectory::zrange()` lexicographic pagination and `zscan()` cursor propagation; the current by-value cursor should be caught.
- Pipelined `BlockDirectory::set()` and `ObjectDirectory::zadd()` followed by `Pipeline::execute()`.
- `remove_host()` behavior for first, middle, last, missing, substring, and final-host deletion cases.
- Connection pool operation under concurrent calls, including release on Redis exception.
- Missing-key and missing-field behavior to verify errno mapping rather than uncaught optional access.

No dedicated unit test file for `d4n_directory.cc` was found in the local source subset. Observable integration signals appear in D4N SAL paths and performance counters for D4N cache behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_directory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_directory.h -->
# sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_directory.h

## Purpose

`d4n_directory.h` declares the Redis-backed directory API for D4N cache metadata. It defines the metadata records used to describe cached S3 objects and cache blocks, the directory classes that persist those records in Redis, a small Redis connection pool, and a pipeline helper for batching Redis commands. This header is the contract consumed by the D4N SAL filter and cache policy implementation.

## Important APIs and types

- `SeqContainer` is a C++20 concept requiring `push_back(value_type)`. It constrains `BlockDirectory::set_values()` so the implementation can serialize metadata into either `std::vector<std::string>` or `std::list<std::string>`.
- `RedisPool` owns a deque of shared Boost.Redis connections, lazily starts each connection with `async_run()`, blocks callers when the pool is empty, and returns connections through `release()`.
- `ObjectFields` and `BlockFields` enumerate the expected order of Redis `HMGET` fields for object and block hashes. The implementation indexes response vectors with these enum values.
- `CacheObj` stores D4N object metadata: S3 object name, bucket name/id as used by callers, creation time string, dirty flag, set of cache host addresses, etag, total object size, owner user id, and display name.
- `CacheBlock` embeds a `CacheObj` and adds block id, object version, delete marker flag, block size, and LFUDA global weight.
- `Directory` is a base class that carries an optional `std::shared_ptr<RedisPool>` and exposes `set_redis_pool()`.
- `Pipeline` wraps a Boost.Redis `request` and exposes `start()`, `execute()`, `is_pipeline()`, and `get_request()`.
- `BucketDirectory`, `ObjectDirectory`, and `BlockDirectory` declare the Redis operations implemented in `d4n_directory.cc`.

## Control flow and API shape

The header organizes D4N metadata at three levels:

1. `BucketDirectory` handles bucket membership/order using sorted-set operations. Its methods operate on a `bucket_id` string key and members.
2. `ObjectDirectory` handles whole-object metadata and object-level sorted-set operations keyed by a `CacheObj`.
3. `BlockDirectory` handles per-block metadata, block hash lookup, vectorized/pipelined bulk operations, and host removal.

Each concrete directory stores a shared `boost::redis::connection` passed at construction. The base `Directory` can later be configured with a `RedisPool`; implementation code chooses the pool if present and otherwise uses the shared connection.

Most public methods accept `const DoutPrefixProvider* dpp` for logging/config access and `optional_yield y` for either asynchronous/yielded or blocked completion. Methods that mutate sorted sets or hashes generally return `int` status. The policy layer and SAL layer use those return codes directly in RGW operation control flow.

`Pipeline` is intentionally simple: callers call `start()`, pass the pipeline to directory methods that support it, and then call `execute()` to submit the accumulated request. The header exposes `request& get_request()`, so batching logic is not encapsulated from callers.

## State and persistence contract

The header defines the in-memory representation of Redis-persisted D4N state:

- Object hash fields correspond to `ObjectFields`.
- Block hash fields correspond to `BlockFields`.
- Block metadata reuses `CacheObj::dirty` and `CacheObj::hostsList` to record block dirty state and block locations.
- `CacheBlock::globalWeight` is explicitly tied to LFUDA policy.

The persistence key format is private in `ObjectDirectory::build_index()` and `BlockDirectory::build_index()` declarations, but callers must populate `CacheObj` and `CacheBlock` fields consistently because the implementation derives Redis keys from those fields. `CacheObj::size` and several strings have no default semantic value, so uninitialized or empty fields can produce invalid directory rows.

`RedisPool` state is runtime-only. It tracks the Asio context, Redis config, pooled connections, mutex, condition variable, and whether connections have been started. The pool starts connections lazily on first `acquire()` rather than in the constructor.

## Dependencies and integration points

This header depends on Ceph RGW common types (`rgw_common.h`, `rgw_asio_thread.h`, `DoutPrefixProvider`, `optional_yield`), Boost.Asio, Boost.Redis, C++ threading primitives, and C++20 concepts.

Integration points include:

- `rgw_sal_d4n.h` includes this header to store directory members on `D4NFilterDriver` and to expose getters for filter objects/readers/writers.
- `d4n_policy.h` includes this header so policies can update block/object/bucket directory state during eviction and cleaning.
- `rgw_sal_d4n.cc` configures Redis connection pooling and passes the pool to directories.
- `d4n_directory.cc` relies on `ObjectFields` and `BlockFields` order matching the hard-coded Redis field vectors.

## Risks and edge cases

- `RedisPool::acquire()` can block indefinitely when all connections are checked out. It calls `maybe_warn_about_blocking(dpp)` if a `DoutPrefixProvider` is available, but there is no timeout or cancellation path for waiters.
- `RedisPool::cancel_all()` only iterates over connections currently in `m_pool`. Connections checked out at destruction time are not canceled by this method.
- `RedisPool::current_pool_size()` returns an `int` from a `size_t`, which can truncate very large pools.
- `RedisPool` has a typo in `m_aquire_release_mtx`; harmless but visible API maintenance noise.
- `PolicyDriver` and directory users rely on raw pointers and shared connections, so lifetime order matters. Directories must not outlive their Redis connection.
- `CacheObj::size` has no default initializer, unlike most bool fields. Using a default-constructed `CacheObj` with `set()` can serialize an indeterminate size.
- The field enums are order-sensitive. Adding, removing, or reordering fields in the implementation without updating these enums will silently corrupt parsing.
- `Pipeline` holds a single `request` and mutable mode flag without locking; it is not thread-safe.

## Test signals

Tests should compile consumers against this header with C++20 concept support and Boost.Redis version variants. Behavioral tests should validate:

- Lazy connection startup and release/blocking behavior in `RedisPool`.
- `cancel_all()` behavior with checked-in and checked-out connections.
- Object/block field enum alignment against serialized `HMGET` order.
- Default construction of `CacheObj` and `CacheBlock` before serialization.
- Pipeline append/execute lifecycle and rejection or behavior of reuse after `execute()`.

No direct header-specific tests were found in the local search. The strongest integration signal is construction and configuration in `D4NFilterDriver::initialize()` plus broad use by `rgw_sal_d4n.cc` read/write/delete/list flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_directory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_policy.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_policy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_policy.h -->
# sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_policy.h

## Purpose

`d4n_policy.h` declares the cache policy abstraction and two concrete D4N cache policy implementations: LFUDA and LRU. It is the policy contract used by the D4N SAL filter to ask whether cache entries exist, make room for new cache data, update cache metadata after reads/writes, manage dirty write-cache objects, erase entries, and run background cleaning. It also declares `PolicyDriver`, the small selector that instantiates a policy by configuration name.

## Important APIs and types

- `RefCount` is an enum with `NOOP`, `INCR`, and `DECR` operations used by policy update paths to protect active blocks from eviction.
- `State` is the dirty-object state machine: `INIT`, `IN_PROGRESS`, and `INVALID`.
- `CachePolicy` is the abstract base class. It defines protected `Entry`, `Entry_delete_disposer`, and `ObjEntry` types plus virtual methods for initialization, existence checks, eviction, refcount updates, block updates, dirty-object updates, block and dirty-object erase, dirty invalidation, and cleaning.
- `LFUDAPolicy` extends `CachePolicy` with heap-based LFUDA state, dirty-object cleaning state, Redis synchronization helpers, directory pointers, cache driver pointer, SAL driver pointer, timer, and cleaner thread.
- `LFUDAEntry` extends `Entry` with `localWeight` and a Fibonacci heap handle.
- `LFUDAObjEntry` extends `ObjEntry` with a heap handle for creation-time ordered dirty-object cleaning.
- `LRUPolicy` extends `CachePolicy` with an intrusive list, block and dirty-object maps, and a cache driver pointer.
- `PolicyDriver` owns a raw `CachePolicy*`, constructs `LFUDAPolicy` for `"lfuda"` and `LRUPolicy` for `"lru"`, and exposes `get_cache_policy()` and `get_policy_name()`.

## Control flow and API shape

The D4N SAL layer interacts through `CachePolicy`, not directly through LFUDA or LRU, for most operations:

1. `init()` receives the Ceph context, log provider, Asio context, and underlying SAL driver.
2. `eviction()` is called before caching new data to ensure enough local cache space.
3. `update()` records a cached block/head object access or insertion, optionally changing dirty state and refcount.
4. `update_refcount_if_key_exists()` is used around read paths to protect blocks while they are being served.
5. `update_dirty_object()` registers a dirty write-cache object for later write-back.
6. `invalidate_dirty_object()` handles deletes/overwrites of dirty objects so cleaner deletes instead of writes stale data.
7. `erase()` and `erase_dirty_object()` remove policy state when cache entries are deleted.
8. `cleaning()` is run as a background policy operation for write-cache flushing.

`LFUDAPolicy` uses two different heaps: one for eviction candidates ordered by LFUDA entry comparator and one for dirty objects ordered by creation time. Its comparator treats dirty blocks and positive-refcount blocks as lower eviction priority, so the heap top should be an eligible clean/unreferenced victim when one exists.

`LRUPolicy` intentionally provides a smaller subset of semantics. It satisfies the interface, but refcount update, dirty invalidation, and cleaning are no-ops or false-returning stubs.

## State and persistence behavior

The header declares in-memory state and the persistence collaborators:

- `entries_map` and `entries_heap`/`entries_lru_list` track cached block policy state.
- `o_entries_map` and `object_heap` track dirty objects pending write-back.
- `lfuda_lock` protects LFUDA block heap/map state.
- `lfuda_cleaning_lock`, `cond`, and `state_cond` protect dirty-object state and coordinate cleaner wakeups.
- `age`, `weightSum`, and `postedSum` support LFUDA scoring and Redis synchronization.
- `conn` is the Redis connection used for LFUDA global metadata.
- `blockDir`, `objDir`, and `bucketDir` are directory clients used by the LFUDA cleaner and eviction logic.
- `cacheDriver` persists cache bytes and cache xattrs.
- `driver` points to the underlying SAL driver for backend writes/deletes.
- `tc` is the dirty-object cleaner thread and `rthread_timer` drives Redis sync.

The header also shows ownership choices. `LFUDAPolicy` manually `new`s the three directory objects in its constructor and deletes them in its destructor. `PolicyDriver` manually owns `cachePolicy`.

## Dependencies and integration points

The header includes Boost.Asio coroutine primitives, Boost heap Fibonacci heap, Boost system error definitions, D4N directories, D4N SAL declarations, and RGW cache driver declarations.

Integration points:

- `rgw_sal_d4n.h` and `rgw_sal_d4n.cc` access `PolicyDriver` through `D4NFilterDriver::get_policy_driver()`.
- `d4n_policy.cc` provides the concrete implementation.
- `d4n_directory.h` types are used for Redis directory updates during eviction and cleaning.
- `rgw_cache_driver.h` provides local cache persistence and xattrs.
- Ceph configuration keys such as `d4n_writecache_enabled`, `rgw_lfuda_sync_frequency`, `rgw_d4n_cache_cleaning_interval`, `rgw_d4n_local_rgw_address`, and `rgw_max_chunk_size` are consumed by the implementation.

## Risks and edge cases

- `static std::string empty` is defined in a header with external linkage semantics that can be problematic across translation units; it is used as a default non-const reference argument. Calls that omit `restore_val` share this mutable object.
- Virtual methods accept `uint8_t op`, while callers use `RefCount` enum values. The unscoped enum converts implicitly, but stronger typing would reduce invalid operation values.
- `PolicyDriver::cachePolicy` is not default-initialized and unknown `policyName` leaves it indeterminate. `get_cache_policy()` or the destructor can then dereference/delete garbage.
- Raw owning pointers in `LFUDAPolicy` and `PolicyDriver` make exception safety and partial construction fragile.
- `LFUDAPolicy::quit` is `inline static std::atomic<bool>`, so all LFUDA policy instances share one stop flag. Multiple D4N filter instances could interfere with each other's cleaner lifecycle.
- The LFUDA comparator logic is subtle: it mixes dirty and refcount conditions with local weight ordering, and correctness depends on the heap top being an evictable candidate or proving none are evictable.
- `LRUPolicy` does not implement the full dirty-write-cache contract exposed by `CachePolicy`, so selecting `"lru"` in configurations that expect write-cache cleaning or invalidation can silently skip those behaviors.
- Several methods accept `optional_yield y` and store it in LFUDA state (`save_y()` and member `y`), so lifetime/thread use of yield contexts needs scrutiny.

## Test signals

Header-level tests should verify interface behavior through both policies:

- `PolicyDriver` selection for `"lfuda"` and `"lru"`, plus behavior for invalid names.
- `CachePolicy` polymorphic calls from SAL-style code for eviction/update/erase.
- LFUDA comparator ordering for clean, dirty, refcounted, and differently weighted entries.
- Dirty state-machine transitions for `INIT`, `IN_PROGRESS`, and `INVALID`.
- LRU implementation conformance where methods are intentionally no-op should be documented or guarded by configuration tests.
- Destructor/lifecycle behavior with cleaner thread and Redis timer cancellation.

No direct unit tests were found in the local source subset. Integration signals are the numerous calls from `rgw_sal_d4n.cc`, especially read refcount updates, write-cache dirty-object registration, delete invalidation, and eviction before cache insertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_policy.h -->
