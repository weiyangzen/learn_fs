# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestAsyncRouterAdmin.java

Purpose: async-enabled version of `TestRouterAdmin`, proving admin mount checks and inherited router-admin behavior work when async RPC is enabled.

Important APIs/types/functions: extends `TestRouterAdmin`; uses `StateStoreDFSCluster`, `RouterConfigBuilder`, `ActiveNamenodeResolver`, `RouterRpcServer`, `RemoteMethod`, `RemoteLocation`, `HdfsFileStatus`, `AsyncUtil`, Mockito spies, and reflection via inherited `setField`. Config enables state store, admin, RPC, mount-checking, and `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`.

Control flow: `globalSetUp()` starts a one-nameservice state-store cluster with async RPC and admin mount checks. It registers synthetic active `ns0` and `ns1` namenode reports, refreshes state-store caches, and calls `setUpMocks()`. `setUpMocks()` replaces the router RPC server with a spy, stubs `getFileInfo`, replaces the RPC client with a spy, and prepares mocked async responses for destination checks against remote locations.

State and persistence behavior: the test mutates router internals through reflection and state-store/membership records; inherited admin tests operate on the static fields initialized here. Integration points include mount-table admin validation, async client response handling, namenode membership, and state-store cache refresh. Risks include tight coupling to private field names and inherited tests relying on static state. Test signals are inherited from `TestRouterAdmin`, with this class specifically ensuring they execute under async RPC.
