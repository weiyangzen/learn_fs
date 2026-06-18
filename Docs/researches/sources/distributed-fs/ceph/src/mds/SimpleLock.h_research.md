# sources/distributed-fs/ceph/src/mds/SimpleLock.h

Purpose: Defines the MDS metadata lock abstraction used by dentries, inodes, scatter locks, file locks, local locks, and cap permission derivation.

Important APIs/types: `LockType` maps Ceph lock IDs to state-machine tables (`sm_simplelock`, `sm_scatterlock`, `sm_filelock`, `sm_locallock`). `SimpleLock` defines wait masks, state/action/type names, lease/rdlock/wrlock/xlock APIs, gather-set APIs, cache APIs, state encode/decode, replica/rejoin helpers, cap calculation helpers, and formatter/print support.

Control flow: State-machine tables determine whether clients or auth MDS can lease/read/rdlock/wrlock/xlock. Waiters are translated into parent-object waiter bits via lock-specific shifts. Auth locks initialize gather sets from replicas for distributed state transitions; replica import/export helpers remove gather participants and decide when a transition has completed.

State and persistence behavior: Durable/replayable state is `state` plus gather set. Local pinning state (`num_rdlock`, `num_wrlock`, `num_xlock`, xlock owner, exclusive client, caches) is transient. `set_state_rejoin()` marks locks needing recovery when a replica survived an auth failover with non-sync state.

Dependencies and integration points: Depends on `MDSCacheObject`, `locks.h`, `MutationImpl`, Ceph cap constants, `MDLockCache`, and MDS waiter contexts. It is foundational for cache authority, replica coherence, capability issuance, and journal replay of locked metadata.

Risks: `WAIT_XLOCK` and `WAIT_STABLE` intentionally share the same bit, so callers must use them consistently. Capability grants vary by auth/replica/loner/xlocker state; bugs can produce stale cache permissions. Replica state export/rejoin is sensitive to auth failover and unsafe request replay.

Test signals: Validate state/action/type string coverage, every lock type's state-machine pointer, cap grants under auth/replica/loner/xlocker modes, gather removal during export/import, rejoin recovery marking, and encode/decode compatibility.
