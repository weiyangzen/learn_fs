# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestLeaseManager.java

## Purpose
JUnit 5 coverage for `LeaseManager` bookkeeping, lease expiration, inode-to-lease indexing, restart restoration, and ancestor-directory filtering for open under-construction files. It combines lightweight Mockito-backed `FSNamesystem` tests with one `MiniDFSCluster` persistence/restart scenario.

## Important APIs, Types, and Functions
- Exercises `LeaseManager.addLease`, `removeLease`, `removeAllLeases`, `reassignLease`, `countLease`, `countPath`, `checkLeases`, `getInternalLeaseHolder`, `getLease`, `getINodeIdWithLeases`, `getINodeWithLeases`, `getINodeWithLeases(INodeDirectory)`, and `getUnderConstructionFiles`.
- Uses `FSNamesystem.getFilesBlockingDecom`, `getMaxListOpenFilesResponses`, and lock-state predicates through mocks.
- Builds synthetic `INodeDirectory` and `INodeFile` objects with `PermissionStatus`, `FsPermission`, `BlockInfo.EMPTY_ARRAY`, `Snapshot.CURRENT_STATE_ID`, and `DFSUtil` path component helpers.
- Full-cluster restart path uses `MiniDFSCluster`, `DistributedFileSystem`, `FSDirectory`, `safeMode`, `saveNamespace`, and `restartNameNode(true)`.

## Control Flow
- `testRemoveLeases`, `testCountPath`, and `testCheckLease` validate direct lease map changes and expired lease cleanup.
- `testLeaseRestorationOnRestart` creates an open file, intentionally removes its `LeaseManager` entry while leaving the inode under-construction feature intact, saves namespace, restarts the NameNode, then verifies the lease is rebuilt from inode state.
- `testInodeWithLeases` and `testInodeWithLeasesAtScale` populate mocked inode IDs with under-construction files and verify list/count APIs across empty, small, boundary, and large scales.
- `testInodeWithLeasesForAncestorDir` builds a small in-memory directory tree, leases selected files, and verifies directory-scoped filtering before and after lease removal.
- Helper `verifyINodeLeaseCounts` cross-checks lease-manager counts against `getUnderConstructionFiles` and `FSNamesystem.getFilesBlockingDecom`.

## State and Persistence Behavior
- Direct tests target in-memory lease maps keyed by holder and inode ID.
- Restart test verifies persisted fsimage reconstruction: lease identity must survive when only the inode under-construction state is serialized.
- Ancestor filtering depends on parent pointers and inode map lookups in `FSDirectory`.
- Expiration behavior depends on artificial lease period settings and lock-hold limit `maxLockHoldToReleaseLeaseMs`.

## Dependencies and Integration Points
- Depends on NameNode internals: `FSNamesystem`, `FSDirectory`, `INodeFile`, `INodeDirectory`, `INodesInPath`, `LeaseManager`, `OpenFilesIterator`, and snapshot-aware child lookup.
- Uses Mockito for lock and inode lookup contracts and AssertJ/JUnit assertions for counts.
- Integrates with HDFS persistence through `MiniDFSCluster` and NameNode RPC save namespace.

## Risks and Edge Cases
- Mocked lock state can hide real locking regressions outside `LeaseManager` logic.
- Scale loop is tuned around `INODE_FILTER_WORKER_TASK_MIN` and `INODE_FILTER_WORKER_COUNT_MAX`; changes to parallel filtering thresholds can change runtime.
- Restart scenario depends on saved fsimage behavior and open stream lifetime; cleanup relies on cluster shutdown.
- Directory tree map keys are simple local names, so duplicate names in different branches would collide if added later.

## Test Signals
- Strong signal for lease bookkeeping invariants, inode resolution, expiration progress, and restart restoration.
- Covers no-lease, duplicate-add, nonexistent-remove, reassignment, ancestor scoping, and high-cardinality lease filtering.
- Timeout annotations guard hangs in lease expiration and large-scale filtering.
