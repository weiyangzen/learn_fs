# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorage.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorage.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorage.java

### Purpose
`SnapshotDirStateMachineStorage` implements Ratis `StateMachineStorage` for Alluxio snapshots that may be directories instead of single files, while preserving compatibility with older single-file snapshots.

### Important APIs, Types, And Functions
`init()` stores `RaftStorage` and loads the latest snapshot. `findLatestSnapshot()` scans snapshot names matching Ratis' snapshot regex and returns `SingleFileSnapshotInfo` or `FileListSnapshotInfo`. `loadLatestSnapshot()`, `signalNewSnapshot()`, `cleanupOldSnapshots()`, `getSnapshotDir()`, and `getTmpDir()` complete the storage contract. `matchSnapshotPath()` exposes regex matching.

### Control Flow
The latest snapshot is the matching path with the greatest term/index. Directory snapshots are represented by all non-MD5 files with relative paths and optional stored MD5 hashes. Cleanup only runs after `signalNewSnapshot()` and deletes older matching snapshot paths beyond the retention count.

### State, Persistence, And Dependencies
State is the `RaftStorage`, cached latest `SnapshotInfo`, and a boolean indicating a newly taken snapshot. Persistent data is in the Ratis state-machine dir and tmp dir. Dependencies include Ratis snapshot info types, `SimpleStateMachineStorage`, MD5 utilities, Apache Commons file filters, and Java NIO file listing.

### Integration Points
`JournalStateMachine`, `RaftSnapshotManager`, and `RaftJournalServiceHandler` share this storage for local snapshot creation, peer snapshot install, latest metadata, and cleanup after Ratis snapshot retention decisions.

### Risks
`Files.list()` failures return null latest snapshots and only log a warning. Directory snapshots without MD5 sidecars are allowed, so integrity coverage may vary by writer. Cleanup depends on `signalNewSnapshot()` and will not remove old snapshots if that call is missed.

### Test Signals
Test empty dirs, latest selection across term/index, old single-file compatibility, directory file-list metadata with relative paths, missing MD5 files, retention cleanup, tmp/snapshot directory paths, and malformed snapshot names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotDirStateMachineStorage.java -->
