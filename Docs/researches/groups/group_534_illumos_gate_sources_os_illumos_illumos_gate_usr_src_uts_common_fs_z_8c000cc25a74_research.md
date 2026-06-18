# Group Research: group_534_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_8c000cc25a74

Scope: `Docs/research_subset_a.md`  
Repository: `/home/sansha/Github/learn_fs`  
Files read completely: 4

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_ioctl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_ioctl.c

Implements the illumos ZFS `/dev/zfs` ioctl control plane and module driver entry points. It is the central kernel dispatcher for pool administration, dataset administration, send/receive, properties, delegation, snapshots/bookmarks/holds, encryption keys, sharing, fault injection, zvol forwarding, and control-device cleanup state.

Key elements:
- Defines the modern ioctl registration model with `zfs_ioc_vec_t`, `zfs_ioctl_register()`, per-command input-key schemas, name checking, pool-state checking, optional history logging, and output-nvlist smushing.
- Preserves legacy ioctl support through `zfs_ioc_legacy_func_t` handlers and registration helpers for pool, dataset read, dataset modify, and metadata commands.
- Provides broad security-policy functions for global-zone versus local-zone visibility, delegated dataset permissions, pool configuration privilege, share ACL checks, snapshot/bookmark/hold/release permissions, send/receive permissions, encryption key permissions, and labeled-system MLS label rules.
- Handles nvlist copyin/copyout with `get_nvlist()`, `put_nvlist()`, `nvlist_smush()`, and `zfs_check_input_nvpairs()`.
- Implements pool operations including create, destroy, import/export, tryimport, stats/config listing, scrub/scan, freeze, upgrade, reguid, sync, checkpoint/discard checkpoint, initialize, trim, wait, clear, and reopen.
- Implements vdev operations including add, remove/cancel remove, online/offline/fault/degrade, attach, detach, mirror split, set path, and set FRU.
- Implements dataset operations including create, clone, destroy, rename, rollback, promote, remap, object-to-path/stats, dataset/snapshot listing, properties, received properties, ZPL properties, delegated ACLs, quotas, userspace accounting upgrades, temporary snapshots, and diffs.
- Implements snapshot/bookmark/hold operations through `dsl_dataset_snapshot()`, destroy snapshot nvl handling, bookmark create/get/destroy, user holds, user releases, and cleanup-fd support through `zfs_onexit`.
- Implements send/receive entry points, including legacy and nvlist send APIs, send-space estimation, send progress, resumable receive, delayed receive properties, local property overrides, received-property clearing/restoration, hidden encryption args, and cleanup action handles.
- Implements encryption key ioctls for load, unload, and change-key using `dsl_crypto_params_create_nvlist()` and SPA keystore calls.
- Implements NFS/SMB sharing and SMB ACL resource-file management, dynamically resolving sharefs/NFS/SMB symbols.
- Defines `/dev/zfs` driver entry points, control-device clone-open minor allocation, control-device close cleanup, zvol delegation for non-control minors, and module `_init`, `_fini`, and `_info`.

Main dependencies and interactions:
- Bridges userland `zfs`, `zpool`, and `libzfs_core` requests to SPA, DSL, DMU, ZPL, zvol, ZIL, delegation, crypto, vdev, scan, trim, initialize, checkpoint, send/receive, bookmark, and user-hold subsystems.
- Uses `zfs_onexit.c` for per-control-device callbacks used by temporary holds and resumable receive state.
- Uses ZPL helpers from `zfs_vfsops`, `zfs_znode`, `zfs_dir`, `zfs_ctldir`, and `zvol` when operations affect mounted filesystems or zvol device minors.
- Uses nvlist contracts from `sys/zfs_ioctl.h`; new ioctls are expected to declare acceptable input keys and use `zfsdev_ioctl()` validation before handler dispatch.
- Uses `spa_history_log_nvl()` or legacy history strings to record state-changing operations when registration allows logging.
- Shares special property behavior with DSL/DMU/ZPL code: quotas and reservations go through DSL setters, volsize through zvol, ZPL version through mounted/unmounted zfsvfs handling, keylocation through crypto validation, and userquota through mounted zfsvfs quota routines.

Implementation notes:
- The file contains both old `zfs_cmd_t` field-based ioctls and newer nvlist-based ioctls. The top-level dispatcher enforces names, pool state, secpolicy, and input shape before invoking modern handlers.
- Pool-state checks reject operations on suspended pools with `EAGAIN` or readonly pools with `EROFS` according to command registration flags.
- Zone checks intentionally return `ENOENT` for datasets not visible in a local zone, avoiding information disclosure.
- Some property-setting operations are best effort: `zfs_set_prop_nvlist()` records per-property errors, retries selected failures, batches generic DSL property updates, and then falls back to individual sets.
- Receive property handling is failure-aware: it stashes original received/local props, clears old received props, extracts delayed properties such as `refquota` and `keylocation`, restores prior state on receive failure, and reports `ZPROP_ERR_*` flags when clearing/restoration cannot be guaranteed.
- Snapshot unmounting is best effort and forced for snapshot vfs instances; destroy, promote, rollback, and recursive snapshot rename paths use this to avoid mounted snapshot conflicts.
- The control device allocates clone minors for `O_EXCL` opens; these minors carry `zfs_onexit_t` lists and are destroyed on close, firing registered callbacks.
- The module initialization order is SPA, ZFS, zvol, ioctl registration, module install, TSD creation, LDI identity, and share lock setup; teardown refuses to unload when pools, ZFS mounts, zvols, or injection state are busy.

Risk/attention points:
- This file is an ABI and policy choke point. Adding or changing ioctls requires stable ioctl numbers, explicit nvlist key schemas, permission checks, pool-state flags, and history-log behavior.
- Legacy handlers can mutate `zc_name`, so `zfsdev_ioctl()` snapshots the pool name before dispatch for later history-log TSD use.
- Several code paths read objset contents without full ownership and document that as an existing compromise for stats/ZPL property access.
- Receive and property paths are particularly sensitive to partial failure: callers may observe both an errno and an output nvlist of per-property errors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_log.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_log.c

Builds ZFS Intent Log records for filesystem namespace, data, attribute, and ACL operations. The functions are called while a DMU transaction is active; in normal operation they allocate and assign in-memory intent transactions, while replay mode suppresses new logging.

Key elements:
- `zfs_log_create_txtype()` maps create kind plus ACL/xvattr presence to ZIL transaction types such as `TX_CREATE`, `TX_CREATE_ACL_ATTR`, `TX_MKDIR_ATTR`, and `TX_MKXATTR`.
- `zfs_log_xvattr()` packs requested extended attributes, create time, AV scanstamp or project ID, and attribute flags into a ZIL `lr_attr_t` payload.
- `zfs_log_fuid_ids()` and `zfs_log_fuid_domains()` append FUID and domain replay data.
- `zfs_log_create()` logs file, directory, xattr-directory, ACL-create, and xvattr-create records, including object ID, dnode slot count, mode, UID/GID/FUID, generation, create time, rdev, ACL data, FUID data, and name.
- `zfs_log_remove()` logs remove/rmdir and purges async write records for unlinked objects to avoid stale object-id reuse leaks.
- `zfs_log_link()`, `zfs_log_symlink()`, and `zfs_log_rename()` log namespace link, symlink, and rename operations.
- `zfs_log_write()` logs writes as indirect, copied, or need-copy records based on log bias, slog availability, write size, and commit semantics.
- `zfs_log_truncate()` logs file space truncation/free operations.
- `zfs_log_setattr()` logs setattr payloads, including xvattr and FUID domain data when needed.
- `zfs_log_acl()` logs legacy ACL v0 records for old ZPL versions or modern FUID-aware ACL records for newer filesystems.

Main dependencies and interactions:
- Paired with `zfs_replay.c`, whose replay vector interprets these record layouts.
- Depends on znode state, SA attributes, vnode attributes, ACL structures, FUID structures, DMU reads, ZIL intent transaction allocation, and SPA slog/log-bias state.
- Called by ZPL vnode/directory operations after metadata/data mutation decisions have been made.

Implementation notes:
- All public logging helpers immediately return when `zil_replaying(zilog, tx)` is true; replayed operations update replay state instead of recursively logging.
- Create records encode dnode slot count into high bits of `lr_foid` with `LR_FOID_SET_SLOTS()`, preserving large-dnode replay.
- `zfs_log_write()` splits indirect writes on block boundaries and limits copied payloads to `ZIL_MAX_COPIED_DATA`; failed immediate data reads fall back to `WR_NEED_COPY`.
- `itx->itx_sync` is set for write/truncate/setattr/ACL records when the znode has synchronous waiters.
- FUID replay data is optional and appended only when ephemeral identities or ACL FUIDs require domain reconstruction.

Risk/attention points:
- The packed xvattr layout must stay synchronized with `zfs_replay_xvattr()` in `zfs_replay.c`; mismatched offsets would corrupt replayed attributes.
- The ACL/FUID record sizes include padding via `ZIL_ACE_LENGTH()`, which replay depends on for locating FUID arrays and domain strings.
- `zfs_log_xvattr()` appears to encode `XAT_OPAQUE` using `XAT0_APPENDONLY`; replay expects `XAT0_OPAQUE`, so this is a notable compatibility/bug-sensitive area when auditing attribute replay behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_onexit.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_onexit.c

Implements per-`/dev/zfs` control-device cleanup callbacks. It lets kernel code associate cleanup state with a clone-opened ZFS control fd so state can survive across related ioctls and still be released automatically when the fd closes or the process exits.

Key elements:
- `zfs_onexit_init()` allocates a `zfs_onexit_t`, initializes its mutex, and creates the action list.
- `zfs_onexit_destroy()` removes every registered action, drops the lock while firing each callback, frees action nodes, and tears down the list/mutex.
- `zfs_onexit_fd_hold()` validates a user fd, obtains the underlying minor, confirms it is a ZFS control-device minor, and keeps the file table entry held until `zfs_onexit_fd_rele()`.
- `zfs_onexit_add_cb()` registers a callback/data pair on a control minor and returns an action handle, implemented as the action-node address cast to `uint64_t`.
- `zfs_onexit_del_cb()` removes a callback by action handle and optionally fires it before freeing the node.
- `zfs_onexit_cb_data()` returns the callback data associated with an action handle without removing it.

Main dependencies and interactions:
- Uses `zfsdev_get_soft_state()` from `zfs_ioctl.c` to validate that a minor is a `ZSST_CTLDEV` control device rather than a zvol minor.
- Used by receive and temporary snapshot/hold flows to store cleanup state tied to a caller-supplied cleanup fd.
- Relies on `/dev/zfs` clone opens with `O_EXCL`, which create unique control minors in `zfs_ctldev_init()`.

Implementation notes:
- Callers are expected to hold the fd before doing work so later callback registration or lookup cannot fail because the fd was closed concurrently.
- The callback list is protected by `zo_lock`; callbacks are invoked after removing the node and outside the lock to avoid callback-induced deadlocks.
- Action handles are kernel pointers exposed as opaque integers to userland, but each lookup scans the current minor's action list before accepting the handle.

Risk/attention points:
- Action handles are only meaningful for the owning control minor and must not be treated as portable or persistent identifiers.
- Consumers must balance `zfs_onexit_fd_hold()` with `zfs_onexit_fd_rele()` or they will leak file references.
- Callback functions must tolerate being fired during close/exit, explicit delete, or cleanup after abnormal caller termination.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_onexit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_replay.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_replay.c

Implements replay of ZFS Intent Log records for ZPL operations. The file translates logged record payloads from `zfs_log.c` back into vnode/ZPL operations after a crash or replay event, using a transaction-type vector indexed by ZIL transaction type.

Key elements:
- `zfs_init_vattr()` reconstructs a `vattr_t` from logged mode, UID/GID, rdev, and node ID, treating ephemeral IDs as unset vnode IDs.
- `zfs_replay_xvattr()` unpacks logged xvattr bitmaps, flags, create time, AV scanstamp or project ID, and extended attribute booleans.
- FUID helpers reconstruct replay-time domain tables and FUID lists: `zfs_replay_domain_cnt()`, `zfs_replay_fuid_domain_common()`, `zfs_replay_fuid_ugid()`, `zfs_replay_fuid_domain()`, and `zfs_replay_fuids()`.
- `zfs_replay_swap_attrs()` byteswaps variable-size xvattr payloads for logs written on opposite-endian systems.
- `zfs_replay_create_acl()` replays ACL-bearing creates and mkdirs, claims the logged object/dnode slots, reconstructs ACL and FUID replay state, and calls `VOP_CREATE()` or `VOP_MKDIR()`.
- `zfs_replay_create()` replays normal create, mkdir, xattr-directory creation, symlink, and attr-bearing create/mkdir records.
- `zfs_replay_remove()`, `zfs_replay_link()`, and `zfs_replay_rename()` replay namespace operations through vnode operations with case-insensitive flags when logged.
- `zfs_replay_write()` replays write records, dropping writes to already-removed files, handling full-block dmu-sync records, and using `z_replay_eof` to preserve file-size semantics.
- `zfs_replay_write2()` handles delayed EOF extension for `TX_WRITE2` records by updating SA size in a DMU transaction.
- `zfs_replay_truncate()` replays truncation/free-space operations through `VOP_SPACE()`.
- `zfs_replay_setattr()` replays vnode attributes, xvattrs, and FUID domain context through `VOP_SETATTR()`.
- `zfs_replay_acl_v0()` and `zfs_replay_acl()` replay legacy and FUID-aware ACL records through `VOP_SETSECATTR()`.
- `zfs_replay_vector[]` maps all supported transaction types to their replay handlers and maps unsupported entries to `zfs_replay_error()`.

Main dependencies and interactions:
- Consumes the exact record formats produced by `zfs_log.c`, including create/ACL/xvattr/FUID packing and dnode-slot encoding.
- Calls ZPL vnode operations so replay follows normal filesystem mutation paths while using `kcred`.
- Uses `dnode_try_claim()` to recreate logged object IDs and large-dnode slot counts.
- Temporarily stores FUID replay context on `zfsvfs->z_fuid_replay` so lower-level create/setattr/ACL paths can resolve identities.
- Updates ZIL replay sequence state through `zil_replaying()` when replay creates its own DMU transaction in `zfs_replay_write2()`.

Implementation notes:
- Most handlers byteswap fixed record headers first, then byteswap variable sections such as ACLs, FUID arrays, and xvattr payloads using logged lengths.
- Create replay smuggles logged creation time, generation number, and dnode size through otherwise unused `vattr_t` fields because generic create vnode operations do not expose those ZFS-specific values.
- Write replay treats missing file objects as success for ordinary writes because log records may be replayed out of order relative to remove records.
- `z_replay_eof` is set only around replayed full-block writes that extend past current EOF and is cleared immediately after the write path.
- Each handler releases vnodes it acquired and frees temporary FUID replay state before returning.

Risk/attention points:
- Replay correctness depends on strict agreement with `zfs_log.c` record layout, especially variable xvattr and ACL/FUID offsets.
- Endian conversion must happen before interpreting variable sizes; mistakes can mislocate names, ACLs, or domain strings.
- The create replay path claims exact object IDs and dnode slot counts; failure there prevents faithful replay of later records targeting those IDs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_replay.c -->