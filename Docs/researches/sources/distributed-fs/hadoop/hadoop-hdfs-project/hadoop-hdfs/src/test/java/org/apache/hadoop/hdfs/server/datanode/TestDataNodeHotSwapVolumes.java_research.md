# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeHotSwapVolumes.java

## Purpose

`TestDataNodeHotSwapVolumes` is a broad integration suite for live DataNode volume reconfiguration. It verifies parsing of changed storage directories, adding and removing volumes, federation behavior, block-report consequences, file-lock cleanup, concurrent add/list races, active-write removal, disk-failure reload, and same-mount tiering rejection.

## Important APIs, Types, and Functions

Important helpers include `startDFSCluster`, `setConfiguration`, `addVolumes`, `createFile`, `verifyFileLength`, `getNumReplicas`, `waitReplication`, `getDataDirs`, `triggerDeleteReport`, `getNumBlocksReport`, and `assertFileLocksReleased`. The suite exercises `DataNode.parseChangedVolumes`, `DataNode.reconfigurePropertyImpl(DFS_DATANODE_DATA_DIR_KEY, ...)`, `DataStorage`, `BlockPoolSliceStorage`, `FsDatasetSpi`, `FsVolumeSpi`, `FsVolumeImpl`, `FsDatasetTestUtil`, DataNode block reports, and `DataNodeTestUtils` disk-failure helpers.

## Control Flow

Cluster setup lowers block size, heartbeat, DF, heartbeat recheck, disk-check gap, and tolerated failed volumes for fast test feedback. Parsing tests compare new, removed, and unchanged `StorageLocation` lists and reject empty input or storage-type changes. Add-volume tests create new MiniDFSCluster instance storage directories, reconfigure `dfs.datanode.data.dir`, verify the effective configuration and `current` metadata directories, write files, and inspect block reports for distribution across old and new volumes. Removal tests reconfigure to a subset of directories, check file locks, schedule reports, then verify block missing behavior, new writes, replication recovery, or re-add behavior.

Concurrency coverage spies on `FsDatasetSpi.addVolume` and runs delayed add-volume operations in separate `SubjectInheritingThread`s while another thread repeatedly lists storage directories. Active-write removal uses `DataNodeFaultInjector.logDelaySendingAckToUpstream` plus barriers so a reconfiguration thread removes the volume while the write pipeline is blocked, then confirms the file remains readable and future writes succeed. Disk-failure reload simulates failed storage with `DataNodeTestUtils.injectDataDirFailure`, waits for disk error detection, restores the directory, reconfigures the original paths, and confirms a new volume object is used. Full-block-report coverage spies on the BPOS-to-NameNode protocol and expects a block report after removing a volume.

## State and Persistence Behavior

The test intentionally manipulates on-disk DataNode storage directories, `current` metadata directories, block pool storage directories, file locks, and block files. It validates that removed or failed volumes are removed from DataNode in-memory metadata and persistent storage tracking, and that re-added volumes can be formatted or rediscovered. In federation cases, volume changes must appear across namespaces, with empty volumes reported for namespaces that have not written new blocks. `tearDown` shuts down the cluster after each test.

## Dependencies and Integration Points

The suite integrates MiniDFSCluster, federated NameNode topology, `DistributedFileSystem`, `DFSClient`, block reports (`BlockListAsLongs`, `StorageBlockReport`, `BlockReportContext`), DataNode reconfiguration, FsDataset implementations, DataNode disk error detection, Mockito protocol spies, and platform assumptions for disk-failure injection. It is a direct regression surface for HDFS volume hot swap behavior.

## Risks and Edge Cases

Risks covered include storage type mutation of an existing path, partial add failures leaving stale metadata, lost file locks after volume removal, block reports retaining removed storage, re-adding a volume that still has blocks, append distribution after adding volumes, federation block-pool mismatches, replication after removing the volume containing a block, races between asynchronous add volume and storage listing, removing a volume during active writes, and direct reload after disk error. Timing and filesystem behavior are important: many tests depend on heartbeats, block reports, latches, or OS file-lock semantics; disk-failure injection is skipped on Windows.

## Test Signals

Signals include exact changed-volume list sizes and URIs, expected exception messages, effective configuration equality, `current` directory existence, block-report volume counts and block counts, file length and replication waits, `BlockMissingException` after removal, released lock assertions, no concurrent add/list errors, single remaining volume after active-write removal, successful reads and future writes, Mockito verification of one full block report, and rejection of same-mount volume additions.
