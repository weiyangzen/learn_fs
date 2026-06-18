# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterRefreshFairnessPolicyController.java

## Purpose
This integration test validates dynamic replacement of a router's fairness policy controller, including invalid class handling, concurrent refresh requests, and changed handler allocations after refresh.

## Important APIs, Types, and Functions
The test uses `RouterRpcClient.refreshFairnessPolicyController(Configuration)`, `getRouterRpcFairnessPolicyController()`, `StaticRouterRpcFairnessPolicyController`, `NoRouterRpcFairnessPolicyController`, `DFS_ROUTER_FAIRNESS_POLICY_CONTROLLER_CLASS`, `DFS_ROUTER_FAIR_HANDLER_COUNT_KEY_PREFIX`, `RemoteMethod`, and router RPC metrics for accepted/rejected permits.

## Control Flow
Each test starts a two-nameservice `StateStoreDFSCluster` with state store and RPC enabled, static fairness configured, nine handlers, and metrics enabled. Invalid refresh tests set nonexistent or non-implementing classes and expect the old static controller class name to be returned. Successful refresh switches from static to no-fairness. The concurrent test starts 100 threads that refresh the controller and counts shutdown log messages. The handler-change test blocks mocked remote invocations, refreshes configured ns0/ns1 permit counts, waits for old calls to finish, then issues new calls and checks accepted/rejected metrics reflect both old and new allocations.

## State and Persistence
State is in the running router's RPC client controller reference, active invocation threads, and metrics counters. The state store only backs cluster membership and mount resolution.

## Dependencies and Integration Points
The test integrates controller construction, shutdown, router RPC invocation, metrics, and subject-preserving threads. It uses Mockito to delay `RouterRpcClient.invokeMethod()` and `GenericTestUtils.LogCapturer` to inspect controller shutdown logs.

## Risks and Test Signals
The concurrent refresh count assumes every refresh creates and shuts down a controller; implementation changes may alter log count while remaining correct. Sleeps around mocked invocations can be timing-sensitive. Passing tests signal safe fallback on invalid classes, class-change success, no controller leaks during concurrent refresh, and immediate application of new per-namespace permit limits.
