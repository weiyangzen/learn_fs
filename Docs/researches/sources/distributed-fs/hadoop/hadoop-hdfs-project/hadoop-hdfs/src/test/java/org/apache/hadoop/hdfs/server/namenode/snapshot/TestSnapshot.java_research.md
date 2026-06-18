# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshot.java

## Purpose

`TestSnapshot` is the broad snapshot functionality suite for HDFS. It combines a randomized, multi-iteration invariant test over generated directory trees with targeted tests for snapshot creation, illegal names, snapshottable permissions, metadata timestamps, reserved raw paths, offline image viewing, and fsimage/edit-log consistency.

## Important APIs, types, and helpers

- Public APIs under test: `allowSnapshot`, `disallowSnapshot`, `createSnapshot`, `deleteSnapshot`, `renameSnapshot`, `setTimes`, `setPermission`, `setOwner`, `setReplication`, `append`, `delete`, `mkdirs`, `saveNamespace`, and safe mode controls.
- Snapshot model helpers: `SnapshotTestHelper.TestDirectoryTree`, `SnapshotTestHelper.createSnapshot`, `checkSnapshotCreation`, `getSnapshotFile`, `dumpTree2File`, and `compareDumpedTreeInFile`.
- Persistence and tooling: `FSImageTestUtil.findLatestImageFile`, `PBImageXmlWriter`, `MiniDFSCluster` restart flows.
- Inner modification hierarchy: `Modification`, `FileStatusChange`, `FileChangePermission`, `FileChangeReplication`, `FileChown`, `FileAppend`, `FileAppendNotClose`, `FileAppendClose`, `FileCreation`, `FileDeletion`, `DirCreationOrDeletion`, and `DirRename`.

## Control flow

The fixture starts a three-datanode `MiniDFSCluster`, creates a `TestDirectoryTree` of height `5`, and records namespace internals. The main `testSnapshot` runs `runTestSnapshot(20)`.

Each randomized iteration enables nested snapshots, creates one snapshot on the tree root and one on a random directory, prepares modifications for the snapshot roots plus an additional random directory, applies each modification, and verifies all previously recorded snapshots still expose the same status, length, and existence as before the modification. It then applies random chmod and chown operations to directories and calls `checkFSImage`.

`checkFSImage` dumps the namespace tree, restarts without formatting to validate edit-log replay, saves namespace in safe mode, restarts again to validate fsimage load, and compares all dumped trees. `testOfflineImageViewer` runs one snapshot iteration, finds the latest protobuf fsimage, and verifies `PBImageXmlWriter` can parse it.

Targeted tests cover:

- Updating a subdirectory mtime under a snapshotted parent while the snapshot copy retains old times.
- Illegal snapshot names including `.snapshot`, absolute paths, path separators, and nested names.
- Attempts to create/delete/rename snapshots on non-snapshottable directories.
- Idempotence of `allowSnapshot` and `disallowSnapshot`, including root's special snapshottable-with-zero-quota behavior.
- Snapshot mtime stability across restart, mtime change after rename, and directory mtime persistence after snapshot deletion.
- Snapshot operations through `/.reserved/raw` paths, including root-level raw paths, followed by NameNode restart.

The inner modification classes load snapshot state, mutate current files/directories, then check snapshots. Status-changing classes compare full `FileStatus.toString()`. Append checks snapshot lengths and reads at the old boundary to ensure EOF. Creation/deletion and directory operations verify snapshot file existence and child status snapshots.

## State and persistence behavior

Persistence is a primary concern. The main loop repeatedly verifies both edit-log replay and fsimage save/load after many snapshot and mutation combinations. It also validates offline fsimage parsing and raw reserved path edit replay.

State tracked by the suite includes snapshot root lists, snapshot file mappings, file status snapshots, file lengths, directory child status, open append streams, and the generated directory tree's current non-snapshot children. The invariant is that current-tree mutations must not alter any existing snapshot view.

## Dependencies and integration points

This file integrates the HDFS client API, NameNode namespace internals, fsimage/edit-log persistence, offline image viewer, reserved raw path handling, directory tree test helpers, and randomized mutation generation. It depends on deterministic snapshot-path mapping through `SnapshotTestHelper` even while the current tree changes.

## Risks and maintenance notes

- The test is randomized using `Time.now()` as seed and logs the seed. Failures may require reproducing with the printed seed if behavior is order-sensitive.
- The global static `snapshotList` and counters make per-test lifecycle assumptions important.
- Comparing `FileStatus.toString()` is intentionally stronger than `equals`, but can be sensitive to harmless formatting changes.
- The open append sequence depends on `hsync(UPDATE_LENGTH)` and close ordering.
- Broad slow tests can mask which exact mutation caused failure unless the printed modification count and dump output are used.

## Test signals

Signals include snapshot existence checks, immutable `FileStatus` and length comparisons, EOF reads at snapshot boundaries, exact exception messages for invalid APIs, root snapshot quota values, mtime equality/inequality, successful offline image parsing, and dump-tree equality after edit replay and fsimage load.
