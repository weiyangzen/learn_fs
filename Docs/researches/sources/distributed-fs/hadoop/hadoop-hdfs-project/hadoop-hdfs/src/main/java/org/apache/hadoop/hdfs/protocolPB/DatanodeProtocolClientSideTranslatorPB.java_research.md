# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/DatanodeProtocolClientSideTranslatorPB.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/DatanodeProtocolClientSideTranslatorPB.java

Purpose: client-side translator for DataNode-to-NameNode protocol calls, implementing `DatanodeProtocol` over `DatanodeProtocolPB`.

Important APIs: registers DataNodes, sends heartbeats, block reports, cache reports, received/deleted block notifications, error reports, version requests, bad block reports, and block synchronization commits. It also implements method-support probing and closeable proxy cleanup.

Control flow and state: stores an RPC proxy. Methods build request protos, invoke the proxy through `ipc`, and convert response protos to native commands or status objects. Block reports choose buffer-based or long-list encoding based on `NamespaceInfo.Capability.STORAGE_BLOCK_REPORT_BUFFERS`.

Dependencies and integration: integrates DataNode service loops with NameNode PB RPC, `RPC`, `ProtobufRpcEngine2`, `PBHelper`, `PBHelperClient`, storage report conversion, and slow peer/disk reporting.

Risks and test signals: capability-gated block report encoding, optional rolling-upgrade v1/v2 response fields, skipped null synchronization targets, and storage UUID compatibility fields are important. Tests should cover old/new block report forms, heartbeat optional metrics, command conversion, and method support.
