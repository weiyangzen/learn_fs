# sources/control-plane/mayastor/io-engine/src/replica_backend.rs

## Purpose
This file defines the backend-neutral replica and snapshot contracts. It lets higher-level code manipulate replicas, snapshots, and clones without depending on LVS or LVM implementation details.

## Important APIs, Types, And Functions
`ReplicaOps` extends `LogicalVolume` and `BdevStater` with share/unshare/update, resize, entity ID, destroy, snapshot creation, snapshot config preparation, PTPL creation, and bdev access. `SnapshotOps` defines snapshot destroy, clone config preparation, clone creation, descriptor lookup, and discarded-state check. `ListReplicaArgs`, `FindReplicaArgs`, `ListSnapshotArgs`, `FindSnapshotArgs`, and `ListCloneArgs` are filter types. `IReplicaFactory` is the backend trait. `ReplicaBdevStats` augments bdev stats with entity and pool metadata. `ReplicaFactory` selects concrete factories and probes replicas.

## Control Flow
Callers use filter structs to locate replicas/snapshots/clones through every enabled backend. `ReplicaFactory::find` returns the first non-snapshot replica unless `allow_snapshots` is set. `bdev_as_replica` asks each backend whether an untyped bdev can be treated as a replica. Default snapshot/clone config helpers construct `SnapshotParams` and `CloneParams` from names/UUIDs.

## State, Persistence, And Dependencies
This file holds no state. It defines abstractions over backend state. Dependencies include core logical volume, share, snapshot, bdev stats types, pool backend errors, and concrete LVS/LVM replica factories.

## Integration Points
RPC services, NVMf custom admin snapshot handling, snapshot/clone workflows, and stats paths use these traits. LVS implements the traits in `lvs/mod.rs`.

## Risks
Factory probing hides backend order in `PoolFactory::backends`. `FindReplicaArgs::allow_snapshots` is a subtle safety switch. Trait objects use `?Send`, consistent with SPDK thread affinity but requiring callers to stay on appropriate reactors.

## Test Signals
Tests should verify replica lookup excludes snapshots by default, `allow_snapshots` behavior, bdev-to-replica conversion, stats metadata construction, snapshot/clone config helpers, and multi-backend probing error behavior.
