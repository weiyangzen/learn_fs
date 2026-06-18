# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncProtocolTestBase.java

Purpose: shared fixture for async Router protocol module tests. It creates a small HA federated cluster and supplies both the normal `RouterRpcServer` and a Mockito-spied async variant backed by `RouterAsyncRpcClient`.

Important APIs/types/functions: `MiniRouterDFSCluster`, `RouterConfigBuilder`, `RouterRpcServer`, `RouterAsyncRpcClient`, `MockResolver`, `CallerContext`, `FsPermission`, and async config keys `DFS_ROUTER_ASYNC_RPC_HANDLER_COUNT_KEY` and `DFS_ROUTER_ASYNC_RPC_RESPONDER_COUNT_KEY`. Static getters expose router configuration, cluster, and nameservice id; instance getters expose router context, filesystem, and RPC servers.

Control flow: `setUpCluster()` starts one nameservice with two HA NNs and three DNs, makes `nn0` active, enables router RPC, constrains client/async handler/responder threads to one, reduces DN report cache expiry, starts routers, registers NNs, and waits for active namespaces. `setUp()` obtains a router, initializes async thread pools, creates an async client, spies the RPC server so `getRPCClient()` returns the async client and `isAsync()` returns true, maps `/` to the active namespace, and creates `/testdir`. `tearDown()` clears `CallerContext`, deletes `/testdir`, and closes the router FS.

State and persistence behavior: tests inherit filesystem state under `/testdir`, resolver mappings, thread pools, and async call context. Risks include static cluster sharing, single-thread timing sensitivity, and async thread-pool cleanup. Test signal is mostly indirect: subclasses depend on the fixture to produce comparable sync/async protocol behavior.
