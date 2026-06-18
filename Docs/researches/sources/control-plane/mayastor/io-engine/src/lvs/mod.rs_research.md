# sources/control-plane/mayastor/io-engine/src/lvs/mod.rs

## Purpose
This module is the LVS backend adapter that connects the concrete SPDK logical-volume implementation to the generic pool, replica, snapshot, and stats traits used by io-engine services. It re-exports the internal LVS/lvol types and hides backend-specific calls behind `PoolOps`, `ReplicaOps`, `SnapshotOps`, `IPoolFactory`, and `IReplicaFactory`.

## Important APIs, Types, And Functions
The public exports are `Lvs`, `Lvol`, `LvsBdev`, iterators, `LvsError`, snapshot descriptors, and snapshot ops. `impl ReplicaOps for Lvol` maps share/unshare, resize, entity-id, destroy, snapshot, and bdev access to lvol methods. `impl SnapshotOps for Lvol` maps snapshot destruction and clone creation. `impl PoolOps for Lvs` handles replica creation, pool destroy/export/grow, and error reset. `PoolLvsFactory` creates/imports/finds/lists pools; `ReplLvsFactory` converts bdevs to replicas and finds/lists replicas, snapshots, and clones.

## Control Flow
Pool creation/import starts at `PoolLvsFactory` and calls `Lvs::create_or_import` or `Lvs::import_from_args`. Replica creation calls `Lvs::create_lvol_with_opts`. Listing paths filter by backend, pool name/uuid, replica name/uuid, or snapshot/source uuid. Snapshot and clone paths first locate the relevant `Lvol`, validate whether it is a snapshot when required, then delegate to snapshot helpers in `lvol_snapshot`.

## State, Persistence, And Dependencies
State is the underlying SPDK LVS metadata and lvol properties. Entity IDs, snapshots, clone relationships, pool UUIDs, and base bdev identity come from the lvol/LVS layer. Stats use SPDK bdev stats from the lvol or the LVS base bdev. Dependencies include `core` bdev/share/snapshot traits, `pool_backend`, `replica_backend`, SPDK bdev stats reset, and the internal LVS submodules.

## Integration Points
This is the LVS implementation selected by `PoolFactory` and `ReplicaFactory`. It integrates with RPC/control-plane operations that create/list/destroy pools and replicas, NVMf sharing via `Lvol::share_nvmf`, snapshot RPC flows through `SnapshotOps`, and pool metrics through `BdevStater`.

## Risks
`ReplLvsFactory::find` returns any lvol by UUID and relies on upper layers to reject snapshots unless requested. Pool disk reporting unwraps crypto base bdevs and returns an empty list if the base bdev is not available. Snapshot lookup paths convert missing lvols into `Invalid` errors while other list paths silently return empty results, so callers need to account for mixed semantics.

## Test Signals
Useful coverage includes creating/importing/exporting/growing/destroying LVS pools, creating and listing replicas with every filter, verifying snapshot and clone list behavior, rejecting non-snapshot lookups through `find_snap`, share/unshare and PTPL paths, stats/reset behavior, encrypted pool disk reporting, and bdev-to-replica conversion for snapshot and non-snapshot lvols.
