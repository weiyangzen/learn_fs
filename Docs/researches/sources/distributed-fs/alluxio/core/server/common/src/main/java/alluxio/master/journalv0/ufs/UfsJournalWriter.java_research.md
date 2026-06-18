# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsJournalWriter.java

## Purpose
`UfsJournalWriter` is the legacy UFS-backed journal writer. It owns checkpoint creation, sequence-number assignment, current-log writing, completed-log rotation, completed-log deletion, and UFS resource closure.

## Important APIs, Types, and Functions
The public methods are `completeLogs()`, `getCheckpointOutputStream(long)`, `write(JournalEntry)`, `flush()`, `getNextSequenceNumber()`, `close()`, `recover()`, `deleteCompletedLogs()`, and `completeCurrentLog()`. It contains `CheckpointOutputStream` for temporary checkpoint writes and `EntryOutputStream` for current-log writes/rotation. It uses `UfsCheckpointManager`, `JournalFormatter`, `UnderFileSystem`, `CreateOptions`, `ExceptionMessage`, and configuration key `MASTER_JOURNAL_LOG_SIZE_BYTES_MAX`.

## Control Flow, State, and Persistence
The writer creates a UFS handle, computes `completed/` and `checkpoint.data.tmp` paths, and starts sequence numbers at one. `getCheckpointOutputStream()` recovers any interrupted checkpoint update, creates the journal directory if needed, sets the next sequence number from the supplied latest sequence, deletes stale temp checkpoint files, and returns a singleton checkpoint stream. Normal `write()` and `flush()` reject calls until the checkpoint stream has been closed.

`CheckpointOutputStream.write()` assigns a sequence number and serializes entries to the temporary checkpoint. Closing the checkpoint flushes and closes the temp file, atomically updates `checkpoint.data` through `UfsCheckpointManager`, completes any current log, and marks the stream closed. `EntryOutputStream` writes current log entries with assigned sequence numbers, flushes them, and marks the log for rotation when it exceeds max size, when UFS does not support flush, or after write/flush failures. Rotation closes `log.out`, renames it to the next completed log, and opens a fresh current log.

## Dependencies and Integration Points
It integrates with `UfsMutableJournal`, `AsyncJournalWriter`, `UfsCheckpointManager`, and legacy replay through `UfsJournalReader`. Persistent artifacts are `checkpoint.data.tmp`, `checkpoint.data`, `checkpoint.data.backup`, `log.out`, and `completed/log.%020d`.

## Risks and Test Signals
Risks include sequence-number gaps if serialization fails after incrementing, `deleteCompletedLogs()` iterating down to log zero, UFS rename semantics, no-flush object-store durability, singleton stream lifecycle misuse, and runtime exceptions during checkpoint update recovery. Signals are checkpoint-before-log enforcement, write-after-close errors, crash recovery for checkpoint files, log rotation on size/no-flush/error, replay from checkpoint plus completed logs, and UFS handle closure.
