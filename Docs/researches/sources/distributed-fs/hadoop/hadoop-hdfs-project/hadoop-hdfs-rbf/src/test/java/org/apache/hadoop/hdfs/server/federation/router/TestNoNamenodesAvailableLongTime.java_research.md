# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestNoNamenodesAvailableLongTime.java

## Purpose

`TestNoNamenodesAvailableLongTime` reproduces a failover window where a Router cache records no active namenode even though one namenode has become active in the cluster. It verifies that Router RPC cache rotation recovers without waiting for the next state-store cache refresh, including observer-read scenarios.

## Important APIs, types, and functions

The setup path uses `StateStoreDFSCluster`, `RouterConfigBuilder`, `NamenodeHeartbeatService`, `FederationRPCMetrics`, `FederationNamenodeContext`, `FederationNamenodeServiceState`, `NameNode`, and client `FileSystem` instances. Helper methods include `setupCluster()`, `initEnv()`, `routerCacheNoActiveNamenode()`, `allRoutersLoadCache()`, `allRoutersHeartbeat()`, `transitionActiveToStandby()`, `setSecondNonObserverNamenodeInTheRouterCacheActive()`, and `stopObserver()`.

## Control flow

`setupCluster()` builds an HA federated cluster with configurable observer namenode count and a long cache flush interval. `initEnv()` transitions all namenodes to standby, heartbeats and loads Router caches so the Router sees no active, then switches the second non-observer cached namenode to active and heartbeats without refreshing the Router cache. Tests then perform filesystem operations that initially hit stale routing state and rely on Router RPC retry/cache rotation to recover.

`testShouldRotatedCache()` verifies create succeeds after one `NoNamenodesAvailableException` metric increment. `testShouldNotBeRotatedCache()` proves illegal operations, such as default ACL on a file, should not be treated as cache-rotation signals after the active is already reachable. `testUseObserver()`, `testAtLeastOneObserverNormal()`, and `testAllObserverAbnormality()` cover observer reads when observers are available, partially down, or all down.

## State and persistence behavior

State is split between NameNode HA state, heartbeat records in the state store, and Router in-memory resolver cache. The central persistence behavior is intentional staleness: heartbeat records are updated, but Router cache refresh is withheld. Metrics such as `getProxyOpNoNamenodes()`, `getObserverProxyOps()`, and `getProxyOpFailureCommunicate()` are used as observable state.

## Dependencies and integration points

This test integrates failover, Router resolver cache ordering, observer read routing, client retry policy (`dfs.client.retry.max.attempts`), ACL validation, and RPC metrics. It depends on `NoNamenodesAvailableException` being classified as an unavailable exception by `RouterRpcClient`.

## Risks and test signals

The test is timing and ordering sensitive because it depends on cached namenode list order and manual heartbeat/cache refresh sequencing. It provides strong signals for regressions that cause long-lived stale `NoNamenodesAvailableException` responses after failover, but it does not model real asynchronous cache refresh races beyond the controlled mini-cluster sequence.
