<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/QJournalProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/QJournalProtocolPB.java

Purpose: Protobuf RPC interface marker for the main `QJournalProtocol`, adding protocol metadata and NameNode-to-JournalNode Kerberos annotations to the generated blocking service.

Important APIs/types/functions: Extends `QJournalProtocolService.BlockingInterface`; annotated with protocol name `org.apache.hadoop.hdfs.qjournal.protocol.QJournalProtocol`, version `1`, and qjournal Kerberos principals.

Control flow: No logic. Hadoop RPC binds generated protobuf qjournal service methods through this interface.

State and persistence behavior: None. It declares the wire service surface for remote JournalNode mutation and read operations.

Dependencies/integration: Used by `IPCLoggerChannel.createProxy`, `QJournalProtocolTranslatorPB`, and server-side translator registration.

Risks: Protocol metadata changes are compatibility-sensitive. Security annotations must align with NameNode client and JournalNode server login configuration.

Test signals: RPC setup tests should verify protocol engine registration, method support queries, secure principal resolution, and version compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/QJournalProtocolPB.java -->
