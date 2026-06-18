<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolServerSideTranslatorPB.java

Purpose: Server-side protobuf adapter that converts `InterQJournalProtocolPB` requests into calls on an `InterQJournalProtocol` implementation.

Important APIs/types/functions: Constructor accepts the delegate. Implements `getEditLogManifestFromJournal` and `getStorageInfo`, translating journal id and optional nameservice id fields and wrapping `IOException` in `ServiceException`.

Control flow: Each RPC method extracts protobuf fields, calls the Java protocol delegate, and returns the delegate's protobuf response or storage info proto directly.

State and persistence behavior: No owned state beyond the delegate reference. Persistent effects are whatever the delegate's JournalNode implementation performs or exposes.

Dependencies/integration: Used by JournalNode RPC server for syncer APIs; shares `GetEditLogManifestRequestProto` with the main qjournal protocol.

Risks: Optional nameservice ids become null when absent, so delegate behavior must consistently select storage directories. All IO failures cross the RPC boundary as `ServiceException`.

Test signals: Verify request field conversion, absent nameservice handling, exception wrapping, and delegate invocation for manifest and storage info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolServerSideTranslatorPB.java -->
