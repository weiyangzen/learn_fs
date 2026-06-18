# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/CacheReplicationMonitor.java

## Purpose

`CacheReplicationMonitor` is the NameNode background thread that scans cache directives and schedules DataNodes to cache or uncache block replicas. It turns namespace cache directives into per-block desired cache replication and per-datanode pending cache commands.

## Important APIs and types

- The class extends `SubjectInheritingThread` and implements `Closeable`.
- `work` is the monitor loop.
- `setNeedsRescan` and `waitForRescanIfNeeded` coordinate immediate rescans with callers through a CRM lock and conditions.
- `close` shuts the monitor down while the global FSNamesystem write lock is held.
- `rescan`, `resetStatistics`, `rescanCacheDirectives`, `rescanFile`, and `rescanCachedBlockMap` implement mark-and-sweep cache reconciliation.
- `addNewPendingCached`, `addNewPendingUncached`, `chooseDatanodesForCaching`, and `chooseRandomDatanodeByRemainingCapacity` select datanode cache actions.

## Control flow

The thread waits until a periodic interval expires or requested scan count exceeds completed count. Each scan flips a boolean mark, takes the global namesystem write lock, records the current scan count, resets cache statistics, applies directives, scans the cached-block map, and resets datanode caching directive send timestamps. Directive scanning skips expired directives, resolves paths without following invalid or unsupported entries, applies directory directives only to immediate child files, skips under-construction blocks, and updates per-directive needed/cached byte and file counts.

The cached-block scan first drops pending cache entries that no longer fit effective datanode cache capacity. It then removes completed pending-uncache entries, decides whether each cached block is still needed, trims pending cache entries when enough replicas are cached, trims pending uncache entries when replicas are under target, schedules new uncache work for over-cached blocks, or schedules new cache work for under-cached blocks. Blocks with no desired or pending cache state are removed from the global cached-block set.

## State and persistence behavior

The monitor maintains scan counters, shutdown flag, mark bit, previous scan statistics, and last lock-hold timestamp. It mutates in-memory `CachedBlock` entries and datanode pending cached/uncached lists. Cache directives are namespace state, but the monitor's pending decisions are runtime state derived by rescans.

## Dependencies and integration points

It integrates with `FSNamesystem`, `FSDirectory`, `BlockManager`, `CacheManager`, `CachePool`, `CacheDirective`, `CachedBlock`, `INodeFile`, datanode cache reports, block completeness and corruption state, stale-node detection, and NameNode locking modes.

## Risks and edge cases

The monitor holds the global write lock during scans but can drop/reacquire it when configured to limit lock time; correctness depends on rescanning and mark logic tolerating namespace changes. Directory directives scan only direct children, not recursively. Weighted random selection assumes positive total cache remaining percent; all-zero or inconsistent cache metrics would be risky. Pending capacity computation subtracts pending cached bytes and adds pending uncached bytes, so stale pending lists can affect scheduling.

## Test signals

Tests should cover periodic and forced rescan synchronization, directive expiry, file and directory directive application, under-construction block skipping, pool limit enforcement, cached-block mark cleanup, pending cache capacity pruning, corrupt/non-service datanode filtering, stale-node preference, weighted target selection, and safe shutdown with locks held.
