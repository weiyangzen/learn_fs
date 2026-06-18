
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockStatsMXBean.java

## Purpose
`TestBlockStatsMXBean` validates the NameNode `BlockStatsMXBean` and underlying storage-type statistics. It checks per-storage-type node counts, JMX serialization, failed-storage removal and restoration, per-storage-type xceiver load, and percent fields exposed through JMX.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster` with seven datanodes and mixed storage types: RAM_DISK on all nodes, DISK on three, ARCHIVE on three, and NVDIMM on one. It reads stats through `BlockManager.getStorageTypeStats`, `HeartbeatManager.getStorageTypeStats`, and `/jmx` JSON. It uses `StorageTypeStats`, `DataNodeTestUtils.injectDataDirFailure`, `restoreDataDirFromFailure`, `DistributedFileSystem` storage policies, and `GenericTestUtils.waitFor`.

## Control Flow and State
`setup` builds the mixed-storage cluster with disk-check gap set to zero. `testStorageTypeStats` checks in-service node counts for RAM_DISK, DISK, ARCHIVE, and NVDIMM. `testStorageTypeStatsJMX` fetches `/jmx`, locates `Hadoop:service=NameNode,name=BlockStats`, and verifies serialized storage-type entries. `testStorageTypeStatsWhenStorageFailed` creates a file, injects volume failures into selected storage dirs, expects a write failure when DISK is unavailable, waits for heartbeat-driven stats removal, restores volumes, restarts datanodes, and verifies counts recover. `testStorageTypeLoad` opens HOT and COLD policy files, waits for DISK and ARCHIVE xceiver counts, and verifies total load. `testStorageTypePercentJMX` confirms percent-used fields are present in JMX output.

## Dependencies and Integration Points
The file integrates NameNode block stats, heartbeat aggregation, DataNode volume failure simulation, storage policies, Jetty JMX JSON output, and platform assumptions that skip failure injection on Windows.

## Risks and Test Signals
Risks include sleep-based heartbeat waits, platform-specific volume failure behavior, JSON schema drift, and cleanup after injected failures. Strong signals are exact storage-type counts, JMX bean presence and fields, storage-type removal after disk failure, recovery after restart, and independent load accounting for DISK and ARCHIVE.
