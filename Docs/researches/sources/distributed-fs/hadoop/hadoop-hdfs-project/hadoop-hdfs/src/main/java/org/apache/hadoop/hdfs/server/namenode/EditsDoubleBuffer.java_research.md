# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditsDoubleBuffer.java

## Purpose
`EditsDoubleBuffer` provides the two-buffer edit-log staging mechanism used by edit-log output streams. New edits are written into the current buffer while the ready buffer is flushed, avoiding allocation and allowing callers to separate write and sync phases.

## Important APIs and Types
Main methods are `writeOp`, `writeRaw`, `close`, `setReadyToFlush`, `flushTo`, `shouldForceSync`, `isFlushed`, byte/transaction counters, and ready/current buffer accessors. Nested `TxnBuffer` extends `DataOutputBuffer`, tracks `firstTxId` and `numTxns`, and serializes operations through `FSEditLogOp.Writer`.

## Control Flow
Writes append to `bufCurrent`. `setReadyToFlush` asserts the previous ready buffer is empty, then swaps current and ready. `flushTo` writes the ready buffer to an output stream and resets it. `close` refuses to close if current bytes remain and logs a decoded dump of unflushed edits for diagnostics.

## State and Persistence
State is in-memory buffer content plus transaction metadata. Persistence occurs only when a caller flushes the ready buffer to a concrete stream.

## Dependencies and Integration
Used by `EditLogFileOutputStream` and `EditLogBackupOutputStream`. It depends on `FSEditLogOp.Writer`, `DataOutputBuffer`, `HdfsServerConstants.INVALID_TXID`, and diagnostic hex encoding.

## Risks and Test Signals
Correct use requires `setReadyToFlush` only when the ready buffer is empty. Closing with unflushed data intentionally fails and can log raw edit bytes. Tests should cover txid tracking, raw writes, force-sync threshold, swap/flush/reset behavior, close diagnostics, and malformed unflushed edit decoding.
