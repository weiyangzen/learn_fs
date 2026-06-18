<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNode.java

Purpose: Daemon wrapper that hosts qjournal RPC/HTTP servers and manages multiple per-journal `Journal` instances in one JVM.

Important APIs/types/functions: `setConf`, `start`, `stop`, `join`, `getOrCreateJournal`, `startSyncer`, `getLogDir`, MXBean methods, upgrade/rollback/discard/ctime delegators, HTTP/RPC address accessors, and `main`.

Control flow: Configuration resolves local journal directories, including nameservice-specific paths. Startup validates directories, initializes metrics and security login, registers MXBean, starts HTTP server, then RPC server. `getOrCreateJournal` validates journal id, constructs `Journal` lazily, and starts optional `JournalNodeSyncer`. Stop shuts down syncers, RPC, HTTP, journals, metrics, MXBean, and tracer.

State and persistence behavior: Runtime maps track journals and syncers by journal id. Persistent state belongs to each `Journal` directory under configured edits dirs. MXBean status infers formatted journals from loaded journals and on-disk directories.

Dependencies/integration: Implements `Tool`, `Configurable`, and `JournalNodeMXBean`; integrates with `JournalNodeRpcServer`, `JournalNodeHttpServer`, security, metrics, tracing, disk checks, and DFS config keys.

Risks: Federated nameservice directory resolution is configuration-sensitive. MXBean may mark any directory under a journal dir as formatted even if not analyzed. ErrorReporter stops the daemon on storage file errors. Lazy journal creation means first RPC can trigger storage analysis and syncer startup.

Test signals: Tests should cover startup/shutdown, absolute directory validation, HA/federated directory selection, lazy journal creation, syncer enablement and retry flags, MXBean JSON/status, security login address, error reporter stop, and upgrade delegator paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNode.java -->
