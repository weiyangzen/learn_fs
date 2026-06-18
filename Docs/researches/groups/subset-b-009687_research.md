# subset-b-009687 Research

Grouped source research for NFS-Ganesha Ceph and Gluster FSAL export, handle, pNFS, compatibility, and upcall files. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/export.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/export.c

## Purpose

`export.c` implements Ceph FSAL export-level operations: export teardown, path lookup, NFS filehandle digest conversion, host-handle lookup, dynamic filesystem information, ACL capability reporting, unexport preparation, and export operation-vector registration. The complete 534-line file was read for this report.

## Important APIs, Types, and Functions

Key functions are `release`, `lookup_path`, `wire_to_host`, `host_to_key`, `create_handle`, `get_fs_dynamic_info`, `fs_acl_support`, `ceph_prepare_unexport`, `get_fsal_obj_hdl`, `fs_supported_attrs`, and `export_ops_init`. It works primarily with `struct ceph_export`, `struct ceph_mount`, `struct ceph_handle`, `struct ceph_host_handle`, `struct ceph_handle_key`, `struct ceph_statx`, `struct gsh_buffdesc`, and Ganesha `export_ops`.

## Control Flow

Export release deconstructs the root handle, detaches the export, removes it from the shared `ceph_mount` export list, decrements the mount refcount under `cmount_lock`, and shuts down/removes the shared libcephfs mount when the last export releases it. Path lookup normalizes `host:/path` forms, verifies the requested path starts under `CTX_FULLPATH(op_ctx)`, strips the shared mount prefix, special-cases the export root, then calls `fsal_ceph_ll_walk` and `construct_handle`. Filehandle decode converts little-endian wire fields to host values; `host_to_key` adds the current export id back into the cache key. `create_handle` validates the host handle length, reconstructs a `vinodeno_t`, finds the Ceph inode, fetches enough statx data, and constructs the FSAL handle.

## State and Persistence Behavior

This file manages no disk persistence directly, but it is responsible for shared mount lifetime and inode-cache identity. `release` is the main persistence-adjacent path because `ceph_shutdown` ends the libcephfs client session, and `ceph_prepare_unexport` calls `ceph_sync_fs` before unexport. Filehandle state is stable across NFS clients through the packed inode, snap, fscid tuple plus Ganesha's export id handling.

## Dependencies and Integration Points

Dependencies include libcephfs low-level calls through `statx_compat.h`, Ganesha FSAL export APIs, `cmount_lock`/AVL mount registry from `internal.c`, op-context export path data, NFS core shutdown/grace state, LTTng tracepoints, and optional POSIX ACL support. It integrates with `main.c` export creation, `internal.c` handle construction, and `handle.c` object operations.

## Risks and Edge Cases

Path prefix validation depends on string layout after `cmount_path` trimming; mismatches can return server fault rather than a clearer stale/cross-export error. `host_to_key` depends on `op_ctx->ctx_export`, so callers must have a valid export context. Legacy little-endian filehandle compatibility must not regress. `release` assumes `op_ctx->fsal_export` matches the handle being deconstructed through `deconstruct_handle`. Shutdown behavior differs when `USE_FSAL_CEPH_ABORT_CONN` is compiled.

## Test Signals

Useful tests include exporting both `/` and subdirectories with and without `cmount_path`, NFSv3/NFSv4 filehandle round trips across restart, stale inode lookup, multiple exports sharing a `ceph_mount` with different refcounts, unexport during admin shutdown/grace, statfs reporting with subvolume quotas, ACL-disabled exports masking `ATTR_ACL`, and LTTng/debug trace smoke checks for handle creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/handle.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/handle.c

## Purpose

`handle.c` is the main Ceph FSAL object-operation implementation. It maps Ganesha `fsal_obj_ops` to libcephfs operations for lookup, readdir, create, mkdir, mknod, symlink, readlink, getattr, link, rename, unlink, open/create, read/write, commit, locks, delegations, setattr, close, filehandle encoding, fallocate, and NFSv4 xattrs. The complete 3469-line file was read for this report.

## Important APIs, Types, and Functions

Important entry points include `ceph_fsal_release`, `ceph_fsal_lookup`, `ceph_fsal_readdir`, `ceph_fsal_mkdir`, `ceph_fsal_mknode`, `ceph_fsal_symlink`, `ceph_fsal_readlink`, `ceph_fsal_getattrs`, `ceph_fsal_link`, `ceph_fsal_rename`, `ceph_fsal_unlink`, `ceph_open2_by_handle`, `ceph_fsal_open2`, `ceph_fsal_read2`, `ceph_fsal_write2`, `ceph_fsal_commit2`, `ceph_fsal_lock_op2`, `ceph_deleg_cb`, `ceph_fsal_lease_op2`, `ceph_fsal_setattr2`, `ceph_fsal_close2`, `ceph_fsal_handle_to_wire`, `ceph_fsal_fallocate`, xattr helpers, and `handle_ops_init`. Core private state is `struct ceph_handle`, `struct ceph_fd`, `struct ceph_state_fd`, `struct ceph_fsal_cb_info`, and `struct fsal_share`.

## Control Flow

Object creation and lookup paths call statx compatibility wrappers, construct Ceph handles, and optionally post-apply attributes through `setattr2`. `open2` has separate open-by-handle and open-by-name flows: non-create by-name performs lookup first, create-by-name calls `fsal_ceph_ll_create`, handles exclusive/unchecked semantics, constructs the handle, installs a global or state fd, and sets remaining attributes only when it knows it created the file. Read/write paths call `fsal_start_io`, perform synchronous `ceph_ll_read`/`ceph_ll_write` loops or optional nonblocking libcephfs I/O, complete I/O through FSAL fd helpers, update temporary share counters, and invoke the caller callback. Metadata operations translate FSAL masks to Ceph set/get masks and security-label xattrs. `handle_ops_init` installs all implemented operations over defaults.

## State and Persistence Behavior

The file owns per-object and per-state fd lifecycle through `fsal_fd`, fd LRU insertion/removal, `close_fsal_fd`, and libcephfs `Fh *` handles. Share-deny state is kept in `struct fsal_share` on the object and updated under `obj_lock`. Stateless I/O and truncate paths temporarily acquire share counters and release them after completion. Persistent effects are CephFS namespace changes, file data writes, fsync/commit, xattrs, security labels, POSIX ACL xattrs, delegation/lock state in libcephfs/MDS, and optional fallocate/punch-hole changes.

## Dependencies and Integration Points

Dependencies include libcephfs low-level APIs, `statx_compat.h`, Ganesha fd/share/state helpers, POSIX ACL conversion, security label export options, `nfs_core` shutdown state, Linux fallocate constants, optional nonblocking and zerocopy Ceph I/O, optional lock and delegation libcephfs APIs, and LTTng tracepoints. The file depends on `internal.c` for handle construction and attribute conversion and on `main.c` for module feature flags such as `CephFSM.async` and `CephFSM.zerocopy`.

## Risks and Edge Cases

The file is heavily compile-option dependent, so matrix builds are important. Create cleanup admits a rare unchecked-create race that can leave a partially created file after later errors. Some metadata updates temporarily use root credentials, especially security labels after restrictive creates. Async callbacks construct a lightweight op context and rely on the original request lifetime retaining export references until callback completion. `ceph_fsal_reopen2` temporarily overwrites `op_ctx->creds`. Lock range validation guards signed `flock.l_len` overflow, but conflicting-lock translation uses POSIX structures directly. Xattr names are forced into `user.*`, so namespace assumptions are protocol-visible.

## Test Signals

Strong signals include create/open verifier behavior, unchecked create fallback, share-deny conflicts, fd LRU counts after open/reopen/close, stateless and stateful read/write, async and zerocopy read/write callbacks, stable write and commit/fsync behavior, truncate with and without state, rename over non-empty directory mapping to `EEXIST`, security label get/set with permission edge cases, POSIX ACL round trips, lock test/set/unlock, delegation recall callback behavior, fallocate and punch-hole if compiled, and NFSv4 xattr list/get/set/remove errors for `ERANGE` and missing xattrs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/internal.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/internal.c

## Purpose

`internal.c` supplies Ceph FSAL shared helpers: object-handle construction/destruction, FSAL-to-Ceph attribute mask conversion, Ceph statx-to-FSAL attribute conversion, optional POSIX ACL xattr conversion, and the global AVL registry for shared `ceph_mount` objects. The complete 531-line file was read for this report.

## Important APIs, Types, and Functions

Important functions are `construct_handle`, `deconstruct_handle`, `attrmask2ceph_want`, `ceph2fsal_attributes`, `ceph_get_posix_acl`, `ceph_set_acl`, `ceph_get_acl`, `ceph_mount_key_cmpf`, `ceph_mount_init`, `ceph_mount_lookup`, `ceph_mount_insert`, and `ceph_mount_remove`. Global state is `struct avltree avl_cmount` and `pthread_rwlock_t cmount_lock`.

## Control Flow

`construct_handle` allocates a `ceph_handle`, copies inode/snap/fscid/export id into its key, stores the libcephfs inode pointer, initializes the public FSAL object handle, and initializes a global fd for regular files. `deconstruct_handle` verifies the export id from the op context, releases the Ceph inode with `ceph_ll_put`, destroys regular-file fd state, finalizes the FSAL handle, and frees memory. Attribute conversion helpers set FSAL valid masks only for statx fields present. ACL helpers read POSIX ACL xattrs, convert them to NFSv4 ACLs, and write FSAL ACLs back to POSIX xattr format.

## State and Persistence Behavior

The file creates and destroys in-memory object handles and owns the shared `ceph_mount` lookup tree state. It persists no files itself, but ACL helpers read and write persistent CephFS ACL xattrs. The AVL key compares filesystem name, mount path, user id, and secret key so exports can share or isolate libcephfs sessions.

## Dependencies and Integration Points

Dependencies include libcephfs inode lifetime APIs, Ganesha FSAL object initialization, POSIX mode/dev conversion, optional `libacl`/POSIX ACL conversion helpers, `nfs_exports.h` options, and the Ceph module/global op context. It is used by `main.c` during export root creation, `export.c` during filehandle reconstruction, and `handle.c` for every object returned to upper layers.

## Risks and Edge Cases

`deconstruct_handle` relies on the active `op_ctx->fsal_export` matching the object export id; calling it under the wrong context would release the inode through the wrong mount. ACL conversion can allocate zero ACEs or produce malformed ACLs if xattr data is corrupt. `ceph_mount_key_cmpf` treats `NULL` and non-`NULL` keys distinctly and asserts `cm_mount_path`, so create paths must always populate mount path before AVL operations. Attribute conversion marks sec-label support off when export options disable it, so tests need both option states.

## Test Signals

Useful tests include handle lifecycle with regular and non-regular files, inode ref release under duplicate handle merge/release, attribute masks with partial statx data, creation/change time propagation, ACL get/set on files and directories, corrupt or missing ACL xattrs, mount sharing across identical keys, mount separation across user/secret/filesystem/path changes, AVL insert/remove order, and wrong-export release assertions in debug builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/internal.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/internal.h

## Purpose

`internal.h` is the private Ceph FSAL contract shared by module, export, handle, pNFS, and compatibility code. It defines module state, shared mount state, export state, object handles, fd/state wrappers, pNFS DS wire structures, supported/settable attribute masks, error conversion, and internal prototypes. The complete 286-line file was read for this report.

## Important APIs, Types, and Functions

Key types are `struct ceph_fsal_module`, `struct ceph_mount`, `struct ceph_export`, `struct ceph_fd`, `struct ceph_state_fd`, `struct ceph_join_deleg_arg`, `struct ceph_host_handle`, `struct ceph_handle_key`, `struct ceph_handle`, and under `CEPH_PNFS`, `struct ds_wire` and `struct ds`. It declares `construct_handle`, `deconstruct_handle`, `attrmask2ceph_want`, `ceph2fsal_attributes`, `export_ops_init`, `handle_ops_init`, pNFS ops initializers, `ceph_alloc_state`, ACL helpers, mount AVL helpers, and delegation helpers.

## Control Flow

This header has no executable flow beyond the inline `ceph2fsal_error` converter. It establishes how implementation files exchange ownership: module code creates `ceph_export` and shared `ceph_mount`, export code resolves paths and filehandles, handle code operates on `ceph_handle`, and internal code initializes/finalizes those structures.

## State and Persistence Behavior

The definitions describe all long-lived Ceph FSAL state. `ceph_fsal_module` stores global configuration flags (`client_oc`, `async`, `zerocopy`, reclaim/service registration options). `ceph_mount` is shared by exports and owns the libcephfs mount, refcount, mount key, delegation flags, and current upcall export. `ceph_export` owns export config and root handle. `ceph_handle` owns the libcephfs inode pointer, global fd, cache key, share state, and optional pNFS counters. Persistent identity is represented by packed inode/snap/fscid fields plus export id in the handle key.

## Dependencies and Integration Points

It includes libcephfs, FSAL public/private headers, UUID support, statx compatibility, commonlib, and AVL tree support. All Ceph FSAL implementation files depend on this header, and compile-time features (`CEPH_PNFS`, `CEPHFS_POSIX_ACL`, `USE_FSAL_CEPH_LL_DELEGATION`) alter the exposed state and prototypes.

## Risks and Edge Cases

Packed filehandle structs are wire/cache ABI and must not change casually. Secrets are present in `ceph_mount` keys and must be freed correctly and not logged. The pNFS declarations in this header do not align cleanly with some references in `mds.c` in the inspected tree, which is a compile-risk when `CEPH_PNFS` is enabled. The inline error converter assumes Ceph errors are negative POSIX values.

## Test Signals

Test signals are compile coverage across feature macros, structure-size and filehandle round-trip checks, static assertions or ABI checks for packed handle fields, mount refcount transitions, pNFS builds, ACL-enabled and ACL-disabled builds, async/zerocopy configuration, and leak checks for user id, secret key, mount path, and root handles during export teardown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/main.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/main.c

## Purpose

`main.c` implements Ceph FSAL module registration, module/export configuration parsing, shared libcephfs mount creation/reuse, root handle initialization, delegation/reclaim support, libcephfs cache callbacks, optional Ceph service registration, and module teardown. The complete 1150-line file was read for this report.

## Important APIs, Types, and Functions

Important items include global `CephFSM`, `ceph_conf_commit`, `init_config`, `find_cephfs_root`, `ceph_export_commit`, export config tables, `enable_delegations`, `handle_deleg_transition`, `create_unique_id`, `reclaim_reset`, `node_takeover_reclaim`, `select_filesystem`, callback functions `ino_release_cb`, `ino_invalidate_cb`, `dentry_invalidate_cb`, `umask_cb`, `register_callbacks`, `create_export`, `ceph_register_nfs_service`, `MODULE_INIT init`, and `MODULE_FINI finish`.

## Control Flow

Module init registers FSAL `Ceph`, initializes the mount AVL tree, installs module ops, and initializes object ops. Configuration parsing loads module flags and rejects incompatible `client_oc` plus `zerocopy`. Export creation parses FSAL block parameters, builds a mount key, reuses an existing `ceph_mount` or creates a new libcephfs client, reads Ceph config, sets key and client options, initializes/mounts/selects filesystem, registers callbacks, performs reclaim reset, finds the export root, constructs the root handle, attaches the export, and enables delegation timeout when configured. Error paths unwind in reverse under `cmount_lock`.

## State and Persistence Behavior

Global module state persists for the module lifetime. Shared `ceph_mount` objects persist while at least one export references the same filesystem/mount/user/secret key. Reclaim support creates stable Ceph client UUIDs from node id and either export id or a CityHash over node/user/filesystem/mount path, then starts/finishes reclaim with libcephfs. Callback registration connects Ceph MDS cache invalidation/release events to Ganesha upcall vectors.

## Dependencies and Integration Points

Dependencies include Ganesha FSAL registration, config parsing, export manager, NFS recovery/grace APIs, CityHash, libcephfs session/config/mount/callback/delegation/reclaim APIs, dynamic loader support for `libganesha_rados_urls.so`, and object/export ops from other Ceph FSAL files. It integrates with runtime export option changes through `handle_deleg_transition`.

## Risks and Edge Cases

Mount sharing is protected by `cmount_lock`, but create error handling manipulates export lists and refcounts before all fields are fully initialized. `select_filesystem` has a fallback branch that appears to reference `cm->fs_name` rather than `cm->cm_fs_name`, a likely compile issue when named-filesystem support is absent. Service registration exits the process if the RADOS URL library cannot be loaded while `register_service` is true. Delegation timeout must stay below Ceph MDS session timeout to avoid blacklist risk. Reclaim UUID changes can affect state recovery compatibility.

## Test Signals

Useful tests include module config parsing, incompatible flag rejection, export config validation for `cmount_path`, shared mount reuse and teardown, failed `ceph_create`/config/init/mount/select/reclaim paths, root lookup for mounted root and subdirectories, callback-driven invalidate/release upcalls, delegation option transitions at runtime, reclaim reset and node takeover across multiple mounts, service registration missing-library handling, and module unload after all exports release.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/mds.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/mds.c

## Purpose

`mds.c` implements Ceph FSAL pNFS metadata-server support under `CEPH_PNFS`: device info/list reporting, layout capability queries, layout grants, layout returns, and layout commits. The complete 698-line file was read for this report.

## Important APIs, Types, and Functions

Key functions are `initiate_recall`, `getdeviceinfo`, `getdevicelist`, `fs_layouttypes`, `fs_layout_blocksize`, `fs_maximum_segments`, `fs_loc_body_size`, `fs_da_addr_size`, `export_ops_pnfs`, `layoutget`, `layoutreturn`, `layoutcommit`, and `handle_ops_pnfs`. Important structures include `struct ceph_file_layout`, `struct pnfs_deviceid`, `struct ds_wire`, `struct pnfs_segment`, `struct fsal_layoutget_arg/res`, and `struct fsal_layoutcommit_arg/res`.

## Control Flow

`export_ops_pnfs` registers export pNFS methods. `getdeviceinfo` validates files layout type, derives the file layout from an inode encoded in the device id, emits a fixed 1024-stripe index array, then encodes one NFS multipath address per Ceph OSD. `layoutget` validates the requested layout type, fetches Ceph file layout, constrains or expands the segment for Linux client behavior, tracks issued read/write layout counters under object lock, builds a DS wire handle carrying the filehandle and Ceph layout, then XDR-encodes a file layout. `layoutreturn` decrements issued counters when disposing layouts. `layoutcommit` fetches old size/mtime, grows size if needed, selects a commit mtime, and writes attributes back.

## State and Persistence Behavior

The file tracks pNFS layout counters (`rd_issued`, `rw_issued`, serials, max length) in `struct ceph_handle` when pNFS is compiled. Device info is generated from live Ceph OSD and file-layout state rather than stored locally. Layout commit can persist size and mtime changes to CephFS. Layout return is mostly bookkeeping because the actual Ceph cap hold/return calls are disabled in `#if 0` blocks.

## Dependencies and Integration Points

Dependencies include libcephfs pNFS/layout helpers, Ganesha pNFS XDR helpers, IP utility multipath encoding, upcall layout recall vectors, and Ceph handle/export state from `internal.h`. It integrates with `export_ops_init` and `handle_ops_init` only when `CEPH_PNFS` is defined.

## Risks and Edge Cases

This file shows concrete bit-rot risk in the inspected tree: several references (`handle->vi`, `handle->wire`, pointer-style `stxnew->...`, direct `op_ctx->creds` argument where wrappers expect a pointer) do not match the current `internal.h`/compat wrapper shapes. These may be hidden by `CEPH_PNFS` being disabled, but should be treated as compile blockers when enabling pNFS. Layout range handling intentionally lies for whole-file Linux client requests. OSD address encoding assumes NFS port 2049 and one host per OSD. Counter decrement in write-layout paths appears to decrement `rd_issued` in places where `rw_issued` is expected.

## Test Signals

Minimum signals are a `CEPH_PNFS` build, layoutget/layoutreturn/layoutcommit integration tests, device info XDR decode tests with varied OSD counts and stripe units, bad layout type and out-of-range layout requests, whole-file Linux layout requests, layout counter balance under failures, DS wire-handle decode by the data-server side, and layoutcommit size/mtime monotonicity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/mds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/statx_compat.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/statx_compat.c

## Purpose

`statx_compat.c` provides fallback implementations for Ceph FSAL low-level wrappers when libcephfs does not expose the newer statx-style API (`USE_FSAL_CEPH_STATX` disabled). It converts POSIX `struct stat` results into the local `struct ceph_statx` compatibility shape. The complete 204-line file was read for this report.

## Important APIs, Types, and Functions

Key functions are `posix2ceph_statx`, `fsal_ceph_ll_walk`, `fsal_ceph_ll_getattr`, `fsal_ceph_ll_lookup`, `fsal_ceph_ll_mkdir`, optional `fsal_ceph_ll_mknod`, `fsal_ceph_ll_symlink`, `fsal_ceph_ll_create`, `fsal_ceph_ll_setattr`, and `fsal_ceph_readdirplus`.

## Control Flow

Each wrapper calls the older libcephfs low-level API with uid/gid credentials, receives POSIX stat data where applicable, and populates `ceph_statx`. `fsal_ceph_ll_setattr` converts the requested Ceph setattr mask back into a POSIX `struct stat`. `fsal_ceph_readdirplus` calls `ceph_readdirplus_r`; if `AT_NO_ATTR_SYNC` is absent it may issue a lookup to acquire an inode ref and refreshed attributes.

## State and Persistence Behavior

The file owns no persistent state. It affects persistent CephFS metadata only through `fsal_ceph_ll_setattr` and creation wrappers. Its main state behavior is compatibility preservation: callers elsewhere can use `ceph_statx` masks even when libcephfs only returned POSIX stat.

## Dependencies and Integration Points

Dependencies include older libcephfs APIs, POSIX stat/time fields, `timespec_to_nsecs`, and the declarations/macros in `statx_compat.h`. It is linked only for fallback builds and is used by export and handle code through uniform wrapper names.

## Risks and Edge Cases

Birth time is not populated from POSIX stat fallback but the mask claims basic stats plus version. `stx_version` is synthesized from ctime nanoseconds, which may not have the same semantics as true Ceph version/change attributes. The fallback credentials pass only caller uid/gid, not the full auxiliary group set available in newer `UserPerm` paths. Readdir behavior changes based on `AT_NO_ATTR_SYNC`, potentially causing extra lookups and inode references.

## Test Signals

Test signals include a build with `USE_FSAL_CEPH_STATX` disabled, lookup/getattr/create/mkdir/symlink parity with statx builds, setattr mask translation for size/mode/uid/gid/time, readdirplus inode reference handling, auxiliary-group permission differences, and NFS change attribute stability across metadata updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/statx_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/statx_compat.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/statx_compat.h

## Purpose

`statx_compat.h` defines the Ceph FSAL statx compatibility interface. With newer libcephfs it provides inline wrappers that create/destroy `UserPerm` and call statx-capable APIs; without it, it defines a local `struct ceph_statx`, statx/setattr masks, fallback prototypes, and inline wrappers for operations that do not need stat conversion. The complete 532-line file was read for this report.

## Important APIs, Types, and Functions

Important definitions are `CEPH_STATX_HANDLE_MASK`, `CEPH_STATX_ATTR_MASK`, `user_cred2ceph`, wrappers named `fsal_ceph_ll_*`, fallback `struct ceph_statx`, `CEPH_STATX_*` masks, `CEPH_SETATTR_*` masks from libcephfs context, and `AT_NO_ATTR_SYNC` fallback.

## Control Flow

In statx builds, each inline wrapper converts `struct user_cred` into a libcephfs `UserPerm`, calls the corresponding `ceph_ll_*` operation with full or handle-only stat masks, destroys the permission object, and returns the libcephfs status. In fallback builds, stat-returning operations are implemented in `statx_compat.c`, while simple operations such as readlink/open/opendir/link/unlink/rename/rmdir/xattr call older uid/gid libcephfs APIs directly.

## State and Persistence Behavior

The header stores no state, but it centralizes credential translation and determines whether auxiliary groups reach libcephfs. Persistent effects are delegated to callers through create, setattr, xattr, namespace, and I/O operations. The chosen stat mask controls which attributes upper layers consider valid.

## Dependencies and Integration Points

Dependencies include `fsal_types.h`, libcephfs types (`UserPerm`, `Inode`, `Fh`, `ceph_statx`), POSIX mode/dev/time types, and build-system feature detection. It is included by Ceph export, handle, internal, main, and fallback compatibility code.

## Risks and Edge Cases

Every wrapper allocates a `UserPerm`; allocation failure returns `-ENOMEM` and must be mapped by callers. Statx and fallback builds have subtly different permission semantics, attribute availability, and sync behavior. Wrapper signatures must stay synchronized with call sites; pNFS code in this tree appears out of sync for some `fsal_ceph_ll_getattr/setattr` uses. Since most wrappers are inline, compile coverage is the primary guard.

## Test Signals

Useful signals are dual builds with and without `USE_FSAL_CEPH_STATX`, full auxiliary-group permission tests, allocation-failure injection for `ceph_userperm_new`, stat mask coverage for handle-only and full-attribute lookups, xattr namespace operations, and compile tests for all feature combinations that include pNFS, ACL, mknod, and sync-inode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/statx_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/CMakeLists.txt

## Purpose

`CMakeLists.txt` defines the build target for the Gluster FSAL module. It sets GFAPI-related compile definitions, enumerates source files, creates the `fsalgluster` module library, links it to Ganesha and Gluster dependencies, assigns shared-object version properties, and installs it in the FSAL destination. The complete 60-line file was read for this report.

## Important APIs, Types, and Functions

Build-level items include `add_definitions(-D__USE_GNU ${GFAPI_CFLAGS})`, `fsalgluster_LIB_SRCS`, `add_library(fsalgluster MODULE ...)`, `add_sanitizers(fsalgluster)`, `target_link_libraries`, `set_target_properties`, and `install(TARGETS fsalgluster ...)`.

## Control Flow

CMake configures a module target from `main.c`, `export.c`, `handle.c`, `fsal_up.c`, `gluster_internal.h`, `gluster_internal.c`, `mds.c`, and `ds.c`. It links the target against `ganesha_nfsd`, system libraries, GFAPI libraries, LTTng libraries, and undefined-symbol rejection flags.

## State and Persistence Behavior

There is no runtime state. The file persists build/install contract: the output is a module named `fsalgluster` with version `4.2.0`, soversion `4`, installed under `${FSAL_DESTINATION}`.

## Dependencies and Integration Points

It integrates CMake feature detection variables (`GFAPI_CFLAGS`, `GFAPI_LIBRARIES`, `LTTNG_LIBRARIES`, `SYSTEM_LIBRARIES`, `LDFLAG_DISALLOW_UNDEF`, `FSAL_DESTINATION`) with the Gluster FSAL source set. Sanitizer integration is inherited through `add_sanitizers`.

## Risks and Edge Cases

The source list must stay synchronized with feature code; missing `mds.c`/`ds.c` would silently break pNFS support, while missing `fsal_up.c` would break upcalls. `-D__USE_GNU` can affect libc feature exposure globally for this target. `LIB_PREFIX` is set but not used locally. Link failures are a useful signal because `LDFLAG_DISALLOW_UNDEF` should catch missing GFAPI symbols.

## Test Signals

Test signals are a clean build with Gluster enabled, sanitizer builds, install packaging checks for `fsalgluster`, link checks with and without LTTng, GFAPI version compatibility builds, and pNFS/upcall symbol resolution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/ds.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/ds.c

## Purpose

`ds.c` implements Gluster FSAL pNFS data-server operations. It creates DS handles from client wire handles, supports direct anonymous GFAPI read/write by object handle, commits stable writes, releases DS handles, and registers DS operation vectors. The complete 298-line file was read for this report.

## Important APIs, Types, and Functions

Key functions are `dsh_release`, `ds_read`, `ds_write`, `ds_commit`, `make_ds_handle`, and `pnfs_ds_ops_init`. Important types include `struct glfs_ds_handle`, `struct glfs_ds_wire`, `struct glusterfs_export`, `struct fsal_pnfs_ds`, `struct fsal_ds_handle`, `stateid4`, and NFSv4 stability/verifier types.

## Control Flow

`make_ds_handle` validates the wire handle size, copies the GFAPI object handle, creates a `glfs_object` with `glfs_h_create_from_handle`, and returns a DS handle. `ds_read` uses `glfs_h_anonymous_read` against the MDS export's GFAPI context and sets EOF on short or zero read. `ds_write` zeroes the verifier, writes with `glfs_h_anonymous_write`, records stability, and invalidates the MDS-side cache via `up_process_event_object`. `ds_commit` opens the object and calls `glfs_fsync` when the last write was `FILE_SYNC4`, then closes the temporary fd.

## State and Persistence Behavior

The DS handle stores the GFAPI object handle, a lazy connection flag, and last write stability. Persistent effects are direct Gluster file data writes and fsyncs. Because writes bypass normal MDS object flow, the file explicitly triggers cache invalidation so Ganesha metadata does not remain stale.

## Dependencies and Integration Points

Dependencies include GFAPI handle/anonymous I/O functions, Ganesha pNFS DS default ops, Gluster export state, `op_ctx->ctx_pnfs_ds`, FSAL credential macros for commit open, and Gluster upcall invalidation. It is wired into the module through `pnfs_ds_ops_init`.

## Risks and Edge Cases

Stateid validation is not performed locally. `ds_write` returns the requested stability as achieved and only records it for later commit; error handling around partial writes depends on GFAPI return values. `ds_commit` only fsyncs when `stability_got == FILE_SYNC4`, which is unusual because unstable writes are typically the ones needing later commit. The wire handle validation is size-based and assumes the handle layout matches `struct glfs_ds_wire`. Temporary open/close failure handling can collapse into `NFS4ERR_INVAL`.

## Test Signals

Test signals include DS handle decode with valid and invalid sizes, read EOF and partial reads, write partial/error behavior, cache invalidation after DS writes, stable/unstable commit behavior, fsync error handling, GFAPI handle close on release, and pNFS integration with MDS export ids.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/export.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/export.c

## Purpose

`export.c` implements Gluster FSAL export operations and export creation. It maps NFS export paths to Gluster volume paths, creates FSAL handles from GFAPI handles, reports dynamic filesystem stats, allocates per-state fd containers, manages shared `glusterfs_fs` volume objects, configures GFAPI/upcalls, and enables pNFS MDS/DS support. The complete 832-line file was read for this report.

## Important APIs, Types, and Functions

Important functions are `export_release`, `lookup_path`, `wire_to_host`, `create_handle`, `glfs2fsal_handle`, `get_dynamic_info`, `gluster_free_state`, `glusterfs_alloc_state`, `fs_supported_attrs`, `get_fsal_obj_hdl`, `export_ops_init`, `glusterfs_free_fs`, `glusterfs_get_fs`, and `glusterfs_create_export`. Important config/state types are `struct glexport_params`, `enum transport`, `struct glusterfs_export`, and `struct glusterfs_fs`.

## Control Flow

Export release detaches the export, frees ops, decrements the shared Gluster volume object, and frees export strings. `lookup_path` translates the NFS mount path into a Gluster volume-relative path, looks up a GFAPI object, extracts its handle and volume UUID, and constructs a Ganesha FSAL handle. `create_handle` reverses a wire handle by extracting the GFAPI object handle from the second half of the digest. `glusterfs_get_fs` reuses an existing volume object by volume name or creates a new GFAPI context, sets volfile server/logging, initializes it, and registers or starts upcall handling. `glusterfs_create_export` parses config, initializes export ops, attaches the export, stores path/credential state, and enables pNFS DS/MDS registration when supported.

## State and Persistence Behavior

Shared volume state is kept in `GlusterFS.fs_obj` under `GlusterFS.glfs_lock` with a refcount and `destroy_mode`. Runtime export state stores mount path, volume export path, saved uid/gid, security-label xattr, and pNFS flags. Persistent effects are only indirect through GFAPI; this file primarily manages client connection lifetime, upcall registration, and pNFS DS registry entries.

## Dependencies and Integration Points

Dependencies include GFAPI (`glfs_new`, `glfs_set_volfile_server`, `glfs_set_logging`, `glfs_init`, `glfs_h_*`, `glfs_statvfs`, upcall register/unregister), Ganesha config parsing, FSAL export/state APIs, Gluster internal handle construction, pNFS utilities, export manager, LTTng tracepoints, and optional old polling-thread upcalls. It integrates with `fsal_up.c`, `ds.c`, and Gluster MDS pNFS code.

## Risks and Edge Cases

Volume reuse keys only on volume name, not hostname, transport, volpath, or log path, so two exports with the same volume name but different connection parameters may unexpectedly share a GFAPI context. `lookup_path` string translation has symlink and prefix TODOs and must handle root export path specially. Error cleanup in `glusterfs_get_fs` calls `glist_del` on a freshly initialized object in an error path, which should be reviewed. Upcall thread/register cleanup must avoid races with destroy mode and export release. pNFS DS insertion can fail on server id collision after export attach.

## Test Signals

Useful tests include multiple exports of one volume, conflicting same-volume config, path lookup for root and subdirectory exports, wire handle length validation, statvfs mapping, export release with active upcall thread, upcall register/unregister failures, GFAPI init failure cleanup, pNFS DS server-id collision, pNFS MDS/DS enabled and disabled exports, ACL support mask behavior, and leak/race tests around shared `glusterfs_fs` refcounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/fsal_up.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/fsal_up.c

## Purpose

`fsal_up.c` implements Gluster FSAL upcall processing. It translates GFAPI inode invalidation and optional lease recall events into Ganesha FSAL up-vector calls, either through an older polling thread or through the newer GFAPI upcall registration callback. The complete 368-line file was read for this report.

## Important APIs, Types, and Functions

Key functions are `up_process_event_object`, `GLUSTERFSAL_UP_Thread`, and `gluster_process_upcall`. Important types include `struct glusterfs_fs`, `struct glfs_upcall`, `struct glfs_upcall_inode`, optional `struct glfs_upcall_lease`, `struct glfs_object`, `struct fsal_up_vector`, and `struct gsh_buffdesc`.

## Control Flow

`up_process_event_object` extracts a GFAPI object handle, prepends the volume UUID to build the FSAL cache key, and dispatches based on the event reason. Inode invalidation calls `invalidate_close` with `FSAL_UP_INVALIDATE_CACHE`; optional lease recall calls `delegrecall`. `GLUSTERFSAL_UP_Thread` registers as an RCU thread, waits for upcall readiness, polls `glfs_h_poll_upcall`, handles retryable `ENOMEM`, decodes inode invalidate or lease recall payloads, processes object/parent/old-parent objects, frees callbacks, and exits when `destroy_mode` is set. `gluster_process_upcall` performs the same decode/dispatch for registered callback mode and frees the callback before returning.

## State and Persistence Behavior

The file owns no persistent data. It observes `gl_fs->destroy_mode`, `up_poll_usec`, GFAPI context, and up-vector readiness. Its runtime effect is cache and delegation state invalidation in Ganesha, keeping MDCACHE and client delegation state coherent with backend Gluster changes.

## Dependencies and Integration Points

Dependencies include GFAPI upcall APIs, Gluster internal state, FSAL up-vector interfaces, SAL functions, Userspace RCU thread registration, logging, and optional Gluster delegation support. It is started/registered by `export.c` when upcalls are enabled and is also called directly by `ds.c` after DS writes.

## Risks and Edge Cases

Event enum naming differs between poll and callback APIs (`GLFS_UPCALL_*` versus `GLFS_EVENT_*`), so dispatch mappings must match the compiled GFAPI version. The polling loop aborts on persistent `ENOMEM`, treats `ENOTSUP` as event-level exit, and can leak responsiveness if callbacks are repeatedly null. Parent and old-parent invalidations are best-effort and errors other than no-entry are logged. Callback mode waits for upcall readiness inside the callback, so readiness ordering matters.

## Test Signals

Test signals include synthetic inode invalidation for object, parent, and old parent handles; optional lease recall; missing/null event args; GFAPI handle extraction and volume-id failures; polling-thread shutdown through `destroy_mode`; `ENOMEM` retry behavior; `ENOTSUP` handling; callback-mode cleanup; direct invalidation after pNFS DS write; and MDCACHE invalidation observed by subsequent NFS LOOKUP/GETATTR.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/fsal_up.c -->
