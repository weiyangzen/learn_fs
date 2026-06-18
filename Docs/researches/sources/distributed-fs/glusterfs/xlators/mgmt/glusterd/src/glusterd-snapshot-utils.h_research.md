# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapshot-utils.h

## Purpose
`glusterd-snapshot-utils.h` declares the shared snapshot utility surface used by GlusterFS glusterd management code. It exposes snapshot limits, small path/UUID formatting macros, and function prototypes for snapshot metadata lookup, restore, peer synchronization, missed operation handling, quorum, snapd status reporting, backend plugin probing, and snapshot sidecar file copying.

## Important APIs, Types, And Functions
The header defines snapshot count defaults: `GLUSTERD_SNAPS_MAX_HARD_LIMIT` as `256`, `GLUSTERD_SNAPS_DEF_SOFT_LIMIT_PERCENT` as `90`, and `GLUSTERD_SNAPS_MAX_SOFT_LIMIT_PERCENT` as `100`.

`GLUSTERD_GET_SNAP_DIR(path, snap, priv)` formats `${priv->workdir}/snaps/${snap->snapname}` into a caller-supplied `PATH_MAX` buffer and clears the buffer on `snprintf()` failure or truncation. `GLUSTERD_GET_UUID_NOHYPHEN(ret_string, uuid)` converts a UUID to text with `uuid_utoa_r()` and copies it into `ret_string` while removing hyphens.

Lookup and backend declarations include `glusterd_snapshot_plugin_by_name()`, `glusterd_snapshot_probe()`, `glusterd_is_cmd_available()`, `glusterd_is_path_mounted()`, `glusterd_snap_volinfo_find()`, `glusterd_snap_volinfo_find_from_parent_volname()`, and `glusterd_snap_volinfo_find_by_volume_id()`.

Snapshot lifecycle declarations include `glusterd_snapshot_remove()`, `glusterd_bricks_snapshot_restore()`, `glusterd_snapshot_umount()`, `glusterd_snap_unmount()`, `glusterd_remove_trashpath()`, `glusterd_snap_volinfo_restore()`, `gd_restore_snap_volume()`, `glusterd_snapshot_restore_cleanup()`, `glusterd_snapobject_delete()`, `glusterd_cleanup_snaps_for_volume()`, and `glusterd_snap_brick_create()`.

Peer, missed-operation, and import/export declarations include `glusterd_missed_snapinfo_new()`, `glusterd_missed_snap_op_new()`, `glusterd_add_missed_snaps_to_dict()`, `glusterd_add_missed_snaps_to_export_dict()`, `glusterd_import_friend_missed_snap_list()`, `glusterd_add_snapshots_to_export_dict()`, `glusterd_compare_friend_snapshots()`, `gd_add_vol_snap_details_to_dict()`, `gd_add_brick_snap_details_to_dict()`, `gd_import_new_brick_snap_details()`, and `gd_import_volume_snap_details()`.

Status, ordering, config, and response helpers include `glusterd_add_snapd_to_dict()`, `glusterd_compare_snap_time()`, `glusterd_compare_snap_vol_time()`, `glusterd_snap_use_rsp_dict()`, `glusterd_snap_quorum_check()`, `glusterd_is_snapd_enabled()`, `glusterd_is_snap_soft_limit_reached()`, `gd_get_snap_conf_values_if_present()`, and `glusterd_get_snap_status_str()`.

Filesystem adjunct declarations include `glusterd_store_create_snap_dir()`, `glusterd_copy_file()`, `glusterd_copy_folder()`, `glusterd_get_geo_rep_session()`, `glusterd_restore_geo_rep_files()`, and `glusterd_copy_quota_files()`.

## Control Flow
The header does not implement control flow, but it describes how other glusterd modules compose snapshot operations. High-level command paths can validate quorum with `glusterd_snap_quorum_check()`, create or restore local backend bricks through backend-facing helpers, update or aggregate operation dictionaries with `glusterd_snap_use_rsp_dict()`, then persist or clean snapshot objects with store and lifecycle helpers.

Peer-handshake code uses the export declarations to serialize local snapshots, missed snapshot entries, volume details, and brick details into dictionaries, then uses import/compare declarations to reconcile friend state and replay missed work. Restore paths use lookup declarations to find snap volumes, restore brick and volume metadata, copy quota/geo-rep files, and clean up old snapshot or origin-volume state.

## State And Persistence Behavior
The header exposes operations over persistent glusterd state but owns no state itself. Its prototypes operate on `glusterd_snap_t`, `glusterd_volinfo_t`, `glusterd_brickinfo_t`, `glusterd_missed_snap_info`, `glusterd_snap_op_t`, `dict_t`, `xlator_t`, `uuid_t`, and `struct cds_list_head` objects defined elsewhere.

The macros affect caller-owned buffers only. `GLUSTERD_GET_SNAP_DIR()` depends on `priv->workdir` and `snap->snapname`, so it mirrors the on-disk store layout under glusterd's working directory. `GLUSTERD_GET_UUID_NOHYPHEN()` depends on the caller providing a large enough output buffer for a 32-character UUID plus null terminator.

The declared functions touch persistent store files, volfiles, missed-snapshot ledgers, brick xattrs, mount state, quota files, geo-rep files, and peer RPC dictionaries through their implementations in this and related snapshot modules.

## Dependencies And Integration Points
This header assumes the including compilation unit has access to GlusterFS management types and snapshot backend types, especially `struct glusterd_snap_ops`, `glusterd_snap_t`, `glusterd_volinfo_t`, `glusterd_brickinfo_t`, `glusterd_missed_snap_info`, `glusterd_snap_op_t`, `dict_t`, `gf_boolean_t`, `xlator_t`, `uuid_t`, and `struct cds_list_head`. It is integrated with the glusterd snapshot command implementation, store layer, volume generation layer, peer handshake path, snapd service code, geo-rep/quota/NFS-Ganesha sidecar handling, and LVM/ZFS snapshot backend plugins.

The header is also an ABI-style contract inside glusterd: many functions declared here are implemented in `glusterd-snapshot-utils.c`, while several lifecycle/backend functions such as `glusterd_snapshot_remove()`, `glusterd_bricks_snapshot_restore()`, `glusterd_snapshot_umount()`, `glusterd_remove_trashpath()`, `gd_restore_snap_volume()`, `glusterd_snapshot_restore_cleanup()`, and `glusterd_snap_brick_create()` are implemented by neighboring snapshot modules.

## Risks
`GLUSTERD_GET_SNAP_DIR()` signals truncation by clearing `path[0]`, so callers must check for an empty string before using the path. Many existing call sites rely on path lengths being valid rather than explicitly checking this macro result.

`GLUSTERD_GET_UUID_NOHYPHEN()` has no size parameter and writes into `ret_string` directly. Callers must provide at least 33 bytes and must pass a valid UUID. The macro's local variable names are protected by block scope but it still evaluates its arguments in macro context.

The declaration set is broad and mixes utilities implemented in this file with functions implemented elsewhere, which makes ownership less obvious. Callers need to know which functions mutate persistent state, which only aggregate dictionaries, and which can trigger backend mount or xattr side effects.

Several prototypes accept mutable `char *` for names, paths, and status buffers even when the implementation treats them as read-only. This weakens const-correctness and makes it easier for future call sites to pass undersized or mutable-string assumptions incorrectly.

## Test Signals
Compile-time tests should include this header from modules that already include glusterd management type definitions, ensuring all prototypes remain synchronized with implementations and no missing forward declarations are introduced.

Macro tests should exercise normal and overlong snapshot paths for `GLUSTERD_GET_SNAP_DIR()` and UUID conversion for `GLUSTERD_GET_UUID_NOHYPHEN()`, including output buffer sizing in the caller. Integration tests should cover the declared public surface through snapshot create/delete/restore/clone/config, peer attach/handshake, missed operation replay, snapd status reporting, quota and geo-rep restore, NFS-Ganesha export copy, and backend plugin probe/selection.
