# Research: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapshot.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007111`: lines 1-8120, `Docs/researches/chunks/subset-b-007111_research.md`
- `subset-b-007112`: lines 8121-9479, `Docs/researches/chunks/subset-b-007112_research.md`

## Chunk Research

### subset-b-007111: lines 1-8120

# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapshot.c lines 1-8120

## Scope

This chunk covers the first 8120 lines of GlusterFS glusterd snapshot management. It starts at the file header, includes the snapshot RPC handlers, prevalidate and commit dispatchers, snapshot object and snapshot-volume construction, backend brick snapshot scheduling, delete/restore/activate/deactivate/config/status logic, and ends inside `glusterd_snapshot_prevalidate()` after the delete prevalidate branch begins. The source file continues after this chunk with postvalidate dispatch, CLI entry handling, missed-snapshot list parsing, and restore cleanup helpers.

The code in this range is the management-plane coordinator for snapshots. It does not implement a storage snapshot backend directly; instead it validates requests, builds and persists glusterd metadata, creates snapshot volume/brick objects, calls the selected `glusterd_snap_ops` plugin for backend create/clone/activate/deactivate/remove/details operations, drives the mgmt-v3 transaction phases, and prepares response dictionaries for the CLI and peer reconciliation.

## Purpose

The visible file section implements the lifecycle for these snapshot operations:

- `create`: validate the origin volumes, generate snapshot and snapshot-volume UUIDs, create a `glusterd_snap_t`, duplicate origin `glusterd_volinfo_t` objects into snapshot volumes, add snapshot bricks, copy quota and geo-replication metadata, generate volfiles, take backend brick snapshots through plugin callbacks, optionally activate snapshots on create, and record events/limits afterward.
- `clone`: validate an activated snapshot, create a clone volume from the snapshot volume, call backend clone operations, move the clone into the normal volume list, and delete the temporary snapshot object after successful postvalidate.
- `restore`: validate a snapshot has not already been restored, require stopped origin volumes, back up origin volume store directories, collect local brick restore data, run per-brick restore helpers, and replace the origin volume metadata with data from the snapshot.
- `delete`: resolve a single snapshot, all snapshots, or snapshots for a volume, mark snapshots for decommission, remove backend snapshots and glusterd store state, and preserve missed operations for disconnected peers.
- `activate` and `deactivate`: mount or unmount snapshot bricks, start or stop the snapshot volume, and update runtime mount directories.
- `config`, `info`, `list`, and `status`: validate and persist snapshot limits/options, expose snapshot and snapshot-volume metadata, and gather plugin-specific per-brick status details.

The implementation is strongly dictionary-driven. RPC handlers add keys such as `snapname`, `volcount`, `volnameN`, `volN_volid`, `volumeN_username`, `volN.brick_snapdeviceM`, `volN.brickM.status`, `missed_snaps_N`, and `status.snapN.*`; later validation, commit, brick-op, and postvalidate functions rely on those keys to coordinate work across nodes.

## Important APIs, Types, and Data

`snap_create_args_t` carries state for asynchronous per-brick snapshot work. It stores `xlator_t *this`, request/response dictionaries, the snapshot volume, the target brick, a `syncargs` barrier, and volume/brick indexes. `glusterd_schedule_brick_snapshot()` allocates one instance per local eligible snapshot brick and frees it in `glusterd_take_brick_snapshot_cbk()`.

`struct gd_snap_unsupported_opt_t` records volume options that are copied from the origin volume but temporarily unsupported for snapshot volumes. `glusterd_snap_clear_unsupported_opt()` removes quota/deem-statfs options before generating snapshot volfiles and saves their values; `glusterd_snap_set_unsupported_opt()` restores them afterward.

`snap_mount_dir` is a global path buffer used by plugin brick-path and cleanup code to build runtime mount paths below the glusterd snapshot mount root.

`glusterd_find_missed_snap()` scans a snapshot volume's bricks against the peer list and adds missed snapshot create/delete/restore entries when the peer owning a brick is disconnected or not befriended. `glusterd_add_missed_snaps_to_dict()` serializes those entries as `peer_uuid:snap_uuid=snap_volname:brick_number:brick_path:op:status` and increments `missed_snap_count`.

`snap_max_limits_display_commit()`, `snap_max_hard_limits_validate()`, `snap_max_hard_limit_set_commit()`, and `glusterd_snapshot_config_commit()` handle snapshot limits and cluster options. They read and write `GLUSTERD_STORE_KEY_SNAP_MAX_HARD_LIMIT`, `GLUSTERD_STORE_KEY_SNAP_MAX_SOFT_LIMIT`, `GLUSTERD_STORE_KEY_SNAP_AUTO_DELETE`, `GLUSTERD_STORE_KEY_SNAP_ACTIVATE`, and `GLUSTERD_GLOBAL_OPT_VERSION`.

`glusterd_snapshot_restore_prevalidate()` and `glusterd_snapshot_restore()` implement the restore path. Prevalidate ensures the snapshot exists, is not already restored, and all origin volumes are stopped; it backs up the origin volume store directory with `glusterd_snapshot_backup_vol()` and exports local snapshot brick metadata into `rsp_dict`. Commit recreates stopped snapshot brick mounts, calls `glusterd_bricks_snapshot_restore()`, invokes `gd_restore_snap_volume()`, and detaches/unrefs the replaced parent `volinfo`.

`glusterd_snap_create_clone_common_prevalidate()` is shared by snapshot create and clone prevalidation. For every local brick it requires the brick process to be running, probes snapshot support, records the snapshot plugin name, backend snapshot device name, filesystem type, snapshot type, mount options, source brick mount directory, original brick order, and current brick status.

`glusterd_new_snap_object()`, `glusterd_create_snap_object()`, `glusterd_create_snap_object_for_clone()`, `glusterd_find_snap_by_name()`, and `glusterd_find_snap_by_id()` create and find `glusterd_snap_t` objects. Persistent snapshot objects are stored with `glusterd_store_snap()` and inserted into `priv->snapshots` ordered by time. Clone objects are temporary scaffolding and are later deleted from memory.

`glusterd_do_snap_vol()` is the main snapshot-volume constructor. It duplicates an origin `glusterd_volinfo_t`, assigns a new UUID and auth credentials, links it either as a snapshot volume or a clone, copies geo-replication and quota files, creates snapshot brickinfos with `glusterd_add_brick_to_snap_volume()`, removes `features.barrier`, handles Ganesha export state for clones, persists the new volinfo, and generates brick/trusted-client/other-client volfiles.

`glusterd_add_brick_to_snap_volume()` creates each snapshot brickinfo. It records the origin path, consumes filesystem/snapshot/mount data from the prevalidate dictionary, marks missing or down bricks as pending missed snapshots, asks the snapshot plugin to construct the brick path, canonicalizes paths, copies host/UUID/mount metadata, and preserves original brick IDs for non-clone snapshot volumes.

`glusterd_take_brick_snapshot()`, `glusterd_take_brick_snapshot_task()`, `glusterd_take_brick_snapshot_cbk()`, and `glusterd_schedule_brick_snapshot()` drive backend creation. They choose create versus clone plugin operations, optionally activate bricks when `snap-activate-on-create` is enabled, write per-brick success status keys into `rsp_dict`, and wait on a synctask barrier.

`glusterd_snapshot_umount()`, `glusterd_snapshot_remove()`, `glusterd_snap_volume_remove()`, and `glusterd_snap_remove()` tear down snapshot data. They stop brick processes, deactivate mount points through the backend plugin, remove backend snapshots, delete runtime pid/mount directories, delete glusterd store metadata, decrement parent `snap_count`, unref volinfos, delete snapshot store entries, and delete snapshot objects.

`glusterd_snapshot_get_snapvol_detail()`, `glusterd_snapshot_get_snap_detail()`, `glusterd_snapshot_get_all_snap_info()`, `glusterd_snapshot_get_info_by_volume()`, `glusterd_snapshot_get_all_snapnames()`, and `glusterd_snapshot_get_vol_snapnames()` populate CLI response dictionaries for `snapshot info` and `snapshot list`.

`glusterd_get_single_brick_status()`, `glusterd_get_single_snap_status()`, `glusterd_get_each_snap_object_status()`, `glusterd_get_snap_status_of_volume()`, `glusterd_get_all_snapshot_status()`, and `glusterd_snapshot_status_commit()` populate `snapshot status` responses. Pending and deactivated snapshots are special-cased before calling the backend plugin's `details()` callback.

`glusterd_snapshot_prevalidate()`, `glusterd_snapshot()`, and `glusterd_snapshot_brickop()` are transaction-phase dispatchers. Prevalidate switches on `GF_SNAP_OPTION_TYPE_*` and calls operation-specific validators. Commit dispatches create/clone/config/delete/restore/activate/deactivate/status. Brick-op handles create pre/post barriers by setting the barrier value and invoking `gd_brick_op_phase()` for each origin volume.

The handler functions `glusterd_handle_snapshot_config()`, `glusterd_handle_snapshot_info()`, `glusterd_handle_snapshot_list()`, `glusterd_handle_snapshot_create()`, `glusterd_handle_snapshot_status()`, `glusterd_handle_snapshot_clone()`, `glusterd_handle_snapshot_restore()`, and `glusterd_handle_snapshot_delete()` parse CLI/RPC dictionaries, add derived fields, choose local response versus mgmt-v3 transaction, and call `glusterd_mgmt_v3_initiate_snap_phases()` or `glusterd_mgmt_v3_initiate_all_phases()`.

## Control Flow

Snapshot create begins in `glusterd_handle_snapshot_create()`. The handler reads `volcount` and `snapname`, optionally appends a GMT timestamp, stores `snap-time`, generates a snapshot UUID, and for each volume generates internal auth credentials plus a snapshot volume UUID. It then starts the mgmt-v3 snapshot phases. In prevalidate, `glusterd_snapshot_create_prevalidate()` verifies every requested origin volume exists, is started, is not rebalancing, has no active geo-replication session, is not itself a snapshot volume, and has not exceeded the effective hard limit. It then calls the shared prevalidate helper to verify local brick health and snapshot support and to export backend brick parameters.

The create commit path is `glusterd_snapshot()` to `glusterd_snapshot_create_commit()`. It creates and stores the `glusterd_snap_t`, loops over origin volumes, checks soft-limit state on the originator, calls `glusterd_do_snap_vol()` for each volume, schedules backend brick snapshot tasks, writes the snapshot UUID into `rsp_dict`, and either marks snapshot volumes stopped or starts them depending on `snap-activate-on-create`. On any failure after object creation, it force-removes the partially created snapshot.

Clone follows the same broad pattern but starts at `glusterd_handle_snapshot_clone()`, places the clone name into `volname1` to acquire volume locks, generates a clone UUID/auth, and calls the snapshot phases. Prevalidate requires the clone name not to already exist, finds the parent snapshot, requires its snap volume to be activated, and exports backend brick data. Commit creates a temporary snap object named after the clone, records parent snapshot name and parent snapshot-volume ID, builds a clone volume with `glusterd_do_snap_vol(..., clone=1)`, schedules backend clone work, removes the clone volume from the temporary snap list, and inserts it into `priv->volumes`. Postvalidate deletes the temporary snap object on success or cleans up the clone on failure.

Restore begins by expanding the snapshot into its parent volume names in `glusterd_handle_snapshot_restore()`. Prevalidate backs up each stopped origin volume's store directory by moving it into the glusterd trash area and recreating an empty origin volume directory. It also exports local snapshot brick paths, origin paths, status, device paths, filesystem type, snapshot type, and mount options. Commit finds missed restore operations on disconnected peers, recreates snapshot brick mounts as needed, calls the brick restore helper, restores the parent volume metadata, and removes the old parent volinfo from `priv->volumes`.

Delete dispatch first resolves the requested delete mode. Single-snapshot delete populates parent `volnameN` keys for locking and runs mgmt-v3 phases; delete-all and delete-by-volume only populate a response dictionary for CLI confirmation in this handler path. The commit path marks the snapshot `GD_SNAP_STATUS_DECOMMISSION`, stores that state so a restart can observe the in-progress removal, records missed deletes for disconnected peers on the originator, removes backend snapshots and metadata, and returns the removed snap name and UUID.

Activation and deactivation share prevalidation in `glusterd_snapshot_activate_deactivate_prevalidate()`: find the snapshot, fetch the first snap volume, and reject redundant activate/deactivate unless activate is forced. Activate commit calls `glusterd_snap_brick_create()` for local bricks, starts the snapshot volume, and returns the snapshot UUID. Deactivate commit stops the snapshot volume, unmounts snapshot bricks, recursively removes the runtime snapshot mount directory, and returns the snapshot UUID.

Status/info/list flows are mostly local dictionary population. `snapshot info` either walks all snapshots, one snapshot, or one origin volume's snapshot list. `snapshot list` returns all names or names under a volume. `snapshot status` uses the mgmt-v3 commit path to collect names for all/volume queries or full per-brick details for a specific snapshot.

## State and Persistence Behavior

Persistent snapshot state is represented by `glusterd_snap_t` records in `priv->snapshots`, snapshot volume records in `priv->volumes` or in origin volume `snap_volumes` lists, and on-disk glusterd store files. Creation stores the snap object early with status `GD_SNAP_STATUS_INIT`; postvalidate later marks it `GD_SNAP_STATUS_IN_USE`. Delete stores `GD_SNAP_STATUS_DECOMMISSION` before removal. Restore prevalidation physically moves the origin volume store directory into a trash path to allow rollback if backup setup fails.

Snapshot volume state is derived by duplicating origin volume metadata. The code intentionally changes identity and classification fields: `volume_id`, `volname`, `parent_volname`, `is_snap_volume`, `snapshot`, auth credentials, brick paths, and sometimes `restored_from_snap`. Parent origin `snap_count` is incremented when a snapshot volume is added and decremented when it is removed.

Backend state is delegated to snapshot plugins through `struct glusterd_snap_ops`. This chunk calls `create`, `clone`, `activate`, `deactivate`, `remove`, `brick_path`, and `details`. The plugin owns LVM/thin/snapshot-device specifics; glusterd owns request ordering, metadata persistence, and cleanup decisions.

The code persists global config changes by mutating `conf->opts`, bumping `GLUSTERD_GLOBAL_OPT_VERSION`, and calling `glusterd_store_options()`. Per-volume hard limits are persisted by setting `volinfo->snap_max_hard_limit` and storing the volinfo.

Missed snapshot state is first staged in response dictionaries and then, in `glusterd_snapshot_update_snaps_post_validate()`, imported into the in-memory missed list via `glusterd_add_missed_snaps_to_list()` and flushed with `glusterd_store_update_missed_snaps()`. This allows later reconciliation for peers that were down during create/delete/restore.

Runtime mount and pid directories under `snap_mount_dir` are created indirectly by plugin brick-path/activation code and removed by `glusterd_snapshot_remove()` or deactivate cleanup. The code treats some directory cleanup failures as non-fatal when paths are absent or non-empty because multiple bricks can share higher-level snapshot directories.

## Dependencies and Integration Points

This chunk depends on glusterd core types and services: `glusterd_conf_t`, `glusterd_snap_t`, `glusterd_volinfo_t`, `glusterd_brickinfo_t`, peer lists, volume lists, snapshot lists, locking, RCU peer traversal, glusterd store helpers, volfile generation, auth helpers, quota/georep copy helpers, Ganesha export helpers, brick start/stop helpers, and mgmt-v3 transaction orchestration.

It integrates with the snapshot backend plugin layer through `glusterd_snapshot_plugin_by_name()` and `struct glusterd_snap_ops`. Plugin outputs are consumed during prevalidate and commit through brick paths, mount options, fstype/snap type, device names, status details, and backend create/remove/activate/deactivate operations.

It integrates with the CLI/RPC layer through `rpcsvc_request_t`, `glusterd_op_send_cli_response()`, and the command constants `GF_SNAP_OPTION_TYPE_*`, `GF_SNAP_CONFIG_*`, `GF_SNAP_INFO_TYPE_*`, `GF_SNAP_STATUS_TYPE_*`, and `GF_SNAP_DELETE_TYPE_*`. Originating handlers either send a local response for read-only/listing operations or initiate mgmt-v3 phases for mutating cluster operations.

It integrates with brick operations through `glusterd_snapshot_brickop()`, `glusterd_set_barrier_value()`, and `gd_brick_op_phase(GD_OP_SNAP, ...)`. Snapshot create uses this to enable barriers before backend creation and disable them afterward, reducing write activity during the snapshot operation.

It integrates with eventing through `gf_event()` for snapshot activation, snapshot soft/hard limit reached, and auto-delete success/failure. It also emits detailed `gf_msg()` and `gf_smsg()` logs with glusterd message IDs for operational diagnosis.

## Risks and Edge Cases

The code relies on many string-keyed dictionary contracts shared across handlers, validators, commit functions, brick-op phases, and peers. A typo, index mismatch, or inconsistent 0-based versus 1-based counter can silently skip brick metadata or status. This risk is visible in mixed keys such as `volname%d`, `volname%" PRId64`, `vol%d_volid`, `vol%" PRId64 "_brickcount`, `snap-vol%d.brick%d.status`, and `clone%d.brick%d.status`.

The visible code repeatedly documents that only one snapshot volume is currently assumed in places such as clone, activate, deactivate, and status. Multi-volume snapshots are partially supported by loops in create, restore, info, and delete, but several paths still take `snap->volumes.next` directly. Extending multi-volume snapshot support would require careful review of those TODO-marked assumptions.

Several cleanup paths deliberately suppress failures. `glusterd_snapshot_umount()` logs an unmount failure but returns success due to known brick-daemon mount references; auto-delete failures are ignored after logging; half-created snapshot cleanup often forces removal. These choices improve operator progress but can leave backend or runtime state behind.

Restore prevalidation mutates disk state by backing up origin volume store directories before the full distributed restore succeeds. The helper attempts rollback on backup setup failure, but failures after prevalidation rely on later restore cleanup/revert code outside this chunk. This is a high-risk path because it changes durable metadata before final commit completion.

Memory ownership is subtle around dictionary setters. The code mixes `dict_set_dynstr()`, `dict_set_dynstrn()`, `dict_set_dynstr_with_alloc()`, `dict_set_strn()`, and `dict_set_bin()` with manual `GF_FREE()` on failure. Review should verify whether each setter takes ownership or copies data, especially in paths such as clone handling, status string insertion, and generated UUID storage.

Some string handling checks only negative `snprintf()` returns while not always checking truncation. Other calls use buffers such as `char snap_path[4352]`, `char key[64]`, and `char key[128]` for generated paths/keys. Most keys are bounded by known small prefixes, but path and snapshot-name handling should still be tested near maximum lengths.

The clone handler stores `clone-volname%d` using an empty `snap_volname` buffer in the visible code; the actual clone volume identity is later driven by `vol1_volid` and `clonename`, but this key looks suspicious and may be unused or stale.

Backend plugin selection depends on brick prevalidation recording a consistent `snap_plugin`. If different local bricks report different plugins, the shared `volN.snap_plugin` key can be overwritten or only represent the last local brick processed. The code appears to store one plugin name per volume, so heterogeneous backend support is a risk.

Peer-disconnection handling records missed operations, but only for paths where the originator can identify peer ownership. Incorrect peer state, stale brick UUIDs, or failures to persist missed snaps can leave a cluster with divergent backend snapshot state.

Status and info responses use a mixture of local-only enumeration and mgmt-v3 status collection. For status-by-volume and all-status paths, this chunk initially returns names/counts rather than full per-brick details; callers must understand the iteration model to fetch detailed entries.

## Test Signals

Useful tests for this chunk include:

- Snapshot create success with one volume and multiple local/remote bricks, verifying `glusterd_snap_t` status transitions from `INIT` to `IN_USE`, parent `snap_count`, generated volfiles, quota/georep copies, `snapuuid` response, and backend plugin create calls.
- Create prevalidate rejection cases for nonexistent volume, stopped volume, active rebalance, active geo-replication, snapshot volume input, duplicate snapshot name, empty description, unsupported brick snapshot backend, down local brick, and hard-limit exhaustion.
- Create failure injection after snap object creation, after snap volume creation, after backend brick creation, and during volfile generation, verifying force cleanup and absence of leaked store entries where expected.
- Activate-on-create and deactivated-create tests verifying snapshot brick activation, volume status, pid/mount directory behavior, and status response text for deactivated snapshots.
- Clone tests from an activated snapshot, including duplicate clone name rejection, inactive snapshot rejection, backend clone invocation, normal volume-list insertion, temporary snap object deletion, and cleanup on failed clone.
- Restore tests requiring stopped origin volumes, verifying backup of origin store directories, restoration of brick metadata, missed restore recording for disconnected peers, and rollback/revert behavior in later chunks.
- Delete tests for single snapshot, all snapshots, and volume-scoped deletion, including decommission store status, backend remove calls, parent `snap_count` decrement, missed delete recording, and force versus non-force behavior.
- Snapshot config tests for system and per-volume hard limits, soft-limit percent range, auto-delete toggle, activate-on-create toggle, option version bump, and store persistence.
- Status/info/list tests covering all/single/volume subcommands, pending snapshots (`snap_status == -1`), deactivated snapshots, plugin `details()` failures, and dictionary key/count consistency.
- Peer partition tests where a brick-owning peer is disconnected during create/delete/restore and `missed_snap_count` plus persisted missed-snap list contents are verified.
- Boundary tests for maximum snapshot names, generated timestamp names, long brick paths, many bricks/volumes, and generated dictionary key formatting.
- Sanitizer or leak tests around dictionary value ownership, especially status strings and UUID buffers passed through `dict_set_*` calls.

## Cross-Chunk Notes

This chunk ends in the middle of `glusterd_snapshot_prevalidate()` after the delete branch begins. The remaining prevalidate branches, postvalidate dispatcher, top-level snapshot RPC entry points, missed-snapshot import parsing, restore rollback helpers, and final volume-name extraction functions are outside this chunk.

The merge lane should combine this report with later chunks for the same file before producing the final source-tree-aligned report at `Docs/researches/sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapshot.c_research.md`. This chunk provides most of the lifecycle and commit behavior, but not the file's final dispatch and recovery utilities.

### subset-b-007112: lines 8121-9479

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
