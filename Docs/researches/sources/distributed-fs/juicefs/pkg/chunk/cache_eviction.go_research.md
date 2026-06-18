## sources/distributed-fs/juicefs/pkg/chunk/cache_eviction.go

Purpose: defines disk-cache key indexing and eviction policies for JuiceFS chunk cache.

Important APIs/types/functions: constants define policies `none`, `2-random`, and `lru`. `cacheItem` stores logical size and access time; negative size marks staging blocks. `KeyIndex` abstracts add/remove/get/iteration/reset. `NewKeyIndex` instantiates policy implementations from `Config.CacheEviction`. `noneEviction` is a map with no eviction iterator and protects staging blocks unless removal explicitly passes `staging=true`. `randomEviction` samples pairs from map iteration, preferring expired or older entries. `lruEviction` tracks `cacheKey` to `lruItem` plus a min-heap ordered by access time, then size, then id; staging entries are kept out of the heap.

Control flow and state: `get` updates atime, `reset` returns a snapshot while clearing active state for rescans, and `evictionIter` removes yielded entries from the index as it yields. LRU uses `heap.Fix` on access/update and `heap.Remove` on deletion.

Dependencies and integration points: used by `cacheStore` to track cached and staged blocks, choose removals under capacity/free-space pressure, and preserve atime across scans. Depends on `container/heap`, `time`, and `cacheKey` from disk cache.

Risks and test signals: `EvictionNone.evictionIter` panics by design and must not be called. Staging blocks rely on negative sizes and explicit staging removal, so sign mistakes can leak staged files or evict unuploaded data. `verifyHeap` is available but unused; LRU integrity depends on correct heap position bookkeeping.
