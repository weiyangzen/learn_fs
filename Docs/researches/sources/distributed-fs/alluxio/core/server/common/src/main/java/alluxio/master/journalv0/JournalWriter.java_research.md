# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalWriter.java

## Purpose
`JournalWriter` defines the legacy read-write journal persistence protocol. It separates checkpoint creation from incremental log writes and provides recovery and log-compaction operations.

## Important APIs, Types, and Functions
The interface defines `completeLogs()`, `getCheckpointOutputStream(long)`, `write(JournalEntry)`, `flush()`, `getNextSequenceNumber()`, `close()`, `recover()`, `deleteCompletedLogs()`, and `completeCurrentLog()`.

## Control Flow, State, and Persistence
The contract requires checkpoint output to be obtained and closed before normal log writes begin. Checkpoints should represent master state with completed logs applied; subsequent current logs contain later entries. Completing logs moves current log data into the completed-log sequence, and deleting completed logs is safe after a checkpoint reflects their state.

## Dependencies and Integration Points
It depends on protobuf `JournalEntry`, `JournalOutputStream`, and `IOException`. `UfsJournalWriter` is the concrete implementation in this subset, and `AsyncJournalWriter` can wrap it for batched flushing.

## Risks and Test Signals
Risks include caller misuse of checkpoint-before-log ordering, sequence-number gaps, deleting logs before a durable checkpoint update, and close/recover idempotency. Signals are checkpoint/log replay round trips, crash-recovery simulations, log rotation tests, and sequence-number monotonicity.
