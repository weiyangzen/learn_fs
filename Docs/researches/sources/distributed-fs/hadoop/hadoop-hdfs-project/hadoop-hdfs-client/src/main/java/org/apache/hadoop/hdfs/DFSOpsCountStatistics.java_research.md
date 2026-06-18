# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSOpsCountStatistics.java

## Purpose
`DFSOpsCountStatistics` is the HDFS implementation of `StorageStatistics` for counting how many times each distributed filesystem operation is issued by HDFS clients.

## Important APIs, Types, and Functions
The nested `OpType` enum defines the tracked operations and their stable string symbols, such as `op_create`, `op_open`, `op_get_file_status`, snapshot operations, cache operations, xattr operations, storage policy operations, erasure-coding operations, and quota operations. `OpType.fromSymbol` maps a symbol back to an enum through a static `HashMap`. The class name exported to global storage statistics is `DFSOpsCountStatistics`. Counters are held in an `EnumMap<OpType, LongAdder>`.

The public surface is `incrementOpCounter(OpType)`, `getScheme()`, `getLongStatistics()`, `getLong(String)`, `isTracked(String)`, and `reset()`. The private `LongIterator` adapts the enum map entries to `StorageStatistics.LongStatistic`.

## Control Flow
Construction initializes one `LongAdder` per enum value. Filesystem front-ends call `incrementOpCounter` immediately around operations. Consumers iterate `getLongStatistics()` to see all counters, call `getLong(symbol)` for a single counter, or call `isTracked(symbol)` to validate a key. `reset()` resets every `LongAdder`.

## State and Persistence
All state is in-memory and thread-safe through `LongAdder`. Counters are process-local and reset when the `StorageStatistics` instance is reset or the JVM exits. There is no persistence to HDFS, logs, or metrics files in this class.

## Dependencies and Integration Points
The class extends `org.apache.hadoop.fs.StorageStatistics` and reports the HDFS scheme through `HdfsConstants.HDFS_URI_SCHEME`. `DistributedFileSystem` and `WebHdfsFileSystem` obtain/register this statistic in `GlobalStorageStatistics` and increment matching `OpType`s for their public filesystem methods. External callers can inspect it through Hadoop filesystem statistics APIs.

## Risks
Every new user-visible DFS operation needs a matching enum value and increments in all relevant filesystem front-ends; otherwise statistics silently undercount. Symbol strings are external-facing and must remain unique and stable. `LongAdder` snapshots are weakly consistent under concurrent updates, suitable for metrics but not exact transactional accounting. The enum contains historical spelling/casing in symbols such as `op_set_storagePolicy` and `op_set_quota_bystoragetype`, so cleanup refactors could break consumers.

## Test Signals
`TestDFSOpsCountStatistics` verifies symbol uniqueness, iteration across all enum values, `getLong`, `isTracked`, `reset`, and concurrent increments. `TestDistributedFileSystem` and WebHDFS tests assert that higher-level operations increment selected counters in integrated filesystem flows.
