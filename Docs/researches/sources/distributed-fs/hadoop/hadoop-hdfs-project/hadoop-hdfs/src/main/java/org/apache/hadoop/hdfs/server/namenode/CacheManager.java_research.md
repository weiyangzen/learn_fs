# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CacheManager.java

## Purpose
`CacheManager` is the NameNode-side controller for path-based caching. It stores cache pools, cache directives, and the cached-block-to-DataNode map, then coordinates with `CacheReplicationMonitor` and `BlockManager` to schedule cache and uncache work. It is constructed by `FSNamesystem`, and most public mutating APIs assert that the appropriate `FSNamesystem` lock is already held.

## Important APIs and Types
Key state includes `directivesById`, `directivesByPath`, `cachePools`, `nextDirectiveId`, `cachedBlocks`, and the CRM `ReentrantLock`. `PersistState` packages protobuf fsimage state. External-facing operations include `addDirective`, `modifyDirective`, `removeDirective`, `listCacheDirectives`, `addCachePool`, `modifyCachePool`, `removeCachePool`, `listCachePools`, `processCacheReport`, `saveState`, and `loadState`. Compatibility persistence is isolated in `SerializerCompat`.

## Control Flow
Directive creation validates pool name, path, replication, expiry, permissions, and pool capacity unless `CacheFlag.FORCE` is set, then allocates a monotonic ID and calls `addInternal`. Modifications build a merged directive from supplied fields and defaults, validate against source/destination pools, remove the old directive, and re-add the new one. Cache reports take the BM write lock, resolve the DataNode, clear its cached list, then insert or reuse `CachedBlock` entries and link them into DataNode cached/pending lists.

## State and Persistence
Persistent state is limited to pools, directives, and `nextDirectiveId`; DataNode cached block reports are in-memory and rebuilt from reports. Fsimage save/load supports protobuf `PersistState` and legacy `DataOutputStream`/`DataInput` serialization with startup progress steps. Edit log replay paths bypass time-dependent validation to remain deterministic.

## Dependencies and Integration
The class integrates with `FSNamesystem`, `FSDirectory`, `BlockManager`, `CacheReplicationMonitor`, `NameNodeMetrics`, protobuf helpers, `FSImageSerialization`, `StartupProgress`, and permission checking through `FSPermissionChecker`.

## Risks and Test Signals
Correctness depends on external lock discipline: FS lock for directives/pools and BM lock for cached blocks. Expiry validation depends on wall-clock time, so replay must use `modifyDirectiveFromEditLog`. Pool limit checks use a shallow direct-child directory size computation, which is a behavior boundary worth testing. `setCachedLocations` contains a duplicated `return;` after cache miss; harmless, but a cleanup/test signal. Tests should cover fsimage round trip, edit-log replay, list pagination/filtering, forced over-limit directives, disabled caching, DataNode cache report transitions, and CRM rescan signaling.
