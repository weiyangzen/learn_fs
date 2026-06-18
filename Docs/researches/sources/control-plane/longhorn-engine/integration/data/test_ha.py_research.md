# sources/control-plane/longhorn-engine/integration/data/test_ha.py

## Purpose
This pytest module exercises high-availability behavior for Longhorn engine volumes under replica failure, rebuild, revision-counter divergence, backing-image rebuilds, volume expansion, expansion rollback, and replica-side corruption. It is a black-box integration suite over controller and replica gRPC fixtures plus CLI helper commands.

## Important APIs, types, and functions
- Test entry points: `test_ha_single_replica_failure`, `test_ha_single_replica_rebuild`, `test_ha_double_replica_rebuild`, `test_ha_revision_counter_consistency`, `test_snapshot_tree_rebuild`, backing-file rebuild variants, `test_ha_remove_extra_disks`, expansion/rebuild tests, and `test_replica_crashed_update_state_error`.
- Shared helper `ha_single_backing_replica_rebuild_test` factors backing raw/qcow2 rebuild checks.
- The file depends heavily on `common.core` helpers for lifecycle (`open_replica`, `cleanup_replica`, `cleanup_controller`), data I/O (`get_dev`, `get_blockdev`, `verify_data`, `verify_read`, `verify_async`), polling (`wait_for_rebuild_complete`, `wait_for_purge_completion`, `wait_for_volume_expansion`), and model helpers (`Snapshot`, `Data`).
- `common.cmd` exposes engine CLI calls such as `add_replica`, `snapshot_create`, `snapshot_info`, and `snapshot_purge`.
- Constants define stable volume names, replica directories, disk/head metadata names, page/volume sizes, backing volume names, and expansion target sizes.

## Control flow
Most tests start by opening one or more replica fixtures, starting a controller volume with those replica URLs, asserting all replicas are initially `RW`, then writing deterministic random data through the exported block device. Failure cases intentionally remove, close, or corrupt one replica, verify the controller marks it `ERR`, and continue I/O on the surviving replica. Rebuild flows delete the failed controller replica entry, reopen/recreate the replica backend, call `cmd.add_replica`, then wait until rebuild completion before asserting state and data.

The double-rebuild test creates asymmetric revision counters by closing replica2, doing additional writes on replica1, then closing replica1 and restarting the controller with reversed replica order. The expected behavior is that the lower revision-counter replica is listed but marked `ERR`, and rebuilding it synchronizes both revision counters.

Expansion tests write before and after expanding a volume from `SIZE` to `EXPANDED_SIZE`, delete/rebuild replicas, and verify old and expanded regions. Failure/rollback tests create directories at expected temporary expansion metadata paths so expansion metadata updates fail; they verify rollback state, absence of failed expansion artifacts, unchanged replica meta `Size`, and later successful retry.

## State and persistence behavior
The suite validates persistent disk chains, replica revision counters, snapshot metadata, replica JSON metadata, expansion artifact files, and volume-head data across process cleanup/restart. It checks both controller-visible state (`replica_list`, `volume_get`, snapshot info) and filesystem state in fixed replica directories, including `volume-head-000.img`, expansion disk files, temporary metadata, and `REPLICA_META_FILE_NAME`.

## Dependencies and integration points
These tests require the Longhorn engine/controller/replica integration fixtures, local block device frontend support, CLI wrappers in `common.cmd`, snapshot tree helper data, JSON metadata files in fixed replica directories, and backup/backing-file test fixtures. They cross the controller gRPC API, replica gRPC API, sync/rebuild path, backing-image path, frontend block device path, and Linux filesystem operations.

## Risks and edge cases
- The tests rely on exact revision counter increments, which can be sensitive to request coalescing or backend write count changes.
- Fixed-path metadata manipulation is intentionally invasive and can leave artifacts if cleanup fixtures fail.
- Expansion rollback assertions assume temporary metadata cleanup happens synchronously enough for immediate filesystem checks after polling volume expansion state.
- The backing rebuild helper contains snapshot purge expectations that encode a workaround for not removing the parent of `volume-head`; engine snapshot chain changes could break this.
- `test_replica_crashed_update_state_error` simulates disk corruption by deleting the head file and depends on fast asynchronous controller state updates.

## Test signals
Strong signals include replica mode transitions (`RW`, `WO`, `ERR`), preserved reads after failures, synchronized revision counters after rebuild, snapshot tree shape after purge, data integrity across backing formats, zero-filled expanded regions, accurate `last_expansion_error`/timestamp fields, replica meta `Size` values, and automatic state update to `ERR` after head-file removal.
