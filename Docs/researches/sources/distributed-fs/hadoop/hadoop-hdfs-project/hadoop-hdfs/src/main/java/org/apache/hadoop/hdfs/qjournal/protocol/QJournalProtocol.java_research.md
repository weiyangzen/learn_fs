<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/QJournalProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/QJournalProtocol.java

Purpose: NameNode-to-JournalNode RPC contract for quorum edit logging, recovery, reading, and storage lifecycle operations.

Important APIs/types/functions: Formatting/state calls (`isFormatted`, `getJournalState`, `format`, `newEpoch`), write calls (`journal`, `heartbeat`, `startLogSegment`, `finalizeLogSegment`, `purgeLogsOlderThan`), read calls (`getEditLogManifest`, `getJournaledEdits`), recovery calls (`prepareRecovery`, `acceptRecovery`), and upgrade/rollback/discard/ctime operations.

Control flow: Active NameNode obtains state, proposes a new epoch, recovers unfinalized segments, starts segments, journals batches with `RequestInfo`, finalizes segments, and may purge old logs. Standby/readers fetch manifests or RPC-cached edits. Recovery uses prepare/accept to converge a quorum on one segment length.

State and persistence behavior: Methods mutate or expose JournalNode storage: namespace format data, edit log files, in-progress/finalized segment names, persisted promised/writer epochs, committed txid, and Paxos recovery records.

Dependencies/integration: Consumed by `IPCLoggerChannel` through `QJournalProtocolTranslatorPB`; implemented by JournalNode RPC server delegation into `Journal`. Security annotations use JournalNode server principal and NameNode client principal.

Risks: Correctness relies on `RequestInfo` epoch and serial enforcement on the server. `getJournaledEdits` requires the in-memory JournalNode cache and can fail on cache misses, so callers need streaming fallback. Some admin operations require all JournalNodes, unlike quorum writes.

Test signals: Protocol tests should cover all translator conversions, optional nameservice ids, idempotent `discardSegments`, recovery handshakes, namespace consistency checks, cache-miss handling, and old-client layout-version defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/QJournalProtocol.java -->
