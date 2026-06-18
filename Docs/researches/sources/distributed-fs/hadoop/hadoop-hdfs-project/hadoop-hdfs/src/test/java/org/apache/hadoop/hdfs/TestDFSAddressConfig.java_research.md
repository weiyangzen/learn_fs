<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSAddressConfig.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSAddressConfig.java

Purpose: Tests MiniDFSCluster DataNode address configuration behavior for default localhost binding and explicit `dfs.datanode.*.address` settings.

Important APIs, types, and functions: `DFS_DATANODE_ADDRESS_KEY`, `DFS_DATANODE_HTTP_ADDRESS_KEY`, `DFS_DATANODE_IPC_ADDRESS_KEY`, `MiniDFSCluster.startDataNodes`, `stopDataNode`, `DataNode.getXferAddress`, `DataNodeProperties`, and `StartupOption.REGULAR`.

Control flow: The test starts a default cluster and asserts the DataNode transfer address contains `127.0.0.1`. It stops the DataNode, unsets all DataNode address config keys, restarts DataNodes with the option to check configuration, and again expects localhost. It then stops the DataNode, sets transfer/http/ipc addresses to `0.0.0.0:0`, restarts, and expects the transfer address to contain `0.0.0.0`.

State and persistence behavior: DataNode processes are stopped and restarted inside one MiniDFSCluster, while the mutable `Configuration` controls bind address selection. No NameNode metadata persistence is involved.

Dependencies and integration points: Exercises MiniDFSCluster's DataNode startup API, configuration key handling, DataNode socket binding/reporting, and restart lifecycle.

Risks: Assertions inspect string forms of socket addresses, which can vary with Java/network stack formatting. The test does not use try/finally around the final cluster shutdown, so an earlier assertion failure could leave cleanup to the test harness.

Test signals: Success means MiniDFSCluster defaults to loopback when DataNode address keys are absent and honors explicit wildcard bind addresses when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSAddressConfig.java -->
