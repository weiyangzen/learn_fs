# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/namenode_tracker.cc

Purpose: implements HA NameNode tracking for failover decisions inside `RpcEngine`.

Important APIs and functions: constructor, destructor, `GetFailoverAndUpdate`, `IsCurrentActive_locked`, `IsCurrentStandby_locked`, and helper `format_endpoints`.

Control flow: the constructor enables HA when at least two resolved NameNode infos are available, stores first as active candidate and second as standby candidate, and marks resolved if endpoints exist. `GetFailoverAndUpdate` identifies whether the current endpoint belongs to active or standby, swaps active/standby on active failure, emits events, and optionally re-resolves endpoints for the selected node.

State and persistence: in-memory active/standby `ResolvedNamenodeInfo`, booleans `enabled_`/`resolved_`, `IoService`, event handlers, and `swap_lock_`. No disk persistence; “active” is a client-side current guess.

Dependencies and integration: depends on NameNode resolution helpers, event handlers, logging, Boost TCP endpoints, and `IoService`. Used by `RpcEngine::RpcCommsError` when retry policy requests failover.

Risks and test signals: only the first two NameNodes are used even if more are configured. Endpoint comparison ignores port mismatch after logging, matching only address. Failover event context uses a cast of `c_str()` to integer, which is fragile for consumers. Tests should cover active failure, standby response, empty endpoint vectors, unresolved standby, and DNS re-resolution.
