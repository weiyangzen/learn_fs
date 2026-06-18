# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestListSnapshot.java

Purpose: Tests listing snapshottable directories and snapshots, with ordered snapshot deletion enabled.

Important APIs/types/functions: uses `hdfs.getSnapshottableDirListing`, `hdfs.getSnapshotListing`, `SnapshotStatus`, `SnapshottableDirectoryStatus`, and `SnapshotManager.setAllowNestedSnapshots(true)`. It expects `SnapshotException` through `LambdaTestUtils.intercept` when listing snapshots on a non-snapshottable directory.

Control flow: the test first asserts no snapshottable dirs exist and `getSnapshotListing(dir1)` fails. It allows snapshots on `/`, verifies root listing and empty snapshot listing, disallows root snapshots, and checks listings again. It then allows snapshots on `/TestSnapshot1`, creates `s0`, `s1`, `s2`, verifies names, full paths, and first snapshot ID, deletes `s2`, verifies listing still contains three entries with the last marked deleted, then deletes `s0` and expects only two entries.

State and persistence behavior: live manager/listing behavior only; no restart. Ordered deletion creates an intermediate deleted snapshot visible in listing until earlier snapshots allow cleanup.

Dependencies and integration points: integrates public HDFS snapshot listing APIs, ordered deletion status flags, and snapshottable-directory listing.

Risks and test signals: targeted validation of user-visible listing semantics under ordered deletion. It does not validate pagination, permissions, or persistence of deleted flags.
