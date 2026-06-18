# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalProgressLogger.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalProgressLogger.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalProgressLogger.java

### Purpose
`RaftJournalProgressLogger` adapts the generic `AbstractJournalProgressLogger` to embedded-journal replay progress.

### Important APIs, Types, And Functions
The constructor accepts a `JournalStateMachine` and optional final commit index. `getLastAppliedIndex()` returns `JournalStateMachine.getLastAppliedCommitIndex()`. `getJournalName()` returns a constant `"RAFT"`.

### Control Flow
There is no complex flow; callers periodically invoke inherited logging, which asks this class for the current applied index and label.

### State, Persistence, And Dependencies
It stores only a state-machine reference. It has no persistence. It depends on `AbstractJournalProgressLogger`, `OptionalLong`, and `JournalStateMachine`.

### Integration Points
`RaftJournalSystem.catchUp()` uses it when a `LeaderNotReadyException` suggests Ratis is still replaying, giving progress estimates while gaining primacy.

### Risks
The optional end index may be absent if Ratis group info could not be read, reducing progress logs to current index only. Accuracy depends on `mLastAppliedCommitIndex` being updated after every transaction.

### Test Signals
Validate last-applied forwarding, journal name, behavior with present and absent end commit indexes, and integration with catch-up retry logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalProgressLogger.java -->
