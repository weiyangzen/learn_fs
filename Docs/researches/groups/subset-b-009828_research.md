# subset-b-009828 research

Grouped research for Samba VFS modules covering audit logging, Btrfs features, cache priming, CAP/CATIA filename translation, and the legacy/new CephFS libcephfs backends. Each source section is bounded for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_audit.c -->
# sources/user-network-fs/samba/source3/modules/vfs_audit.c

## Purpose
`vfs_audit.c` is a small Samba VFS module that logs selected share and file operations to syslog. It wraps the next VFS implementation for connect, disconnect, mkdir, open, close, rename, unlink, and chmod, emitting an audit record that includes the target path, file descriptor where available, failure status, and `errno` text.

## Important APIs, types, and functions
- `audit_syslog_facility()` maps the `audit:facility` smb.conf parameter through platform-available `LOG_*` values, defaulting to `LOG_USER`.
- `audit_syslog_priority()` maps `audit:priority` to syslog priorities, defaulting to `LOG_NOTICE` and falling back to `LOG_WARNING` for invalid values.
- `audit_connect()` delegates to `SMB_VFS_NEXT_CONNECT()`, calls `openlog("smbd_audit", LOG_PID, facility)`, and logs the service/user connection.
- `audit_mkdirat()`, `audit_renameat()`, and `audit_unlinkat()` build displayable full paths with `full_path_from_dirfsp_atname()` before delegating.
- `audit_openat()`, `audit_close()`, and `audit_fchmod()` log handle-oriented operations using `fsp_str_dbg()`, `fsp_get_pathref_fd()`, and `fsp->fsp_name`.
- `vfs_audit_fns` registers the wrapped VFS entry points, and `vfs_audit_init()` registers the module under the name `audit`.

## Control flow
The module is a pass-through wrapper. Each operation calls the corresponding `SMB_VFS_NEXT_*` function, then logs success or failure. Path-based operations first allocate full `smb_filename` objects so the log line records the resolved path rather than only the relative component. `audit_renameat()` preserves the original failure `errno` across talloc cleanup so callers see the next-module error unchanged. `audit_connect()` only starts syslog logging after the lower connect succeeds; `audit_disconnect()` logs before passing disconnect down the stack.

## State and persistence behavior
There is no persistent module-owned state. Configuration is read dynamically from loadparm for each log event, and all durable output is external syslog data. Temporary `smb_filename` allocations are freed after each operation. The module does not alter file state except through the delegated VFS calls.

## Dependencies and integration points
The module depends on Samba's VFS dispatch layer, `smbd/smbd.h`, loadparm helpers, talloc-backed `smb_filename` helpers, and the platform syslog API. It is declared in `source3/modules/wscript_build` as `vfs_audit` and integrates by adding `audit` to a share's `vfs objects`.

## Risks and edge cases
- Logging happens after most file operations, so failure logging depends on preserving `errno` correctly; `audit_mkdirat()` and `audit_unlinkat()` do not explicitly save `errno` across `syslog()`/cleanup.
- Log contents include raw paths and user/service names, so deployments must treat syslog as sensitive audit data.
- Facility availability is compile-time platform dependent because many `LOG_*` values are guarded by `#ifdef`.
- The module covers only a small set of operations and should not be mistaken for complete file activity auditing.

## Test signals
There are no targeted tests for this file in the inspected module tree. Practical validation is configuration-driven: load the module on a test share, exercise connect/open/close/create/rename/unlink/chmod paths, and confirm syslog facility/priority mapping plus error propagation. Build registration in `wscript_build` is the static integration signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_btrfs.c -->
# sources/user-network-fs/samba/source3/modules/vfs_btrfs.c

## Purpose
`vfs_btrfs.c` exposes Btrfs-specific behavior to Samba shares. It advertises compression/block-refcounting support, maps SMB compression requests to Linux inode flags, and optionally implements Samba snapshot create/delete hooks using Btrfs subvolume ioctls with `@GMT-` names compatible with shadow-copy consumers.

## Important APIs, types, and functions
- `btrfs_fs_capabilities()` extends downstream filesystem capabilities with `FILE_FILE_COMPRESSION` and `FILE_SUPPORTS_BLOCK_REFCOUNTING`.
- `btrfs_fget_compression()` reads `FS_IOC_GETFLAGS` and reports `COMPRESSION_FORMAT_LZNT1` when `FS_COMPR_FL` is set, using `/proc/self/fd` for pathref handles when available.
- `btrfs_set_compression()` reads and writes `FS_COMPR_FL` with `FS_IOC_GETFLAGS` and `FS_IOC_SETFLAGS`.
- `btrfs_snap_check_path()` accepts only Btrfs subvolume roots when `btrfs:manipulate snapshots = yes`; otherwise it delegates to the next VFS module.
- `btrfs_gen_snap_dest_path()` generates `@GMT-%Y.%m.%d-%H.%M.%S` names in UTC.
- `btrfs_snap_create()` uses `BTRFS_IOC_SNAP_CREATE_V2`, optionally setting `BTRFS_SUBVOL_RDONLY` for read-only snapshots.
- `btrfs_snap_delete()` validates the snapshot basename with `strptime()` and destroys it with `BTRFS_IOC_SNAP_DESTROY`.
- `vfs_btrfs_init()` registers the module as `btrfs`.

## Control flow
Capability and compression calls are direct wrappers around Linux ioctl state. Compression get handles normal file descriptors first, then pathref descriptors via `/proc` if Samba recorded proc-fd support. Compression set requires a usable IO fd and accepts `NONE`, `DEFAULT`, or `LZNT1`, using Samba's compression constants as SMB-facing signals rather than Btrfs algorithm selectors.

Snapshot hooks are gated by `btrfs:manipulate snapshots`. When disabled, all snapshot operations pass through to the next VFS module. When enabled, `snap_check_path` verifies the share path is a directory with inode `256`, matching Btrfs subvolume root convention. Create opens the source subvolume and destination directory, fills the Btrfs ioctl argument with the source fd and generated subvolume name, temporarily escalates with `become_root()`, and returns both base and snapshot paths. Delete splits `snap_path` with `dirname()`/`basename()`, confirms the basename matches the exact Samba shadow-copy timestamp format, then performs the destroy ioctl as root.

## State and persistence behavior
The module persists changes in filesystem metadata: compression inode flags and Btrfs subvolumes. It stores no long-lived in-memory state. Snapshot timestamps are encoded in directory names, making the snapshot namespace itself the persistence layer.

## Dependencies and integration points
This file depends on Linux `FS_IOC_*` flags, Btrfs ioctl ABI structs/constants, Samba VFS snapshot hooks, `become_root()` privilege handling, talloc, and timestamp utilities. It is registered as `vfs_btrfs` in `wscript_build`; consumers usually combine it with snapshot-aware clients or Samba shadow-copy logic.

## Risks and edge cases
- The compression mapping reports Btrfs compression as `LZNT1`, which is a Windows-facing compatibility value and not a Btrfs algorithm choice.
- `btrfs_set_compression()` debug messages appear inverted: clearing compression says "setting compression" and setting `FS_COMPR_FL` says "clearing compression".
- Snapshot manipulation requires root and can destroy subvolumes; the strict name-format check reduces but does not remove operational risk.
- Subvolume detection by inode `256` follows Btrfs convention but is still a filesystem-specific assumption.
- Large fixed ioctl name buffers are intentionally not fully zeroed; name length checks must remain correct.

## Test signals
No direct tests were found in this subset. Useful validation requires a Btrfs-backed share: check advertised SMB capabilities, query/set compression through SMB, create read-only and read-write snapshots with `btrfs:manipulate snapshots = yes`, reject non-subvolume paths, and ensure malformed snapshot names are not deleted. Build registration in `wscript_build` is the static integration signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_btrfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_cacheprime.c -->
# sources/user-network-fs/samba/source3/modules/vfs_cacheprime.c

## Purpose
`vfs_cacheprime.c` is a performance-oriented Samba VFS module that primes the kernel buffer cache before file reads or `sendfile()` transfers. It performs large sequential `pread()` calls, intended to match RAID stripe widths, so later zero-copy or ordinary reads have lower latency.

## Important APIs, types, and functions
- `READAHEAD_MIN` and `READAHEAD_MAX` clamp configured read-ahead size between 128 KiB and 100 MiB.
- Global `g_readsz` and `g_readbuf` hold the process-wide read-ahead buffer and size.
- `prime_cache()` stores per-file-handle progress in a VFS fsp extension of type `off_t`, reads from the file with `sys_pread()`, and disables further read-ahead for that handle on read failure by setting `*last = -1`.
- `cprime_connect()` reads `cacheprime:debug` and `cacheprime:rsize`, allocates the global buffer once, and then delegates connect.
- `cprime_sendfile()` primes only when `offset == 0`, then delegates `SMB_VFS_NEXT_SENDFILE()`.
- `cprime_pread()` primes before all delegated preads when the global buffer exists.
- `vfs_cacheprime_init()` registers the module as `cacheprime`.

## Control flow
On the first successful connect in an smbd process, the module parses `cacheprime:rsize`, clamps it, and allocates one global buffer. Later connects in the same process do not reallocate or resize the buffer, even if share configuration differs, to avoid corrupting concurrent users. During reads, `prime_cache()` creates or fetches a per-fsp offset marker. If the current cached range already covers the requested offset/count, it skips work. Otherwise it reads `g_readsz` bytes starting at the last primed offset, advances the marker by the number of bytes actually read, and lets the original VFS operation proceed.

## State and persistence behavior
State is entirely in-process and non-persistent. `g_readbuf` and `g_readsz` are shared by all connections handled by the process. Each open file handle has its own fsp extension tracking the last primed offset or `-1` to suppress future attempts after an error. The module never changes file contents.

## Dependencies and integration points
The module depends on Samba VFS fsp extensions, loadparm module parameters, `sys_pread()`, and delegated `sendfile`/`pread` VFS operations. It is registered in `source3/modules/wscript_build` as `vfs_cacheprime` and is configured with `cacheprime:rsize` and `cacheprime:debug`.

## Risks and edge cases
- The global buffer is process-wide, so different shares in the same process cannot safely use different read-ahead sizes after the first allocation.
- `prime_cache()` uses `VFS_ADD_FSP_EXTENSION()` as though it returns a usable initialized `off_t`; the initial marker value depends on Samba extension allocation semantics.
- Large configured sizes can allocate up to 100 MiB per smbd process.
- On systems where `pread` is emulated with seek/read/seek, the module can be counterproductive, as the source comment warns.
- The module can perform extra I/O for workloads that do not benefit from sequential readahead.

## Test signals
No direct automated tests were found. Validation should compare read/sendfile latency and backend disk I/O with and without the module, test min/max `cacheprime:rsize` clamping, verify no repeated priming for already covered ranges, and confirm read errors disable further priming per file handle. Build registration in `wscript_build` is the static integration signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_cacheprime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_cap.c -->
# sources/user-network-fs/samba/source3/modules/vfs_cap.c

## Purpose
`vfs_cap.c` implements Samba's legacy CAP filename encoding module. It maps bytes with the high bit set to a `:xx` hexadecimal representation before passing paths to the underlying filesystem, and decodes directory entries back for SMB clients. This supports environments that need CAP-style storage names for non-ASCII byte values.

## Important APIs, types, and functions
- `capencode()` converts every byte `>= 0x80` to `:<lower-hex><lower-hex>`.
- `capdecode()` converts `:xx` sequences back to bytes using `hex_byte()`.
- Path wrappers such as `cap_mkdirat()`, `cap_openat()`, `cap_fstatat()`, `cap_stat()`, `cap_lstat()`, `cap_unlinkat()`, `cap_lchown()`, `cap_chdir()`, `cap_mknodat()`, and `cap_realpath()` encode names before delegating.
- Link and symlink wrappers encode both source/target and destination components as needed.
- `cap_readdir()` delegates `READDIR`, decodes `d_name`, and returns a talloc-backed replacement `struct dirent`.
- `cap_fgetxattr()`, `cap_fremovexattr()`, and `cap_fsetxattr()` encode xattr names before delegation.
- `cap_create_dfs_pathat()` and `cap_read_dfs_pathat()` encode DFS reparse/symlink paths and preserve returned stat information.
- `vfs_cap_fns` registers the wrappers and explicitly marks async getxattr-at as not implemented.

## Control flow
Most entry points allocate an encoded name under `talloc_tos()`, construct or copy an `smb_filename`, replace `base_name`, call the next VFS operation, and restore/preserve `errno` where the code expects cleanup to run after failure. Operations that receive directory-relative names sometimes build full paths first and then delegate relative to `conn->cwd_fsp`, preserving the historical CAP behavior of encoding the complete backing-store path. Directory reads run in the reverse direction: they fetch the next entry, decode the exposed name, copy the `dirent`, and substitute the decoded `d_name`.

## State and persistence behavior
The persistent state is encoded filenames on the backing filesystem. The module has no durable configuration or cache. Temporary encoded/decoded strings and synthetic `smb_filename` objects are talloc-scoped. Because filenames are stored encoded, disabling the module changes what names clients see and which paths operations resolve.

## Dependencies and integration points
The module depends on Samba VFS path helpers, `synthetic_smb_fname()`, `synthetic_pathref()`, `full_path_from_dirfsp_atname()`, fsp structures, and hexadecimal utility functions. It is registered in `wscript_build` as `vfs_cap` and loaded with `vfs objects = cap`.

## Risks and edge cases
- `capdecode()` treats any colon as a hex tag and advances three bytes without validating that two hex digits follow, so literal colon names or malformed CAP names can decode unexpectedly.
- CAP encoding is byte-oriented, not Unicode-aware, and can conflict with modern filename normalization expectations.
- Some functions preserve `errno` carefully, while others return after talloc cleanup without saving it consistently.
- Several operations use full-path encoding and `cwd_fsp`, which can be sensitive to directory handle semantics.
- `cap_linkat()` has duplicated `TALLOC_FREE(old_full_fname)` calls, harmless under talloc but a maintenance smell.

## Test signals
No targeted tests were found in the inspected tree. Useful tests should create filenames containing high-bit bytes, verify backing-store `:xx` names, list through Samba and confirm decoded names, exercise rename/link/symlink/DFS/xattr paths, and include malformed colon sequences. Build registration in `wscript_build` is the static integration signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_catia.c -->
# sources/user-network-fs/samba/source3/modules/vfs_catia.c

## Purpose
`vfs_catia.c` maps filenames between Windows-visible names and Unix backing-store names for applications such as CATIA that use characters forbidden by Windows clients. It is a broad VFS wrapper that applies configured character mappings to pathname arguments, stream names, xattr names, DFS paths, and the `files_struct` names used by fd-oriented operations.

## Important APIs, types, and functions
- `struct share_mapping_entry` caches parsed `catia:mappings` for global and per-share configuration.
- `struct catia_cache` stores original and mapped `files_struct` `base_name` pointers, alternate stream base names, and recursion state.
- `init_mappings()` loads and caches share-level mappings, falling back to global mappings.
- `catia_string_replace_allocate()` delegates to `string_replace_allocate()` for `vfs_translate_to_unix` and `vfs_translate_to_windows` directions.
- `catia_translate_name()` provides the VFS translate-name hook and returns mapped names when lower modules do not.
- `CATIA_FETCH_FSP_PRE_NEXT()` and `CATIA_FETCH_FSP_POST_NEXT()` temporarily replace `fsp->fsp_name->base_name` with the Unix-mapped name before fd-based downstream calls, then restore it.
- Direct pathname wrappers cover open, rename, stat/lstat/fstatat, unlink, lchown, mkdir, chdir, realpath, xattr names, DFS paths, and stream info.
- Fd-based wrappers cover read/write, async read/write, fsync, fstat, truncate, fallocate, locks, sharemode, leases, ACLs, DOS attributes, compression, and fsctl.
- `vfs_catia_init()` registers the module as `catia` and creates a custom debug class.

## Control flow
On connect, the module disables `smbd async dosmode` because it does not provide async DOS attribute fetch hooks. For path operations, the usual flow is to map the incoming Windows-visible `base_name` to the Unix backing name, create a temporary `smb_filename`, and delegate to the next VFS module. Directory and fd-based operations are harder because downstream modules inspect the existing `files_struct`; `catia_fetch_fsp_pre_next()` creates or validates an fsp extension, stores original pointers, swaps in mapped pointers, and marks the cache busy. The post hook restores original pointers and clears the busy marker. Recursion is explicitly detected; validated recursive calls can reuse the mapped state, while changed names force a temporary cache.

Stream handling gets special treatment. `catia_fstreaminfo()` maps the base path to Unix for the lower stream query, then maps each returned stream name back to the Windows-visible form while preserving `:$DATA` suffixes. Async pread/pwrite/fsync keep the mapped fsp state active until the lower async request completes, then restore in the completion callback before marking the request done.

## State and persistence behavior
Mappings are cached in the static `srt_head` list for the lifetime of the process. Per-open-file mapping state lives in VFS fsp extensions and is removed with the fsp. No separate metadata is persisted; the backing filesystem sees mapped Unix names, and SMB clients see reverse-mapped Windows names. The module can make durable name changes through create, rename, link, symlink, DFS, xattr, and stream operations.

## Dependencies and integration points
The module depends on Samba's VFS dispatch layer, fsp extensions, `string_replace.h`, talloc, tevent request APIs, ACL/DOS attribute hooks, and path helpers. `vfs_fruit.c` comments explicitly mention using CATIA mappings for Apple illegal character handling, and `wscript_build` registers `vfs_catia`.

## Risks and edge cases
- The module relies on pointer identity in `files_struct` names to validate cache safety; external mutation of those pointers can force cache recreation or trigger panic paths.
- Async operations must restore mapped fsp names exactly once after lower completion; mistakes can leak Unix names into SMB-facing state.
- Share/global mapping cache is static and not invalidated on runtime configuration changes.
- Mapping collisions are possible if two Windows-visible names map to the same Unix name or vice versa.
- Disabling async DOS mode is necessary for correctness but can affect performance.
- Many VFS operations are wrapped; any new operation that uses names but is not added here can bypass translation.

## Test signals
No dedicated CATIA tests were found in this subset. High-value tests should configure representative `catia:mappings`, create and list names containing Windows-forbidden characters, exercise rename/link/symlink/streams/xattrs/ACLs/DOS attributes, cover alternate streams, and force nested VFS calls to validate recursion protection. Build registration and the `vfs_fruit.c` integration note are static signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_catia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_ceph.c -->
# sources/user-network-fs/samba/source3/modules/vfs_ceph.c

## Purpose
`vfs_ceph.c` is the legacy Samba VFS backend for CephFS via the userspace `libcephfs` client. It replaces ordinary POSIX filesystem calls with libcephfs calls, supports shared libcephfs mount instances across connections with identical configuration, exposes stat/xattr/DFS/POSIX ACL behavior, and adapts Ceph's `-errno` return convention to Samba's `errno`/`-1` convention.

## Important APIs, types, and functions
- `status_code()` and `lstatus_code()` convert negative Ceph errors into Samba-style returns.
- `struct cephmount_cached` tracks a mount cookie, refcount, `ceph_mount_info *`, and DLIST links.
- `cephmount_get_cookie()` keys mounts by `ceph:config_file`, `ceph:user_id`, and `ceph:filesystem`.
- `cephmount_mount_fs()` creates a Ceph mount, reads config, enables `client_acl_type=posix_acl`, disables local default permission checks with `fuse_default_permissions=false`, optionally selects a filesystem, and mounts.
- `cephwrap_connect()`/`cephwrap_disconnect()` manage mount-cache references and store the mount in `handle->data`.
- Directory/file wrappers cover statfs, fdopendir/readdir/closedir, mkdir/open/close/pread/pwrite/lseek/rename/fsync/stat/fstat/fstatat/lstat/timestamps/unlink/chmod/chown/chdir/truncate/fallocate/links/mknod/realpath.
- `init_stat_ex_from_ceph_statx()` maps `ceph_statx` into Samba `stat_ex`, including btime.
- DFS wrappers store referrals as `msdfs:` symlinks and parse them on read.
- Xattr and DOS attribute wrappers integrate with Samba EA DOS attributes while preserving btime from Ceph statx.
- POSIX ACL hooks use `posixacl_xattr_*` helpers.

## Control flow
Connection setup first attempts to reuse a cached mount for the share's cookie. If none exists, it mounts a new CephFS client and inserts it into the cache. Each VFS operation then calls the corresponding libcephfs API using `handle->data`. Many operations are fd-relative (`ceph_openat`, `ceph_mkdirat`, `ceph_unlinkat`), while rename/link/mknod build full paths before calling path-based APIs. The module rejects named streams for path operations by returning `ENOENT`.

Async read/write/fsync are "fake async": the send function performs the synchronous libcephfs call immediately, stores the result in a tevent request, and posts completion. `sendfile` and `recvfile` return `ENOTSUP` because libcephfs is userspace. Strict allocation uses `ceph_fallocate()` when growing files. Filesystem sharemode is not implemented and warns operators to consider `kernel share modes = no`.

## State and persistence behavior
Persistent state is entirely in CephFS: files, directories, xattrs, ACL xattrs, timestamps, symlinks, and DFS referral symlinks. In-process state consists of the global mount cache and per-handle `handle->data` mount pointer. Mount cache entries persist until their refcount reaches zero at disconnect, then unmount and release the Ceph client.

## Dependencies and integration points
The module depends directly on `cephfs/libcephfs.h`, Samba VFS, statvfs/statx translation, tevent, smbd profiling hooks, POSIX ACL xattr helpers, DFS referral helpers, and loadparm. It is registered in `wscript_build` as `vfs_ceph` with Ceph library dependencies.

## Risks and edge cases
- The global mount cache is not visibly synchronized in this file; concurrent connect/disconnect behavior depends on smbd process/thread assumptions.
- Fake async can block the event loop during large Ceph reads/writes/fsyncs.
- `realpath()` is a string join and explicitly does not resolve symlinks.
- Sharemode/locking support is minimal: lock succeeds, getlock returns false, and filesystem sharemodes are unsupported.
- Named streams are largely treated as missing, so stream support must come from other modules if needed.
- Error handling must consistently convert `-errno`; missed conversions would invert or lose failures.

## Test signals
No direct tests were found in the inspected subset. Validation requires a CephFS test cluster: mount reuse across shares with identical cookies, basic filesystem operations, stat btime preservation, xattr/DOS attribute round trips, DFS symlink referrals, strict allocation, fake async behavior, and unsupported sendfile/sharemode paths. Build registration in `wscript_build` is the static integration signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_ceph.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_ceph_new.c -->
# sources/user-network-fs/samba/source3/modules/vfs_ceph_new.c

## Purpose
`vfs_ceph_new.c` is a newer Samba CephFS VFS backend built around dynamically loaded libcephfs low-level APIs. Compared with `vfs_ceph.c`, it keeps explicit Ceph inode and file-handle references in Samba fsp extensions, supports optional proxy lib loading, optional fscrypt key setup through keybridge, optional native Ceph async I/O, and caches share capability details such as case-sensitivity behavior.

## Important APIs, types, and functions
- `struct vfs_ceph_config` stores module configuration, mount/cache pointers, dynamic library handle, cached capabilities, and function pointers loaded with `dlsym()`.
- `enum vfs_cephfs_proxy_mode` and `enum vfs_cephfs_fscrypt_mode` parse `ceph_new:proxy` and `ceph_new:fscrypt`.
- `vfs_cephfs_load_lib()` loads `libcephfs_proxy.so.2` or `libcephfs.so.2` and resolves all required high-level and low-level Ceph symbols.
- `cephmount_*` helpers maintain a refcounted mount cache keyed by config file, user id, and filesystem, with a synthetic debug fd index.
- `vfs_ceph_load_config()`, `vfs_ceph_connect()`, and `vfs_ceph_disconnect()` parse config, load the library, mount/reuse CephFS, optionally configure fscrypt, and clean up.
- `struct vfs_ceph_iref` wraps `Inode *` ownership, while `struct vfs_ceph_fh` wraps directory state, `UserPerm`, `Fh *`, inode ref, debug fd, open flags, and cached dirent memory as a VFS fsp extension.
- `vfs_ceph_ll_*` helpers wrap low-level Ceph inode, lookup, open, create, read/write, xattr, link, rename, statfs, and setattr APIs.
- `vfs_ceph_aio_state` and AIO helpers either submit native `ceph_ll_nonblocking_readv_writev()` when available or fall back to posted synchronous calls with profiling metadata.
- `vfs_ceph_check_case_sensitivity()` reads `ceph.dir.casesensitive` from the share root and caches Samba filesystem capability bits.
- The final `ceph_new_fns` table registers a broad VFS surface under `ceph_new`.

## Control flow
Startup parses share parameters, optionally fetches an fscrypt key from varlink keybridge, dynamically loads libcephfs symbols, and obtains or creates a cached mount. File open resolves the parent directory to an inode reference, allocates an fsp extension with a Ceph `UserPerm`, then either creates a new low-level file or looks up and opens an existing inode. `O_PATH` pathref opens can skip `ceph_ll_open()` and keep only the inode reference. Close releases `Fh *`, owned `Inode *`, `UserPerm`, and cached dirent memory through the fsp-extension destructor.

Most VFS operations fetch the relevant `vfs_ceph_fh` from `files_struct` or resolve a temporary `vfs_ceph_iref`, call a `vfs_ceph_ll_*` helper, then convert `-errno` with `status_code()`/`lstatus_code()`. Directory reads use the `vfs_ceph_fh` itself as the `DIR *` carrier and fill a reusable `struct dirent`. Path-based stat/lstat and pathref xattrs resolve inode references by walking names, while fd-based operations use the stored low-level handle and user permission. DFS referrals are implemented as Ceph symlinks containing `msdfs:` targets.

## State and persistence behavior
Durable state lives in CephFS: files, directories, symlinks, xattrs, ACL xattrs, timestamps, DOS EA attributes, and optional fscrypt policy on the share root. In-process state includes a refcounted mount cache, per-share loaded library/config, cached share capabilities, optional tevent threaded context for async I/O, optional keybridge/fscrypt key data, and per-fsp Ceph handles. Debug fds are synthetic numbers only and are not OS file descriptors.

## Dependencies and integration points
The module integrates with Samba VFS, talloc, tevent, smbd profiling, loadparm, POSIX ACL xattr helpers, DFS helpers, base64 utilities, optional varlink keybridge, optional Linux fscrypt headers, and dynamically loaded libcephfs symbols. It is registered in `wscript_build` as `vfs_ceph_new` and can use either normal libcephfs or the CephFS proxy library depending on `ceph_new:proxy`.

## Risks and edge cases
- Dynamic symbol loading makes startup sensitive to libcephfs/proxy ABI availability; missing any required symbol disables the module.
- Mount cache and config lifetimes are complex: cached mounts can outlive individual `vfs_ceph_config` objects, while fsp extensions keep config pointers.
- Native async completion handles orphaned requests by reparenting state to `NULL`; incorrect cleanup could leak state or complete freed requests.
- `vfs_ceph_ll_walk()` rewrites paths relative to the current Ceph cwd because `ceph_ll_walk()` does not honor absolute paths as expected.
- Case-sensitivity is cached from the share root and assumes administrators do not override it deeper in the tree.
- fscrypt setup lacks strong key validation and applies policy to the connect path when configured.
- Like the legacy module, sendfile/recvfile/sharemode/lease support is limited or unsupported.

## Test signals
No direct tests were found in this subset. Validation should cover library/proxy loading modes, mount cache reuse/refcounting, low-level open/create/O_PATH paths, directory iteration, stat/btime and case-sensitivity xattr capabilities, xattr/DOS/ACL behavior, DFS symlink referrals, strict allocation, optional native async reads/writes, fscrypt keybridge policy setup, and teardown with open handles. Build registration in `wscript_build` is the static integration signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_ceph_new.c -->
