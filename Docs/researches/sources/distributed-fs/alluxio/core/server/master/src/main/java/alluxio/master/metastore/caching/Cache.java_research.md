# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/Cache.java

## Purpose
`Cache` is a generic write-back cache for metastore entries. It supports concurrent per-key access, lazy loading from a backing store, asynchronous eviction to a backing store, metrics, and optional cache bypass reads.

## Important APIs and Types
- Abstract `Cache<K,V>` implements `Closeable`.
- Configured by `CacheConfiguration` max size, high/low watermarks, and eviction batch size.
- `get(K, ReadOption)` loads on misses unless skip-cache or full-cache behavior bypasses population.
- `put`, `putNewEntry`, and `remove` update cached dirty entries.
- `flush()` writes all dirty entries to backing store without evicting them.
- `clear()` clears in-memory entries and invokes callbacks.
- Abstract hooks: `load`, `writeToBackingStore`, `removeFromBackingStore`, `flushEntries`.
- Callback hooks: `onCacheUpdate`, `onCacheRemove`, `onPut`, `onRemove`.
- Inner `EvictionThread` performs CLOCK-like eviction; inner `Entry` stores key, nullable value, dirty bit, and referenced bit.

## Control Flow
Reads first honor skip-cache or full-cache bypass. Normal reads use `ConcurrentHashMap.compute` to serialize per-key loads and mark hits as referenced. Writes use `compute` to invoke callbacks atomically with cache changes; if a new entry arrives while the cache is full, it synchronously writes through and does not cache. Removes store a dirty tombstone (`mValue == null`) so eviction can delete from backing storage. The eviction thread starts lazily when the high watermark is reached, scans entries, clears referenced bits on first pass, flushes dirty candidates, then removes clean unreferenced entries until the low watermark target is met.

## State and Persistence
State is the concurrent map plus eviction thread. Persistence is delegated to subclasses. Dirty entries must be flushed before eviction or checkpoint. Metrics record hits, misses, load times, evictions, and size gauges.

## Dependencies and Integration Points
Used by `CachingInodeStore` for inode and edge caches. Integrates with `ReadOption`, `MetricKey`, `MetricsSystem`, and `StatsCounter`.

## Risks and Edge Cases
- Subclasses must set `entry.mDirty = false` after successful `flushEntries`; otherwise entries cannot be evicted.
- `clear()` is explicitly not threadsafe and requires external synchronization.
- Eviction callbacks and backing writes run in the eviction thread, so slow backing stores can cause the cache to fill and force synchronous writes.
- Tombstone semantics require subclasses to handle null values carefully.
- `close()` interrupts and joins the eviction thread but does not itself flush dirty entries.

## Test Signals
Tests should cover single-flight miss loading, skip-cache reads, write-through when full, dirty tombstone removal, eviction watermarks and referenced bit behavior, flush clearing dirty bits through subclass behavior, metrics counters, and close interruption.
