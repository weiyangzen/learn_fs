## subset-b-009699

Grouped research for FSAL core, local filesystem tracking, POSIX ACL conversion, and asynchronous FSAL upcalls in nfs-ganesha.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/default_methods.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/default_methods.c

### Purpose
`default_methods.c` defines the process-wide default method vectors for FSAL modules, exports, object handles, pNFS data servers, and pNFS data-server handles. These defaults provide ABI-compatible fallback behavior when older or simpler FSALs do not implement newer hooks: unsupported operations generally return `ERR_FSAL_NOTSUPP`, pNFS operations return NFSv4 errors, and capability accessors delegate to shared FSAL static configuration.

### Important APIs, Types, And Functions
The exported globals are `def_fsal_ops`, `def_export_ops`, `def_handle_ops`, and `def_pnfs_ds_ops`, declared privately in `fsal_private.h` and copied during FSAL registration. Module-level defaults include `unload_fsal`, `init_config`, `update_config`, `create_export`, `update_export`, `create_fsal_pnfs_ds`, `fsal_pnfs_ds_ops`, `fsal_extract_stats`, `fsal_reset_stats`, and NFS service registration hooks. Export-level defaults include capability getters such as `fs_supports`, `fs_maxfilesize`, `fs_acl_support`, `fs_supported_attrs`, quota stubs, pNFS layout capability stubs, `global_verifier`, and `alloc_state`. Object-level defaults include lookup/create/link/rename/unlink/xattr/layout/open/read/write/lock/setattr/close hooks, `handle_cmp`, `handle_to_key`, `check_verifier`, `compute_readdir_cookie`, and `is_referral`. pNFS data server defaults include `pds_release`, `pds_permissions`, `pds_handle`, `ds_read`, `ds_read_plus`, `ds_write`, and `ds_commit`.

### Control Flow
Registration code copies these vectors, after which each FSAL overrides the methods it supports. Callers route through module, export, or object operation tables. Unsupported defaults log through FSAL or PNFS components and return stable error codes. `unload_fsal` locks `fsal_lock`, refuses unload if references or exports remain, rejects statically linked modules, removes the FSAL from `fsal_list`, destroys the module rwlock, and `dlclose`s the shared object. `update_export` only validates stacking consistency between the original export and updated super-FSAL. `check_verifier` obtains atime and mtime through `getattrs` and compares them with the NFS exclusive-create verifier.

### State And Persistence
The file owns no persistent storage but manipulates FSAL process state through copied operation vectors. `unload_fsal` changes the global FSAL list and shared-object lifetime. `global_verifier` reads the global `NFS4_write_verifier`. pNFS DS defaults allocate and release `fsal_pnfs_ds` and `fsal_ds_handle` objects. `pds_permissions` mutates `op_ctx->export_perms` to root operation defaults for DS requests.

### Dependencies And Integration Points
It depends on `fsal.h`, `fsal_private.h`, `FSAL/fsal_config.h`, localfs and commonlib helpers, pNFS utilities, NFS core state, and credential context. `fsal_manager.c` consumes `def_fsal_ops` during `register_fsal`; FSAL implementations typically copy or override `def_export_ops` and `def_handle_ops` for export/object initialization. `fsal_helper.c` depends on object methods defaulted here when performing higher-level policy wrappers.

### Risks
The `unload_fsal` error path calls `PTHREAD_RWLOCK_unlock(&fsal_hdl->fsm_lock)` even though this function does not acquire that rwlock in the visible code, which is a shutdown risk if exercised. Silent no-op reference methods require an upper layer such as MDCACHE to override them; direct use without overrides can leak or mishandle handle lifetimes. Defaults that return success for `lookup_junction`, `check_quota`, `handle_merge`, or `io_advise` are deliberately permissive and can hide missing FSAL-specific semantics. `pds_handle` allocates a generic DS handle while logging unimplemented behavior, so incomplete pNFS DS support may progress farther than expected before failing reads/writes.

### Test Signals
Tests should verify that newly registered FSALs receive all default vector entries, unsupported object/export operations map to expected FSAL or NFSv4 errors, capability getters reflect `fsal_staticfsinfo_t`, exclusive create verifier comparison uses atime/mtime correctly, unload refuses busy or static FSALs, and partial pNFS DS defaults release all allocations on shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/default_methods.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_config.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_config.c

### Purpose
`fsal_config.c` provides small shared accessors over `struct fsal_staticfsinfo_t`. It centralizes how the rest of FSAL code asks whether an FSAL supports features and what configured static limits apply.

### Important APIs, Types, And Functions
The key API is `fsal_supports(struct fsal_staticfsinfo_t *info, fsal_fsinfo_options_t option)`, which maps every known `fso_*` option to fields such as `no_trunc`, `chown_restricted`, `lock_support`, `delegations`, `pnfs_mds`, `pnfs_ds`, `rename_changes_key`, `readdir_plus`, `xattr_support`, and `preserve_unlinked`. Scalar getters expose `maxfilesize`, `maxlink`, `maxnamelen`, `maxpathlen`, `acl_support`, `supported_attrs`, `maxread`, `maxwrite`, `umask`, `expire_time_parent`, and `readdir_mode`.

### Control Flow
The implementation is direct. `fsal_supports` switches on the requested option and returns a boolean derived from the corresponding field or bitmask. Unknown options return false. The scalar functions return fields without validation or clamping.

### State And Persistence
The file is read-only with respect to FSAL state. It does not allocate memory or persist data; callers own and initialize the `fsal_staticfsinfo_t` instance.

### Dependencies And Integration Points
It includes `fsal.h` and `FSAL/fsal_init.h`. `default_methods.c` export capability methods call these helpers through `exp_hdl->fsal->fs_info`. `fsal_helper.c` uses the export methods backed by these helpers to decide whether to permit time setting, link permission behavior, RDMA/zero-copy read buffer ownership, preserved unlink behavior, and other feature-gated flows.

### Risks
Because getters trust `info`, misinitialized FSAL static info propagates directly into protocol behavior. Unknown `fso_*` values fail closed, which is safe for compatibility but can make newly added capabilities appear unsupported until this switch is updated. There is no synchronization here; correctness depends on FSAL static info being immutable or externally protected after initialization.

### Test Signals
Tests should cover every `fso_*` mapping, delegation read/write bit extraction, unknown option false behavior, and that export operations in `default_methods.c` return the same values as these helpers for a populated `fsal_staticfsinfo_t`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_convert.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_convert.c

### Purpose
`fsal_convert.c` translates between POSIX/kernel filesystem concepts and nfs-ganesha FSAL abstractions: errno to `fsal_errors_t`, mode/test/open flags, object types, device IDs, and `stat` attributes.

### Important APIs, Types, And Functions
`posix2fsal_error` maps POSIX errors into FSAL major codes, logging notable IO, NXIO, memory, delay, and default server-fault cases. `fsal2posix_testperm` converts `FSAL_R_OK`, `FSAL_W_OK`, and `FSAL_X_OK` to `R_OK`, `W_OK`, and `X_OK`. `posix2fsal_type` maps `S_IF*` mode bits to `object_file_type_t`. `posix2fsal_fsid` and `posix2fsal_devt` split `dev_t` into major/minor structures. `fsal2posix_openflags` maps read/write/truncate FSAL open flags to POSIX `O_*` flags. `object_file_type_to_str` is a diagnostic helper. `posix2fsal_attributes_all` and `posix2fsal_attributes` fill `struct fsal_attrlist` from `struct stat`.

### Control Flow
Error conversion is a large switch with platform-specific cases for Linux and AIX. Attribute conversion checks `fsalattr->valid_mask` before writing each field, obtains the supported mask from `op_ctx->fsal_export->exp_ops.fs_supported_attrs`, computes `change` as the newer of mtime and ctime in nanoseconds, converts `st_blocks` to `spaceused`, and maps raw device numbers for special files.

### State And Persistence
The file has no persistent state. It reads global request context through `op_ctx` in `posix2fsal_attributes`, so conversion depends on a current FSAL export context. Outputs are caller-owned structs.

### Dependencies And Integration Points
It depends on POSIX headers, `fsal.h`, `fsal_convert.h`, and `common_utils.h`. VFS-like FSALs and local filesystem code use these helpers when translating syscalls into FSAL responses. `localfs.c` uses device conversion for filesystem indexing. `fsal_up_async.c` uses `posix2fsal_error` to convert `fridgethr_submit` failures.

### Risks
`posix2fsal_error` maps `EBADF` to `ERR_FSAL_NOT_OPENED`, with a comment noting this can be wrong for write-on-read-only-FD cases. Unknown errno values become `ERR_FSAL_SERVERFAULT`, so new platform errors can surface as severe faults. `fsal2posix_openflags` intentionally ignores some FSAL flags; callers must handle create/exclusive/share semantics elsewhere. Attribute conversion requires valid `op_ctx`; calling it outside an operation context can dereference invalid state.

### Test Signals
Tests should cover errno mappings including retry and unsupported cases, file type conversion for every `S_IF*`, open flag combinations, major/minor conversion, valid-mask driven attribute population, and `ATTR_CHANGE` selection between mtime and ctime.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_convert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_destroyer.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_destroyer.c

### Purpose
`fsal_destroyer.c` implements server shutdown and emergency cleanup for loaded FSALs. It walks the global FSAL registry, releases lingering handles, pNFS data servers, exports, module references, local filesystem tracking, context refstrings, and locks.

### Important APIs, Types, And Functions
`destroy_fsals` is the main orderly teardown entry point. `emergency_cleanup_fsals` calls each FSAL module's emergency cleanup hook. Internal helpers are `shutdown_handles`, `shutdown_pnfs_ds`, and `shutdown_export`.

### Control Flow
`destroy_fsals` iterates `fsal_list` with safe list traversal. For each FSAL it releases objects on `m->handles`, releases pNFS DS objects on `m->servers`, releases every export on `m->exports`, forcibly zeroes unexpected nonzero module refcounts, and invokes `m->m_ops.unload`. After all modules, it calls `release_posix_file_systems`, `destroy_ctx_refstr`, and `destroy_fsal_lock`. `shutdown_pnfs_ds` also zeroes unexpected DS refcounts before calling `ds_release`.

### State And Persistence
This file destroys process-global runtime state. It mutates FSAL refcounts, DS refcounts, export lists, handle lists, module list membership through unload callbacks, local filesystem registries, and FSAL locks. It does not persist state outside the process.

### Dependencies And Integration Points
It depends on `fsal_private.h` for `fsal_list` and lock lifecycle, `fsal_commonlib` and localfs cleanup for shared FSAL resources, and export/core headers for export references. It relies on method vectors initialized in `default_methods.c` and FSAL-specific overrides for actual release behavior.

### Risks
The destroy path intentionally masks refcount leaks by storing zero before unload; that helps shutdown complete but can hide use-after-free risks in stackable FSALs. Release callbacks must tolerate being called during global teardown and with lingering references. `destroy_fsals` does not visibly lock `fsal_lock` while iterating `fsal_list`, so shutdown assumes no concurrent module registration/unregistration. If a default or buggy release method is installed, lingering handles or DS objects may not release backend resources.

### Test Signals
Tests should simulate FSALs with exports, handles, DS objects, nonzero refcounts, static and dynamic unload behavior, and emergency cleanup hooks. Shutdown tests should assert release ordering, list drainage, local filesystem registry cleanup, and logging of leaked references.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_destroyer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_helper.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_helper.c

### Purpose
`fsal_helper.c` implements common high-level FSAL operations used by protocol layers and cache layers. It wraps low-level object methods with NFS/FSAL policy: credential checks, create ownership rules, setattr semantics, path walking, cross-junction readdir behavior, delegation conflict handling, synchronous I/O wrappers, RDMA read buffer handling, and xattr list encoding.

### Important APIs, Types, And Functions
Permission helpers include `fsal_not_in_group_list`, `check_open_permission`, `fsal_check_create_owner`, and `fsal_check_setattr_perms`. Main operation helpers include `open2_by_name`, `fsal_setattr`, `fsal_readlink`, `fsal_link`, `fsal_lookup`, `fsal_lookup_path`, `fsal_lookupp`, `fsal_create_set_verifier`, `fsal_create`, `fsal_create_verify`, `fsal_readdir`, `fsal_remove`, `fsal_rename`, `fsal_open2`, `fsal_reopen2`, `fsal_statfs`, `fsal_verify2`, `get_optional_attrs`, `get_buffer_for_io_response`, `fsal_read2`, `fsal_read`, `fsal_write`, `fsal_listxattr_helper`, and `fsal_close2`.

### Control Flow
Open-by-name validates the parent directory, rejects dot entries, checks lookup permission, calls the FSAL `open2` method, and if requested performs a post-open permission check with cleanup close on failure. `fsal_setattr` rejects bad truncates, checks delegations, verifies time-setting support, computes required ACL/mode permissions, applies Linux-like setuid/setgid clearing, and calls `setattr2`. Lookup and path walking enforce directory execute permissions, prohibit `..` in full paths, and hold/release object references while walking through MDCACHE. `fsal_create` normalizes owner/group attributes, dispatches by object type, closes regular files opened only for create, and handles `ERR_FSAL_EXIST` by lookup/type verification. Readdir checks list and attribute permissions, invokes object `readdir`, and `populate_dirent` handles cross-junction attributes by temporarily switching export context. Remove and rename protect junction/export roots, check delegation conflicts, close objects before unlink, optionally mark preserved unlinks with open states, and delegate to object operations. Synchronous read/write call async operations and wait on a condition variable, repeating while `fsal_resume` is set.

### State And Persistence
The helpers primarily mutate operation-local structs, but also rely heavily on `op_ctx` for credentials, export context, RDMA state, and unlink-with-states state. Reference counts on object handles and exports are acquired and released during lookup, readdir junction traversal, and close/error paths. The file does not persist data beyond the backend operations it invokes.

### Dependencies And Integration Points
It integrates protocol layers with FSAL object/export vectors from `default_methods.c` and FSAL implementations. It uses `nfs_exports`, `nfs4_acls`, SAL state/delegation functions, `fsal_convert`, RDMA request structures when enabled, and `nfs_param` runtime configuration. The helpers expect object methods to honor reference and callback contracts.

### Risks
Correctness is sensitive to reference balance on error paths, especially cross-junction readdir and path walking. Permission logic depends on accurate current attributes and ACL availability; missing ACLs intentionally deny some non-owner setattr paths. `fsal_create` temporarily modifies `attrs->valid_mask` and restores it, so early returns must preserve caller expectations. Synchronous I/O waits rely on callbacks always firing. `fsal_listxattr_helper` parses flat xattr buffers and has subtle cookie/length behavior; malformed non-NUL-terminated lists or size limits can expose edge bugs. RDMA buffer selection asserts that requested size fits `data_chunk_length`.

### Test Signals
Tests should cover non-root owner/group create and setattr cases, setuid/setgid clearing, exclusive-create verifier replay, lookup of dot/dotdot/root, path traversal with repeated slashes and `..`, cross-junction readdir success and stale-junction failure, remove/rename of junctions and delegated objects, preserved unlink state marking, RDMA and allocated read buffers, synchronous read/write resume, optional attrs with `ATTR_RDATTR_ERR`, and xattr cookie/maxbytes edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_manager.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_manager.c

### Purpose
`fsal_manager.c` owns FSAL module lifecycle: global registration state, loading static and dynamic FSALs, parsing FSAL config blocks, looking up modules, registering/unregistering modules, and initializing sub-FSALs.

### Important APIs, Types, And Functions
Global state includes `pthread_mutex_t fsal_lock`, `GLIST_HEAD(fsal_list)`, loader status variables `dl_error`, `so_error`, `new_fsal`, and `load_state`. Public functions include `initialize_fsal_lock`, `destroy_fsal_lock`, `load_fsal_static`, `start_fsals`, `load_fsal`, `lookup_fsal`, `register_fsal`, `unregister_fsal`, `fsal_init`, `fsal_load_init`, and `subfsal_commit`. Config integration is represented by `fsal_block`, `fsal_dummy_block`, `fsal_name_adder`, and the weak `start_custom_static_fsals`.

### Control Flow
Startup initializes locks and context refstrings, parses `FSAL_LIST`, transitions the loader to idle, and loads static `MDCACHE` and `PSEUDO` FSALs before optional custom static FSALs. Dynamic loading constructs `libfsal<name>.so`, lowercases the basename, stats it, enters `loading`, calls `dlopen`, then accepts registration from a constructor or falls back to `dlsym("fsal_init")`. Successful registration leaves the new module in `new_fsal`; `load_fsal` takes an initial reference, stores path and `dl_handle`, and returns the handle. `register_fsal` validates API versions, copies `def_fsal_ops`, initializes lists/locks, inserts into `fsal_list`, and optionally registers pNFS FSAL ID. `fsal_load_init` looks up or loads by name, calls `init_config` or `update_config`, marks `is_configured`, and registers NFS backend services.

### State And Persistence
The file manages process-global FSAL module state only. It protects the module list and loader state with `fsal_lock`, initializes `fs_lock` for local filesystem tracking when available, stores module path/name strings, shared-object handles, refcounts, and configuration status.

### Dependencies And Integration Points
It depends on `default_methods.c` through `def_fsal_ops`, config parsing, NFS core parameters for module location, pNFS utilities, localfs locking, FSAL commonlib registration, and static FSAL init functions from `fsal_private.h`. Export parsing and sub-FSAL configuration call `fsal_load_init`.

### Risks
The loader state machine is global, so concurrent or reentrant loads depend on strict `fsal_lock` discipline. `dl_error` sometimes points to `dlerror()` storage and sometimes duplicated storage, so ownership must remain consistent. `load_fsal` calls `LogFatal` on `dlopen` failure, making missing modules fatal in that path. Version checks allow older minor versions but reject newer minors. Registration copies only module ops; FSAL-specific export/object defaults must be handled elsewhere. Static loading requires `load_state == idle`, while constructors during process init use `init`, making startup ordering important.

### Test Signals
Tests should cover static FSAL load, dynamic constructor registration, manual `fsal_init` fallback, missing library/symbol failures, version mismatch, duplicate or invalid load states, case-insensitive lookup with refcount increment, init/update config paths, unregister with nonzero refcount, and pNFS FSAL ID table registration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_private.h -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_private.h

### Purpose
`fsal_private.h` is the private bridge among FSAL core implementation files. It exposes default operation vectors, the global FSAL registry lock/list, lock lifecycle functions, and statically linked FSAL initialization entry points.

### Important APIs, Types, And Functions
It declares `extern struct fsal_ops def_fsal_ops`, `extern struct export_ops def_export_ops`, `extern struct fsal_obj_ops def_handle_ops`, and `extern struct fsal_pnfs_ds_ops def_pnfs_ds_ops`. It declares `extern pthread_mutex_t fsal_lock`, `extern struct glist_head fsal_list`, `initialize_fsal_lock`, `destroy_fsal_lock`, `pseudo_fsal_init`, and `mdcache_fsal_init`.

### Control Flow
There is no executable control flow. Including files use these declarations to share process-global FSAL state and default method vectors without exposing them as public FSAL API.

### State And Persistence
The header declares process-global state owned by `fsal_manager.c` and default vectors owned by `default_methods.c`. It does not define or persist data itself.

### Dependencies And Integration Points
`fsal_manager.c` defines `fsal_lock` and `fsal_list`; `default_methods.c` defines the default vectors; `fsal_destroyer.c` walks `fsal_list` and destroys locks; static startup calls `mdcache_fsal_init` and `pseudo_fsal_init`.

### Risks
This header intentionally exposes mutable globals inside the FSAL implementation boundary. Any new internal user must obey locking rules for `fsal_list` and must not treat default vectors as immutable API contracts beyond their versioned FSAL ABI role. Adding vector declarations here must stay synchronized with `default_methods.c` and registration code.

### Test Signals
Build coverage is the main signal: all FSAL core objects must link against one definition of each extern. Lifecycle tests should indirectly validate that users of `fsal_lock`, `fsal_list`, and default vectors agree on initialization and destruction order.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/localfs.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/localfs.c

### Purpose
`localfs.c` tracks locally mounted POSIX filesystems for FSALs that can host local filesystems. It scans mount tables, computes stable FSIDs/devices, maintains lookup indexes, builds parent/child mount topology, resolves export roots, claims/unclaims filesystems for FSAL exports, and exposes a DBus cache view when enabled.

### Important APIs, Types, And Functions
Path and index helpers include `open_dir_by_path_walk`, `re_index_fs_fsid`, `re_index_fs_dev`, `change_fsid_type`, `lookup_fsid`, `lookup_dev`, and locked variants. Scan/build helpers include `populate_posix_file_systems`, `posix_get_fsid`, `posix_create_file_system`, optional `posix_create_fs_btrfs_subvols`, `posix_find_parent`, and `path_is_subset`. Export lifecycle APIs include `resolve_posix_filesystem`, `claim_posix_filesystems`, `release_posix_file_system`, `release_posix_file_systems`, `unclaim_child_map`, `unclaim_all_filesystem_maps`, `get_fs_first_export_ref`, `unclaim_all_export_maps`, `is_filesystem_exported`, and `str_claim_type`. DBus support includes `posix_showfs` and `dbus_cache_init`.

### Control Flow
`resolve_posix_filesystem` stats an export path with configured retry/delay, rescans mount state with `populate_posix_file_systems`, then claims the matching root filesystem. Scanning initializes AVL indexes once, releases unclaimed top-level filesystems, reads `MOUNTED`, filters unsupported or dangerous filesystem types, stats candidate mount points, creates filesystem records, and builds parent links. `posix_create_file_system` fills path/device/type, computes FSID from device, blkid UUID, statfs fsid, or export override, inserts into fsid and dev AVL indexes, links into the global list, and optionally discovers btrfs subvolumes. Claiming finds the root filesystem by device or configured FSID override, then `process_claim` recursively claims root/subtree/child filesystems while resolving conflicts with existing root, subtree, and child claims.

### State And Persistence
Global runtime state includes `fs_lock`, `posix_file_systems`, `fs_initialized`, `avl_fsid`, `avl_dev`, and optional blkid cache. Each `fsal_filesystem` stores path, device, type, fsid/dev keys, parent/children, export maps, claim counters, owning FSAL, unclaim callback, and private data. State is in-memory and rebuilt from mount tables; backend filesystems are persistent but not modified except through FSAL claim/unclaim callbacks.

### Dependencies And Integration Points
It depends on local FSAL headers, export state, idmapper DBus functions, POSIX mount/stat APIs, blkid/uuid when enabled, btrfsutil when enabled, `fsal_convert` for device mapping, and core parameters such as `fsid_device`, `fsid_override`, `resolve_fs_retries`, and `resolve_fs_delay`. FSAL implementations pass `claim_filesystem_cb` and `unclaim_filesystem_cb` to attach backend-specific data to filesystem records.

### Risks
Mount scanning must avoid hangs; NFS/autofs and pseudo filesystems are filtered before `stat`, but new problematic filesystem types may need additions. Claim conflict logic is complex and order-sensitive for overlapping exports; comments acknowledge spurious warnings depending on export ordering. FSID derivation can collide; duplicate handling updates device/type in some cases and drops duplicates in others. `change_fsid_type` compresses or truncates identifiers for alternate formats, creating collision risk. All registry mutations rely on `fs_lock`; callbacks invoked while locked must avoid deadlocks. `open_dir_by_path_walk` rejects `..` and uses `O_NOFOLLOW`, but path parsing edge cases need coverage.

### Test Signals
Tests should cover path walking with absolute/relative roots, symlinks, repeated slashes, and `..`; mount scan filtering; FSID derivation with device, statfs, blkid UUID, and override; duplicate fsid/dev insertion; parent-child topology; resolve retry behavior; root/subtree/child claim conflicts across same and different FSALs; unclaim recursion; lookup by fsid/dev under locks; btrfs subvolume discovery when enabled; and DBus `showfs` output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/localfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/posix_acls.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL/posix_acls.c

### Purpose
`posix_acls.c` converts between POSIX draft ACLs, FSAL/NFSv4 ACL representations, and Linux POSIX ACL xattr wire format. It implements the NFSv4-to-POSIX mapping strategy referenced by the file comments and preserves mask/deny semantics where possible.

### Important APIs, Types, And Functions
ACE classification helpers are `is_ace_valid_for_effective_acl_entry`, `is_ace_valid_for_inherited_acl_entry`, `isallow`, and `isdeny`. POSIX ACL entry helpers include `ace_count`, `find_entry`, and `get_entry`. Main conversion functions are `posix_acl_2_fsal_acl` and `fsal_acl_2_posix_acl`. Xattr helpers are `posix_acl_xattr_size`, `posix_acl_entries_count`, `xattr_2_posix_acl`, and `posix_acl_2_xattr`.

### Control Flow
POSIX-to-FSAL conversion first reads mask and other entries, then walks POSIX ACL entries and emits one or two FSAL ACEs per entry. It sets special IDs for owner/group/everyone/mask, group flags for group entries, inheritance flags for default ACLs, allow permissions from POSIX read/write/execute bits, mask-deny iflags when the POSIX mask suppresses permissions, and explicit deny ACEs when later entries or `other` allow permissions not granted to the current entry. FSAL-to-POSIX conversion builds separate allow and deny ACLs, precomputes `EVERYONE@` allow/deny effects, ensures required `USER_OBJ` and `GROUP_OBJ` entries, processes applicable effective or inherited ACEs, creates user/group/mask entries as needed, calculates a mask if needed, checks the resulting ACL, and returns the allow ACL. Xattr conversion validates header size/version/endian fields and serializes/deserializes tag, permission, and qualifier IDs.

### State And Persistence
The file allocates and frees POSIX ACL objects and temporary text/debug buffers. It does not maintain global state. Xattr conversion reads and writes caller-provided buffers using little-endian ACL structures suitable for persistent extended attributes.

### Dependencies And Integration Points
It depends on `posix_acls.h`, libacl APIs, FSAL ACE macros, endian helpers, and FSAL logging. VFS-style FSALs use it when exposing NFSv4 ACLs over POSIX ACL capable backends or translating stored POSIX ACL xattrs into FSAL ACL attributes.

### Risks
ACL mapping is inherently lossy between NFSv4 and POSIX models; deny ordering, inheritance, special IDs, and mask behavior can produce surprising results. `fsal_acl_2_posix_acl` has a FIXME about allocating maximum possible entries and possible leaks; some error paths return without freeing both ACLs. `get_entry` returns NULL on qualifier set failure without deleting the new entry. Xattr parsing must reject malformed sizes and unknown tags; otherwise ACLs could be misinterpreted. Macro-heavy conditions such as `if IS_FSAL_ACE_READ_DATA (*f_ace)` rely on unusual macro syntax and need compiler coverage.

### Test Signals
Tests should round-trip simple owner/group/other ACLs, named users/groups with masks, deny ACEs, inherited/default ACLs, directory write/delete-child behavior, `EVERYONE@` deny interactions, xattr size/count validation, endian serialization, malformed tags/version/size rejection, and debug string paths under `COMPONENT_FSAL`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/posix_acls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL_UP/fsal_up_async.c -->
## sources/user-network-fs/nfs-ganesha/src/FSAL_UP/fsal_up_async.c

### Purpose
`fsal_up_async.c` provides asynchronous wrappers for FSAL upcalls and related callback work. It copies request arguments into heap allocations, queues work on a `fridgethr`, invokes the synchronous upcall implementation in a worker context, calls optional completion callbacks, and releases references.

### Important APIs, Types, And Functions
Async FSAL upcall wrappers include `up_async_invalidate`, `up_async_update`, `up_async_lock_grant`, `up_async_lock_avail`, `up_async_layoutrecall`, `up_async_notify_device`, and `up_async_delegrecall`. Protocol/internal async helpers include `async_cbgetattr`, `async_delegrecall_per_state`, and `async_delegrecall`. Each wrapper has a corresponding queued function such as `queue_invalidate`, `queue_update`, `queue_lock_grant`, `queue_layoutrecall`, `queue_notify_device`, `queue_cbgetattr`, `queue_delegrecall_per_state`, `queue_delegrecall`, or `up_queue_delegrecall`.

### Control Flow
Each upcall wrapper allocates an args struct, copies scalar parameters and file/object handle bytes into flexible array storage where needed, submits to `fridgethr_submit`, frees the args on submit failure, and returns either an FSAL status converted from POSIX submit status or a raw int for internal helpers. Queue callbacks call through `vec->up_fsal_export->up_ops` for invalidate/update/lock/layout/delegation/device work, invoke optional callbacks with FSAL or state status, and free args. `async_cbgetattr`, `async_delegrecall_per_state`, and `async_delegrecall` take object/client/state/export references before queueing and release them in the queued function or submit-failure path.

### State And Persistence
The file maintains no global state. It transfers ownership of heap-allocated argument blocks to fridge worker callbacks and temporarily holds object, state, client ID, and export references to keep asynchronous work safe after the caller returns.

### Dependencies And Integration Points
It depends on NFS core structures, FSAL upcall vectors, SAL functions, pNFS utilities, `fridgethr_submit`, and error conversion from `fsal_convert.c`. It integrates backend FSAL upcalls with MDCACHE/SAL operations such as invalidation, attribute updates, lock notifications, layout recall/device notifications, callback getattr, and delegation recall.

### Risks
The file comments say every async call takes an export reference, but several vector-based wrappers only store `vec` and have an `XXX` comment about export refcounting for delegation recall; callers must ensure `vec` and its export remain alive until queued work runs. `up_async_update` shallow-copies `struct fsal_attrlist`, so embedded allocations such as ACLs or buffers must remain valid or be immutable until execution. Owner and cookie pointers for lock/layout operations are copied as pointers, not deep-copied. Queue failure paths are mostly balanced, but any newly added argument type must mirror reference cleanup exactly.

### Test Signals
Tests should cover successful queue execution and submit failure for each wrapper, callback invocation status, deep-copy behavior for handle buffers, object/client/state/export refcount balance, layout recall with and without `layoutrecall_spec`, notify-device parameter propagation, and lifetime safety when exports or states are concurrently released.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL_UP/fsal_up_async.c -->
