# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalGarbageCollector.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalGarbageCollector.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalGarbageCollector.java

### Purpose
`UfsJournalGarbageCollector` periodically removes UFS journal files that are no longer needed to recover full master state.

### Important APIs, Types, And Functions
The constructor schedules `gc()` at `MASTER_JOURNAL_GC_PERIOD_MS`. `close()` cancels scheduling and shuts down the executor. `gc()` snapshots journal files and delegates deletion decisions to `gcFileIfStale()`. `deleteNoException()` logs and swallows deletion failures.

### Control Flow
GC keeps the latest checkpoint, sets its end sequence as the checkpoint boundary, and considers older checkpoints, logs at or below that boundary, and temporary checkpoints. Files are only deleted if their last-modified time exceeds the normal or temporary-file threshold.

### State, Persistence, And Dependencies
State is the scheduled executor/future, journal, and UFS handle. Persistent effects are UFS file deletions. Dependencies include `UfsJournalSnapshot`, `UfsJournalFile`, Alluxio configuration thresholds, and `ThreadFactoryUtils`.

### Integration Points
`UfsJournalLogWriter` creates this collector while the journal is primary and closes it with the writer.

### Risks
Incorrect checkpoint boundary calculation can delete logs still needed for recovery. UFS last-modified metadata may be missing or stale, preventing cleanup. Delete failures are non-fatal and can leave buildup. Scheduling starts shortly after writer creation.

### Test Signals
Test latest checkpoint retention, stale old checkpoint/log deletion, fresh file retention, tmp checkpoint threshold, missing last-modified behavior, snapshot listing failure, delete failure logging, and close cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalGarbageCollector.java -->
