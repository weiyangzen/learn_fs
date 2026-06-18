<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemMBean.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemMBean.java

Purpose: `TestFSNamesystemMBean` validates NameNode/FSNamesystem JMX exposure, ensuring attributes are present, have expected types/values, and can be served even when the namesystem write lock or FSEditLog monitor is held by another thread. It also verifies edit-log sync metrics and reconstruction queue initialization progress.

Important APIs, types, and functions: it uses the platform `MBeanServer`, object names `Hadoop:service=NameNode,name=FSNamesystem`, `FSNamesystemState`, and `NameNodeInfo`, `NameNodeMXBean`, Jetty `JSON.parse`, `ConfigBuilder`/`TestMetricsConfig`, `SubjectInheritingThread`, `MiniDFSCluster`, `DFSTestUtil`, and `GenericTestUtils.waitFor`. `MBeanClient` iterates all attributes for the three MBeans and marks success if every `getAttribute` returns without exception.

Control flow: the basic test starts a cluster, reads `SnapshotStats`, parses it as JSON, and compares snapshot counters with `FSNamesystem`. It also asserts `PendingDeletionBlocks` is a `Long` and `NumEncryptionZones` is an `Integer`. Lock tests configure a short metrics cache period, start a cluster, hold either the FSNamesystem global write lock or synchronize on the edit log, wait for cache expiry, run `MBeanClient`, and assert JMX calls complete within 20 seconds. Metrics tests create directories to force edit-log syncs and read `TotalSyncCount`/`TotalSyncTimes`. Reconstruction progress creates a file, restarts the NameNode, waits until progress becomes `1.0`, and checks both direct API and MBean attribute.

State and persistence behavior: tests observe runtime MBean state derived from namespace counters, edit-log sync stats, and block reconstruction initialization. The reconstruction test crosses a NameNode restart, so it also checks post-restart metric progression after processing mis-replicated blocks.

Dependencies and integration points: depends on Hadoop metrics2 JMX registration, FSNamesystem direct MBean registration, NameNode edit-log metrics, reconstruction queue initialization, metrics cache configuration files, and lock-free/cache-safe JMX access patterns.

Risks and edge cases: swallowing exceptions in `MBeanClient` hides root cause, only exposing `succeeded=false`. JMX object names and attribute names are string contracts and brittle under metric renames. The lock tests rely on cache period and join timeout to detect deadlock risk. Writing the metrics config file can affect other metrics tests if not isolated by test filename handling.

Test signals: parsed `SnapshotStats` counters match namesystem APIs, type assertions for MBean attributes, successful full attribute sweep while locks are held, positive sync count with non-null sync times, and reconstruction progress reaching `1.0` after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemMBean.java -->
