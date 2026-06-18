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
