# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftSnapshotManager.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftSnapshotManager.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftSnapshotManager.java

### Purpose
`RaftSnapshotManager` downloads the newest available embedded-journal snapshot from peer masters when local Ratis logs are insufficient or leader snapshotting is disallowed.

### Important APIs, Types, And Functions
`downloadSnapshotFromOtherMasters()` starts or polls one async download. `waitForAttemptToComplete()` blocks for an in-flight attempt. `core()` selects candidate snapshots, `retrieveFollowerInfos()` requests peer metadata in parallel, and `downloadSnapshotFromAddress()` streams and installs one snapshot. `SnapshotGrpcInputStream` adapts streamed `SnapshotData` chunks to an `InputStream`.

### Control Flow
The manager compares local snapshot term/index to peer metadata, prioritizes newer peer snapshots by `TermIndex`, downloads into the Ratis tmp dir with `DirectoryMarshaller`, moves the tmp dir to the final snapshot directory name, reloads storage metadata, signals a new snapshot, and updates metrics. Failed peers are tried in descending freshness order.

### State, Persistence, And Dependencies
Persistent output is a directory snapshot under `SnapshotDirStateMachineStorage.getSnapshotDir()`. Volatile state includes one `CompletableFuture` and last download duration/size metrics. Dependencies include `RaftJournalServiceClient`, master address configuration, retry policies, `DirectoryMarshaller`, Apache Commons `FileUtils`, Ratis snapshot naming, and metrics.

### Integration Points
`JournalStateMachine.takeSnapshot()` uses this on leaders when local leader snapshots are not allowed, and `notifyInstallSnapshotFromLeader()` uses it when a follower needs a missing snapshot.

### Risks
Only one download future is tracked; callers must poll or wait to observe completion. Moving tmp directories assumes local filesystem semantics. A failed download deletes tmp data in `finally`. Metadata freshness compares only term/index, so peers with equal snapshots are ignored. Data streaming reads byte-by-byte through the marshaller.

### Test Signals
Cover no peers, no local snapshot, metadata sorting, ignoring stale peer snapshots, successful download/install, tmp cleanup on failure, metrics updates, repeated poll behavior, wait-for-attempt behavior, and chunked stream byte counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftSnapshotManager.java -->
