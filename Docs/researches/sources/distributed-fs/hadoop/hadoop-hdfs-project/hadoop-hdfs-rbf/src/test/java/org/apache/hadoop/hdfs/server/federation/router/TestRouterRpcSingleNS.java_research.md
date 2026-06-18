## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterRpcSingleNS.java

Purpose: compact single-nameservice coverage for Router RPC forwarding, especially edit-log and namespace-save operations. It parallels part of `TestRouterRpc` but runs with one nameservice and two datanodes.

Important APIs and types include `MiniRouterDFSCluster`, `RouterConfigBuilder`, `ClientProtocol`, `NamenodeProtocol`, `NameNodeProxies`, `FileSystem`, `SafeModeAction`, and federation test helpers for file creation and existence. The class maintains Router and NameNode protocol/filesystem handles, nameservice ID, and per-test Router/NameNode file paths.

Control flow: `globalSetUp()` starts one nameservice with two datanodes, starts Routers with metrics and RPC services, sets short datanode report cache expiry, registers NameNodes, and waits for registration. `testSetup()` installs mock locations, clears files, creates NameNode test directories, selects a Router and the only nameservice, creates a test file directly on the NameNode, and verifies it. `setRouter()` and `setNamenode()` initialize client and namenode protocol proxies. Tests assert `rollEdits()` returns the same transaction ID later reported by `getCurrentEditLogTxid()`, and that `saveNamespace()` succeeds after entering safemode, then leaves safemode.

State and persistence behavior is MiniDFS namespace state: edit-log rolling, safemode state, and saved namespace operation. There is no state-store or mount-table mutation beyond mock locations.

Dependencies and integration points are Router RPC forwarding to a single NameNode, NameNode protocol proxy creation through Router URI, HDFS safemode, and filesystem fixture setup. Risks covered include single-namespace Router code paths diverging from multi-namespace logic, transaction ID forwarding errors, and namespace save not propagating through Router. Test signals are transaction ID equality and boolean success from `saveNamespace`.
