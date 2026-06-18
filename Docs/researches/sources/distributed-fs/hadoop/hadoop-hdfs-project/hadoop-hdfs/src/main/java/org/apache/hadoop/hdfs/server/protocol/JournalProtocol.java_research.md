<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/JournalProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/JournalProtocol.java

## Purpose

`JournalProtocol` defines the RPC path used by an active NameNode to publish edit-log records to a remote BackupNode-style journal receiver.

## Important APIs and types

The interface is secured with NameNode Kerberos principals and declares `versionID = 1L`. Methods are `journal(JournalInfo, epoch, firstTxnId, numTxns, byte[] records)`, `startLogSegment(JournalInfo, epoch, txid)`, and `fence(JournalInfo, epoch, fencerInfo)` returning `FenceResponse`.

## Control flow

The active NameNode sends edit batches through `journal`, announces log rolls through `startLogSegment`, and uses `fence` to invalidate older writers when a new epoch begins. Implementations reject stale epochs with fencing errors and append serialized edit records to remote state.

## State and persistence behavior

Server implementations persist edit-log records and log-segment boundaries. The interface carries epoch and transaction ID ordering needed to make remote journal state consistent.

## Dependencies and integration points

It depends on `JournalInfo`, `FenceResponse`, `FencedException`, NameNode storage/edit-log code, and `JournalProtocol.proto` translators.

## Risks and test signals

Risks are severe: stale writers, transaction gaps/overlap, or namespace mismatches can corrupt recovery. Tests should cover in-order journal batches, log roll boundaries, fencing with old/new epochs, namespace mismatch, and RPC retry around duplicate batches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/JournalProtocol.java -->
