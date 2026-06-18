# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-utils.c lines 1-8647

Chunk id: `subset-b-007115`
Source: `sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-utils.c`
Line range: 1-8647 of 12989

## Purpose

This chunk contains most of GlusterD's shared management utility layer for cluster locks, RPC message submission, volume and brick object lifecycle, peer volume export/import, brick process start/stop, brick multiplexing, local brick validation, geo-replication restart, statedump signaling, quota-conf import/export, and service cleanup after peer detach. It sits behind higher-level operation state machines and translates in-memory `glusterd_*` objects into persisted store files, generated volfiles, on-wire dictionaries, and local daemon processes.

The code is not a narrow helper file: it owns several critical state transitions for `glusterd_volinfo_t`, `glusterd_brickinfo_t`, `glusterd_brick_proc_t`, `glusterd_rebalance_t`, and service connection objects. It also mediates between cluster metadata consensus and host-local effects such as xattrs, pidfiles, sockets, mount table reads, external command execution, and RPC connections.

## Important APIs, Types, and Functions

- `glusterd_defrag_ref`, `glusterd_defrag_unref`, `glusterd_defrag_rpc_get`, and `glusterd_defrag_rpc_put` manage refcounts and RPC references for `glusterd_defrag_info_t` under its lock.
- `is_brick_mx_enabled`, `get_mux_limit_per_process`, and `get_gd_vol_thread_limit` read `priv->opts` for brick multiplexing and volume dictionary fan-out limits, including compile-time `GF_ENABLE_BRICKMUX` defaulting.
- `glusterd_lock`, `glusterd_unlock`, `glusterd_get_lock_owner`, and the static `glusterd_lock_t lock` implement a single in-process cluster-operation lock owner by UUID.
- `glusterd_submit_request`, `glusterd_serialize_reply`, and `glusterd_submit_reply` allocate iobuf/iobref objects, XDR-encode payloads, and submit client/server RPCs.
- `glusterd_volinfo_new`, `glusterd_volinfo_ref`, `glusterd_volinfo_unref`, `glusterd_volinfo_delete`, and `glusterd_volinfo_remove` allocate, initialize, reference, destroy, and unlink volume objects. Initialization builds snapd, gfproxyd, and shd service members and dictionaries for options and geo-replication secondaries.
- `glusterd_brickinfo_new`, `glusterd_brickinfo_delete`, `glusterd_brickprocess_new`, `glusterd_brickprocess_delete`, `glusterd_brick_process_add_brick`, and `glusterd_brick_process_remove_brick` maintain brick metadata and the brick-multiplex process list.
- `glusterd_brickinfo_new_from_brick`, `glusterd_resolve_brick`, `glusterd_volume_brickinfo_get`, and `glusterd_volume_brickinfo_get_by_brick` parse `host:/path` strings, canonicalize paths, resolve hostnames to UUIDs, and find matching bricks.
- `glusterd_validate_and_create_brickpath`, `glusterd_check_and_set_brick_xattr`, `glusterd_is_path_in_use`, and `glusterd_new_brick_validate` enforce local brick directory, mount, root-partition, xattr, and peer-connectivity rules.
- `glusterd_volume_start_glusterfs`, `glusterd_brick_start`, `attach_brick`, `send_attach_req`, `glusterd_volume_stop_glusterfs`, and `glusterd_brick_stop` are the core local brick daemon start, attach, detach, terminate, and connect paths.
- `find_compat_brick_in_vol` and `find_compatible_brick` implement brick multiplex placement by checking UUID locality, volume option compatibility, shared-storage restrictions, process brick count limits, pmap sign-in state, pidfiles, and socket readiness.
- `glusterd_add_volume_to_dict`, `glusterd_add_volumes_to_export_dict`, `glusterd_compare_friend_data`, `glusterd_import_volinfo`, `glusterd_import_friend_volume`, and `glusterd_import_friend_volumes_synctask` implement peer metadata synchronization using version/checksum comparison and dictionary import/export.
- `glusterd_vol_add_quota_conf_to_dict` and `glusterd_import_quota_conf` serialize quota GFID entries and checksums into peer dictionaries and reconstruct `quota.conf` stores.
- `glusterd_compute_cksum`, `glusterd_volume_compute_cksum`, `get_checksum_for_file`, and `glusterd_sort_and_redirect` compute stable volume info and quota checksums, sorting normal volume info before checksum generation.
- `glusterd_restart_bricks`, `glusterd_spawn_daemons`, `glusterd_restart_gsyncds`, and `_local_gsyncd_start` restart bricks, geo-replication sessions, rebalance, snapd, gfproxyd, and shd after glusterd restart or metadata import.
- `glusterd_add_brick_detail_to_dict`, `glusterd_add_brick_to_dict`, `glusterd_get_brick_root`, `glusterd_get_mnt_entry_info`, `glusterd_get_brick_mount_device`, and `glusterd_add_inode_size_to_dict` populate CLI/status dictionaries with capacity, inode, mount, fs, device, pid, port, and online-state details.
- `glusterd_brick_statedump`, `glusterd_brick_terminate`, `glusterd_nfs_statedump`, `glusterd_quotad_statedump`, and `glusterd_set_dump_options` write statedump option files and signal local daemons.
- `glusterd_friend_remove_cleanup_vols` removes volumes fully owned by a detached peer and reconfigures daemon services.
- `glusterd_get_trusted_client_filepath`, `glusterd_get_dummy_client_filepath`, and the beginning of `glusterd_volume_defrag_restart` generate client volfile paths and begin rebalance restart handling.

## Control Flow

Cluster RPC helpers encode requests and replies through the Gluster iobuf/iobref and XDR stack. `glusterd_submit_request` serializes a request when present, creates an iobref if the caller did not provide one, submits through `rpc_clnt_submit`, and deliberately returns success after submission to avoid double-destroying frames when later RPC-layer failures race with callbacks. `glusterd_submit_reply` mirrors this for service replies.

Volume lifecycle starts in `glusterd_volinfo_new`, which allocates zeroed state, initializes linked lists, dictionaries, service wrappers, locks, store mutexes, and an atomic refcount. `glusterd_volinfo_unref` decrements under `conf->volume_lock` and calls `glusterd_volinfo_delete` at zero. Delete tears down brick lists, dictionaries, service connections, store handles, auth fields, shd process state, mutexes, and locks.

Brick creation and validation flow from parsing to local filesystem mutation. `glusterd_brickinfo_new_from_brick` splits a brick string into hostname and path, canonicalizes the path, optionally resolves the host UUID, and records a realpath for local bricks when available. `glusterd_new_brick_validate` rejects local paths that contain or are contained by existing bricks and rejects remote peers that are missing, disconnected, or not befriended. `glusterd_validate_and_create_brickpath` creates the directory, validates that it is a directory, rejects paths under the glusterd workdir, warns/rejects mountpoint or root-partition usage unless forced or partition warnings are ignored, sets volume-id xattrs, and creates `.glusterfs`.

Local brick start in `glusterd_brick_start` first resolves the brick UUID and no-ops for remote bricks. It suppresses duplicate attempts when the brick is already starting, `start_triggered` is set, or the volume is in peer-update. It verifies the backend `trusted.glusterfs.volume-id` xattr before launching non-snapshot bricks. If an existing pidfile points to a running process, brick-multiplex mode additionally proves that the process has the requested brick path open and extracts the management socket from `/proc/<pid>/cmdline` or FreeBSD process APIs. Existing processes are connected and added to brick-process accounting. If no suitable process exists, it creates the run directory, tries to attach to a compatible brick process, and falls back to `glusterd_volume_start_glusterfs`.

`glusterd_volume_start_glusterfs` constructs the `glusterfsd` command line. It assigns TCP/RDMA ports with pmap helpers, removes stale sockets and old RPC clients, computes volfile IDs and log paths, adds valgrind options when requested, applies snapshot-specific volume IDs and disables snapshot health/changelog behavior, adds transport and bind-address options, enables memory accounting and brick-mux flags, and then runs the process synchronously or asynchronously. On success it creates a `glusterd_brick_proc_t`, links the brick into the process, and connects over the hashed Unix socket path.

Brick multiplex attach flow uses `find_compatible_brick` to search the same volume, other regular volumes, or snapshot volumes. Compatibility excludes shared-storage mismatches and compares all unsafe options in both directions while allowing auth, event-thread, diagnostics log, and user options. `find_compat_brick_in_vol` enforces per-process brick count limits, same local UUID, started/starting status, pmap registration, pidfile liveness, and service-running checks. `attach_brick` builds the target volfile path, sends `GLUSTERD_BRICK_ATTACH`, binds the new brick path to the existing port, and updates brick-process accounting. `attach_brick_callback` copies the pidfile from the already-running brick on success, marks status started, and references the other brick's RPC; on failure it resets status/port, removes process accounting, and stores volinfo.

Brick stop goes through `glusterd_brick_stop` for local filtering and then `glusterd_volume_stop_glusterfs`. The stop path removes the brick from its brick process, optionally unlinks it from the volume list, then either sends a detach/terminate RPC for multiplexed or graceful-cleanup cases or sends `SIGTERM` through `glusterd_brick_terminate`. It disconnects RPC, removes pmap entries when needed, unlinks pidfiles, marks the brick stopped, clears `start_triggered`, and optionally deletes brick store/volfile metadata.

Peer synchronization exports local volume state with `glusterd_add_volumes_to_export_dict`. It can populate one dictionary directly or spawn detached worker threads to fill per-range dictionaries when a volume-per-thread limit is configured, then serializes them into a single dict buffer. Each volume export includes identity, topology counts, versions, status, checksums, transport, stage-delete flag, snapshot details, auth, rebalance state/dict, volume options, geo-rep secondaries, brick/TA-brick metadata, op versions, and quota xattr version. Quota-enabled volumes also export quota GFIDs, types, version, and checksum.

Peer comparison starts in `glusterd_compare_friend_data`. It imports newer global options first, then compares each remote volume by name, version, checksum, quota version, and quota checksum. Newer remote versions set `volpeerupdate` and mark bits in `status_arr`; checksum mismatches reject the comparison. If any update is needed, an async synctask imports the marked volumes under `conf->big_lock`, guarded by `conf->restart_bricks` so imports do not race brick restarts.

Volume import reconstructs `glusterd_volinfo_t` from dictionary keys, with backward compatibility for missing topology fields, rebalance IDs, rebalance ops, op versions, and decommissioned flags. `glusterd_import_friend_volume` replaces stale local volumes only when the incoming version is newer. It refs the old volume, disconnects or preserves rebalance state, copies brick ports and `real_path`, stops stale bricks, deletes stale stores/bricks, stores the new volinfo, regenerates volfiles, starts bricks/services if the volume is started, imports quota config, and notifies fetchspec listeners.

Restart control in `glusterd_restart_bricks` serializes against imports via `conf->restart_bricks`, increments `conf->blockers`, checks server quorum, starts or stops bricks for started normal and snapshot volumes, persists volinfo after restart attempts, and starts shared services when needed. `glusterd_spawn_daemons` chains brick, geo-rep, rebalance, snapd, gfproxyd, and shd restart helpers.

Geo-rep restart walks `volinfo->gsync_secondaries`. `_local_gsyncd_start` derives local brick paths, parses secondary URL pieces, builds the per-session config path, resolves status/state files, skips sessions that were created/stopped/corrupt or missing required config entries, handles paused sessions specially, records active secondaries, and invokes `glusterd_start_gsync`. `glusterd_start_gsync` first sets the `session-owner` using `gsyncd --config-set`, then starts monitor mode with `--glusterd-uuid`, unlocking `big_lock` while running external commands.

Status/detail dictionary generation combines live process checks and filesystem inspection. `glusterd_add_brick_to_dict` reports host, path, UUID, TCP/RDMA ports, pid, and online status, with extra brick-path verification under multiplexing. `glusterd_add_brick_detail_to_dict` reports `statvfs` capacity/inode values, mount device/type/options, and inode size from `xfs_info` or `tune2fs` when applicable.

## State and Persistence Behavior

- In-memory cluster state is anchored in `glusterd_conf_t` lists: `priv->volumes`, `priv->snapshots`, `priv->brick_procs`, hostname caches, and global option dicts.
- `glusterd_volinfo_t` carries persistent fields such as name, topology, versions, checksums, auth, geo-rep dictionaries, quota checksums/versions, rebalance metadata, brick lists, snapshot membership, and service handles.
- `glusterd_brickinfo_t` stores host/path/UUID, `real_path`, pid/log/socket-derived state, pmap ports, status, start flags, snapshot status, RPC client, brick-process membership, and a restart mutex.
- Store persistence is handled through `glusterd_store_volinfo`, `glusterd_store_delete_volume`, `glusterd_store_delete_brick`, `glusterd_store_save_quota_version_and_cksum`, and store handle temp/rename functions. This chunk calls those APIs but does not define most store internals.
- Volume checksums are persisted in `GLUSTERD_CKSUM_FILE`; quota checksums use `GLUSTERD_VOL_QUOTA_CKSUM_FILE`. Normal volume info is sorted before checksum so line ordering does not create false mismatches.
- Quota config import writes a temp quota-conf file through `gf_store_mkstemp`, writes the header and GFID records, renames it atomically, computes checksum, and stores checksum/version metadata. Failure unlinks temp paths and destroys quota handles.
- Brick start/stop depends on pidfiles under the volume run directory, hashed Unix socket paths under `GLUSTERD_SOCK_DIR`, and pmap port registrations. Multiplex attach copies pidfiles from the parent brick process.
- Brick membership on disk is enforced with `GF_XATTR_VOL_ID_KEY`, while `GFID_XATTR_KEY` and volume-id xattrs are used to reject brick paths already inside a Gluster volume unless `force` allows overwrite.
- Geo-rep restart depends on `gsyncd.conf`, status files, state files, and `volinfo->gsync_secondaries`/`gsync_active_secondaries`.
- Statedumps write transient `DEFAULT_VAR_RUN_DIRECTORY/glusterdump.<pid>.options` files, send `SIGUSR1`, sleep briefly, then unlink the options file.
- Peer import can replace a whole local volume object. It intentionally copies live-only fields such as brick ports and real paths from the old object before deleting stale brick/store metadata, then persists the new volume and regenerates volfiles.

## Dependencies and Integration Points

- Gluster core libraries: `dict_t`, `data_t`, `iobuf`, `iobref`, XDR helpers, RPC client/server APIs, runner APIs, locks, atomics, list macros, UUID helpers, logging/events, `gf_store_*`, and compatibility syscall wrappers.
- GlusterD modules: operation state machine, peer management, store, geo-replication, snapshot utilities, service helpers, server quorum, shd service helpers, quota utilities, and protocol utilities.
- External daemons/tools: `glusterfsd`, `gsyncd`, `valgrind`, `xfs_info`, `tune2fs`, `pmap_unset`, and OS process/mount table interfaces.
- OS resources: `/dev/fuse` or `/dev/puffs`, `/proc/<pid>/cmdline`, `/proc/<pid>/fd`, mount table via `_PATH_MOUNTED`, xattrs, pidfiles, Unix sockets, signals, directories, and temporary files.
- Cluster protocols: peer probe/sync dictionaries, brick management RPC program `gd_brick_prog`, pmap port binding/signout, fetchspec notifications, and service manager callbacks for snapd/gfproxyd/shd/NFS/quotad.
- Snapshot integration: snapshot volumes get special volfile IDs, parent volume IDs, read-only translator options, snapshot details in dictionaries, and stale restored snapshot cleanup.
- Quorum integration: brick restarts check server quorum and may stop bricks when quorum is not met.

## Risks and Edge Cases

- The global `glusterd_lock_t lock` is a simple static owner slot with TODO timestamp handling; it is not persisted and depends on callers for process-level synchronization.
- Many paths depend on `PATH_MAX` and `snprintf` checks. Most are guarded, but some intermediate `snprintf` return values are overwritten or used only for best-effort logging.
- `glusterd_submit_request` intentionally masks submit failures after `rpc_clnt_submit` to avoid double frame destruction; callers must rely on callbacks or RPC-layer handling for late failures.
- Brick multiplexing is explicitly race-prone: comments describe stale sockets/RPC objects, pidfile readiness assumptions, pmap sign-in timing, and retry loops that temporarily unlock `big_lock`.
- `find_compat_brick_in_vol` compares option dictionaries by current values only. Comments note that option changes for already-colocated non-snapshot bricks are not fully addressed.
- `glusterd_brick_start` trusts xattrs and process inspection to identify valid existing bricks. Stale pidfiles, missing socket files, process command-line parsing, and multiplexed processes can produce false negatives and cleanup.
- `search_brick_path_from_proc` uses `/proc/<pid>/fd` symlink matching on Linux and FreeBSD procstat APIs. Permission issues or disappearing processes can make a running brick look absent.
- `glusterd_get_sock_from_brick_pid` parses command-line strings for `-S` and `--brick-name`, which is fragile if invocation formatting changes.
- Peer import failure paths can leave newly allocated `new_volinfo` not fully linked or cleaned in every branch; callers depend heavily on store/import conventions and process lifetime.
- `glusterd_compare_friend_data` allocates a variable-size `status_arr` based on count but uses bit arithmetic across 64-volume groups; off-by-one errors here would import the wrong volume.
- `glusterd_dict_arr_serialize` merges dicts by direct member traversal and unrefs all array dicts, including the ref to `peer_data` added by the caller. Ownership is subtle.
- `compute_checksum` has legacy behavior differences before `GD_OP_VERSION_5_4`; compatibility requires preserving old checksum semantics even if they process fixed buffer sizes.
- Brick path validation removes newly created directories on failure, but only when this function created the path. Existing path mutations such as test xattr setting/removal or forced volume-id overwrite still have side effects.
- `glusterd_is_path_in_use` walks parent directories using `dirname` on a mutable buffer and reports xattr errors through `keys[i]`; error reporting could be fragile if the loop exits with unexpected `i`.
- Statedump helpers read pidfiles and call `kill` without confirming the process identity beyond the pidfile. They guard against pid zero but not pid reuse.
- `_local_gsyncd_start` unlocks around external commands indirectly through `glusterd_start_gsync`; config/state-file interpretation determines whether sessions resume, pause, or mark config corrupt.
- Static `cached_fs` in `glusterd_add_inode_size_to_dict` is process-global and not visibly synchronized in this chunk.

## Test Signals

- Brick creation tests should cover local path creation, pre-existing non-directory paths, paths under glusterd workdir, mountpoint/root-partition rejection and force overrides, xattr unsupported filesystems, parent path already containing Gluster xattrs, and cleanup of newly created paths on failure.
- Brick start tests should exercise missing/mismatched volume-id xattrs, remote bricks no-op behavior, stale pidfile cleanup, missing socket detection, RDMA/TCP/BOTH port assignment, valgrind mode, snapshot brick options, and `only_connect`.
- Brick multiplex tests should cover attach success, attach callback pidfile copy/RPC ref, attach failure cleanup/store update, process limit enforcement, option mismatch in both dictionary directions, shared-storage isolation, pmap not-yet-registered retries, stale starting bricks, and graceful detach.
- Peer sync tests should compare same-version checksum match, checksum rejection, newer remote version update, stage-deleted remote volume skip, quota version/checksum mismatches, missing old-version keys, global option version import, and quorum-ratio-triggered brick restart.
- Import tests should verify stale volume replacement preserves live brick ports/real paths, stops removed bricks, disconnects old RPCs, preserves/migrates snapshot child lists, imports quota conf atomically, regenerates volfiles, and starts services for started volumes.
- Checksum tests should include sorted normal volume info, quota conf behavior before and after op-version 7.0, short reads, temp-file cleanup, and compatibility with the fixed-size pre-5.4 checksum path.
- Geo-rep restart tests should cover Created/Stopped/Paused/Config Corrupted statuses, missing state-file or pid-file template entries, invalid secondary URLs, active-secondary dict rollback on start failure, and lock release around `gsyncd`.
- Status/detail tests should cover `statvfs` failure, mount table lookup, dynamic inode filesystems, missing `xfs_info`/`tune2fs`, cached inode size reuse, multiplex brick online detection by open fd, and RDMA port reporting.
- Signal/statedump tests should cover malformed option prefixes for NFS/quotad, duplicate NFS option handling, pidfile missing/unreadable, pid zero refusal, option-file cleanup, and pid reuse risk if feasible.
- Concurrency tests should stress `conf->restart_bricks` exclusion between import and restart, `conf->blockers` callback signaling, volume ref/unref deletion under `volume_lock`, and detached dictionary population thread completion.

## Cross-Chunk Notes

This chunk ends inside `glusterd_volume_defrag_restart`; the remainder of defrag/rebalance restart and later utility functions are in `subset-b-007116`. Final whole-file synthesis should connect this chunk's rebalance state copying/import behavior with the later defrag startup and cleanup logic.
