# sources/distributed-fs/ceph/src/rgw/rgw_cache.cc

Purpose: implements RGW in-memory object cache lookup, update, expiry, LRU eviction, chained-cache invalidation, and JSON/test-instance support for cache notification types.

Important APIs/types/functions: `ObjectCache::get()`, `put()`, `invalidate_remove()`, `chain_cache_entry()`, `touch_lru()`, `remove_lru()`, `invalidate_lru()`, `set_enabled()`, `invalidate_all()`, `do_invalidate_all()`, `chain_cache()`, `unchain_cache()`, destructor, and dump/test-instance methods for `ObjectMetaInfo`, `ObjectCacheInfo`, `RGWCacheNotifyInfo`.

Control flow: `get()` takes a shared lock, misses disabled/absent/expired/type-mismatched entries, upgrades to write lock for expiry or LRU promotion, and fills `rgw_cache_entry_info` with locator/generation. `put()` invalidates chained dependents, increments generation, promotes LRU, merges flags/data/xattrs/meta/version, and supports negative entries. `chain_cache_entry()` verifies all referenced cache generations before registering dependent cache callbacks.

State/persistence: cache state is process memory only. Notification structs are serializable for cache invalidation messages. Entries carry `time_added`, generation counters, xattrs/data/meta/version, and dependent chained entries.

Dependencies/integration: Ceph shared mutex, RGW perf counters, configuration `rgw_cache_lru_size` and `rgw_cache_expiry_interval`, `rgw_cache_entry_info`, formatter, bufferlist, and chained caches.

Risks: lock upgrade is manual unlock/lock and must re-check map state. `for_each()` in the header appears to call the callback only for entries younger than expiry when expiry is set, but skips all entries if expiry is zero. Negative entries return `-ENODATA`. LRU size condition uses `>` so one extra entry can exist until touch.

Test signals: concurrent get/put/invalidate races, expiry removal and chained invalidation, type-mask miss, negative cache hit, xattr modification merge, generation mismatch in `chain_cache_entry()`, LRU eviction, and disable clears cache.
