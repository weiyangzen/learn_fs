<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestMiniJournalCluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestMiniJournalCluster.java

Purpose: Tests `MiniJournalCluster` startup, quorum URI generation, storage directory configuration, and fixed port validation/binding.

Important APIs/types/functions: `MiniJournalCluster.Builder`, `waitActive`, `getQuorumJournalURI`, `getJournalNode`, `setHttpPorts`, `setRpcPorts`, `NetUtils.getFreeSocketPorts`, and `LambdaTestUtils.intercept`.

Control flow: `testStartStop` starts a default three-node cluster, waits for activity, verifies quorum URI has three authorities, and checks node 0 edits dir under MiniDFS base directory. `testStartStopWithPorts` first asserts mismatched port-array sizes throw expected `IllegalArgumentException`s, then allocates six free ports, starts a cluster with three fixed HTTP and three fixed RPC ports, verifies bound ports match, and rechecks storage dir configuration.

State and persistence behavior: Creates JournalNode directories under MiniDFS base directory and starts real JournalNode RPC/HTTP services. Try-with-resources or finally shutdown stops services.

Dependencies and integration points: Validates the QJM fixture used by NameNode/QJM tests and the port-selection helper used for deterministic network bindings.

Risks: Free ports can be stolen between discovery and binding. The assertion message "should not be zero" has a double negative but checks the right value.

Test signals: Passing means default and fixed-port mini journal clusters start, become IPC-active, expose expected ports, and validate builder arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestMiniJournalCluster.java -->
