# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogInputStream.java

## Purpose
`EditLogInputStream` is the abstract base for all edit-log readers. It defines transaction range metadata, operation reading, corruption resynchronization, skipping by transaction ID, layout version access, position reporting, length reporting, in-progress status, operation-size limits, and locality hints.

## Important APIs and Types
Subclasses implement `getName`, `getFirstTxId`, `getLastTxId`, `close`, `nextOp`, `getVersion`, `getPosition`, `length`, `isInProgress`, `setMaxOpSize`, and `isLocalLog`. The base class implements `readOp`, `resync`, default `nextValidOp`, `scanNextOp`, `skipUntil`, and cached-op handling.

## Control Flow
`readOp` returns a previously cached operation first, otherwise delegates to `nextOp`. `resync` populates the cache with `nextValidOp`, enabling callers to skip corrupted sections. `skipUntil` reads forward until it finds an operation with txid at least the requested value and caches that operation for the next `readOp`.

## State and Persistence
Only `cachedOp` is stored in the base class. Persistence belongs to concrete stream sources.

## Dependencies and Integration
Used by `FSEditLogLoader`, checkpoint roll-forward, journal recovery, backup-node input streams, file/URL/byte-string streams, and any custom journal manager stream.

## Risks and Test Signals
The default `nextValidOp` catches `Throwable` and returns null, so subclasses needing precise corruption handling should override it. `skipUntil` consumes operations and depends on txid ordering. Tests should cover cached-op behavior, resync behavior, skip boundaries, EOF, corrupted stream subclasses, and stream name/current-name reporting.
