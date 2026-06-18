# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestObserverWithRouter.java

## Purpose

`TestObserverWithRouter` is the main observer-read and state-id propagation test suite for Router-Based Federation. It verifies that reads are routed to observer namenodes only when client and Router configuration permit it, that `msync` and federated state propagation keep observer reads consistent, and that the Router handles observer failure, stale state ids, and per-namespace overrides.

## Important APIs, types, and functions

The suite uses `MiniRouterDFSCluster`, `RouterContext`, `MockResolver`, `RouterConfigBuilder`, `FederationNamenodeContext`, `FederationNamenodeServiceState`, `MembershipNamenodeResolver`, `RouterStateIdContext`, `ClientGSIContext`, `RouterFederatedStateProto`, `RpcHeaderProtos`, and the client proxy providers `RouterObserverReadProxyProvider` and `RouterObserverReadConfiguredFailoverProxyProvider`. `ConfigSetting` enumerates three client enablement modes: a namenode proxy flag, direct Router observer-read proxy provider, and configured HA failover proxy provider.

## Control flow

`init()` starts a two-nameservice HA cluster with two observers per nameservice unless a test is tagged to skip automatic startup. `startUpCluster()` applies default observer-read, tail-edits, and state-context settings; starts namenodes; transitions one active, one standby, and remaining observers per namespace; starts Router RPC; registers namenodes; installs mock locations; and selects a Router.

The early tests verify basic routing: writes go to active, eligible reads go to observers, and missing client observer configuration keeps reads on active. Other tests disable federated state propagation or per-nameservice observer reads and assert active-only behavior. Failure tests stop observers and verify fallback to active or remaining observers while marking unavailable namenodes. `testRouterMsync()` and the auto-msync tests count active RPCs caused by explicit and implicit `msync`.

State-id tests exercise `ClientGSIContext.receiveResponseState()`, `RouterStateIdContext.updateResponseState()`, max-size filtering, namespace cleanup, shared state across connection-pool cleanup, periodic active refresh when state becomes stale, and behavior when restarted active namenodes stop sending state ids.

## State and persistence behavior

The key state is in-memory state id tracking per namespace via `LongAccumulator`, encoded router federated state in RPC response headers, Router resolver membership cache, observer eligibility configuration, and metrics counters for active versus observer proxy operations. The suite also manipulates cluster membership expiry and connection pool cleanup to validate state cleanup. It does not persist mount table edits; locations are installed through mock cluster setup.

## Dependencies and integration points

This file spans HDFS client failover configuration, Router RPC routing, observer namenode HA states, tail edits, connection pools, state-id propagation headers, and metrics. It is a major integration signal for consistency of observer reads through RBF.

## Risks and test signals

The tests rely on precise RPC-count expectations and mini-cluster timing, especially for auto-msync periods, connection-pool cleanup, and periodic state refresh. They catch regressions that route reads to stale observers, omit `msync`, over-propagate state headers, fail to clean namespace state, or mishandle restarted namenodes with disabled state context.
