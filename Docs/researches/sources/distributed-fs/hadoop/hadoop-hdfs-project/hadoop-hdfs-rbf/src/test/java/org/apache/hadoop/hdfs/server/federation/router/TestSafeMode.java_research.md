# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestSafeMode.java

Purpose: sanity-checks that router client protocol calls can proxy HDFS safe-mode operations to registered active namenodes in an HA federated cluster.

Important APIs/types/functions: `MiniRouterDFSCluster`, `RouterContext`, `ClientProtocol`, `SafeModeAction`, and `FederationTestUtils.NAMENODES`. `setup()` starts a two-nameservice HA cluster, starts routers, registers namenodes, installs mock locations, transitions `nn0` active and `nn1` standby for each namespace, and waits for active namespace visibility.

Control flow: `testProxySetSafemode()` obtains the router-facing `ClientProtocol` from a random router and calls `setSafeMode(SAFEMODE_GET, true)` and `setSafeMode(SAFEMODE_GET, false)`. Although the method name references set, `SAFEMODE_GET` exercises proxying of safe-mode query actions through the router.

State and persistence behavior: cluster routing state includes mock location mappings and namenode HA state, but the test does not mutate files or long-lived state. Teardown shuts down the entire mini cluster. Dependencies include router RPC startup, namenode registration, HA transitions, and client protocol forwarding. Risks are minimal beyond cluster startup flakiness; assertions are implicit because the test fails on thrown exceptions. Test signal is successful completion of both safe-mode proxy calls.
