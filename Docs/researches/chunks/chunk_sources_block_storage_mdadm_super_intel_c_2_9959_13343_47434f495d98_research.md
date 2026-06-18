# Chunk Research: sources/block-storage/mdadm/super-intel.c lines 9959-13343

## Scope

This chunk covers the tail of IMSM reshape-apply logic, mdmon metadata update preparation/processing, disk deletion and degradation helpers, container validation, bad-block handling, migration backup/recovery, drive policy checks, spare criteria, reshape analysis/execution, reshape management, internal bitmap support, and the final `super_imsm` superswitch registration.

The first lines are a continuation from the previous chunk: `apply_reshape_container_disks_update()` has already found or allocated a replacement `imsm_dev`; this chunk finishes expanding maps, swapping `id->dev`, clearing the migration record, and returning success.

## APIs And Entry Points

- `imsm_process_update(st, update)` is the mdmon-side dispatcher for `enum imsm_update_type` records. It handles checkpoint, takeover, container reshape, migration reshape, size change, spare activation, array create/kill/rename, disk add/remove, bad-block preallocation, and RWH policy updates.
- `imsm_prepare_update(st, update)` validates update payload sizes and preallocates memory needed by `imsm_process_update()`, including `update->space`, `update->space_list`, and enlarged metadata buffers via `super->next_buf`.
- `apply_takeover_update(u, super, space_list)` applies RAID10-to-RAID0 and RAID0-to-RAID10 metadata transformations.
- Migration/reshape backup hooks include `init_migr_record_imsm()`, `save_backup_imsm()`, `save_checkpoint_imsm()`, `recover_backup_imsm()`, `wait_for_reshape_imsm()`, `check_degradation_change()`, and `imsm_manage_reshape()`.
- Internal bitmap hooks include `add_internal_bitmap_imsm()`, `locate_bitmap_imsm()`, `write_init_bitmap_imsm()`, and `set_bitmap_imsm()`.
- The chunk closes by populating `struct superswitch super_imsm`, wiring the above functions into mdadm/mdmon's metadata abstraction.

## Control Flow

Metadata updates follow a two-phase local/remote pattern. Callers allocate a typed update record, invoke `imsm_update_metadata_locally()`, and optionally queue the same record with `append_metadata_update()` if `st->update_tail` is present. `imsm_update_metadata_locally()` constructs a temporary `metadata_update`, calls `imsm_prepare_update()`, then `imsm_process_update()`, and finally frees any preallocated `space_list` nodes.

Container reshape flow starts in `imsm_reshape_super()` when the target device name equals the container name. It validates a pure RAID-disk-count increase through `imsm_reshape_is_allowed_on_container()`, fixes size mismatches, builds an `update_reshape_container_disks` record with selected spares, applies it locally, and may queue it. The apply function was started in the previous chunk and finishes here by enlarging each `imsm_map`, copying the old map to `MAP_1`, marking only selected arrays as `MIGR_GEN_MIGR`, resetting array size, replacing the `imsm_dev`, and clearing `super->migr_rec`.

Volume reshape flow starts in `imsm_reshape_super()` when operating on a subarray. It resolves the active subarray by mdstat, sets `super->current_vol`, calls `imsm_analyze_change()`, then dispatches to takeover, migration, or array-size updates. `imsm_analyze_change()` supports RAID0->RAID5 migration, RAID0<->RAID10 takeover, RAID5 layout changes between supported IMSM layouts, chunk-size migration except RAID10, and expand-only size changes.

Runtime reshape management is performed by `imsm_manage_reshape()`. It locates exactly one volume with `MIGR_GEN_MIGR`, initializes or reloads migration checkpoint state, allocates a checkpoint buffer, loops over migration units, backs up critical stripes into the IMSM migration copy area when source/destination geometry overlaps, advances kernel reshape through sysfs `sync_max`/`suspend_lo`/`suspend_hi`, writes checkpoint states, watches degradation, and clears on-disk migration records after success.

Recovery flow in `recover_backup_imsm()` only runs during assembly when sysfs `array_state` is `inactive`, the migration record indicates data in the copy area, and exactly one IMSM volume is in general migration. It reads the migration copy area from valid member disks, writes it back to the destination offset, tolerates skipped disks only up to `imsm_get_allowed_degradation()`, then marks the copy area normal through `save_checkpoint_imsm()`.

## State And Dependencies

Key mutated state includes `super->buf`, `super->next_buf`, `super->updates_pending`, `super->anchor->num_disks`, `num_raid_devs`, disk `index`/`raiddisk`/status flags, `imsm_dev` map state, RAID level, member counts, order tables, array size, migration unit fields, BBM log entries, and RWH bitmap policy.

The chunk depends on earlier IMSM helpers for map access, map sizing, ordinal access, RAID geometry, metadata mutation, disk lookup, geometry validation, and bitmap layout. It also uses mdadm-wide sysfs helpers, mdstat lookup, spare selection, metadata queueing, bad-block helpers, stripe conversion, platform/HBA discovery, ATA/NVMe encryption probes, device size/path helpers, and OS calls like `open()`, `lseek()`, `read()`, `write()`, `fsync()`, and `posix_memalign()`.

## Risks And Cross-Chunk References

- The takeover path contains an inline FIXME warning that nested index renumbering for RAID10-to-RAID0 failed disks may be wrong.
- Several update paths assume prepared scratch memory exists and use generic allocations as linked-list nodes; size/type mismatches could corrupt later frees.
- `apply_reshape_migration_update()` is defined just before this chunk and only accepts `u->subdev <= 1`, while this chunk’s callers can operate on selected subarrays.
- `recover_backup_imsm()` may issue partial restore writes before deciding too many disks were skipped.
- `imsm_manage_reshape()` aborts on `degraded > 1`, while allowed degradation is topology-dependent elsewhere.
- `write_init_bitmap_imsm()` computes `to_write` but writes `MAX_SECTOR_SIZE` each loop.
- This chunk starts mid-`apply_reshape_container_disks_update()`; setup and spare conversion are in the previous chunk around lines 9897-9958.
- Earlier definitions around lines 529-610 provide `enum imsm_update_type`, update structs, `geo_params`, and reshape type enums used throughout this chunk.
- The final `super_imsm` table is the integration boundary for the whole file, exposing both earlier and current chunk functions to mdadm/mdmon.

## Summary

This chunk is the operational back half of IMSM metadata handling. It turns prepared typed updates into durable metadata mutations, validates platform and drive policies, manages online reshape backup/checkpoint/recovery, supports bad-block and internal bitmap hooks, and registers the completed IMSM implementation with mdadm’s superswitch interface.