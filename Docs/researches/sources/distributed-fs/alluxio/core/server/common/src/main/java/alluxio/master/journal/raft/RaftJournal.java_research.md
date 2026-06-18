# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournal.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournal.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournal.java

### Purpose
`RaftJournal` is the per-master `Journal` facade for embedded journals. It binds one `Journaled` state machine to the shared Raft-backed writer managed by `RaftJournalSystem`.

### Important APIs, Types, And Functions
The constructor stores the `Journaled`, journal URI, and `AtomicReference<AsyncJournalWriter>`. `getStateMachine()` exposes the master state machine for replay and snapshotting. `createJournalContext()` returns `MasterJournalContext` wrapping the current async writer or throws `UnavailableException` when the server is not primary or the writer is closed.

### Control Flow
Creation is passive. Write requests ask for a journal context, dereference the shared writer, and fail fast if it is absent. `close()` is intentionally empty because ownership of the shared writer and Ratis resources lives in `RaftJournalSystem`.

### State, Persistence, And Dependencies
The object keeps only pointers. Persistence is delegated to `AsyncJournalWriter`, `RaftJournalWriter`, and Ratis. It depends on Alluxio `Journal`, `Journaled`, `MasterJournalContext`, and `UnavailableException`.

### Integration Points
`RaftJournalSystem.createJournal()` creates one instance per `Master` and stores it by master name. `JournalStateMachine` later iterates these journals to replay entries and write or restore snapshots.

### Risks
The class is `@NotThreadSafe`, but the writer reference is atomic because writer availability changes during primacy transitions. Callers must treat `UnavailableException` as retryable failover. A stale context may continue to use an async writer until higher-level close/flush behavior stops it.

### Test Signals
Verify context creation with present and absent writer references, location propagation, state-machine exposure, close no-op behavior, and failover windows where the writer reference flips to null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournal.java -->
