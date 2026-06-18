<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JNStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JNStorage.java

Purpose: JournalNode-specific `Storage` wrapper around a single journal directory and `FileJournalManager`.

Important APIs/types/functions: Constructor analyzes/recovers storage. Key methods include `format`, `analyzeStorage`, `refreshStorage`, `checkConsistentNamespace`, `findFinalizedEditsFile`, edit-file path builders, Paxos path builders, `purgeDataOlderThan`, `getOrCreatePaxosDir`, upgrade-related storage overrides, `isFormatted`, and `close`.

Control flow: Startup creates a `StorageDirectory`, `FileJournalManager`, and analyzes state. Format clears the directory, writes namespace properties, creates `paxos`, and re-analyzes. Purge removes old edit logs through FJM and old numeric Paxos decision files. Recovery startup delegates abnormal storage states to `StorageDirectory.doRecover`.

State and persistence behavior: Persists VERSION/properties, finalized and in-progress edit files under `current`, Paxos recovery decisions under `current/paxos`, sync temporary files, and journal-sync staging under `edits.sync`. Layout version checks are relaxed because JournalNodes mostly scan edit files rather than decode all future layouts.

Dependencies/integration: Owned by `Journal`; uses HDFS `Storage`, `NNStorage` edit-file naming, `FileJournalManager`, and configured journal directory permissions.

Risks: `getOrCreatePaxosDir` logs but does not throw if `mkdir` fails, so later file creation reveals the error. Purge deletes numeric Paxos files by txid and assumes no unrelated numeric files live there. Layout version relaxation must stay compatible with edit-log scanning behavior.

Test signals: Cover format/force semantics, namespace consistency failures, path generation, paxos purge, startup recovery states, rollback/upgrade storage refresh, directory permission creation, and missing finalized-file errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JNStorage.java -->
