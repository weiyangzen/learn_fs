<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/InterQJournalProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/InterQJournalProtocol.java

Purpose: Defines JournalNode-to-JournalNode RPCs used by the optional journal syncer to discover and synchronize edit logs between peers.

Important APIs/types/functions: `getEditLogManifestFromJournal(jid, nameServiceId, sinceTxId, inProgressOk)` and `getStorageInfo(jid, nameServiceId)`. The interface has qjournal-specific Kerberos annotations and version id `1L`.

Control flow: A JournalNode sync client asks a peer for its manifest or storage identity; server implementations delegate into the same journal state used for NameNode-facing manifests.

State and persistence behavior: No state in the interface. Responses expose persisted edit-log manifests and storage metadata for a named journal.

Dependencies/integration: Implemented over protobuf by `InterQJournalProtocolPB` translators and served by JournalNode RPC plumbing. Uses JournalNode Kerberos principal for both client and server because both ends are JournalNodes.

Risks: Manifest correctness depends on peer storage consistency and nameservice selection. In-progress inclusion must be handled carefully so syncers do not copy unstable data incorrectly.

Test signals: Inter-JN RPC tests should verify manifest filtering by txid, storage info conversion, optional nameservice id handling, Kerberos annotation expectations, and behavior against unformatted or missing journals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/InterQJournalProtocol.java -->
