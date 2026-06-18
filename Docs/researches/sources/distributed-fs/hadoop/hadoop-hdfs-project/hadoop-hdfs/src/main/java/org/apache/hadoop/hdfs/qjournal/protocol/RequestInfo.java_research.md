<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/RequestInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/RequestInfo.java

Purpose: Value object attached to mutating qjournal RPCs to identify the journal, nameservice, active-writer epoch, per-epoch IPC serial, and highest committed transaction known by the writer.

Important APIs/types/functions: Constructor plus getters/setters for epoch and IPC serial, `getJournalId`, `getNameServiceId`, `getCommittedTxId`, and `hasCommittedTxId`.

Control flow: `IPCLoggerChannel.createReqInfo` increments the serial for each write-like RPC. `Journal.checkRequest` uses epoch to fence stale writers, serial to reject reordered/retried stale IPCs, and committed txid to update local lag/recovery metadata.

State and persistence behavior: In-memory RPC payload only. Its fields drive persistent updates to `last-promised-epoch` and `committed-txid` on the server.

Dependencies/integration: Converted to/from `RequestInfoProto` by `QJournalProtocolTranslatorPB` and server translator. Uses `HdfsServerConstants.INVALID_TXID` to represent absent committed txid.

Risks: Epoch and serial setters make the object mutable, so callers should not reuse it across RPCs after conversion. Moving committed txid backwards is rejected by server/client preconditions.

Test signals: Verify protobuf conversion with and without nameservice/committed txid, serial monotonic rejection, higher-epoch promise updates, and absent committed-txid behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/RequestInfo.java -->
