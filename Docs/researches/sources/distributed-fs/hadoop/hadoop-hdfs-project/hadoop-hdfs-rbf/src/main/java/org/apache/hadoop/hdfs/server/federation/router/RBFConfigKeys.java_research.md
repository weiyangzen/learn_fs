# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RBFConfigKeys.java

## Purpose
`RBFConfigKeys` defines the Router-Based Federation configuration namespace, all router-specific keys, and default values used by router services, state store, RPC clients, HTTP/admin servers, quota, safemode, security, fairness, observer reads, async RPC, and federation rename.

## Important APIs, Types, And Functions
- `FEDERATION_ROUTER_PREFIX` is the root `dfs.federation.router.` prefix.
- RPC/admin/http defaults define bind keys, addresses, ports, handler counts, and enable flags.
- Heartbeat and monitor keys define router and NameNode heartbeat intervals, monitor lists, DNS resolution options, and health timeouts.
- State-store keys define enablement, serializer, driver class, ZooKeeper defaults, cache TTLs, and membership/router expiration.
- Quota, safemode, mount-table cache, security, delegation token, fairness, observer, async RPC, and federation rename keys supply feature flags and defaults.

## Control Flow
There is no executable control flow beyond class initialization of constants. Runtime services read these keys from `Configuration` during their own initialization.

## State And Persistence
The class stores only immutable public constants. It indirectly controls persisted behavior by selecting state-store drivers, paths, cache TTLs, and feature enablement defaults.

## Dependencies And Integration Points
Defaults reference implementation classes such as `MountTableResolver`, `MembershipNamenodeResolver`, `StateStoreZooKeeperImpl`, `StateStoreSerializerPBImpl`, `ZKDelegationTokenSecretManagerImpl`, `FederationRPCPerformanceMonitor`, and `NoRouterRpcFairnessPolicyController`. Nearly every router class in this subset imports some keys.

## Risks And Edge Cases
Default choices are operationally significant: RPC, admin, HTTP, state store, router heartbeat, metrics, and safemode are enabled by default, while quota and async RPC are disabled by default. Misconfigured timeouts or handler counts can cause broad router behavior changes. Because keys are public constants, renames are compatibility-sensitive and must preserve deprecated behavior or migration paths.

## Test Signals
Configuration defaults are exercised broadly through `MiniRouterDFSCluster`-based tests, `TestRouter`, heartbeat tests, admin tests, quota tests, fairness tests, observer-read tests, and async RPC tests. Tests that instantiate routers with minimal configs are especially useful for detecting accidental default changes.
