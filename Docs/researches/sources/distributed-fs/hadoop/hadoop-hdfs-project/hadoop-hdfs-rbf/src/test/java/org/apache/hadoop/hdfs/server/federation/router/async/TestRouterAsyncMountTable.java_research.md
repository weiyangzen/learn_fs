# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncMountTable.java

Purpose: runs the standard mount-table router tests with async RPC enabled.

Important APIs/types/functions: extends `TestRouterMountTable`; uses `StateStoreDFSCluster`, `RouterConfigBuilder`, `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`, and inherited mount-table admin/client helpers. Static inherited fields such as `cluster`, `routerContext`, `stateStore`, and test mount table state are initialized by the subclass.

Control flow: `globalSetUp()` creates a state-store-backed Router cluster with admin/RPC services and async RPC enabled, starts routers, obtains a router context, generates a mock mount table, and initializes inherited state-store references. The actual test methods are inherited from `TestRouterMountTable`, so this class functions as a configuration specialization rather than adding new assertions.

State and persistence behavior: inherited tests persist mount-table records in the router state store and exercise router cache reloads. Integration points include admin RPC, mount-table manager, state-store cache, and router client path resolution under async RPC. Risks are inherited static state coupling and missed async-specific assertions beyond successful inherited behavior. Test signals are the inherited suite’s mount-table add/remove/list/cache/path-resolution assertions executed with async RPC enabled.
