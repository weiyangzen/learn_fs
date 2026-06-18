# subset-b-009833 Research

Grouped research for Samba VFS modules under `sources/user-network-fs/samba/source3/modules`. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_solarisacl.c -->
# sources/user-network-fs/samba/source3/modules/vfs_solarisacl.c

## Purpose

`vfs_solarisacl.c` implements Samba VFS POSIX ACL hooks for Solaris-style ACL storage. It translates between Samba's internal `SMB_ACL_T` model and Solaris `aclent_t` arrays, then uses Solaris `acl()`, `facl()`, and `aclsort()` to read, write, and delete default ACL state. The module registers as `solarisacl` and is intended to sit in the VFS stack where Samba needs Solaris-native ACL semantics rather than the generic POSIX ACL backend.

## Important APIs, Types, And Functions

The file aliases Solaris ACL concepts with `SOLARIS_ACE_T`, `SOLARIS_ACL_T`, `SOLARIS_ACL_TAG_T`, and `SOLARIS_PERM_T`, all backed by Solaris `aclent_t`/mode types. `_IS_DEFAULT()` detects `ACL_DEFAULT`; `_IS_OF_TYPE()` filters access versus default entries for Samba's `SMB_ACL_TYPE_ACCESS` and `SMB_ACL_TYPE_DEFAULT`.

Public VFS-facing functions are `solarisacl_sys_acl_get_fd()`, `solarisacl_sys_acl_set_fd()`, and `solarisacl_sys_acl_delete_def_fd()`, with `solarisacl_sys_acl_get_file()` implemented as an internal helper despite being declared in the companion header. Private conversion helpers include `smb_acl_to_solaris_acl()`, `solaris_acl_to_smb_acl()`, `smb_tag_to_solaris_tag()`, `solaris_tag_to_smb_tag()`, `solaris_perm_to_smb_perm()`, and `smb_perm_to_solaris_perm()`. System-call helpers `solaris_acl_get_file()`, `solaris_acl_get_fd()`, `solaris_add_to_acl()`, and `solaris_acl_sort()` allocate and normalize the native ACL arrays.

The VFS table binds `sys_acl_get_fd_fn`, `sys_acl_blob_get_fd_fn`, `sys_acl_set_fd_fn`, and `sys_acl_delete_def_fd_fn`; `vfs_solarisacl_init()` registers the module with `smb_register_vfs()`.

## Control Flow

ACL reads call `facl(fd, GETACLCNT)` or `acl(path, GETACLCNT)`, allocate an `aclent_t` array of the returned size, fetch entries with `GETACL`, and convert only entries matching the requested access/default type. Conversion builds a Samba ACL by appending `struct smb_acl_entry` values and mapping Solaris tags such as `USER_OBJ`, `GROUP_OBJ`, `OTHER_OBJ`, and `CLASS_OBJ` to Samba tags.

ACL writes start from the caller-supplied Samba ACL, convert it to a Solaris ACL of the requested type, fetch the other ACL half from the file descriptor, append that other half, sort/validate with `aclsort()`, and submit the combined array with `facl(fd, SETACL, count, solaris_acl)`. Default ACL deletion is implemented by reading only the access ACL and writing it back with `acl(path, SETACL)`, relying on Solaris behavior that a directory `SETACL` replaces both access and default entries with the provided set.

## State And Persistence

The module has no durable module-private storage. Persistent state is entirely the filesystem ACL stored by Solaris. Temporary ACL arrays are heap allocated with Samba allocation helpers and freed at function exit. `errno` is used as the primary failure channel for VFS operations returning Unix-style errors.

## Dependencies And Integration Points

The module depends on Samba VFS headers, `files_struct`, `smb_filename`, talloc-backed ACL helpers, and Solaris ACL APIs from `system/filesys.h`. Build integration appears in `source3/modules/wscript_build` as `vfs_solarisacl`, and `source3/wscript` can add it to required static modules on Solaris-like builds. It also delegates ACL blob serialization to `posix_sys_acl_blob_get_fd`.

## Risks And Edge Cases

The source has high-risk implementation defects: `solarisacl_sys_acl_get_file()` is declared non-static in the header but defined static in the C file, and `solarisacl_sys_acl_delete_def_fd()` passes `fsp->fsp_name->base_name` to a function that expects `const struct smb_filename *`, which would dereference a string pointer as a structure. There is also a `DBG_DEBG` typo in an error path. These look like compile or runtime blockers unless hidden by version-specific macro behavior outside this file. Functional risks include relying on callers to supply mask entries, using `aclsort()` as the main validity gate, and preserving the unrelated access/default half by refetching it immediately before write, which can race with other ACL writers.

## Test Signals

Useful tests should cover access and default ACL round trips, deletion of a directory default ACL while preserving access entries, invalid ACL type rejection, invalid tag handling, and Solaris-specific mask normalization. Build tests are especially important for this snapshot because of the apparent prototype, argument, and debug macro inconsistencies. Runtime tests need a filesystem and platform that provide Solaris `acl()`, `facl()`, `aclent_t`, and `aclsort()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_solarisacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_solarisacl.h -->
# sources/user-network-fs/samba/source3/modules/vfs_solarisacl.h

## Purpose

`vfs_solarisacl.h` declares the Solaris ACL VFS module entry points used by Samba code and by `vfs_solarisacl.c`. It is a small prototype header for reading, writing, and deleting Solaris-backed ACLs through Samba's VFS ACL abstraction.

## Important APIs And Types

The header exposes `solarisacl_sys_acl_get_file()`, `solarisacl_sys_acl_get_fd()`, `solarisacl_sys_acl_set_fd()`, `solarisacl_sys_acl_delete_def_fd()`, and `vfs_solarisacl_init()`. These signatures use Samba types `vfs_handle_struct`, `files_struct`, `struct smb_filename`, `SMB_ACL_T`, `SMB_ACL_TYPE_T`, `TALLOC_CTX`, and `NTSTATUS`. It does not define any native Solaris ACL types; those are private to the C implementation.

## Control Flow And Integration

The intended flow is that VFS ACL hooks call the declared functions through the function table registered by `vfs_solarisacl_init()`. Callers pass a Samba filename or file descriptor wrapper plus an ACL type, and the implementation is responsible for conversion to/from Solaris ACL arrays. The header guard `__VFS_SOLARISACL_H__` protects repeated inclusion.

## State And Persistence

The header owns no state. It defines the module's external ABI within Samba and therefore constrains how other translation units can call Solaris ACL operations. Persistent ACL state remains in the filesystem.

## Dependencies

This header assumes that including translation units have already included Samba core type definitions for VFS handles, file structures, ACL types, talloc contexts, and NT status values. It is included by `vfs_solarisacl.c` after Samba base headers.

## Risks And Edge Cases

The declaration of `solarisacl_sys_acl_get_file()` is external, but the C file defines the function as `static`, creating an internal/external linkage mismatch. The header also makes the expected argument type explicit: callers must pass `const struct smb_filename *`, not a raw path string. That matters because the implementation reads `smb_fname->base_name`. Any mismatched caller can compile with warnings in permissive C modes but fail badly at runtime.

## Test Signals

Header-level validation is primarily compile coverage: include the header in the implementation and any platform-specific build that enables `vfs_solarisacl`, and build with warnings treated seriously. ABI tests should verify that the function table signatures match Samba's current VFS ACL hook typedefs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_solarisacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_streams_depot.c -->
# sources/user-network-fs/samba/source3/modules/vfs_streams_depot.c

## Purpose

`vfs_streams_depot.c` implements named streams by storing each stream as a real file under a sidecar directory tree. By default this tree lives at `<share connectpath>/.streams`, although the `streams_depot:directory` parameter can move it elsewhere. The module exposes `FILE_NAMED_STREAMS`, maps stream paths to sidecar files based on the base file's stable file id, and supports stream stat, open, unlink, rename, and enumeration.

## Important APIs, Types, And Functions

`struct streams_depot_config_data` stores `directory`, `check_valid`, and `delete_lost` configuration. `struct streams_depot_dirnames` carries the two-level hash and hex file-id directory components. `hash_fn()` and `streams_depot_get_dirnames()` derive paths like `XX/YY/<file-id-hex>`.

Path helpers are central: `stream_rootdir()` resolves the configured root; `streams_depot_rootdir_pathref()` opens or creates it; `streams_depot_mkdir_pathref()` creates and opens pathref directories; `stream_dir_pathref()` opens or creates a base file's stream directory; and `stream_name()` normalizes a stream name to `:<name>:$DATA`, rejecting non-`$DATA` stream types. `walk_streams()` iterates sidecar entries.

VFS hooks include `streams_depot_openat()`, `streams_depot_fstatat()`, `streams_depot_stat()`, `streams_depot_lstat()`, `streams_depot_unlinkat()`, `streams_depot_rename_stream()`, `streams_depot_fstreaminfo()`, `streams_depot_fs_capabilities()`, and `streams_depot_connect()`.

## Control Flow

Non-stream operations mostly delegate directly to the next VFS module. For named streams, stat converts the requested name to a base file path, validates that the base exists, resolves its hashed sidecar directory, normalizes the stream filename, and stats the sidecar file. Open asserts an alternate-stream `fsp`, uses the already-open `base_fsp` and its stat data, creates the sidecar directory on `O_CREAT`, optionally marks the base file with `SAMBA_XATTR_MARKER`, and opens the stream file inside the sidecar directory.

When a base file is unlinked, the module computes the stream directory path from the base file id and tries to remove that directory before unlinking the base file. Stream unlink removes only the normalized sidecar stream file. Stream rename renames files within the same sidecar directory and checks destination existence when `replace_if_exists` is false. Enumeration walks the sidecar directory, stats each entry, appends `stream_struct` entries, and then calls the next `fstreaminfo` on `metadata_fsp(fsp)`.

## State And Persistence

Persistent stream bytes are ordinary files under the depot directory. Directory structure is deterministic from the base file's `file_id`, not from the pathname. If `check_valid` is enabled, the base file gets `SAMBA_XATTR_MARKER` set to `'1'` when a stream is created, and `stream_dir_valid()` later uses that marker to detect directories left behind after inode reuse. Invalid stream directories are either recursively removed when `delete_lost` is true or renamed to a `lost-<random>` name.

## Dependencies And Integration Points

The module depends on Samba pathref helpers, VFS file-id creation, xattr functions, directory iteration helpers, recursive directory removal, and standard VFS open/stat/rename/unlink operations. It is registered as `streams_depot` and built from `source3/modules/wscript_build`. Selftest references include stream depot torture shares such as `vfs_fruit_stream_depot`, `vfs_wo_fruit_stream_depot`, and `external_streams_depot`.

## Risks And Edge Cases

The file-id based path scheme is vulnerable to orphaned stream directories if files are deleted outside Samba; the marker mechanism mitigates this only on filesystems with usable xattrs and only after Samba has created a stream. Base-file unlink removes the stream directory before unlinking the base, but it ignores sidecar removal failure, so orphaned streams can remain. The stream directory root can be outside the share, so permission, backup, and cleanup policy need explicit attention. The code rejects unsupported stream types and unsupported open resolution flags, which is correct but observable to clients. Cross-filesystem or externally modified depot directories can produce stale or hidden stream state.

## Test Signals

Test coverage should create, open, stat, rename, enumerate, and delete alternate data streams; verify sidecar cleanup on base-file delete; verify invalid-directory rename/delete behavior under inode reuse simulations; test configured external depot directories; and confirm `FILE_NAMED_STREAMS` is advertised. Existing Samba selftest/torture references for streams depot and fruit integration are strong signals for this module.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_streams_depot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_streams_xattr.c -->
# sources/user-network-fs/samba/source3/modules/vfs_streams_xattr.c

## Purpose

`vfs_streams_xattr.c` implements NTFS-style named streams by storing stream contents in extended attributes on the base file. It advertises `FILE_NAMED_STREAMS`, creates fake file descriptors for stream opens, derives stream stat metadata from the base file plus stream xattr content, and implements stream I/O by reading and rewriting xattr values.

## Important APIs, Types, And Functions

`struct streams_xattr_config` stores the primary xattr prefix, extension xattr prefix, maximum extents, and whether to persist `:$DATA` in raw stream names. `struct stream_io` is attached as an FSP extension for alternate-stream handles and caches base path, xattr names, raw stream name, owning `fsp`, and handle pointer.

Large stream support is implemented by `fgetxattr_multi()`, `fsetxattr_multi()`, and `fremovexattr_multi()`. The anchor xattr stores stream data plus a marker byte; marker zero means all data fits in the anchor, and nonzero marker values identify how many extension xattrs exist. `streams_xattr_ext_name()` builds primary and extent names. `streams_xattr_get_name()` parses `:<stream>[:$DATA]` names, honors `store_stream_type`, and builds raw and full xattr names.

VFS hooks cover connect, open/close, stat/fstat/lstat/fstatat, pread/pwrite and async wrappers, unlink, stream rename, truncate, fallocate, stream enumeration, fsync, lock/sharemode/lease/fcntl behavior, chmod/chown no-ops for streams, and xattr operations on stream FSPs.

## Control Flow

Connect reads `streams_xattr:prefix`, `streams_xattr:ext_prefix`, `streams_xattr:store_stream_type`, and `streams_xattr:max xattrs per stream`, then stores config on the VFS handle. Open passes non-stream paths through. For named streams it rejects unsupported resolution flags, resolves the xattr name, reads the existing value, creates or truncates an empty one-byte xattr when needed, allocates a fake fd, and attaches `stream_io` to the stream FSP.

Reads fetch the full xattr-backed stream into memory, subtract the marker byte from the logical length, and copy the requested range. Writes fetch the existing value, grow/zero-fill if needed, copy the new bytes, and write the complete value back across anchor and extent xattrs. Truncate resizes the value and rewrites it. Rename copies the source xattr payload to the destination with optional `XATTR_CREATE`, then removes the source. Enumeration lists xattr names, filters private Samba attributes, selects names with the configured prefix, reads values, and emits `stream_struct` entries.

## State And Persistence

Stream bytes persist as xattrs on the base file. Logical empty streams still consume a one-byte value because xattrs cannot represent zero-length payloads in this implementation. Large streams can span the anchor plus up to `max_extents` extension xattrs, with stale extension cleanup attempted when shrinking. Per-open transient state is held in the FSP extension and rechecked if `fsp->fsp_name` changes.

## Dependencies And Integration Points

The module depends on Samba VFS xattr operations, fake fd helpers, FSP extensions, `hash_inode()` for synthetic stream inode values, `tevent` async request wrappers, `get_ea_names_from_fsp()`, `samba_private_attr_name()`, and share parameter helpers. It is built as `vfs_streams_xattr`; selftest references include `samba3.blackbox.delete_stream` with `acl_streams_xattr` and `vfs.streams_xattr` torture runs.

## Risks And Edge Cases

The implementation rewrites whole streams on each write, so large streams are expensive and can hit xattr size limits. If an extent write fails after the anchor was updated, later reads can return short data when missing extents are encountered. Fsync for stream handles is effectively a no-op because there is no pathname-based sync in this layer and no direct basefile handle in that callback. Stream locks are mostly accepted locally rather than mapped to byte-range locks on a durable backing object. The source also contains suspicious implementation details: `SMB_VFS_HANDLE_SET_DATA()` names `struct stream_xattr_config` instead of `struct streams_xattr_config`, and some `tevent_req_nomem()` calls appear to pass arguments in the wrong order in pass-through async paths.

## Test Signals

Tests should cover one-byte empty streams, create/open/truncate/read/write/rename/unlink, stream names containing colons under fruit native encoding, multi-extent streams near `smbd max xattr size`, shrinking from multi-extent to short streams, enumeration filtering of Samba private attributes, fake-fd close behavior, and failure recovery after partial extent writes. Existing `vfs.streams_xattr` and delete-stream selftests are directly relevant.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_streams_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_syncops.c -->
# sources/user-network-fs/samba/source3/modules/vfs_syncops.c

## Purpose

`vfs_syncops.c` is a durability-focused Samba VFS module that forces metadata and close-time synchronization after operations that create, remove, or rename directory entries. It is intended for filesystems or clustered deployments where Samba must ensure metadata survives power loss or failover. The module registers as `syncops`.

## Important APIs, Types, And Functions

`struct syncops_config_data` stores three booleans: `onclose`, `onmeta`, and `disable`. `parent_dir()` computes the parent path string for a name. `syncops_sync_directory()` opens a directory through Samba's `OpenDir()` and calls `smb_vfs_fsync_sync()` on the directory FSP. `syncops_two_names()` syncs both parent directories for operations involving source and destination paths, while `syncops_smb_fname()` syncs one parent directory.

The `SYNCOPS_NEXT_SMB_FNAME` macro wraps simple metadata operations by calling the next VFS function, checking config, constructing a full path from `dirfsp` and `smb_fname`, syncing the parent directory, and returning the original result. Explicit wrappers handle `renameat`, `linkat`, `openat`, `unlinkat`, `mknodat`, `mkdirat`, `symlinkat`, and `close`.

## Control Flow

On connect, the module calls the next connect hook, allocates config, and reads `syncops:onclose` (default true), `syncops:onmeta` (default true), and `syncops:disable` (default false). Metadata wrappers first perform the requested operation through the next VFS module. If it fails, or if syncops is disabled, or if `onmeta` is false, they return immediately. Otherwise they derive full paths and fsync the affected parent directories. `renameat` and `linkat` explicitly handle two directory names; create-like and delete-like operations use the shared macro. `close` fsyncs the file descriptor before closing when the file can be written and `onclose` is enabled.

## State And Persistence

The module has no durable private state. It intentionally changes persistence behavior of underlying filesystems by invoking fsync on files and directories. Config is per VFS handle/share connection and is talloc-managed with the connection.

## Dependencies And Integration Points

The module uses Samba directory helpers from `source3/smbd/dir.h`, path construction via `full_path_from_dirfsp_atname()`, and the core VFS operation chain. It is listed in `source3/modules/wscript_build` and appears in `source3/wscript` default shared modules for non-static builds.

## Risks And Edge Cases

The major risk is performance: fsync on close and parent-directory fsync after metadata changes can dominate workload latency. Some error paths intentionally return the original successful metadata result even if path construction or sync fails, so durability can silently degrade under memory pressure or directory-open failures. Parent path calculation is string-based and assumes normalized names. The `mkdirat` wrapper passes an unused macro parameter expression, but the macro body uses `smb_fname` directly, so this is confusing but not functionally significant.

## Test Signals

Tests should verify that each metadata operation delegates correctly when disabled, that configured `onmeta=no` and `onclose=no` suppress sync behavior, and that rename/link sync both parent directories when source and destination differ. Fault injection around `OpenDir()`, path construction, and fsync would validate that user-visible operation status is preserved while durability warnings can be diagnosed through debug logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_syncops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_time_audit.c -->
# sources/user-network-fs/samba/source3/modules/vfs_time_audit.c

## Purpose

`vfs_time_audit.c` is an instrumentation VFS module that measures elapsed time for Samba VFS calls and logs a warning when an operation exceeds a configurable threshold. It is designed to diagnose slow storage, filesystem, network, or lower VFS-module behavior without changing operation semantics. It registers as `time_audit`.

## Important APIs, Types, And Functions

The module has one global setting, `audit_timeout`, loaded from `time_audit:timeout` in milliseconds and stored as seconds. Logging helpers are `smb_time_audit_log_msg()`, `smb_time_audit_log()`, `smb_time_audit_log_fsp()`, `smb_time_audit_log_at()`, `smb_time_audit_log_fname()`, and `smb_time_audit_log_smb_fname()`.

Most wrappers follow a standard pattern: capture `clock_gettime_mono()` before and after `SMB_VFS_NEXT_*`, compute `nsec_time_diff() * 1.0e-9`, and log if above threshold. Async operations maintain small state structs that capture FSP or path context and use `vfs_aio_state.duration` or send/receive monotonic timestamps in recv callbacks. The function table is broad and ends with `smb_vfs_assert_all_fns(&vfs_time_audit_fns, "time_audit")`, which asserts that every VFS operation has an audit wrapper.

## Control Flow

The wrappers delegate to the next VFS module and preserve return values. Path-aware operations sometimes build a full filename before timing so log messages include useful context. Create/open/close, directory operations, stat variants, quota, DFS, snapshot, read/write/sendfile/recvfile, rename, fsync, allocation, lock, lease, ACL, xattr, compression, copy offload, durable handle, and DOS attribute paths are all covered.

Async wrappers such as pread, pwrite, fsync, get DOS attributes, getxattrat, offload read, and offload write create a parent request, call the next async send function, store results in a state struct in the callback, and log from recv based on the lower layer's reported duration or send-to-recv elapsed time.

## State And Persistence

There is no filesystem persistence. Runtime state is limited to the global `audit_timeout` and per-async-request talloc state. The persistent side effect is log output at `DEBUG(0)` warning level when calls exceed the threshold.

## Dependencies And Integration Points

The module depends on Samba VFS macro APIs, monotonic time helpers, `tevent` async request helpers, NT status tevent helpers, Samba pathname and FSP structures, and debug logging. It is built as `vfs_time_audit` in `source3/modules/wscript_build` and listed among default shared modules in `source3/wscript`. Because it asserts all VFS functions, it is sensitive to VFS interface changes and acts as coverage pressure for new hooks.

## Risks And Edge Cases

Instrumentation overhead is small but nonzero on every VFS call, including very hot read/write/stat paths. Some logging helpers dereference contextual structures such as `dir_fsp`, `smb_fname`, `fsp->conn`, or `fsp->fsp_name`; most common null cases are handled, but not every helper is equally defensive. If logging itself blocks or allocates heavily during storage stalls, the module can add noise. Because the timeout is global static state, per-share configuration changes after module initialization are not represented. Wrappers must preserve `errno` on failure; most do, and `fallocate` explicitly saves it, but this is a recurring regression risk.

## Test Signals

Tests should load the module with a very low timeout and verify warning logs for representative sync and async VFS calls. ABI tests should confirm `smb_vfs_assert_all_fns()` passes after VFS interface changes. Failure-path tests should check `errno`/NTSTATUS preservation for operations like open, unlink, fallocate, xattr reads, and async receives.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_time_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_tsmsm.c -->
# sources/user-network-fs/samba/source3/modules/vfs_tsmsm.c

## Purpose

`vfs_tsmsm.c` integrates Samba with Tivoli Storage Manager Space Management through DMAPI. It detects migrated/offline files, advertises remote-storage capabilities, forces asynchronous I/O heuristically for possibly offline files, sends client notifications when I/O brings files online, and optionally invokes an HSM script to mark files offline. The module registers as `tsmsm` and is compiled only when DMAPI support is available.

## Important APIs, Types, And Functions

`struct tsmsm_struct` stores `online_ratio`, `hsmscript`, `attrib_name`, and optional `attrib_value`. `tsmsm_connect()` initializes this config from parameters `tsmsm:hsm script`, `tsmsm:online ratio`, `tsmsm:dmapi attribute`, and `tsmsm:dmapi value`, and requires an available DMAPI session. `tsmsm_is_offline()` is the core detector: it first uses block-count heuristics, then queries DMAPI attributes when a file may be migrated. `tsmsm_aio_force()` uses the same heuristic to decide whether I/O should be forced asynchronous.

I/O wrappers include sync and async `pread`/`pwrite`, `sendfile`, and receive callbacks that notify clients when a previously offline-looking file was accessed successfully. Attribute wrappers include `tsmsm_fget_dos_attributes()` and `tsmsm_fset_dos_attributes()`. `tsmsm_set_offline()` executes the configured script using `smbrun()`. `tsmsm_fs_capabilities()` adds `FILE_SUPPORTS_REMOTE_STORAGE` and `FILE_SUPPORTS_REPARSE_POINTS`.

## Control Flow

Connect delegates to the next VFS connect, allocates config, validates DMAPI session availability, reads configuration, and stores handle data. Offline detection first compares `512 * st_blocks` to `st_size * online_ratio`; sufficiently allocated files are assumed online. Sparse or low-block files trigger DMAPI path handling under `become_root()`: convert path to DMAPI handle, query the configured attribute, recreate a stale session on `EINVAL`, and decide offline based on attribute existence or exact configured value.

Before I/O, `tsmsm_aio_force()` cheaply decides if a file may be offline. After successful reads/writes that started from a possibly offline file, the module sends `NOTIFY_ACTION_MODIFIED | NOTIFY_ACTION_DIRLEASE_BREAK` with `FILE_NOTIFY_CHANGE_ATTRIBUTES` so clients can refresh offline status. `sendfile` is rejected with `ENOSYS` for possibly offline files to avoid blocking/non-AIO recall behavior. Setting DOS attributes delegates first, then may invoke the HSM script to offline the file.

## State And Persistence

The module keeps per-handle configuration only. Persistent state is external: DMAPI-managed file migration attributes and any effects of the configured HSM script. Notifications are transient SMB state changes.

## Dependencies And Integration Points

The file requires `USE_DMAPI` and includes platform-specific DMAPI headers from XFS, AIX/JFS, or system locations. It uses Samba DMAPI session helpers, root privilege transitions, `get_full_smb_filename()`, `notify_fname()`, VFS async I/O, DOS attribute hooks, and capability hooks. Build integration appears as `vfs_tsmsm` in `source3/modules/wscript_build`.

## Risks And Edge Cases

DMAPI calls require elevated privileges and can be slow, so the heuristic is important but can misclassify sparse online files as possibly offline. On DMAPI path-to-handle failure, the module assumes offline, which favors recall safety but can affect client behavior. The HSM script command is built with shell quoting around only the path argument and uses `smbrun()`, so script path configuration must be trusted. A stale DMAPI session is retried, but repeated DMAPI failures can produce conservative offline decisions. `tsmsm_fset_dos_attributes()` appears to call `tsmsm_set_offline()` unless a specific old/new offline-bit condition returns early, so behavior should be verified against intended offline transition semantics.

## Test Signals

Tests need a DMAPI-capable filesystem or mocks for session, handle, and attribute calls. Key scenarios are online-ratio fast path, DMAPI attribute existence and value matching, stale-session recreation, sendfile rejection for possible offline files, notifications after successful recall-triggering I/O, DOS offline attribute reporting, HSM script invocation, and capability bit advertisement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_tsmsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_unityed_media.c -->
# sources/user-network-fs/samba/source3/modules/vfs_unityed_media.c

## Purpose

`vfs_unityed_media.c` is a Samba VFS module for Avid shared-media workflows. It makes client-specific suffixed media directories appear as unsuffixed numeric directories to each client, reducing collisions when multiple clients use `Avid MediaFiles/MXF` or `OMFI MediaFiles`. The module rewrites paths under those media roots to include a suffix derived from username, client IP, or hostname.

## Important APIs, Types, And Functions

`enum um_clientid` selects suffix identity: `user`, `ip`, or `hostname`. `struct um_config_data` stores that choice. `um_dirinfo_struct` wraps a real `DIR *` plus original path, client path, media-root flag, and current client subdirectory name.

Path helpers include `get_digit_group()`, which extracts the first numeric group from a path; `alloc_append_client_suffix()`, which appends `_<clientid>.<number>`; `is_apple_double()`, `starts_with_media_dir()`, `is_in_media_dir()`, and `is_in_media_files()`, which recognize Avid/OMFI media roots and levels; `alloc_get_client_path()` and `alloc_get_client_smb_fname()`, which transform visible paths to client-specific physical paths; and `alloc_set_client_dirinfo()` helpers for directory listing state.

The VFS table wraps connect, fstatvfs, directory open/read/rewind/close, mkdir, open, create_file, rename, stat/lstat/fstat, unlink, lchown, chdir, symlink/readlink, link, mknod, and realpath. Async xattrat hooks are explicitly not implemented.

## Control Flow

Connect reads `unityed_media:clientid`, defaulting to username, and stores config. Most VFS calls first check whether the target path is under `Avid MediaFiles/MXF` or `OMFI MediaFiles`; outside those roots they delegate unchanged. Inside media roots, paths are copied and the relevant numeric component is suffixed with the selected client identity and the extracted number. Operations that receive `dirfsp` build full paths first, then call the next VFS operation from `cwd_fsp` with rewritten names when needed.

Directory listing wraps the real `DIR *` in `um_dirinfo_struct`. `um_readdir()` strips this client's suffix from matching directory names before returning entries and can skip or expose other clients' suffixed directories depending on branch behavior. AppleDouble `._` names are handled by applying suffix logic after the prefix. Stat-style calls rewrite to the physical client path, delegate, and copy stat data back to the visible filename.

## State And Persistence

Persistent state is the on-disk naming scheme: client-specific media directories such as numeric Avid directories with appended `_<client>.<number>`. The module does not store an index. Per-directory iteration state is heap allocated in `um_fdopendir()` and freed in `um_closedir()`. Per-share config is stored on the VFS handle.

## Dependencies And Integration Points

The module depends on Samba VFS pathname helpers, `get_current_username()`, `get_remote_machine_name()`, remote socket address helpers, `smb_strtoul()`, talloc string builders, and standard VFS chaining. It registers a custom debug class `unityed_media`, is built as `vfs_unityed_media`, and is listed among default shared modules in `source3/wscript`.

## Risks And Edge Cases

This module is intentionally domain-specific and can surprise general-purpose filesystem users. The numeric-group parser uses the first digit group in a path, so unexpected digits elsewhere can influence suffixing. Several comments mark FIXME areas around stat correctness for database files and directory-state behavior. Directory listing mutates `dirent->d_name` in place, which depends on the returned buffer being writable and long enough for truncation semantics. Path rewriting is string-based and must stay aligned with Samba's path normalization, AppleDouble handling, and relative path forms like `./OMFI MediaFiles`. Cross-client visibility rules are controlled by branch constants in code rather than explicit configuration.

## Test Signals

Tests should exercise username/IP/hostname suffix modes; path rewrites for `Avid MediaFiles/MXF/<number>` and `OMFI MediaFiles`; AppleDouble names; mkdir/open/create/rename/stat/unlink/link/symlink/readlink under and outside media roots; directory listing suffix stripping; and relative `./` path inputs. Avid workflow integration tests should verify that each client sees its own numeric media directories while physical storage remains suffixed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_unityed_media.c -->
