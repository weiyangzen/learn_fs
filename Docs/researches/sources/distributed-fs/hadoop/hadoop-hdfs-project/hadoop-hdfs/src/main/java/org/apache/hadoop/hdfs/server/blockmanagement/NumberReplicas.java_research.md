<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/NumberReplicas.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/NumberReplicas.java

## Purpose

`NumberReplicas` is a typed counter container for the replica-state counts BlockManager computes for a block or block group. It centralizes the meaning of live, stale, corrupt, excess, maintenance, decommissioned, and EC-redundant replica counts.

## Important APIs and types

It extends `EnumCounters<StoredReplicaState>`. `StoredReplicaState` includes `LIVE`, `READONLY`, `DECOMMISSIONING`, `DECOMMISSIONED`, `MAINTENANCE_NOT_FOR_READ`, `MAINTENANCE_FOR_READ`, `CORRUPT`, `EXCESS`, `STALESTORAGE`, and striped-only `REDUNDANT`. Accessors expose individual counts and derived totals such as `decommissionedAndDecommissioning`, `maintenanceReplicas`, `outOfServiceReplicas`, and `liveEnteringMaintenanceReplicas`.

## Control flow

There is no complex algorithm in this class. Callers increment enum counters while inspecting storages, then use the named accessors to feed placement, redundancy, maintenance, and reconstruction decisions.

## State and persistence behavior

The state is an in-memory enum-indexed counter array inherited from `EnumCounters`. The class comment calls it immutable, but the inherited counter operations mutate it; callers should treat instances as local computation snapshots rather than persisted state.

## Dependencies and integration points

It integrates with BlockManager replica counting, low-redundancy priority decisions, replication work, decommission/maintenance handling, stale-node logic, excess-replica tracking, and EC internal-block accounting.

## Risks and edge cases

Some counts are intentionally not mutually exclusive: stale replicas may also be live. Maintenance has read-serving and not-for-read subcategories, and out-of-service folds maintenance together with decommissioned/decommissioning. For striped blocks, live excludes redundant internal block replicas, so callers must use `redundantInternalBlocks` separately.

## Test signals

Useful tests exercise accessor derivations after counter increments, stale/live overlap, maintenance read/not-read split, out-of-service totals, and striped redundant counts feeding EC redundancy decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/NumberReplicas.java -->
