# subset-b-009695 Research

Grouped research for NFS-Ganesha SaunaFS and VFS FSAL source files. Each section preserves its source path and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs/saunafs_c_api.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs/saunafs_c_api.h

Purpose: this header is the C ABI exported by the SaunaFS client library for NFS-Ganesha's FSAL_SAUNAFS integration. It declares opaque client/session/file-context objects, stable wire-facing types, metadata structures, ACL constants, xattr modes, locking data, and operations used to communicate with SaunaFS metadata and chunk servers.

Important APIs and types: `sau_init_params_t` captures connection and cache/write/read tunables, master host/port, subfolder, password fields, ACL cache settings, SUGID clearing policy, and IO limits configuration. Opaque handles include `sau_t`, `sau_fileinfo_t`, `sau_context_t`, and `sau_acl_t`. `sau_inode_t`, `sau_entry_t`, `sau_attr_reply_t`, `sau_direntry_t`, `sau_namedinode_entry_t`, `sau_xattr_reply_t`, `sau_stat_t`, `sau_chunk_info_t`, `sau_chunkserver_info_t`, `sau_acl_ace_t`, `sau_lock_info_t`, and `sau_lock_interrupt_info_t` define the data exchanged with the client library. The main operation families are context setup (`sau_create_context`, `sau_create_user_context`, `sau_update_groups`, `sau_destroy_context`), connection setup (`sau_set_default_init_params`, `sau_init`, `sau_init_with_params`, `sau_destroy`), inode namespace operations (`sau_lookup`, `sau_mknod`, `sau_link`, `sau_symlink`, `sau_mkdir`, `sau_rmdir`, `sau_unlink`, `sau_rename`, `sau_readlink`), file IO (`sau_open`, `sau_read`, `sau_readv`, `sau_write`, `sau_flush`, `sau_fsync`, `sau_release`), attributes (`sau_getattr`, `sau_setattr`, `sau_statfs`), xattrs, ACLs, trash/reserved listings, chunks/chunkservers, and byte-range locks.

Control flow and state: callers initialize `sau_init_params_t`, open a `sau_t` instance, create a per-request credential context, execute inode-oriented operations, then release fileinfo/context/instance resources. Operations return `0` or positive byte counts on success and `-1`/`NULL` with `sau_last_err()` set on failure. Several returned buffers require matching destroy helpers (`sau_destroy_direntry`, `sau_free_namedinode_entries`, `sau_destroy_acl`, `sau_destroy_chunks_info`, `sau_destroy_chunkservers_info`). Lock cancellation is callback driven: `sau_setlk` can register `sau_lock_interrupt_info_t`, later passed to `sau_setlk_interrupt`.

Persistence behavior: the API itself holds no on-disk state, but it exposes persistent SaunaFS inode identifiers, generation numbers, POSIX `struct stat` attributes, xattrs, ACLs, and chunk layout metadata. Attribute, entry, directory-entry, symlink, ACL, and IO cache parameters in `sau_init_params_t` directly affect client-side consistency windows.

Dependencies and integration points: includes POSIX headers for `struct stat`, open flags, `struct iovec`, and uid/gid/pid types. FSAL_SAUNAFS wraps these declarations in internal helpers and object/export implementations. ACL bit definitions intentionally mirror NFSv4/RichACL concepts while tagging SaunaFS special identities with `SAU_ACL_SPECIAL_WHO`.

Risks: several helper macros appear inconsistent (`SAU_ACL_POSIX_MODE_EXECUTE` uses `EXECUTE`, and `SAU_ACL_POSIX_MODE_ALL` references `SAU_POSIX_MODE_EXEC`), so consumers should not assume those macros compile unless validated by the library build. Lifetime rules for returned nested strings and chunk arrays are easy to misuse. API errors are SaunaFS-native and must be converted before returning FSAL/NFS status. Cache timeout defaults can create visible NFS consistency behavior.

Test signals: compile FSAL_SAUNAFS against the exact installed SaunaFS client header; exercise connection initialization, credential contexts with secondary groups, create/open/read/write/flush/release, xattr list/get/set/remove, ACL round trips, lock conflict/cancel, and chunkserver/chunk-layout queries. Failure tests should assert `sau_last_err`, `sau_error_conv`, and caller cleanup on partial allocations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs/saunafs_c_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs/saunafs_error_codes.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs/saunafs_error_codes.h

Purpose: this header defines the SaunaFS metadata/client error code namespace and declares `saunafs_error_string(uint8_t status)`.

Important APIs and types: `enum saunafs_error_code` maps numeric statuses from `SAUNAFS_STATUS_OK` through filesystem, metadata, chunk, quota, session, lock, range, timeout, and parsing failures. Codes include POSIX-like cases (`EPERM`, `ENOENT`, `EACCES`, `EEXIST`, `EINVAL`, `ENOTEMPTY`, `ENOSPACE`, `EROFS`, `ENAMETOOLONG`, `EFBIG`, `EBADF`, `ENODATA`, `E2BIG`) and SaunaFS-specific cases (`CHUNKLOST`, `NOCHUNKSERVERS`, `WRONGCHUNKID`, `BADMETADATACHECKSUM`, `METADATAVERSIONMISMATCH`, `WAITING`). `SAUNAFS_ERROR_MAX` is a sentinel.

Control flow and state: callers receive or store compact integer statuses, pass them to string/conversion functions, then translate to FSAL/NFS errors in higher layers. The header has no mutable state.

Dependencies and integration points: FSAL_SAUNAFS uses this status space through the C API and `saunafs_internal.c`. The enum is part of the boundary between SaunaFS client semantics and Ganesha's `fsal_status_t`/NFSv4 status mapping.

Risks: numeric stability matters because errors may cross C ABI boundaries. New SaunaFS errors require updates in conversion code or they may collapse to generic errors. Some codes are semantically close but not equivalent (`DELAYED`, `WAITING`, `TEMP_NOTPOSSIBLE`, `NOTDONE`), so retry/delay behavior must be checked in callers.

Test signals: verify every enum value is accepted by `saunafs_error_string`, `sau_error_conv`, and FSAL conversion paths; include unknown/out-of-range values and retry-like statuses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs/saunafs_error_codes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_acl.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_acl.c

Purpose: this file converts ACLs between Ganesha FSAL/NFSv4 representation and SaunaFS ACL representation, then implements `getACL` and `setACL` wrappers for SaunaFS inode ACL operations.

Important functions: `convertFsalACLToSaunafsACL` creates a SaunaFS ACL from a mode and FSAL ACL, copying allow/deny ACEs, preserving low-byte flags, permissions, type, user/group ids, and translating FSAL special identities to SaunaFS special ids with `SAU_ACL_SPECIAL_WHO`. `convertSaunafsACLToFsalACL` allocates FSAL ACE data, pulls entries with `sau_get_acl_entry`, maps SaunaFS special identities back to `FSAL_ACE_SPECIAL_*`, and interns the ACL with `nfs4_acl_new_entry`. `getACL` releases an existing output ACL, calls `saunafs_getacl`, applies masks with `sau_acl_apply_masks(ownerId)`, converts to FSAL ACL, and destroys the SaunaFS ACL. `setACL` ignores NULL ACLs as success, converts FSAL ACLs to SaunaFS, calls `saunafs_setacl`, and destroys temporary SaunaFS ACLs.

Control flow and state: conversion is one-way allocation with explicit cleanup. `getACL` owns the old `*acl`, the temporary `sau_acl_t`, and the returned FSAL ACL reference. `setACL` owns only its temporary `sau_acl_t`. Error paths use `fsalLastError()` for SaunaFS failures and `ERR_FSAL_FAULT` for conversion/allocation failure.

Dependencies and integration points: depends on `context_wrap.h`, `saunafs_internal.h`, Ganesha FSAL ACL helpers/macros, `nfs4_ace_alloc`, `nfs4_acl_new_entry`, `nfs4_acl_release_entry`, and SaunaFS C API ACL calls. It uses `op_ctx->creds` and `SaunaFSExport::fsInstance`.

Risks: `convertSaunafsACLToFsalACL` asserts `sau_get_acl_entry` success and does not recover in non-debug builds beyond the API behavior. Only allow/deny ACEs are copied from FSAL to SaunaFS, so audit/alarm-like entries are dropped. The low-byte flag mask can discard higher FSAL flag bits except the explicit special-id marker. Conversion validity depends on FSAL macros interpreting group/special flags after `flag`/`iflag` fields are set.

Test signals: round-trip ACLs containing owner/group/everyone special ids, user ids, group ids, allow and deny entries, inherited/group flags, empty ACLs, NULL ACLs, invalid special ids, and SaunaFS get/set failures. Confirm existing output ACL references are released before replacement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_fsal_types.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_fsal_types.h

Purpose: this header defines FSAL_SAUNAFS private module, export, handle, state, pNFS, and constant types used by the SaunaFS backend.

Important types and constants: `SAUNAFS_VERSION` and `kDisconnectedChunkServerVersion` encode chunkserver version semantics. Block/chunk constants define a 64 KiB block, 1024 blocks per chunk, and `SFSCHUNKSIZE`. Special inode bounds separate regular inodes from synthetic inodes. `SAUNAFS_SUPPORTED_ATTRS` advertises POSIX-like attributes plus ACL and NFSv4 xattr support. `struct SaunaFSModule` embeds `fsal_module`, object operations, and static fsinfo. `struct SaunaFSExport` embeds `fsal_export`, root handle, `sau_t *fsInstance`, init params, fileinfo cache, pNFS mode flags, and cache limits. `struct SaunaFSFd`, `struct SaunaFSStateFd`, `struct SaunaFSHandleKey`, `struct SaunaFSHandle`, `struct DSWire`, and `struct DataServerHandle` define open state, handle identity, share reservation, and pNFS data-server handles.

Control flow and state: handles carry both public `fsal_obj_handle` state and SaunaFS-specific inode/export/share/fd state. Exports own the SaunaFS client instance and cache. NFSv4 state objects embed a `SaunaFSFd` so opens/locks can associate a client-library fileinfo with protocol state. pNFS data-server handles track an inode and optional cache entry.

Dependencies and integration points: includes `fsal_api.h`, `fileinfo_cache.h`, and the SaunaFS C API. Other FSAL_SAUNAFS files use these structures for export creation, handle allocation, IO, ACL, and pNFS layout operations.

Risks: handle keys contain module id, export id, and inode, so export id stability is part of persistent handle identity. Cache settings and pNFS flags are per-export mutable runtime behavior. The file exposes constants that must remain consistent with SaunaFS server/client chunk sizing and inode reservation rules.

Test signals: construct exports with cache and pNFS options, validate handle key encoding/decoding across export ids, assert `SAUNAFS_SUPPORTED_ATTRS` matches implemented ops, and test fileinfo cache cleanup through export and state destruction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_fsal_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_internal.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_internal.c

Purpose: this file provides shared SaunaFS FSAL helpers for credential context creation and error conversion.

Important functions: `createContext` converts a Ganesha `user_cred` into a SaunaFS `sau_context_t`. It maps anonymous uid/gid to root ids, creates a user context, prepends the primary gid to the secondary group array, and registers groups with `sau_update_groups`. `saunafsToNfs4Error` and `saunafsToFsalError` convert SaunaFS error codes through `sau_error_conv` into NFSv4 or FSAL errors, warning when no error was set and substituting `EINVAL`. `fsalLastError` and `nfs4LastError` read `sau_last_err()`.

Control flow and state: contexts are per-operation/per-credential and must be destroyed by callers. Secondary groups bind the context to a specific SaunaFS instance according to the C API contract. Error conversions preserve the native SaunaFS code as `fsal_status_t.minor`.

Dependencies and integration points: includes FSAL POSIX/NFS conversion helpers, `pnfs_utils.h`, and `saunafs_internal.h`. All SaunaFS wrappers should use these conversions rather than returning raw SaunaFS statuses.

Risks: `createContext` allocates `caller_glen + 1` gids but copies only `caller_glen` secondary entries after setting the primary gid; that is intentional but needs coverage. It uses `free(garray)` on memory allocated with `gsh_malloc`, which may be inconsistent if Ganesha memory wrappers require `gsh_free`. Failures from `sau_update_groups` are ignored, so callers may operate with incomplete group data.

Test signals: contexts for NULL creds, anonymous creds, normal creds, many secondary groups, failed context creation, and failed group update. Error tests should cover zero, known, and unknown SaunaFS error codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_internal.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_internal.h

Purpose: this header declares shared FSAL_SAUNAFS internal functions for contexts, export/object operation vector initialization, handle allocation, ACL operations, error conversion, and pNFS operation setup.

Important APIs: `createContext`, `exportOperationsInit`, `handleOperationsInit`, `allocateHandle`, `deleteHandle`, `getACL`, `setACL`, `saunafsToFsalError`, `fsalLastError`, `nfs4LastError`, `pnfsMdsOperationsInit`, `exportOperationsPnfs`, `pnfsDsOperationsInit`, and `handleOperationsPnfs`.

Control flow and state: this header ties independent implementation files into the module registration path. Handles allocated by `allocateHandle` must be released through `deleteHandle`. ACL helpers consume `SaunaFSExport`, inode ids, mode, and FSAL ACL references. Error helpers centralize C API status mapping.

Dependencies and integration points: includes local FSAL filesystem support and `saunafs_fsal_types.h`, making the private SaunaFS structures visible to all implementation files.

Risks: broad internal declarations mean operation initialization, pNFS hooks, and handle lifetime must remain ABI-consistent across multiple compilation units. Any signature drift can silently break module registration or object op vectors.

Test signals: build-time coverage is primary; runtime smoke tests should create an export, allocate/release handles, invoke ACL helpers, and verify pNFS operation vectors are populated only when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/CMakeLists.txt

Purpose: this top-level CMake file configures the VFS-family FSAL build directory.

Important behavior: it adds `-D__USE_GNU`, includes the current source directory so generated sub-FSAL entry points can include local headers, sets `LIB_PREFIX`, always adds the `os` object-library subdirectory, and conditionally adds `vfs` for `USE_FSAL_VFS` or `USE_FSAL_LUSTRE`, and `xfs` for `USE_FSAL_XFS`.

Control flow and state: CMake options select platform object code first, then module-specific shared objects. There is no runtime state in this file.

Dependencies and integration points: feeds `FSAL_VFS/os` and `FSAL_VFS/vfs` build scripts. The generated Lustre/VFS module entry point in the build tree depends on current-directory include paths.

Risks: `__USE_GNU` changes libc feature visibility and is required for GNU extensions used by VFS file operations. Conditional subdirectory logic must match top-level option definitions; otherwise VFS shared modules may not be built.

Test signals: configure with `USE_FSAL_VFS`, `USE_FSAL_LUSTRE`, `USE_LLAPI`, `USE_FSAL_XFS`, Linux, and FreeBSD combinations and verify the expected module targets are present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/empty_check_hsm.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/empty_check_hsm.c

Purpose: this file supplies the default non-Lustre HSM check hook for FSAL_VFS.

Important function: `check_hsm_by_fd(int fd)` ignores its file descriptor and returns `ERR_FSAL_NO_ERROR`.

Control flow and state: VFS open paths call this hook after opening a file. In the plain VFS module, this implementation makes HSM checks a no-op so opens continue normally.

Dependencies and integration points: included in `fsalvfs` target by `vfs/CMakeLists.txt`; the Lustre variants instead use `llapi_check_hsm.c`.

Risks: the hook must remain ABI-compatible with the Lustre implementation. Plain VFS will never return `ERR_FSAL_DELAY` for offline files.

Test signals: build plain FSAL_VFS and verify opens do not depend on Lustre headers or `lustreapi`, and that `vfs_open2_by_handle`/`vfs_open2` proceed after the no-op check.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/empty_check_hsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/export.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/export.c

Purpose: this file implements FSAL_VFS export lifecycle, dynamic filesystem info, quotas, wire-handle validation, filesystem claiming, export creation, and export updates.

Important functions: `release` tears down sub-FSAL state, unclaims filesystems, detaches the export, frees ops, and frees the export object. `get_dynamic_info` obtains a usable fd via `find_fd`, calls `fstatvfs`, and fills byte/file counts. `get_quota` and `set_quota` wrap `quotactl` under caller credentials and root filesystem device selection. `wire_to_host` validates incoming handles through `vfs_check_handle`. `get_fsal_obj_hdl` maps a global `fsal_fd` back to its containing object. `vfs_export_ops_init` populates export ops. `vfs_claim_filesystem` gets and stores a root fd in filesystem private data. `vfs_unclaim_filesystem` closes root fds. `vfs_create_export` loads config, initializes sub-FSAL ops, attaches the export, resolves/claims POSIX filesystems, initializes sub-FSAL export state, and installs `op_ctx->fsal_export`. `vfs_update_export` validates mutable config updates and forbids changes to `fsid_type` and `async_hsm_restore`.

Control flow and state: exports own filesystem claims and root fds indirectly through `fsal_filesystem::private_data`; `unclaim_all_export_maps` releases them. Export creation is staged with cleanup labels for config, attach, filesystem resolution, and sub-FSAL initialization. Dynamic info and quotas temporarily switch credentials where kernel permission/quota behavior requires it.

Dependencies and integration points: depends on Ganesha FSAL commonlib, config parsing, localfs filesystem registry, handle syscall helpers, export manager, sub-FSAL API, and OS quota/mount wrappers. It is called from the generated module entry point in `vfs/main-c.in.cmake`.

Risks: root fd lifetime is central to `open_by_handle_at` on Linux; leaked or prematurely closed root fds break persistent handle reopening. Quota calls use `root_fs->device`, with comments noting cross-mount ambiguity. Update validation only checks selected options, so other config changes are delegated to default update logic. `root_fd(fs) > 0` skips closing fd 0, which is intentional in normal cases but worth watching if a root fd can be 0.

Test signals: export create/release under valid/invalid paths, filesystem claim/unclaim, cross-device exports, config reload changing and not changing `fsid_type`/`async_hsm_restore`, dynamic info on regular files/directories, quota get/set with privilege failures, and stale/spoofed wire handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/file.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/file.c

Purpose: this file implements FSAL_VFS file IO, fd lifecycle, NFSv4 state allocation, share reservation integration, open/create/reopen/close, read/write/seek/fallocate/commit/lock, and getattr/setattr operations.

Important functions: `vfs_open_my_fd`, `vfs_close_my_fd`, `vfs_reopen_func`, and `vfs_close_func` bridge `vfs_fd` and generic `fsal_fd` lifecycle. `vfs_alloc_state` and `vfs_free_state` allocate state-specific fds. `vfs_merge` merges share reservations on duplicate file handles. `fetch_attrs` stats objects according to type and calls sub-FSAL getattrs. `vfs_open2_by_handle` handles object-based open/reopen, share conflict checks, fd LRU insertion/bumping, HSM checks, verifier/truncate attribute refresh, and error cleanup. `vfs_open2` handles open-by-name and create modes, including exclusive/guarded/unchecked create, credential switching, handle creation, post-create setattr/getattr, and partial-create cleanup. `find_fd` chooses state, global, or temporary fds for attributes and IO. `vfs_read2`/`vfs_write2` perform vector IO and update callback args. `vfs_seek2` maps NFSv4 data/hole seek to `lseek(SEEK_DATA/SEEK_HOLE)`. `vfs_fallocate` wraps `fallocate` and hole punching. `vfs_commit2` uses `fsync`. `vfs_lock_op2` maps FSAL lock ops to OFD `fcntl` locks. `vfs_getattr2`, `vfs_setattr2`, and `vfs_close2` implement metadata and close semantics.

Control flow and state: fd access is coordinated through Ganesha's `fsal_start_io`, `fsal_start_global_io`, `fsal_start_fd_work_no_reclaim`, `fsal_complete_io`, LRU insertion/removal, and share counters. State fds live in `struct vfs_state_fd`; regular file handles also have a global fd. Opens with state update share reservations under `obj_lock`; stateless IO temporarily acquires and then releases share counters. Create-by-name opens the parent by handle, switches to caller credentials for creation, allocates a new object handle from `name_to_handle`, and may delete the newly created file on later failures.

Persistence behavior: persistent identity is the VFS file handle generated by OS-specific code, while mutable persistent state includes file contents, mode, ownership, timestamps, ACL/xattrs through sub-FSAL hooks, byte-range locks, and size. In-memory state includes open fd LRU entries, share counters, state-specific fds, and cached symlink/handle data.

Dependencies and integration points: uses POSIX syscalls (`openat`, `preadv`, `pwritev`, `ftruncate`, `fchmod`, `fchown`, `utimens`, `fsync`, `fcntl`, `fallocate`), Ganesha FSAL fd/share/state helpers, `check_hsm_by_fd`, and sub-FSAL attr hooks. Object operation pointers are installed by `handle.c`.

Risks: this is concurrency-sensitive: work mutexes, object locks, share counters, and fd LRU updates must stay balanced on every path. `vfs_open2` notes rare unchecked-create races can leak partially created files if the retry path recreated the file without tracking ownership. SEEK has a non-atomic size check. `vfs_setattr2` handles symlink and unopenable object limitations with special cases. Error handling around `status2` from `fsal_complete_io` is logged but not generally propagated.

Test signals: NFSv3 create/open without state, NFSv4 open/reopen/close with deny modes, duplicate handle merge, read/write stable and unstable writes, commit, truncate and large-size errors, symlink/socket/block/char/fifo attrs, chmod/chown/timestamps, ACL/xattr sub-FSAL attrs, HSM delay, OFD lock test/lock/unlock/conflict, fd LRU exhaustion, and cleanup after create failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/handle.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/handle.c

Purpose: this file implements VFS object handles and namespace operations: lookup, create directory/node/symlink, readlink, hardlink, readdir, rename, unlink, handle digest/key, xattrs, path lookup, wire-handle validation, and handle reconstruction.

Important functions: `vfs_fsal_open` delegates to OS `vfs_open_by_handle`. `handle_to_key` and `handle_to_wire` expose persistent handle bytes. `alloc_handle` allocates a sub-FSAL-sized handle, copies VFS handle bytes, sets type/fs/fileid/fsid, initializes regular-file fds, caches symlink content, records parent/name for unopenable files, initializes generic FSAL object state, and calls `vfs_sub_init_handle`. `check_filesystem` detects mount boundary crossings, reloads/claims new POSIX filesystems, and marks cross-FSAL transitions. `lookup_with_fd` stats, obtains or invents a handle, allocates object handles, and populates referral fs_locations. Namespace functions wrap `mkdirat`, `mknodat`, `symlinkat`, `renameat`, `unlinkat`, `link_by_handle`, and directory iteration. `vfs_handle_ops_init` installs the full object op vector. `vfs_lookup_path`, `vfs_check_handle`, and `vfs_create_handle` are export-level handle entry points.

Control flow and state: object handles own type-specific data: global fd/share state for regular files, symlink content, or parent handle/name for unopenable types. Lookup opens parent directories by persistent handle, checks filesystem ownership, obtains stable OS handles, allocates Ganesha object handles, and returns attributes. Readdir streams kernel directory entries, looks up each child to get a real object handle, and calls the MDCACHE callback. Release closes regular global fds, finalizes the public handle, and frees private memory.

Persistence behavior: VFS persistent handles are opaque OS handle bytes containing or associated with fsid. Dummy handles represent cross-FSAL/cross-device referral-like boundaries and are not valid for normal VFS reopening. Directory entries and file operations mutate the underlying POSIX filesystem.

Dependencies and integration points: depends on localfs filesystem registry, OS xattr wrappers, VFS syscall helpers, sub-FSAL API, CityHash for referral fsid derivation, NFS export context, and object operation defaults. It supplies methods consumed by MDCACHE and export operations.

Risks: filesystem boundary logic is security-sensitive; spoofed fsids are rejected by `vfs_check_handle`, but dummy handles and cross-FSAL cases require careful testing. Unopenable types rely on stored parent handle/name and must be updated on rename. Readdir races are tolerated for `ENOENT` but other lookup errors abort iteration. Symlink handling differs by OS and may rely on cached content. Extended attribute helpers prefix `user.` and must enforce length/option semantics correctly.

Test signals: lookup across same fs, new mount, unclaimed fs, and different FSAL; create/remove all object types; symlink read/refresh; hardlink support disabled/enabled; readdir with deletion races; rename unopenable objects; NFSv3/v4 handle digest/recreate; invalid/spoofed/dummy handles; xattr get/set/list/remove and ERANGE/ENODATA mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/handle_syscalls.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/handle_syscalls.c

Purpose: this shared file implements OS-independent helper logic around symlink reads and root handle acquisition for VFS filesystems.

Important functions: `vfs_readlink` refreshes cached symlink content by opening/statting a symlink handle, allocating `st_size + 1`, calling `vfs_readlink_by_handle`, NUL-terminating, and updating the VFS object. It has FreeBSD-specific `fhstat` behavior. `vfs_get_root_handle` opens the filesystem path as a directory, optionally changes fsid indexing to the configured type, logs the resulting fsid, and calls OS `vfs_re_index`.

Control flow and state: `vfs_readlink` frees old link content before refresh and restores the object to NULL/zero length on error. `vfs_get_root_handle` returns an opened root fd via output parameter; the caller stores it in filesystem private data and later closes it during unclaim.

Dependencies and integration points: uses `vfs_fsal_open`, `vfs_stat_by_handle`, `vfs_readlink_by_handle`, `change_fsid_type`, and OS-specific `vfs_re_index`. Called from `handle.c` readlink paths and `export.c` filesystem claiming.

Risks: symlink size can change between stat and readlink, yielding truncation or errors. Root fd acquisition must happen before Linux `open_by_handle_at` can work. Reindex failure closes the root fd and prevents filesystem claiming.

Test signals: symlink refresh on changed targets, ENOENT-to-stale behavior, allocation cleanup on readlink failures, fsid_type override, and platform-specific reindex behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/handle_syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/os/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/os/CMakeLists.txt

Purpose: this CMake file selects and builds platform-specific VFS handle syscall support.

Important behavior: when `FREEBSD` is set, `freebsd/handle_syscalls.c` is used; when `LINUX` is set, `linux/handle_syscalls.c` is used. The selected source is built as an object library `fsal_os` with sanitizers and `-fPIC`. LTTng-generated headers are added as dependencies when tracing is enabled.

Control flow and state: build-time platform selection determines the runtime persistent-handle format and syscalls. No runtime state is stored here.

Dependencies and integration points: the `fsal_os` object library is linked into VFS and Lustre FSAL modules by `vfs/CMakeLists.txt`.

Risks: exactly one platform source must be selected; missing `LINUX`/`FREEBSD` leaves `fsal_os_STAT_SRCS` empty. Handle format incompatibilities are platform-defined, so mixed build/runtime assumptions are unsafe.

Test signals: configure Linux and FreeBSD builds, verify `fsal_os` has one source, and run handle create/open/recreate tests on each platform.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/os/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/os/freebsd/handle_syscalls.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/os/freebsd/handle_syscalls.c

Purpose: this file implements FreeBSD-specific persistent handle operations using `getfhat`, `fhopen`, and FreeBSD file-handle structures.

Important functions: `vfs_sizeof_handle` computes packed handle length from `v_fhandle`. `display_vfs_handle` logs fsid and fid details. `vfs_fd_to_handle` and `vfs_name_to_handle` call `getfhat` with follow/no-follow flags. `vfs_open_by_handle` calls `fhopen` and maps `ENOENT` to `ESTALE`. `vfs_extract_fsid` extracts `FSID_TWO_UINT32`. `vfs_encode_dummy_handle` encodes a filesystem fsid into fid data, marks `fh_flags` as `HANDLE_DUMMY`, and sets reserved fsid type metadata. `vfs_is_dummy_handle` and `vfs_valid_handle` classify and validate handles. `vfs_re_index` obtains the root handle, extracts its fsid, and reindexes the Ganesha filesystem registry.

Control flow and state: persistent handle bytes are FreeBSD `v_fhandle` bytes. On filesystem claim, reindexing aligns Ganesha's fsid with the fsid embedded in FreeBSD handles.

Dependencies and integration points: depends on FreeBSD mount/fhandle APIs, `syscalls.h`, FSAL fsid encoding helpers, and VFS common methods. Used through the common syscall interface by export and handle code.

Risks: handle length must fit `VFS_HANDLE_LEN`; the compile-time check guards `MAXFIDSZ`. Dummy handles use special `fh_flags` and encoded fsid in fid data; validation must reject malformed lengths. `fhopen` errors drive stale-handle behavior.

Test signals: create handles for root, files, directories, symlinks; reopen by handle; stale deleted handles; dummy handle encode/validate; fsid reindex on export claim; invalid length/fid cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/os/freebsd/handle_syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/os/linux/handle_syscalls.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/os/linux/handle_syscalls.c

Purpose: this file implements Linux-specific persistent VFS handle encoding, validation, extraction, and reopening using `name_to_handle_at` and `open_by_handle_at`.

Important functions and format: the first handle byte stores fsid type, handle type width flags, and a dummy flag. `display_vfs_handle` decodes the fsid, type, dummy marker, and opaque bytes for logging. `vfs_map_name_to_handle_at` calls `name_to_handle_at`, encodes the configured fsid, encodes the kernel handle type as 8/16/32 bits, appends opaque kernel handle bytes, and enforces `VFS_HANDLE_LEN`. `vfs_open_by_handle` reconstructs `struct file_handle` from the encoded bytes and calls `open_by_handle_at(root_fd(fs), ...)`. `vfs_fd_to_handle`, `vfs_name_to_handle`, `vfs_extract_fsid`, `vfs_encode_dummy_handle`, `vfs_is_dummy_handle`, `vfs_valid_handle`, and `vfs_re_index` complete the interface.

Control flow and state: Linux handles require a live root fd for the mount stored during filesystem claim. Fsid is embedded in the NFS-visible handle so incoming handles can be mapped back to the correct `fsal_filesystem`. Dummy handles encode only fsid and cannot be reopened.

Dependencies and integration points: uses Linux file handle syscalls, FSAL fsid encode/decode helpers, and the VFS root fd stored by `export.c`. Common handle and export code call these functions through `fsal_handle_syscalls.h`.

Risks: handle size limits are tight; Btrfs/GPFS-like 40-byte handles plus wide fsids and 32-bit handle types can exceed the NFS handle budget. Validation must account for fsid length, type width, minimum and maximum kernel handle sizes. `open_by_handle_at` maps `ENOENT` to `ESTALE`; permission/capability failures can surface as FSAL errors. Dummy handles must not be treated as reopenable.

Test signals: ext4/xfs/btrfs-style handle sizes, all fsid types, 8/16/32-bit handle types, invalid first byte/type flags, oversized handles, deleted-file stale opens, dummy handles, and root fd closure/reopen failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/os/linux/handle_syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/state.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/state.c

Purpose: this file provides VFS state-handle storage for builds using `VFS_NO_MDCACHE`, keyed by object handle bytes.

Important functions: `vfs_state_cmpf` compares `gsh_buffdesc` keys by length then bytes. `vfs_state_lookup` searches the AVL tree. `vfs_state_init` initializes the global tree. `vfs_state_release` removes and frees an entry by key. `vfs_state_locate` maps an object to a persistent `state_hdl`, creating a `vfs_state_entry` if needed and initializing it with `state_hdl_init`.

Control flow and state: a process-global AVL tree maps file-handle keys to `state_hdl` objects. `vfs_state_locate` always updates `ostate.file.obj` to the current object pointer, allowing reconstructed handles to reuse state. `free_vfs_fsal_obj_handle` releases state entries for regular files.

Dependencies and integration points: uses Ganesha SAL state structures, AVL helpers, object `handle_to_key`, and VFS handle release paths.

Risks: the tree is global and this file does not show explicit locking; correctness depends on surrounding serialization or build-mode assumptions. Keys point at handle memory (`gsh_buffdesc`) rather than deep-copying bytes, so lifetime must be tied to object handles. Race handling after `avltree_insert` frees the loser entry but still depends on safe concurrent tree access.

Test signals: locate/release cycles for duplicate handles, reconstructed handles, concurrent state lookup if supported, regular-file handle release, and no-MDCACHE builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/subfsal.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/subfsal.h

Purpose: this header defines the VFS sub-FSAL extension interface used by plain VFS, Lustre-over-VFS, and related modules.

Important APIs: `vfs_sub_export_param` exposes sub-FSAL export config parameters. `vfs_sub_fini`, `vfs_sub_init_export_ops`, `vfs_sub_init_export`, `vfs_sub_alloc_handle`, and `vfs_sub_init_handle` let each sub-FSAL extend export operations, allocate larger private handles, and attach per-handle operations/data.

Control flow and state: export creation calls sub-FSAL init hooks after base export setup; handle allocation goes through `vfs_sub_alloc_handle` so sub-FSAL-specific structs can embed or extend `vfs_fsal_obj_handle`; handle initialization calls `vfs_sub_init_handle`.

Dependencies and integration points: included by VFS export/handle code and implemented by sub-FSAL-specific files such as `vfs/subfsal_vfs.c` or Lustre variants.

Risks: allocation layout is critical because the returned object must contain a valid `vfs_file_handle_t` area pointed to by `handle`. Hook ordering must match export lifetime or sub-FSAL cleanup can see partially initialized objects.

Test signals: plain VFS and Lustre module initialization, export config parsing, handle allocation size/layout, and cleanup ordering on export creation failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/subfsal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/subfsal_helpers.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/subfsal_helpers.c

Purpose: this helper implements referral filesystem-location extraction for VFS sub-FSALs using a `user.fs_location` xattr.

Important function: `vfs_get_fs_locations` opens the directory if no fd is supplied, resolves `/proc/self/fd/<fd>` to a real path, rewrites the path from export full path to pseudopath when needed, reads `user.fs_location` through VFS xattr helpers, parses it as `server:path`, and creates an `nfs4_fs_locations` structure with one server.

Control flow and state: the function may replace `attrs_out->fs_locations`, set `ATTR4_FS_LOCATIONS`, and close only fds it opened locally. It releases any existing fs_locations before populating a new one.

Dependencies and integration points: used by `vfs/vfs/attrs.c` common attr hook and `handle.c` referral population. Depends on `/proc/self/fd`, export context macros, `vfs_getextattr_value`, and NFSv4 fs_locations helpers.

Risks: Linux `/proc/self/fd` availability is assumed. Path rewrite checks total length but depends on the fd path starting with `CTX_FULLPATH(op_ctx)`. The xattr parser requires a colon; malformed values clear locations without returning a hard error. Single-server support may be too narrow for complex referrals.

Test signals: referrals with full path equal/different from pseudopath, missing xattr, malformed xattr, long pseudopath rewrite, supplied fd versus local open, and cleanup of previous fs_locations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/subfsal_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/CMakeLists.txt

Purpose: this CMake file builds the plain VFS, Lustre, and dummy-Lustre FSAL shared modules from common VFS sources.

Important behavior: it defines `fsalvfs_LIB_SRCS_common` with base export, handle, syscall, file, xattr, state, sub-FSAL helper, `subfsal_vfs.c`, and `attrs.c`. Optional POSIX ACL support adds `../../posix_acls.c` and `gos` objects. `USE_FSAL_VFS` configures `main-c.in.cmake` with name `VFS`, adds `empty_check_hsm.c`, builds `fsalvfs`, links `ganesha_nfsd` and system libraries, sets version `4.2.0`, and installs it. `USE_FSAL_LUSTRE` configures a Lustre or dummy-Lustre entry point, adds `llapi_check_hsm.c`, and links `lustreapi` only when `USE_LLAPI` is true.

Control flow and state: build-time flags select module name, HSM implementation, ACL support, and link libraries. Generated `main.c`/`lustre_main.c`/`dummy_lustre_main.c` specialize the same module template.

Dependencies and integration points: consumes the `fsal_os` object library from `os/CMakeLists.txt`, Ganesha core library, optional `lustreapi`, and optional POSIX ACL support objects.

Risks: common sources are shared across modules, so changes can affect VFS and Lustre. Dummy-Lustre builds include `llapi_check_hsm.c` but without `USE_LLAPI`, relying on preprocessor no-op paths. Link options use `LDFLAG_DISALLOW_UNDEF`, so missing optional libraries surface at build time.

Test signals: configure/build plain VFS, Lustre with LLAPI, dummy Lustre without LLAPI, POSIX ACL enabled/disabled, and sanitizer/LTTng combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/attrs.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/attrs.c

Purpose: this file implements VFS sub-FSAL attribute hooks, especially referrals and optional ACL support.

Important functions: `vfs_sub_getattrs_common` populates `ATTR4_FS_LOCATIONS` for referral directories via `vfs_get_fs_locations`. `vfs_sub_getattrs_release` releases an existing ACL in an attrlist. Under `ENABLE_VFS_DEBUG_ACL`, an AVL-backed in-memory ACL store is implemented with `vfs_acl_init`, `vfs_acl_release`, `vfs_sub_getattrs`, and `vfs_sub_setattrs`. Under `ENABLE_VFS_POSIX_ACL`, `vfs_sub_getattrs` reads effective/default POSIX ACLs, converts them to FSAL ACLs, and sets `ATTR_ACL`; `vfs_sub_setattrs` converts FSAL ACLs back to POSIX access/default ACLs and writes them by fd. With neither option, getattrs only handles referrals and setattrs is a no-op.

Control flow and state: referral handling is common across all builds. Debug ACL mode stores ACLs in a process-global AVL keyed by object handle bytes. POSIX ACL mode reads/writes kernel ACL state on the object fd and skips object types where fd ACL access is invalid. `vfs_setattr2` and `fetch_attrs` call these hooks from file operations.

Dependencies and integration points: uses FSAL access/ACL conversion helpers, NFSv4 ACL intern/refcount helpers, POSIX ACL APIs when enabled, and `subfsal_helpers.c` for referrals.

Risks: debug ACL storage is not persistent and appears unprotected by explicit locks. POSIX ACL conversion doubles initial ACE allocation then shrinks after conversion; conversion errors must not leak ACL memory. `acl_set_fd` error mapping uses `fsalstat(errno, 0)` in some paths instead of `posix2fsal_error`, which should be verified. Referral getattrs passes `fd == -1` in some paths and POSIX ACL mode deliberately skips ACL reads for that case.

Test signals: referral fs_locations with/without ACLs, debug ACL get/set/release, POSIX ACL read/write on files and directories, default ACLs on directories, symlink/device/socket skip behavior, no-ACL builds, and attrlist ACL release/refcount correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/attrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/attrs.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/attrs.h

Purpose: this header declares VFS sub-FSAL attribute and ACL hook functions.

Important APIs: `vfs_acl_init`, `vfs_sub_getattrs`, and `vfs_sub_setattrs`. The get/set hooks accept a VFS object handle, an fd, requested attribute mask, and an attrlist.

Control flow and state: base VFS file and handle code call these hooks through `sub_ops` to extend POSIX attributes with referrals and optional ACL data. `vfs_acl_init` is meaningful in debug ACL builds.

Dependencies and integration points: includes `../vfs_methods.h` for VFS handle types and FSAL attr structures. Implemented by `vfs/attrs.c`.

Risks: declarations are unconditional while implementations vary by compile flags; callers must tolerate no-op behavior when ACL support is disabled.

Test signals: compile all ACL flag combinations and verify the same symbols are provided.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/attrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/llapi_check_hsm.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/llapi_check_hsm.c

Purpose: this file implements the Lustre HSM-aware `check_hsm_by_fd` hook used by FSAL_LUSTRE and dummy-Lustre builds.

Important function: `check_hsm_by_fd` reads `async_hsm_restore` from the current VFS export. If disabled, or if built without `USE_LLAPI`, it returns success. With LLAPI enabled, it calls `llapi_hsm_state_get_fd`, checks `HS_RELEASED`, allocates one-item `hsm_user_request`, gets the file FID with `llapi_fd2fid`, requests `HUA_RESTORE` over the whole file with `llapi_hsm_request`, and returns `ERR_FSAL_DELAY` when a restore is triggered.

Control flow and state: VFS open paths call this hook after opening a fd. A released Lustre file turns an otherwise successful open into a delay/retry signal. The HSM request is submitted to the filesystem root path from `op_ctx->fsal_export->root_fs`.

Dependencies and integration points: depends on Lustre `lustreapi.h` when `USE_LLAPI` is set, FSAL error conversion, and VFS export private config. Plain VFS links a no-op replacement instead.

Risks: memory allocated by `llapi_hsm_user_request_alloc` is not freed in the visible function after request submission or some errors. Error returns from LLAPI are negative errno-style values and are converted with `-rc` in logging/status. Dummy-Lustre builds compile the no-LLAPI path, so HSM restore is silently disabled.

Test signals: `async_hsm_restore` false/true, no-LLAPI build, LLAPI errors from state get/fid/request, released and non-released states, open path mapping of `ERR_FSAL_DELAY` to retry behavior, and request allocation cleanup under sanitizers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/llapi_check_hsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/main-c.in.cmake -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/main-c.in.cmake

Purpose: this CMake template generates the module entry point for VFS, Lustre, or dummy-Lustre FSAL modules.

Important types and functions: `VFS_SUPPORTED_ATTRIBUTES` advertises POSIX attrs, xattrs, fs_locations, and optionally ACLs. The static `struct vfs_fsal_module VFS` sets `fs_info` limits/capabilities, including max file size, link/name/path limits, chown restriction, case behavior, named attrs, unique handles, ACL support, max IO, xattr support, and default lock support false. `vfs_params` defines module config options such as link/symlink support, cansettime, maxread/maxwrite, umask, `auth_xdev_export`, and `only_one_user`. `init_config` probes OFD lock support with `F_OFD_GETLK`, loads config, validates errors, and logs fsinfo. `vfs_init` registers the FSAL with generated `myname`, installs module ops, and initializes object ops. `vfs_unload` unregisters the FSAL.

Control flow and state: module load registers one global `VFS` module instance. Runtime config can adjust the advertised fsinfo fields. OFD lock support is feature-probed using a temporary file before config display. Module unload unregisters the FSAL.

Dependencies and integration points: generated by `vfs/CMakeLists.txt` with `@FSAL_LUSTRE_VFS_NAME@` set to `VFS`, `LUSTRE`, or `DUMMYLUSTRE`. It connects `vfs_create_export`, `vfs_update_export`, `init_config`, and `vfs_handle_ops_init` to Ganesha's FSAL registry.

Risks: the module initializes `.acl_support = FSAL_ACLSUPPORT_ALLOW` even when `VFS_SUPPORTED_ATTRIBUTES` excludes `ATTR_ACL`, so consumers should verify actual supported attr masks. Lock support depends on runtime OFD lock probing. The lock-test path uses `/tmp`; restricted environments can disable lock support despite kernel support.

Test signals: module load/unload, config parsing with valid/invalid values, OFD lock probe success/failure, generated names for all three modules, supported attribute masks with ACL enabled/disabled, and export creation through registered module ops.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/main-c.in.cmake -->
