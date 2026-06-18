<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FenceResponse.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FenceResponse.java

## Purpose

`FenceResponse` is the return value for `JournalProtocol.fence`. It tells a new journal writer what epoch it replaced, the last transaction observed by the journal, and whether the journal was in sync.

## Important APIs and types

The immutable fields are `previousEpoch`, `lastTransactionId`, and `isInSync`. Public methods are the constructor, `getPreviousEpoch()`, `getLastTransactionId()`, and `isInSync()`.

## Control flow

A NameNode or fencer calls `JournalProtocol.fence(...)`. The journal implementation fences older writers, computes these status values, and returns `FenceResponse`. Callers use it to decide whether journal state is safe for failover or recovery.

## State and persistence behavior

The response is in-memory, but it summarizes persistent edit-log/journal state and fencing epoch state maintained by the journal implementation.

## Dependencies and integration points

It depends on `JournalProtocol` semantics and is serialized through journal RPC protobuf translators. It integrates with backup-node journaling and HA failover safety checks.

## Risks and test signals

Incorrect `isInSync` or transaction IDs can make failover unsafe. Tests should cover fencing an older writer, repeated fence calls, stale epoch rejection, and out-of-sync journal reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FenceResponse.java -->
