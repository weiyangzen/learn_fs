# sources/distributed-fs/eos/namespace/ns_quarkdb/LRU.hh

Purpose: implements a bounded LRU cache for namespace metadata objects that avoids evicting entries still referenced outside the cache.

Important APIs/types/functions: `hasGetId<EntryT>` detects required `getId`. `LRU<IdT, EntryT>` exposes `get`, `put`, `remove`, `size`, `GetMaxNum`, `SetMaxNum`, `GetRequests`, and `GetHits`. Private `Purge` evicts unreferenced old entries; `CleanerJob` asynchronously resets evicted shared pointers.

Control flow: `get` increments request count, finds an id, moves the object to the list tail, increments hits, and returns it. `put` refuses caching when max is zero, returns existing cached object for duplicate ids, purges when full, then inserts at the tail. `Purge` walks from least recently used, skips objects with `use_count() > 1`, erases ids for unreferenced objects, queues them for cleaner disposal, and compacts the dense hash map.

State and persistence: in-memory cache state includes dense hash map id-to-list iterator, list of shared objects, mutex, max size, atomic counters, deletion queue, and cleaner thread. No persistent state.

Dependencies and integration: used by QuarkDB file/container metadata services for object caches. Depends on Google dense hash map, Murmur3 hashing, `ConcurrentQueue`, and `AssistedThread`.

Risks: objects with external references can prevent cache size from falling below target. Dense hash sentinel keys reserve `UINT64_MAX-1` and `UINT64_MAX`-like ids, so id domains must avoid those values. Cleaner shutdown uses a null sentinel and relies on assisted thread termination ordering. `mAvgRtt` issue is elsewhere; here counters are straightforward.

Test signals: `sources/distributed-fs/eos/namespace/ns_quarkdb/tests/LruBenchmark.cc` and cache-related service tests exercise performance and behavior.
