# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/JournalProtocolServerSideTranslatorPB.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/JournalProtocolServerSideTranslatorPB.java

Purpose: server-side translator from `JournalProtocolPB` calls to a `JournalProtocol` implementation.

Important APIs: `journal` forwards journal info, epoch, first transaction ID, transaction count, and raw edit records. `startLogSegment` forwards journal info, epoch, and txid. `fence` returns previous epoch, last transaction ID, and in-sync state from `FenceResponse`.

Control flow and state: stores only the delegate and cached empty responses for void calls. `IOException` becomes `ServiceException`.

Dependencies and integration: uses `PBHelper.convert(JournalInfo)` and generated journal protos. It integrates remote edit logging and fencing with Hadoop protobuf RPC.

Risks and test signals: byte-array edit record conversion and epoch/fencing fields must remain exact. Tests should cover non-empty records, zero-record edge cases, start segment txid propagation, fence response fields, and exception wrapping from the delegate.
