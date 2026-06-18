# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/mover/TestStorageMover.java

## Purpose
`TestStorageMover` is a slow test suite for archival storage migration through `Mover.run`. It focuses on namespace-wide and path-scoped policy satisfaction, reusable synthetic namespace/cluster layouts, open-file safety, movement after renames, snapshots, and storage-full fallback behavior.

## Important APIs, Types, and Functions
- Static configuration sets block size, heartbeat/redundancy intervals, mover moved-window, and default storage-policy-satisfier mode.
- `NamespaceScheme` describes directories, files, file size, snapshots, and per-path `BlockStoragePolicy`; `prepare(...)` creates namespace objects and snapshots, while `setStoragePolicy(...)` applies policies.
- `ClusterScheme` describes cluster size, replication, storage type matrix, and capacities.
- `MigrationTest` encapsulates cluster setup, namespace preparation, mover execution, verification, replication checks, and cleanup.
- `MigrationTest.verifyRecursively(...)` walks the namespace using `listPaths` and verifies files with `Mover.StorageTypeDiff`.
- `PathPolicyMap` creates `/hot`, `/warm`, and `/cold` directories and can rename files among them to force policy changes after initial placement.
- `setVolumeFull(...)` mutates `FsVolumeImpl` capacity for a selected `StorageType`.

## Control Flow and Behavior
Most tests instantiate a `NamespaceScheme` and `ClusterScheme`, then call `MigrationTest.runBasicTest`: start the cluster, prepare files, verify initial state, set storage policies, run mover, and verify policy satisfaction. `testMigrateFileToArchival` moves a file to COLD. `testMoveSpecificPaths` runs `Mover.Cli.getNameNodePathsToMove` with `/foo/bar` and `/foo2` and verifies only the selected scopes. `testMigrateOpenFileToArchival` appends to an open file, runs migration, checks the under-construction block still has one location, continues writing, and reads back appended content. `testHotWarmColdDirs` initially satisfies policies, renames files across policy directories, reruns mover, and verifies the new layout.

Capacity tests fill either all DISK or all ARCHIVE volumes by setting volume capacities to zero and triggering heartbeats. When DISK is full, increasing replication for HOT can fall back to ARCHIVE, while COLD remains ARCHIVE-only; moving HOT to WARM can produce `NO_MOVE_BLOCK`. When ARCHIVE is full, increasing replication for COLD cannot add replicas, HOT file creation still works, and moving a COLD file to WARM can succeed because WARM allows DISK.

## State and Persistence
The tests create HDFS namespace objects, snapshots, file blocks, storage policy xattrs/metadata, and MiniDFSCluster storage directories. Verification forces block reports from each DataNode to synchronize NameNode state before checking locations. Open-file testing preserves an under-construction block across mover execution and validates subsequent writes. Capacity mutation is test-only in-memory state on `FsVolumeImpl`, communicated to the NameNode through heartbeats.

## Dependencies and Integration Points
The class integrates `MiniDFSCluster`, `DistributedFileSystem`, `Mover`, `Mover.Cli`, `BlockStoragePolicySuite`, `BlockStoragePolicy`, `DirectoryListing`, `HdfsLocatedFileStatus`, `LocatedBlock`, `DataNodeTestUtils`, `FsDatasetSpi`/`FsVolumeImpl`, `SnapshotTestHelper`, `Dispatcher`, `BlockPlacementPolicy`, and balancer `ExitStatus`. It tests interactions among policy selection, block placement, DataNode volume capacity, and mover scheduling.

## Risks and Edge Cases
- `verifyRecursively` lists one partial directory listing and does not paginate beyond the returned partial listing; this is acceptable for small test namespaces but would be unsafe as a general utility.
- `Thread.sleep(5000)` after mover runs is a coarse synchronization point.
- Direct `FsVolumeImpl.setCapacityForTesting(0)` depends on concrete dataset implementation.
- Open-file behavior is subtle: migrating completed blocks must not disturb the current under-construction block.
- The static `DEFAULT_CONF` is mutable and shared across tests.

## Test Signals
Signals include `Mover.run` returning expected `ExitStatus`, `Mover.StorageTypeDiff.removeOverlap(true)` proving storage types satisfy policy choices, replication count checks by storage type, successful reads after open-file migration, and policy ID verification for selected files after no-space movement.
