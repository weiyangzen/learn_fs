# subset-b-009831 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_glusterfs.c -->
# sources/user-network-fs/samba/source3/modules/vfs_glusterfs.c

Purpose: implements the bottom-layer Samba VFS module named `glusterfs`, translating Samba file, directory, DFS, xattr, stat, lock, and async I/O operations directly to GlusterFS libgfapi. It is intended for shares backed by a Gluster volume without relying on a local FUSE mount.

Important APIs/types/functions: the module centers on `glfs_t` connection handles stored in `handle->data`, `glfs_fd_t` file handles stored as Samba FSP extensions, and the `glusterfs_fns` VFS dispatch table. `vfs_gluster_connect()` parses `glusterfs:*` smb.conf parameters, initializes libgfapi, sets translator options, registers a preopened `glfs_t`, and adjusts Samba parameters for shadow copy and async DOS mode. `vfs_gluster_openat()` creates and attaches `glfs_fd_t` handles; `vfs_gluster_fsp_ext_destroy()` prevents leaks when directory FSP close paths bypass the VFS close hook. Read, write, and fsync have both synchronous wrappers and pthreadpool-backed `tevent_req` async implementations. Path operations use gfapi `*at` variants when `HAVE_GFAPI_VER_7_11` is available and otherwise synthesize full paths. ACL integration is delegated to `posixacl_xattr_*` helpers.

Control flow: tree connect either reuses a matching preopened `(volume, connectpath)` entry or creates a new `glfs_t`, configures volfile servers, md-cache options, snapview path, write-behind pass-through or write-behind rejection, logging, and `glfs_init()`. File open attaches an FSP extension before calling `glfs_openat()`, `glfs_open()`, or `glfs_creat()`, then later all handle-based operations fetch that extension. Directory functions cast `glfs_fd_t` to `DIR *` for Samba's VFS interface. Async `pread`, `pwrite`, and `fsync` submit blocking gfapi calls to Samba's pthread pool, record profile timings, and fall back to synchronous execution if thread creation returns `EAGAIN`.

State and persistence: process-local state includes the global `glfs_preopened` list with reference counts and per-FSP gfapi handles. Persistent changes are the backend filesystem mutations: creates, writes, timestamps, xattrs, DFS symlinks, locks, mode/ownership changes, and sparse allocation/discard where gfapi supports it. Runtime smb.conf parameter changes (`shadow:mountpoint=/`, `smbd async dosmode=false`) are applied at connect time for the share.

Dependencies and integration points: depends on libgfapi headers/functions, Samba VFS/FSP extension APIs, `tevent`, pthreadpool, profiling macros, DFS helper routines, POSIX ACL xattr helpers, and Gluster translator behavior. It integrates with Samba's file-id and stream behavior by disabling proc-fd assumptions (`have_proc_fds=false`) and by returning a sentinel integer from `openat()` while storing the real gfapi handle out of band.

Risks: the preopened list is global process state and must remain consistent across connect/disconnect error paths. The module has many version-gated gfapi branches; older fallback paths synthesize full paths and are more exposed to path handling differences. `readdir()` uses a static dirent buffer, which is acceptable only under Samba's expected single-threaded event model. Unsupported operations intentionally return `ENOSYS`/`ENOTSUP` for quota, sharemode, leases, sendfile/recvfile, and flags. DFS and real-name lookup depend on Gluster-specific xattrs and symlink formats. Test signals include connecting with multiple volfile server syntaxes, shared preopen reference release, directory FSP destructor cleanup, pathref opens with and without `O_PATH`, gfapi version matrix builds, async I/O fallback on pthreadpool `EAGAIN`, xattr pathref behavior, DFS referral creation/readback, and refusal when write-behind cannot be made pass-through.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_glusterfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_glusterfs_fuse.c -->
# sources/user-network-fs/samba/source3/modules/vfs_glusterfs_fuse.c

Purpose: implements the stackable `glusterfs_fuse` helper module for shares that access Gluster through a local FUSE mount. It preserves Gluster-specific case-insensitive name lookup and stabilizes Samba file IDs across local FUSE device numbers.

Important APIs/types/functions: `vfs_gluster_fuse_get_real_filename_at()` queries the `glusterfs.get_real_filename:<name>` xattr on a directory to resolve actual case. `struct vfs_glusterfs_fuse_handle_data` caches mappings from local `st_dev` values to synthetic 64-bit device IDs. `vfs_glusterfs_fuse_load_devices()` scans `/etc/mtab`, stats mount directories, strips any host prefix from `mnt_fsname`, and hashes the remaining filesystem name with `vfs_glusterfs_fuse_uint64_hash()`. `vfs_glusterfs_fuse_file_id_create()` delegates to the next module, then replaces `id.devid` when a mapping is found.

Control flow: on connect the module calls `SMB_VFS_NEXT_CONNECT()`, allocates handle data, preloads the mount-device cache, and stores it on the VFS handle. File ID creation first uses the default downstream ID, then lazily reloads `/etc/mtab` if the device was not cached. Real-name lookup opens `"."` relative to the directory pathref FD, reads the Gluster xattr with `fgetxattr()`, maps `ENOATTR` to `ENOENT`, and returns the xattr value as the found name.

State and persistence: the only module state is per-connection cached device mappings under the VFS handle. It does not persist data; it reads kernel mount state and Gluster xattrs to adapt Samba's runtime behavior.

Dependencies and integration points: depends on the host mount table (`setmntent()`/`getmntent()`), `stat()`, Linux xattr APIs, Samba file ID creation, and a lower VFS module/default filesystem implementation for ordinary operations. It is intentionally stackable and only overrides connect, file-id creation, and real-filename lookup.

Risks: `/etc/mtab` can be stale, hidden by containerization, or differ from `/proc/self/mounts`; cache reload only happens on misses. The hash is not collision-proof, so different Gluster fsnames can theoretically map to the same synthetic device. The real-name xattr path opens the directory and closes it manually; failures must preserve mapped NT status. Test signals include multiple Gluster FUSE mounts with different fsnames, mount table reload after remount, hash stability across process restarts, `ENOATTR` to not-found mapping, and file IDs remaining stable when the local FUSE device changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_glusterfs_fuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_gpfs.c -->
# sources/user-network-fs/samba/source3/modules/vfs_gpfs.c

Purpose: implements Samba's GPFS VFS module, providing GPFS-aware share modes, leases, NFSv4/POSIX ACL conversion, Windows attributes, HSM/offline handling, quota-aware disk free, time setting, truncation, and GPFS-specific real filename lookup.

Important APIs/types/functions: `struct gpfs_config_data` stores per-share feature flags and NFSv4 ACL parameters; `struct gpfs_fsp_extension` caches offline state per FSP. Share mode paths use `gpfswrap_set_share()` via `set_gpfs_sharemode()` and `vfs_gpfs_filesystem_sharemode()`. Lease support maps Linux lease constants to `GPFS_LEASE_*` with `gpfswrap_set_lease()`. ACL paths include `vfs_gpfs_getacl()`, `gpfs_get_nfs4_acl()`, `gpfsacl_fget_nt_acl()`, `gpfsacl_fset_nt_acl()`, `gpfsacl_sys_acl_*()`, and converters between GPFS NFSv4/POSIX structures and Samba ACL structures. Windows attributes use `gpfswrap_get_winattrs()` and `gpfswrap_set_winattrs()`. `vfs_gpfs_connect()` initializes the wrapper library, checks filesystem type, reads `gpfs:*` parameters, and adjusts Samba oplock parameters when leases are enabled.

Control flow: connect calls the next module, skips IPC shares, initializes the GPFS library/device/export registration, optionally verifies `statfs().f_type == GPFS_SUPER_MAGIC`, fills config flags, and stores config on the VFS handle. Open creates an FSP extension with offline assumed true, optionally adds `O_SYNC`, and can deny access to offline HSM files when recalls are disabled. ACL get first tries GPFS NFSv4 ACLs and falls back to POSIX ACLs for non-NFSv4 results; ACL set dispatches to Samba's NFSv4 ACL engine with a GPFS put callback or to POSIX handling. DOS attribute reads can be synchronous or pthreadpool-backed with copied credentials, and update `st_ex_btime`. Disk-free can combine statvfs data with user and group GPFS quota limits.

State and persistence: per-share config lives in `handle` data; per-open offline cache lives in FSP extensions. Persistent backend state includes GPFS share reservations/leases, ACLs, Windows attributes, timestamps, quotas consulted for reporting, sparse/offline attributes, and file data. The module also changes runtime Samba share parameters for kernel oplocks and level2 oplocks when GPFS leases require it.

Dependencies and integration points: depends heavily on `lib/util/gpfswrap.h`, GPFS kernel/userspace support, Samba NFSv4 ACL helpers, `non_posix_acls`, pthreadpool/tevent, security token credential switching, statvfs conversion, notify/lease break signaling, and optional kernel oplocks. `test_vfs_gpfs.c` already covers share-access deny mapping and Windows attribute conversions. Build integration is in `wscript_build` with GPFS-specific dependencies.

Risks: many features are independently gated by smb.conf and GPFS runtime support, so ENOSYS/fallback behavior is part of the contract. ACL conversion is security-sensitive, especially special IDs, owner deny remapping, control flags, and chmod emulation over NFSv4 ACLs. Windows attribute async reads must not use stack memory after dispatch and must restore credentials/user context correctly. Offline recall notification depends on the cached offline state being refreshed after successful I/O. Timestamp conversion can fail or clamp because GPFS uses unsigned 32-bit seconds. The source also contains suspicious duplicated text in `vfs_gpfs_ftruncate()` in this snapshot, so compile tests are an important signal. Test signals include the existing unit test, GPFS and non-GPFS connect paths, `gpfs:check_fstype`, sharemode denial mapping, lease break delivery, NFSv4 and POSIX ACL round trips, chmod emulation, async DOS attributes under non-root credentials, quota-limited disk-free values, HSM offline no-recall denial, and timestamp clamp/no-clamp behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_gpfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_hpuxacl.c -->
# sources/user-network-fs/samba/source3/modules/vfs_hpuxacl.c

Purpose: implements the `hpuxacl` VFS module, adapting Samba POSIX ACL operations to HP-UX JFS/VxFS ACLs through the HP-UX `acl()` API. It supports JFS-style POSIX ACLs and explicitly does not support deprecated HFS ACLs.

Important APIs/types/functions: HP-UX ACL entries are represented by `struct acl` aliases `HPUX_ACE_T` and `HPUX_ACL_T`. Public VFS entry points are `hpuxacl_sys_acl_get_fd()`, `hpuxacl_sys_acl_set_fd()`, and `hpuxacl_sys_acl_delete_def_fd()`; file-path variants do most work because HP-UX lacks a usable `facl` path in this module. Converters include `smb_acl_to_hpux_acl()`, `hpux_acl_to_smb_acl()`, `smb_tag_to_hpux_tag()`, `hpux_tag_to_smb_tag()`, and permission mapping helpers. `hpux_acl_get_file()` uses `ACL_CNT` then `ACL_GET`; `hpux_acl_sort()` uses `aclsort()` when present or `hpux_internal_aclsort()` otherwise. `hpux_acl_call_present()` and `hpux_aclsort_call_present()` probe symbols with `shl_findsym()` to avoid calling absent HP-UX functions.

Control flow: reads validate the requested ACL type, probe for `acl()`, fetch the complete HP-UX ACL, then filter access or default entries into Samba ACL form. Sets convert the supplied Samba ACL into HP-UX entries; for directories, they fetch and merge the other ACL half because HP-UX `ACL_SET` writes access and default ACLs together. Default ACL deletion rewrites only the access ACL back to the directory. Sorting validates required singleton entries, default singleton entries, duplicate named entries, ordering, and optional class-object recalculation before `ACL_SET`.

State and persistence: there is no per-handle module state. Static booleans cache whether `acl()` and `aclsort()` symbols were already found. Persistent state is the filesystem ACL written through HP-UX `acl()`.

Dependencies and integration points: depends on HP-UX `<sys/aclv.h>`, `<dl.h>` shared-library symbol probing, Samba POSIX ACL structures, `posix_sys_acl_blob_get_fd`, and the VFS ACL dispatch table. The header `vfs_hpuxacl.h` publishes the cross-file prototypes.

Risks: fd operations are path-based, so rename/unlink races are a semantic limitation compared with true fd ACL syscalls. Directory set/delete behavior must preserve the ACL half not being edited. The internal ACL sorter is correctness-critical and has small-entry assumptions inherited from HP-UX ACL limits. This snapshot shows likely compile/type hazards, including path strings passed where `struct smb_filename *` prototypes are declared and a missing dot in the VFS function table initializer; build coverage should catch whether this tree has local compatibility macros or needs repair. Test signals include HP-UX builds with and without `aclsort()`, runtime without JFS ACL support, access/default ACL round trips on files and directories, default ACL deletion preserving access ACLs, invalid duplicate entries, class mask recalculation, and path-race review for fd wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_hpuxacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_hpuxacl.h -->
# sources/user-network-fs/samba/source3/modules/vfs_hpuxacl.h

Purpose: declares the public HP-UX ACL helper functions implemented by `vfs_hpuxacl.c` for use as Samba VFS POSIX ACL callbacks.

Important APIs/types/functions: prototypes cover `hpuxacl_sys_acl_get_file()`, `hpuxacl_sys_acl_get_fd()`, `hpuxacl_sys_acl_set_file()`, `hpuxacl_sys_acl_set_fd()`, and `hpuxacl_sys_acl_delete_def_fd()`. The signatures use Samba's `vfs_handle_struct`, `struct smb_filename`, `files_struct`, `SMB_ACL_TYPE_T`, and `SMB_ACL_T` types.

Control flow: the header has no runtime control flow. It establishes the contract that file ACL operations can be called either by pathname-style `struct smb_filename` or by an open FSP, with implementation details hidden in the C file.

State and persistence: no state is declared. Persistent ACL effects occur only through the implementation's calls to HP-UX `acl()`.

Dependencies and integration points: depends on Samba core type declarations being included before or through the C file. It is included by `vfs_hpuxacl.c` and should match the VFS function table assignments in that file.

Risks and test signals: prototype drift is the main risk, because the C file uses both path-oriented and FSP-oriented wrappers. Compile testing on HP-UX is the key signal, followed by ABI checks that all declarations match Samba's current VFS callback signatures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_hpuxacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_io_uring.c -->
# sources/user-network-fs/samba/source3/modules/vfs_io_uring.c

Purpose: implements the stackable `io_uring` VFS module, providing Linux `io_uring` backed async `pread`, `pwrite`, and `fsync` for Samba file I/O.

Important APIs/types/functions: `struct vfs_io_uring_config` owns one `struct io_uring`, a tevent FD watcher, recursion flags, and queued/pending request lists. `struct vfs_io_uring_request` embeds an SQE/CQE pair, profiling state, request pointer, completion callback, and list ownership. `vfs_io_uring_connect()` initializes the ring using `io_uring:num_entries` and `io_uring:sqpoll` parameters. `vfs_io_uring_queue_run()` and `_vfs_io_uring_queue_run()` move requests from queue to pending, submit SQEs, reap CQEs, and guard against recursive short-I/O resubmission. `vfs_io_uring_pread_send/recv()`, `vfs_io_uring_pwrite_send/recv()`, and `vfs_io_uring_fsync_send/recv()` expose Samba async VFS operations.

Control flow: connect stores config, calls the next module, initializes the ring, marks it dontfork when supported, and registers the ring FD with tevent. Send functions validate ranges, prepare state, build an SQE, enqueue it, defer callbacks when still in progress, and profile async duration. Completion functions translate negative CQE results to Unix errors, handle short reads/writes by advancing an iovec and resubmitting, treat zero-length write completion as `ENOSPC`, and finish the tevent request only after the requested byte count or EOF. Destructors tear down the whole ring if an in-flight request state is destroyed.

State and persistence: all state is per-connection runtime state. It does not persist filesystem data beyond the underlying read/write/fsync effects. Queue and pending lists are mutable in-memory state, and teardown completes outstanding requests with synthetic negative errors such as `-EUCLEAN` or `-ESHUTDOWN`.

Dependencies and integration points: depends on liburing, Linux kernel `io_uring`, Samba tevent integration, Samba VFS async request conventions, `iov_advance()`, `sys_valid_io_range()`, profiling, and optional `io_uring_ring_dontfork()`/`writev2` support. It stacks above another module for open and all non-async operations, except it rejects POSIX append I/O on platforms lacking `io_uring_prep_writev2()`.

Risks: teardown currently has a TODO for true cancellation of queued/pending requests and instead destroys the ring and completes requests with errors. The destructor path intentionally shuts down the whole ring when a request state would disappear while in a list. Recursion handling is subtle because completion can resubmit before the outer queue run unwinds. SQPOLL changes kernel privilege/resource behavior. Test signals include connect failure cleanup, ring FD event processing, short read/write resubmission, zero write completion, invalid ranges, append mode with and without `writev2`, request-state destructor during shutdown, fork behavior, and fallback to lower VFS for non-overridden operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_io_uring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_linux_xfs_sgid.c -->
# sources/user-network-fs/samba/source3/modules/vfs_linux_xfs_sgid.c

Purpose: implements the `linux_xfs_sgid` VFS workaround module for a Linux XFS behavior where newly created directories may fail to inherit the SGID bit as Samba expects.

Important APIs/types/functions: the module overrides only `mkdirat` with `linux_xfs_sgid_mkdirat()`. It uses `SMB_VFS_NEXT_MKDIRAT()`, `full_path_from_dirfsp_atname()`, `SMB_VFS_PARENT_PATHNAME()`, `SMB_VFS_NEXT_STAT()`, root privilege elevation, and `SMB_VFS_NEXT_FCHMOD()`.

Control flow: after the downstream `mkdirat` succeeds, the module builds the created path, finds and stats the parent, and returns success unchanged if the parent does not have `S_ISGID` or if follow-up checks fail. If the parent has SGID, it stats the new directory, adds `S_ISGID` to its mode, strips `S_IFDIR` before chmod, temporarily becomes root because Linux XFS may otherwise ignore SGID chmod while returning success, and applies the mode through the next `fchmod`.

State and persistence: no module state is stored. Persistent behavior is limited to setting the SGID mode bit on newly created directories.

Dependencies and integration points: stackable over the normal filesystem module, relies on Samba path helpers and privilege helpers, and assumes `smb_fname->fsp` is valid for the just-created directory chmod path.

Risks: errors after successful mkdir are intentionally logged but do not turn the operation into failure, so callers may see success even when SGID repair failed. The root-elevated chmod is narrow but security-sensitive. Test signals include mkdir under SGID and non-SGID parents, failure to stat parent/new directory, chmod failure while preserving mkdir success, and verifying the mode passed to `FCHMOD` sets SGID without including file-type bits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_linux_xfs_sgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_media_harmony.c -->
# sources/user-network-fs/samba/source3/modules/vfs_media_harmony.c

Purpose: implements the `media_harmony` VFS module for Avid media shares. It gives each SMB client/user a private view of Avid database files (`msmMMOB.mdb`, `msmFMID.pmr`) and `Creating` directories under `Avid MediaFiles`/`OMFI MediaFiles`, while also faking selected directory mtimes to avoid unnecessary Avid database refreshes across editors.

Important APIs/types/functions: path classification helpers include `is_in_media_files()`, `starts_with_media_dir()`, `depth_from_media_dir()`, `is_apple_double()`, and `is_avid_database()`. `alloc_append_client_suffix()` appends `_<remote-ip>_<sanitized-username>` using `tsocket_address_inet_addr_string()` and session info. `alloc_get_client_path()` rewrites Avid database and Creating paths; `alloc_get_client_smb_fname()` copies `struct smb_filename` with rewritten `base_name`; `set_fake_mtime()` substitutes mtimes from client-suffixed marker directories. Directory state is held in `struct mh_dirinfo_struct`, wrapping the real `DIR *` plus rewritten names for filtering.

Control flow: most VFS operations first check whether a path is under an Avid media directory. Outside that tree they delegate unchanged. Inside it, namespace operations rewrite source and/or destination paths to client-suffixed names and often operate relative to `cwd_fsp` after constructing full paths. `fdopendir()` wraps the downstream directory stream in `mh_dirinfo_struct`; `readdir()` hides unsuffixed Avid special files and other clients' suffixed versions, while presenting this client's suffixed version under the unsuffixed name. `stat`, `lstat`, `fstat`, and `fdopendir` can replace mtimes for `Avid MediaFiles/MXF` first-level directories or `OMFI MediaFiles` root children from corresponding client-suffixed paths.

State and persistence: persistent state is encoded in real filesystem names suffixed by remote address and sanitized username. Per-open directory state is talloc-allocated in `mh_dirinfo_struct` and freed at `closedir`. The module does not maintain a database; visibility is derived from path naming conventions at runtime.

Dependencies and integration points: depends on Samba VFS stacking, SMB filename copy/synthetic path helpers, connection remote address, authenticated Unix username, current working directory FSP, and downstream filesystem behavior. It registers a custom debug class `media_harmony` after VFS registration.

Risks: the module rewrites paths by string inspection and assumes fixed Avid directory layout at share root; unusual `.`/`..` paths are only partially handled. Directory entries are modified in place to strip suffixes, which relies on downstream dirent mutability and sufficient buffer ownership. Client identity includes IP address, so NAT, reconnects, or address changes alter the visible private filenames. Many operations use full-path reconstruction plus `cwd_fsp`, increasing the chance of path mismatch if Samba path semantics change. The source snapshot includes suspicious duplicate parameter text in `alloc_set_client_dirinfo_path()`, so compile tests matter. Test signals include Windows and macOS Avid directory layouts, AppleDouble variants, directory listings hiding/revealing the right files, per-client create/open/rename/unlink/link/symlink/mknod behavior, fake mtime substitution for MXF/OMFI directories, users with sanitized-name collisions, and reconnects from different remote addresses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_media_harmony.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_nfs4acl_xattr.c -->
# sources/user-network-fs/samba/source3/modules/vfs_nfs4acl_xattr.c

Purpose: implements the `nfs4acl_xattr` VFS module, storing Windows/NFSv4 ACL semantics in extended attributes using selectable NDR, XDR, or Linux NFS encodings and exposing them through Samba NT ACL operations.

Important APIs/types/functions: `struct nfs4acl_config` is allocated in `nfs4acl_connect()` and stores encoding, NFS version, xattr name, default ACL style, numeric ID behavior, mode validation, and Samba NFSv4 ACL parameters. `nfs4acl_get_blob()` reads the configured xattr with dynamic buffer growth after `nfs4acl_validate_blob()`. `nfs4acl_blob_to_smb4()` and `nfs4acl_smb4acl_set_fn()` dispatch to NDR/XDR/NFS encoder-decoder helpers. `nfs4acl_xattr_fget_nt_acl()` maps stored blobs to NT security descriptors; `nfs4acl_xattr_fset_nt_acl()` maps NT descriptors back to stored xattrs through `smb_set_nt_acl_nfs4()`.

Control flow: connect calls the next module, reads `nfs4acl_xattr:*` parameters, selects default xattr names by encoding, configures NFSv4 ACL parameters, stores config, and forces Samba share parameters suitable for xattr-backed NFSv4 ACLs (`inherit acls`, `dos filemode`, masks, DOS attributes, and unknown users). ACL get validates mode if enabled, removes stale ACL xattrs when POSIX mode no longer has broad expected bits, reads the xattr, decodes it, and otherwise synthesizes a default filesystem ACL when the xattr is missing. ACL set restores expected POSIX mode bits if validation is enabled, attempts to store the converted NFSv4 ACL blob, and has a take-ownership retry path for non-root users with `WRITE_OWNER` when the requested owner is the caller.

State and persistence: per-share config is stored on the VFS handle. Persistent ACL state is the configured xattr on each file plus enforced POSIX mode normalization to 0666 for files or 0777 for directories when validation is active. The module deliberately disables POSIX ACL VFS callbacks by installing failing stubs, preventing accidental mixed ACL storage.

Dependencies and integration points: depends on Samba NFSv4 ACL helpers, xattr VFS operations below it, generated NDR definitions, NDR/XDR/NFS xattr codec modules, security token/SID helpers, and default ACL generation. It is built with companion `nfs4acl_xattr_*` sources in `wscript_build`.

Risks: mode validation intentionally deletes the ACL xattr when mode bits do not match expectations, so chmod-like operations can discard stored ACLs. Xattr buffer growth caps at 65536 after repeated `ERANGE`; larger or malformed ACL blobs fail. Ownership retry must only allow Windows-style take ownership, not arbitrary ownership assignment. Forced share parameters can surprise administrators if module stacking/order is wrong. Test signals include all three encodings, custom xattr names, NFSv4.0/4.1 versions, missing xattr default ACLs, stale mode xattr removal, mode restore on set, take-ownership retry success/failure, failing POSIX ACL stubs, malformed blob decode failures, and stack order with lower xattr implementations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_nfs4acl_xattr.c -->
