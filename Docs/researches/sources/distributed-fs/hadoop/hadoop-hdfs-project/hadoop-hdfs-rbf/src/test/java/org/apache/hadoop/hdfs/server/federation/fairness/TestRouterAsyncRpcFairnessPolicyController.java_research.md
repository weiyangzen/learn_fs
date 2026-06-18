# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterAsyncRpcFairnessPolicyController.java

## Purpose
This test verifies `RouterAsyncRpcFairnessPolicyController`, the fairness controller for async RPC call permits. It focuses on per-nameservice async permit limits and the special behavior of the concurrent namespace.

## Important APIs, Types, and Functions
The tests use `DFS_ROUTER_ASYNC_RPC_MAX_ASYNCCALL_PERMIT_KEY`, `DFS_ROUTER_ASYNC_RPC_MAX_ASYNC_CALL_PERMIT_DEFAULT`, `DFS_ROUTER_FAIRNESS_ACQUIRE_TIMEOUT`, `DFS_ROUTER_MONITOR_NAMENODE`, `FederationUtil.newFairnessPolicyController()`, `getAvailableHandlerOnPerNs()`, `acquirePermit()`, and `releasePermit()`.

## Control Flow
`createConf()` installs `RouterAsyncRpcFairnessPolicyController` and sets the per-namespace async permit count. The main allocation test consumes 30 permits for `ns1` and `ns2`, while `CONCURRENT_NS` is not bounded by those permits and continues to acquire successfully. Timeout and invalid-permit tests check that exhausted namespaces wait at least the configured interval and that zero or negative config falls back to the default with an initialization log message.

## State and Persistence
Only in-memory controller permit state is exercised. There is no router process or persistent state-store interaction.

## Dependencies and Integration Points
The test depends on Hadoop configuration, `GenericTestUtils.LogCapturer`, SLF4J logger capture, and the fairness controller factory. It integrates with metrics/JMX indirectly through `getAvailableHandlerOnPerNs()` JSON formatting expectations.

## Risks and Test Signals
String equality on JSON-like maps is order-sensitive and can catch intentional formatting or ordering changes. Timeout checks are scheduler-sensitive but use a lower-bound assertion. Passing tests signal bounded async per-namespace permits, unbounded concurrent namespace handling, fallback defaults, log messages, and availability reporting.
