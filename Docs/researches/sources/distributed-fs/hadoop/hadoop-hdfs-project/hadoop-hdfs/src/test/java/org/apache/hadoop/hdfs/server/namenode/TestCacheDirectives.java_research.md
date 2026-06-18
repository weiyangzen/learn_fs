# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCacheDirectives.java

## Purpose

`TestCacheDirectives` is the main NameNode cache-manager integration suite. It validates cache pool CRUD, cache directive CRUD, permissions, limits, expirations, cache replication and reporting, fsimage/edit-log restart behavior, HA standby expiry consistency, behavior when caching is disabled, and capacity/no-backing-replica edge cases.

## Important APIs, Types, and Functions

The fixture configures cache-related keys through `createCachingConf`: block size, datanode locked memory, heartbeat interval, cache report interval, path-based cache refresh interval, and list batching limits. It uses `MiniDFSCluster`, `DistributedFileSystem`, `NamenodeProtocols`, `NameNode`, `CacheManager`, `CachePoolInfo`, `CachePoolEntry`, `CachePoolStats`, `CacheDirectiveInfo`, `CacheDirectiveEntry`, `CacheDirectiveStats`, `CacheDirectiveIterator`, `CacheFlag`, `Expiration`, `SecondaryNameNode`, `DataNodeTestUtils`, `BlockReaderTestUtil`, `NativeIO.POSIX.NoMlockCacheManipulator`, and HA utilities. Helpers include `validateListAll`, `addAsUnprivileged`, `waitForCachedBlocks`, `waitForCacheDirectiveStats`, `waitForCachePoolStats`, `checkNumCachedReplicas`, `checkPendingCachedEmpty`, and overridable `getDFS` methods.

## Control Flow

Setup starts a four-datanode cluster with stubbed mlock and caching tracing enabled. Teardown removes all directives, waits for cached blocks to drop to zero, shuts down the cluster, and restores the previous `CacheManipulator`. Pool tests add, modify, list, and remove pools while validating duplicate, empty, null, nonexistent, and closed-filesystem failures. Directive tests create multiple pools with different modes, add directives as an unprivileged user, verify ID uniqueness and filtered listing, reject malformed paths and inaccessible/unknown pools, remove and modify directives, and check closed-filesystem failures.

## State and Persistence Behavior

The cache manager state under test includes pool metadata, directive metadata and IDs, max relative expiry, per-directive and per-pool stats, cached-block membership, datanode cached/pending lists, cache capacity/used counters, and fsimage/edit-log serialization. `testCacheManagerRestart` checkpoints with a `SecondaryNameNode`, saves namespace, restarts the NameNode, verifies pools/directives/expiry survive, and ensures the next directive ID advances from the previous persisted ID. `testExpiryTimeConsistency` uses an HA topology, modifies directive expiry on the active, waits for the standby to tail edits, and compares active/standby `CacheDirective.getExpiryTimeString()` under FS read locks.

## Dependencies and Integration Points

This suite integrates NameNode cache RPCs, DFS client convenience APIs, permission checking for cache pools, datanode cache reports, block-location cached-host advertisement, secondary NameNode checkpointing, fsimage save/load, HA edit tailing, datanode capacity accounting, cache monitor scheduling, and `NativeIO` mlock abstraction. `TestCacheDirectivesWithViewDFS` extends this class to run the same behavior through ViewDFS-backed `DistributedFileSystem` instances.

## Risks and Edge Cases

The tests are timing-sensitive because cache reports, heartbeats, path-based refresh, and HA tailing are asynchronous. Several helper waits use 60-120 second timeouts. Capacity tests depend on the fake `NoMlockCacheManipulator` and fixed `CACHE_CAPACITY`. Permission tests distinguish pool visibility from full metadata visibility. Force flags intentionally bypass pool limit failures. Expiry assertions compare wall-clock-derived values with tolerances. Caching-disabled tests assert directives can be added without creating cache replication work or monitor state.

## Test Signals

Important signals include expected exception messages for invalid pool/directive inputs, exact directive ID listing order, partial versus full pool info based on permissions, persisted pool/directive metadata after checkpoint/restart, cached block and replica counts reaching expected values, datanode cache capacity equaling used plus remaining, directory directive stats and pool stats matching bytes/files needed/cached, replication factor step-up/step-down visible in cached hosts, expired directives dropping cached blocks, overlimit bytes accounting, no pending cached entries for over-capacity blocks, cached replica count dropping after backing replicas are removed, no located-block interactions when cache is unused, zero cached blocks when caching is disabled, and matching active/standby expiry strings.
