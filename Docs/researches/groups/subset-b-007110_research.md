# Research: subset-b-007110

Grouped research for GlusterFS glusterd snapshot utility sources. Each source file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapshot-utils.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapshot-utils.c

## Purpose
`glusterd-snapshot-utils.c` is a large support module for GlusterFS management daemon snapshot handling. It implements shared snapshot object cleanup, snapshot volume lookup and restoration, peer-handshake import/export of snapshot metadata, missed snapshot operation replay, response-dictionary aggregation, quorum checks, snapd status reporting, mount/unmount helpers, quota/geo-rep/NFS-Ganesha file copying, soft-limit checks, and snapshot backend plugin selection/probing.

The file sits below the higher-level snapshot command state machines. It is not the CLI parser or the LVM/ZFS backend itself; instead it translates between `glusterd_snap_t`, `glusterd_volinfo_t`, `glusterd_brickinfo_t`, persistent glusterd store files, peer dictionaries, local brick mount state, and backend `glusterd_snap_ops`.

## Important APIs, Types, And Functions
Snapshot object and volume lifecycle helpers include `glusterd_snapobject_delete()`, `glusterd_cleanup_snaps_for_volume()`, `glusterd_snap_volinfo_find_by_volume_id()`, `glusterd_snap_volinfo_find()`, `glusterd_snap_volinfo_find_from_parent_volname()`, `glusterd_snap_volinfo_restore()`, `glusterd_snap_geo_rep_restore()`, `glusterd_gen_snap_volfiles()`, `glusterd_import_friend_snap()`, `glusterd_update_snaps_synctask()`, and `glusterd_compare_friend_snapshots()`. The private `glusterd_brickinfo_dup()` clones brick fields before restore-time path and xattr adjustments.

Peer metadata export/import helpers include `gd_add_brick_snap_details_to_dict()`, `gd_add_vol_snap_details_to_dict()`, `gd_import_new_brick_snap_details()`, `gd_import_volume_snap_details()`, `glusterd_add_snap_to_dict()`, and `glusterd_add_snapshots_to_export_dict()`. These functions use fixed dictionary key schemes such as `snap%d.*`, `snap%d.volcount`, `snap%d.host_bricks`, `<prefix>.snap_status`, `<prefix>.device_path`, `<prefix>.origin_path`, `<prefix>.restored_from_snap`, and `<prefix>.snap_plugin`.

Missed operation handling is centered on `glusterd_missed_snapinfo_new()`, `glusterd_missed_snap_op_new()`, `glusterd_add_missed_snaps_to_export_dict()`, `glusterd_import_friend_missed_snap_list()`, `glusterd_perform_missed_snap_ops()`, and `glusterd_perform_missed_op()`. These functions maintain `priv->missed_snaps_list`, replay pending local delete/restore work, and persist the updated missed-snapshot list with `glusterd_store_update_missed_snaps()`.

Conflict and synchronization helpers include `glusterd_is_peer_snap_conflicting()`, `glusterd_are_snap_bricks_local()`, `glusterd_peer_has_missed_snap_delete()`, `glusterd_check_peer_has_higher_snap_version()`, and `glusterd_compare_snap()`. The comparison result is written back into the peer dict with flags such as `accept_peer_data`, `remove_lvm`, and `remove_my_data`, which the synctask later consumes.

Response aggregation helpers include `glusterd_snap_use_rsp_dict()`, `glusterd_snap_create_use_rsp_dict()`, `glusterd_snap_config_use_rsp_dict()`, and `glusterd_merge_brick_status()`. They fold peer response dictionaries into a single originator dictionary, preserving snap UUIDs, soft-limit flags, missed snap entries, brick online statuses, and snapshot config display values.

Quorum functions are `glusterd_snap_quorum_check()`, private `glusterd_snap_quorum_check_for_create()`, private `glusterd_snap_quorum_check_for_clone()`, private `glusterd_snap_common_quorum_calculate()`, and private `glusterd_volume_quorum_check()`. They combine server-quorum checks via `does_gd_meet_server_quorum()` with per-brick status checks from the operation dictionary.

Local side-effect helpers include `glusterd_is_path_mounted()`, `glusterd_snap_unmount()`, `glusterd_copy_file()`, `glusterd_copy_folder()`, `glusterd_copy_quota_files()`, `glusterd_get_geo_rep_session()`, `glusterd_restore_geo_rep_files()`, `glusterd_copy_nfs_ganesha_file()`, `glusterd_restore_nfs_ganesha_file()`, `glusterd_add_snapd_to_dict()`, `glusterd_is_snapd_enabled()`, `glusterd_is_snap_soft_limit_reached()`, `gd_get_snap_conf_values_if_present()`, `glusterd_get_snap_status_str()`, `glusterd_snapshot_plugin_by_name()`, `glusterd_snapshot_probe()`, and `glusterd_is_cmd_available()`.

## Control Flow
Snapshot cleanup begins from a volume or snap object. `glusterd_cleanup_snaps_for_volume()` walks `volinfo->snap_volumes`, deletes each snap from the store, detaches and frees the `glusterd_snap_t`, deletes the snapshot volume store file, and unreferences the snap volume. It continues after individual failures because it is meant for peer-detach cleanup. `glusterd_snapobject_delete()` itself removes the snap from its list heads, destroys its lock, frees the description, and frees the object.

Snapshot restore flow starts with a snapshot volinfo and an origin/new volinfo. `glusterd_snap_volinfo_restore()` iterates every brick in the snapshot volume, allocates a new brickinfo, duplicates the stored brick fields, then either restores the original path from the peer dict when `retain_origin_path` is true or asks the selected snapshot plugin to compute a restored brick path. It imports optional brick fields from dict keys, replaces the local brick's `GF_XATTR_VOL_ID_KEY` with the origin volume id when the brick belongs to this node and is not missed, records missed restore work for pending bricks, adds the new brickinfo to the target volume, regenerates volfiles, and restores `marker.tstamp` timestamps for geo-rep indexing.

Peer handshake export walks `priv->snapshots` in `glusterd_add_snapshots_to_export_dict()`, and `glusterd_add_snap_to_dict()` serializes each snap and snap volume into a dictionary. It records whether this node hosts any snap bricks, the snap id/name/description/timestamp/restored/status fields, volume count, normal volume metadata through `glusterd_add_volume_to_dict()`, and quota configuration when quota is enabled.

Peer handshake import and reconciliation are two-phase. `glusterd_compare_friend_snapshots()` first scans the peer snapshot list and calls `glusterd_compare_snap()` for each one. `glusterd_compare_snap()` checks whether the peer has pending missed delete/restore state, whether a local snap with the same name/id exists, whether the peer snap volume version is newer, and whether either side hosts snapshot bricks. It then marks the dict for no-op, peer rejection, local data removal, LVM backend removal, and/or peer-data acceptance. After all decisions are recorded, `glusterd_compare_friend_snapshots()` launches `glusterd_update_snaps_synctask()`. The synctask serializes execution under `conf->big_lock` and `conf->restart_bricks`, removes local data when requested, and imports accepted peer snapshots with `glusterd_import_friend_snap()`.

`glusterd_import_friend_snap()` creates a new snap object, copies fields from the peer dict, skips decommissioned snapshots by removing them immediately, creates the snap directory, inserts the snap into `priv->snapshots` ordered by timestamp, imports every snap volume with `glusterd_import_volinfo()`, writes volinfo and volfiles with `glusterd_gen_snap_volfiles()`, recreates/start bricks for started snap volumes or stops/unmounts inactive ones, imports quota conf, stores the snap object, and triggers `glusterd_fetchsnap_notify()`. Error cleanup removes the partially imported snap through `glusterd_snap_remove()`.

Missed snapshot synchronization imports `missed_snap_count` entries from peer data, appends them to local memory using helper code outside this file, replays pending local delete/restore entries through `glusterd_perform_missed_snap_ops()`, and persists the updated list. `glusterd_perform_missed_op()` dispatches pending delete to `glusterd_snap_remove()` and pending restore to a full local restore sequence: find the parent volume, restore snapshot bricks, call `gd_restore_snap_volume()`, optionally remove old backend LVMs if the origin had already been restored, detach and unref the old origin volinfo, and run `glusterd_snapshot_restore_cleanup()`.

Quorum checking is called against an operation dict before snapshot create, clone, delete, or restore. Create and clone paths first require glusterd server quorum, then find the target volume or snap volume named in the dict, choose the key prefix (`vol`, `snap-vol`, or `clone`), and call `glusterd_volume_quorum_check()`. For pure distribute, two-way replicate, and non-disperse volumes it requires every brick status to be online. For larger replicate/disperse-shaped layouts it iterates distributed subvolumes and also fails when any required brick status is missing or false. Delete and restore currently require only server quorum.

File-copy side flows are direct filesystem operations. `glusterd_copy_quota_files()` copies `quota.conf` when present and requires `quota.cksum` whenever `quota.conf` exists. `glusterd_restore_geo_rep_files()` reconstructs geo-rep session directory names from snapshot secondary strings, then copies session folders from the snap geo-rep directory back into `${workdir}/geo-replication`. `glusterd_copy_nfs_ganesha_file()` copies a Ganesha export file into a snapshot directory or creates a clone export file by replacing the source volume name with the clone volume name. `glusterd_restore_nfs_ganesha_file()` copies a saved snapshot export file back to the global Ganesha export directory when it exists.

## State And Persistence Behavior
The primary in-memory state is `glusterd_conf_t` from `THIS->private`, especially `priv->snapshots`, `priv->missed_snaps_list`, `priv->opts`, `priv->workdir`, `priv->big_lock`, `priv->cond_restart_bricks`, and `priv->restart_bricks`. Snapshot objects own list links, locks, ids, names, status, description, timestamp, restored state, and child snap volumes. Snapshot volumes and bricks carry parent volume names, backend plugin names, snap statuses, device paths, mount paths, origin paths, fstype, mount options, and local-node UUID membership.

Persistent glusterd store state is updated through `glusterd_store_delete_snap()`, `glusterd_store_delete_volume()`, `glusterd_store_volinfo()`, `glusterd_store_snap()`, `glusterd_store_create_snap_dir()`, and `glusterd_store_update_missed_snaps()`. Volfile persistence is regenerated by `generate_brick_volfiles()`, `generate_client_volfiles()`, and `glusterd_create_volfiles_and_notify_services()`.

Filesystem state outside the store includes brick mount points, `/etc/mtab`, backend snapshot mounts, `GF_XATTR_VOL_ID_KEY` xattrs on brick paths, `marker.tstamp` files under volume store directories, quota files, geo-rep session directories, and NFS-Ganesha export files under `CONFDIR "/exports"`. `glusterd_snap_unmount()` calls backend plugin `deactivate()` and retries failed unmounts three times.

Dictionary state is a major transient persistence boundary across RPC and peer handshakes. The code assumes stable string key formats for snapshots, volumes, bricks, status flags, missed operations, quota config, snapd pseudo-bricks, and config display data. Many operations return success with optional fields absent but fail on required fields missing.

## Dependencies And Integration Points
This module depends on Gluster's dictionary, syscall wrapper, UUID, logging, memory, list, and synchronization APIs. It integrates with `glusterd-op-sm`, `glusterd-utils`, `glusterd-store`, `glusterd-volgen`, snapd service helpers, snapd service management, server quorum checks, error codes, and message ids.

The snapshot backend integration point is `struct glusterd_snap_ops`; this file selects `lvm_snap_ops` or `zfs_snap_ops`, probes them, calls plugin `brick_path()` during restore path computation, and calls plugin `deactivate()` during unmount. The actual snapshot create/delete/restore backend work lives elsewhere.

Peer integration happens through export/import dictionaries during friend handshakes. The module shares snapshot metadata with other glusterd peers, reconciles conflicts based on snap ids, snap volume versions, local brick hosting, and missed-operation ledgers, and launches a synctask for state-changing imports/removals.

CLI and operation-machine integration happens through response-dict aggregation, snapshot quorum checking, soft-limit reporting, and status formatting. Snapd integration exposes a snapd pseudo-brick entry with hostname `Snapshot Daemon`, UUID path, port, pid, and running status.

Geo-replication, quota, and NFS-Ganesha integrations are file-level adjuncts to snapshot create/restore/clone operations. They copy or restore sidecar configuration so a restored or cloned volume keeps the expected geo-rep, quota, and export behavior.

## Risks
`glusterd_snapshot_plugin_by_name()` does not set `*snap_ops` for unknown plugin names, but callers such as restore and unmount dereference the returned pointer. Bad or empty `snap_plugin` state can therefore become a null or stale function-pointer crash unless validated before call sites.

Several fixed-size buffers are populated with `strcpy()` or `sprintf()` on struct fields and status strings. Many source and destination arrays are Gluster fixed path/name fields, but safety depends on upstream invariants. The status formatter requires the caller to provide enough space and does not use a bounded write.

`glusterd_copy_folder()` copies only regular file paths by calling `glusterd_copy_file()` for every directory entry. It does not recursively create directories, preserve ownership, copy symlinks as symlinks, or remove stale destination files. This is probably enough for the geo-rep sidecar layout it expects, but it is not a general directory copy primitive.

`glusterd_copy_file()` treats short writes as failure but does not retry partial writes; it also returns the last read result, so a successful copy usually returns `0` after EOF. It uses source permission bits but does not preserve ownership, timestamps, xattrs, or fsync durability.

`glusterd_get_geo_rep_session()` parses geo-rep secondary strings with `strtok_r()` and assumes the documented `primary_node_uuid:ssh://secondary_host::secondary_vol:secondary_voluuid` shape. Malformed strings cause failure, and the check after `secondary_temp = gf_strdup(token)` mistakenly tests `secondary` rather than `secondary_temp`, which can miss an allocation failure.

Snapshot peer reconciliation is sensitive to dict key correctness and version semantics. `glusterd_compare_snap()` initially calls `dict_set_uint32(peer_data, buf, 0)` before `buf` is populated, which may attempt to set an empty key before setting the intended flags. The conflict algorithm also has a single-volume snapshot assumption in `glusterd_check_peer_has_higher_snap_version()`.

Missed operation replay mutates important state and persists even after partial progress. Failures during replay deliberately still flow toward store update in some cases, so tests need to verify idempotence and correctness after interrupted delete/restore work.

`glusterd_snap_unmount()` frees only the last `brick_mount_path` pointer after the loop; repeated local bricks can leak earlier allocated mount path strings if `glusterd_find_brick_mount_path()` allocates each time. The function also returns the last plugin deactivate result, so volumes with no local eligible bricks may leave `ret` as `-1`.

Quorum checking uses dictionary brick status keys generated elsewhere. Missing or stale status keys are treated as brick-down, which is conservative but can fail operations if aggregation and key-prefix conventions drift.

## Test Signals
Unit-level tests should cover snapshot object deletion with null and valid objects, snap volume lookup by name, parent name, and volume id, brickinfo duplication, status string formatting for every `GD_SNAP_STATUS_*`, plugin lookup for LVM/ZFS/unknown names, command availability for missing/non-regular/non-executable/executable paths, mount detection against controlled mtab data, and `glusterd_mntopts_exists()` token matching.

Restore tests should cover `retain_origin_path` true and false, plugin `brick_path()` output, local versus remote bricks, pending brick `snap_status == -1`, xattr replacement success/failure, missed restore dict entries, volfile regeneration failure, and geo-rep marker timestamp restoration when `VKEY_MARKER_XTIME` is enabled/disabled/missing.

Peer handshake tests should construct peer dictionaries with matching snaps, missing snaps, same-name/different-id conflicts, newer peer snap-volume versions, local-only hosted bricks, peer-hosted bricks, both-hosted conflicts, decommissioned snapshots, quota-enabled snap volumes, and started/stopped snap volumes. Verify resulting dict flags, synctask import/removal behavior, store writes, volfile generation, brick start/stop, unmount calls, and notification.

Missed snapshot tests should import/export missed snap lists, replay pending delete and restore entries only for `MY_UUID`, skip create/done entries, mark all entries for the same snap done after one successful replay, persist partial progress, and remain idempotent across repeated peer handshakes.

Response aggregation tests should cover create/delete/clone/config/default command types, merging missed snap counts from multiple sources, preserving snap UUID and soft-limit flags, delete skipping brick status merge, clone versus snap-volume status key prefixes, and config display aggregation for system limits and per-volume limits.

Quorum tests should cover server quorum failure, create/clone/delete/restore command dispatch, pure distribute, replica count two, replica count three, disperse, distributed subvolume status calculations, missing brick status keys, and correct `op_errstr`/`op_errno` values.

Filesystem side-effect tests should cover quota file absence/presence, missing `quota.cksum`, copy permission propagation, partial write/read failures, NFS-Ganesha source snapshot versus origin volume, clone export name replacement, optional restore when export file is absent, geo-rep secondary parsing with `root@host`, malformed secondary strings, and copy-folder behavior with nested entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapshot-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapshot-utils.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapshot-utils.h -->
