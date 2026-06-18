# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNode.java

Purpose: Tests `JournalNode` daemon behavior, including storage directory selection, RPC/HTTP services, metrics, Paxos acceptor behavior, startup failure handling, syncer startup configuration, federation, and handler counts.

Important APIs/types/functions: `JournalNode`, `JournalNodeRpcServer`, `IPCLoggerChannel`, `JNStorage`, `MetricsAsserts`, `getOrCreateJournal`, `getJournalSyncerStatus`, `getHttpServerURI`, `prepareRecovery`, `acceptRecovery`, and `DFS_JOURNALNODE_*` keys.

Control flow: Setup tailors configuration by test method, starts a JournalNode, creates/formats journals, and opens an IPC channel. Tests verify nameservice/common/default edit dirs, metric tags/counters, journal writes and lag gauges, epoch transition segment info, HTTP `/jmx` and `/getJournal`, Paxos prepare/accept persistence and rejection, invalid dir startup failure, clean stop on bind failure, syncer gating under disabled/bad/federated configs, and handler count fallback.

State and persistence behavior: Formatted journal directories, metrics, Paxos accepted recovery state, and finalized edit bytes served over HTTP are validated.

Dependencies and integration points: JournalNode lifecycle, RPC server, HTTP server, metrics, federation config, static host resolution, QJM IPC client, and syncer selection.

Risks: Misconfiguration can place edits under wrong namespace, leak services, expose bad HTTP data, or start syncers against the wrong URI.

Test signals: Passing validates daemon startup, storage layout, metrics, HTTP serving, Paxos acceptor semantics, config validation, syncer gating, and handler counts.
