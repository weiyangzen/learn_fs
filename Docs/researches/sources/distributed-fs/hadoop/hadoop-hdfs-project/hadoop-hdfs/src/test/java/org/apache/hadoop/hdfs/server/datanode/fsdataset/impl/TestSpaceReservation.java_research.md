# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestSpaceReservation.java

## Purpose

`TestSpaceReservation` is a slow MiniDFSCluster suite for DataNode reserved-space accounting for replicas in progress. It ensures RBW and temporary replica reservations reserve a full-block remainder, shrink as bytes are written, release on close, abort, errors, pipeline and lease recovery, re-replication, and replica finalization, and appear in JMX volume info.

## Important APIs and types

- `FsVolumeImpl.getReservedForReplicas()`, `reserveSpaceForReplica`, `getRecentReserved`, and test capacity overrides are central signals.
- `FSDataOutputStream`, `DFSOutputStream`, `DFSTestUtil.abortStream`, append, hsync/hflush, and lease recovery exercise client write paths.
- `BlockPoolSlice.createRbwFile` and `createTmpFile` are mocked through reflection into `FsVolumeImpl.bpSlices` to force file creation failures.
- `DataNodeFaultInjector` simulates mirror connection failure during pipeline recovery.
- `FsDatasetImpl.finalizeNewReplica` and `ReplicaInfo.getBytesReserved()` validate per-replica state cleanup.
- JMX `Hadoop:service=DataNode,name=DataNodeInfo` exposes `VolumeInfo`.

## Control flow

Shared helpers initialize HDFS configuration with fast DU refresh and scanner disabled, start clusters with one storage per DataNode, optionally cap volume capacity, and retain a reference to the single test volume. The base create/append helper writes a random partial block, asserts the reserved remainder, closes and verifies release, appends and verifies reservation, writes again and verifies the reservation shrinks.

Limited-space and EOF tests assert block allocation failure when two writers exceed capacity and that aborted writers release reservations on every replica in a three-node pipeline. RBW and temporary file creation error tests inject `IOException` from `BlockPoolSlice`, then verify reservation release happens once and does not clear unrelated pre-existing reservations.

Other tests assert JMX contains reserved-space fields, re-replication reserves exactly the source byte count for temporary replicas and releases it, concurrent writer stress leaves no leak, append close and abort restore only still-open reservations, mirror failure during pipeline recovery releases all reservations, lease recovery after a stopped DataNode leaves zero reservation, and finalizing a new replica clears both volume and `ReplicaInfo` reserved-byte counters.

## State and persistence behavior

The suite creates real clusters, data files, block replicas, JMX state, and DataNode volume state. It mutates capacity for testing, global `DataNodeFaultInjector`, reflected block-pool slice maps, and DataNode configuration during cleanup. Shutdown closes volume references, clients, filesystem, cluster, and restores the fault injector.

## Dependencies and integration points

It integrates HDFS create, append, close, abort, hflush/hsync, re-replication, block reports, pipeline recovery, lease recovery, DataNode JMX, `FsDatasetImpl`, `FsVolumeImpl`, `BlockPoolSlice`, and `ReplicaInfo`. It is a high-value regression suite for disk-full avoidance and reservation leak prevention.

## Risks and edge cases

- Many assertions depend on asynchronous cleanup and use `GenericTestUtils.waitFor`.
- Reflection into `bpSlices` tightly couples tests to `FsVolumeImpl` internals.
- The one-volume setup simplifies allocation behavior and may not cover multi-volume selection races.
- The stress test is time-based and can miss rare reservation leaks.
- Some failure messages contain historical typos but are not semantically relevant.

## Test signals

Strong signals are exact reservation byte counts, zero-reservation waits across all DataNodes, forced RBW/tmp creation failures, JMX field presence, temporary replica `recentReserved`, concurrent stress leak check, append abort/close accounting, injected pipeline failure, lease recovery, and finalization cleanup of both volume and replica state.
