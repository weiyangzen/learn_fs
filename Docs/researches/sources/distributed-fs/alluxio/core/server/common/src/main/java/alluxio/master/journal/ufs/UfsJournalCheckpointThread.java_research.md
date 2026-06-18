# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointThread.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointThread.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointThread.java

### Purpose
`UfsJournalCheckpointThread` is the standby tailer for UFS journals. It continuously replays checkpoint/log files into a master, reports catch-up progress, and periodically writes compacted checkpoints.

### Important APIs, Types, And Functions
It extends `AutopsyThread`. Public methods are `awaitTermination(boolean)`, `getNextSequenceNumber()`, `getCatchupState()`, and `onError()`. Core private methods are `runInternal()`, `maybeCheckpoint()`, and `writeCheckpoint(long)`. `CatchupState` reports `NOT_STARTED`, `IN_PROGRESS`, and `DONE`.

### Control Flow
`run()` starts a progress logger thread, then `runInternal()` loops over `JournalReader.advance()`. Checkpoints restore master state; log entries apply to the master and sinks. When no entry is found, the thread maybe checkpoints and sleeps. Shutdown optionally waits a quiet period; active checkpoint writes are interrupted and cancelled.

### State, Persistence, And Dependencies
It owns a `UfsJournalReader`, next sequence-to-checkpoint, shutdown flags, checkpointing flag, catch-up state, and last applied sequence. Persistent writes occur through `UfsJournalCheckpointWriter`. Dependencies include `Master`, `UfsJournal`, `JournalUtils`, `UfsJournalProgressLogger`, configuration sleep/checkpoint thresholds, and `AutopsyThread`.

### Integration Points
`UfsJournal.start()`, `awaitLosePrimacy()`, and `resume()` create this thread. `gainPrimacy()` and `suspend()` stop it and use `getNextSequenceNumber()` to continue replay or record suspend position.

### Risks
A crashed thread propagates during `awaitTermination()` and can kill standby promotion. Interrupted checkpoints are cancelled, but shutdown handling must distinguish intentional interruption. I/O errors reopen the reader and continue, while corruption can crash the master. Quiet-period shutdown is essential to avoiding missed final entries.

### Test Signals
Test checkpoint restore and log apply, catch-up state transitions, checkpoint threshold behavior, cancellation of in-progress checkpoints, quiet-period shutdown, I/O reader reopen, autopsy error propagation, progress logger shutdown, and sequence returned after termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointThread.java -->
