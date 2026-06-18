# subset-b-009829 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_ceph_snapshots.c -->
# sources/user-network-fs/samba/source3/modules/vfs_ceph_snapshots.c

## Purpose
`vfs_ceph_snapshots.c` exposes CephFS snapshots as SMB Previous Versions while remaining independent from the Ceph userspace VFS module. It is designed to work on kernel-mounted CephFS shares by discovering Ceph's per-directory snapshot namespace, defaulting to `.snap`, and translating SMB time-warped `@GMT` requests into the backing snapshot paths. The module both enumerates snapshots through the shadow-copy VFS hook and protects snapshot paths from mutation by returning read-only style errors for write operations.

## Important APIs, Types, And Functions
The exported VFS table is `ceph_snap_fns`, registered as `ceph_snapshots`. Its most important hooks are `get_shadow_copy_data_fn`, path translation wrappers for `stat`, `lstat`, `openat`, `chdir`, `readlinkat`, `realpath`, `get_real_filename_at`, and guard wrappers for mutating operations such as `renameat`, `linkat`, `symlinkat`, `unlinkat`, `mkdirat`, `mknodat`, `fchmod`, `fntimes`, `fchflags`, and `fsetxattr`.

`ceph_snap_get_btime_fsp()` reads the Ceph virtual xattr `ceph.snap.btime` and parses `seconds.nanoseconds` into a one-second timestamp. `ceph_snap_fill_label()` opens an individual snapshot directory entry by pathref and formats the btime as a `@GMT-%Y.%m.%d-%H.%M.%S` label. `ceph_snap_enum_snapdir()` opens the `.snap` directory with Samba directory helpers, verifies `SEC_DIR_LIST`, counts entries, and optionally fills labels. `ceph_snap_get_parent_path()` calculates the directory whose `.snap` namespace should be searched and rejects absolute parents outside `conn->connectpath`.

`ceph_snap_gmt_convert_dir()` searches a particular `<dir>/<snapdir>` for a snapshot whose btime matches a requested `twrp` timestamp. `ceph_snap_gmt_convert()` first treats the name as a directory with its own `.snap`, then falls back to the parent `.snap` and appends the trimmed basename for files or inherited child paths. `ceph_snap_gmt_strip_snapshot()` treats nonzero `smb_filename->twrp` as the source of the `@GMT` request.

## Control Flow
Shadow-copy enumeration starts at `ceph_snap_get_shadow_copy_data()`. For directory fsp values it enumerates `<dir>/<snapdir>`; for files it computes the parent directory and enumerates that parent snapshot namespace. Enumeration relies on `OpenDir()`, `ReadDirName()`, `dir_hnd_fetch_fsp()`, `smbd_check_access_rights_fsp()`, `vfs_stat()`, `openat_pathref_fsp()`, and `SMB_VFS_NEXT_FGETXATTR()`. For labels, every child snapshot entry is opened and mapped to Ceph btime.

Access to a previous version flows through `smb_filename->twrp`. Read-style operations convert the path and temporarily call the next VFS implementation with the converted backing name or synthetic pathref. Write-style operations check for a nonzero timestamp and fail with `EROFS`; cross-version renames fail as `EXDEV` or `EROFS` depending on source or destination. Non-time-warped calls fall straight through to the next module.

## State And Persistence
The module keeps no durable private state. Snapshot identity and labels are derived on demand from CephFS directory entries and the `ceph.snap.btime` xattr. The only configuration read is `ceph:snapdir`, defaulting to `.snap`. Output labels lose subsecond precision, so multiple Ceph snapshots in the same second can collide at the SMB label layer.

## Dependencies And Integration Points
This module depends on Samba's VFS dispatch macros, `struct smb_filename`, `files_struct`, shadow-copy structures, pathref helpers, directory helpers from `source3/smbd/dir.h`, access checks, and CephFS' virtual btime xattr. It deliberately sets `getxattrat_send/recv` to not implemented for time-warped paths, avoiding ambiguous xattr access through snapshots.

## Risks
The largest behavioral risk is timestamp collision: Ceph supports subsecond snapshots, but SMB labels only carry whole seconds. Snapshot lookup is O(number of snapshots) for every conversion and can be expensive in large `.snap` directories. Path conversion mutates temporary `base_name` values before dispatching to the next module; callers must preserve errno and lifetimes carefully. The module assumes the Ceph btime xattr exists; old CephFS versions cannot enumerate or access snapshots through this path. Parent fallback means inherited snapshot contents depend on Ceph semantics and the child existing at snapshot creation.

## Test Signals
Useful tests include Previous Versions enumeration with and without labels, permission-denied `.snap` directories, configurable `ceph:snapdir`, file and directory `@GMT` opens, inherited child lookup through parent snapshots, write attempts under `@GMT` paths returning `EROFS`, rename from snapshot returning `EXDEV`, collision behavior for same-second snapshots, and absence or malformed `ceph.snap.btime` xattrs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_ceph_snapshots.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_commit.c -->
# sources/user-network-fs/samba/source3/modules/vfs_commit.c

## Purpose
`vfs_commit.c` implements a Samba VFS module that periodically commits dirty file data to stable storage. It is meant to reduce data loss and smooth writeback load without requiring synchronous I/O on every write. The module is configured per share with `commit:dthresh`, `commit:eof mode`, and `commit:debug`.

## Important APIs, Types, And Functions
The private `struct commit_info` is stored as a per-fsp extension and tracks dirty bytes, dirty threshold, EOF behavior, and expected EOF. `enum eof_mode` has `EOF_NONE`, `EOF_HINTED`, and `EOF_GROWTH`. `commit_do()` calls `fdatasync()` when available, otherwise `fsync()`, and resets dirty bytes on success. `commit_all()` flushes any pending dirty bytes at close. `commit()` updates counters and decides whether threshold or EOF conditions require a sync.

`commit_openat()` creates the fsp extension for writable opens if threshold or EOF mode is enabled, then delegates to `SMB_VFS_NEXT_OPENAT()`. `commit_pwrite()` and the async `commit_pwrite_send/recv()` wrap writes and call `commit()` for successful writes. `commit_ftruncate()` updates EOF tracking after truncation or extension. The registered VFS table is `vfs_commit_fns`.

## Control Flow
Connect first delegates and then reads the module debug level. On writable open, the module reads `commit:dthresh` through `conv_str_size()` and `commit:eof mode` from smb.conf. EOF tracking is initialized lazily: before the first write, `SMB_VFS_NEXT_FSTAT()` captures the current file size as the expected EOF. Each successful write increments `dbytes`; if `dbytes > dthresh`, the module commits immediately. EOF modes commit when `offset + bytes_written` reaches the expected EOF. In hinted mode this happens once, then EOF tracking is disabled; in growth mode the expected EOF advances with file growth.

The async write path delegates to the next module asynchronously, then performs the commit synchronously in the completion callback. The callback uses `fh_get_pos(fsp->fh)` as the offset argument, which is a notable semantic difference from the synchronous path's explicit offset.

## State And Persistence
All state is per-open-file and stored in the Samba VFS fsp extension. No module state survives close except data that was actually synced to disk. `commit_close()` attempts to flush outstanding dirty data but deliberately ignores commit errors, relying on close to surface writeback problems.

## Dependencies And Integration Points
The module depends on Samba VFS extension helpers, `tevent_req`, `struct vfs_aio_state`, `lp_parm_*` configuration accessors, and platform `fdatasync`/`fsync`. It sits above the default or storage-specific VFS module and operates on `fsp_get_io_fd()`.

## Risks
Threshold comparison uses `>` rather than `>=`, so exactly equal dirty byte counts do not flush. Async writes perform a blocking commit inside a completion callback, which can add latency to the event loop. EOF inference depends on client size hints and current stat information, so sparse, out-of-order, or concurrent writes can produce surprising commit timing. If no sync primitive is available the module logs a warning and treats commit as successful. Dirty byte accounting adds `ssize_t` values into `size_t`; only positive writes call `commit()`, but overflow on very long sessions remains a theoretical concern.

## Test Signals
Tests should cover threshold-triggered sync, no extension for read-only opens, hinted EOF commit after writing the declared size, growth mode after extension, truncation updating EOF, close-time flush, simulated fsync failure propagation on writes, and async pwrite completion behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_commit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_crossrename.c -->
# sources/user-network-fs/samba/source3/modules/vfs_crossrename.c

## Purpose
`vfs_crossrename.c` adds a fallback for `renameat()` calls that fail with `EXDEV`, allowing small regular files to be moved across filesystem boundaries by copy-then-unlink. It is intended as a compatibility shim for shares spanning mount points, not as a full atomic cross-device rename implementation.

## Important APIs, Types, And Functions
`crossrename_connect()` reads `crossrename:sizelimit` in MiB and stores a module-global byte limit. `copy_reg()` performs the fallback copy for regular files: it validates the source stat, enforces the size limit, unlinks any destination, opens source and destination relative to pathref directory fds, copies bytes with `transfer_file()`, copies ownership, mode, and timestamps, closes both fds, and unlinks the source through the next VFS layer. `crossrename_renameat()` profiles the operation, calls `SMB_VFS_NEXT_RENAMEAT()`, and invokes `copy_reg()` only on `EXDEV`.

## Control Flow
The normal path is a direct pass-through rename. Named streams are rejected with `ENOENT`. If the lower module returns `EXDEV`, the fallback first removes the destination unless it does not exist, then copies the source file to a new destination opened with `O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW` and mode `0600`. Metadata is restored after the data copy, then the source is unlinked. Any NTSTATUS failure is mapped back to errno for the VFS return.

## State And Persistence
The only state is `module_sizelimit`, a process-global value updated on connect from share configuration. File data and metadata are persisted by normal filesystem writes; there is no journal or rollback state. Partial destination files can remain if the copy fails after destination creation.

## Dependencies And Integration Points
This module depends on Samba pathref fds (`fsp_get_pathref_fd()`), `SMB_VFS_NEXT_RENAMEAT()`, `SMB_VFS_NEXT_UNLINKAT()`, profiling macros, `transfer_file()`, and POSIX `openat`, `fchown`, `fchmod`, and `futimens`. It uses the lower VFS only for rename and unlink; the copy itself uses direct syscalls.

## Risks
The fallback is not atomic and can expose partial destination content or lose the original destination after an interrupted operation. `how` flags such as no-replace are not re-applied in the fallback path. The module-global size limit can be problematic if multiple shares with different settings are served by the same process. ACLs, xattrs, alternate streams, and Samba-specific metadata are not copied. Error cleanup closes descriptors but does not remove partial destination files.

## Test Signals
Tests should simulate `EXDEV`, verify size-limit enforcement, confirm metadata preservation for uid/gid/mode/timestamps where permitted, ensure non-regular files and streams fail, exercise destination pre-existence and unlink failures, and check behavior when copy or close fails mid-operation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_crossrename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_default.c -->
# sources/user-network-fs/samba/source3/modules/vfs_default.c

## Purpose
`vfs_default.c` is Samba's terminal VFS module. It supplies a concrete implementation for every VFS hook, mostly by wrapping local POSIX/syscall behavior with Samba path, security, profiling, async, DFS, ACL, xattr, durable-handle, and FSCTL semantics. `vfs_default_init()` asserts that the function table is complete before registering `DEFAULT_VFS_MODULE_NAME`.

## Important APIs, Types, And Functions
The central export is `vfs_default_fns`, a full `struct vfs_fn_pointers`. Connect-time initialization sets `conn->have_proc_fds` and enables `openat2()` resolve constraints (`VFS_OPEN_HOW_RESOLVE_NO_SYMLINKS`, `VFS_OPEN_HOW_RESOLVE_NO_XDEV`) unless disabled by build or share options. Disk hooks implement free-space, quotas, statvfs, capabilities, DFS referral read/create, and unsupported snapshot creation/deletion. Directory hooks wrap `fdopendir`, `readdir`, `rewinddir`, `mkdirat`, and `closedir`.

File hooks cover `openat`, `create_file`, close, sync and async pread/pwrite/fsync, seek, sendfile/recvfile, rename, stat family calls, allocation-size calculation, unlink, chmod/chown/time changes, truncate/fallocate, locks, leases, symlink/readlink/link/mknod, realpath, file-id creation, stream info, byte-range locking, parent-path calculation, name translation, FSCTL dispatch, DOS attributes, offload copy, compression stubs, POSIX and NT ACLs, xattrs, AIO policy, and durable handles.

Key internal async state structs include `vfswrap_pread_state`, `vfswrap_pwrite_state`, `vfswrap_fsync_state`, `vfswrap_get_dos_attributes_state`, `vfswrap_offload_read_state`, `vfswrap_offload_write_state`, and `vfswrap_getxattrat_state`.

## Control Flow
Most wrappers profile the operation, assert that unsupported stream cases do not reach raw syscalls, call the POSIX or Samba helper, and return errno/NTSTATUS in the expected VFS form. `vfswrap_openat()` validates resolve flags, uses `openat2()` for symlink and xdev restrictions, falls back to `openat()`, handles `O_PATH` pathrefs, temporarily becomes root where pathref emulation requires it, and records whether `/proc/self/fd` fallback is available for the fsp.

Async pread, pwrite, and fsync create tevent requests and schedule pthreadpool jobs. If thread creation returns `EAGAIN`, they fall back to synchronous work to keep serving clients. The getxattr-at implementation either performs synchronous fgetxattr or uses per-thread cwd and credentials when the platform supports them. The DOS attribute async path reads `SAMBA_XATTR_DOS_ATTRIB`, retries as root on access denied, parses the blob, and optionally adds `FILE_ATTRIBUTE_OFFLINE` from DMAPI.

`vfswrap_fsctl()` handles sparse setting, object IDs, reparse points, shadow-copy data marshalling, find-files-by-SID placeholder success, allocated ranges dummy data, and selected unsupported operations. Shadow-copy marshalling delegates to `SMB_VFS_GET_SHADOW_COPY_DATA()`, making modules such as `vfs_ceph_snapshots` visible to SMB clients.

Server-side copy uses an offload token database. `vfswrap_offload_read_send()` creates/stores a token. `vfswrap_offload_write_send()` validates offsets, token handles, source size, and lock conflicts, then tries reflink or `copy_file_range()` before falling back to an async read/write loop that switches user/service context between source and destination fsp values.

## State And Persistence
Persistent filesystem state is delegated to local filesystems, xattrs, ACLs, reparse metadata, and durable-handle cookies. Process-level state includes `vfswrap_logged_ioctl_message`, the static offload token context, and a static `try_copy_file_range` flag that disables future copy-file-range attempts after unsupported errors. Per-request async state is talloc-owned and protected by destructors that prevent cancellation while pthread jobs may still reference memory.

## Dependencies And Integration Points
This file is integrated with nearly every smbd subsystem: loadparm, profiling, DFS parsing, security descriptors, POSIX ACL mapping, xattr DOS attributes, DMAPI offline status, pthreadpool/tevent, strict byte-range locks, offload-token database, durable handle helpers, reparse point helpers, and platform wrappers from `lib/util/sys_rw.h`, `system/filesys.h`, and `lib/util/statvfs.h`. All higher VFS modules ultimately rely on these default hooks if they call `SMB_VFS_NEXT_*`.

## Risks
Because this is the terminal VFS, incorrect errno mapping or incomplete hook coverage affects the whole server. Several operations intentionally use compatibility approximations: allocated ranges report whole-file allocation, find-files-by-SID returns success without enumerating files, default stream info only reports `::$DATA`, and compression is unsupported. Pathref fallbacks can degrade from handle-based to path-based operations when proc-fds are unavailable. Async xattr support depends on platform thread credential semantics. Server-side copy must maintain user context and strict locks across source and destination services. The static `try_copy_file_range` switch is process-wide and may suppress future fast paths after one unsupported filesystem result.

## Test Signals
High-value tests include complete VFS hook registration, `openat2()` resolve success/fallback/ENOSYS behavior, pathref chmod/chown/xattr with and without proc-fds, async read/write/fsync fallback on pthreadpool pressure, DFS symlink creation and parsing, FSCTL shadow-copy marshalling, sparse/object-id/reparse FSCTLs, strict allocate truncate, offload token creation and copy fallback, DOS xattr parsing with access-denied retry, durable disconnect/reconnect cookies, ACL get/set wrappers, and errno preservation around context changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_default.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_default_quota.c -->
# sources/user-network-fs/samba/source3/modules/vfs_default_quota.c

## Purpose
`vfs_default_quota.c` lets Samba expose and store Windows default quota values on filesystems that only support user and group quota records. It maps default user or group filesystem quota operations to a configured real user or group quota record, root by default.

## Important APIs, Types, And Functions
The module registers `get_quota_fn` and `set_quota_fn` as `default_quota`. Configuration macros read `default_quota:uid`, `default_quota:uid nolimit`, `default_quota:gid`, and `default_quota:gid nolimit`. `default_quota_get_quota()` delegates the requested quota lookup, then rewrites default quota requests to read the configured uid/gid quota record while preserving qflags. `default_quota_set_quota()` blocks writes to the configured uid/gid when the `nolimit` option is set and mirrors default FS quota updates into the configured uid/gid quota record.

## Control Flow
For ordinary user/group quota queries the module returns the next module result, except configured storage IDs can be reported as no-limit. For `SMB_USER_FS_QUOTA_TYPE`, it reads `SMB_USER_QUOTA_TYPE` for the configured uid. When group quotas are compiled in, the same pattern applies to group defaults. Set operations first reject protected configured IDs when `nolimit` is enabled, delegate the original set to the next module, and then, for default FS quota types, writes the same disk quota to the configured uid/gid record.

## State And Persistence
The module has no private memory state. Persistence is the underlying quota database: default quota values are stored by updating a real quota record. The mapping target is read from smb.conf on each operation through macros.

## Dependencies And Integration Points
It depends on Samba quota types (`SMB_QUOTA_TYPE`, `unid_t`, `SMB_DISK_QUOTA`), `SMB_QUOTAS_SET_NO_LIMIT()`, group quota compile guards, and next VFS quota hooks. It is usually stacked above a quota-capable module or the default sysquota implementation.

## Risks
The module uses real uid/gid quota records as metadata storage, so choosing an enforced account can affect actual quota behavior. The initial set delegates the default quota type to the lower layer before writing the configured record; lower layers that reject default FS quota types may prevent the mirror write. `return -1` paths for protected IDs do not consistently set errno in the module itself. Group quota behavior is conditional on compile-time support.

## Test Signals
Tests should verify default user quota read/write mapping, protected uid/gid no-limit behavior, qflags preservation, configured non-root uid/gid records, group quota builds, lower-layer ENOSYS propagation, and Windows Explorer default quota UI behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_default_quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_delay_inject.c -->
# sources/user-network-fs/samba/source3/modules/vfs_delay_inject.c

## Purpose
`vfs_delay_inject.c` is a test VFS module that injects configurable delays into selected VFS calls. It is used to exercise races, timeout paths, async I/O sequencing, and byte-range-lock retry behavior without changing the storage backend.

## Important APIs, Types, And Functions
`inject_delay()` reads `delay_inject:<vfs_func>` in milliseconds and sleeps synchronously. `vfs_delay_inject_fntimes()` uses it for timestamp changes. Async read/write wrappers define `vfs_delay_inject_pread_state` and `vfs_delay_inject_pwrite_state`; send functions either delegate immediately or first schedule `tevent_wakeup_send()`, then call the next async VFS operation. Receive functions return the stored result and `vfs_aio_state`.

Byte-range locking uses `struct vfs_delay_inject_brl_lock_state`, a global `brl_lock_states` DLIST, and optional tevent timers. `vfs_delay_inject_brl_lock_windows()` delays a particular lock request identified by `brl_req_guid()`, returns `NT_STATUS_RETRY` while pending, and eventually delegates to the next lock implementation. `vfs_delay_inject_brl_lock_timer()` wakes share-mode waiters when the delay expires.

## Control Flow
For async pread and pwrite, configuration keys `delay_inject:pread_send` and `delay_inject:pwrite_send` control whether a wakeup timer is inserted before `SMB_VFS_NEXT_PREAD_SEND()` or `SMB_VFS_NEXT_PWRITE_SEND()`. Timer failure maps to `EIO`. Completion callbacks copy the lower result into the wrapper state and mark the request done.

For Windows byte-range locks, the first call for a request GUID allocates state under the request memory context, records the target expiration time, and optionally creates a global-event-context timer if `delay_inject:brl_lock_windows_use_timer` is true. While the timer exists, the module returns retry with `smblctx = 0`; without a timer but before expiration, it returns retry with `smblctx = UINT64_MAX`. After expiration the state is freed and the lock is passed down.

## State And Persistence
Delay configuration is read dynamically from smb.conf. Async request state is transient. Byte-range delay state is global in-process until its talloc owner is freed or expiration occurs; the destructor removes it from the global list. Nothing is persisted.

## Dependencies And Integration Points
The module depends on tevent wakeups/timers, Samba global event context, byte-range lock APIs, share-mode wakeups, VFS async pread/pwrite APIs, and `smb_msleep()`. It should be stacked above modules whose behavior needs delay simulation.

## Risks
Synchronous delay injection blocks the smbd worker. Global `brl_lock_states` must be kept consistent with request lifetime. Timer wakeups depend on global event context behavior. Negative or very large configured delays are not locally validated. Async delay wrappers preserve the lower `vfs_aio_state`, but injected wakeup failures collapse to `EIO`.

## Test Signals
Tests should set per-function delays and verify elapsed timing, ensure zero delay delegates immediately, exercise async pread/pwrite callbacks, simulate wakeup failure, test byte-range lock retry and eventual success with timer and non-timer modes, and verify state cleanup when lock requests are cancelled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_delay_inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_dfs_samba4.c -->
# sources/user-network-fs/samba/source3/modules/vfs_dfs_samba4.c

## Purpose
`vfs_dfs_samba4.c` retrieves DFS referrals from Samba AD data using Samba4 libraries. It lets smbd answer DFS referral requests from directory service state and falls back to the next VFS implementation when AD lookup reports not found.

## Important APIs, Types, And Functions
`struct dfs_samba4_handle_data` stores an event context, loadparm context, and SAM database LDB context. `dfs_samba4_connect()` delegates connect, allocates handle data, initializes an s4 event context, initializes loadparm with s3 helpers, and connects to samdb using a system session. `dfs_samba4_get_referrals()` calls `dfs_server_ad_get_referrals()` with the remote client address and request structure. The module registers `connect`, `disconnect`, and `get_dfs_referrals` hooks.

## Control Flow
Connect setup is all-or-fail: on any allocation or initialization failure it calls the next disconnect and returns `-1`. Referral lookup fetches handle data, logs the requested DFS name, calls the AD DFS server helper, and falls back to `SMB_VFS_NEXT_GET_DFS_REFERRALS()` only when the helper returns `NT_STATUS_NOT_FOUND`. Other errors are returned directly; success returns `NT_STATUS_OK`.

## State And Persistence
The handle state is allocated per connection under `handle->conn`. Persistent DFS data is not stored by this module; it lives in AD/SAMDB. The module registers a custom debug class at init and falls back to `DBGC_VFS` if registration fails.

## Dependencies And Integration Points
Dependencies include Samba4 event and auth/session libraries, loadparm, SAMDB, DFS NDR structures, `dfs_server_ad_get_referrals()`, and smbd connection state. It bridges source3 VFS request handling with source4 AD DFS implementation.

## Risks
Failure paths call next disconnect but rely on talloc ownership for cleanup before handle data is installed. Runtime availability of SAMDB and system session context is mandatory. Only `NT_STATUS_NOT_FOUND` falls back; LDAP, auth, or parse errors surface directly to clients. The debug message on successful class registration says `fileid`, likely a copy/paste cosmetic issue.

## Test Signals
Tests should cover successful AD referral lookup, not-found fallback to default DFS links, samdb connection failure, loadparm/event initialization failure, remote address handling, custom debug class registration, and service disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_dfs_samba4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_dirsort.c -->
# sources/user-network-fs/samba/source3/modules/vfs_dirsort.c

## Purpose
`vfs_dirsort.c` provides sorted directory listings by caching all entries from an opened directory and returning them in case-insensitive name order. It is a presentation-layer module for clients or tests that expect stable sorted enumeration.

## Important APIs, Types, And Functions
`struct dirsort_privates` tracks a linked list node per open directory, current position, cached `struct dirent` array, entry count, directory mtime, underlying `DIR *`, and either fsp or smb filename identity. `compare_dirent()` uses `strcasecmp_m()`. `open_and_sort_dir()` reads all entries through `SMB_VFS_NEXT_READDIR()`, grows the cache in 4096-entry increments after an initial 64, and sorts with `TYPESAFE_QSORT()`. `dirsort_fdopendir()`, `dirsort_readdir()`, `dirsort_rewinddir()`, and `dirsort_closedir()` implement the VFS hooks.

## Control Flow
On fdopendir, the module opens the lower directory, reads and sorts it immediately, links the private node into handle data, and returns the lower `DIR *`. On each readdir, it finds the node by `DIR *`, checks current directory mtime, and if changed rewinds and rebuilds the sorted cache. It then returns the next cached entry. Rewind only resets the cached position. Closedir removes the node, calls lower closedir, and frees cache state.

## State And Persistence
State is per-open-directory and stored as a linked list in VFS handle data. It is memory-only and freed on closedir. The only freshness signal is directory mtime.

## Dependencies And Integration Points
The module depends on Samba VFS directory hooks, talloc, DLIST macros, `vfs_stat_fsp()`, `SMB_VFS_STAT()`, and Samba's locale-aware case-insensitive comparison. It wraps lower directory behavior and does not change create/delete operations.

## Risks
Large directories can consume significant memory because every `struct dirent` is cached. Freshness depends on mtime granularity and filesystem behavior. Copying `struct dirent` by value assumes fixed storage is adequate for the platform layout. If cache rebuilding fails after an mtime change, the old state may be partly disrupted. The struct contains an `smb_fname` path mode that is not populated by this implementation, suggesting legacy or incomplete opendir support.

## Test Signals
Tests should enumerate unsorted directories, verify case-insensitive order, handle rewind, close multiple directories out of order, mutate a directory during enumeration and confirm refresh, exercise very large directories, and check memory cleanup on lower open or sort failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_dirsort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_error_inject.c -->
# sources/user-network-fs/samba/source3/modules/vfs_error_inject.c

## Purpose
`vfs_error_inject.c` is a test module that injects configured Unix errors or panic behavior into selected VFS paths. It is used to exercise client/server error handling for stale handles, access denial, read-only filesystems, interruption, durable reconnect mismatch, and related fault paths.

## Important APIs, Types, And Functions
`unix_error_map_array` maps string names to errno values: `ESTALE`, `EBADF`, `EINTR`, `EACCES`, and `EROFS`. `inject_unix_error()` reads `error_inject:<vfs_func>`, returns a mapped errno, or calls `smb_panic()` for `panic`. Wrappers exist for `chdir`, `pwrite`, `openat`, `unlinkat`, and `durable_reconnect`.

`vfs_error_inject_openat()` has separate keys for `openat` and `openat_create`; create injection only fires for non-existing `O_CREAT` targets. It avoids injecting into pathref directory opens. `vfs_error_inject_unlinkat()` injects only when the parent directory is not owned by the current user. `vfs_error_inject_durable_reconnect()` decodes the default durable cookie and can modify `stat_info.st_ex_nlink` before passing it down.

## Control Flow
Each simple wrapper checks configuration and either sets errno/returns failure or delegates. The open wrapper first tests create-specific behavior with `SMB_VFS_FSTATAT()`, then calculates whether the generic open error applies based on fsp pathref state and directory-open flags. Unlink builds a full path, resolves the parent, stats it, and lets owner-matching callers proceed without injection. Durable reconnect uses NDR pull/push for `vfs_default_durable_cookie`, validates magic/version, mutates supported fields, and delegates with the modified blob.

## State And Persistence
There is no persistent state. Configuration is read per call. Durable reconnect mutation affects only the request cookie passed down, not stored server state directly.

## Dependencies And Integration Points
The module depends on Samba loadparm, VFS path helpers, parent pathname resolution, default durable cookie NDR definitions, and errno/NTSTATUS mapping. It is explicitly tied to the default durable cookie format for the reconnect injection path.

## Risks
Only a small errno vocabulary is supported. Unknown configured strings log errors but then delegate normally, which can hide misconfigured tests. `fake` open behavior is careful around pathrefs, but new open flag combinations could bypass or over-apply injection. The durable reconnect path must track default cookie format changes. The panic option is intentionally disruptive.

## Test Signals
Tests should verify every mapped errno on each hook, unknown strings, panic behavior in controlled environments, create-only open injection, pathref directory opens bypassing injection, unlink parent-owner bypass, durable reconnect `st_ex_nlink` mutation, and default delegation when unset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_error_inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_expand_msdfs.c -->
# sources/user-network-fs/samba/source3/modules/vfs_expand_msdfs.c

## Purpose
`vfs_expand_msdfs.c` rewrites MSDFS referral targets based on the client's IP address. It supports referral strings containing `@mapfile@`, where the map file contains IP prefixes and replacement host strings, allowing clients to be directed to nearby DFS targets.

## Important APIs, Types, And Functions
`read_target_host()` opens the map file, scans `IP-prefix whitespace expansion` lines, and returns the first expansion whose prefix matches the client address. `expand_msdfs_target()` parses the `@...@` segment, converts backslashes to slashes for absolute map file paths, gets the remote address from `conn->sconn->remote_address`, reads the target host, applies Samba substitution with `talloc_sub_full()`, and replaces the `@...@` segment in the referral target. `expand_read_dfs_pathat()` wraps the `read_dfs_pathat` VFS hook.

## Control Flow
The module always delegates to `SMB_VFS_NEXT_READ_DFS_PATHAT()` first. If the caller is only checking whether a DFS link exists, it returns the delegated status unchanged. If referrals were returned, it iterates over `alternate_path` entries and expands only entries containing `@`. Any expansion failure frees the referral list, sets count to zero, and returns `NT_STATUS_NO_MEMORY`.

## State And Persistence
The module stores no state. Map files on disk are read for each expansion. Target substitutions use current connection/session data such as service name, unix name, connect path, gid, sanitized username, and domain.

## Dependencies And Integration Points
It depends on Samba MSDFS referral parsing, `struct referral`, tsocket remote address helpers, source3 substitution helpers, loadparm substitution state, and the lower `read_dfs_pathat` implementation from default or other DFS modules.

## Risks
The map parser accepts only space as the delimiter, not arbitrary whitespace before the first separator. Prefix matching is first-match and string-based, so ordering in the map file is security and routing significant. Map file paths come from DFS link content after slash conversion; deployments must control who can write those links. A lookup miss is reported as no memory in the wrapper, conflating configuration misses with allocation failures. The function mutates the target string in place by writing NUL at the first `@`.

## Test Signals
Tests should cover map lookup order, default blank-prefix entries, client IP variations, substitution variables, malformed map lines, missing map files, referrals with and without `@`, check-only calls with null referral outputs, and multiple referral entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_expand_msdfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_extd_audit.c -->
# sources/user-network-fs/samba/source3/modules/vfs_extd_audit.c

## Purpose
`vfs_extd_audit.c` logs selected file operations to syslog and Samba debug logs. It is an auditing wrapper for connection lifecycle, mkdir, open, close, rename, unlink, and chmod operations.

## Important APIs, Types, And Functions
`audit_syslog_facility()` maps `extd_audit:facility` strings to platform syslog facility constants, defaulting to `LOG_USER`. `audit_syslog_priority()` maps `extd_audit:priority`, defaulting to `LOG_NOTICE` and falling back to `LOG_WARNING` on invalid selection. Hook wrappers `audit_connect()`, `audit_disconnect()`, `audit_mkdirat()`, `audit_openat()`, `audit_close()`, `audit_renameat()`, `audit_unlinkat()`, and `audit_fchmod()` delegate to the next VFS module and log operation names, paths, fds, modes, and failures.

## Control Flow
Connect delegates first, then calls `openlog()` and emits a connect record if Samba syslog logging is enabled. Most operation wrappers build a full path where needed, call the lower VFS function, then log success or failure. `audit_renameat()` preserves errno across logging and talloc cleanup. Disconnect logs before delegating. Init registers a custom debug class.

## State And Persistence
The module has no per-handle state. Syslog output is external persistent audit evidence depending on system logger configuration. The debug class id is process-global.

## Dependencies And Integration Points
It depends on syslog, Samba loadparm `lp_syslog()`, path conversion helpers, VFS next hooks, and debug class registration. It is intended to be stacked near the top of a VFS chain so it observes client-facing operations after earlier modules have transformed paths if ordered that way.

## Risks
Audit coverage is selective, not comprehensive. Some logging uses high-severity debug macros such as `DBG_ERR` for unlink even on normal operations, which can be noisy. `audit_openat()` combines `fsp->fsp_name` and the input name in a way that can produce confusing path text. Logging after the operation means failed path allocation prevents the audited operation rather than just suppressing logging. Sensitive paths and usernames may be emitted to syslog.

## Test Signals
Tests should verify facility/priority parsing, connect/disconnect logs, errno preservation on rename failure, operation logs for success and failure, behavior when `lp_syslog()` disables syslog, path allocation failures, and custom debug class registration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_extd_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_fake_acls.c -->
# sources/user-network-fs/samba/source3/modules/vfs_fake_acls.c

## Purpose
`vfs_fake_acls.c` is a test-oriented module that stores fake ownership and POSIX ACL data in xattrs rather than relying on real filesystem ownership/ACL changes. It lets Windows ACL and ownership behavior be exercised on filesystems or test setups where real Unix metadata should not be changed.

## Important APIs, Types, And Functions
The module uses xattrs `system.fake_uid`, `system.fake_gid`, `system.fake_access_acl`, and `system.fake_default_acl`. `fake_acls_fuid()`, `fake_acls_fgid()`, and `fake_acls_fuidgid()` read fake uid/gid values from xattrs. `fake_acls_fstatat()`, `fake_acls_stat()`, `fake_acls_lstat()`, and `fake_acls_fstat()` overlay stat uid/gid with fake values when available. `fake_acls_blob2acl()` and `fake_acls_acl2blob()` serialize `struct smb_acl_t` through NDR. `fake_acls_sys_acl_get_fd()`, `fake_acls_sys_acl_set_fd()`, and `fake_acls_sys_acl_delete_def_fd()` implement ACL storage in xattrs.

Ownership hooks `fake_acls_lchown()` and `fake_acls_fchown()` write fake uid/gid xattrs, with a current-user check for uid changes. `fake_acl_process_chmod()` rewrites ACL entries to reflect chmod user/mask/other mode changes, adding a mask entry if missing. `fake_acls_fchmod()` first delegates chmod to preserve special bits, then updates the stored fake access ACL if present. `fake_acls_connect()` installs a recursion guard struct for pathref handling.

## Control Flow
Stat wrappers first call the next stat implementation. For fsp-backed names they read xattrs from `metadata_fsp()`. For path-only fstatat, the module may need to open a pathref fsp to access xattrs; it uses `filename_convert_dirfsp_rel()` and a `calling_pathref_fsp` guard to avoid recursion when that helper itself stats paths. Failure to obtain a pathref after a successful lower stat is treated as absence of fake uid/gid, with a debug message.

ACL get grows a temporary blob buffer until `FGETXATTR` no longer returns `ERANGE`, then NDR-decodes it. ACL set NDR-encodes the ACL and writes the configured xattr. Chmod updates fake ACL permissions after the real chmod call. Connect allocates handle data after lower connect succeeds.

## State And Persistence
Fake metadata is persisted in filesystem xattrs. The only memory state is the per-handle recursion guard. Fake ownership and ACLs are independent of real filesystem ownership and may diverge intentionally.

## Dependencies And Integration Points
The module depends on Samba xattr VFS hooks, pathref and filename conversion helpers, NDR ACL definitions, POSIX ACL helper APIs, current security token helpers, and metadata fsp handling for streams. It wraps stat, ACL, chmod, and chown paths while delegating most storage operations.

## Risks
The `system.*` xattr namespace may require elevated privileges or be unavailable on some filesystems. `fake_acls_lchown()` returns `EACCES` as a positive integer instead of setting errno and returning `-1`, which is suspicious for VFS error conventions. Pathref fallback intentionally ignores some errors, which is acceptable for tests but can hide metadata issues. ACL blobs depend on Samba's NDR shape. Real chmod still executes, so mode bits are not purely fake.

## Test Signals
Tests should cover fake uid/gid stat overlays, fsp and path-only fstatat, recursion guard behavior, xattr absence, malformed ACL blobs, ACL set/get/delete default ACL, chmod ACL permission rewriting including mask creation, fchown/lchown privilege checks, stream metadata behavior, and filesystems without `system.*` xattr support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_fake_acls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_fake_dfq.c -->
# sources/user-network-fs/samba/source3/modules/vfs_fake_dfq.c

## Purpose
`vfs_fake_dfq.c` is a testing module that fakes disk-free, quota, and selected stat values from smb.conf parameters keyed by real path. It helps tests simulate quota and capacity conditions without changing the underlying filesystem.

## Important APIs, Types, And Functions
`dfq_load_param()` builds a parametric key of the form `<section>/<param>/<path>` under `fake_dfq`. `dfq_disk_free()` resolves the real path, reads `df/block size`, `df/disk free`, and `df/disk size`, and either returns fake values or delegates. `dfq_get_quota()` resolves real path, selects sections `u<uid>`, `g<gid>`, `udflt`, or `gdflt`, reads quota fields, and supports injected `err` (`ENOTSUP`) and `nosys` (`ENOSYS`). `dfq_fake_stat()` can set a fake setgid group using `stat/sgid/<path>`. Stat wrappers apply that fake stat overlay after lower stat success.

## Control Flow
Disk-free and quota operations first call `SMB_VFS_NEXT_REALPATH()` to normalize the path used in configuration keys. If no block size is configured, they delegate to the next module. Otherwise, disk-free fills the caller's block size/free/size fields and returns free space in 1 KiB units. Quota fills `SMB_DISK_QUOTA` fields from parameters after zeroing the structure. Stat hooks delegate, then use `full_path_tos()` and `dfq_load_param()` to optionally force group and setgid bits.

## State And Persistence
The module has no private state. Fake values persist only as smb.conf parameters. No filesystem quota or stat data is modified.

## Dependencies And Integration Points
It depends on VFS realpath, disk-free, quota, and stat hooks; Samba loadparm parametric options; `SMB_DISK_QUOTA`; and full-path helpers. It is intended for tests stacked above the real backend.

## Risks
Configuration keys include full real paths, which can be brittle across path canonicalization changes or mount layout changes. `dfq_disk_free()` divides by `(1024 / bsize)` when block size is below 1024, so unusual non-divisor block sizes would produce inaccurate math. A configured quota block size of zero delegates, so explicit zero cannot be tested as a returned value. Stat fake group id zero is treated as absent.

## Test Signals
Tests should verify fake disk-free math for block sizes below and above 1024, realpath fallback to next module, every quota type and field, injected ENOTSUP/ENOSYS, stat setgid overlay on stat/fstat/lstat/fstatat, path-key stability, and delegation when parameters are absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_fake_dfq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_fake_perms.c -->
# sources/user-network-fs/samba/source3/modules/vfs_fake_perms.c

## Purpose
`vfs_fake_perms.c` is a simple testing module that makes all reported files look owned by the current session user/group and mode `0700`, preserving directory type bits for directories. It does not modify underlying filesystem permissions.

## Important APIs, Types, And Functions
`fake_perms_stat()` wraps `SMB_VFS_NEXT_STAT()` and rewrites `smb_fname->st`. `fake_perms_fstat()` wraps `SMB_VFS_NEXT_FSTAT()` and rewrites the returned stat buffer. Both use `handle->conn->session_info->unix_token` when available, or `geteuid()`/`getegid()` for artificial connections such as DFS.

## Control Flow
Each hook delegates first and exits on lower error. On success, directory modes become `S_IFDIR | S_IRWXU`; non-directories become `S_IRWXU`. The uid/gid are replaced with the connected user's unix token if present.

## State And Persistence
There is no private state and no persistent change. Only returned stat structures are modified.

## Dependencies And Integration Points
The module depends on Samba stat VFS hooks, `connection_struct` session info, security unix tokens, and POSIX mode macros. It is often used in test shares where permission checks should be simplified at the metadata reporting layer.

## Risks
Only `stat` and `fstat` are wrapped; callers using `lstat` or `fstatat` may see real permissions. Non-directory file type bits are discarded when mode is set to `S_IRWXU`, which may make symlinks, devices, or FIFOs appear as regular permission bits without type. Artificial connection fallback may not match intended SMB user identity.

## Test Signals
Tests should verify stat and fstat overlays for files and directories, uid/gid from session token, artificial connection fallback, lower error propagation, and contrast with unwrapped lstat/fstatat behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_fake_perms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_fileid.c -->
# sources/user-network-fs/samba/source3/modules/vfs_fileid.c

## Purpose
`vfs_fileid.c` changes how Samba constructs `struct file_id` keys used by share-mode and byte-range-lock databases. It supports device-id mapping algorithms for clustered, mounted, or otherwise unstable device number environments, and can mark selected paths/inodes as "nolock" by assigning an external id.

## Important APIs, Types, And Functions
`struct fileid_handle_data` stores the chosen mapping function, allow/deny lists for filesystem type and mount directory, cached mount entries, and nolock configuration. Mount metadata is represented by `struct fileid_mount_entry`; nolock entries use `struct fileid_nolock_inode`.

Mapping algorithms include `fileid_mapping_fsname()` using a hash of mount fsname, `fileid_mapping_fsid()` using `statfs().f_fsid`, `fileid_mapping_hostname()` using hostname plus device, and `fileid_mapping_next_module()` delegating to the lower VFS. `fileid_find_mount_entry()` lazily loads `/etc/mtab` through `fileid_load_mount_entries()` and applies allow/deny filters. `fileid_mapping_nolock_extid()` derives an extid from slot, CTDB virtual node number, and hostname. `fileid_file_id_create()` calls the configured mapping function and applies nolock extid when appropriate.

## Control Flow
On connect, the module delegates first, allocates handle state, reads `fileid:mapping` as legacy fallback and `fileid:algorithm` as the preferred setting, and selects mapping behavior. Algorithms such as `fsname_nodirs`, `hostname`, `fsname_norootdir`, and `fsname_norootdir_ext` also set nolock flags or root-dir nolock behavior. It then copies fstype/mntdir allow/deny lists, reads `nolock_all_inodes`, `nolock_all_dirs`, `nolock_max_slots`, legacy `nolockinode`, rootdir nolock, and `nolock_paths`. Path-based nolock entries are resolved relative to the share connect path and added by stat.

When Samba asks for a file id, `fileid_file_id_create()` retrieves handle data, maps the device id/inode, and if `extid` is still zero and the inode matches nolock rules, sets `extid` to the configured derived value.

## State And Persistence
State is per VFS handle and includes cached `/etc/mtab` entries. The cache reloads when a device is not found. There is no persistent repository state; behavior depends on current mount table, hostname, CTDB VNN, process id for slot selection, and smb.conf settings.

## Dependencies And Integration Points
The module depends on `/etc/mtab`, `getmntent()`, `stat()`, `statfs()`, `gethostname()`, CTDB `get_my_vnn()`, Samba VFS file-id hooks, loadparm string lists, and share-mode/locking consumers of `struct file_id`. It can also delegate to a lower file-id implementation with `next_module`.

## Risks
File ID stability is critical; changing algorithms or mount identifiers can invalidate locking/share-mode assumptions. Hashes of fsname or hostname/device can collide in theory. `/etc/mtab` may be incomplete or container-specific. The hostname algorithm forces all inodes into nolock extid behavior, which changes lock database partitioning. `nolock_max_slots` uses `getpid() % max_slots`, so process distribution affects extid. Allow/deny filters compare exact strings only. Legacy `nolockinode` ignores device by setting dev zero.

## Test Signals
Tests should cover every algorithm, mount allow/deny filtering, mtab reload after a miss, fsname `/dev/` stripping, fsid packing/hash behavior, hostname failure handling, nolock all-inodes/all-dirs/rootdir/path/legacy inode modes, max-slot extid distribution, next-module delegation, and stable file ids across reconnect where expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_fileid.c -->
