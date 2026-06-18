# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalLogWriter.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalLogWriter.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalLogWriter.java

### Purpose
`UfsJournalLogWriter` writes primary-master journal entries to UFS log files, rotates completed logs, flushes durable data, and recovers from UFS write/flush failures.

### Important APIs, Types, And Functions
It implements `JournalWriter` with `write()`, `flush()`, `close()`, and `getNextSequenceNumber()`. Important helpers are `maybeRecoverFromUfsFailures()`, `recoverLastPersistedJournalEntry()`, `maybeRotateLog()`, `createNewLogFile()`, `completeLog()`, and inner `JournalOutputStream`.

### Control Flow
Writes ensure primary writability, recover if a prior I/O failure occurred, rotate if needed, assign the next sequence, write a delimited entry, enqueue it for retry, and advance the sequence. Flush syncs the output stream and clears retry entries; oversize logs or UFSs without true flush rotate on the next write. Recovery scans the incomplete log, completes it at the last persisted sequence, creates a new log, and rewrites unflushed entries from the retry queue.

### State, Persistence, And Dependencies
Persistent files are `logs/0x<start>-0x7fffffffffffffff` while open and `logs/0x<start>-0x<next>` when completed. State includes next sequence, rotate flag, current output stream, retry queue, recovery flag, max log size, closed flag, and garbage collector. Dependencies include `UnderFileSystem`, `UfsJournalSnapshot`, `JournalEntryStreamReader`, metrics, `CreateOptions`, and `OpenOptions`.

### Integration Points
`UfsJournal.gainPrimacy()` creates this writer and wraps it in `AsyncJournalWriter`. The writer's GC removes superseded files, and `UfsJournalReader` consumes completed logs.

### Risks
UFS rename and flush semantics differ, especially for object stores; the code rotates on non-flush-capable UFSs to force close/commit. Recovery cannot fill gaps before the oldest retry entry. Closing completes the current log and can race with leadership loss, so `completeLog()` rechecks writability and tolerates concurrent completion.

### Test Signals
Cover sequence assignment, log creation and completion, flush clearing retry queue, size-based rotation, non-flush UFS rotation, write/flush failure recovery, missing-entry recovery fatal path, concurrent complete handling, empty log deletion, close behavior, and GC lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalLogWriter.java -->
