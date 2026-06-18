# Group Research: subset-b-009691

This grouped report covers the requested NFS-Ganesha FSAL_KVSFS, FSAL_LIZARDFS, and FSAL_MEM source files. Each section preserves the original source path in the title and is delimited for deterministic splitting into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_handle.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_handle.c

Purpose: Implements the KVSFS object-handle operations that adapt Ganesha's `fsal_obj_ops` surface to the KVSNS backing namespace API. It allocates private handles, performs lookup/path/root reconstruction, creates namespace objects, lists directories, mutates attributes, emits wire handles, and releases resources.

Important APIs and types: The central private type is `struct kvsfs_fsal_obj_handle`, declared in `kvsfs_methods.h`; this file fills it with a `struct kvsfs_file_handle`, Ganesha public `fsal_obj_handle`, optional symlink cache, file share counters, and an `fsal_fd`. Exposed helpers are `kvsfs_alloc_handle()`, `kvsfs_lookup_path()`, `kvsfs_create_handle()`, and `kvsfs_create2()`. Static object methods include `kvsfs_lookup`, `kvsfs_mkdir`, `kvsfs_makesymlink`, `kvsfs_readsymlink`, `kvsfs_linkfile`, `kvsfs_readdir`, `kvsfs_rename`, `kvsfs_getattrs`, `kvsfs_setattr2`, `kvsfs_unlink`, `kvsfs_handle_to_wire`, `kvsfs_handle_to_key`, `kvsfs_release`, and `kvsfs_merge`.

Control flow: `kvsfs_handle_ops_init()` starts from default object ops and installs KVSFS implementations plus open/read/write/commit functions defined elsewhere. Lookups build caller credentials from `op_ctx`, call `kvsns_lookup`, `kvsns_lookupp`, or `kvsns_get_root`, fetch `struct stat` through `kvsns_getattr`, and allocate Ganesha handles from the result. Creation paths call `kvsns_creat`, `kvsns_mkdir`, or `kvsns_symlink`, then fetch attributes and allocate the returned object. `kvsfs_readdir()` opens a KVSNS directory, pages `MAX_ENTRIES` dentries, looks up each returned name to create a child handle and attributes, and streams entries through the mdcache callback with synthetic cookies offset to account for dot entries.

State and persistence: Persistent namespace state lives outside this file in KVSNS. This layer stores only opaque inode handles, cached symlink content, file open/share state, and `fsal_fd` lifecycle state. Attribute changes are translated from FSAL masks to `STAT_*_SET` flags and delegated to `kvsns_setattr`. Wire handles copy the `struct kvsfs_file_handle` bytes, so file-handle ABI size and contents are compatibility-sensitive.

Dependencies and integration: The file depends on Ganesha FSAL commonlib, `fsal_convert`, `op_ctx`, `fsal_fd`/share helpers, pNFS optional `handle_ops_pnfs()`, and KVSNS calls such as `kvsns_getattr`, `kvsns_lookup`, `kvsns_readdir`, `kvsns_closedir`, `kvsns_link`, `kvsns_rename`, and `kvsns_unlink`. It integrates with export creation via `kvsfs_lookup_path()` and `kvsfs_create_handle()`.

Risks: `kvsfs_lookup()` allocates a handle from a zeroed file handle before assigning the returned inode, relying on later assignment for correctness. Error handling around directory open/read/close can skip `kvsns_closedir()` on some read errors. `kvsfs_getattrs()` checks `retval == ENOENT` even other code treats KVSNS errors as negative errno. Create helpers allocate handles that are not always returned to the caller, which should be audited against actual open/create call chains. Parent pre/post attributes are ignored throughout.

Test signals: Exercise root lookup, `"."` and `".."` lookup, stale wire-handle reconstruction, directory pagination and callback termination, create/mkdir/symlink/unlink/rename/link under non-root credentials, setattr masks for size/mode/owner/group/times, short handle output buffers, fd release paths, and pNFS-enabled handle allocation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_main.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_main.c

Purpose: Defines the KVSFS FSAL module object, static filesystem capabilities, module load/unload hooks, and module-level configuration initialization.

Important APIs and types: The global `struct kvsfs_fsal_module KVSFS` embeds `struct fsal_module` and the shared object operation vector. Its `fs_info` advertises large files, POSIX name/path limits, hard-link support, no symlink support in static info, named attributes, unique handles, supported attribute mask, max I/O size, and no lock support. `kvsfs_init_config()` is the module config callback. `kvsfs_load()` and `kvsfs_unload()` are the `MODULE_INIT` and `MODULE_FINI` entry points.

Control flow: On load, `kvsfs_load()` registers the FSAL under name `KVSFS` with `FSAL_ID_KVSFS`, installs module callbacks for export creation and config initialization, installs pNFS module callbacks (`kvsfs_pnfs_ds_ops_init`, `kvsfs_getdeviceinfo`, `kvsfs_fs_da_addr_size`), and initializes handle ops with `kvsfs_handle_ops_init()`. On unload, it unregisters the FSAL. `kvsfs_init_config()` currently logs static fsinfo and supported attributes without parsing tunables.

State and persistence: The only state is the global module object and its initialized ops vectors. Persistent filesystem state belongs to KVSNS and per-export objects created elsewhere.

Dependencies and integration: Includes Ganesha FSAL init/API headers, pNFS utilities, and KVSFS internal/method headers. The module depends on `kvsfs_create_export()` being provided by the export implementation and on pNFS helpers from KVSFS MDS/DS code.

Risks: Static capability flags are policy-sensitive; this file says `symlink_support = false` while handle code implements symlink creation/read, so client behavior may not match implementation. `named_attr = true` is marked with `XXX` while xattr functions are stubs. `lock_support = false` despite a lock-op prototype elsewhere should be verified. Failed registration only prints to stderr.

Test signals: Load/unload module under Ganesha, verify advertised FSAL capabilities through config dump and NFS client behavior, check pNFS callback registration when KVSFS pNFS is enabled, and confirm unsupported features are not advertised inconsistently.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_mds.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_mds.c

Purpose: Implements the KVSFS pNFS metadata-server side for NFSv4.1 FILE layouts: layout type discovery, device address encoding, layout grant, return, and commit hooks.

Important APIs and types: Public integration functions are `export_ops_pnfs()`, `handle_ops_pnfs()`, `kvsfs_getdeviceinfo()`, and `kvsfs_fs_da_addr_size()`. It uses `struct kvsfs_exp_pnfs_parameter` from `kvsfs_methods.h` for stripe unit, DS count, and fixed DS address array. Layout encoding uses Ganesha helpers `FSAL_encode_v4_multipath()` and `FSAL_encode_file_layout()`.

Control flow: Export pNFS ops advertise only `LAYOUT4_NFSV4_1_FILES`, a 4 MiB block size, one segment, and fixed loc-body/device-address sizes. `kvsfs_getdeviceinfo()` finds the first export on the module export list, reads its pNFS DS array, encodes stripe indices, encodes one multipath member per configured DS, and returns NFSv4 status. `kvsfs_layoutget()` validates layout type, copies the object's KVSFS file handle into a DS handle descriptor, grants a whole-file segment with `return_on_close`, builds device id `1`, and encodes the file layout. `layoutreturn` and `layoutcommit` validate layout type and otherwise mostly acknowledge.

State and persistence: pNFS DS topology is stored in the export's `pnfs_param`; layout grants do not create persistent reservations. The DS wire body embeds a KVSFS file handle. Layout commit currently does not persist size/time changes.

Dependencies and integration: Depends on Ganesha pNFS/XDR helpers, module export list, `op_ctx`, `struct pnfs_deviceid`, and KVSFS handle internals. It is registered from `kvsfs_main.c` and conditionally installed on object ops from `kvsfs_alloc_handle()` when the export is pNFS MDS-enabled.

Risks: `kvsfs_getdeviceinfo()` uses the first export in `fsal_hdl->exports` instead of matching `deviceid`, which is unsafe with multiple exports. `ipport` is stored separately from `sockaddr_in` and is converted with `ntohs()` despite being an `unsigned short`; config byte order must be verified. Layoutcommit is a stub and can hide DS-side size/time updates. The fixed device address buffer size is heuristic. Multiple DS handling is marked TODO in layoutget.

Test signals: Validate GETDEVICEINFO with zero, one, and four DS entries; multi-export pNFS configurations; client LAYOUTGET/RETURN/COMMIT; bad layout type handling; XDR buffer exhaustion; and DS address byte order on the wire.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_mds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_methods.h -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_methods.h

Purpose: Declares the KVSFS FSAL private structures and cross-file method prototypes used by module, export, handle, pNFS, xattr, locking, and I/O implementations.

Important APIs and types: Key structs include `kvsfs_fsal_module`, `kvsfs_fsal_export`, `kvsfs_exp_pnfs_parameter`, `kvsfs_pnfs_ds_parameter`, `kvsfs_fd`, `kvsfs_state_fd`, and `kvsfs_fsal_obj_handle`. It declares `kvsfs_handle_ops_init()`, export lookup/reconstruction helpers, `kvsfs_alloc_handle()`, all open/read/write/commit/close helpers, share/lock helpers, and extended attribute operations.

Control flow: This header is the contract that lets `kvsfs_main.c` initialize ops, `kvsfs_handle.c` allocate/reconstruct handles and dispatch operations, export code call path and wire-handle creation, and xattr/pNFS code register into the same object ops vector. It also defines `KVSFS_NB_DS` and pNFS export parameter layout used by MDS device encoding.

State and persistence: The header documents state ownership. `kvsfs_fsal_export` owns root inode, KVSNS config path, pNFS enable flags, and DS parameters. `kvsfs_fsal_obj_handle` owns an allocated variable-size `kvsfs_file_handle` pointer plus either file state or symlink content. `kvsfs_state_fd` embeds `state_t` first, matching Ganesha's default state-freeing convention.

Dependencies and integration: Depends on FSAL types, Ganesha list/fd/share/state primitives, KVSNS inode/open/credential types, and pNFS sockaddr definitions. It is included by most KVSFS implementation files.

Risks: The comment notes `kvsfs_pnfs_ds_parameter` needs refactoring because port is separate from `sockaddr_in`; byte order and config parsing errors are likely here. Fixed `KVSFS_NB_DS = 4` limits DS scaling. The object handle stores both opaque handle pointer and inode field in the file union, so duplication must stay coherent. Xattr and lock prototypes imply support that module static info may not advertise accurately.

Test signals: Compile all KVSFS variants with pNFS on/off, verify struct layout assumptions for state embedding and handle allocation, exercise wire-handle sizing, and check static capability flags against the operations declared here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_methods.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_xattrs.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_xattrs.c

Purpose: Provides the KVSFS extended-attribute operation symbols required by the object ops vector, but the implementation is effectively a placeholder.

Important APIs and types: The file defines local callback typedefs `xattr_getfunc_t` and `xattr_setfunc_t`, an unused `fsal_xattr_def_t`, a diagnostic `print_vfshandle()`, and all FSAL xattr entry points declared in `kvsfs_methods.h`: list, name-to-id, get by id/name, set by name/id, get xattr attrs, and remove by id/name.

Control flow: Every public xattr function returns `ERR_FSAL_NO_ERROR` immediately without filling output buffers, ids, counts, attributes, or end-of-list markers. `print_vfshandle()` writes the fixed text `(not yet implemented)` into a caller buffer, but is not connected to a xattr table.

State and persistence: No xattr state is read or written. No KVSNS xattr API is called. As a result, named attribute operations can appear successful while doing nothing.

Dependencies and integration: Includes Ganesha list/config/commonlib headers, `fsal_convert`, and `kvsfs_fsal_internal.h`. The functions are installed into object ops by `kvsfs_handle_ops_init()`, and `kvsfs_main.c` advertises `named_attr = true`.

Risks: Silent success is the main correctness risk. Clients may believe xattrs were set or removed when no persistence occurred. Output parameters can remain uninitialized, especially `p_nb_returned`, `end_of_list`, `pxattr_id`, `p_output_size`, and `p_attrs`. This conflicts with module capability advertisement and can cause protocol-visible corruption or client hangs.

Test signals: NFSv4 named attribute operations should verify list counts and EOF, set/get/remove round trips, small-buffer behavior, unknown names, and whether unsupported xattrs should return `ERR_FSAL_NOTSUPP` instead of success. Static fsinfo should be reconciled with real support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_xattrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/CMakeLists.txt -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/CMakeLists.txt

Purpose: Builds the LizardFS FSAL as a Ganesha loadable module.

Important APIs and types: The build target is `fsallizardfs`, a `MODULE` library with sources `context_wrap.c`, `ds.c`, `export.c`, `handle.c`, `lzfs_acl.c`, `lzfs_internal.c`, `main.c`, `mds_export.c`, and `mds_handle.c`, plus their headers. It applies `-D__USE_GNU` and `${LIZARDFS_CFLAGS}` and links `${SYSTEM_LIBRARIES}` and `${LIZARDFS_CLIENT_LIB}`.

Control flow: CMake collects the FSAL sources into `fsallizardfs`, applies sanitizer integration with `add_sanitizers(fsallizardfs)`, sets module version `3.12.0`/SOVERSION `3`, and installs it to `${FSAL_DESTINATION}` under component `fsal`.

State and persistence: No runtime state. The file controls which implementation units are compiled into the plugin and therefore which FSAL operations are available.

Dependencies and integration: Requires the LizardFS client library and headers to be available in the parent build. It relies on Ganesha's module loading convention and sanitizer helper macro.

Risks: Missing `LIZARDFS_CLIENT_LIB` or mismatched `LIZARDFS_CFLAGS` will fail link/compile. The target does not link `ganesha_nfsd` explicitly, unlike FSAL_MEM, so symbol resolution relies on module loading and parent link policy. Version/SOVERSION must remain consistent with deployment packaging expectations.

Test signals: Configure with and without LizardFS client development files, build with sanitizers enabled, inspect undefined symbols in the module, install packaging paths, and run a Ganesha startup smoke test loading `fsallizardfs`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/context_wrap.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/context_wrap.c

Purpose: Provides credential-aware wrapper functions around the LizardFS C API. Each wrapper creates a `liz_context_t` from Ganesha credentials, calls the underlying LizardFS operation, and normally destroys the context before returning.

Important APIs and types: Wrappers include lookup, mknod, open, read, write, flush, getattr, opendir/readdir, mkdir/rmdir/unlink, setattr, fsync, rename, symlink/readlink/link, chunk info, ACL get/set, and byte-range lock get/set. All accept `liz_t *instance` and `struct user_cred *cred` plus operation-specific LizardFS types.

Control flow: The standard pattern is `lzfs_fsal_create_context(instance, cred)`, return error/null if it fails, call `liz_*`, destroy context, and return the result. This centralizes credential translation for the rest of the FSAL and keeps handle/export code from managing LizardFS contexts directly.

State and persistence: The wrappers do not own persistent state. They create short-lived contexts and delegate all filesystem state to the LizardFS client instance. Calls with `cred == NULL` are used by pNFS DS paths to create root-like/local contexts via `lzfs_fsal_create_context()`.

Dependencies and integration: Depends on `context_wrap.h`, `lzfs_internal.h`, and the LizardFS C API. Used heavily by `handle.c`, `export.c`, `ds.c`, `mds_export.c`, `mds_handle.c`, and ACL conversion code.

Risks: `liz_cred_getlk()` creates a context but does not call `liz_destroy_context(ctx)` before returning, which leaks per-lock-test contexts. Because wrappers return `-1` or `NULL` without setting a LizardFS error when context creation fails, callers using `liz_last_err()` may report stale errors. Repetitive create/destroy can be expensive under high I/O and lock rates.

Test signals: Leak-test repeated lock tests, failure-inject context creation, validate credential mapping for normal users, anonymous users, and supplemental groups, and compare direct LizardFS error codes with FSAL error translation after wrapper failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/context_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/context_wrap.h -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/context_wrap.h

Purpose: Declares the credential-aware LizardFS wrapper API used by the LizardFS FSAL implementation.

Important APIs and types: The header includes `fsal_types.h` and `lizardfs/lizardfs_c_api.h`, then declares wrappers for namespace operations, file I/O, metadata, directories, setattr/fsync, links, chunk information, ACLs, and POSIX-style locks. Important data types are `liz_t`, `liz_inode_t`, `liz_entry`, `liz_fileinfo_t`, `liz_attr_reply`, `liz_chunk_info_t`, `liz_acl_t`, and `liz_lock_info_t`.

Control flow: This header forms the abstraction boundary between Ganesha FSAL code and raw LizardFS API calls requiring a user context. Implementation files call `liz_cred_*` functions rather than constructing contexts inline.

State and persistence: No state is declared here. The wrappers pass through pointers to LizardFS instance state, fileinfo objects, ACL objects, and result buffers owned by callers or the LizardFS library.

Dependencies and integration: Included by LizardFS export, handle, ACL, MDS, DS, and internal files. It couples the FSAL directly to the LizardFS C API ABI.

Risks: The header exposes raw LizardFS pointer lifetimes, so callers must know whether returned entries, fileinfo handles, ACLs, and chunk-info arrays need explicit release. Wrapper return conventions mix `int`, `ssize_t`, and pointer returns, which increases error-handling inconsistency. Any LizardFS C API signature change breaks multiple FSAL units.

Test signals: Compile against supported LizardFS library versions, run ABI/header compatibility checks, and exercise each wrapper through its FSAL caller with both success and error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/context_wrap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/ds.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/ds.c

Purpose: Implements LizardFS pNFS data-server handle operations: converting layout wire handles to DS handles, cached file opening, DS read/write/commit, and DS handle cleanup.

Important APIs and types: `struct lzfs_fsal_ds_wire` carries a 32-bit inode over the wire. `struct lzfs_fsal_ds_handle` stores the inode and optional `liz_fileinfo_cache` entry. Registered ops are `make_ds_handle`, `dsh_release`, `dsh_read`, `dsh_write`, `dsh_commit`, and `dsh_read_plus`.

Control flow: `lzfs_fsal_make_ds_handle()` validates descriptor size and inode, handles endian conversion, allocates a DS handle, and returns it. DS read/write/commit call `lzfs_int_openfile()`; that function reuses an existing cache entry, pops expired entries, acquires a cache entry by inode, opens the file with `O_RDWR` using null credentials if needed, and attaches the fileinfo. Read and write call `liz_cred_read()`/`liz_cred_write()`. Commit and stable writes flush through `liz_cred_flush()`. Release returns the cache entry and opportunistically clears expired cache entries.

State and persistence: DS state is the per-export `fileinfo_cache` plus per-DS-handle cache entry references. Persistent file data is in LizardFS. `writeverf` is zeroed on commit; write operation does not fill verifier in the shown path.

Dependencies and integration: Depends on `op_ctx->ctx_pnfs_ds->mds_fsal_export`, `pnfs_utils`, LizardFS wrappers, and fileinfo cache APIs. Export creation in `main.c` creates the fileinfo cache when pNFS DS support is enabled.

Risks: `lzfs_fsal_ds_handle_commit()` returns `NFS4_OK` if opening the file fails, which may mask real commit failures. DS open always uses `O_RDWR` and null credentials, so authorization model depends on pNFS/MDS layout validation rather than DS operation credentials. Cache eviction and release must match LizardFS fileinfo lifetimes. `read_plus` is unimplemented. Stable write returns `UNSTABLE4` on flush failure but still returns `NFS4_OK`.

Test signals: pNFS DS read/write/commit with cached and expired fileinfo entries, invalid/big-endian DS handles, stable write flush failures, cache saturation, concurrent DS handles for one inode, and client behavior when READ_PLUS is requested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/export.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/export.c

Purpose: Implements LizardFS FSAL export operations: export release, path lookup, wire-handle conversion, handle reconstruction, dynamic filesystem info, static capability accessors, state allocation, and fd-to-object lookup.

Important APIs and types: Core methods are `lzfs_fsal_release`, `lzfs_fsal_lookup_path`, `lzfs_fsal_wire_to_host`, `lzfs_fsal_create_handle`, `lzfs_fsal_get_fs_dynamic_info`, `lzfs_fsal_fs_supports`, `lzfs_fsal_alloc_state`, `lzfs_free_state`, `get_fsal_obj_hdl`, and `lzfs_fsal_export_ops_init()`. State allocation uses `struct lzfs_fsal_state_fd`.

Control flow: `lzfs_fsal_release()` deletes the root handle, detaches the export, drains and destroys the pNFS fileinfo cache, destroys the LizardFS client instance, frees the configured subfolder, and frees the export. `lookup_path()` validates and strips the Ganesha export full path, special-cases root, then uses `liz_cred_lookup()` from `SPECIAL_INODE_ROOT` to fetch attributes and allocate a handle. Wire conversion swaps a `liz_inode_t` in place based on endianness flags. Handle reconstruction validates inode descriptor size, gets attrs by inode, and allocates a handle.

State and persistence: Export state owns the mounted `liz_t` instance, root handle, pNFS fileinfo cache, LizardFS init parameters, and pNFS feature flags. Per-open NFS state owns an `lzfs_fsal_fd` initialized with `FSAL_FD_STATE`.

Dependencies and integration: Uses Ganesha FSAL config/commonlib, `fsal_convert`, `context_wrap`, `lzfs_internal`, and LizardFS statfs/getattr APIs. `lzfs_fsal_export_ops_init()` is called during export creation in `main.c`.

Risks: `lookup_path()` returns the shared root handle for root without taking an obvious extra reference in this function; correctness depends on Ganesha calling conventions. Path prefix validation uses `strstr(real_path, CTX_FULLPATH(op_ctx)) == real_path`, which can be sensitive to normalized slashes and path aliases. `wire_to_host()` mutates the caller buffer before length validation. Cleanup must avoid releasing cached fileinfo after the LizardFS instance is destroyed; current ordering is correct but high risk.

Test signals: Export mount/unmount under normal and pNFS DS modes, root and non-root lookup paths, big-endian wire handles, stale inode reconstruction, statfs values, state allocation/free under NFSv4 opens, and config reload/release leak checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/fileinfo_cache.h -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/fileinfo_cache.h

Purpose: Declares the LizardFS fileinfo cache used by the pNFS DS implementation to reuse `liz_fileinfo_t` objects by inode.

Important APIs and types: Opaque types are `liz_fileinfo_cache_t` and `liz_fileinfo_entry_t`. Functions create/reset/destroy the cache, acquire/release/erase entries, pop expired entries, free entries, extract fileinfo from an entry, and attach fileinfo to an entry.

Control flow: DS code acquires a cache entry for an inode. If `liz_extract_fileinfo()` returns null, it opens the file and calls `liz_attach_fileinfo()`. On DS handle release it calls `liz_fileinfo_cache_release()`. Cache drains use `liz_fileinfo_cache_pop_expired()` followed by `liz_extract_fileinfo()`, LizardFS release, and `liz_fileinfo_entry_free()`.

State and persistence: Cache state is opaque and configured by max entries plus minimum timeout. It stores references to LizardFS fileinfo handles, not file data. Entries may be retained after release until eviction timeout.

Dependencies and integration: The header uses the LizardFS C API and is included by `lzfs_internal.h`, making the cache part of the FSAL private ABI. Implementation is outside the requested files, likely supplied by the LizardFS client library or another source unit.

Risks: Lifetime semantics are subtle: acquired entries must be released or erased; popped expired entries must be freed after releasing their fileinfo; attached fileinfo must not be double-released. Cache fullness returns null from acquire, which DS maps to I/O failure. Timeout units differ between API docs and export config, requiring correct seconds-to-ms conversion.

Test signals: Cache acquire/release balance, erase on open failure, expiration drain, max-size pressure, concurrent acquire of same inode, export teardown drain, and valgrind/ASAN leak checks during pNFS DS workloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/fileinfo_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/handle.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/handle.c

Purpose: Implements LizardFS object-handle operations for namespace manipulation, metadata, file open/reopen/close, read/write/commit, share reservation, locking, wire handles, and object op registration.

Important APIs and types: Registered methods include `release`, `merge`, `lookup`, `mkdir`, `mknode`, `readdir`, `symlink`, `readlink`, `getattrs`, `link`, `rename`, `unlink`, `close`, `handle_to_wire`, `handle_to_key`, `open2`, `status2`, `reopen2`, `read2`, `write2`, `commit2`, `setattr2`, `close2`, `lock_op2`, `close_func`, and `reopen_func`. Private helpers include `lzfs_int_close_fd`, `lzfs_reopen_func`, `lzfs_int_open_by_handle`, `lzfs_int_open_by_name`, and `lzfs_int_close_func`.

Control flow: Namespace operations translate FSAL calls into `liz_cred_*` operations and allocate handles from returned `struct stat`. Open paths either reopen an existing inode, look up an existing child, or create a file via `liz_cred_mknod()`, optionally apply attributes, then open by handle. I/O uses Ganesha `fsal_start_io()`/`fsal_complete_io()` to select state/global/temp fds and enforce share rules, then loops over iovecs with `liz_cred_read()` or `liz_cred_write()`. Metadata updates build LizardFS setattr masks and optionally ACL updates. Locks translate FSAL locks to `liz_lock_info_t` and call LizardFS getlk/setlk.

State and persistence: Handles store inode, unique key, export pointer, share counters, and a global `lzfs_fsal_fd`. Per-state fds come from export state allocation. Persistent state is delegated to LizardFS; handle state controls Ganesha caching and open/share behavior.

Dependencies and integration: Depends on FSAL fd/share helpers, `context_wrap`, `lzfs_internal`, LizardFS error codes, ACL helpers, and optional pNFS MDS ops. It is initialized from `lzfs_fsal_new_handle()`.

Risks: `lzfs_int_open_by_handle()` calls `lzfs_reopen_func(obj_hdl, openflags | after_mknod ? 0x1000 : 0, ...)`; C precedence makes this effectively `(openflags | after_mknod) ? 0x1000 : 0`, likely losing requested open flags. `write2()` assigns then adds `nb_written`, double-counting each iovec. `read2()` has a suspicious `offset == 0` EOF check where `nb_read == 0` was likely intended. `close2()` updates share counters using the global fd's openflags instead of the state fd's openflags. Several create paths return success after failed post-create `setattr2()` while clearing `new_obj`.

Test signals: Open/reopen with every NFS open flag combination, exclusive create verifier, truncate, read/write multi-iovec byte counts, stateless I/O share release, close2 share counters, lock leak/regression tests, mknode rawdev creation, ACL get/set through getattr/setattr, and pNFS-enabled layout ops installation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/lzfs_acl.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/lzfs_acl.c

Purpose: Converts ACLs between Ganesha FSAL/NFSv4 representation and LizardFS ACL representation, and implements internal get/set ACL helpers for LizardFS handles.

Important APIs and types: Main functions are `lzfs_int_convert_fsal_acl()`, `lzfs_int_convert_lzfs_acl()`, `lzfs_int_getacl()`, and `lzfs_int_setacl()`. It uses `fsal_acl_t`, `fsal_ace_t`, `liz_acl_t`, `liz_acl_ace_t`, `nfs4_ace_alloc()`, `nfs4_acl_new_entry()`, and LizardFS ACL helpers. `lzfs_int_apply_masks()` is declared and called but defined elsewhere.

Control flow: FSAL-to-LizardFS conversion filters only ALLOW and DENY ACEs, maps flags, permissions, type, user/group ids, and special owner/group/everyone ids. LizardFS-to-FSAL conversion allocates an FSAL ACE array, reads each LizardFS ACL entry, maps flags and special ids, and interns the ACL through Ganesha's ACL cache. `getacl` releases any existing output ACL, fetches a LizardFS ACL, applies masks using owner id, converts it, destroys the LizardFS ACL, and returns FSAL status. `setacl` converts and calls `liz_cred_setacl()`.

State and persistence: No long-lived state is stored here. ACL persistence is in LizardFS. Ganesha ACL cache references are created/released through NFSv4 ACL helpers.

Dependencies and integration: Used by `handle.c` from `getattrs` and `setattr2`. Depends on `context_wrap`, `lzfs_internal`, LizardFS ACL API, Ganesha ACL macros, and `op_ctx->creds`.

Risks: The unused `count` variable in FSAL-to-LizardFS conversion suggests an earlier sizing design. Unsupported ACE types are silently skipped, which can weaken ACLs. In LizardFS-to-FSAL conversion, `iflag` is assigned instead of preserving group/user flag interactions beyond the low byte. Invalid special ids are logged and coerced. Mask application is external and must be correct for effective permissions.

Test signals: Round-trip ACLs with user, group, owner@, group@, everyone@, ALLOW/DENY, inherited flags, unsupported ACE types, empty ACLs, null ACL set, invalid special ids from server, and ACL cache reference leak checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/lzfs_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/lzfs_internal.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/lzfs_internal.c

Purpose: Provides shared LizardFS FSAL helpers for error translation, credential context creation, static fsinfo access, handle allocation, and handle deletion.

Important APIs and types: Functions include `lizardfs2fsal_error()`, `lizardfs2nfs4_error()`, `lzfs_fsal_last_err()`, `lzfs_nfs4_last_err()`, `lzfs_fsal_create_context()`, `lzfs_fsal_staticinfo()`, `lzfs_fsal_new_handle()`, and `lzfs_fsal_delete_handle()`. It uses `struct lzfs_fsal_module`, `struct lzfs_fsal_export`, and `struct lzfs_fsal_handle`.

Control flow: Error helpers read LizardFS error codes, convert through `liz_error_conv()`, and map to FSAL or NFSv4 errors. Context creation maps anonymous export uid/gid to root uid/gid, creates a user context, and adds supplemental groups either from a stack array or heap array. Handle creation allocates and initializes an FSAL object handle, fills inode and unique key, installs object ops, sets fsid/fileid, records export pointer, and initializes a global fd for regular files.

State and persistence: The file creates in-memory handle state and contexts only. Persistent filesystem state is not modified. `lzfs_fsal_new_handle()` is the main constructor for cached Ganesha object state.

Dependencies and integration: Depends on `fsal_convert`, `pnfs_utils`, `lzfs_internal.h`, LizardFS C API, Ganesha `op_ctx`, and object/fd initialization helpers. Called by export and handle code throughout the FSAL.

Risks: In the heap supplemental-group path, memory is allocated with `gsh_malloc()` but freed with `free()`, which may mismatch allocators. Anonymous uid/gid mapping to zero is security-sensitive and must match export policy. Context creation ignores errors from `liz_update_groups()`. Handle ops are initialized per handle, so any mutable shared ops assumptions should be checked.

Test signals: Error translation for representative LizardFS errors, anonymous credential mapping, large supplemental group arrays above 64 entries, ASAN allocator mismatch checks, handle creation for every object type, and pNFS MDS ops installed only when export flag is enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/lzfs_internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/lzfs_internal.h -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/lzfs_internal.h

Purpose: Defines the private ABI for the LizardFS FSAL, including module/export/handle/fd/key/DS structs, constants, supported attribute mask, and cross-file helper prototypes.

Important APIs and types: Important structs are `lzfs_fsal_module`, `lzfs_fsal_export`, `lzfs_fsal_fd`, `lzfs_fsal_state_fd`, `lzfs_fsal_key`, `lzfs_fsal_handle`, `lzfs_fsal_ds_wire`, and `lzfs_fsal_ds_handle`. Constants include LizardFS version encoding, special inode ids, name/block/chunk sizes, max regular inode, supported attrs, largest pNFS stripe count, expected backup DS count, and TCP protocol number.

Control flow: The header wires implementation units together: main/export code uses export ops prototypes; handle code uses handle constructor/destructor and pNFS hooks; DS/MDS code uses DS wire structs; ACL code uses internal get/set helpers; all files share error/context helpers.

State and persistence: It defines where runtime state lives: export owns `liz_t`, root handle, fileinfo cache, pNFS flags, cache settings, and init params; handles own inode, unique key, fd, export pointer, and share counters; DS handles own inode plus cache entry.

Dependencies and integration: Includes Ganesha FSAL API/commonlib, LizardFS C API, and `fileinfo_cache.h`. This makes the FSAL private implementation tightly coupled to both Ganesha internals and LizardFS client ABI.

Risks: `lzfs_fsal_ds_wire` uses `uint32_t inode`; if `liz_inode_t` changes or exceeds 32 bits, pNFS DS handles truncate. Special inode constants and `MAX_REGULAR_INODE` encode LizardFS-specific assumptions. `LZFS_SUPPORTED_ATTRS` includes ACL support, so ACL conversion must remain reliable. Constants such as `LZFS_BIGGEST_STRIPE_COUNT` and expected backup DS count directly shape wire layouts and buffer sizes.

Test signals: Compile against LizardFS API versions, assert inode type/size assumptions, verify special inode behavior for root and metadata files, pNFS layout encoding for large files near stripe limits, and attribute mask behavior against client GETATTR/SETATTR.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/lzfs_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/main.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/main.c

Purpose: Registers the LizardFS FSAL module, defines module/export configuration schema, initializes static filesystem capabilities, creates exports, mounts LizardFS client instances, and enables pNFS MDS/DS integration.

Important APIs and types: Global module state is `gLizardFSM`; default capabilities live in `default_lizardfs_info`. Config blocks are `lzfs_fsal_param_block` for module-wide options and `lzfs_fsal_export_param_block` for per-export LizardFS client options. Core functions are `lzfs_fsal_create_export()`, `lzfs_fsal_init_config()`, `init()`, and `finish()`.

Control flow: Module init registers `LizardFS`, installs DS ops, export creation, config init, and pNFS module ops. Config init copies defaults and applies module flags such as pNFS MDS/DS, link/symlink support, fsal trace, grace, and umask. Export creation allocates an export, initializes export ops, parses LizardFS connection/cache settings, mounts a LizardFS instance with `liz_init_with_params()`, attaches the export, optionally creates fileinfo cache and registers a pNFS DS, optionally enables pNFS MDS export ops, fetches root attributes, creates root handle, and sets `op_ctx->fsal_export`.

State and persistence: Exports own mounted LizardFS client state, parsed init params, pNFS flags, root handle, and optional fileinfo cache. Persistent data is in the LizardFS cluster.

Dependencies and integration: Depends on Ganesha config parser, FSAL registration, pNFS DS registry, `context_wrap`, `lzfs_internal`, and LizardFS client initialization. It links module capabilities to object/export ops implemented in other files.

Risks: `lzfs_export->lzfs_params.subfolder` is overwritten with `CTX_FULLPATH(op_ctx)`, ignoring parsed `subfolder` and requiring correct later free ownership. pNFS DS registration uses `export_id` as server id and can collide. Error cleanup has separate `error_pds` and `error` paths that must balance DS refs. Password/md5 config handling is sensitive. Module unregister aborts on failure.

Test signals: Config parsing with required hostname and optional client parameters, delayed init, password/md5 paths, pNFS MDS/DS combinations, duplicate pNFS server ids, root getattr failure cleanup, export release after partial create failure, and module load/unload smoke tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/mds_export.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/mds_export.c

Purpose: Implements LizardFS pNFS MDS export/module operations: GETDEVICEINFO, device list, layout type/block/segment reporting, loc-body and device-address sizing, and DS address selection from LizardFS chunkserver/chunk metadata.

Important APIs and types: Public hooks are `lzfs_fsal_export_ops_pnfs()` and `lzfs_fsal_ops_pnfs()`. The main operation is `lzfs_fsal_getdeviceinfo()`. Helpers include chunkserver sorting/dedup/removal/shuffle functions and DS list encoders `lzfs_int_fill_chunk_ds_list()` and `lzfs_int_fill_unused_ds_list()`.

Control flow: GETDEVICEINFO validates FILE layout type, uses `deviceid->device_id2` to find the matching export, retrieves chunk info for `deviceid->devid`, retrieves and randomizes live chunkserver IPs, computes a stripe count bounded by `LZFS_BIGGEST_STRIPE_COUNT`, encodes stripe indices, then encodes multipath DS entries. For chunks with known parts it prefers standard part replicas, then non-standard replicas, and pads with randomized chunkservers up to three addresses. Remaining stripe entries are filled from the randomized server list.

State and persistence: No persistent state is modified. Device info reflects current LizardFS chunk layout and chunkserver availability. Randomized DS ordering creates per-call variability.

Dependencies and integration: Depends on Ganesha pNFS/XDR utilities, module export list, LizardFS chunk/chunkserver APIs, constants from `lzfs_internal.h`, and `op_ctx->creds`. Export ops are enabled from `main.c` when MDS pNFS is supported.

Risks: The custom `remove_if()` copies from `j` to `i`, which is the reverse of the usual compaction direction and appears likely to corrupt filtering results. Duplicate-IP predicate assumes sorted array and pointer arithmetic against previous element. `liz_destroy_chunkservers_info(chunkserver_info)` is called before filtering and freeing labels; correctness depends on LizardFS API semantics. Randomization uses `rand()` without explicit seeding/thread-safety. Device-address size is heuristic but large.

Test signals: GETDEVICEINFO for disconnected servers, duplicate IPs, empty chunkserver list, files with more than 4096 chunks, chunks with fewer than three replicas, non-standard chunk parts, multi-export device ids, XDR buffer boundaries, and repeated calls to check DS distribution stability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/mds_export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/mds_handle.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/mds_handle.c

Purpose: Implements LizardFS pNFS MDS object-handle layout operations: LAYOUTGET, LAYOUTRETURN, and LAYOUTCOMMIT.

Important APIs and types: The main functions are `lzfs_fsal_layoutget()`, `lzfs_fsal_layoutreturn()`, `lzfs_fsal_layoutcommit()`, and `lzfs_fsal_handle_ops_pnfs()`. It uses `struct lzfs_fsal_ds_wire` for DS wire handles, `struct pnfs_deviceid`, `FSAL_encode_file_layout()`, and `MFSCHUNKSIZE` as layout stripe unit.

Control flow: `layoutget` validates FILE layout type, fills a device id with FSAL id, export id in `device_id2`, and file inode in `devid`, encodes a DS wire handle containing the inode, and emits a whole-file FILE layout with `return_on_close` and `last_segment` set. `layoutreturn` accepts only FILE layout type and otherwise does no state cleanup. `layoutcommit` validates type, gets current file attributes, optionally grows size to `last_write + 1`, optionally updates mtime if the supplied time is newer, calls `liz_cred_setattr()`, and marks commit done.

State and persistence: Layout grants do not create local reservations. Layout commit can persist size and mtime to LizardFS. DS wire state is just inode.

Dependencies and integration: Depends on pNFS utilities, `op_ctx`, LizardFS wrappers, and handle/export internals. `lzfs_fsal_handle_ops_pnfs()` is called by handle ops initialization when export pNFS MDS is enabled.

Risks: `layoutcommit` sets `attr.st_mtim.tv_sec = arg->new_time.nseconds` instead of assigning `tv_nsec`, corrupting mtime when nanoseconds are supplied. It does not inspect or decode layoutcommit type-specific data beyond generic args. Layoutget logs `res->segment` before setting offset/length locally, relying on caller-provided segment contents. DS wire inode is 32-bit.

Test signals: LAYOUTGET/COMMIT with size growth, mtime-only commit, nanosecond mtime validation, bad layout type, client close return-on-close behavior, DS handle reconstruction from layout, and pNFS writes that extend files through the DS path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/mds_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/CMakeLists.txt -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/CMakeLists.txt

Purpose: Builds the in-memory MEM FSAL as a Ganesha loadable module.

Important APIs and types: The build target is `fsalmem`, a `MODULE` library composed from `mem_export.c`, `mem_handle.c`, `mem_int.h`, `mem_main.c`, and `mem_up.c`. It defines `-D__USE_GNU`, links `ganesha_nfsd`, `${SYSTEM_LIBRARIES}`, `${LTTNG_LIBRARIES}`, and `${LDFLAG_DISALLOW_UNDEF}`, applies sanitizers, and installs to `${FSAL_DESTINATION}`.

Control flow: CMake declares source list, creates the module, attaches sanitizers, links required libraries, sets version `4.2.0` and SOVERSION `4`, and installs the artifact as FSAL component.

State and persistence: No runtime state. The file determines which MEM FSAL implementation units and trace dependencies are present in the plugin.

Dependencies and integration: Tightly integrated with the Ganesha server library because it links `ganesha_nfsd` directly. Optional LTTng tracing libraries are linked through `${LTTNG_LIBRARIES}`.

Risks: `LDFLAG_DISALLOW_UNDEF` makes missing symbols fail link, useful for module quality but sensitive to platform link rules. Version/SOVERSION must match package expectations. Missing LTTng variable setup can affect builds depending on parent CMake defaults.

Test signals: Build with tracing enabled/disabled, sanitizer builds, undefined-symbol checks, install path packaging, and Ganesha startup with `fsalmem` loaded.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_export.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_export.c

Purpose: Implements FSAL_MEM export lifecycle, dynamic filesystem info, wire-handle endian normalization, NFS state allocation, fd-to-handle lookup, export op registration, async behavior configuration, export creation, and export update.

Important APIs and types: Core methods are `mem_release_export()`, `mem_get_dynamic_info()`, `mem_wire_to_host()`, `mem_free_state()`, `mem_alloc_state()`, `get_fsal_obj_hdl()`, `mem_export_ops_init()`, `str_async_type()`, `mem_create_export()`, and `mem_update_export()`. Configured async modes are `MEM_INLINE`, `MEM_FIXED`, `MEM_RANDOM`, and `MEM_RANDOM_OR_INLINE`.

Control flow: Export creation allocates `mem_fsal_export`, initializes object list and export lock, initializes export ops, loads async config, attaches the export to the FSAL, saves `CTX_FULLPATH(op_ctx)`, sets `op_ctx->fsal_export`, and links the export into `MEM.mem_exports`. Release cleans the root subtree, finalizes and frees the root handle under export lock, detaches export, frees ops, removes from MEM export list, destroys the lock, and frees path/export. Update validates stacking via generic `update_export()`, parses new async config into a temporary struct, then atomically updates async delay/stall/type fields.

State and persistence: MEM FSAL state is entirely in memory. Exports own a root object tree, export path, object list, lock, and async behavior atomics. Dynamic filesystem info reports zeros for capacity and file counts. Per-NFS state owns an `fsal_fd`.

Dependencies and integration: Depends on MEM internals (`mem_int.h`, `mem_clean_export`, `mem_free_handle`, `mem_lookup_path`, `mem_create_handle`), Ganesha export manager/core, config parser, fd/state helpers, and optional LTTng tracepoints.

Risks: `mem_wire_to_host()` sets `fh_min = 1` but then reads a `uint64_t` hashkey and `ushort` length, so malformed short handles can be over-read. Dynamic info zeros may confuse clients expecting finite capacity. `get_fsal_obj_hdl()` assumes fd is the global `mh_file.fd` member, not a state fd. Release ordering must avoid races with concurrent operations during export teardown.

Test signals: Create/release export with populated tree, config parsing for all async modes and update_export changes, malformed wire handles shorter than hash+len, endian conversion, NFSv4 state allocation/free, async delay behavior in MEM I/O tests, and LTTng tracepoint compilation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_export.c -->
