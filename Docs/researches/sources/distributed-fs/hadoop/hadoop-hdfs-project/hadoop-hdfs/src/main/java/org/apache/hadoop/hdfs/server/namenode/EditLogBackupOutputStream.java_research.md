# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogBackupOutputStream.java

## Purpose
`EditLogBackupOutputStream` streams serialized edit-log operations from an active NameNode to a BackupNode over `JournalProtocol` RPC.

## Important APIs and Types
It extends `EditLogOutputStream`, owns an RPC proxy to `JournalProtocol`, backup registration, active `JournalInfo`, a reusable `DataOutputBuffer`, and an `EditsDoubleBuffer`. It implements `write`, `create`, `close`, `abort`, `setReadyToFlush`, `flushAndSync`, `getRegistration`, and `startLogSegment`.

## Control Flow
Writes serialize operations into the current double buffer. `setReadyToFlush` swaps buffers. `flushAndSync` copies ready bytes into a byte array, resets the output buffer, and calls `backupNode.journal(journalInfo, 0, firstTxToFlush, numReadyTxns, data)`. `create` resets buffers and updates log version; `close` refuses unflushed data and stops the RPC proxy.

## State and Persistence
The stream itself has no local durable storage. Durability depends on the remote BackupNode journal handling. Buffer state must be flushed before close.

## Dependencies and Integration
It depends on `NameNodeProxies`, `JournalProtocol`, `NamenodeRegistration`, `JournalInfo`, `RPC.stopProxy`, and `EditsDoubleBuffer`.

## Risks and Test Signals
`writeRaw` is unsupported, so callers must not use raw journal copying through this class. The `durable` argument is ignored because durability is delegated to RPC receiver behavior. Tests should cover connection failure, journal RPC payload txid/count correctness, close with pending bytes, abort idempotence, and start-log-segment forwarding.
