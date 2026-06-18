# sources/distributed-fs/ceph/src/rgw/driver/posix/bucket_cache.h

## Purpose
`bucket_cache.h` implements the POSIX RGW driver's ordered bucket listing cache. It materializes per-bucket directory listings into LMDB named databases, orders them by concatenated object name and instance, and keeps the cache approximately current with filesystem notifications. RGW bucket `list()` calls use this layer instead of walking the filesystem for every listing request.

## Important APIs, Types, and Functions
`BucketCacheEntry<D, B>` is the cached bucket object. It stores the bucket name, an xxhash partition key, an LMDB environment/database handle, intrusive AVL linkage, an LRU object base, a mutex/condition variable, and flags for filled/deleted state. `Factory` allocates or recycles entries for the cohort LRU. `reclaim()` marks an entry deleted, removes its notification watch, drops the LMDB database contents, and closes the DBI handle.

`BucketCache<D, B>` owns the LRU, AVL lookup cache, `Lmdbs` partition manager, and `Notify` implementation. Key public methods are `get_bucket()`, `fill()`, `list_bucket()`, `notify()`, `add_entry()`, `remove_entry()`, and `invalidate_bucket()`. `fill_cache_cb_t` and `list_bucket_each_t` are callback types used to serialize `rgw_bucket_dir_entry` values into LMDB and stream them back to callers.

## Control Flow
`list_bucket()` calls `get_bucket()` with create and lock flags. A missing bucket entry is inserted into the LRU/AVL cache, assigned to one LMDB partition by hash, and opened as a named LMDB database. If the entry is not filled, `fill()` asks the SAL bucket to enumerate entries, serializes selected `rgw_bucket_dir_entry` fields with `zpp::bits`, commits them to LMDB, marks the entry filled, and adds an inotify watch.

After fill, listing unlocks the bucket and scans the LMDB cursor from the marker or first key. Each LMDB value is deserialized back to `rgw_bucket_dir_entry`, `mtime` is reconstructed from seconds/nanoseconds, and the caller callback decides whether to continue.

Notification flow enters `notify()`. Existing filled buckets accept ADD, REMOVE, and INVALIDATE events. ADD calls `driver->mint_listing_entry()` to build metadata for a side-loaded file and writes it to LMDB; REMOVE deletes the key; INVALIDATE drops the DB and clears `FLAG_FILLED`, causing the next list to rebuild.

## State and Persistence Behavior
The LMDB cache is explicitly process-local and ephemeral. `Lmdbs` creates `rgw_posix_lmdbs/part_N` under the configured database root and removes all existing contents at construction. Persistent source of truth remains the POSIX filesystem plus xattrs managed by `rgw_sal_posix.cc`.

State is protected by a mix of partition locks from `TreeX`, per-entry mutexes, and LRU references. Every successful `get_bucket()` path must be paired with `lru.unref()`, and the destructor resets the notifier before draining cached entries to avoid callbacks into freed buckets.

## Dependencies and Integration Points
This header depends on LMDB, `lmdb-safe.hh`, `notify.h`, `zpp_bits`, xxhash, Boost intrusive AVL trees, Ceph `cohort_lru`, `scope_guard`, and RGW bucket entry types. It integrates directly with `POSIXDriver::mint_listing_entry()` and `POSIXBucket::fill_cache()` from `rgw_sal_posix.*`.

## Risks
The key format is `name + instance` and omits namespace in serialization comments, so namespacing/version edge cases require care. `invalidate_bucket()` calls `lru.unref()` manually despite also installing an unref scope guard, which looks like a double-unref risk. Notification REMOVE deletes by raw event name, while other paths use `concat_key()`, so versioned or instance-bearing keys can diverge. LMDB exceptions are not caught. Reclaim depends on proper DBI close/drop sequencing and on `safe_link` detecting linked AVL state.

## Test Signals
Useful tests should cover cold fill, marker ordering, prefix/list callback stop behavior, LRU reclaim, destructor drain under active watches, ADD/REMOVE/INVALIDATE notification updates, side-loaded file metadata minting, versioned keys, and double-unref detection under sanitizers.
