# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapshot.c lines 8121-9479

## Scope

This chunk covers the tail of snapshot prevalidation dispatch, snapshot restore cleanup and rollback helpers, snapshot postvalidation dispatch, the RPC entry point for CLI snapshot commands, missed-snapshot in-memory reconciliation, brick-level restore plugin invocation, full origin-volume replacement from a snapshot volume, and a helper that returns active snapshot names and UUIDs. It is a management-plane section of GlusterD snapshot handling, not data-path I/O.

The line range starts inside the preceding prevalidation switch and ends after `glusterd_snapshot_get_volnames_uuids()`. Full-file reconciliation should combine this with earlier chunks that define create/clone/delete/status handlers, snapshot plugin registration, volume-store helpers, and restore preparation.

## Purpose

The code in this range ties snapshot operations into GlusterD's transactional management flow. It makes restore operations crash-aware by moving volume metadata through a trash backup, marking a snapshot as `GD_SNAP_STATUS_UNDER_RESTORE` before destructive work, reverting from the backup if a restore fails, and cleaning backup metadata when the operation succeeds or fails before the commit point.

It also acts as the CLI/RPC dispatcher for all snapshot subcommands. The handler decodes a serialized CLI dictionary, adds the local peer UUID, chooses the command-specific handler by `GF_SNAP_OPTION_TYPE_*`, and returns a CLI response on failure. Postvalidation then performs cluster-wide follow-up such as missed-snapshot list updates, restore cleanup or rollback, and fetchsnap notifications.

The missed-snapshot code maintains `priv->missed_snaps_list`, a per-node/per-snapshot list of brick-level operations that could not be applied everywhere. It deduplicates repeated records and collapses create-then-delete or create-then-restore sequences where the earlier create no longer needs to remain pending.

## Important APIs, Types, and Functions

`glusterd_remove_trashpath(char *volname)` builds `<workdir>/<GLUSTERD_TRASH>/vols-<volname>.deleted`, treats missing trash state as success, and removes the backup directory with `recursive_rmdir()` when present. It depends on `THIS->private` as `glusterd_conf_t` and uses `sys_lstat()` to distinguish `ENOENT` from other filesystem errors.

`glusterd_snapshot_restore_cleanup(dict_t *rsp_dict, char *volname, glusterd_snap_t *snap)` is the success path after restore. It removes the snapshot object with `glusterd_snap_remove(rsp_dict, snap, _gf_false, _gf_true, _gf_false)` and then deletes the restore backup through `glusterd_remove_trashpath()`.

`glusterd_snapshot_revert_partial_restored_vol(glusterd_volinfo_t *volinfo)` is the failure rollback path. It removes the current volume directory under `vols`, renames the trash backup back into place, reloads the restored origin `glusterd_volinfo_t` from disk with `glusterd_store_retrieve_volume()`, transfers the old `snap_volumes` list and `snap_count`, and resets `GF_XATTR_VOL_ID_KEY` on local snapshot bricks that were not missed.

`glusterd_snapshot_revert_restore_from_snap(glusterd_snap_t *snap)` is the startup recovery helper for a snapshot left in restore state. It assumes one volume per snapshot in this code path, finds the parent origin volume from the first snap volume's `parent_volname`, invokes partial-restore rollback, and unreferences the older in-memory volume object.

`glusterd_snapshot_restore_postop(dict_t *dict, int32_t op_ret, char **op_errstr, dict_t *rsp_dict)` chooses restore cleanup or rollback during postvalidation. On success it deletes the snapshot and trash backup. On failure, it checks dictionary key `cleanup`: if missing or zero, it only removes the trash backup; otherwise it reverts the partial restore, marks the snapshot back to `GD_SNAP_STATUS_IN_USE`, persists it with `glusterd_store_snap()`, unmounts a temporary snap mount when the origin volume was stopped, and unreferences stale volume state.

`glusterd_snapshot_postvalidate()` dispatches postvalidation by dictionary key `type`. Create and clone call their specific postvalidate handlers and notify fetchsnap. Delete skips postvalidation when the main op failed; otherwise it updates missed snaps and notifies. Restore updates missed snaps, calls restore postop, and notifies. Activate and deactivate only notify. Status, config, info, and list are no-op postvalidation cases.

`glusterd_handle_snapshot_fn(rpcsvc_request_t *req)` is the unlocked implementation of the CLI snapshot RPC handler. It decodes `gf_cli_req` from XDR, unserializes the request dictionary, sets `"host-uuid"` to `MY_UUID`, reads `"type"`, and calls command-specific handlers such as `glusterd_handle_snapshot_create()`, `glusterd_handle_snapshot_restore()`, `glusterd_handle_snapshot_delete()`, or `glusterd_mgmt_v3_initiate_snap_phases()` for activate/deactivate. `glusterd_handle_snapshot()` wraps it with `glusterd_big_locked_handler()`.

`glusterd_free_snap_op()` and `glusterd_free_missed_snapinfo()` free missed-snapshot list records. `glusterd_snap_op_t` owns at least `brick_path` in this local free helper; this chunk assigns `snap_vol_id` with `gf_strdup()` too, so full-file review should verify ownership is released elsewhere or that `glusterd_free_snap_op()` is incomplete for this allocation.

`glusterd_update_missed_snap_entry()` deduplicates a new `glusterd_snap_op_t` within an existing `glusterd_missed_snap_info`. It matches by `snap_vol_id`, `brick_path`, and op; upgrades pending status to done when a duplicate done record arrives; and marks an earlier create done when a later delete or restore arrives for the same brick number and snap volume.

`glusterd_add_new_entry_to_list()` creates a `glusterd_snap_op_t`, fills `snap_vol_id`, `brick_path`, brick number, op, and status, then either appends it to an existing per-node/per-snapshot record or creates a new `glusterd_missed_snap_info` by splitting `missed_info` as `node_uuid:snap_uuid`.

`glusterd_add_missed_snaps_to_list(dict_t *dict, int32_t missed_snap_count)` parses dictionary keys `missed_snaps_<i>`. Each value is expected in a compact string format parsed as `nodeid:snap_uuid=snap_vol_id:brick_num:brick_path:snap_op:snap_status`, then forwarded to `glusterd_add_new_entry_to_list()`. The comment states no extra lock is needed because the GlusterD big lock is held.

`glusterd_bricks_snapshot_restore(dict_t *rsp_dict, glusterd_volinfo_t *snap_vol, gf_boolean_t *retain_origin_path)` iterates snapshot bricks local to `MY_UUID`, resolves the snapshot backend plugin from `snap_vol->snap_plugin`, formats `snap_vol->volume_id` without hyphens, and calls `snap_ops->restore()` for each local brick. It records any brick failure but still attempts remaining local bricks.

`gd_restore_snap_volume()` replaces an origin volume's management metadata with a duplicate of the snapshot volume. It persists `GD_SNAP_STATUS_UNDER_RESTORE`, stops the snap volume, duplicates `snap_vol`, overwrites origin-derived fields such as `volname`, `volume_id`, version, snap count, and restored-from metadata, calls `glusterd_snap_volinfo_restore()`, restores geo-rep files best-effort, restores quota files as required, sets the new volume status to the original status, links it into `conf->volumes`, stores it, and transfers the origin's `snap_volumes` list on success.

`glusterd_snapshot_get_volnames_uuids()` finds an origin volume, iterates started snapshot volumes under `volinfo->snap_volumes`, populates response dictionary keys `snapname.N`, `snap-id.N`, `snap-volname.N`, sets `snap-count`, serializes the dictionary into `gf_getsnap_name_uuid_rsp`, and fills `op_ret`, `op_errno`, and `op_errstr`.

## Control Flow

Restore success flow runs through the postvalidation path. The restore command's main operation reports `op_ret == 0`; `glusterd_snapshot_postvalidate()` first updates missed-snapshot state, then `glusterd_snapshot_restore_postop()` calls `glusterd_snapshot_restore_cleanup()`. Cleanup removes the snapshot object and deletes the trash backup directory. A fetchsnap notification follows so peers or consumers see the snapshot-list change.

Restore failure has two branches. If dictionary key `cleanup` is missing or zero, the code assumes the restore failed early enough that the origin volume does not need rollback, so it only removes the trash backup. If `cleanup` is set, the code treats the origin volume as partially replaced: it deletes the current volume metadata directory, renames the backup back, reloads volinfo from store, repairs local snapshot brick volume-id xattrs, persists the snapshot status as in-use, and unmounts temporary snap mounts for stopped volumes.

Crash recovery uses persisted snapshot status. `gd_restore_snap_volume()` stores `GD_SNAP_STATUS_UNDER_RESTORE` before stopping the snap volume and before replacing origin metadata. If GlusterD restarts while a snapshot is in that state, `glusterd_snapshot_revert_restore_from_snap()` can locate the parent volume and call the same partial restore revert helper.

CLI dispatch is dictionary-driven. `glusterd_handle_snapshot()` acquires the big lock, `glusterd_handle_snapshot_fn()` decodes and validates the request dictionary, then switches on `type`. Most commands call a `glusterd_handle_snapshot_*()` function that begins the corresponding management operation; activate and deactivate enter the mgmt v3 snapshot phase engine directly. Only failure paths send the CLI response in this function; successful command-specific flows are expected to respond through their own operation machinery.

Missed-snapshot ingestion is a parse-then-merge flow. `glusterd_add_missed_snaps_to_list()` reads all `missed_snaps_i` strings from a dictionary, duplicates each string because the dictionary may be forwarded to non-originator nodes, tokenizes it, validates required fields and positive numeric values, then appends or merges it in `priv->missed_snaps_list`. Deduplication prefers completed status over pending status and collapses redundant create records when delete or restore later makes the missed create irrelevant.

Volume restore flow in `gd_restore_snap_volume()` is staged to make rollback possible. It marks the snapshot under restore and stores that state, stops the snap volume, duplicates the snapshot volinfo, rewrites the duplicate to look like the origin volume while keeping restored-from metadata, restores brick paths and management files via `glusterd_snap_volinfo_restore()`, handles geo-rep and quota side files, then stores the new origin volinfo. Failure before successful store unreferences `new_volinfo`; success transfers the origin's snapshot volume list to the new volume object.

## State and Persistence Behavior

Persistent filesystem state is concentrated under `priv->workdir`. Restore backup directories use `GLUSTERD_TRASH/vols-<volname>.deleted`; origin volume metadata lives under the normal volume directory returned by `GLUSTERD_GET_VOLUME_DIR()`. Rollback mutates those directories with `recursive_rmdir()` and `sys_rename()`, so the backup directory is the only local copy of pre-restore metadata during failure handling.

Snapshot status is persisted with `glusterd_store_snap()`. `GD_SNAP_STATUS_UNDER_RESTORE` is stored before destructive restore work, and `GD_SNAP_STATUS_IN_USE` is stored after rollback. That status is a recovery signal for startup repair.

Volume metadata persistence uses `glusterd_store_retrieve_volume()` during rollback and `glusterd_store_volinfo(new_volinfo, GLUSTERD_VOLINFO_VER_AC_INCREMENT)` during successful restore. The in-memory `conf->volumes` list is updated by adding `new_volinfo`, while stale `volinfo` references are explicitly unreferenced in rollback paths.

Snapshot brick filesystem identity is repaired with `sys_lsetxattr(..., GF_XATTR_VOL_ID_KEY, snap_vol->volume_id, ..., XATTR_REPLACE)` for local snapshot bricks whose `snap_status` is not `-1`. This keeps snapshot brick extended attributes aligned with their snap volume IDs after restore rollback.

`priv->missed_snaps_list` is in-memory cluster state for missed brick operations. This chunk updates it under the big lock but does not itself persist the list; postvalidation calls to `glusterd_snapshot_update_snaps_post_validate()` in this range are the integration point that likely store or reconcile missed-snapshot state elsewhere in the file.

Response state uses Gluster dictionaries. The CLI handler mutates the request dictionary by adding `"host-uuid"`. `glusterd_snapshot_get_volnames_uuids()` writes numbered snapshot fields into a supplied dictionary and serializes it into `snap_info_rsp->dict`.

## Dependencies and Integration Points

This range depends on GlusterD core types and global context: `THIS`, `xlator_t`, `glusterd_conf_t`, `glusterd_snap_t`, `glusterd_volinfo_t`, `glusterd_brickinfo_t`, `rpcsvc_request_t`, `gf_cli_req`, `dict_t`, and the global `MY_UUID`.

It uses Gluster utility APIs for strings, UUIDs, memory, lists, logging, and XDR/dictionary handling: `gf_strncpy()`, `gf_uuid_copy()`, `gf_uuid_compare()`, `uuid_utoa()`, `gf_strdup()`, `GF_FREE()`, `cds_list_*`, `gf_msg()`, `gf_smsg()`, `xdr_to_generic()`, `dict_unserialize()`, `dict_get_*()`, `dict_set_*()`, and `dict_allocate_and_serialize()`.

Filesystem and metadata dependencies include `sys_lstat()`, `sys_rename()`, `recursive_rmdir()`, `sys_lsetxattr()`, `PATH_MAX`, `GF_XATTR_VOL_ID_KEY`, `XATTR_REPLACE`, and macros such as `GLUSTERD_GET_VOLUME_DIR()` and `GLUSTERD_TRASH`.

Snapshot operation integration points include pre/postvalidation handlers from earlier chunks, `glusterd_snap_remove()`, `glusterd_find_snap_by_name()`, `glusterd_snapshot_update_snaps_post_validate()`, `glusterd_fetchsnap_notify()`, `glusterd_snap_unmount()`, and the command handlers for create, clone, restore, info, list, config, delete, status, activate, and deactivate.

Restore integrates with volume lifecycle and side metadata through `glusterd_store_snap()`, `glusterd_stop_volume()`, `glusterd_volinfo_dup()`, `glusterd_snap_volinfo_restore()`, `glusterd_restore_geo_rep_files()`, `glusterd_copy_quota_files()`, `glusterd_set_volume_status()`, and `glusterd_store_volinfo()`.

Backend snapshot mechanics are plugin-based. `glusterd_bricks_snapshot_restore()` resolves `struct glusterd_snap_ops` with `glusterd_snapshot_plugin_by_name()` and calls the plugin's `restore` method for local bricks only. The `retain_origin_path` pointer lets plugin restore logic communicate whether the origin path should be retained.

## Risks and Edge Cases

The range starts in the middle of a prevalidation switch. Full interpretation of the default path and command coverage needs the previous chunk.

Restore rollback is filesystem-destructive. If `recursive_rmdir(pathname)` succeeds but `sys_rename(trash_path, pathname)` fails, the origin metadata directory has been removed and the backup still sits under trash. Recovery procedures must account for that split state.

`glusterd_remove_trashpath()` treats `ENOENT` as success. That is correct for idempotent cleanup, but it can hide cases where a restore expected a backup and it was already missing. Callers rely on the `cleanup` decision and snapshot status to decide whether missing backup is acceptable.

Several paths assume one volume per snapshot. `glusterd_snapshot_revert_restore_from_snap()` takes the first entry in `snap->volumes`, and `glusterd_snapshot_restore_postop()` reads dictionary key `volname1`. Multi-volume snapshot support would need broader iteration and rollback semantics.

The missed-snapshot parser uses `strtok_r()` with `:` and `=` delimiters and then immediately passes some `strtok_r()` results to `atoi()`. If a numeric token is absent, this can call `atoi(NULL)` before the later validation check. Brick paths containing `:` would also break the string format.

`glusterd_add_new_entry_to_list()` mutates its `missed_info` argument with `strtok_r()`. Current callers pass a local buffer and do not reuse the original value, but callers must not pass immutable or still-needed strings.

`glusterd_free_snap_op()` frees `brick_path` but this chunk allocates both `snap_vol_id` and `brick_path`. If `snap_vol_id` is not freed by a broader helper or custom ownership convention outside this slice, missed-snapshot entries leak memory.

`glusterd_bricks_snapshot_restore()` does not check whether `glusterd_snapshot_plugin_by_name()` produced a non-null `snap_ops` with a valid `restore` callback before dereferencing it. Invalid or missing `snap_plugin` values could crash unless guaranteed by earlier validation.

`gd_restore_snap_volume()` copies `restored_from_snapname_id` and `restored_from_snapname` with `strcpy()`. This is safe only if source fields are bounded by the destination arrays' sizes by type contract. Full-file or struct-level review should verify those limits.

`gd_restore_snap_volume()` adds `new_volinfo` to `conf->volumes` before storing it. The failure path relies on `glusterd_volinfo_unref(new_volinfo)` to remove any inserted list entry. That ownership behavior is essential and should be covered by tests.

The CLI handler only sends a response when `ret` is nonzero. Command handlers must own success responses consistently; otherwise clients could hang on success paths.

## Test Signals

Restore cleanup tests should cover successful restore deleting both the snapshot object and `GLUSTERD_TRASH/vols-<vol>.deleted`, plus idempotent cleanup when the trash directory is already absent.

Restore rollback tests should simulate failures after the origin volume directory has been replaced: verify trash backup rename, reloaded volinfo, transferred `snap_volumes`, preserved `snap_count`, reset local snapshot brick `GF_XATTR_VOL_ID_KEY`, and persisted `GD_SNAP_STATUS_IN_USE`.

Crash-recovery tests should force a restart after `GD_SNAP_STATUS_UNDER_RESTORE` is stored and before restore completes, then verify `glusterd_snapshot_revert_restore_from_snap()` restores the origin metadata and unreferences stale volinfo.

Postvalidation tests should exercise all `GF_SNAP_OPTION_TYPE_*` branches: create/clone postvalidate plus fetchsnap notification, delete skipping postvalidate on failed op, delete and restore missed-snap updates, restore cleanup versus rollback, activate/deactivate notification, and no-op status/config/info/list handling.

RPC handler tests should cover malformed XDR, empty request dictionary, unserialization failure, missing `type`, host UUID injection, unknown command type, command-specific handler failures with `op_errno` defaulting to `EG_INTRNL`, and successful paths relying on command handlers for responses.

Missed-snapshot tests should include duplicate pending entries, pending upgraded to done, create followed by delete, create followed by restore, different `snap_vol_id` values, same brick number with different paths, invalid field counts, invalid numeric fields, and paths containing delimiter characters if those are possible in Gluster brick paths.

Brick restore plugin tests should cover local and remote bricks, plugin restore failure on one brick while later local bricks are still attempted, `retain_origin_path` updates, and invalid plugin names if validation does not already reject them.

Volume restore tests should verify snap status persistence before destructive work, stopping the snap volume, origin-derived fields on `new_volinfo`, restored-from metadata, geo-rep restore warning behavior, quota copy hard failure, status preservation, version preservation, store version increment, list insertion/removal on failure, and transfer of `orig_vol->snap_volumes` on success.

`glusterd_snapshot_get_volnames_uuids()` tests should cover no snapshots, stopped snapshots being filtered out, multiple started snapshots with correctly numbered dictionary keys, serialization failure, missing origin volume, and `op_ret`/`op_errno` propagation.

## Cross-Chunk Notes

The preceding chunk contains most snapshot prevalidation and command-specific logic that feeds this postvalidation and restore code. The merge lane should connect dictionary keys such as `type`, `snapname`, `volname1`, `cleanup`, and `missed_snaps_i` to the handlers that set them.

Later chunks, if any, should be checked for persistence of `priv->missed_snaps_list`, definitions of `glusterd_missed_snap_op_new()` and `glusterd_missed_snapinfo_new()`, and any broader cleanup helpers that might free `snap_vol_id` for missed-snapshot records.
