<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestDatanodeRestart.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestDatanodeRestart.java

Purpose: restart-focused DataNode tests for replica persistence and registration waits. It checks finalized replicas survive DataNode restarts, RBW replicas are recovered as RWR with correct length after restart, and client operations wait for DataNode registration state instead of failing immediately on missing saved registration.

Important APIs/types/functions: `MiniDFSCluster`, `DFSTestUtil`, `FSDataOutputStream`, `DataNodeTestUtils`, `FsDatasetImpl`, `ReplicaMap`, `ReplicaInfo`, `ReplicaState.RWR`, `DataNodeFaultInjector.noRegistration`, `testFinalizedReplicas`, `testRbwReplicas`, private `testRbwReplicas`, `dataset`, and `testWaitForRegistrationOnRestart`.

Control flow: `testFinalizedReplicas` starts three DataNodes, writes two files at replication 3, verifies contents and replication, restarts DataNodes, and checks file readability again. The RBW helper writes and `hflush`es an unclosed file, optionally truncates on-disk block files by one byte to simulate corruption, restarts DataNodes, and inspects the restarted DataNode `volumeMap`; the replica should become `RWR`, with corrupt length rounded down to checksum packet boundary. It invalidates the recovered replica afterward. `testWaitForRegistrationOnRestart` installs a fault injector whose `noRegistration` throws, creates a one-DataNode cluster, verifies write and read paths wait roughly the configured five-second BP-ready timeout, restores the injector to prove operations succeed, then repeats for `getReplicaVisibleLength` via append/open.

State and persistence behavior: finalized files persist across local volume restart. RBW disk state transitions to RWR in memory on restart, preserving or truncating byte length based on corruption. Registration state is intentionally unavailable through the fault injector, exercising timeout behavior rather than disk state.

Dependencies and integration points: uses NameNode/DataNode MiniDFSCluster lifecycle, DataNode local `rbw` directories, `ReplicaMap`, client socket timeout, BP-ready timeout, and HDFS append/read RPCs.

Risks: `testRbwReplicas` lacks `@Test` annotation in this file, so only direct framework discovery would miss it unless invoked elsewhere or intentionally disabled. Timing assertions allow 5-10 seconds and can be sensitive to slow test hosts.

Test signals: failures indicate replica state regression on restart, corrupt RBW length recovery mistakes, or DataNode RPCs bypassing registration wait semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestDatanodeRestart.java -->
