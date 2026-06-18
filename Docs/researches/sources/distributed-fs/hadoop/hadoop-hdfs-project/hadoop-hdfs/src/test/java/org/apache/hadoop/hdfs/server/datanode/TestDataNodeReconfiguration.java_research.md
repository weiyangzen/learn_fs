# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeReconfiguration.java

## Purpose

`TestDataNodeReconfiguration` verifies live DataNode reconfiguration for transfer throttles, block/cache reports, peer and disk outlier detection, disk usage refresh behavior, disk balancer settings, slow-I/O threshold, and balancer mover concurrency. It ensures new values are validated, applied to runtime objects, written into DataNode configuration, and reverted to defaults without restart.

## Important APIs, Types, and Functions

The suite exercises `DataNode.reconfigureProperty` and `reconfigurePropertyImpl` for many keys: `DFS_DATANODE_BALANCE_MAX_NUM_CONCURRENT_MOVES_KEY`, block report interval/split/initial delay, max receiver threads, transfer/write/read bandwidth, cache report interval, peer stats/outlier keys, disk outlier and profiling keys, `FS_DU_INTERVAL_KEY`, `FS_GETSPACEUSED_JITTER_KEY`, `FS_GETSPACEUSED_CLASSNAME`, disk balancer enable/plan-valid interval, and slow-I/O warning threshold. Helpers include `startDFSCluster`, `createDNsForTest`, `testAcquireOnMaxConcurrentMoversReconfiguration`, and nested `DummyCachingGetSpaceUsed`.

## Control Flow

Each test starts from a ten-DataNode MiniDFSCluster unless it explicitly starts standalone DataNodes with a mock NameNode. Reconfiguration tests generally try invalid values first, expect `ReconfigurationException` with `NumberFormatException` or `IllegalArgumentException`, apply a valid value, assert runtime object state, then apply `null` to revert and verify defaults and absent config keys. Balancer mover tests acquire all throttler permits before and after max changes and cover failed downsize when current permits are busy. Block-report changes are checked through each `BPServiceActor` scheduler. Data xceiver changes inspect `DataXceiverServer` max count and throttler bandwidth objects. Peer/disk slow metrics update `DataNodePeerMetrics`, `DiskMetrics`, file I/O profiling hooks, and slow detector thresholds.

Disk usage tests update refresh interval and jitter inside each `BlockPoolSlice` `CachingGetSpaceUsed`, then revert to defaults. `testDfsUsageKlass` changes the space-used implementation to `DummyCachingGetSpaceUsed` and observes a static counter increasing after refreshes. Disk balancer tests toggle enablement and parse plan validity intervals in raw milliseconds and time-unit strings. Slow-I/O threshold reconfiguration checks invalid strings/negative values, a valid value, and default restoration.

## State and Persistence Behavior

The suite mutates live DataNode configuration and runtime service objects across all DataNodes. It observes state in xceiver throttlers, BP service actor schedulers, DataNode configuration, peer/disk metrics detectors, file I/O profiling hooks, block pool slices, and disk balancer. Temporary standalone DataNode directories are deleted in `tearDown`. `DummyCachingGetSpaceUsed.counter` is static and demonstrates periodic refresh behavior after class reconfiguration.

## Dependencies and Integration Points

The file integrates DataNode reconfiguration infrastructure, MiniDFSCluster federation topology, mock-NameNode DataNode startup, block report and outlier report schedulers, xceiver server throttling, peer metrics, disk metrics, file I/O profiling, FsDataset volume internals, disk balancer, and Hadoop `GetSpaceUsed` implementations. It is a broad runtime-config regression suite.

## Risks and Edge Cases

The primary risks are partial application where configuration changes but runtime objects do not, failed validation accepting bad values, default reversion leaving stale config keys, and concurrency limits shrinking below active usage. Some tests instantiate a new `BlockPoolManager` for scheduler verification, which is a narrow check of refreshed scheduler config. `testDfsUsageKlass` uses sleeps and static counter state, so it can be timing-sensitive. The repeated loop across ten DataNodes increases coverage but also test runtime.

## Test Signals

Signals include expected exceptions for invalid values, exact runtime values after valid reconfiguration, null config entries after default reversion, throttler acquire success/failure counts, failed concurrent-mover downsize, BP service actor scheduler intervals, peer/disk detector threshold values, profiling hook enablement and sample range, `CachingGetSpaceUsed` interval/jitter values, increasing dummy space-used refresh counter, disk balancer enablement and validity intervals, and slow-I/O warning threshold restoration.
