# subset-b-009698 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_xattrs.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_xattrs.c

## Purpose

This file implements the MDCACHE stackable FSAL extended-attribute operation vector. Every function is a thin pass-through from an MDCACHE object handle to the wrapped lower FSAL object handle. It covers both the older FSAL xattr API using `fsal_xattrent_t`/integer xattr IDs and the NFSv4.2-style named xattr operations using `xattrkey4`, `xattrvalue4`, `setxattr_option4`, cookies, and `xattrlist4`.

## Important APIs, Types, and Functions

- `struct mdcache_fsal_obj_handle`: recovered with `container_of(obj_hdl, ..., obj_handle)` and used to reach `handle->sub_handle`.
- `subcall(...)`: wraps lower-FSAL calls, preserving the MDCACHE stack's usual tracing/error behavior.
- Legacy xattr wrappers: `mdcache_list_ext_attrs`, `mdcache_getextattr_id_by_name`, `mdcache_getextattr_value_by_id`, `mdcache_getextattr_value_by_name`, `mdcache_setextattr_value`, `mdcache_setextattr_value_by_id`, `mdcache_remove_extattr_by_id`, and `mdcache_remove_extattr_by_name`.
- NFSv4 xattr wrappers: `mdcache_getxattrs`, `mdcache_setxattrs`, `mdcache_removexattrs`, and `mdcache_listxattrs`.

## Control Flow

Each function extracts the MDCACHE wrapper, invokes the corresponding `handle->sub_handle->obj_ops` method with the same arguments, stores the returned `fsal_status_t`, and returns it unchanged. There is no local validation, translation, name filtering, caching, cookie manipulation, or attribute invalidation visible in this file.

## State and Persistence Behavior

The file maintains no local persistent state. Extended attributes are stored and listed by the lower FSAL. MDCACHE object identity is only used to find the lower handle, so correctness depends on the wrapper handle lifetime and lower handle lifetime being synchronized elsewhere in MDCACHE.

## Dependencies and Integration Points

This file depends on FSAL public types, `mdcache_int.h`, and the lower FSAL's `obj_ops` implementation. It integrates with MDCACHE handle operation initialization elsewhere, where these functions are assigned into the MDCACHE object ops vector. The NFS protocol layer will observe whatever semantics the lower FSAL exposes, including support for NFSv4.2 xattrs.

## Risks and Edge Cases

- Since there is no local cache invalidation, any metadata cache consistency after xattr mutation must be handled by the lower FSAL, `subcall`, or surrounding MDCACHE code.
- The pass-through assumes `sub_handle` and each xattr method pointer are valid. Missing optional lower-FSAL xattr methods must be guarded before this layer or by default ops.
- The legacy ID-based xattr API is lower-FSAL-defined; MDCACHE does not stabilize IDs across calls.
- Return buffer sizing and cookie semantics are entirely delegated.

## Test Signals

Useful coverage includes xattr list/get/set/remove through an MDCACHE export backed by an xattr-capable FSAL, unsupported xattr operations backed by a lower FSAL without support, small-buffer `ERR_FSAL_TOOSMALL` behavior, list cookie continuation, and cache coherency checks where a set/remove is followed by get/list through the same MDCACHE object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_xattrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/CMakeLists.txt

## Purpose

This CMake file builds the NULL stackable FSAL as the `fsalnull` module. NULLFS is a pass-through stackable FSAL used to layer on top of another FSAL while preserving a separate module boundary and operation vector.

## Important APIs, Types, and Functions

- `add_definitions(-D__USE_GNU)`: enables GNU extensions for this module build.
- `fsalnull_LIB_SRCS`: includes `handle.c`, `file.c`, `xattrs.c`, `nullfs_methods.h`, `main.c`, and `export.c`.
- `add_library(fsalnull MODULE ...)`: builds a loadable FSAL module rather than a static/shared library consumed normally by linkers.
- `add_sanitizers(fsalnull)`: ties the module into the repository sanitizer configuration.
- `target_link_libraries(fsalnull ganesha_nfsd ${LDFLAG_DISALLOW_UNDEF})`: links against core Ganesha and rejects unresolved symbols when configured.
- Optional LTTng dependency generation is wired under `USE_LTTNG`.

## Control Flow

At configure time, the file defines compile options, source membership, optional trace-generation dependency, link libraries, module version properties, and install destination. It does not contain runtime control flow.

## State and Persistence Behavior

The only persistent artifact is the generated module library and its installation into `${FSAL_DESTINATION}` as component `fsal`. Version metadata is set to `4.2.0` with `SOVERSION 4`.

## Dependencies and Integration Points

The module expects symbols from `ganesha_nfsd`, the FSAL module loader, and the generated LTTng trace headers when tracing is enabled. The source list corresponds to the NULLFS operation implementations and must remain synchronized with function declarations in `nullfs_methods.h`.

## Risks and Edge Cases

- Omitting a new NULLFS source file from `fsalnull_LIB_SRCS` will produce missing behavior or unresolved symbols.
- `${LDFLAG_DISALLOW_UNDEF}` is useful for catching missing symbols early but can expose platform/linker-specific incompatibilities.
- The hardcoded module version should be updated only in line with project release conventions.

## Test Signals

Build tests should confirm `fsalnull` compiles with and without `USE_LTTNG`, links without undefined symbols, and installs to the expected FSAL module directory. Runtime smoke tests should verify the module can be loaded by name `NULL`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/export.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/export.c

## Purpose

This file implements NULLFS export-level operations and export creation/update. NULLFS is stackable: it owns a top export and delegates nearly every export operation to `export.sub_export` after temporarily switching `op_ctx->fsal_export` to the lower export.

## Important APIs, Types, and Functions

- `struct nullfs_fsal_export`: private wrapper around `struct fsal_export`.
- `release`: releases the lower export, drops the lower FSAL reference, detaches this export from the NULL FSAL, poisons ops, and frees the wrapper.
- Export capability pass-throughs: `get_dynamic_info`, `fs_supports`, `fs_maxfilesize`, `fs_maxread`, `fs_maxwrite`, `fs_maxlink`, `fs_maxnamelen`, `fs_maxpathlen`, `fs_acl_support`, `fs_supported_attrs`, `fs_umask`, `fs_expiretimeparent`, and `fs_readdir_mode`.
- Quota and state hooks: `get_quota`, `set_quota`, `nullfs_alloc_state`, and `nullfs_is_superuser`.
- Handle serialization hooks: `wire_to_host` and `nullfs_host_to_key`.
- Lifecycle hook: `nullfs_prepare_unexport`.
- `nullfs_export_ops_init`: installs all supported export operations.
- Configuration schema: `sub_fsal_params`, `export_params`, and `export_param` parse the nested lower `FSAL { name = ... }` block.
- `nullfs_create_export` and `nullfs_update_export`: create/update the lower export and stack it under NULLFS.

## Control Flow

Most export methods follow one pattern: recover `nullfs_fsal_export`, set `op_ctx->fsal_export` to `exp->export.sub_export`, call the lower export method, restore `op_ctx->fsal_export` to the NULL export, and return the result. `nullfs_create_export` parses the configured lower FSAL name, looks up that module, calls the lower module's `create_export`, releases the lookup reference, stacks the lower export with the newly allocated NULL export via `fsal_export_stack`, initializes default export ops, overwrites with NULLFS ops, and sets `op_ctx->fsal_export` to the new export. `nullfs_update_export` first calls the generic `update_export` to check stack changes, reparses lower FSAL config, and delegates update to the lower FSAL with `original->sub_export`.

## State and Persistence Behavior

The wrapper export stores its lower export in `export.sub_export`; the lower export's `super_export` points back through `fsal_export_stack`. The file mutates the thread-local request context while delegating. No data is persisted by NULLFS itself; export lifetime is managed through FSAL references, export lists, and explicit release.

## Dependencies and Integration Points

This file integrates with the config parser (`load_config_from_node`, `CONF_RELAX_BLOCK`, `subfsal_commit`), FSAL module registry (`lookup_fsal`, `fsal_put`), export manager, and common FSAL stacking helpers. It relies on lower FSAL export operations being complete and on `op_ctx` being initialized by request/config code.

## Risks and Edge Cases

- Every temporary `op_ctx->fsal_export` switch must be restored on all paths. The current simple wrappers restore after direct calls, but new error branches would need the same discipline.
- `release` assumes `sub_export` exists and has a valid release op.
- `nullfs_create_export` allocates `myself` before calling lower `create_export`; it frees on lower error, but lower create side effects remain lower-FSAL responsibility.
- Capability methods return lower-FSAL values, so NULLFS's static module info is less authoritative than export ops.
- `nullfs_alloc_state` uses `op_ctx->fsal_export = exp_hdl` for restore while most wrappers restore `&exp->export`; those are expected equivalent but worth preserving carefully.

## Test Signals

Tests should load a NULLFS export stacked over a real FSAL, verify capability queries reflect the lower FSAL, run reload/update with unchanged and changed lower config, exercise quota calls where supported, and unexport while checking for lower export release and no stale `op_ctx` after failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/file.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/file.c

## Purpose

This file implements NULLFS file I/O object operations. It delegates close, open, read, write, seek, advise, commit, lock, close-state, and fallocate calls to the lower FSAL handle while preserving the stackable export context.

## Important APIs, Types, and Functions

- `struct null_async_arg`: records the NULLFS object, upper callback, and upper callback argument while an async lower-FSAL read/write is outstanding.
- `null_async_cb`: restores the upper export for the callback, invokes the original callback with the NULLFS object handle, restores the lower/current export, and frees the wrapper argument.
- `nullfs_close`: delegates old-style close.
- Multi-FD operations: `nullfs_open2`, `nullfs_check_verifier`, `nullfs_status2`, `nullfs_reopen2`, `nullfs_read2`, `nullfs_write2`, `nullfs_seek2`, `nullfs_io_advise2`, `nullfs_commit2`, `nullfs_lock_op2`, `nullfs_close2`, and `nullfs_fallocate`.

## Control Flow

Synchronous operations recover `nullfs_fsal_obj_handle` and `nullfs_fsal_export`, switch `op_ctx->fsal_export` to the lower export, call the lower handle's matching op, restore the NULL export, and return. `nullfs_open2` additionally wraps a returned lower `sub_handle` into a NULLFS handle with `nullfs_alloc_and_check_handle`. Async `read2` and `write2` allocate `null_async_arg`, call the lower FSAL with `null_async_cb`, and rely on the callback to translate the lower callback back into the upper NULLFS object context.

## State and Persistence Behavior

The file does not own persistent file data. It transiently allocates async callback wrappers and creates wrapper object handles when open-create returns a new lower object. State objects and file descriptors are lower-FSAL/SAL-owned and passed through unchanged.

## Dependencies and Integration Points

The code depends on `nullfs_methods.h` object/export wrappers, FSAL common multi-FD interfaces, access-check definitions, and lower FSAL `obj_ops`. It is installed into the NULLFS handle ops vector by `nullfs_handle_ops_init` in `handle.c`.

## Risks and Edge Cases

- Async callback correctness depends on `save_exp->super_export` being the right upper export when the lower callback fires.
- `nullfs_read2` and `nullfs_write2` allocate callback state unconditionally and do not handle allocation failure.
- If the lower FSAL completes async operations synchronously, `op_ctx` transitions still need to remain valid through `null_async_cb`.
- `nullfs_open2` only wraps when `sub_handle` is non-NULL. A lower FSAL that returns a handle with an error status would still be passed into `nullfs_alloc_and_check_handle`; that helper currently wraps only if status is success.

## Test Signals

Coverage should include read/write callback object identity, open-create returning a new object, reopen and close-state sequencing, fallocate pass-through, lock conflicts, and failure cases from lower FSAL methods. Async tests should confirm callback argument memory is freed and upper callbacks see the NULLFS handle, not the lower handle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/handle.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/handle.c

## Purpose

This file implements NULLFS object-handle wrapping and most non-I/O object operations. It turns lower-FSAL handles into `nullfs_fsal_obj_handle` objects, delegates namespace and attribute operations to the lower handle, and translates readdir callbacks so upper layers see NULLFS handles.

## Important APIs, Types, and Functions

- `nullfs_alloc_handle`: allocates a wrapper handle, initializes the public FSAL handle, copies type/fsid/fileid/fs/state state handle from the lower handle, assigns `NULLFS.handle_ops`, and sets `refcnt`.
- `nullfs_alloc_and_check_handle`: wraps a successful lower handle creation result.
- Namespace operations: `lookup`, `makedir`, `makenode`, `makesymlink`, `readsymlink`, `linkfile`, `renamefile`, and `file_unlink`.
- Directory operations: `nullfs_readdir_cb`, `read_dirents`, `compute_readdir_cookie`, and `dirent_cmp`.
- Attribute and wire-handle operations: `getattrs`, `nullfs_setattr2`, `handle_to_wire`, `handle_to_key`, `nullfs_lookup_path`, and `nullfs_create_handle`.
- Lifecycle and special handling: object `release` and `nullfs_is_referral`.
- `nullfs_handle_ops_init`: starts from `fsal_default_obj_ops_init` and installs NULLFS operation wrappers, including file and xattr operations declared elsewhere.

## Control Flow

Creation-style calls set `*new_obj` or `*handle` to NULL, switch to the lower export, call the lower operation, restore NULLFS context, then wrap the returned lower handle on success. Non-creation calls delegate to lower ops and return the lower status. Readdir is special: the lower FSAL receives `nullfs_readdir_cb`, which wraps each lower dirent handle, restores upper NULLFS context for the original callback, then restores lower context before continuing lower readdir.

## State and Persistence Behavior

Each NULLFS handle owns a pointer to the lower `sub_handle` and participates in the FSAL module handle list through `fsal_obj_handle_init(..., true)`. Release delegates lower release, finalizes the wrapper handle, and frees the wrapper. Persistent filesystem data remains lower-FSAL-owned; NULLFS persists only wrapper identity and copied metadata fields.

## Dependencies and Integration Points

This file ties together `NULLFS.handle_ops`, `nullfs_fsal_export`, lower `obj_ops`, common FSAL handle initialization/finalization, NFSv4 ACL headers, and object type helpers. Export-level `lookup_path` and `create_handle` are referenced from `export.c`.

## Risks and Edge Cases

- `nullfs_alloc_and_check_handle` assumes allocation succeeds; `nullfs_alloc_handle` does not check `gsh_calloc` return before dereference.
- If a lower FSAL returns success with `sub_handle == NULL`, wrapper allocation would dereference NULL.
- Some functions cast `obj_hdl` directly to `struct nullfs_fsal_obj_handle *` rather than using `container_of`; this relies on `obj_handle` being the first field.
- Readdir callback returns `false` on wrapper allocation failure although the enum is `enum fsal_dir_result`; this depends on `false` mapping to the intended stop/continue value.
- Context switching around callbacks is subtle and must match the stack direction.

## Test Signals

Tests should cover lookup/create/mkdir/mknode/symlink/link/rename/unlink pass-through, handle serialization round trips, readdir handle wrapping and cookie compare behavior, release ordering, referral detection, and failure injection where lower operations return errors or NULL handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/main.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/main.c

## Purpose

This file defines the NULLFS module object, static filesystem capability defaults, module initialization, module unload, and minimal module configuration behavior.

## Important APIs, Types, and Functions

- `static const char myname[] = "NULL"`: module registration name and library naming anchor.
- Global `struct null_fsal_module NULLFS`: contains `struct fsal_module module` and the NULLFS object ops vector.
- Static `fs_info`: advertises broad capabilities such as large file size, symlink/link/lock support, named attributes, unique handles, ACL support, all attributes, max I/O size, and parent expiry behavior.
- `init_config`: logs filesystem info and supported attributes; no tunables are applied.
- `MODULE_INIT nullfs_init`: registers the FSAL, installs create/update/init module ops, and initializes handle ops.
- `MODULE_FINI nullfs_unload`: unregisters the FSAL.

## Control Flow

On module load, `nullfs_init` calls `register_fsal`, returns early on failure, assigns module operation callbacks, and initializes `NULLFS.handle_ops`. On configuration init, `init_config` only logs. On unload, `nullfs_unload` calls `unregister_fsal` and reports failure to stderr.

## State and Persistence Behavior

The global `NULLFS` module structure persists for the process lifetime while loaded. Runtime exports and handles are managed by other files; this file only seeds default module-level state and operation vectors.

## Dependencies and Integration Points

This file integrates with the FSAL module registry (`register_fsal`, `unregister_fsal`), common FSAL init headers, and methods declared in `nullfs_methods.h`. It uses `FSAL_ID_NO_PNFS`, so NULLFS does not advertise pNFS identity here.

## Risks and Edge Cases

- Static `fs_info` may overstate actual lower-FSAL capabilities; export operations in `export.c` delegate capability queries to the lower FSAL, which should be preferred at runtime.
- A registration failure only prints to stderr and leaves the module unregistered.
- No module tunables means any stack-specific behavior must live in export config.

## Test Signals

Tests should verify module load/unload, registry name `NULL`, exported module ops being non-NULL after initialization, and that `init_config` succeeds without configuration parameters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/nullfs_methods.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/nullfs_methods.h

## Purpose

This header defines NULLFS private module, export, handle, readdir state, and method prototypes. It is the internal contract shared by `main.c`, `export.c`, `handle.c`, `file.c`, and `xattrs.c`.

## Important APIs, Types, and Functions

- `struct null_fsal_module`: embeds `struct fsal_module` plus a reusable `struct fsal_obj_ops handle_ops`.
- `extern struct null_fsal_module NULLFS`: process-global module instance.
- `nullfs_create_export` and `nullfs_update_export`: module export lifecycle entry points.
- `struct nullfs_readdir_state`: carries the upper callback, NULLFS export, and caller directory state while the lower FSAL performs readdir.
- `struct nullfs_fsal_export`: wrapper containing `struct fsal_export`.
- Export handle functions: `nullfs_lookup_path`, `nullfs_create_handle`, and `nullfs_alloc_and_check_handle`.
- `struct nullfs_fsal_obj_handle`: wrapper containing public object handle, lower `sub_handle`, and signed debug-friendly `refcnt`.
- `nullfs_unopenable_type`: classifies sockets, character devices, and block devices as unopenable.
- File, multi-FD, lock, fallocate, and xattr prototypes used by operation-vector initialization.

## Control Flow

The header itself has no executable control flow except the inline `nullfs_unopenable_type`, which returns true for socket, character, or block object types. Its main role is compile-time linkage and type sharing between implementation files.

## State and Persistence Behavior

The types define the persistent runtime wrapper state: each export wraps a lower export, each object wraps a lower object handle, and readdir temporarily stores callback translation state. The header does not allocate or free state.

## Dependencies and Integration Points

It depends on FSAL core types being included before or through implementation files. It references `fsal_up_top`, config error types, FSAL object ops, NFS state, async callbacks, xattr entry types, and I/O hint structures.

## Risks and Edge Cases

- Any change to `struct nullfs_fsal_obj_handle` layout affects implementation code that casts from `struct fsal_obj_handle *`.
- `refcnt` is declared but not meaningfully manipulated in the reviewed implementation; future code should avoid assuming it is authoritative unless lifecycle is completed.
- The prototype set must stay synchronized with operation assignments in `nullfs_handle_ops_init`.

## Test Signals

Compile coverage is the main signal for this header. Runtime tests for every operation-vector assignment indirectly validate that prototypes, wrapper structure layout, and linkage remain consistent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/nullfs_methods.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/xattrs.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/xattrs.c

## Purpose

This file implements NULLFS legacy extended-attribute object operations. Like the rest of NULLFS, it delegates each xattr call to the lower FSAL after switching request context to the lower export.

## Important APIs, Types, and Functions

- `nullfs_list_ext_attrs`
- `nullfs_getextattr_id_by_name`
- `nullfs_getextattr_value_by_id`
- `nullfs_getextattr_value_by_name`
- `nullfs_setextattr_value`
- `nullfs_setextattr_value_by_id`
- `nullfs_remove_extattr_by_id`
- `nullfs_remove_extattr_by_name`
- `struct nullfs_fsal_obj_handle` and `struct nullfs_fsal_export` are recovered from public handles/context.

## Control Flow

Every function extracts the lower `sub_handle`, recovers the current NULLFS export from `op_ctx->fsal_export`, sets `op_ctx->fsal_export` to `export->export.sub_export`, calls the corresponding lower `obj_ops` function, restores the NULLFS export, and returns the lower status.

## State and Persistence Behavior

NULLFS stores no xattr data and does no xattr caching. All persistence, ID interpretation, permissions, and buffer-size behavior are delegated to the lower FSAL.

## Dependencies and Integration Points

The functions are installed into the NULLFS object ops vector in `handle.c`. The file depends on `os/xattr.h`, FSAL common types, and `nullfs_methods.h`. It only covers the older FSAL xattr API; NFSv4-style xattr methods are not implemented here for NULLFS.

## Risks and Edge Cases

- Optional xattr support must be reflected by lower FSAL ops/default ops; this layer does not check method availability.
- Context restoration must be maintained if additional error handling is added.
- ID-based xattr APIs can be unstable across lower FSAL implementations.

## Test Signals

Tests should run list/get/set/remove by name and ID through a NULLFS-stacked export, include unsupported lower-FSAL behavior, verify errors pass through unchanged, and confirm follow-up operations see lower-FSAL state changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/xattrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/access_check.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/access_check.c

## Purpose

This file provides common FSAL access checking for NFS-Ganesha objects. It evaluates NFSv4 ACLs or POSIX mode bits against `op_ctx->creds`, formats ACL/access data for logs, and manages process/thread credentials used by local-filesystem FSALs.

## Important APIs, Types, and Functions

- ACE matching helpers: `fsal_check_ace_owner`, `fsal_check_ace_group`, `fsal_check_ace_matches`, and `fsal_check_ace_applicable`.
- ACL/mask formatting: `fsal_ace_type`, `fsal_ace_perm`, `fsal_ace_flag`, `fsal_print_ace_int`, `fsal_print_acl_int`, `display_fsal_inherit_flags`, `display_fsal_ace`, and `display_fsal_v4mask`.
- Access evaluation: `fsal_check_access_acl`, `fsal_check_access_no_acl`, and public `fsal_test_access`.
- Credential switching: `fsal_set_credentials`, `fsal_restore_ganesha_credentials`, `fsal_set_credentials_only_one_user`, and `fsal_save_ganesha_credentials`.
- Global credential state: `ganesha_uid`, `ganesha_gid`, `ganesha_ngroups`, and `ganesha_groups`.

## Control Flow

`fsal_test_access` determines whether ACL data is needed from the requested access flags, fetches required attributes with `getattrs`, optionally grants owner skip, then chooses ACL evaluation if ACLs are required or available for a v4 mask; otherwise it falls back to POSIX mode-bit evaluation. ACL evaluation handles root specially, grants owner read/write ACL and attr privileges, walks ACEs in order, applies only matching and object-applicable allow/deny ACEs, tracks remaining requested access, and returns either success, access denied, permission denied, or no matching ACE. Mode evaluation selects owner, group, alternate group, or other bits, handles root execute semantics, and computes allowed/denied masks.

## State and Persistence Behavior

The access checks themselves are stateless aside from logs and temporary attr allocation/release. Credential helpers persist the server's original uid/gid/group list in globals and can mutate thread credentials on platforms with `GSH_CAN_HOST_LOCAL_FS`.

## Dependencies and Integration Points

This file relies on `op_ctx`, `op_ctx->fsal_export->exp_ops.is_superuser`, FSAL attr and ACL structures, NFSv4 ACL macros, display/logging utilities, and OS credential helpers from `os/subr.h`. It is the default object `test_access` implementation used by FSALs unless overridden.

## Risks and Edge Cases

- ACL behavior differs under `ENABLE_RFC_ACL`; without it, some denied ACL administrative bits return `ERR_FSAL_PERM` rather than `ERR_FSAL_ACCESS`.
- Root is allowed all directory access and all file access except execute unless an execute bit/ACE path grants it.
- `fsal_ace_perm` uses a static buffer, so it is not reentrant across concurrent formatting in the same expression.
- Missing ACL with `FSAL_ACE4_REQ_FLAG` returns `ERR_FSAL_NO_ACE`, which callers such as delete/rename helpers interpret specially.
- Credential switching failures are fatal, so local FSALs must pass valid groups.

## Test Signals

High-value tests include owner/group/everyone ACE allow/deny ordering, inherit-only and file-vs-directory applicability, root file execute denial, owner implicit ACL/attr rights, `FSAL_ACE4_REQ_FLAG` no-ACL behavior, POSIX mode fallback for primary and supplementary groups, and credential save/restore on supported platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/access_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/common_pnfs.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/common_pnfs.c

## Purpose

This file provides common pNFS helpers for FSALs implementing metadata server or data server behavior. It focuses on XDR encoding of device IDs, network addresses, files layouts, flex file layouts, device address versions, and POSIX-to-NFSv4 error mapping.

## Important APIs, Types, and Functions

- Global `struct fsal_module *pnfs_fsal[FSAL_ID_COUNT]`: registry-like array for pNFS-capable FSALs.
- `xdr_fsal_deviceid`: encodes/decodes a 16-byte pNFS device ID as opaque bytes.
- `FSAL_encode_ipv4_netaddr`: encodes `netaddr4` protocol strings and universal IPv4 address strings for TCP, UDP, SCTP, and RDMA.
- `make_file_handle_ds`: creates a Ganesha DS-marked NFSv4 file handle from a lower FSAL opaque handle and server ID.
- `FSAL_encode_file_layout`: encodes `nfsv4_1_file_layout4` location body pieces and DS file handles.
- `FSAL_encode_v4_multipath`: encodes a multipath list of network endpoints.
- `FSAL_encode_data_server` and `FSAL_encode_flex_file_layout`: encode flex file data server and layout structures.
- `FSAL_encode_ff_device_versions4`: encodes flex file device address version and connection details.
- `posix2nfs4_error`: maps selected `errno` values to NFSv4 status values.

## Control Flow

The encoding helpers are linear XDR writers. Each writes one field or counted array at a time, logs a major/critical message on encoding failure or invalid input, and returns an NFSv4 status immediately. File handle helpers build temporary `nfs_fh4` buffers, mark them as DS handles, and encode them as byte arrays. Flex file layout encoding nests mirror and stripe loops and reuses `FSAL_encode_data_server`.

## State and Persistence Behavior

The helpers do not persist state beyond the global `pnfs_fsal` array. Encoded layouts persist only in the caller-provided XDR stream. Temporary file handle buffers are stack-local.

## Dependencies and Integration Points

The file depends on ONC RPC XDR functions, NFSv4 generated XDR routines, Ganesha file-handle layout (`file_handle_v4_t`), pNFS utility types, export/file-handle headers, and logging. FSALs call these helpers while servicing `LAYOUTGET`, `GETDEVICEINFO`, or flex-file layout operations.

## Risks and Edge Cases

- `FSAL_encode_ipv4_netaddr` only supports IPv4-style universal addresses and a fixed set of protocol numbers.
- `make_file_handle_ds` must fit lower opaque handles into `NFS4_FHSIZE`; oversize handles return server fault.
- Several XDR calls cast away constness; callers must pass stable values.
- `FSAL_encode_flex_file_layout` overwrites `nfs_status` in nested loops and returns the last status, relying on helpers to return immediately for most failures.
- `posix2nfs4_error` defaults unknown errors to `NFS4ERR_SERVERFAULT`.

## Test Signals

Tests should decode encoded netaddr strings for supported protocols, reject invalid protocols, verify DS file handle flags/server IDs/endian flags, exercise same-FH and per-stripe FH layout encoding, cover flex file mirrors/stripes, force oversize handle failure, and validate errno-to-NFSv4 status mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/common_pnfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/commonlib.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/commonlib.c

## Purpose

This large shared FSAL utility file implements common export/handle initialization, FSAL diagnostics, fsid encoding, ACL inheritance and mode conversion, remove/rename access helpers, share reservation accounting, file descriptor LRU and multi-FD synchronization, verifier helpers, referral detection, FSAL backend registration with the NFS service, and request operation-context lifecycle management.

## Important APIs, Types, and Functions

- Export/handle helpers: `fsal_attach_export`, `fsal_detach_export`, `fsal_export_init`, `fsal_export_stack`, `free_export_ops`, `fsal_default_obj_ops_init`, `fsal_obj_handle_init`, and `fsal_obj_handle_fini`.
- pNFS DS helpers: `fsal_pnfs_ds_init` and `fsal_pnfs_ds_fini`.
- Diagnostics/conversion: `msg_fsal_err`, `fsal_dir_result_str`, `display_fsinfo`, `display_attrlist`, `log_attrlist`, `encode_fsid`, and `decode_fsid`.
- ACL helpers: `fsal_inherit_acls`, `fsal_remove_access`, `fsal_rename_access`, `fsal_mode_to_acl`, `fsal_acl_to_mode`, and supporting static ACE generation/reuse helpers.
- Share helpers: `update_share_counters`, `check_share_conflict`, and `merge_share`.
- FD LRU globals and functions: `fsal_fd_mutex`, `fsal_fd_cond`, `fsal_fd_global_lru`, `fd_lru_state`, `lru_try_one`, `fd_lru_run`, `bump_fd_lru`, `insert_fd_lru`, `remove_fd_lru`, `fsal_init_fds_limit`, `fd_lru_pkginit`, and `fd_lru_pkgshutdown`.
- Multi-FD synchronization: `close_fsal_fd`, `reopen_fsal_fd`, `wait_to_start_io`, `fsal_start_global_io`, `fsal_start_io`, `fsal_complete_io`, `fsal_start_fd_work`, and `fsal_complete_fd_work`.
- Verifier/referral helpers: `set_common_verifier`, `check_verifier_stat`, `check_verifier_attrlist`, and `fsal_common_is_referral`.
- NFS service registration: `unregister_nfs_service_with_fsal_backend`, `fsal_registration_try_register`, and `register_nfs_service_with_fsal_backend`.
- Operation context: `init_ctx_refstr`, `destroy_ctx_refstr`, `set_op_context_export`, `set_op_context_client`, `set_op_context_pnfs_ds`, save/restore/discard helpers, `init_op_context`, `release_op_context`, `suspend_op_context`, and `resume_op_context`.
- Optional DBus summary: `fd_usage_summarize_dbus`.

## Control Flow

The early section provides direct initialization and list-management helpers. ACL functions either copy and transform inherited ACEs, synthesize ACLs from POSIX mode bits, derive POSIX mode from ACL order, or perform delete/rename access checks through object `test_access`. Share functions update counters and detect conflicts between access and deny modes.

The FD subsystem starts a fridge thread in `fd_lru_pkginit`. `fd_lru_run` waits for server initialization, monitors open FD counters against low/high/hard watermarks, reclaims global FDs from the LRU tail via `lru_try_one`, detects futility under high churn, and adjusts its next sleep interval based on FD count and open rate. I/O startup uses `wait_to_start_io` to coordinate `io_work`, `fd_work`, desired read/write flags, and reopen permissions. Reopen/close work waits for I/O quiescence, calls FSAL-specific reopen/close hooks, updates LRU membership/counters, and signals condition variables. `fsal_start_io` chooses state FD, related open-state/delegation FD, global FD, or temporary FD depending on state type, open flags, share reservations, and contention.

Operation-context functions manage thread-local `op_ctx`: initializing refs, switching exports/clients/pNFS DS contexts, saving/restoring nested export contexts, releasing refs, suspending async contexts, and resuming them.

## State and Persistence Behavior

Persistent process state includes FSAL registration lists protected by `fsal_registration_lock`, `nfs_service_ready`, global FD counters/LRU lists/state, LRU tuning parameters, the `no_export` refstr, and monotonic `op_id`. Object/export helpers manipulate FSAL export and handle intrusive lists. FD state persists in `struct fsal_fd` counters, open flags, condition variables, LRU links, and export pointers. Operation contexts hold references to exports, pNFS DS objects, and refcounted path strings until explicitly cleared or released.

## Dependencies and Integration Points

This file is central to the FSAL layer. It depends on Ganesha list, logging, config, NFS init, MDCACHE, NFSv4 ACL, state, pNFS, atomic, resource-limit, and optional DBus utilities. FSAL implementations call these helpers to initialize handles/exports, enforce common access semantics, manage FDs, and interact with request context. SAL/NFS request dispatch owns `op_ctx` setup and uses the save/restore helpers when crossing export boundaries.

## Risks and Edge Cases

- FD synchronization is complex: missed `io_work`/`fd_work` transitions or condition signals can deadlock I/O, reopen, close, or LRU reclamation.
- `reopen_fsal_fd` contains explicit stale `fsal_export` repair before LRU insertion; regressions here can cause use-after-free or wrong-export accounting after export reload.
- Global FD hard-limit behavior returns delay/temporary FD paths; tests need high-FD-pressure scenarios.
- ACL conversion must preserve delete/delete-child and inherited ACE semantics while updating mode-generated ACEs.
- `fsal_remove_access` intentionally treats `ERR_FSAL_NO_ACE` differently from explicit denial; changing that can alter NFSv4 delete semantics.
- Operation-context ref management must balance `get_gsh_export_ref`, `put_gsh_export`, `gsh_refstr_get/put`, and `pnfs_ds_get_ref/put`; leaks or double releases affect long-running servers.
- `fd_lru_pkgshutdown` converts any shutdown `rc`, including success, through `posix2fsal_error`; success depends on that mapper handling zero correctly.

## Test Signals

High-value tests include export stack setup/teardown, object handle list insertion/removal, fsid encode/decode variants, ACL inheritance/mode round trips, remove/rename access with `DELETE`, `DELETE_CHILD`, and no-ACE cases, share conflict and merge scenarios, FD LRU low/high/hard watermark behavior, concurrent read/write versus reopen/close, fallback to temp FD, stale export pointer repair after export reload, verifier set/check round trips, referral detection on sticky directories, NFS service registration before and after readiness, and op-context save/restore/release leak checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/commonlib.c -->
