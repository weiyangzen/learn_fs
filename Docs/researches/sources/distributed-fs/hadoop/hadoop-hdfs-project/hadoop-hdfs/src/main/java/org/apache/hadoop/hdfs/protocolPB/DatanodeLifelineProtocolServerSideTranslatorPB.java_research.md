# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/DatanodeLifelineProtocolServerSideTranslatorPB.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/DatanodeLifelineProtocolServerSideTranslatorPB.java

Purpose: server-side PB translator for lifeline RPCs, forwarding `sendLifeline` to `DatanodeLifelineProtocol`.

Important APIs: constructor stores the delegate. `sendLifeline` converts protobuf storage reports to `StorageReport[]`, converts optional `VolumeFailureSummary`, converts registration, and calls the delegate with cache, transfer, xceiver, and failed volume metrics.

Control flow and state: only stores `impl` and reuses a static empty response. `IOException` is converted to `ServiceException`.

Dependencies and integration: uses `PBHelperClient.convertStorageReports`, `PBHelper.convertVolumeFailureSummary`, `PBHelper.convert(DatanodeRegistration)`, and generated lifeline/datanode protos.

Risks and test signals: lifeline uses `HeartbeatRequestProto`, so drift from heartbeat field semantics can affect behavior. Tests should compare a client-built lifeline request with server decode behavior, including absent volume failure summary, zero cache fields, and exception wrapping.
