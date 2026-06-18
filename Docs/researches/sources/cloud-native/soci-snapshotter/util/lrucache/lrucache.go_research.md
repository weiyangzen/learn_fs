# sources/cloud-native/soci-snapshotter/util/lrucache/lrucache.go

Purpose: this package provides a reference-count-aware LRU cache. It delays final eviction callbacks until an entry has been removed from the LRU and all borrowers have released their references.

Important APIs and types: `Cache` wraps `groupcache/lru.Cache`, a mutex, and optional `OnEvicted`. `New` configures the inner LRU callback to finalize the cache-owned reference. `Get` returns value, a `done` release function, and ok flag. `Add` inserts new values or returns the existing value for duplicate keys; both paths increment a borrower reference and return a one-shot `done`. `Remove` removes from LRU. `refCounter` stores key, value, callback, reference count, and once guards for initialization/finalization.

Control flow: adding a new entry creates a refCounter, increments once for cache ownership, increments once for the caller, and inserts it. LRU eviction or explicit remove calls `finalize`, dropping the cache-owned ref. Borrowers call `done`, which is protected by `sync.Once` and decrements under the cache mutex. When ref count reaches zero, `OnEvicted` runs.

State and persistence: all state is in memory. The cache does not persist values and does not close resources by itself; `OnEvicted` is the finalization hook.

Dependencies and integration points: depends on `github.com/golang/groupcache/lru`. Useful for cached remote/layer resources where active users must keep objects alive past LRU eviction.

Risks: `OnEvicted` runs while locks are held through `dec`, so callbacks that re-enter the cache can deadlock. `refCounts` is signed and can go non-positive; one-shot `done` prevents common double-decrement, but misuse of internals could underflow. Changing `Cache.OnEvicted` after entries are added only affects future entries because the callback is copied into each `refCounter`.

Test signals: `lrucache_test.go` covers add/get duplicate behavior, explicit remove delayed until references are released, LRU overflow delayed eviction, and one-shot `done`.
