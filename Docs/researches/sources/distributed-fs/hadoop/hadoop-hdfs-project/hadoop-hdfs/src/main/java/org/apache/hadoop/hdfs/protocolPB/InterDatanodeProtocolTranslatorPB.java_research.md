# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/InterDatanodeProtocolTranslatorPB.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/InterDatanodeProtocolTranslatorPB.java

Purpose: client-side translator implementing `InterDatanodeProtocol` over protobuf RPC for replica recovery between DataNodes.

Important APIs: constructor configures `ProtobufRpcEngine2` and opens an RPC proxy with UGI, socket factory, and timeout. `initReplicaRecovery` sends a recovering block and converts the response into `ReplicaRecoveryInfo` or null. `updateReplicaUnderRecovery` sends old block and recovery/new block metadata and returns the storage UUID. `isMethodSupported` probes RPC support.

Control flow and state: stores a final PB proxy; `close` stops it. Calls use `ipc` for exception conversion.

Dependencies and integration: depends on `PBHelper`, `PBHelperClient`, Hadoop RPC utilities, and generated inter-datanode protos.

Risks and test signals: if `replicaFound=true` but block/state fields are missing, the client throws `IOException`, protecting against malformed servers. Tests should cover null recovery, malformed response, timeout/proxy setup, and storage UUID return.
