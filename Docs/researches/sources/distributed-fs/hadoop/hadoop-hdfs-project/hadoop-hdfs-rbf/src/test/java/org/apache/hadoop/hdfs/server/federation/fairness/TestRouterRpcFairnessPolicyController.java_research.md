# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterRpcFairnessPolicyController.java

## Purpose
This unit test validates `StaticRouterRpcFairnessPolicyController`, which allocates a fixed number of router handler permits across monitored nameservices and the concurrent-operation namespace.

## Important APIs, Types, and Functions
It constructs controllers through `FederationUtil.newFairnessPolicyController()`, uses `DFS_ROUTER_HANDLER_COUNT_KEY`, `DFS_ROUTER_MONITOR_NAMENODE`, `DFS_ROUTER_FAIR_HANDLER_COUNT_KEY_PREFIX`, and `DFS_ROUTER_FAIRNESS_ACQUIRE_TIMEOUT`, and asserts `acquirePermit()`, `releasePermit()`, and `getAvailableHandlerOnPerNs()` behavior.

## Control Flow
Default tests divide 30 handlers equally among `ns1`, `ns2`, and `concurrent`; 31 handlers allocate the extra permit to concurrent. Preconfigured handler tests reserve `ns1=30` and split remaining handlers. Error tests verify insufficient total handlers or low preconfigured counts log `StaticRouterRpcFairnessPolicyController.ERROR_MSG`. Timeout tests exhaust `ns1` and assert a failed acquire waits at least 100 ms. Availability tests check JSON-like reporting before and after one acquire.

## State and Persistence
Controller state is in-memory semaphores per namespace. No router cluster or state store is started.

## Dependencies and Integration Points
The test depends on `HdfsConfiguration`, the controller factory, SLF4J log capture, and `RouterRpcFairnessConstants.CONCURRENT_NS`. It is a fast validation layer below the router integration tests.

## Risks and Test Signals
JSON string assertions are sensitive to map ordering. Error tests catch logs after swallowing expected construction exceptions, so they validate operator-facing diagnostics as well as validation behavior. Passing tests signal correct static allocation, leftover handling, configured overrides, timeout waits, release semantics, and no-fairness fallback reporting as `N/A`.
