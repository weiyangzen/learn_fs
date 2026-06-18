# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/InterDatanodeProtocolPB.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/InterDatanodeProtocolPB.java

Purpose: protobuf RPC interface for DataNode-to-DataNode recovery coordination via `InterDatanodeProtocol`.

Important API: extends generated `InterDatanodeProtocolService.BlockingInterface`; declares DataNode principals for both client and server; publishes protocol name `org.apache.hadoop.hdfs.server.protocol.InterDatanodeProtocol`, version 1.

Control flow and state: none. Hadoop RPC consumes it for metadata and generated blocking methods.

Dependencies and integration: paired with the client and server translators for replica recovery initialization and updating replicas under recovery.

Risks and test signals: incorrect Kerberos principal metadata can break secure inter-DataNode recovery. Integration tests should exercise replica recovery RPCs in secure and non-secure setups and verify client/server protocol version agreement.
