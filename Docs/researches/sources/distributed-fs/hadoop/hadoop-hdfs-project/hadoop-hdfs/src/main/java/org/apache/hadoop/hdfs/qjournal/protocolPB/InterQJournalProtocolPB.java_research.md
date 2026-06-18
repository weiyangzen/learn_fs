<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolPB.java

Purpose: Protobuf RPC interface marker for `InterQJournalProtocol`, adding Hadoop protocol metadata and JournalNode Kerberos annotations to the generated blocking service.

Important APIs/types/functions: Extends `InterQJournalProtocolService.BlockingInterface`; annotated with `@ProtocolInfo` protocol name/version and `@KerberosInfo`.

Control flow: No executable logic. Hadoop RPC uses this interface to bind generated protobuf service methods to secure JournalNode-to-JournalNode RPC endpoints.

State and persistence behavior: None. It only declares the wire service contract.

Dependencies/integration: Used by `InterQJournalProtocolTranslatorPB`, server-side translator, and JournalNode RPC server setup.

Risks: Protocol name and version must remain compatible with clients. Kerberos principal choice must match inter-JournalNode authentication.

Test signals: RPC compatibility tests should verify `isMethodSupported`, protocol version negotiation, and secure client/server principal configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolPB.java -->
