# sources/distributed-fs/ceph/src/rgw/rgw_bucket_sync_cache.h

Purpose: provides a per-datalog-shard LRU cache for bucket-shard sync state used by data sync coroutines.

Important APIs/types/functions: `rgw::bucket_sync::State`, `Entry`, `EntryToKey`, `Cache`, and `Handle`. `State` tracks key `(rgw_bucket_shard, optional generation)`, current `rgw_data_sync_obligation`, a counter, and progress timestamp.

Control flow: `Cache::create()` returns an intrusive pointer with configured target size. `Cache::get()` calls intrusive LRU `get_or_create()` and returns a `Handle` that retains both cache and entry. `Handle` implements copy/move assignment in an order that keeps the cache alive while replacing entries.

State/persistence: in-memory only; no disk/RADOS writes. The cached state represents live data-sync progress and obligations for bucket shards.

Dependencies/integration: depends on Ceph intrusive LRU, Boost intrusive ref counters, `rgw_data_sync.h`, `rgw_bucket_shard`, and `rgw_data_sync_obligation`.

Risks: explicitly uses thread-unsafe reference counting because intended scope is single-threaded; cross-thread sharing would be unsafe. LRU eviction must not invalidate active `Handle`s. Progress state is volatile and must be reconstructable.

Test signals: cache hit/create behavior by shard/generation key, LRU eviction with active handles, copy/move handle lifetime, counter updates, and no cross-thread use assumptions in data sync tests.
