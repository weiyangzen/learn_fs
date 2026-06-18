# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestProportionRouterRpcFairnessPolicyController.java

## Purpose
This JUnit 5 test validates `ProportionRouterRpcFairnessPolicyController`, which allocates router RPC permits per nameservice by configured or default proportions of the total handler count.

## Important APIs, Types, and Functions
Tests call `FederationUtil.newFairnessPolicyController(conf)`, then exercise the `RouterRpcFairnessPolicyController` API: `acquirePermit(ns)`, `releasePermit(ns)`, and timeout behavior. Config inputs include `DFS_ROUTER_HANDLER_COUNT_KEY`, `DFS_ROUTER_MONITOR_NAMENODE`, `DFS_ROUTER_FAIRNESS_ACQUIRE_TIMEOUT`, and `DFS_ROUTER_FAIR_HANDLER_PROPORTION_KEY_PREFIX`.

## Control Flow
`createConf()` installs the proportional controller class and a monitored NameNode list containing `ns1` and `ns2`. Tests assert default 10% allocation, a custom `ns1=0.5` allocation, acquire timeout duration after all permits are consumed, minimum one permit for zero proportion, support for configured totals greater than router handler count, and transparent expansion for unregistered namespaces that receive default permits.

## State and Persistence
State is confined to controller semaphore/permit state inside each test-created controller. No cluster, state store, or persistent records are used.

## Dependencies and Integration Points
The test depends on `HdfsConfiguration`, router fairness config keys, `RouterRpcFairnessConstants.CONCURRENT_NS`, and `Time.monotonicNow()` for timeout assertions. It integrates indirectly with production controller construction through `FederationUtil`.

## Risks and Test Signals
The timeout assertions depend on wall-clock scheduling and only check lower bounds. The proportional controller intentionally allows aggregate namespace permits to exceed total handlers, so regressions would show as unexpected failures in overcommit and unregistered namespace cases. Passing tests signal correct default proportioning, configured override parsing, release semantics, and cluster expansion friendliness.
