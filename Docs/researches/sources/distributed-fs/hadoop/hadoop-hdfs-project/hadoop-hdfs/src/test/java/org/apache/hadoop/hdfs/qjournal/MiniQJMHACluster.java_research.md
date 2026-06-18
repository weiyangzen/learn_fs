<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/MiniQJMHACluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/MiniQJMHACluster.java

Purpose: Test utility that composes a `MiniJournalCluster` with an HA `MiniDFSCluster` using QJM shared edits.

Important APIs/types/functions: `MiniQJMHACluster.Builder`, `createDefaultTopology`, `initHAConf`, `getDfsCluster`, `getJournalCluster`, and `shutdown`. Uses `MiniDFSNNTopology`, `NameNode.initializeSharedEdits`, `HATestUtil.setFailoverConfigurations`, and `ConfiguredFailoverProxyProvider`.

Control flow: Builder defaults to zero DataNodes and two NameNodes. Construction retries on `BindException`, selecting a random base port, starting three JournalNodes, setting their shared edits config, creating a NameNode topology, initializing HA configuration, starting MiniDFS once to format local namespace dirs, shutting down NameNodes, initializing shared edits, applying optional startup options, and restarting NameNodes.

State and persistence behavior: Persists JournalNode shared edits and MiniDFS NameNode storage under configured base directories. `forceRemoteEditsOnly` makes the QJM URI both edits dir and required edits dir.

Dependencies and integration points: Provides reusable HA/QJM integration setup for tests of failover, shared edits, and NameNode fencing.

Risks: Infinite retry loop on repeated bind conflicts has no explicit cap. Random port selection reduces but does not eliminate collisions. Shutdown assumes both cluster fields are initialized.

Test signals: A built instance with active NameNodes and active JournalNodes indicates HA configuration, shared edits initialization, and failover proxy settings are valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/MiniQJMHACluster.java -->
