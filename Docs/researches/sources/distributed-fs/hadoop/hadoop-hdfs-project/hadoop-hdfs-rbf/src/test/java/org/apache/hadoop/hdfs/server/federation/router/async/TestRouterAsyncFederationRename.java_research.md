# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncFederationRename.java

Purpose: async variant of federation rename tests, verifying router rename semantics across namespaces when async RPC is enabled.

Important APIs/types/functions: extends `TestRouterFederationRename`; uses `StateStoreDFSCluster`, `RouterConfigBuilder`, and `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`. The class reuses inherited cluster fields, setup helpers, and rename assertions while changing the router configuration to async RPC.

Control flow: `globalSetUp()` builds a state-store cluster with router RPC/admin/state-store behavior and async RPC enabled. Inherited per-test setup installs mount entries and creates source/destination filesystem state. The overridden async tests run the same rename cases as the synchronous superclass, including cases where rename crosses federation boundaries and must coordinate physical namespace operations.

State and persistence behavior: state-store mount entries and physical HDFS paths are the key state; inherited teardown clears the test environment. Integration points include mount resolution, router client protocol rename implementation, async invocation of underlying namenodes, and failure cleanup across destinations. Risks are inherited-test coupling and subtle cross-namespace partial-rename failure modes. Test signals are inherited assertions about final source/destination existence, return values, and namespace placement under async execution.
