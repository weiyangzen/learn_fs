# Research: subset-b-009694

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/handle.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/handle.c

This file implements the object-handle operation vector for the RGW FSAL. It adapts Ganesha handle operations to librgw file-handle APIs for lookup, directory enumeration, create, open, read/write, commit, close, setattr, wire-handle encoding, optional extended attributes, and share-state merging.

Important functions are `lookup_int`, `rgw_fsal_readdir`, `rgw_fsal_mkdir`, `getattrs`, `rgw_fsal_setattr2`, `rgw_fsal_open2`, `rgw_fsal_reopen2`, `rgw_fsal_read2`, `rgw_fsal_write2`, `rgw_fsal_commit2`, `rgw_alloc_state`, `rgw_fsal_close2`, `handle_to_wire`, `handle_to_key`, and `handle_ops_init`. The private state is `struct rgw_handle` from `internal.h`, which stores the public `fsal_obj_handle`, a librgw `rgw_file_handle`, an export pointer, `fsal_share`, and open flags. Per-open state is `struct rgw_open_state`.

Control flow is mostly direct translation: lookup calls `rgw_lookup`, refreshes with `rgw_getattr`, then constructs a new handle; readdir invokes `rgw_readdir2`, and the callback looks up each entry to build Ganesha handles and attributes; create/open by name calls `rgw_create`, then `rgw_open`; open by handle checks or updates share reservations before `rgw_open`; read/write iterate the supplied iovecs using `rgw_read`/`rgw_write`; stable writes call `rgw_fsync`; commit calls `rgw_commit`; close calls `rgw_close` and updates open/share state. Attribute setting maps FSAL masks to RGW setattr flags and handles truncate separately.

State is process-local and handle-local. No metadata is persisted here; persistence belongs to RGW. Wire handles and hash keys are derived from `rgw_fh->fh_hk`, so handle stability depends on librgw's bucket/object key semantics. The code integrates with `fsal_default_obj_ops_init`, Ganesha share counters, `op_ctx`, POSIX-to-FSAL converters, and optional `USE_FSAL_RGW_XATTRS` callbacks.

Risks include complicated error cleanup in create/open paths, a likely suspicious unlink-on-create-error call using the newly created object handle rather than the parent directory handle, reliance on `errno` in xattr paths after librgw returns negative codes, limited READ_PLUS support, and librgw's lack of a conventional fd abstraction causing shared handle-level open state. Test signals should cover create modes, verifier handling, truncation, share denial, stateless NFSv3 I/O, readdir cookies, xattr compile mode, close idempotence, and stale/invalidation behavior after rename/unlink.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/internal.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/internal.c

This file contains RGW FSAL internal helpers shared by module/export and handle operations. Its main responsibilities are converting librgw negative POSIX-style errors into `fsal_status_t` and constructing/destructing private RGW object handles.

The key API is `rgw2fsal_error(int)`, which stores the positive POSIX errno in `minor` and maps common conditions to FSAL majors such as `ERR_FSAL_NOENT`, `ERR_FSAL_IO`, `ERR_FSAL_ACCESS`, `ERR_FSAL_EXIST`, `ERR_FSAL_STALE`, and `ERR_FSAL_DELAY`. `construct_handle` allocates a `struct rgw_handle`, attaches the librgw `rgw_file_handle`, copies upcall ops from the export, initializes the embedded public object handle with `fsal_obj_handle_init`, assigns `RGWFSM.handle_ops`, fills fsid/fileid from `struct stat`, and returns it to the caller. `deconstruct_handle` finalizes the public handle and frees the private allocation.

Control flow is intentionally small: callers obtain an RGW handle/stat from librgw, call `construct_handle`, then later call `release` in `handle.c`, which may release the librgw file-handle reference and then call `deconstruct_handle`. This file does not own persistence; it creates in-memory wrappers around persistent RGW objects.

Dependencies are Ganesha FSAL types, `fsal_convert`, common allocation helpers, and the declarations in `internal.h`. The error mapping is an integration point between librgw and every FSAL operation that returns provider errors.

Risks are mostly semantic drift: if librgw adds important negative errors, unmapped cases become `ERR_FSAL_SERVERFAULT`; `EBADF` is mapped to `ERR_FSAL_NOT_OPENED` even though comments note access-mode ambiguity; `construct_handle` does not check allocation failure because Ganesha allocation helpers are expected to abort. Test signals should verify representative error translations and ensure constructed handles get correct type, fsid, fileid, ops vector, export pointer, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/internal.h -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/internal.h

This header defines the private contract for FSAL_RGW. It ties Ganesha FSAL structures to librgw types and exposes the internal functions used across `main.c`, `handle.c`, `internal.c`, and `up.c`.

Important types are `struct rgw_fsal_module`, the singleton module wrapper containing `struct fsal_module`, the object ops vector, config strings, and `librgw_t`; `struct rgw_export`, containing the public export, `struct rgw_fs`, root handle, and RGW user/access credentials; `struct rgw_handle`, containing the public object handle, librgw file handle, upcall vector, export pointer, share reservation state, and open flags; and `struct rgw_open_state`, embedding a `state_t` plus open flags. Attribute support masks expose POSIX attributes and optionally `ATTR4_XATTR` when `USE_FSAL_RGW_XATTRS` is enabled. The header also enforces a minimum `librgw_file` version at compile time.

State is divided into module-global library state, per-export mount/authentication state, per-object handle state, and per-open state. Wire identity is not defined here directly, but the handle stores `rgw_file_handle`, whose `fh_hk` is used by handle digest and invalidation paths.

Dependencies include Ganesha FSAL headers, `sal_data.h`, uuid/dirent system headers, and Ceph `librgw.h`/`rgw_file.h`. Integration points are the exported prototypes for handle/export ops initialization, state allocation, error conversion, and RGW invalidation upcalls.

Risks include broad sharing of the global `RGWFSM`, credential string lifetimes from config parsing, and coupling to librgw internal handle-key layout. Test signals should include compile coverage for librgw version guards, xattr/non-xattr builds, and ABI-sensitive uses of `struct rgw_fh_hk` in wire handles and upcalls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/main.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/main.c

This file registers the RGW FSAL module, parses module/export configuration, initializes librgw once, mounts an RGW filesystem per export, creates the root handle, and unregisters/shuts down the module at unload.

The singleton `RGWFSM` defines static FSAL capabilities: large file size, 1024 name/path length, no links/symlinks/locks, named attributes, unique handles, settable times, optional xattrs, computed readdir cookies, and chunked readdir. `rgw_items` configures global Ceph options (`ceph_conf`, `name`, `cluster`, `init_args`, `umask`). Export params require `user_id`, `access_key_id`, and `secret_access_key`. `init_config` loads module config and displays fs info. `create_export` performs lazy `librgw_create` under `init_mtx`, parses export credentials, calls `rgw_mount` or optional `rgw_mount2`, attaches the export, registers invalidation upcalls, fetches root attributes, constructs the root handle, and sets `op_ctx->fsal_export`. `init` registers the FSAL and installs module/handle ops. `finish` unregisters and calls `librgw_shutdown`.

State persistence is external to Ceph RGW. This file owns process lifetime for the librgw instance and per-export mount handles. The root handle is held in `struct rgw_export` and normal object persistence is represented by librgw handles.

Dependencies include Ganesha config parsing, FSAL registration, export manager context, common allocation, and librgw. Integration points are the `MODULE_INIT`/`MODULE_FINI` symbols, `fsal_attach_export`, invalidation registration, and `handle_ops_init`.

Risks include incomplete cleanup on several `create_export` error paths, logging but continuing when `ceph.conf` is missing, module-global initialization races if `librgw_create` fails, and credential requirements that must match RGW auth behavior. Test signals should cover config validation, failed librgw init, bad credentials, repeated exports, mount2 path cases, root getattr failures, invalidation registration failure, and module unload after partially initialized exports.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/up.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/up.c

This file implements the RGW FSAL upcall bridge. It receives invalidation notifications from librgw and forwards them into Ganesha's FSAL upcall vector so cached objects can be invalidated.

The only function is `rgw_fs_invalidate(void *handle, struct rgw_fh_hk fh_hk)`. The `handle` argument is expected to be a `struct rgw_export *` that was registered in `main.c` via `rgw_register_invalidate`. The function validates the export and `export->export.up_ops`, wraps the RGW file-handle key in a `gsh_buffdesc`, and calls `up_ops->invalidate(..., FSAL_UP_INVALIDATE_CACHE)`. Errors are logged but not returned because the librgw callback is asynchronous and has `void` return type.

State behavior is transient. The upcall does not persist anything; it translates an RGW handle key into a cache invalidation request. The file relies on the same `struct rgw_fh_hk` layout used by `handle_to_wire` and `handle_to_key`, so cache identity must remain consistent across librgw, Ganesha wire handles, and upcall invalidation.

Dependencies include FSAL APIs, export context headers, common FSAL support, and the RGW internal definitions. The integration point is the callback registration in `create_export`.

Risks include lost invalidations if the export pointer or upcall vector is missing, no retry on `invalidate` failure, and possible cache-key mismatch if librgw changes `fh_hk`. Test signals should include forced invalidation callbacks with valid and null exports, validation that the same key invalidates handles created by lookup/open, and log/error behavior when the upcall vector rejects invalidation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/up.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/CMakeLists.txt

This build file defines the SaunaFS FSAL shared module `fsalsaunafs`. It is the build integration point that collects the FSAL implementation files, links against the SaunaFS client library, attaches optional sanitizer/LTTng behavior, and installs the resulting module into the configured FSAL destination.

The source list includes the files in this research item plus adjacent support files: ACL handling, internal error/context helpers, and private type headers. `add_library(fsalsaunafs MODULE ...)` builds a dynamically loaded Ganesha FSAL module. `target_link_libraries(fsalsaunafs ${SAUNAFS_CLIENT_LIB})` is the critical external dependency. `add_sanitizers` applies the repository's sanitizer wrapper. When `USE_LTTNG` is enabled, the target depends on generated trace headers and includes generated CMake file properties. The module version and soversion are set to `4.0.0` and `4`.

There is no runtime state in this file, but it controls which implementation objects are present in the module. Missing any of `context_wrap`, `handle`, `export`, `ds`, or `mds_*` would remove core runtime capabilities.

Dependencies are CMake variables from the parent build, the SaunaFS client library, sanitizer macros, LTTng generation, and `FSAL_DESTINATION`. Integration is with Ganesha's plugin loading convention; the FSAL name in `main.c` expects a matching shared library.

Risks include stale source lists when new implementation files are added, unresolved `${SAUNAFS_CLIENT_LIB}` configuration, and trace-generation ordering issues under `USE_LTTNG`. Test signals are configure/build with and without LTTng, sanitizer builds, install-tree validation, and module load tests confirming `libfsalsaunafs.so` exports the expected init/fini symbols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/context_wrap.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/context_wrap.c

This file is a thin credential/context adapter around the SaunaFS C API. Each wrapper creates a `sau_context_t` from the current Ganesha user credentials, invokes one `sau_*` operation, and destroys the context with GCC cleanup attributes where used.

The wrappers cover lookup, mknod, open, read, write, flush, getattr, opendir/readdir, mkdir, rmdir, unlink, setattr, fsync, rename, symlink, readlink, link, chunk-info retrieval, ACL get/set, byte-range locks, and xattr get/set/list/remove. Inputs are `sau_t *instance`, optional `struct user_cred *cred`, inodes, names, stat data, `fileinfo_t`, or SaunaFS-specific structs. Most functions return the underlying integer status or pointer; context creation failure returns `-1` or `NULL`.

Control flow is deliberately uniform: `createContext(instance, cred)`, null check, call the matching `sau_*` API. This keeps handle/export/ds code independent of raw context management. One notable inconsistency is `saunafs_getlock`, which creates a context without the cleanup attribute, so its context lifetime depends on external behavior or is a leak risk.

State is not persisted here. The context is temporary per operation and the persistent state lives in SaunaFS metadata/data servers and in `sau_fileinfo_t` objects returned from open/opendir.

Dependencies are `context_wrap.h`, `saunafs_internal.h`, and the SaunaFS C API. Integration points are almost every SaunaFS FSAL operation in `handle.c`, `export.c`, `ds.c`, and `mds_handle.c`.

Risks include context allocation failures being collapsed to generic errors, the `saunafs_getlock` cleanup asymmetry, and wrapper signatures that sometimes allow `cred == NULL` for pNFS data-server operations. Test signals should mock or integration-test context creation failure, credential propagation, every wrapper's error mapping via callers, and lock/xattr operations with real SaunaFS servers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/context_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/context_wrap.h -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/context_wrap.h

This header declares the SaunaFS context wrapper API used by the FSAL implementation. Its purpose is to expose credential-aware operations with Ganesha-friendly signatures while hiding direct `sau_context_t` creation and destruction from handle, export, MDS, and DS code.

The declarations include namespace-like `saunafs_*` functions for metadata operations (`lookup`, `mknode`, `mkdir`, `rmdir`, `unlink`, `rename`, `symlink`, `readlink`, `link`), file operations (`open`, `read`, `write`, `flush`, `fsync`), attribute operations (`getattr`, `setattr`), directory operations (`opendir`, `readdir`), pNFS support (`get_chunks_info`), ACL support (`setacl`, `getacl`), byte-range locking (`setlock`, `getlock`), and xattrs (`getxattr`, `setxattr`, `listxattr`, `removexattr`).

State behavior is implicit in the types: `sau_t` represents a mounted SaunaFS client instance, `struct user_cred` supplies caller credentials, `sau_inode_t` identifies persistent filesystem objects, and `fileinfo_t`/`sau_fileinfo` represent open file or directory state returned by the client library.

Dependencies are `fsal_types.h` and `saunafs_fsal_types.h`, which supplies `fileinfo_t` and SaunaFS types. This header is a major integration boundary between Ganesha's FSAL layer and the SaunaFS client C API.

Risks include declarations that mirror external C API types closely, so client library ABI/API changes ripple into the FSAL. Since errors are mostly raw `int`/pointer returns, callers must consistently use `fsalLastError`, `nfs4LastError`, or `saunafsToFsalError`. Test signals should include compiler coverage against the target SaunaFS client version and caller tests that validate every failure path uses the proper error conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/context_wrap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/ds.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/ds.c

This file implements SaunaFS pNFS data-server operations. It creates data-server handles from pNFS wire handles, opens/caches SaunaFS file handles for direct I/O, services DS read/write/commit calls, and installs the DS operation vector.

Important functions are `clearFileInfoCache`, `dsh_release`, `openfile`, `dsh_read`, `dsh_write`, `dsh_commit`, `dsh_read_plus`, `make_ds_handle`, `ds_permissions`, and `pnfsDsOperationsInit`. `struct DataServerHandle` stores the public `fsal_ds_handle`, inode, and an optional `FileInfoEntry_t` from the export-level fileinfo cache. `struct DSWire` is the client-visible DS wire payload containing the inode.

Control flow for I/O starts with `make_ds_handle`, which validates and endian-converts the inode from the wire buffer. `dsh_read`/`dsh_write` locate the MDS FSAL export through `op_ctx->ctx_pnfs_ds`, call `openfile`, extract a cached `fileinfo_t`, and invoke `saunafs_read` or `saunafs_write` with no user credentials. Writes flush when requested stability is not `UNSTABLE4`; commit flushes and returns an all-zero verifier. Release returns the cache entry to the LRU and opportunistically clears expired entries.

State is centered on `FileInfoCache_t`: DS handles retain acquired cache entries while alive; released entries can be reused or expired. Persistent file data belongs to SaunaFS. DS permissions install root export permissions in `op_ctx`.

Dependencies include pNFS DS defaults, Ganesha export context, the SaunaFS wrappers, and the fileinfo cache. Risks include weak stateid validation, `dsh_commit` returning OK if opening fails, no READ_PLUS support, credential-null I/O semantics, and cache correctness under concurrent DS handles. Test signals should cover endian wire handles, bad handles, repeated read/write sharing a cached fileinfo, cache expiry, stable write flush failures, DS permission behavior, and NFSv4.2 READ_PLUS rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/export.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/export.c

This file implements SaunaFS export operations: export release, path lookup, dynamic filesystem information, state allocation/freeing, wire/host handle conversion, handle reconstruction, supported attributes/ACL reporting, and operation-vector initialization.

Key functions are `release`, `lookup_path`, `get_dynamic_info`, `fs_free_state`, `allocate_state`, `wire_to_host`, `host_to_key`, `create_handle`, `fs_acl_support`, `fs_supported_attrs`, `get_fsal_obj_hdl`, and `exportOperationsInit`. `allocate_state` creates a `SaunaFSStateFd` with an embedded `SaunaFSFd` initialized as `FSAL_FD_STATE`. `wire_to_host` validates and endian-converts a `sau_inode_t`; `host_to_key` adds the current export id into `SaunaFSHandleKey`; `create_handle` rehydrates an inode handle by calling `saunafs_getattr`.

Control flow for root/path lookup validates exported path prefixes, special-cases `/`, then calls `saunafs_lookup` below `SPECIAL_INODE_ROOT` and allocates a handle. Release tears down root handle, detaches export ops, drains the fileinfo cache by forcing zero timeout/size, releases cached SaunaFS file handles, destroys the client instance, frees duplicated `subfolder`, and frees the export.

State and persistence are per-export: `sau_t *fsInstance`, root handle, cached DS fileinfo entries, and FSAL open states. Persistent metadata remains in SaunaFS. Dynamic stats come from `sau_statfs`.

Dependencies include Ganesha common FSAL/export helpers, `context_wrap`, private types, ACL option checks, and SaunaFS statfs/getattr APIs. Integration points are `main.c` export creation and all handle reconstruction after NFS filehandle cache misses.

Risks include path-prefix validation edge cases, cleanup ordering with pNFS DS references, forced cache draining while handles may be in use, and endian assumptions for 32-bit `sau_inode_t`. Test signals should cover root lookup, non-root path lookup, stale wire handle reconstruction, big-endian/little-endian handle conversion, ACL-disabled exports, statfs mapping, and export release with populated DS cache.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/fileinfo_cache.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/fileinfo_cache.c

This file implements a small thread-safe cache for SaunaFS `sau_fileinfo_t` objects used mainly by pNFS data-server handles. It tracks entries by inode, separates in-use entries from LRU entries, and expires entries by timeout or maximum count pressure.

Private types are `struct FileInfoEntry` and `struct FileInfoCache`. Entries contain list/tree hooks, inode, `fileinfo`, timestamp, `is_used`, and a `lookup` flag used by the AVL comparator. The cache contains LRU and used lists, an AVL tree for available entries, count/limit settings, timeout, and a mutex. Public APIs are `createFileInfoCache`, `resetFileInfoCacheParameters`, `destroyFileInfoCache`, `acquireFileInfoCache`, `releaseFileInfoCache`, `eraseFileInfoCache`, `popExpiredFileInfoCache`, `fileInfoEntryFree`, `extractFileInfo`, and `attachFileInfo`.

Control flow: acquire looks up an unused entry by inode in the AVL tree; if found, it moves it from LRU to used and removes it from lookup, otherwise allocates a new entry. Release moves a used entry to LRU and reinserts into the AVL tree. Pop-expired inspects the oldest LRU entry and removes it if the cache is over capacity or the minimum timeout has elapsed. Destroy frees entries but deliberately does not release `fileinfo` objects; callers such as export release and DS cache clear do that.

State is in-memory only. Timestamps use `timespec_get(TIME_UTC)` converted to milliseconds. Persistence is the open SaunaFS fileinfo object referenced by entries.

Dependencies include Ganesha `glist`, `avltree`, allocation helpers, pthread mutexes, and SaunaFS C API types. Risks include no hard cap during acquire, reliance on callers to release `fileinfo`, assert-heavy misuse detection, duplicate entries possible for in-use same-inode handles, and time conversion naming using nanoseconds divided by a microsecond constant. Test signals should cover concurrent acquire/release, duplicate inode use, timeout expiry, max-entry pressure, erase-on-open-failure, and destroy after drained cache.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/fileinfo_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/fileinfo_cache.h -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/fileinfo_cache.h

This header declares the opaque fileinfo cache used by the SaunaFS FSAL. It provides a C ABI around cached `sau_fileinfo_t` pointers without exposing list/tree internals to DS or export code.

The main public types are `fileinfo_t` as an alias for `sau_fileinfo_t`, opaque `FileInfoCache_t`, and opaque `FileInfoEntry_t`. The lifecycle functions are `createFileInfoCache`, `resetFileInfoCacheParameters`, and `destroyFileInfoCache`. Entry management functions are `acquireFileInfoCache`, `releaseFileInfoCache`, `eraseFileInfoCache`, `popExpiredFileInfoCache`, and `fileInfoEntryFree`. Accessors `extractFileInfo` and `attachFileInfo` move the underlying SaunaFS fileinfo pointer in or out of an acquired entry.

State semantics are part of the contract: acquiring can return an entry whose fileinfo is NULL, meaning the caller must open the file and attach the fileinfo before release; erase is used when opening failed and the entry should not enter the LRU; pop-expired removes an unused entry and transfers responsibility to the caller to release the contained fileinfo and free the entry.

Dependencies are limited to the SaunaFS C API and C++ compatibility guards. Integration points are `ds.c` for pNFS DS I/O reuse and `export.c`/`main.c` for cache creation and destruction.

Risks include caller-owned cleanup requirements that are easy to violate, no explicit error object for full-cache conditions despite comments mentioning NULL, and opaque entries that hide whether fileinfo is attached unless callers use `extractFileInfo`. Test signals should validate lifecycle pairing, failed-open erase, export shutdown draining, and C/C++ include compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/fileinfo_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/handle.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/handle.c

This file is the primary SaunaFS object-handle implementation. It maps Ganesha object operations to SaunaFS client calls for lookup, readdir, attributes, filehandle encoding, open/create, read/write/commit/close, setattr, links, rename/unlink, symlink/readlink, locks, special nodes, fallocate, xattrs, share merging, and handle allocation.

Important APIs include `handleOperationsInit`, `allocateHandle`, `deleteHandle`, `open2`, `openByHandle`, `openByName`, `reopen_func`, `read2`, `write2`, `commit2`, `setattr2`, `close2`, `lock_op2`, `fallocate_`, and the xattr functions. The key state types are `SaunaFSHandle` with embedded public handle, global `SaunaFSFd`, inode/key/export/share; and `SaunaFSStateFd`, which binds NFSv4 state to a per-state file descriptor.

Control flow uses `context_wrap` wrappers for SaunaFS operations and Ganesha fd helpers for concurrency. Opens by name perform lookup or `saunafs_mknode` then open by handle. Opens by handle use `fsal_start_fd_work_no_reclaim`, share conflict checks, and `reopen_func`. I/O uses `fsal_start_io`/`fsal_complete_io`, choosing state, global, or temporary fds; stateless I/O releases temporary share counters afterward. Setattr maps FSAL masks to `SAU_SET_ATTR_*`; locks translate FSAL lock operations to SaunaFS lock info and set the lock owner on fileinfo. Fallocate emulates allocate by extending size and deallocate by writing zeroes then restoring size.

State is in-memory per handle and state object; persistent changes are delegated to SaunaFS metadata/data services. Wire handles encode only `sau_inode_t`, while keys include module/export/inode.

Dependencies include FSAL fd/share helpers, POSIX conversion, SaunaFS wrappers, ACL helpers, error conversion, and optional Linux fallocate constants. Risks include long and subtle cleanup paths, possible NULL misuse in new-handle error handling, fallback zero-writing deallocation cost, unsupported READ_PLUS, xattr error conversion using raw return values, and lock owner casting. Test signals should cover every create mode, stateless/stateful I/O, share denial, fd reopen/no-op paths, link/symlink/mknode, ACL/xattr builds, fallocate allocate/deallocate, lock conflict reporting, and handle merge.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/main.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/main.c

This file registers and initializes the SaunaFS FSAL module, defines static capabilities and configuration parameters, creates exports, optionally enables pNFS MDS/DS support, creates the root handle, and unregisters the module on unload.

The singleton `SaunaFS` advertises POSIX-like capabilities: links, symlinks, locks, named attrs/xattrs, unique handles, pNFS MDS and DS support, optional ACL support, and SaunaFS attribute masks. Module-level config toggles static FS info such as umask, maxread/maxwrite, pNFS flags, tracing, and grace. Export config includes master hostname/port, mountpoint/subfolder, delayed init, read/write/cache timings, write-cache parameters, keep-cache, fileinfo cache limits, and password/md5 credentials. `createExport` parses config, initializes a `sau_t` client instance, attaches the export, creates DS registration when enabled, installs MDS export ops when enabled, reads root attributes, and allocates the root handle. `initializeSaunaFS` registers the FSAL, installs module ops, DS ops, MDS ops, and object ops.

State is process-local for the module and per-export for `SaunaFSExport`, including the `sau_t` instance, root handle, pNFS booleans, and optional fileinfo cache. Filesystem persistence lives in the SaunaFS cluster.

Dependencies include FSAL registration/config APIs, `pnfs_utils`, `context_wrap`, private SaunaFS types/internal helpers, `pnfs_ds_insert/remove/put`, and the SaunaFS C API.

Risks include complex pNFS DS registration cleanup, overwriting configured `subfolder` with `CTX_FULLPATH`, possible mismatch between FSAL config flags and actual export `fs_supports` results, and abort on unregister failure. Test signals should cover config parsing defaults, failed `sau_init_with_params`, pNFS MDS-only/DS-only/both/none exports, duplicate DS server id, root getattr failure cleanup, fileinfo cache creation failure, and module load/unload.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/mds_export.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/mds_export.c

This file implements pNFS metadata-server export/module operations for SaunaFS. It reports supported layouts, estimates XDR buffer sizes, and converts SaunaFS chunk/chunkserver topology into NFSv4.1 file-layout device information.

Important helpers are `randomizedChunkserverList`, `fillChunkDataServerList`, `fillUnusedDataServerList`, `releaseResources`, `getdeviceinfo`, `getdevicelist`, `fs_layouttypes`, `fs_layout_blocksize`, `fs_maximum_segments`, `fs_loc_body_size`, `fs_da_addr_size`, `exportOperationsPnfs`, and `pnfsMdsOperationsInit`. It filters disconnected chunkservers, removes duplicate IPs after sorting, randomizes usable servers, and encodes multipath data-server addresses with `FSAL_encode_v4_multipath`.

Control flow for `getdeviceinfo` validates `LAYOUT4_NFSV4_1_FILES`, finds the export by `deviceid->device_id2`, retrieves chunk info for `deviceid->devid`, builds a randomized chunkserver list, computes a stripe count bounded by `SAUNAFS_BIGGEST_STRIPE_COUNT`, encodes stripe indices, encodes chunk-local DS lists first, fills remaining stripes from randomized servers, and frees SaunaFS-allocated chunk metadata. `getdevicelist` returns EOF without entries; layouts rely on encoded device IDs from layoutget.

State is not stored persistently here. It derives layout/device answers from current SaunaFS chunkserver and chunk metadata. Randomization uses `srandom(time(NULL))` per shuffle call.

Dependencies include `pnfs_utils`, XDR helpers, SaunaFS chunk APIs, and FSAL module export lists. Risks include a suspicious `remove_if` copy direction that appears to copy from `step` to `i` rather than keeping element `i` at `step`, random seeding per request, no device list enumeration, fixed NFS port/protocol assumptions, and large XDR sizing. Test signals should cover disconnected/duplicate chunkservers, chunks with standard and nonstandard parts, no chunkservers, large files near stripe limits, device export lookup failure, and XDR encode failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/mds_export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/mds_handle.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/mds_handle.c

This file implements pNFS object-handle operations for SaunaFS MDS behavior: layoutget, layoutreturn, and layoutcommit. It encodes file layouts that point clients at DS handles and commits client-reported size/mtime changes back to SaunaFS metadata.

The main functions are `layoutget`, `layoutreturn`, `isOffsetChangedByClient`, `hasRecentModificationTime`, `layoutcommit`, and `handleOperationsPnfs`. `layoutget` validates the layout type, builds a `pnfs_deviceid` from FSAL id/export id/inode, encodes a `DSWire` inode payload with `FSAL_encode_file_layout`, uses `SFSCHUNKSIZE` as layout utility, sets `return_on_close`, and marks the response as the last segment. `layoutreturn` validates type and otherwise accepts returns without extra state. `layoutcommit` fetches current attributes, conditionally sets size when `last_write + 1` exceeds current size, conditionally sets mtime only if the client time is newer, calls `saunafs_setattr`, and marks commit done.

State is minimal. Layout identity is encoded through inode/export id; no per-layout allocation is stored in this file. Persistent effects happen only in `layoutcommit` through size and mtime setattr.

Dependencies include `pnfs_utils`, `context_wrap`, private SaunaFS types, XDR encoding, and Ganesha `op_ctx`. Integration point is `handleOperationsPnfs`, called during object ops initialization.

Risks include broad layouts with no range-specific tracking, no verification of returned layout body, no stateid-specific checks in these functions, and layoutcommit performing setattr even when mask remains zero. Test signals should cover unsupported layout types, encoded DS wire handle size/content, return-on-close behavior, size growth on layoutcommit, mtime conflict rules, no-op layoutcommit, getattr/setattr failure mapping, and pNFS client interoperability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/mds_handle.c -->
