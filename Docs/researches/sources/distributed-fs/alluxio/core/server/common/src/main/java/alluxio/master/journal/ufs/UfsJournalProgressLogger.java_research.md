# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalProgressLogger.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalProgressLogger.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalProgressLogger.java

### Purpose
`UfsJournalProgressLogger` adapts generic journal replay progress logging to UFS journal sequence numbers.

### Important APIs, Types, And Functions
The constructor takes the `UfsJournal`, optional final sequence number, and a supplier for the last applied sequence. `getLastAppliedIndex()` delegates to the supplier. `getJournalName()` returns `UfsJournal.toString()`.

### Control Flow
The checkpoint thread's side progress thread periodically invokes inherited logging; this adapter supplies current progress and journal name.

### State, Persistence, And Dependencies
It stores references only and has no persistent effects. Dependencies include `AbstractJournalProgressLogger`, `OptionalLong`, `Supplier<Long>`, and `UfsJournal`.

### Integration Points
`UfsJournalCheckpointThread.run()` creates this logger using `UfsJournalReader.getLastSN()` as the optional end sequence and `mLastAppliedSN` as current progress.

### Risks
If `getLastSN()` fails, progress estimates lack an end target. The last applied supplier starts at its default until the first log entry is processed, so early logs may show sparse progress.

### Test Signals
Verify supplier forwarding, journal name, optional end sequence behavior, and progress logging during checkpoint-thread replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalProgressLogger.java -->
