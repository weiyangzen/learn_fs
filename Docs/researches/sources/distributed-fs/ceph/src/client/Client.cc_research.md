# Research: sources/distributed-fs/ceph/src/client/Client.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006901`: lines 1-8769, `Docs/researches/chunks/subset-b-006901_research.md`
- `subset-b-006902`: lines 8770-18201, `Docs/researches/chunks/subset-b-006902_research.md`
- `subset-b-006903`: lines 18202-19256, `Docs/researches/chunks/subset-b-006903_research.md`

## Chunk Research

### subset-b-006901: lines 1-8769

# sources/distributed-fs/ceph/src/client/Client.cc lines 1-8769

## Scope and Purpose

This chunk covers the front half of CephFS `Client.cc`, from includes through the beginning of `Client::_do_setattr`. It implements the core user-space CephFS client control plane: client lifecycle, metadata cache population, MDS request/reply routing, MDS session management, capability and lease handling, snapshot realm tracking, mount/unmount, permission checks, path lookup, and the first part of POSIX-style namespace and inode operations.

The code is the bridge between public libcephfs/FUSE-facing operations and distributed Ceph services. Metadata mutations and lookup state are coordinated with MDS daemons through `MetaRequest` and `MClient*` messages. File data caching and writeback are coordinated with `Objecter`, `ObjectCacher`, `ObjecterWriteback`, and `Filer`. Most mutable client structures are protected by `client_lock`, with lifecycle admission controlled by `initialize_state` and `mount_state` `RWRef_t` state machines.

## Important APIs, Types, and Helpers

- `Client` owns the CephFS mount session, including `Messenger`, `MonClient`, `Objecter`, `ObjectCacher`, `Filer`, `MDSMap`, `FSMap`, inode/dentry caches, open file tables, MDS sessions, cap state, snap realms, timers, finishers, and admin socket commands.
- `Client::CommandHook` exposes admin socket commands: `mds_requests`, `mds_sessions`, `dump_cache`, `kick_stale_sessions`, `status`, and subvolume metrics dumping. It takes `client_lock` before calling dump or control helpers.
- `Inode`, `Dentry`, `Dir`, `Fh`, `MetaSession`, `MetaRequest`, `Cap`, `CapSnap`, and `SnapRealm` form the main local metadata model. `inode_map` indexes inodes by `vinodeno_t`; dentries are cached under `Dir`; `lru` tracks trim candidates.
- Faked inode helpers `_reset_faked_inos`, `_assign_faked_ino`, `_assign_faked_root`, `_release_faked_ino`, `_map_faked_ino`, and `map_faked_ino` maintain a local 32-bit-compatible inode namespace when the platform or config requires it.
- Request helpers `make_request`, `choose_target_mds`, `build_client_request`, `send_request`, `verify_reply_trace`, `unregister_request`, and `put_request` implement blocking metadata RPC execution, request replay, forwarding, trace ingestion, and cleanup.
- Cache mutation helpers `add_update_inode`, `insert_dentry_inode`, `insert_readdir_results`, `insert_trace`, `link`, `unlink`, `trim_cache`, `trim_dentry`, and `_try_to_trim_inode` keep local inode/dentry state aligned with MDS replies and revocations.
- Capability helpers `add_update_cap`, `remove_cap`, `check_caps`, `send_cap`, `get_caps`, `put_cap_ref`, `mark_caps_flushing`, `flush_caps_sync`, `wait_sync_caps`, `handle_caps`, and specialized `handle_cap_*` functions implement CephFS client cap protocol.
- Snapshot helpers `get_snap_realm`, `put_snap_realm`, `adjust_realm_parent`, `update_snap_trace`, `handle_snap`, `queue_cap_snap`, `flush_snaps`, and `handle_cap_flushsnap_ack` maintain snapshot contexts and flush per-snapshot dirty metadata.
- Mount and control-plane helpers `authenticate`, `fetch_fsmap`, `resolve_mds`, `mds_command`, `subscribe_mdsmap`, `mount`, `_unmount`, `_close_sessions`, `abort_conn`, and `unmount` coordinate monitor auth/subscriptions, MDS command routing, and lifecycle teardown.
- POSIX-facing helpers in this chunk include `walk`, `path_walk`, `_lookup`, `_do_lookup`, `do_link`, `unlinkat`, `do_rename`, `do_mkdirat`, `mkdirs`, `mknod`, `do_symlinkat`, `readlinkat`, `_getattr`, `_getvxattr`, and the start of `_do_setattr`.

## Control Flow

Initialization starts in `Client::Client`, which reads config, sets supported feature bits, initializes faked inode state, creates `MDSMap`, constructs `ObjecterWriteback`, and configures `ObjectCacher` with `client_flush_set_callback`. `init()` moves `initialize_state` to initializing, calls `_pre_init()` to start timer/objecter finishers/object cache/filer/fscrypt, registers the dispatcher, then `_finish_init()` creates perf counters and admin socket commands.

Mounting is driven by `mount()`. It enters `CLIENT_MOUNTING`, authenticates and subscribes to the selected MDS map, starts the tick thread, optionally waits for MDS availability, rejects mounts while `CEPH_MDSMAP_REFUSE_CLIENT_SESSION` is set, populates client metadata, then walks from the requested mount root toward the root by repeated `GETATTR` requests. Successful traces build `root`, `root_ancestor`, and parent roots. The mount also opens optional trace output and may initialize Linux dummy fscrypt policy before entering `CLIENT_MOUNTED`.

Metadata operations use `make_request()`. It assigns a client TID, records oldest outstanding TID, stores caller permissions, chooses an MDS by `choose_target_mds()`, opens or waits for a `MetaSession`, checks required MDS feature support, sends the `MClientRequest`, then waits on `request->caller_cond` for a reply, forward, or kick. Forward messages update `resend_mds` and retry counters. Replies are processed by `handle_client_reply()`, which validates the session/TID, calls `insert_trace()`, tracks unsafe requests, wakes the caller once, and unregisters the request after a safe reply.

Trace ingestion decodes MDS reply trace buffers. `insert_trace()` optionally updates snap realms, decodes parent and target inode stats, calls `add_update_inode()`, updates dirfrag distribution, links or unlinks dentries, handles traceless mutation replies, and dispatches readdir/lssnap/snapdiff extras to `insert_readdir_results()`. `verify_reply_trace()` repairs the target inode for create/mutation calls that got traceless replies by looking up the dentry or forcing getattr.

MDS maps and sessions are asynchronous message-driven. `ms_dispatch2()` gates all messages on `CLIENT_INITIALIZED`, dispatches MDS/FS/OSD maps, session messages, request forwards/replies, reclaim replies, snaps, caps, leases, commands, and quotas. `handle_mds_map()` ignores old epochs, decodes the new map outside the client lock, cancels commands targeting missing/laggy MDS daemons, swaps the map, reconnects or closes sessions based on rank state and address/incarnation changes, trims cache for reconnect, and wakes map waiters. `handle_client_session()` moves sessions through open, close, renewcaps, stale, recall, flushmsg, force-ro, and reject behavior.

Reconnect is explicit in `send_reconnect()`: trim reconnect-relevant cache, reset session release and cap sequence state, connect export targets, replay unsafe requests, early-kick flushing caps, then build one or more `MClientReconnect` messages containing current caps, wanted masks, file locks, short paths, and snaprealm metadata. After reconnect it wakes mount waiters and reclaim waiters when needed.

The cap flow is state-machine heavy. Grants and revokes update `Cap::issued`, `implemented`, `wanted`, sequence numbers, max size, inode attributes, and waiters. `check_caps()` computes wanted/used/retain sets, handles lazyio substitution, flushes dirty metadata, releases clean cache, delays cap release unless `CHECK_CAPS_NODELAY`, and sends `MClientCaps` updates. Flush acknowledgements remove `flushing_cap_tids`, clear `flushing_caps`, wake sync waiters, and drop dirty-cap inode refs. Cap imports/exports move auth ownership and flushing-list membership between sessions.

Unmount enters `CLIENT_UNMOUNTING`, waits for readers to drain, optionally aborts sessions and OSD writes, waits for write metadata requests, drops cwd/root/open files/open dirs/low-level pins, releases or purges object cache data, flushes caps when not aborting, trims the metadata cache until both LRU and inode map are empty, closes trace output, stops the tick thread, closes sessions, releases the global snap realm, and finally enters `CLIENT_UNMOUNTED`. Abort and blocklist paths purge data and drop dirty caps rather than flushing.

Path operations use `path_walk()`. It starts from root/cwd/supplied directory, checks mount state, optionally checks lookup permissions, wraps names for charmap normalization/casefolding and fscrypt filename encryption, creates or finds local dentries, calls `_lookup()` for cache or MDS lookup, follows symlinks up to `MAXSYMLINKS`, decrypts encrypted symlink targets when fscrypt is active, and returns a `walk_dentry_result` containing parent dir, dentry name, alternate name, dentry, and target.

The chunk ends inside `_do_setattr()`. The visible portion handles permission and auth-cap checks, local dirtying when exclusive caps permit asynchronous setattr, sync fallback preparation through MDS request args, quota and max-file-size checks, fscrypt auth/file metadata constraints, and Linux fscrypt last-block preparation when truncating encrypted files smaller to an unaligned size. The remainder of setattr is outside this chunk.

## State and Persistence Behavior

Persistent filesystem state is owned by the MDS and OSDs; this client maintains a coherent local cache and sends durable updates through metadata requests, cap flushes, mdlog flushes, and object writes.

- `inode_map`, `root`, `cwd`, `root_parents`, `Dir::dentries`, and the LRU are volatile metadata cache. They are updated from MDS traces and invalidated or trimmed on cap/lease changes, reconnect, unmount, and cache-pressure events.
- Inode attributes are only trusted under appropriate caps. `add_update_inode()` and `handle_cap_grant()` update mode, uid/gid, times, size, layout, xattrs, inline data, quotas, dir stats, change attr, fscrypt metadata, and dirfrag maps according to version and cap ownership rules.
- Dirty metadata lives in inode cap state (`dirty_caps`, `flushing_caps`, `flushing_cap_tids`, `dirty_list`). `mark_caps_flushing()` snapshots dirty bits into a flush TID and `handle_cap_flush_ack()` confirms MDS persistence.
- Dirty file data lives in `ObjectCacher::ObjectSet` per inode. `_flush()`, `_flush_range()`, `flush_set_callback()`, and `_flushed()` coordinate writeback and release `FILE_CACHE`/`FILE_BUFFER` cap refs after commit. Full or blocklisted OSD maps cancel writes and purge object sets to avoid deadlock.
- Unsafe metadata mutations are tracked per session and sometimes per inode (`unsafe_requests`, `unsafe_ops`). A safe reply means the MDS journaled the operation; unmount waits for write requests and can flush mdlog for pending operations.
- Snapshot realms are reference-counted in `snap_realms`. Updating a realm invalidates child contexts; new snaps queue `CapSnap` records so dirty metadata/data are flushed under the old snap context before adopting the new one.
- Faked inode mappings are volatile process-local maps from small `ino_t` values to `vinodeno_t`. They are rebuilt on client construction and cleaned when inodes are released.
- `metadata` is sent to MDS session-open and admin/status output. It includes hostname, pid, entity id, mount root, Ceph version/SHA, and configured overrides.

## Dependencies and Integration Points

- Ceph messaging: `Messenger` dispatches `MClientSession`, `MClientReply`, `MClientCaps`, `MClientLease`, `MClientSnap`, `MClientQuota`, `MClientReconnect`, `MClientMetrics`, maps, and command replies.
- Monitor integration: `MonClient` handles authentication and subscriptions for `mdsmap`, `fsmap`, and `fsmap.user`.
- MDS integration: `MDSMap` and `FSMap` drive target selection, command routing, feature negotiation, reconnect, session state, command cancellation, and MDS availability checks.
- OSD/RADOS integration: `Objecter`, `ObjectCacher`, `ObjecterWriteback`, `Filer`, `OSDMap`, and `Striper` provide file data caching, flushing, full-pool detection, blocklist handling, and epoch barriers.
- Kernel/FUSE/libcephfs integration: callbacks for inode invalidation, dentry invalidation, inode release, remount, interrupt/remount finishers, low-level inode refs, and file descriptor maps connect this cache to external consumers.
- Linux-only fscrypt integration: filename wrapping/unwrapping, symlink decryption, file-size rounding, dummy encryption setup, inode lock/key checks, fscrypt auth/file metadata, and encrypted last-block truncation handling.
- Boost locale is used for UTF-8 validation, normalization, and case folding under directory charmap policy.
- Admin socket and perf counters expose debug state, cache dumps, latency averages/square sums, cap/dentry/open-file metrics, and subvolume metrics.
- POSIX ACL helpers are used when `client_acl_type` enables ACL permission checks.

## Risks and Edge Cases

- Locking is delicate. Many helpers assert `client_lock` held, while async callback finishers assert it is not held and re-enter through callback methods. `make_request()` and dispatcher paths use `adopt_lock` waits, so incorrect lock ownership would deadlock or corrupt state.
- Request lifetime is subtle: `make_request()`, `handle_client_reply()`, `unregister_request()`, and `put_request()` coordinate caller and dispatcher via `dispatch_cond`, refcounts, unsafe lists, and request maps. Double replies, stale replies, and forwards are explicitly guarded.
- Reconnect correctness depends on replaying unsafe requests, preserving old requests for clientreplay, resetting cap sequence numbers, and sending matching reconnect/cap-flush messages. Bugs here risk duplicated or lost metadata operations.
- Cap revocation interacts with object cache flushing. If revoking write/buffer/cache caps while data is dirty, the client must flush or purge correctly. OSD full/blocklist paths deliberately set async errors and purge to avoid holding caps forever.
- `handle_cap_export()`/`handle_cap_import()` move auth caps and flushing lists between sessions. Sequence comparisons and peer cap IDs are critical; mistakes can strand dirty caps or lose auth ownership.
- Dentry cache validity combines leases, session cap TTL/generation, directory shared caps, `I_COMPLETE`, and shared generation counters. Rename in-progress dentries force waits to avoid transient double links.
- Directory completion/order flags are aggressively cleared on link/unlink/readdir changes. Incorrect clearing could cause false ENOENT from local cache or unnecessary MDS lookups.
- Snapshot updates must queue cap snaps before adopting new snap contexts. Missing a dirty inode during `update_snap_trace()` could write data under the wrong snapshot context.
- Fscrypt paths have multiple failure modes: invalid UTF-8 under charmap, missing keys (`-ENOKEY`), symlink decryption failures, encrypted filename alternate-name handling, rounded sizes, and last-block preparation during truncate.
- `_schedule_invalidate_dentry_callback()` assumes `dn->inode` is non-null when checking `dn->inode->ll_ref`; callers must not pass negative dentries to this helper.
- The visible `path_walk()` has a shadowed local `trimmed_path` assignment inside `if (trimmed_path == "")`, so debug logging may keep the empty parameter rather than the computed trimmed path. This is diagnostic but may complicate tracing.
- `_do_setattr()` is partially visible only. The visible part already mixes local dirty-cap updates with sync request fallback; downstream code must preserve the mask/inode_drop invariants established here.

## Test Signals

- Mount lifecycle tests should cover successful root walk, named filesystem subscription, missing filesystem, `require_mds` unavailable/transient behavior, `REFUSE_CLIENT_SESSION`, mount timeout injection, dummy fscrypt policy setup, and clean/abort unmount.
- Metadata request tests should exercise forwards, retry overflow to `-EMULTIHOP`, traceless create/mutation reply repair, unsafe then safe replies, stale reply rejection, request abort on blocklist, and MDS feature-gated operations.
- Cache tests should cover inode update precedence under exclusive/shared caps, xattr and inline-data version updates, empty-directory `I_COMPLETE|I_DIR_ORDERED`, readdir hash-order offsets, snapdiff dual-directory insertion, dentry leases, negative dentries, rename waiters, and trim behavior.
- Cap protocol tests should cover grant, revoke, import/export, stale session generation, delayed release, synchronous cap flush, flush ack ordering, max-size request/renewal, lazyio adjustment, readonly sessions, dirty cap cleanup on session removal, and injected release failure.
- Object cache/error tests should cover flush success/failure, full global and per-pool OSD maps, blocklist transitions, cache purge versus release, epoch barrier propagation, and async error reporting.
- Snapshot tests should cover snaprealm parent changes, split handling, child realm invalidation, new-snap cap-snap queuing, dirty-data flushing before snap context change, and flushsnap acknowledgement cleanup.
- Permission/path tests should cover root DAC override rules, POSIX ACL fallback, sticky-dir deletion, hardlink restrictions, auth caps/root squash matching, charmap normalization/casefolding, fscrypt encrypted names and symlinks, symlink loops, `.`/`..`, snapdir visibility, long names, and path-walk no-target behavior for create.
- Admin and observability tests should verify admin socket command registration/unregistration, JSON dump shape for status/cache/sessions/requests, latency average/square-sum counters, metric message feature filtering, and subvolume metric add/remove behavior.

## Chunk Boundary Notes

This report intentionally covers only lines 1-8769 of `Client.cc`. Later code continues `_do_setattr()` and implements additional POSIX operations, file I/O, xattrs, locks, delegations, reclaim, and low-level APIs. Any whole-file synthesis should merge this with later chunk reports before drawing final conclusions about complete setattr/file-data behavior.

### subset-b-006902: lines 8770-18201

# sources/distributed-fs/ceph/src/client/Client.cc lines 8770-18201

## Scope

This chunk covers a large middle-to-late section of CephFS `Client.cc`. It starts inside the tail of `_do_setattr`, where timestamp setattr operations may be satisfied locally from issued caps or converted into a `CEPH_MDS_OP_SETATTR` request. It ends after the shared quota traversal helper `check_quota_condition`, immediately before the concrete quota exceeded/approaching helpers that continue in the next chunk.

The range contains the main POSIX-like client operations for setattr/stat/statx, chmod/chown/timestamps, directory handles and `readdir`, blockdiff/snapdiff helpers, open/close/read/write/fsync/truncate/fallocate, file locks, statfs, lazy I/O, snapshot create/remove, the low-level `ll_*` API, xattrs and virtual xattrs, namespace mutations, layout/OSD-map inspection helpers, messenger reset callbacks, and the first quota-root traversal helpers.

## Purpose

This code is the userspace CephFS client syscall and low-level API implementation layer. It translates path-, fd-, inode-, and file-handle-oriented operations into local cache/capability decisions, MDS metadata requests, ObjectCacher/Filer data I/O, Objecter map and object operations, and callback/refcount management for libcephfs and FUSE-style users.

The chunk is not a standalone subsystem; it is the central bridge between application-visible filesystem operations and the rest of the CephFS client. Most public methods follow a consistent pattern: verify mount state, take `client_lock`, resolve paths or file descriptors, check permissions and readonly/quota constraints, then delegate to an internal helper that either uses local caps/cache or issues a metadata/data request.

## Important APIs, Types, and Functions

The setattr/stat family includes `stat_to_statx`, `__setattrx`, `_setattrx`, `_setattr`, `setattr`, `setattrx`, `fsetattr`, `fsetattrx`, `stat`, `lstat`, `statx`, `statxat`, `fstat`, `fstatx`, `fill_stat`, and `fill_statx`. `statx_to_mask` maps statx flags and requested fields to Ceph caps such as `CEPH_CAP_AUTH_SHARED`, `CEPH_CAP_LINK_SHARED`, `CEPH_CAP_FILE_SHARED`, and `CEPH_CAP_XATTR_SHARED`. `fill_stat` and `fill_statx` turn cached inode state into POSIX/statx structs, including faked inode numbers, snap IDs as device values, directory nlink synthesis, snapdir size, effective file size, recursive stats, and change attributes.

The chmod/chown/time wrappers include `chmod`, `chmodat`, `lchmod`, `fchmod`, `chown`, `chownat`, `lchown`, `fchown`, `utime`, `lutime`, `utimes`, `lutimes`, `futime`, `futimes`, `futimens`, and `utimensat`. These mostly construct a `stat` or `ceph_statx` payload and funnel into `_setattr`/`_setattrx`, with symlink-following and fd-relative handling expressed through `path_walk` options.

Directory traversal is centered on `dir_result_t` and helpers `_opendir`, `_closedir`, `rewinddir`, `seekdir`, `fill_dirent`, `_readdir_next_frag`, `_readdir_rechoose_frag`, `_readdir_drop_dirp_buffer`, `_readdir_get_frag`, `_readdir_cache_cb`, `readdir_r_cb`, and `_readdir_r_cb`. Public entry points include `opendir`, `fdopendir`, `closedir`, `telldir`, `readdir`, `readdir_r`, `readdirplus_r`, `_getdents`, and `getdir`. `_readdir_r_cb` is the common engine for normal readdir and snapdiff result processing.

The file-handle and open path includes `create_and_open`, `do_openat`, `_lookup_vino`, `lookup_ino`, `_lookup_parent`, `_lookup_name`, `_create_fh`, `_release_fh`, `_put_fh`, `_open`, `_renew_caps`, `_close`, and `close`. File handles (`Fh`) track inode refs, open mode, fd generation, current position, position waiters, actor permissions, lazy I/O mode, readahead state, delegation state, per-fh lock state, and asynchronous error state.

Data I/O is implemented by `read`, `preadv`, `_read`, `_read_async`, `_read_sync`, `write`, `pwritev`, `_preadv_pwritev`, `_preadv_pwritev_locked`, `_write`, `_write_success`, `_flush`, `truncate`, `ftruncate`, `fsync`, `nonblocking_fsync`, `_fsync`, and the async helper contexts `C_Read_Finisher`, `C_Read_Sync_NonBlocking`, `C_Readahead`, `C_Read_Async_Finisher`, `C_Lock_Client_Finisher`, `C_Write_Finisher`, and `C_nonblocking_fsync_state`. `WriteEncMgr`, `WriteEncMgr_Buffered`, and `WriteEncMgr_NotBuffered` manage fscrypt read-modify-write and select ObjectCacher versus Filer writes.

File locking is handled through public `flock`, `getlk`, `setlk` and low-level `ll_getlk`, `ll_setlk`, `ll_flock` wrappers around `_do_filelock`, `_interrupt_filelock`, `_encode_filelocks`, `_release_filelocks`, `_update_lock_state`, `_getlk`, `_setlk`, and `_flock`. These functions translate POSIX lock types into Ceph lock request fields, track inode-level and fh-level `ceph_lock_state_t`, and optionally route blocking lock waits through interrupt callbacks.

The low-level `ll_*` API exposes inode/file-handle operations directly: lookup (`ll_lookup`, `ll_lookup_vino`, `ll_lookup_inode`, `ll_lookupx`, `ll_walk`), inode pinning (`_ll_get`, `_ll_put`, `_ll_drop_pins`, `_ll_forget`, `ll_get`, `ll_forget`, `ll_put`, `ll_get_inode`, `ll_get_snap_ref`, `ll_get_snapid`), attrs (`ll_getattr`, `ll_getattrx`, `ll_setattr`, `ll_setattrx`), namespace operations (`ll_mknod`, `ll_mknodx`, `ll_mkdir`, `ll_mkdirx`, `ll_symlink`, `ll_symlinkx`, `ll_unlink`, `ll_rmdir`, `ll_rename`, `ll_link`, `ll_create`, `ll_createx`), I/O (`ll_open`, `ll_lseek`, `ll_read`, `ll_write`, `ll_readv`, `ll_writev`, `ll_preadv_pwritev`, `ll_flush`, `ll_fsync`, `ll_sync_inode`, `ll_fallocate`, `ll_release`), directory handles (`ll_opendir`, `ll_releasedir`, `ll_fsyncdir`), and layout/OSD helpers.

The xattr layer includes path/fd wrappers for get/list/set/remove xattrs, internal `_getxattr`, `_listxattr`, `_setxattr`, `_do_setxattr`, `_removexattr`, `ll_getxattr`, `ll_listxattr`, `ll_setxattr`, and `ll_removexattr`. Virtual xattrs are described by `Client::VXattr` arrays `_dir_vxattrs`, `_file_vxattrs`, and `_common_vxattrs`, with callbacks for layout, quota, directory stats, recursive stats, snap birth time, caps, mirror info, cluster FSID, client ID, and fscrypt auth/file data.

Other notable helpers are `file_blockdiff_init_state`, `file_blockdiff`, `file_blockdiff_finish`, `readdir_snapdiff`, `_statfs`, `statfs`, `ll_statfs`, callback registration via `_ll_register_callbacks`/`ll_register_callbacks2`, `_sync_fs`, `sync_fs`, `drop_caches`, `_lazyio`, `lazyio_propagate`, `lazyio_synchronize`, `mksnap`, `rmsnap`, `refresh_snapdir_attrs`, `open_snapdir`, `clear_suid_sgid`, `_fallocate`, layout inspection helpers, messenger reset handlers, `get_quota_root`, and `check_quota_condition`.

## Control Flow

Most public APIs first acquire an `RWRef_t` over `mount_state` and return `-ENOTCONN` if the client is not sufficiently mounted. They then take `client_lock` before touching inode maps, dentries, file handles, caps, or directory buffers. Helpers whose names begin with `_` usually assume the lock is already held and enforce that with `ceph_assert(ceph_mutex_is_locked_by_me(client_lock))`.

Path-based operations use `path_walk` from `cwd`, a supplied parent inode, or a fd-derived inode. Options control symlink following, requested cap mask, whether the target must exist, and rename-specific alternate-name behavior. Fd-based operations call `get_filehandle` or `get_fd_inode`; low-level APIs validate `Fh*` handles with `_ll_fh_exists` where they can be called with raw pointers.

Setattr flow filters user masks, performs permission checks through `may_setattr`, may clear setuid/setgid bits, and enters `_do_setattr`. When caps allow, mtime/atime/size updates can be performed locally by changing inode fields, incrementing `change_attr` or `time_warp_seq`, and marking caps dirty. Remaining work is sent as a `CEPH_MDS_OP_SETATTR` `MetaRequest` with inode drop masks and optional fscrypt auxiliary payloads.

Stat flow computes a desired cap mask from statx flags. If the caller did not request `AT_STATX_DONT_SYNC`, `_getattr` refreshes missing or forced caps from the MDS. `fill_stat`/`fill_statx` then materialize the response entirely from the `Inode`. Statx fields are only marked available when the corresponding cap mask was requested or all shared inode caps are present.

Readdir flow emits `.` and `..` first, then tries to serve from a complete ordered directory cache if available. Otherwise `_readdir_get_frag` builds a `CEPH_MDS_OP_READDIR`, `CEPH_MDS_OP_LSSNAP`, or `CEPH_MDS_OP_READDIR_SNAPDIFF` request for the current frag. The result buffer is walked in offset order, callbacks are invoked with `client_lock` temporarily dropped, and offsets are updated. When a full, stable pass reaches the rightmost frag, the directory may be marked `I_COMPLETE` and optionally `I_DIR_ORDERED`.

Open/create flow resolves the target with `create_and_open` or `_ll_create`. Existing files are permission-checked with `may_open`; missing files with `O_CREAT` call `_create`, which prepares a `CEPH_MDS_OP_CREATE` request with inherited fscrypt auth, layout overrides, POSIX ACL create xattrs, dentry cache drop/unless hints, and optional initial `Fh`. `_open` may short-circuit if suitable caps are already issued and local MDS access checks pass; otherwise it sends `CEPH_MDS_OP_OPEN`. Delegation-aware opens may force a cap wait after the MDS open.

Read flow requires read mode unless the read is for fscrypt write preparation. Negative offsets mean "use and advance fh position" and are serialized by `lock_fh_pos`. `_read` obtains file read/cache caps, handles inline data directly, then chooses ObjectCacher async reads when cache caps and `client_oc` are available or Filer reads otherwise. Synchronous reads retry short reads after revalidating size; holes before known EOF are zero-filled. Fscrypt reads expand to encrypted block ranges and decrypt before returning logical data.

Write flow validates write mode, max file size, pool-full state, quotas, inline-data state, and write/auth caps. It may clear setuid/setgid bits, select buffered ObjectCacher writes or unbuffered Filer writes, and delegate fscrypt block-aligned read-modify-write to `WriteEncMgr`. Inline data can be updated in inode memory when still below inline thresholds; otherwise `uninline_data` creates/writes the backing object and marks inline state as `CEPH_INLINE_NONE`. On success `_write_success` updates size/effective size, mtime/ctime, `change_attr`, dirty caps, metrics, and file position.

Fsync flow flushes ObjectCacher data if enabled, pushes dirty caps through `check_caps`, flushes mdlog when unsafe metadata ops exist, waits for unsafe requests to become safe, waits for data or buffer cap refs to commit, and then waits for cap flush tids. `C_nonblocking_fsync_state` implements the same sequence as a resumable state machine for async write finishers.

Namespace mutation flow for mknod/create/mkdir/symlink/unlink/rmdir/rename/link validates snap readonly state, local permission predicates, quota file limits, encryption-key state where applicable, and cross-quota/cross-snapshot constraints. It then sends the matching MDS op with dentry/inode references and cache invalidation/drop hints. Rename additionally sets `is_renaming` on the destination dentry and wakes waiters on failure.

Layout and OSD inspection helpers use `Objecter::with_osdmap`, `OSDMap`, `Striper::file_to_extents`, and CRUSH/PG mapping to expose pool IDs/names/replication, stripe unit and layout, object extents, acting OSDs, OSD addresses, CRUSH locations, and a cached local OSD candidate.

Messenger reset handlers cancel matching one-shot MDS command ops on connection reset/refusal. Remote resets from MDS peers also locate the corresponding `MetaSession` and transition closing sessions to closed, retry opening sessions, or mark open sessions stale/closed depending on `client_reconnect_stale`.

## State and Persistence Behavior

This chunk mutates in-memory client state extensively. Inodes hold stat fields, layout, xattrs, quota and recursive stats, snaprealm pointers, directory frag trees, inline data, fscrypt metadata, cap refs, dirty cap bits, wait lists, file-lock state, delegation state, and flags such as `I_COMPLETE`, `I_DIR_ORDERED`, `I_SNAPDIR_OPEN`, and `I_ERROR_FILELOCK`. File handles hold open mode refs, current position, async errors, per-fh lock state, readahead settings, and delegation hooks.

Durable filesystem changes are committed through MDS `MetaRequest` operations for metadata and Filer/Objecter/ObjectCacher operations for data. Local inode changes are authoritative only when backed by caps and are later flushed through cap dirty/flush machinery. `_write_success`, `_fallocate`, inline write paths, and setattr fast paths all update local inode metadata and mark caps dirty rather than immediately forcing MDS persistence.

Directory state persists in the client cache as dentries, `Dir::readdir_cache`, `dir_result_t` buffers, frag offsets, last names, shared generation counters, and ordered/complete markers. Cache validity is guarded by caps, `shared_gen`, release/order counters, fscrypt key validators, and EAGAIN retry paths when local cache state changes during iteration.

Low-level inode refs are explicit. `_ll_get` transitions an inode into low-level pinned state, may pin the parent dentry for directories, increments snap refs for snapped inodes, and calls `iget`. `_ll_put` reverses this and may call `put_inode`. `ll_unclosed_fh_set` tracks low-level handles returned to callers until `ll_release`.

Xattrs exist in two layers: real inode `xattrs` fetched from the MDS and virtual xattrs computed from live client/MDS/Objecter state. Setting real or virtual xattrs may create MDS requests, update mode for POSIX ACL equivalence, trigger fscrypt setattr paths, or wait for a newer OSDMap when setting layout pools.

Metrics and observability state are updated on I/O paths. Reads/writes update byte counters, latency counters, request counters, `SubvolumeMetricTracker`, and fsync latency counters. File handles store async writeback errors until `flush`, `fsync`, `close`, or low-level equivalents consume them.

## Dependencies and Integration Points

The code depends on MDS protocol messages and ops including setattr, open, create, mkdir/mksnap, symlink, unlink, rmdir/rmsnap, rename/renamesnap, link, lookupino/lookupparent/lookupname/lookuphash, readdir/lssnap/snapdiff, file blockdiff, get/set filelock, set/rm xattr, and metadata log flush/safety tracking. `make_request` is the core integration point to MDS sessions and reply trace insertion.

Data I/O depends on `ObjectCacher`, `Filer`, `Objecter`, `OSDMap`, `SnapContext`, `Striper`, object layouts, pool IDs, truncate sequence/size, and object operations. `uninline_data` directly creates/writes an object and records inline version xattrs through Objecter mutations.

Capability integration is central. The functions call `get_caps`, `get_cap_ref`, `put_cap_ref`, `check_caps`, `_getattr`, `_release`, `_flush`, `_flush_range`, `flush_caps_sync`, `wait_sync_caps`, and cap dirty markers to coordinate local cache authority with MDS grants.

Permission integration uses `UserPerm`, `should_check_perms`, `may_*` helpers, `mds_check_access`, POSIX ACL helpers, xattr permission helpers, quota helpers, and mount-state guards. Some functions intentionally skip checks for special names such as `.`/`..` or for low-level flows where the caller already holds an inode.

Fscrypt integration is Linux-only and appears across path wrapping/unwrapping in adjacent code, xattr callbacks, open/close key-store tracking, read decryption, write read-modify-encrypt, inherited fscrypt auth for new dentries, encrypted symlink target construction, and key-lock checks during rename.

The low-level API integrates with libcephfs users that cache `Inode*`, `Fh*`, and `dir_result_t*` handles. Callback registration integrates inode/dentry invalidation, interrupt switching, remount, inode release, and umask callbacks with background finishers.

## Risks and Edge Cases

Locking is delicate. Many helper callbacks intentionally drop `client_lock` while invoking user callbacks or waiting for OSD/ObjectCacher completions, then reacquire it. Readdir explicitly handles cache mutation after `_getattr` and after callback unlock windows by returning `-EAGAIN`. File-handle position locking uses condition variables and assumes callers hold `client_lock` when entering.

Async I/O lifetime handling is complex. `C_Read_Finisher`, `C_Write_Finisher`, `C_nonblocking_fsync_state`, `WriteEncMgr`, and `iofinish_method_ctx` transfer ownership between unique pointers, released contexts, finisher queues, and callbacks. Errors must release cap refs exactly once and complete user contexts exactly once.

Inline data and fscrypt paths are high risk. Writes may update inline data in memory, uninline concurrently with writes, perform partial encrypted-block reads, pad blocks, encrypt/decrypt bufferlists, and adjust logical versus encrypted size. Any mismatch can corrupt data, leak stale bytes, or report wrong byte counts.

Quota checks are intentionally partly local and can be stale. Writes and namespace mutations check local quota roots before issuing operations, while `statfs` may avoid forced quota-root getattr if sessions are stale to keep `df` responsive. Cross-quota rename rejects can be conservative and depend on cached snaprealm/quota ancestry.

The stat/statx conversion has compatibility hazards. `fill_stat` reports `st_dev` as snapid, synthesizes directory nlink from dirstat, uses ctime as max(ctime, mtime), and reports different directory sizes depending on `client_dirsize_rbytes` and snapdir state. `statx_to_mask` treats `AT_STATX_DONT_SYNC` as mask zero, and `fill_statx` then treats zero as all fields locally available.

Directory offsets and frag ordering are subtle. The code supports hash-order and frag-order modes, uses reserved offsets for `.` and `..`, stores high/low offset components, and marks caches complete only if generation and release/order counters are unchanged. Seek backward disables ordered cache filling.

Raw low-level pointers are risky. `ll_*` APIs must balance `_ll_get`/`_ll_put`, `ll_unclosed_fh_set`, and directory handle closure. Some paths validate `_ll_fh_exists`; others assume the caller passed a live handle. `fdopendir` also transfers responsibility for closing the fd to `closedir`.

Object layout helpers can expose stale or model-dependent placement data because they use the current OSDMap and cached inode layout/truncate state. Address helpers assume at least one address in `get_addrs(...).front()`.

Messenger reset handling only cancels matching one-shot command ops and updates MDS session state for MDS peers. Other in-flight metadata or data operations rely on surrounding session/request machinery outside this chunk.

The requested range starts and ends at chunk boundaries inside larger logic. `_do_setattr` setup appears before line 8770, and concrete quota condition wrappers such as file/byte exceeded checks continue after line 18201.

## Test Signals

Stat/setattr tests should cover chmod/chown/timestamp/truncate/stat/statx/fstatx on files, dirs, symlinks with and without `AT_SYMLINK_NOFOLLOW`, fd-relative paths, O_PATH handles, `AT_STATX_DONT_SYNC`, faked inode numbers, snapdirs, and local-cap fast paths versus forced MDS getattr/setattr paths.

Directory tests should exercise readdir/readdirplus/getdents/getdir on empty dirs, large fragmented dirs, cache-complete dirs, hash-ordered dirs, seeks forward/backward, callback early-stop, fscrypt key invalidation, snapdir listing, and snapdiff. A useful signal is that cache mutations during callbacks return/retry cleanly without duplicate or skipped offsets.

I/O tests should cover buffered and unbuffered reads/writes, O_DIRECT, O_SYNC/O_DSYNC/O_RSYNC, append with implicit offset, preadv/pwritev clamping, short reads near EOF, sparse holes, inline data read/write/uninline transitions, object pool full behavior, max file size, quota rejection, fscrypt partial-block read-modify-write, async low-level I/O callbacks, and async error consumption on flush/fsync/close.

Fsync tests should verify data-only and data+metadata flushes, unsafe request waiting, dirty cap flush waiting, object-cache disabled mode, nonblocking fsync completion ordering, and propagation/clearing of async errors.

Locking tests should cover POSIX byte-range locks, flock locks, unlock state updates, fh close releasing locks, blocking lock interruption through `ll_interrupt`, `I_ERROR_FILELOCK`, and reconnect/session behavior that uses `_encode_filelocks`.

Xattr tests should cover real `user.`, `security.`, `trusted.`, `system.` ACL, and `ceph.` names; unsupported namespaces; list buffer sizing; virtual layout/quota/stats/caps/client-id/fsid/fscrypt xattrs; readonly virtual xattrs; POSIX ACL mode equivalence; layout pool lookup by name/id; OSDMap wait when setting unknown pools; and snap readonly rejection.

Namespace tests should cover create/open with `O_CREAT`, `O_EXCL`, `O_NOFOLLOW`, and `O_PATH`; mknod/mkdir/symlink/unlink/rmdir/rename/link low-level and path APIs; snap mksnap/rmsnap/renamesnap; inherited fscrypt auth; encrypted symlink target generation; cross-quota rename rejection; delegation break on unlink/rename/link; and error cleanup of rename waiters.

Low-level API tests should explicitly balance inode refs and file-handle release, validate stale/invalid handle errors, check `ll_get_inode` with faked and real inode numbers, ensure snap ref counts drop, and verify that `ll_create`/`ll_open` populate `ll_unclosed_fh_set` until `ll_release`.

Layout/OSD helper tests should use controlled layouts and OSDMaps to validate object extent mapping, stripe-unit remainder lengths, pool name/id/replication lookup, OSD address retrieval, CRUSH location lookup, local OSD epoch caching, and empty acting-set errors.

Messenger/session tests should simulate MDS connection reset, remote reset, and refused connection for one-shot commands and MDS sessions in opening, open, closing, stale, and closed states. Expected signals include command cancellation with `-EPIPE`, opening waiter transfer to a new session, and stale versus closed behavior controlled by `client_reconnect_stale`.

## Cross-Chunk Notes

Earlier chunks are needed for full definitions of `Client`, `Inode`, `Fh`, `dir_result_t`, cap helpers, `_do_setattr` setup, path walking, request submission, mount/session lifecycle, and permission helpers. Later chunks are needed for the concrete quota byte/file exceeded and approaching helpers, pool permission checks, POSIX ACL helpers, fscrypt key management APIs, reclaim handling, config-change handling, and the file tail.

The merge lane should combine this document with adjacent `Client.cc` chunk reports before creating the final source-tree-aligned per-file research document at `Docs/researches/sources/distributed-fs/ceph/src/client/Client.cc_research.md`.

### subset-b-006903: lines 18202-19256

# sources/distributed-fs/ceph/src/client/Client.cc lines 18202-19256

## Scope

This chunk covers the tail of `sources/distributed-fs/ceph/src/client/Client.cc`, from quota limit predicates through the `StandaloneClient` initialization and shutdown methods. The range is not one cohesive subsystem; it is a collection of late-file `Client` helpers and public control entry points that bridge CephFS metadata state, RADOS/Objecter operations, POSIX ACL handling, Linux fscrypt ioctls, client session reclaim, runtime configuration changes, subvolume IO metrics, a recursive-ish copy helper, and standalone client lifecycle.

The chunk depends on earlier `Client.cc` code for the generic quota ancestor walk, xattr and setattr request paths, sync/flush behavior, session opening, mount-state guards, inode path walking, and file IO. It also depends on declarations in `Client.h`, `Inode.h`, `MetaSession.h`, `FSCrypt.h`, `posix_acl.h`, and the MDS message classes. This document intentionally remains chunk-level; the merged per-file report should reconcile it with earlier chunks that define the helper calls used here.

## Purpose

The quota helpers provide small predicates over the shared `check_quota_condition()` traversal. They answer whether an inode is over file-count quota, whether a pending byte growth would exceed byte quota, and whether local unreported growth is close enough to a quota ceiling to trigger early reporting. They are used by write/create paths to reject operations or accelerate quota accounting before the MDS sees stale client-side state.

`check_pool_perm()` adds an optional client-side data-pool permission probe. When `client_check_pool_perm` is enabled, it verifies that a regular file's layout pool and namespace permit read and/or write operations by issuing low-level Objecter operations to the first object and caching the result by `(pool_id, pool_ns)`.

The POSIX ACL helpers make the client honor ACL xattrs when `client_acl_type=posix_acl`. They evaluate access ACLs for permission checks, update ACL masks during chmod, and derive inherited access/default ACL xattrs during create. These helpers sit between ordinary VFS/libcephfs permission code and the xattr mutation path backed by MDS requests.

The Linux-only fscrypt block exposes key management and policy operations to libcephfs/FUSE callers. It stores and invalidates keys in the client-side `FSCryptKeyStore`, sets encryption policy xattrs on empty directories, retrieves policy from inode fscrypt context, reports encryption status and subvolume encryption tag, and returns key presence/user-count status.

The reclaim methods implement client session state takeover. `start_reclaim()` contacts every active MDS, asks whether it owns state for a previous client UUID, waits for replies, checks the old client is not blocklisted in the relevant OSD map epoch, and records a pending `reclaiming_uuid`. `finish_reclaim()` either clears per-session reclaim state or sends a finish message and promotes `reclaiming_uuid` to the active `uuid` metadata field.

The remaining helpers expose perf dump output, dynamic config observation, intrusive pointer hooks for `InodeRef`, random active MDS selection, subvolume metric aggregation, an fscrypt-aware `fcopyfile()` helper, and the `StandaloneClient` specialization that owns its `Objecter` lifecycle.

## Important APIs, Types, and Functions

Quota and pool-permission functions:

- `Client::is_quota_files_exceeded(Inode *in, const UserPerm& perms)` returns true if any relevant quota root has `quota.max_files` set and `rstat.rsize()` at or above that limit.
- `Client::is_quota_bytes_exceeded(Inode *in, int64_t new_bytes, const UserPerm& perms)` returns true if recursive bytes plus the proposed growth would exceed `quota.max_bytes`.
- `Client::is_quota_bytes_approaching(Inode *in, const UserPerm& perms)` compares local dirty growth, `in->size - in->reported_size`, against one-sixteenth of remaining quota space. It asserts `size >= reported_size`.
- `Client::check_pool_perm(Inode *in, int need)` expects `client_lock` to be held. It uses `POOL_CHECKED`, `POOL_CHECKING`, `POOL_READ`, and `POOL_WRITE` state bits in `pool_perms`, waits on `waiting_for_pool_perm` to serialize concurrent probes, and returns `-EPERM` or `-EIO` for missing or indeterminate access.

ACL functions:

- `_posix_acl_permission(const InodeRef& in, const UserPerm& perms, unsigned want)` delegates to `posix_acl_permits()` when `ACL_EA_ACCESS` exists, otherwise returns `-EAGAIN` so callers can fall back to mode-bit permission logic.
- `_posix_acl_chmod(const InodeRef& in, mode_t mode, const UserPerm& perms)` fetches xattrs with `_getattr(... CEPH_STAT_CAP_XATTR ...)`, adjusts the access ACL with `posix_acl_access_chmod()`, and persists it through `_do_setxattr()`.
- `_posix_acl_create(const InodeRef& dir, mode_t *mode, bufferlist& xattrs_bl, const UserPerm& perms)` inherits `ACL_EA_DEFAULT` from the parent directory, may emit `ACL_EA_ACCESS` and `ACL_EA_DEFAULT` into an encoded xattr map, and applies `umask_cb` only when no default ACL is present.

Client control and fscrypt functions:

- `set_filer_flags()` and `clear_filer_flags()` update Objecter global op flags under `client_lock`. Only `CEPH_OSD_FLAG_LOCALIZE_READS`, or zero for set, is accepted by assertion.
- `set_uuid()` and `set_session_timeout()` are pre-mount metadata setters guarded by `initialize_state`. `set_uuid()` closes sessions after changing metadata so future session opens use the new UUID.
- `add_fscrypt_key()`, `remove_fscrypt_key()`, `get_fscrypt_key_status()`, `set_fscrypt_policy_v2()`, `get_fscrypt_policy_v2()`, `is_encrypted()`, and low-level `ll_*` variants are Linux-only and map FUSE/ioctl-facing operations onto `FSCryptKeyStore`, `FSCryptContext`, and Ceph xattrs.
- `_is_empty_directory()` acquires `client_lock`, ensures shared directory caps or fetches them via `_ll_getattr()`, and checks `dirstat.nsubdirs | dirstat.nfiles`.
- `ll_set_fscrypt_policy_v2()` accepts only directories, treats an identical existing policy as success and a different one as `-EEXIST`, rejects unsupported policies, then writes `ceph.fscrypt.auth` and `ceph.fscrypt.file` using `CEPH_XATTR_CREATE`.

Reclaim, config, and diagnostics:

- `start_reclaim(const std::string& uuid, unsigned flags, const std::string& fs_name)` subscribes to an MDS map, opens sessions, checks `CEPHFS_FEATURE_RECLAIM_CLIENT`, sends `MClientReclaim`, waits on `waiting_for_reclaim`, validates OSD blocklist state, and records `metadata["reclaiming_uuid"]`.
- `finish_reclaim()` resets `MetaSession::reclaim_state` for all sessions and, when reclaim was started, sends `MClientReclaim("", FLAG_FINISH)` then updates `metadata["uuid"]`.
- `handle_client_reclaim_reply()` is the dispatch-side state update for `MClientReclaimReply`; it records `RECLAIM_OK`/`RECLAIM_FAIL`, maximum OSD epoch, target address vector, and signals waiters.
- `set_cap_epoch_barrier(epoch_t e)` updates `cap_epoch_barrier`, which later cap-release messages use to force the MDS to wait for an OSD map epoch after canceled RADOS operations.
- `get_perf_counters(bufferlist *outbl)` executes the admin-socket `perf dump` command in JSON form after checking the client is initialized.
- `get_tracked_keys()` returns the configuration keys this `md_config_obs_t` implementation observes. It contains a sorted static array and asserts sort order at compile time.
- `handle_conf_change(const ConfigProxy& conf, const std::set<std::string>& changed)` applies live config updates under `client_lock`, including permissions, ACL mode, LRU midpoint, ObjectCacher limits, metric collection, cap release delay, mount timeout, write-delay injection, subvolume snapshot visibility, and fscrypt alternate-name behavior.

Reference and metrics helpers:

- `intrusive_ptr_add_ref(Inode *in)` and `intrusive_ptr_release(Inode *in)` are free functions that integrate `InodeRef` intrusive pointers with `Inode::iget()` and `Client::put_inode()`.
- `_get_random_up_mds()` chooses a random rank from `mdsmap->get_up_mds_set()` while `client_lock` is held, or returns `MDS_RANK_NONE`.
- `SubvolumeMetricTracker` owns `inode_subvolume`, `subvolume_metrics`, `last_subvolume_metrics`, and `metrics_lock`. It maps inode IDs to subvolume inode IDs, aggregates `SimpleIOMetric` instances into `AggregatedIOMetrics`, and exposes current plus last metrics through `dump()`.

Copy and lifecycle:

- `Client::fcopyfile(const char *spath, const char *dpath, UserPerm& perms, mode_t mode)` path-walks the source without following symlinks, copies `fscrypt_auth` and `fscrypt_file` options into destination create calls, then handles symlinks with `readlink()`/`do_symlinkat()`, directories with `do_mkdirat()`, and regular files with `do_openat()`, `open()`, `read()`, and `write()`.
- `StandaloneClient::StandaloneClient()` constructs the base `Client` with a newly allocated `Objecter`, wires the messenger into `MonClient`, and sets client incarnation zero.
- `StandaloneClient::init()` performs `_pre_init()`, `objecter->init()`, messenger dispatcher registration, monitor initialization, authentication, `objecter->start()`, `_finish_init()`, and initialize-state transition. Error paths stop the timer, unlock, shut down Objecter/ObjectCacher/MonClient, and return the failure.
- `StandaloneClient::shutdown()` composes `Client::shutdown()` with `objecter->shutdown()` and `monclient->shutdown()`.

## Control Flow

Quota checks are intentionally thin. Each predicate passes a lambda to `check_quota_condition()`, defined just before this range, which walks from the current inode toward the root quota ancestor until a predicate is true or the root is reached. The bytes-approaching path first computes the client-local growth since the last reported size; if a quota root is already full it returns true, otherwise it treats less than one-sixteenth remaining space as approaching.

`check_pool_perm()` has two phases. First it checks fast exits: disabled config, non-regular file, cached result, or concurrent probe in progress. If another thread is checking the same pool/namespace, the caller waits and retries. If no cached result exists, snapshots are skipped because the write probe could create an orphan first object. For normal head files, the method marks the key `POOL_CHECKING`, issues a `stat` and a `create(true)` operation against the first object through `objecter->mutate()`, drops `client_lock` while waiting, reacquires it, translates `0`/`-ENOENT` into read permission and `0`/`-EEXIST` into write permission, and treats non-`EPERM` unexpected errors as indeterminate `-EIO`. Finally it compares the caller's requested capability mask against the cached bits.

The ACL create/chmod paths fetch xattrs before local manipulation so they work against current MDS state. Create inheritance follows POSIX ACL semantics: symlinks are excluded, the parent default ACL can modify the requested mode, an equivalent ACL may collapse into pure mode bits, directories inherit the default ACL, and only non-empty inherited maps are encoded into the create request bufferlist. In the no-default-ACL case, the client applies its registered umask callback.

Fscrypt policy setting starts from an fd wrapper or direct inode call, then enforces directory-only and empty-directory-only semantics. If the directory already has an fscrypt context, the requested policy is standardized before comparison so padding does not affect equality. New policy setup encodes a freshly initialized `FSCryptContext` with a generated nonce into `ceph.fscrypt.auth`, then initializes `ceph.fscrypt.file` to a zero `uint64_t` size record. Policy retrieval is the inverse: convert the inode context to `fscrypt_policy_v2`, reject non-v2 policies, or return `-ENODATA` if encryption is absent.

Fscrypt key management is local to the client process. `add_fscrypt_key()` creates a key handler and copies the kernel-style key identifier out when requested. `remove_fscrypt_key()` invalidates the key for a user and attempts to sync filesystem state when files are not busy, although the expression `kid->removal_status_flags & (FSCRYPT_KEY_REMOVAL_STATUS_FLAG_FILES_BUSY == 0)` deserves scrutiny because the comparison is evaluated before the bitwise operation. `get_fscrypt_key_status()` converts the user key specifier to a Ceph key identifier, looks it up in the key store, and reports ABSENT, INCOMPLETELY_REMOVED, or PRESENT plus user count.

`start_reclaim()` is a blocking state machine under `client_lock`, with deliberate unlock only while waiting for an OSD map epoch. It rejects uninitialized clients, empty UUIDs, and attempts to reclaim the active UUID. It subscribes to the requested filesystem's MDS map and waits for an epoch. For each in-MDS rank, it waits for the rank to be up, opens a session if needed, checks the MDS feature bit, sends reclaim messages while the session is `RECLAIM_NULL` or `RECLAIMING`, waits for `handle_client_reclaim_reply()`, returns on failure state, and advances only after success. When all ranks have answered, it requires some target address unless the reset flag allows `-ENOENT`; non-reset reclaim then waits for the reported OSD epoch and checks that the target addresses are not blocklisted before recording pending reclaim metadata.

Configuration updates are simple dispatch on changed key names. All mutations happen while holding `client_lock`, which matches ObjectCacher setter expectations and protects shared client state such as `client_permissions`, `acl_type`, and timing fields. The `conf` parameter is not used directly; the implementation reads current values from `cct->_conf`.

`SubvolumeMetricTracker::aggregate()` has two modes. Non-clean aggregation takes a shared lock, copies per-subvolume aggregate values into a result vector, and leaves current metrics in place. Clean aggregation swaps the entire `subvolume_metrics` map into a local temporary under a unique lock, then converts the temporary into result entries after releasing the lock. Both modes later take a unique lock again to store `last_subvolume_metrics` for diagnostic dump output.

`fcopyfile()` performs metadata-sensitive source inspection under `client_lock`, then uses public client methods for the actual IO and creation. For regular files it snapshots `srcin->size` before opening and then copies in up to 1 MiB chunks using explicit offsets. It exits through a local cleanup label that closes destination and, when opened, source file descriptors. Zero-length files create/truncate the destination but skip opening the source for read.

`StandaloneClient::init()` uses the initialization-state writer token to prevent concurrent initialization. It registers both Objecter and Client as messenger dispatchers after Objecter init and before monitor authentication. On monitor init or auth failure, it manually unwinds the partially initialized state because `_finish_init()` has not run.

## State and Persistence Behavior

Most persistent cluster-visible changes in this chunk go through existing MDS or OSD paths rather than writing local files. ACL chmod and fscrypt policy setup are persisted as xattr mutations sent to the MDS. `fcopyfile()` persists new dentries/inodes/data through the ordinary symlink, mkdir, open, read, and write client APIs. Pool-permission probes may create the first data object when write permission exists; this is why snapshot inodes bypass the check.

Client-local durable-for-session state includes:

- `pool_perms`, a process-local permission cache keyed by pool id and namespace. Indeterminate errors erase the key so a later operation can re-probe.
- `metadata`, which carries session metadata such as `uuid`, `timeout`, and temporary `reclaiming_uuid`.
- `reclaim_errno`, `reclaim_osd_epoch`, `reclaim_target_addrs`, and every `MetaSession::reclaim_state`, which drive the reclaim state machine.
- `cap_epoch_barrier`, used later when sending cap releases.
- runtime booleans and limits updated by `handle_conf_change()`.
- `SubvolumeMetricTracker` maps and `last_subvolume_metrics`, all in-memory and reset only by clean aggregation, inode removal, or client teardown.
- the client-side `FSCryptKeyStore`; key presence is not a cluster xattr and must be supplied per client process.

Locking is central. Many entry points assert or acquire `client_lock`. `check_pool_perm()` deliberately unlocks while waiting for Objecter completions to avoid blocking unrelated client work. `_is_empty_directory()`, fscrypt xattr tag lookups, config updates, random MDS selection, and StandaloneClient init use explicit locking. `SubvolumeMetricTracker` uses a separate `std::shared_mutex`, which keeps metrics updates independent from the main client lock.

Initialization and mount state are enforced with `RWRef_t` guards. `set_uuid()` and `set_session_timeout()` assert the pre-mount initialized state. `sync_fs()` and xattr low-level wrappers outside this range use mount-state readers; fscrypt fd wrappers rely on valid file handles, while direct `ll_*` fscrypt methods operate on caller-supplied inodes.

## Dependencies and Integration Points

This code integrates with the CephFS MDS through `MetaRequest`, xattr operations, `MClientReclaim`, `MClientReclaimReply`, MDS feature bits, `MetaSession`, and `MDSMap`. Reclaim depends on session opening, MDS map subscription, `waiting_for_mdsmap`, `waiting_for_reclaim`, and connection-bound session lookup.

It integrates with RADOS through `Objecter`, `ObjectOperation`, `OSDMap::file_to_object_locator()`, `SnapContext`, `C_SaferCond`, `objecter->wait_for_map()`, and `objecter->with_osdmap()`. The pool permission probe and reclaim blocklist check are the main OSD-facing actions in this chunk.

It integrates with the object cache and cap flushing indirectly. `remove_fscrypt_key()` may call `sync_fs()`, whose earlier implementation flushes ObjectCacher data, caps, mdlog, cap releases, unsafe requests, and waits for cap flush acknowledgement. `handle_conf_change()` directly updates ObjectCacher limits.

It integrates with Linux fscrypt and FUSE ioctl handling through `fscrypt_uapi.h`, `FSCrypt`, `FSCryptContext`, `FSCryptKeyStore`, `fscrypt_policy_v2`, `fscrypt_remove_key_arg`, and `fscrypt_get_key_status_arg`. `fuse_ll.cc` calls these client methods for fscrypt policy/key ioctls.

It integrates with POSIX ACL parsing and rewriting through `posix_acl.cc` helpers and the `ACL_EA_ACCESS`/`ACL_EA_DEFAULT` xattr names. The xattr API must permit these names even though `_listxattr()` filters internal `ceph.` names elsewhere.

Subvolume metrics tie into earlier inode update, cap removal, read, and write paths. Inode-to-subvolume mappings are added when inode metadata carries a subvolume ID, removed on cap release paths, and metrics are added by read/write completion paths. Periodic global metrics collection calls `aggregate(true)` in earlier code before sending metrics to the MDS.

`StandaloneClient` is the libcephfs-style client specialization for callers that do not supply an externally managed Objecter. It depends on Messenger, MonClient, Objecter, ObjectCacher, timer, authentication, and dispatcher ordering.

## Risks and Edge Cases

`check_pool_perm()` can have observable side effects because the write probe uses `create(true)` against the file's first object. The snapshot bypass avoids orphan object creation, but head-file probes may still create an object earlier than user data would. The permission result is cached by pool and namespace, so permission changes during a client lifetime may not be noticed unless other code clears `pool_perms`.

The permission probe serializes concurrent checks with `POOL_CHECKING`, but it releases `client_lock` during OSD waits. The inode layout values are copied before unlock, which is good; however, callers must tolerate that the inode or session state may have changed by the time the lock is reacquired. The code signals all waiters on both success and indeterminate failure.

Quota checks depend on current recursive stats and snapshot realm ancestry. If `rstat`, `reported_size`, or quota-root cache state is stale, the helpers may be conservative or late. `is_quota_bytes_approaching()` asserts `size >= reported_size`, so any accounting regression that violates that invariant will abort debug builds.

ACL helpers return `-EAGAIN` when no ACL should be applied, not success. Callers must preserve that contract. Create-mode changes happen through a `mode_t *`, so errors after `posix_acl_inherit_mode()` can leave the local mode value modified even though no create request is emitted by this helper.

The fscrypt status/tag helpers set the local pointer variable `enctag = nullptr` on errors or non-encrypted files, which does not clear the caller's buffer or pointer because it is passed by value. Callers should rely on the return code rather than expecting pointer nulling to escape. The tag lookup also uses `sizeof(enctag)`, which is the size of the pointer parameter, not the backing buffer length; that limits copied tag bytes and is a likely bug surface.

`remove_fscrypt_key()` has a suspicious busy-files condition: `FSCRYPT_KEY_REMOVAL_STATUS_FLAG_FILES_BUSY == 0` is a boolean expression, so the bitwise `&` is probably not checking the intended flag. If the intent was "sync when files are not busy," the expression should be validated against Linux fscrypt semantics.

`ll_set_fscrypt_policy_v2()` writes two xattrs sequentially. If `ceph.fscrypt.auth` succeeds and `ceph.fscrypt.file` fails, the directory may be left partially marked with encryption auth data. Recovery behavior depends on MDS/xattr semantics outside this chunk.

`start_reclaim()` waits while holding `client_lock` for MDS map changes, session open contexts, and reclaim replies. That matches existing client wait helpers, but it is sensitive to correct signaling in map/session/message handlers. Reclaim target fields are not obviously reset at the start except `reclaim_errno`; stale `reclaim_target_addrs` or `reclaim_osd_epoch` should be considered when reviewing repeated reclaim attempts.

`SubvolumeMetricTracker::remove_inode()` removes only the inode-to-subvolume mapping. It does not erase the subvolume entry or decrement any aggregate when the last inode leaves, so empty subvolume metric buckets can persist until clean aggregation swaps the map away.

`fcopyfile()` has several correctness edges. It does not check for negative `readlink()` before using `linkpath[link_size]`, it uses a fixed 4096-byte symlink buffer, it snapshots the source size before copying without handling concurrent truncation/growth, and after each read it sets the next requested read length to the previous return length. Short reads before EOF could therefore reduce future chunk size and still loop until the original size is reached. The TODO-style comment notes that size should be reverified. It also returns `0` for unsupported source types other than symlink, directory, or regular file.

`StandaloneClient::init()` has manual cleanup paths for partial initialization. Any future addition to `_pre_init()` or Objecter/MonClient startup must be mirrored in both failure branches to avoid leaked threads, timers, or dispatchers.

## Test Signals

High-signal coverage for this chunk would include:

- Quota tests with root and nested quota realms covering file-count limit, byte-growth rejection, and approaching-threshold behavior when `size - reported_size` crosses one-sixteenth remaining space.
- Pool permission tests with `client_check_pool_perm` enabled for read-only, write-only, no-access, and transient OSD error cases, including concurrent callers waiting on `POOL_CHECKING` and snapshot inodes skipping the probe.
- POSIX ACL tests for permission fallback (`-EAGAIN`), chmod ACL mask updates, create inheritance from default ACL, directory default ACL propagation, symlink exclusion, equivalent-ACL mode collapse, and umask application only when no default ACL exists.
- Fscrypt ioctl/FUSE tests for adding/removing keys, absent/present/incompletely-removed key status, setting policy on non-directories and non-empty directories, idempotent same-policy set, different-policy `-EEXIST`, unsupported cipher/policy `-EINVAL`, and `ENODATA` for unencrypted inodes.
- Failure-injection tests for the two-step fscrypt xattr creation path, especially auth success followed by file-size xattr failure.
- Reclaim tests with multiple MDS ranks: rank down then map update, session open wait, missing `CEPHFS_FEATURE_RECLAIM_CLIENT`, successful replies with increasing OSD epochs, failure replies carrying errno, reset-mode `-ENOENT`, target blocklisted `-ENOTRECOVERABLE`, and finish messages updating metadata.
- Runtime config tests proving `handle_conf_change()` updates every tracked key and ObjectCacher receives size/object/dirty/age changes under lock.
- Subvolume metric tests for add duplicate inode, add metric for unmapped inode, clean vs non-clean aggregation, `last_subvolume_metrics` dump, and inode removal before later metrics.
- `fcopyfile()` tests for symlink, directory, empty file, encrypted source metadata propagation, regular data copy, read/write errors, long symlink/readlink failure, and concurrent source size changes.
- Standalone client init tests or fault injection around `monclient->init()` and `authenticate()` failures to verify timer shutdown, Objecter shutdown, ObjectCacher stop, MonClient shutdown, and initialize-state behavior.

Existing source-visible test hooks are mostly indirect: `fuse_ll.cc` exercises fscrypt methods for ioctls, `posix_acl.cc` supplies ACL parser semantics, earlier `Client.cc` read/write paths feed subvolume metrics, and admin-socket/perf dump can observe metrics and counters. A merged research pass should look for repository-local QA files outside this source snapshot if available; the checked tree paths for `qa`, `src/test`, and `src/pybind` were absent under `sources/distributed-fs/ceph`.

## Cross-Chunk Notes

The immediately preceding code defines `get_quota_root()` and `check_quota_condition()`, which are essential to the first three functions in this chunk. Earlier chunks also define `_sync_fs()`, `_listxattr()`, `_removexattr()`, `_flush()`, `_fsync()`, `path_walk()`, `do_openat()`, `do_mkdirat()`, `do_symlinkat()`, read/write methods, MDS map subscription, session opening, and message dispatch that calls `handle_client_reclaim_reply()`.

This range reaches the end of `Client.cc`; there is no later chunk needed for function closure. The final per-file document should merge this late-file material with the earlier initialization, mount/session, cap, xattr, IO, and request machinery so the helper dependencies are not duplicated or left dangling.
