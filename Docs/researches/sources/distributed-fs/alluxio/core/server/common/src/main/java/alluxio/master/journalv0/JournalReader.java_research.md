# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalReader.java

## Purpose
`JournalReader` defines the legacy journal replay protocol: read a checkpoint first, then read completed logs in creation order while rejecting readers whose checkpoint changes during replay.

## Important APIs, Types, and Functions
It defines `isValid()`, `getCheckpointInputStream()`, `getNextInputStream()`, and `getCheckpointLastModifiedTimeMs()`.

## Control Flow, State, and Persistence
The contract requires callers to consume the checkpoint before requesting logs. `getNextInputStream()` returns only completed logs and returns `null` when the next completed log is not available. Validity is based on checkpoint last-modified time captured when the checkpoint stream was opened.

## Dependencies and Integration Points
It depends on `JournalInputStream` and `IOException`; `UfsJournalReader` provides the UFS implementation. Replay engines use it to reconstruct master state from persistent checkpoint and completed log files.

## Risks and Test Signals
Risks include timestamp granularity problems on some filesystems, replay races with checkpoint updates, and missed current-log entries because only completed logs are exposed. Signals include checkpoint-first enforcement, invalidation after checkpoint update, and sequential completed-log replay.
