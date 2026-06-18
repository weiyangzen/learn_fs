# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcWhenNamenodeFailover.java

Purpose: regression test for async router behavior when a nameservice transitions out of active service after prior successful operations.

Important APIs/types/functions: `StateStoreDFSCluster`, `RouterConfigBuilder`, `DFSClient`, `DirectoryListing`, `HdfsFileStatus`, `FederationTestUtils.transitionClusterNSToActive`, `transitionClusterNSToStandby`, and `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`.

Control flow: `setupCluster(true)` starts an HA state-store cluster with metrics/admin/RPC/heartbeat and async RPC enabled. The test builds a router `DFSClient` for `hdfs://fed`, limits retry attempts, transitions namespace 0 active, creates `/ARR/testGetFileInfo`, confirms listing `/ARR` returns one child, transitions the cluster nameservices to standby, then asserts a subsequent `getFileInfo` for a non-existing path variant throws `IOException`.

State and persistence behavior: namespace HA state and router membership heartbeat state are central; filesystem path `/ARR/testGetFileInfo` is created before failover. The class keeps `cluster` as an instance field but does not show explicit teardown, so shutdown responsibility may rely on test framework or external cleanup in the larger suite. Integration points include router async RPC, DFS client retry/failover, heartbeat-discovered HA state, and client protocol error handling. Risks are resource leakage and timing between HA transition and router cache update. Test signal is an expected `IOException` instead of stale success or hang after failover.
