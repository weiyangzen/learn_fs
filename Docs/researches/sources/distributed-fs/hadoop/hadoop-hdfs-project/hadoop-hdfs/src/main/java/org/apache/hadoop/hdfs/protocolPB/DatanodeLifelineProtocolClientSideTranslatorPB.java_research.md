# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/DatanodeLifelineProtocolClientSideTranslatorPB.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/DatanodeLifelineProtocolClientSideTranslatorPB.java

Purpose: client-side translator from `DatanodeLifelineProtocol` to `DatanodeLifelineProtocolPB`, letting a DataNode send lightweight lifeline messages to a NameNode over protobuf RPC.

Important APIs: constructor configures `ProtobufRpcEngine2` and creates a NameNode proxy. `sendLifeline` builds a heartbeat-shaped `HeartbeatRequestProto` with registration, storage reports, cache stats when nonzero, transfer/xceiver/failure counts, and optional `VolumeFailureSummary`. `isMethodSupported` probes server method support.

Control flow and state: stores the RPC proxy and null controller. `close` stops the proxy. Calls use `ShadedProtobufHelper.ipc` to translate protobuf service failures back to `IOException`.

Dependencies and integration: integrates DataNode lifeline machinery with Hadoop RPC, UGI, socket factories, `PBHelper`, and `PBHelperClient` storage report conversions.

Risks and test signals: cache capacity/used are omitted when zero, so tests should verify server defaults match intended zero semantics. Cover null volume summaries, RPC proxy lifecycle, and method-support checks.
