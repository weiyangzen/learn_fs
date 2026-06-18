# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestReplicaCachingGetSpaceUsed.java

## Purpose

`TestReplicaCachingGetSpaceUsed` verifies the DataNode `ReplicaCachingGetSpaceUsed` integration with `FsDatasetImpl`. It checks that DataNode DFS-used accounting includes both block and metadata file bytes for finalized replicas and replicas being written, and that `FsDatasetSpi.deepCopyReplica` is safe while replicas are being created concurrently.

## Important APIs and types

- `MiniDFSCluster`, `DistributedFileSystem`, `DFSInputStream`, `LocatedBlock`, and `ExtendedBlock` create real HDFS files and inspect block identities.
- `ReplicaCachingGetSpaceUsed` is selected through `fs.getspaceused.classname`, with `FS_DU_INTERVAL_KEY` and zero jitter making refresh timing predictable.
- `DataNode.getFSDataset().getDfsUsed()` is the primary accounting signal.
- `FsDatasetSpi.deepCopyReplica(String bpid)` exposes a snapshot of replicas for a block pool.
- `ModifyThread extends SubjectInheritingThread` repeatedly creates files while the main thread deep-copies the replica set.

## Control flow

Setup starts a one-node cluster configured to use `ReplicaCachingGetSpaceUsed`. The finalized test writes 20 KB, closes the stream, opens the file through the DFS client, sums block lengths and metadata stream lengths for all located blocks, sleeps long enough for the cached-space refresh, and expects `getDfsUsed()` to match that sum.

The RBW test keeps the output stream open after `hsync`, obtains the same block and metadata totals, waits for refresh, and expects the same accounting while the replica is still in RBW state. It then closes the stream, waits again, and asserts the value is unchanged across RBW-to-finalized transition.

The deep-copy test starts a background writer under `/testFsDatasetImplDeepCopyReplica`, then repeatedly calls `deepCopyReplica` until non-empty snapshots are observed ten times. Any `IOException` during snapshotting fails the test.

## State and persistence behavior

The tests create actual block and metadata files under a temporary MiniDFSCluster data directory. DFS-used state is cached and refreshed asynchronously, so tests rely on sleeps longer than the configured one-second interval. The RBW test is skipped on Windows. The modify thread deletes its test directory when stopped, but its `shouldRun` flag is a plain boolean, so visibility depends on normal test timing rather than explicit synchronization.

## Dependencies and integration points

This file integrates DataNode storage layout, metadata streams, HDFS write and sync paths, cached disk-usage accounting, block-pool replica snapshotting, and subject-preserving test threads. It is a regression surface for replacing shell `du` style accounting with replica-aware cached accounting.

## Risks and edge cases

- Refresh timing is sleep-based; slow hosts can still flake despite the low interval.
- Metadata length is read from DataNode internals rather than from filesystem enumeration.
- The concurrent writer swallows IOExceptions, so the deep-copy test only detects failures surfaced by `deepCopyReplica`.
- Non-volatile thread stop state can delay shutdown under unusual scheduling.

## Test signals

Strong signals are exact `blockLength + metaLength` accounting for finalized and RBW replicas, invariant accounting after close/finalization, Windows skip for RBW behavior, and repeated deep-copy calls under concurrent replica creation.
