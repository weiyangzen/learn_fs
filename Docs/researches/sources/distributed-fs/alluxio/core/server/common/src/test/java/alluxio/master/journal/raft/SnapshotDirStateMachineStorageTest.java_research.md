<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorageTest.java -->
# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorageTest.java

## Purpose
Validates `SnapshotDirStateMachineStorage`, Alluxio's directory-based Ratis state-machine snapshot storage, including snapshot discovery, latest snapshot selection, cleanup retention, and backward compatibility with older single-file snapshots.

## Important APIs, Types, And Functions
- `loadLatestSnapshot()` refreshes the storage's cached latest `SnapshotInfo`.
- `getLatestSnapshot()` returns either `FileListSnapshotInfo`, `SingleFileSnapshotInfo`, or null.
- `signalNewSnapshot()` enables deletion by `cleanupOldSnapshots`.
- The test reuses `RaftSnapshotManagerTest.createSampleSnapshot` and `createStateMachineStorage`.

## Control Flow
Tests first establish that newly created storage reports no snapshot and does not update its latest pointer until `loadLatestSnapshot()` is invoked. They then create multiple snapshot names to verify term/index ordering, exercise cleanup with a retention policy of one snapshot, and finally create a legacy single-file snapshot to ensure it still wins over an older directory snapshot.

## State And Persistence Behavior
The state is entirely filesystem-backed under the Ratis snapshot directory. Cleanup is intentionally gated by `signalNewSnapshot`, avoiding deletion merely because `loadLatestSnapshot()` observed old directories. This guards snapshot retention from accidental eager cleanup.

## Dependencies And Integration Points
Uses Apache Ratis `TermIndex`, `SnapshotRetentionPolicy`, `FileListSnapshotInfo`, `SingleFileSnapshotInfo`, and JUnit temporary storage. It integrates with the helper snapshot format used by the Raft snapshot manager tests.

## Risks And Edge Cases
The cleanup path must handle empty directories, exactly one snapshot, multiple snapshots, and mixed file/directory snapshot formats. Compatibility with `SimpleStateMachineStorage.getSnapshotFileName` is critical because Ratis naming drives both discovery and ordering.

## Test Signals
Passing tests signal lazy snapshot refresh, correct newest-term/newest-index selection, deletion only after explicit signaling, retention of a single newest snapshot, and legacy single-file snapshot support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorageTest.java -->
