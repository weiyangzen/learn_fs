# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ReplicaCachingGetSpaceUsed.java

## Purpose

`ReplicaCachingGetSpaceUsed` is an `FSCachingGetSpaceUsed` implementation that calculates HDFS-used bytes from the in-memory replica map instead of directory usage scans. It aims to be faster and more exact for block and metadata files on a specific volume/block-pool pair.

## Important APIs, Control Flow, and State

The constructor disables first refresh, records the target `FsVolumeImpl` and block pool id from the builder, and leaves periodic refresh behavior to the base class. `refresh` deep-copies replicas for the block pool through `FsDatasetSpi.deepCopyReplica`, filters them by matching volume storage ID, sums `getBytesOnDisk()` plus `getMetadataLength()`, and stores the result in the inherited atomic `used`.

There is no durable state. The value is a cache derived from dataset replica metadata, and debug logs are emitted if copying or full refresh exceeds fixed thresholds. Exceptions are logged and leave the last cached value intact.

## Dependencies, Integration, Risks, and Tests

The class depends on `FSCachingGetSpaceUsed`, `FsVolumeImpl`, `FsDatasetSpi`, `ReplicaInfo`, Commons Collections, and `Time`. It integrates with volume space accounting when configured as `fs.getspaceused.classname`.

Risks include stale values if refresh fails, cost of deep-copying large replica maps, undercounting files not represented by replicas, and volume identity depending on storage ID equality. Tests should compare against expected replica sums, verify empty/null replica collection behavior, simulate refresh exceptions, and cover multi-volume block pools.
