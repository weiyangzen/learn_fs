# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterClientRejectOverload.java

## Purpose

`TestRouterClientRejectOverload` validates Router RPC client overload control and related failover metrics. It ensures overloaded Router client pools reject work only when configured, that HA Router clients can spread load, and that no-namenode and communication failures are reported correctly.

## Important APIs, types, and functions

The suite uses `StateStoreDFSCluster`, `RouterConfigBuilder`, `DFSClient`, `ClientProtocol`, `FederationRPCMetrics`, `MiniDFSCluster`, `NameNode`, `simulateSlowNamenode()`, `simulateThrowExceptionRouterRpcServer()`, `transitionClusterNSToStandby()`, `transitionClusterNSToActive()`, `ObjectMapper`, and Java executors/futures.

## Control flow

`setupCluster(overloadControl, ha)` starts a two-nameservice cluster, enables state store, metrics, admin, RPC, and heartbeat, reduces Router client threads to `4`, optionally enables `DFS_ROUTER_CLIENT_REJECT_OVERLOAD`, and starts without datanodes. `testOverloaded()` submits parallel `renewLease()` calls via separate DFS clients, staggers start times, counts overload `StandbyException` remote failures, and asserts expected counts.

`testWithoutOverloadControl()` proves slow namenodes do not cause client overload rejections. `testOverloadControl()` simulates a slow namenode and expects several overload rejections, then verifies an HA client using two Routers distributes operations. `testConnectionNullException()` injects Router RPC connection-null failures and checks failure metrics. `testNoNamenodesAvailable()` and `testNoNamenodesAvailableLongTimeWhenNsFailover()` cover standby-only windows and cache rotation. `testAsyncCallerPoolMetrics()` parses JSON from `getAsyncCallerPool()` while a slow request is active.

## State and persistence behavior

State includes Router RPC metrics, async caller pool counters, namenode HA states, Router state-store cache, and client retry configuration. No durable user data is needed; calls use `renewLease()` and metadata reads.

## Dependencies and integration points

This file integrates overload rejection, asynchronous RPC caller pool sizing, Router HA failover, metrics JSON, simulated slow namenodes, and no-namenode cache recovery.

## Risks and test signals

The concurrency tests are timing sensitive, with tolerated overload ranges. They are strong signals for thread-pool saturation behavior and metrics regressions, but can be affected by scheduler timing on slow test hosts.
