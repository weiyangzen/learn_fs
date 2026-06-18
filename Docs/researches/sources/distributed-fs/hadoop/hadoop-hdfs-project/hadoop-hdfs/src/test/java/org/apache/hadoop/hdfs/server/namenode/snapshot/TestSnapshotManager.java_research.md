# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotManager.java

## Purpose
`TestSnapshotManager` covers snapshot manager limits and restart handling. It verifies global snapshot ID rollover, configured file-system and per-directory snapshot limits, the relationship between maximum snapshot ID and `Snapshot.CURRENT_STATE_ID`, and replay behavior when the configured limit is lowered after snapshots already exist.

## Important APIs, Types, and Functions
The file uses `SnapshotManager`, `Snapshot`, `SnapshotException`, `FSDirectory`, `INodeDirectory`, `INodesInPath`, `LeaseManager`, `INode.ReclaimContext`, `MiniDFSCluster`, `DistributedFileSystem`, `DFSConfigKeys.DFS_NAMENODE_SNAPSHOT_FILESYSTEM_LIMIT`, and `DFS_NAMENODE_SNAPSHOT_MAX_LIMIT`. Mockito spies/mocks isolate `SnapshotManager#createSnapshot` and `deleteSnapshot`; `LambdaTestUtils.intercept` validates live cluster exceptions.

## Control Flow
`testSnapshotIDLimits` and `testMaxSnapshotLimit` delegate into `testMaxSnapshotLimit`, which constructs a spied `SnapshotManager`, stubs the snapshottable root and max snapshot ID, creates up to the configured limit, then verifies the next create fails with the expected lower-case message. It deletes a snapshot and attempts another create to distinguish count-limit behavior from irreversible ID rollover behavior. `testValidateSnapshotIDWidth` checks the max ID remains below the current-state sentinel. `testSnapshotLimitOnRestart` creates five snapshots, lowers the configured directory limit before restart, verifies all five prior snapshots are replayed, then lowers the file-system limit and checks replay still preserves the existing count while blocking new creation.

## State and Persistence Behavior
The mock-based tests focus on manager counters and max-ID state. The restart test validates edit-log replay under stricter new limits: existing snapshots are preserved even when current configuration would no longer allow that many, but future creation is denied.

## Dependencies and Integration Points
The class straddles internal unit-style manager tests and live NameNode integration. It depends on FSDirectory image-loaded checks, lease manager handoff during snapshot creation, and cluster restart propagation of NameNode configuration into the snapshot manager.

## Risks and Edge Cases
The major risk is confusing reusable snapshot quota slots with non-reusable snapshot ID space. A deleted snapshot may free a configured count slot but cannot roll back max ID allocation. Another risk is restart rejecting or truncating existing snapshots after an operator lowers limits.

## Test Signals
Signals include expected `SnapshotException` message substrings, `getMaxSnapshotID() < CURRENT_STATE_ID`, preserved `getNumSnapshots()` after restart, and updated `getMaxSnapshotLimit()` values after configuration changes.
