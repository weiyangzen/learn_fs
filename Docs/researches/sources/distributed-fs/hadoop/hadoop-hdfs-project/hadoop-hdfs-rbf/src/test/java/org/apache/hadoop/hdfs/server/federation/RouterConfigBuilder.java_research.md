# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/RouterConfigBuilder.java

## Purpose
`RouterConfigBuilder` is a fluent test helper for constructing router `Configuration` objects with selected services enabled. It keeps test setup compact and ensures test routers bind to ephemeral local ports.

## Important APIs, Types, and Functions
The builder controls RPC, admin, HTTP, heartbeat, local heartbeat, state store, metrics, quota, safemode, cache refresh, and federation rename behavior. It exposes paired boolean setters such as `rpc(boolean)` and convenience enablers such as `rpc()`, `stateStore()`, `metrics()`, `quota()`, and `safemode()`. `set(String,String)` records arbitrary extra configuration.

## Control Flow
Callers set flags fluently, then `build()` writes the matching `RBFConfigKeys` into the underlying `Configuration`. RPC, admin, and HTTP services get `127.0.0.1:0` advertised addresses and `0.0.0.0` bind hosts when enabled. `stateStore()` also resets the state-store driver class to the test driver from `FederationStateStoreTestUtils`.

## State and Persistence
The builder holds mutable booleans, the selected `RouterRenameOption`, an extra key-value map, and the target `Configuration`. `build()` mutates and returns that same configuration; repeated builds reuse accumulated state.

## Dependencies and Integration Points
It depends on router config keys, `RouterFederationRename.RouterRenameOption`, the state-store test utility, and `StateStoreDriver`. It is used throughout router, fairness, metrics, resolver, and disable-nameservice tests to start only the router services a test needs.

## Risks and Test Signals
Because the builder mutates its `Configuration`, sharing one builder across tests can leak settings. `all()` does not enable quota or cache refresh, so tests needing those must opt in. Test signals are router startup with expected service endpoints, state-store-backed resolver availability when `stateStore()` is used, and metrics/JMX visibility when `metrics()` and `http()` are enabled.
