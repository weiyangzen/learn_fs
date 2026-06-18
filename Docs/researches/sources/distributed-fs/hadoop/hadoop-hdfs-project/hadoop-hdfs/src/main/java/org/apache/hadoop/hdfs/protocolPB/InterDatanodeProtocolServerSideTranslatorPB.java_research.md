# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/InterDatanodeProtocolServerSideTranslatorPB.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/InterDatanodeProtocolServerSideTranslatorPB.java

Purpose: server-side translator for inter-DataNode recovery RPCs.

Important APIs: `initReplicaRecovery` converts a `RecoveringBlock`, invokes `impl.initReplicaRecovery`, and returns either `replicaFound=false` or block plus original replica state. `updateReplicaUnderRecovery` converts the extended block and returns the storage UUID from the delegate.

Control flow and state: only stores the `InterDatanodeProtocol` delegate. `IOException` from the delegate is wrapped in `ServiceException`.

Dependencies and integration: uses `PBHelper` for recovering blocks and replica state, `PBHelperClient` for replica recovery info and extended blocks, and generated inter-datanode protos.

Risks and test signals: null recovery info is explicitly represented through `replicaFound=false`; clients expect block and state when true. Tests should cover found/not-found responses, missing-field client validation, storage UUID propagation, and exception wrapping.
