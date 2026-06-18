# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestNestedSnapshots.java

Purpose: Tests nested snapshottable directory behavior, snapshot limits/default names, snapshot comparator semantics, and disallowing nested snapshottable directories while retaining snapshot features.

Important APIs/types/functions: configures `DFS_NAMENODE_SNAPSHOT_MAX_LIMIT`, uses `SnapshotManager.setAllowNestedSnapshots`, `SnapshotTestHelper.dumpTree`, `SnapshotTestHelper.getSnapshotRoot/getSnapshotPath`, `Snapshot.ID_COMPARATOR`, and internal `INodeDirectory` construction.

Control flow: `testNestedSnapshots` allows nested snapshots, snapshots `/testNestedSnapshots/foo` and nested `bar`, creates files before/after snapshots, and checks file visibility in live/foo snapshot/bar snapshot. It then allows/deletes root snapshot, disallows `foo`, disables nested snapshots, and verifies allowing snapshots on ancestor/descendant paths fails with messages containing "subdirectory" or "ancestor". `testSnapshotLimit` creates exactly 100 snapshots and expects the next to fail, while checking historical file visibility. `testSnapshotName` verifies default generated name pattern under quota. `testIdCmp` checks null and same/different snapshot ordering. `testDisallowNestedSnapshottableDir` verifies a nested snapshottable directory reverts to `isWithSnapshot` after disallow.

State and persistence behavior: no restart; state focus is live snapshot manager constraints and inode feature transitions.

Dependencies and integration points: integrates snapshot policy config, quota, edit-log fsync test optimization, DFSUtil byte conversion, and internal inode/snapshot classes.

Risks and test signals: broad semantic coverage for nested snapshots. Static `Random` with seed 0 makes limit visibility checks deterministic. No persistence path for nested state.
