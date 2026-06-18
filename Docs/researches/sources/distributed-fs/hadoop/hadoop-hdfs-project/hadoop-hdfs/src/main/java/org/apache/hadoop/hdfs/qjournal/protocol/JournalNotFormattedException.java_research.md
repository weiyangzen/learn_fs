<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/JournalNotFormattedException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/JournalNotFormattedException.java

Purpose: Signals that a JournalNode operation requiring formatted storage was invoked before the journal storage reached normal formatted state.

Important APIs/types/functions: Public constructor accepting a message; subclass of `IOException`.

Control flow: `Journal.checkFormatted` throws this for operations such as epoch negotiation, writes, manifests, and recovery when `JNStorage.isFormatted()` is false.

State and persistence behavior: No state beyond the message. It protects persistent storage from writes against uninitialized or unformatted directories.

Dependencies/integration: Propagates through `QJournalProtocol` translators as RPC failures and influences format/has-data flows in `QuorumJournalManager`.

Risks: Callers must distinguish this expected operational state from other IO failures. Message content includes local storage path and journal id, which is useful but should not be exposed beyond trusted admin channels.

Test signals: Tests should exercise unformatted journal responses for write, recovery, manifest, and state calls, and verify successful operations after format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/JournalNotFormattedException.java -->
