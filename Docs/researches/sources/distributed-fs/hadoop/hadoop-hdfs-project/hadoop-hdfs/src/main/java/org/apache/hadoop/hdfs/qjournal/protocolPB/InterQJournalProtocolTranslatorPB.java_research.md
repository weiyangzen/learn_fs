<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolTranslatorPB.java

Purpose: Client-side adapter that implements `InterQJournalProtocol` by building protobuf requests and invoking an `InterQJournalProtocolPB` proxy.

Important APIs/types/functions: `getEditLogManifestFromJournal`, `getStorageInfo`, `close`, `isMethodSupported`, and private `convertJournalId`.

Control flow: Methods build request protos, conditionally set `nameServiceId`, call the RPC proxy through shaded protobuf `ipc`, and return protobuf responses. `close` stops the proxy.

State and persistence behavior: Holds only the RPC proxy. It reads peer JournalNode state; no local persistence.

Dependencies/integration: Used by JournalNode syncer clients; integrates with Hadoop `RPC`, `RpcClientUtil`, and protobuf helper error translation.

Risks: Request construction must remain in sync with server optional-field names. Failure to close leaks RPC proxy resources.

Test signals: Verify protobuf construction, null nameservice omission, close behavior, method support probing, and IOException translation from `ServiceException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocolPB/InterQJournalProtocolTranslatorPB.java -->
