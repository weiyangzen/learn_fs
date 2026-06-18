# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd.h

## Purpose

`glusterd.h` is the broad public header for the GlusterFS management daemon translator. It establishes daemon-wide constants, primary in-memory objects, path construction macros, operation identifiers, and many handler/stage/commit function prototypes used by the glusterd management, peer, volume, rebalance, quota, geo-replication, and snapshot paths.

## Important APIs, Types, and Constants

- `glusterd_op_t` enumerates management operations such as volume create/start/stop/delete, add/remove/replace brick, rebalance, heal, quota, snapshot, tier, bitrot, and scrub operations. The comment requires new operations to be appended just before `GD_OP_MAX`, making enum order part of compatibility expectations.
- `glusterd_conf_t` is daemon-private process state. It holds peer and volume lists, snapshot and missed-snapshot lists, service controllers for NFS/bitd/scrub/quotad, RPC services, port-map registry, store handles, transaction dictionaries, locks, condition variables, generation counters, worker settings, path roots (`workdir`, `rundir`, `logdir`), and host name lists.
- `glusterd_brickinfo_t` represents a brick and is the key integration type for the snapshot files in this work item. It stores host/path identity, device/origin/mount details, filesystem type, snapshot type, mount options, VG name, brick process membership, status, RPC client, store handle, and a `struct glusterd_snap_ops *snap` backend pointer.
- `glusterd_volinfo_t` represents a volume or snap volume, with persistent store handles, volume geometry, quota checksums, rebalance/replace-brick state, auth, gsync dictionaries, service sub-objects, flags such as `is_snap_volume` and `stage_deleted`, parent/snapshot identity, and the selected `snap_plugin`.
- `glusterd_snap_t`, `glusterd_snap_op_t`, and `glusterd_missed_snap_info` model snapshot objects, per-brick snapshot operations, and missed operation replay lists.
- Path macros such as `GLUSTERD_GET_VOLUME_DIR`, `GLUSTERD_GET_VOLUME_PID_DIR`, `GLUSTERD_GET_BRICK_PIDFILE`, `GLUSTERD_GET_DEFRAG_DIR`, `GLUSTERD_GET_DEFRAG_PID_FILE`, and `GLUSTERD_GET_SNAP_GEO_REP_DIR` encode the on-disk layout under glusterd work and run directories. They guard truncation by zeroing the output path when `snprintf` fails or reaches `PATH_MAX`.
- `MY_UUID` and `__glusterd_uuid()` lazily initialize and return the daemon UUID from `THIS->private`.
- Prototypes cover RPC response helpers, CLI handlers, operation stage/commit functions, rebalance functions, snapshot functions, store/recreate helpers, peer hostname update, and volume lifecycle helpers.

## Control Flow and Integration

The header does not implement operation flow directly, but it defines the vocabulary used by glusterd's state machines. RPC handlers accept `rpcsvc_request_t *`, translate CLI or peer requests into `glusterd_op_t` values and dictionaries, then route through stage and commit functions. Snapshot operations flow through `glusterd_handle_snapshot()`, `glusterd_snapshot_prevalidate()`, `glusterd_snapshot_brickop()`, `glusterd_snapshot()`, and `glusterd_snapshot_postvalidate()`, with brick-specific filesystem actions delegated through `glusterd_brickinfo_t->snap` and the `snap_plugin` stored in `glusterd_volinfo_t`.

`glusterd_conf_t` is the anchor for daemon concurrency. The daemon has a coarse `big_lock`, volume-specific lock protection through `volume_lock` and `store_volinfo_lock`, transport and import locks, condition variables for restart orchestration, and atomic flags/counters for blockers, thread count, and per-volume peer update state. Path macros are widely used before spawning daemons, writing store files, locating pid files, or addressing snap-volume directories.

## State and Persistence Behavior

Persistent state is represented by store handles in `glusterd_conf_t`, `glusterd_volinfo_t`, `glusterd_brickinfo_t`, and `glusterd_snap_t`. The fields point at glusterd's on-disk workdir tree, including `glusterd.info`, volume `info`, `quota.conf`, quota checksums, snap directories, rebalance state, pid files in the run directory, and missed snapshot lists. The header also preserves compatibility fields such as `sub_count`, restored snapshot names, and optional `origin_path`/`device_path` fields used by older snapshot metadata.

The path macros are part of the persistence contract: ordinary volumes live under `workdir/vols/<volname>`, snap volumes under `workdir/snaps/<snapname>/<volname>`, and pid paths mirror this layout under `rundir`. If these macros change, store loading, daemon restart, cleanup, and peer synchronization behavior can break.

## Dependencies

The header depends on Gluster core types from logging, syncop, events, XDR generated management interfaces, service controller headers, pmap, and glusterd state-machine definitions. It also assumes global translator context through `THIS`, UUID helpers, UST/RCU list types, POSIX pthread primitives, and `PATH_MAX`/`NAME_MAX` sizing.

## Risks and Edge Cases

- The header is extremely broad, so small structural changes have high blast radius across management RPC, store loading, snapshot backends, and volume lifecycle code.
- Several structs expose fixed-size path buffers. Callers must respect `VALID_GLUSTERD_PATHMAX`, `PATH_MAX`, and `NAME_MAX`; silently zeroed macro outputs can later become ambiguous "not found" failures.
- `GLUSTERD_REMOVE_SLASH_FROM_PATH` repeatedly calls `strlen(path)` while copying and assumes the destination is large enough for the transformed string.
- Lazy UUID initialization in `__glusterd_uuid()` relies on `THIS->private` being initialized and on UUID initialization being safe in the calling context.
- Enum ordering for `glusterd_op_t` is compatibility-sensitive because operation numbers are exchanged across management code and possibly persisted/logged.
- Locking responsibilities are distributed across many fields. Callers that mutate `glusterd_conf_t->volumes`, `glusterd_volinfo_t`, or store handles without the correct lock can race with peer import, transaction, or restart paths.

## Test Signals

Useful validation includes compile coverage for all glusterd users of the header, operation-number compatibility checks when adding enum members, path macro tests for ordinary and snap volumes near length limits, restart/store-load tests that exercise `workdir` and `rundir` layout, snapshot backend selection tests that rely on `snap_plugin`, and concurrency tests around volume list mutation and daemon restart conditions.
