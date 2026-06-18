# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRespectsBindHostKeys.java

Purpose: Confirms NameNode RPC, service RPC, lifeline RPC, HTTP, and HTTPS listeners honor explicit bind-host configuration keys and do not bind wildcard addresses by default in the tested cases.

Important APIs and functions: Helper methods read listener addresses from `NameNodeRpcServer.getClientRpcServer`, `getServiceRpcServer`, and `getLifelineRpcServer`, plus `NameNode.getHttpAddress` and `getHttpsAddress`. `setupSsl` creates SSL test keystores using `KeyStoreTestUtil`.

Control flow: Each bind-host test starts one cluster without the bind-host key and checks the listener is not `0.0.0.0`, shuts down, sets the corresponding bind key to `0.0.0.0`, starts another cluster, and asserts the listener uses the wildcard. Service and lifeline tests first set their advertised addresses to `127.0.0.1:0`. HTTPS configures test SSL resources and `HTTPS_ONLY` policy before repeating the same pattern.

State and persistence behavior: State is startup-time listener binding and temporary SSL keystore files under a test directory. There is no NameNode namespace persistence under test. HTTPS cleanup removes generated SSL configuration.

Dependencies and integration points: Uses `MiniDFSCluster`, `HdfsConfiguration`, DFS bind host/address keys, Hadoop HTTP policy, `KeyStoreTestUtil`, and AssertJ/JUnit assertions. It tests configuration integration between NameNode startup and IPC/HTTP server socket creation.

Risks: Tests are sensitive to address string formatting such as leading slashes from `InetAddress.toString`. HTTPS setup shares static `keystoresDir` and `sslConfDir`. Port binding behavior can vary if local networking rules restrict wildcard binding.

Test signals: Correct signals are non-wildcard listener addresses without bind keys, exact wildcard listener addresses with bind keys, and successful SSL cluster startup and cleanup for HTTPS.
