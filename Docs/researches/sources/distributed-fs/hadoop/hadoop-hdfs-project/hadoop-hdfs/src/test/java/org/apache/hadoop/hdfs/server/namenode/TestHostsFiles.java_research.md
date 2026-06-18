# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestHostsFiles.java

**Purpose:** Parameterized tests for NameNode include/exclude host-file handling through both `HostFileManager` and `CombinedHostFileManager`.

**Important APIs and flow:** The class is a JUnit parameterized class over host file manager implementation. `getConf()` creates an `HdfsConfiguration` with fast heartbeats, redundancy, pending-reconstruction, and block-report intervals; rack awareness enabled through a topology script key; and `DFS_NAMENODE_HOSTS_PROVIDER_CLASSNAME_KEY` set to the current manager class. `HostsFileWriter` writes include/exclude files for refresh.

**Control flow:** `testHostsExcludeInUI()` creates a four-DataNode, two-rack cluster, writes a replicated file, excludes a DataNode holding a replica, calls `refreshNodes()`, waits for decommission and replication, then checks the `NameNodeInfo` JMX `LiveNodes` JSON contains `Decommissioned`. `testHostsIncludeForDeadCount()` starts zero DataNodes with two include entries and asserts NameNode and JMX dead/live counts. `testNewHostAndExcludeFile()` starts with two included dead hosts, then refreshes with a new hosts file containing a third host and verifies dead count increases.

**State and persistence behavior:** State lives in host include/exclude files, DataNode admin state, NameNode live/dead/decommission counters, block placement, and JMX attributes. No restart is tested; behavior is driven by `refreshNodes()`.

**Dependencies and integration points:** Integrates `HostsFileWriter`, `DatanodeManager.refreshNodes()`, host config manager implementations, block replication, decommission state, rack-aware placement, `FSNamesystem` counters, and NameNode JMX MBeans.

**Risks and test signals:** Tests are timing-sensitive around decommission and replication. Passing for both managers signals host-file parsing and refresh semantics are consistent, decommission appears in UI/JMX, and configured-but-absent hosts count as dead.
