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
