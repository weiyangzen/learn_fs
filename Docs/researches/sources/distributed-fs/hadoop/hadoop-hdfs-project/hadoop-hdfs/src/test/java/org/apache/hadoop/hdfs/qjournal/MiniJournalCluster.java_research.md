<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/MiniJournalCluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/MiniJournalCluster.java

Purpose: Test utility that starts and manages an in-process quorum of HDFS JournalNodes.

Important APIs/types/functions: `MiniJournalCluster.Builder`, `JNInfo`, `getQuorumJournalURI`, `start`, `shutdown`, `restartJournalNode`, `waitActive`, `setNamenodeSharedEditsConf`, and storage directory helpers. Uses `JournalNode`, `QuorumJournalManager`, `DFSConfigKeys`, and `DefaultMetricsSystem.setMiniClusterMode`.

Control flow: Builder validates optional fixed HTTP/RPC port arrays, resolves a base directory, optionally deletes per-node storage directories, creates each `JournalNode` with node-specific edits dir and ports, starts it, and records bound IPC/HTTP addresses. `waitActive` repeatedly creates a `QuorumJournalManager` against each node's config and calls `hasSomeData` until IPC responds. Restart stops a selected node, reuses bound addresses, and starts a new `JournalNode`.

State and persistence behavior: Persists JournalNode edits directories under `journalnode-N`, plus per-journal `current` and `previous` subdirectories. `format(true)` deletes existing node storage at construction. Shutdown stops nodes but does not delete storage.

Dependencies and integration points: Shared fixture for QJM tests and HA clusters, bridging NameNode shared edits config with JournalNode quorum URIs.

Risks: `start` can be called after constructor-started nodes and may double-start if callers misuse it. Fixed port arrays can conflict. `shutdown` aggregates failures and throws after attempting all stops.

Test signals: Consumers treat successful `waitActive`, correct quorum URI authority, restart success, and file existence in quorum storage as health signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/MiniJournalCluster.java -->
