# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogOutputStream.java

## Purpose
`EditLogOutputStream` is the abstract base for edit-log journal writers. It defines how edit operations and raw edit bytes are written, initialized, flushed, synced, aborted, and reported.

## Important APIs and Types
Subclasses implement `write`, `writeRaw`, `create`, `close`, `abort`, `setReadyToFlush`, and `flushAndSync`. The base class tracks `numSync`, `totalTimeSync`, and `currentLogVersion`, and provides `flush`, `flush(boolean)`, `shouldForceSync`, `generateReport`, and version getters/setters.

## Control Flow
Callers write operations, call `setReadyToFlush`, then `flush`. The base `flush` increments sync count, times `flushAndSync`, and accumulates sync duration. Subclasses decide actual durability and buffering policy.

## State and Persistence
The abstract class does not persist edits itself. It stores metrics and the current layout version used by concrete writers.

## Dependencies and Integration
Implemented by local file, backup-node, and other journal streams. Used by `FSEditLog`, `JournalSet`, and NameNode metrics/reporting paths.

## Risks and Test Signals
`getLastJournalledTxId` defaults to invalid, so tracking must be provided elsewhere or overridden. `shouldForceSync` defaults false, making subclass implementation important for buffer pressure. Tests should verify sync metric accounting, durable flag propagation, version propagation, report generation, and subclass behavior for abort-after-failure.
