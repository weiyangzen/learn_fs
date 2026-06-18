# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/BufferedJournalApplier.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/BufferedJournalApplier.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/BufferedJournalApplier.java

### Purpose
`BufferedJournalApplier` serializes application of Raft journal entries into Alluxio master state machines while supporting nonblocking suspension for backup or state-inspection workflows. During suspension, committed entries are held in an in-memory FIFO queue and later applied during resume or bounded catch-up.

### Important APIs, Types, And Functions
The public surface is `processJournalEntry()`, `suspend()`, `resume()`, `catchup(long)`, `isSuspended()`, and `close()`. `applyToMaster()` maps a `JournalEntry` to a master via `JournalEntryAssociation`, calls the target `Journaled.processJournalEntry()`, then appends to configured `JournalSink`s. The inner `RaftJournalCatchupThread` extends `AbstractCatchupThread` and drains the suspend buffer until a target sequence is reached.

### Control Flow
Normal `processJournalEntry()` holds `mStateLock` and either applies immediately or enqueues and notifies waiters. `suspend()` flips `mSuspended`; `resume()` cancels any catch-up thread, drains buffered entries, and eventually takes the state lock once the backlog is small or resume has run too long. `catchup()` requires suspension, starts one background thread, and leaves the applier suspended after reaching the requested sequence.

### State, Persistence, And Dependencies
State is in-memory only: `mLastAppliedSequence`, `mSuspended`, `mResumeInProgress`, `mSuspendBuffer`, and the optional catch-up thread. There is no on-disk spill despite a TODO. Dependencies include `RaftJournal`, `Journaled`, `JournalEntryAssociation`, `JournalUtils`, `JournalSink`, `LockResource`, and `AbstractCatchupThread`.

### Integration Points
`JournalStateMachine` owns this class to decouple Ratis commit application from Alluxio master state access. It is used by Raft suspend/resume/catchup operations and by snapshot pause logic, which resumes the applier before reloading state.

### Risks
The suspend buffer can grow without bound during long suspensions. `resume()` unconditionally unlocks `mStateLock` in `finally`, so its correctness relies on always having acquired the lock by construction before the block exits. Catch-up drains under `mSuspendBuffer` synchronization while `processJournalEntry()` enqueues under both locks, making lock-order changes risky. Replay failures are fatal or delegated to `JournalUtils`.

### Test Signals
Cover immediate apply, suspend-buffer ordering, resume with small and large backlogs, catch-up to an exact sequence, cancellation by resume, duplicate resume/catchup preconditions, sink append side effects, unknown journal entry routing, and stress cases where entries arrive while resume is draining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/BufferedJournalApplier.java -->
