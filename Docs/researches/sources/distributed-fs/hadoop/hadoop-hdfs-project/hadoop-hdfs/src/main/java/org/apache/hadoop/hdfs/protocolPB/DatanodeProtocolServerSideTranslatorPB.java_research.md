# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/DatanodeProtocolServerSideTranslatorPB.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/DatanodeProtocolServerSideTranslatorPB.java

Purpose: server-side translator for DataNode protocol PB calls into a `DatanodeProtocol` NameNode implementation.

Important APIs: handles registration, heartbeat, block report, cache report, received/deleted blocks, error report, version request, bad block report, and commit block synchronization. Constructor receives the delegate and `maxDataLength` for block list decoding.

Control flow and state: methods decode protobuf messages, call the delegate, and encode protobuf responses or cached empty responses. Heartbeat responses include commands, HA status, rolling upgrade status v2 plus legacy v1 compatibility, full block report lease ID, and slow-node flag.

Dependencies and integration: depends on `PBHelper`, `PBHelperClient`, `BlockListAsLongs`, `Preconditions`, generated datanode/HDFS protos, and storage compatibility types.

Risks and test signals: block report decoding rejects simultaneous long-list and buffer forms and is bounded by `maxDataLength`. StorageReceivedDeletedBlocks supports old `storageUuid` fallback. Tests should cover both block report encodings, rolling upgrade finalized/non-finalized behavior, storage fallback, null command response, and synchronization target arrays.
