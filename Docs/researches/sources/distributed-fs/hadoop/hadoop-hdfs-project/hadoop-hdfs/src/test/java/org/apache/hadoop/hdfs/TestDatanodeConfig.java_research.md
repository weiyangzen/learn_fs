# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeConfig.java

Purpose: validates DataNode startup behavior for configured storage directory URI schemes, locked-memory limits, and consistency of bound IPC/HTTP addresses written back to configuration.

Important APIs and types: `DataNode.createDataNode`, `MiniDFSCluster`, `StartupOption.REGULAR`, `NativeIO.POSIX.getCacheManipulator`, `DFS_DATANODE_DATA_DIR_KEY`, `DFS_DATANODE_MAX_LOCKED_MEMORY_KEY`, and AssertJ assertions.

Control flow: class setup clears the cluster base dir and starts a zero-DN NameNode with ephemeral DN ports. `testDataDirectories` verifies unsupported URI schemes fail and file URI/path forms succeed. `testMemlockLimit` assumes native IO and finite memlock limit, then starts a DN at the limit and expects failure above it. `testDataNodeIpcAndHttpSeverConf` starts a DN and compares live listener/HTTP addresses to DN config values.

State and persistence: deletes and recreates MiniDFSCluster base dirs, configures datanode data directories, starts/shuts down individual DataNode instances, and mutates config values.

Dependencies and integration: covers DataNode storage path validation, native OS resource limits, address binding on ephemeral ports, and config normalization during startup.

Risks: native memlock test is platform-dependent and skipped when assumptions fail; base directory cleanup is destructive within the test root; URI parsing must match `Util.fileAsURI` behavior.

Test signals: null DN after unsupported scheme failure, cluster DN up for accepted directories, expected memlock-limit exception text, and exact IPC/HTTP host:port equality with DN configuration.
