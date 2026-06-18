# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/ActiveNamenodeResolver.java

Purpose: `ActiveNamenodeResolver` is the real-time resolver contract for finding eligible Namenodes by nameservice or block pool and for publishing Namenode liveness/state into the State Store.

Important APIs: callers can mark an address unavailable or active, get prioritized Namenode contexts for a nameservice with optional observer-first ordering, get contexts by block pool, register heartbeat/status reports, list active namespaces, list disabled namespaces, set the parent router ID, and rotate cached priority after a bad target.

Control flow and state: interface only. `MembershipNamenodeResolver` is the implementation in this subset and uses State Store membership/disabled namespace records plus in-memory caches.

Dependencies and integration points: used by `RouterRpcServer` to choose target Namenodes, `NamenodeHeartbeatService` to register reports, `RBFMetrics` for namespace aggregation, and `ErasureCoding` for all-namespace fan-out.

Risks: the contract allows `null` lists in the implementation despite comments saying empty lists, so callers must defensively handle both. Ordering semantics are central to failover and observer reads.

Test signals: implementation tests should cover active/observer/standby/unavailable priority, disabled namespace filtering, block-pool lookup, cache rotation, and heartbeat registration.
