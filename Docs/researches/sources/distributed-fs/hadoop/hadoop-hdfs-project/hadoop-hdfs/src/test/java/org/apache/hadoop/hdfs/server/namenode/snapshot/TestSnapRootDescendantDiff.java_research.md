# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapRootDescendantDiff.java

## Purpose

`TestSnapRootDescendantDiff` verifies snapshot diff-report rejection for descendant directories when the configuration disallows computing diffs from non-snapshot-root descendants. It is a narrow regression test for `getSnapshotDiffReport` validation under `DFS_NAMENODE_SNAPSHOT_DIFF_ALLOW_SNAP_ROOT_DESCENDANT=false`.

## Important APIs, types, and helpers

- Configuration keys: `DFS_NAMENODE_SNAPSHOT_CAPTURE_OPENFILES`, `DFS_NAMENODE_ACCESSTIME_PRECISION_KEY`, `DFS_NAMENODE_SNAPSHOT_SKIP_CAPTURE_ACCESSTIME_ONLY_CHANGE`, and `DFS_NAMENODE_SNAPSHOT_DIFF_ALLOW_SNAP_ROOT_DESCENDANT`.
- Public APIs under test: `mkdirs` and `getSnapshotDiffReport`.
- Helper flow: `modifyAndCreateSnapshot` delegates to `TestSnapshotDiffReport.modifyAndCreateSnapshot` and a local snapshot-name generator.
- Assertion helper: `GenericTestUtils.assertExceptionContains`.

## Control flow

The test cluster enables snapshot open-file capture and access-time filtering but explicitly disables descendant diff support. The test creates `/TestSnapRootDescendantDiff/sub1/subsub1/subsubsub1`, creates snapshots on `sub1` while modifying both the snapshot root and a deeper descendant, then attempts to call `getSnapshotDiffReport` on `subsub1` between `s1` and `s2`.

The expected result is an `IOException` whose message says the descendant path is not a snapshottable directory. This confirms that when descendant diff support is disabled, only the snapshottable root is accepted as the diff-report root.

## State and persistence behavior

The file does not test persistence or edit-log replay. The state under test is transient NameNode validation state: the snapshot root exists and has snapshots, but the descendant directory does not gain snapshottable status merely because it lies under the snapshot root.

## Dependencies and integration points

This test integrates snapshot-diff configuration, `DistributedFileSystem.getSnapshotDiffReport`, snapshot creation via `TestSnapshotDiffReport`, and NameNode path validation. It depends on error semantics distinguishing "descendant of a snapshottable root" from "snapshottable directory".

## Risks and maintenance notes

- If descendant snapshot diff support becomes enabled by default or validation messages are changed, this test will need adjustment.
- The local snapshot-name map starts at `s0` per snapshot directory and relies on `TestSnapshotDiffReport.modifyAndCreateSnapshot` creating a predictable sequence.
- Because the test only validates the disabled path, enabled descendant-diff behavior must be covered elsewhere.

## Test signals

The primary signal is the precise exception content for `subsub1`. Secondary signals are successful snapshot creation and mutation setup under the configured diff constraints.
