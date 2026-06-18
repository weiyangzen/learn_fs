# sources/control-plane/mayastor/io-engine/src/rebuild/snapshot_rebuild.rs

## Purpose
This file implements snapshot-to-replica rebuild jobs. It composes the generic bdev rebuild engine with URI creation/destruction logic and snapshot/replica metadata.

## Important APIs, Types, And Functions
`SnapshotRebuildJob` wraps a `BdevRebuildJob` plus job UUID, replica UUID, snapshot UUID, and `Uri` wrappers. `Uri` can create/open and later destroy a bdev URI. `SnapshotRebuildJobBuilder` accepts rebuild options, notify callback, bitmap, UUIDs, and explicit replica/snapshot URIs. `build` resolves/creates URIs, builds the inner bdev rebuild, and cleans up on failure. `SnapshotRebuildJob::builder`, `list`, metadata accessors, and `destroy` are public helpers.

## Control Flow
The builder resolves snapshot and replica URIs from explicit URIs or local lvol UUIDs. Explicit URIs are created before use and marked for deletion if creation succeeded. If creating the replica URI fails, the snapshot URI is closed/destroyed. After successful URI setup, the inner bdev rebuild is built from snapshot URI to replica URI. On inner build failure, both URIs are closed. Dropping a `Uri` marked for deletion schedules async destruction on the master reactor.

## State, Persistence, And Dependencies
Runtime state is the inner rebuild job and URI cleanup flags. Persistent effects include data copied into the replica and temporary bdevs created for remote URIs. Dependencies include `device_create`, `device_destroy`, `Bdev`, LVS `Lvol`, generic bdev rebuild, reactors, read options, and rebuild instance macros.

## Integration Points
Snapshot restore/control-plane flows use this job type. `shutdown_snapshot_rebuilds` enumerates and force-stops active snapshot rebuild jobs. The default builder uses `ReadOptions::CurrentUnwrittenFail` to make snapshot reads fail on current unwritten state.

## Risks
The builder has TODOs where lvol snapshot-vs-replica validation comments do not actually return errors. URI destruction is best-effort and async in `Drop`, so cleanup can lag or fail. Explicit URI creation treats `BdevExists` as non-owned and therefore does not delete it, which is correct but depends on accurate ownership assumptions.

## Test Signals
Test explicit and local URI resolution, cleanup when snapshot or replica URI creation fails, inner rebuild build failure cleanup, metadata accessors, instance list/destroy behavior, default read options, and best-effort async cleanup logging.
