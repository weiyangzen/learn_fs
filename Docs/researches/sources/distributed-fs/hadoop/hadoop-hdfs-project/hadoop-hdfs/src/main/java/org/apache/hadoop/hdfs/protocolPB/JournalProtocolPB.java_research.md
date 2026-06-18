# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/JournalProtocolPB.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/JournalProtocolPB.java

Purpose: protobuf RPC interface for journaling edits from a NameNode to a remote journal receiver, currently used for BackupNode publishing.

Important API: extends generated `JournalProtocolService.BlockingInterface`; declares NameNode principal for both server and client; publishes protocol name `org.apache.hadoop.hdfs.server.protocol.JournalProtocol`, version 1.

Control flow and state: no implementation or state. The interface exists to attach Hadoop RPC and security annotations to generated protobuf service methods.

Dependencies and integration: paired with journal client/server translators and `JournalProtocol` implementations.

Risks and test signals: protocol metadata is compatibility-critical for edit journaling and fencing. Tests should verify secure proxy setup and successful journal/startLogSegment/fence calls through the translators.
