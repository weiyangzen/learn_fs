# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameCache.java

## Purpose
`NameCache<K>` interns frequently repeated NameNode names during namespace loading. It reduces heap duplication for values such as file-name byte arrays referenced by `INode` objects.

## Important APIs and Types
- `NameCache(int useThreshold)` configures the promotion threshold.
- `put(K name)` returns an existing cached/internal value when available, tracks use counts during initialization, promotes names that meet the threshold, and returns null for uncached names after initialization.
- `initialized()` marks the cache ready for steady-state lookup and discards the transient use-count map.
- `reset()` clears the cache and re-enters initialization mode.
- Inner `UseCount` stores the first internal value and its count.

## Control Flow
During initialization, `put` first checks the permanent cache. On a hit it increments `lookups` and returns the canonical value. On a transient hit it increments the count, promotes at or above threshold, and returns the first-seen value. On a new name it inserts a `UseCount`. After `initialized`, the transient map is null and new uncached names are not counted; only permanent cache hits return canonical objects.

## State and Persistence Behavior
All state is in-memory: `cache`, `transientMap`, `lookups`, and `initialized`. There is no disk persistence. The class explicitly requires external synchronization; callers must serialize all mutations and lookups.

## Dependencies and Integration Points
It is package-private to the NameNode namespace code and used by inode/fsimage loading paths. It depends only on Java collections and SLF4J.

## Risks and Edge Cases
- `initialized()` sets `transientMap` to null after clearing it; calling initialization-path code without respecting `initialized` would NPE, but `put` guards that path.
- `promote` increments lookup count by the threshold, so lookup metrics include estimated savings from promotion.
- A threshold of zero or negative is not validated here; callers must provide sane values or every repeated/new path may behave unexpectedly.
- Thread safety is entirely external.

## Test Signals
`TestNameCache` is the direct unit test target. Useful assertions include promotion threshold behavior, canonical return values before and after initialization, lookup counts, and `reset()` rebuilding the transient map.
