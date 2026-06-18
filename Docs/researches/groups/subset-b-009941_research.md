# Research: subset-b-009941

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ipc/vfs_ipc.c -->
# sources/user-network-fs/samba/source4/ntvfs/ipc/vfs_ipc.c

Purpose: implements the default `NTVFS_IPC` backend for IPC$ shares. It accepts tree connects, opens named pipes, bridges SMB read/write/trans/ioctl operations to Samba named-pipe `tstream` transports, and rejects ordinary filesystem operations that do not make sense on IPC$.

Important APIs and types: `struct ipc_private` owns per-share state and the list of open `pipe_state` objects. `pipe_state` binds an `ntvfs_handle` to a lower named pipe stream plus `file_type`, `device_state`, allocation size, and serialized read/write `tevent_queue`s. Key entry points are `ipc_connect`, `ipc_open`, `ipc_read`, `ipc_write`, `ipc_trans`, `ipc_ioctl`, `ipc_close`, `ipc_exit`, `ipc_logoff`, and `ntvfs_ipc_init`.

Control flow: `ipc_connect` normalizes the share path and installs IPC filesystem/device labels. `ipc_open` validates pipe names, creates an NTVFS handle, creates queue state, builds `auth_session_info_transport`, and asynchronously calls `tstream_npa_connect_send`; `ipc_open_done` publishes SMB1/SMB2 open outputs and attaches backend data. Generic read/write/close levels are delegated to `ntvfs_map_*`, while `RAW_*_GENERIC` operations perform queued tstream I/O and reply asynchronously. `ipc_trans` handles `\\PIPE\\LANMAN` RAP, named-pipe handle state, and DCERPC transact write-then-read. SMB2 `FSCTL_NAMED_PIPE_READ_WRITE` follows the same write/read pattern.

State and persistence: pipe state is memory-only and talloc-scoped to handles. The destructor removes it from `pipe_list` and destroys handle backend data. `exit` and `logoff` close matching pipes. No persistent files are created by this backend; durable effects are delegated to named-pipe servers.

Dependencies and integration points: uses NTVFS handle callbacks, tevent async state, `tstream_npa`, named-pipe auth, RAP IPC helpers, tsocket local/remote addresses, and generic NTVFS mappers. `ntvfs_ipc_init` registers backend name `default` for `NTVFS_IPC`.

Risks: async completion must always set status and send exactly once; read/trans/ioctl paths explicitly reject concurrent reads with `NT_STATUS_PIPE_BUSY`; invalid fnum conversion or stale handles produce `INVALID_HANDLE`; pipe-name validation only permits alnum and underscore after lowercasing. Test signals include IPC$ tree connect, SMB1/SMB2 pipe open variants, concurrent transact/read busy behavior, buffer overflow reporting via `STATUS_BUFFER_OVERFLOW`, logoff/exit cleanup, and unsupported filesystem operations returning access-denied style statuses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ipc/vfs_ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ntvfs.h -->
# sources/user-network-fs/samba/source4/ntvfs/ntvfs.h

Purpose: defines the core NTVFS ABI: backend operation tables, module stack contexts, per-connection state, request async state, and file handle backend data. It is the contract that all disk, IPC, and print NTVFS modules implement.

Important APIs and types: `enum ntvfs_type` separates disk, IPC, and print shares. `struct ntvfs_ops` is the central vtable with connect/disconnect, path operations, open/search/ioctl/read/write/lock/info/close, transaction, notify, cancel, print, logoff, and exit callbacks. `struct ntvfs_module_context` links modules in a stack. `struct ntvfs_context` stores protocol, client capabilities, share config, event/messaging contexts, addresses, oplock callbacks, and frontend handle callbacks. `struct ntvfs_request` carries session info, SMB PID, per-request async-state stack, and statistics. `struct ntvfs_handle` stores frontend identity plus per-module backend data. `NTVFS_CURRENT_CRITICAL_SIZES` captures ABI-sensitive sizes for module registration.

Control flow: frontends create `ntvfs_request` instances and call interface functions that dispatch to the first module. Stacked modules call `ntvfs_next_*` wrappers to continue down the chain. Async operations use a linked stack of `ntvfs_async_state`; a backend marks `NTVFS_ASYNC_STATE_ASYNC` when it will reply later.

State and persistence: this header defines in-memory state only. Lifetimes are talloc-based, with handles able to carry one backend data record per module owner. Persistent file semantics live in backend implementations.

Dependencies and integration points: includes raw SMB interface unions, share config, generated security/server-id types, notify/security NDR headers, and `ntvfs_proto.h`. The ABI version is intentionally `0`, with size checks used by registration.

Risks: any struct layout or callback signature change can break modules; callback fields are nullable and callers must guard for `NOT_IMPLEMENTED`; async-state stack misuse can corrupt reply routing. Test signals include module registration version checks, stacked module pass-through, handle callback wiring, and async reply paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ntvfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ntvfs_base.c -->
# sources/user-network-fs/samba/source4/ntvfs/ntvfs_base.c

Purpose: supplies the global NTVFS backend registry, ABI compatibility checks, connection stack construction, default IPC$ share injection, and module initialization.

Important APIs and functions: `ntvfs_register` validates `struct ntvfs_critical_sizes`, rejects duplicate name/type pairs, deep-copies `ntvfs_ops`, and appends to the static backend array. `ntvfs_backend_byname` resolves a registered backend by name and `enum ntvfs_type`. `ntvfs_interface_version` and `ntvfs_interface_differs` implement ABI checks. `ntvfs_init_connection` creates `struct ntvfs_context` and a linked stack of `ntvfs_module_context` objects from the share `ntvfs handler` list. `ntvfs_init` loads static/shared modules and ensures IPC$ exists.

Control flow: process startup calls `ntvfs_init`, which is guarded by a static `initialized` flag, loads modules, and calls `ntvfs_add_ipc_share`. Tree-connect setup calls `ntvfs_init_connection`, which reads handler names from share config, resolves each backend for the requested type, assigns depth, and appends module contexts in order.

State and persistence: registered backends live in static process memory for the life of the server. `ntvfs_init_connection` allocates per-connection state under the caller's talloc context and steals the share config. IPC$ addition mutates the loadparm service table if no IPC$ service exists.

Dependencies and integration points: depends on `share_string_list_option`, loadparm service APIs, Samba module loading, and dlink list helpers. Backend modules register through this file and later dispatch through `ntvfs_interface.c`.

Risks: static registry is not explicitly synchronized; duplicate backend names by type are rejected; missing handler config or missing registered backend returns internal error; ABI checks compare only selected critical sizes and version. Test signals include duplicate registration, unknown handler failure, multiple stacked handlers preserving order/depth, idempotent `ntvfs_init`, and automatic IPC$ creation with handler `default`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ntvfs_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ntvfs_generic.c -->
# sources/user-network-fs/samba/source4/ntvfs/ntvfs_generic.c

Purpose: maps legacy SMB1 and SMB2 operation variants onto a smaller set of generic backend calls, then maps generic results back to the caller's requested information level. It lets backends implement canonical operations while preserving protocol-specific behavior.

Important APIs and functions: async support is implemented by `struct ntvfs_map_async`, `ntvfs_map_async_setup`, `ntvfs_map_async_finish`, and `ntvfs_map_async_send`. Public mappers include `ntvfs_map_open`, `ntvfs_map_fsinfo`, `ntvfs_map_fileinfo`, `ntvfs_map_qfileinfo`, `ntvfs_map_qpathinfo`, `ntvfs_map_lock`, `ntvfs_map_write`, `ntvfs_map_read`, `ntvfs_map_close`, and `ntvfs_map_notify`. `map_openx_open` translates OpenX access/share/disposition rules and `is_exe_filename` implements DOS deny-mode quirks.

Control flow: each mapper allocates a second union, pushes an async state containing original/new I/O and a finish callback, calls the backend's generic operation, then either returns pending async status or immediately pops the state and maps outputs. Open mapping handles Open/OpenX/T2Open/MkNew/Create/CTemp/SMB2; write/read mapping handles older write/read forms and SMB2; close and notify convert SMB2 outputs; file/fs info mapping fan out generic metadata into many raw levels.

State and persistence: only per-request talloc state is created. Some mappers issue synchronous secondary calls, such as setting write time or size after create, unlocking after write-unlock, locking before lock-read, or closing after write-close.

Dependencies and integration points: dispatches through `ntvfs->ops` and async-state helpers. It encodes SMB constants, NT create options, security masks, oplock level mapping, and info-level unions from raw protocol headers.

Risks: compatibility behavior is subtle, especially deny modes, SMB2 unsupported create options, `MAXIMUM_ALLOWED`, Unix info levels intentionally invalid, buffer allocations for streams/EAs, and secondary calls with async disabled. Test signals should cover every raw level, async and immediate backend completion, SMB2 create option rejection, OpenX created-size extension, lock flag validation, and notify empty-change mapping to `NT_STATUS_NOTIFY_ENUM_DIR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ntvfs_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ntvfs_interface.c -->
# sources/user-network-fs/samba/source4/ntvfs/ntvfs_interface.c

Purpose: provides the public NTVFS dispatch wrappers and module-stack pass-through wrappers. It is intentionally thin glue between callers and `struct ntvfs_ops`.

Important APIs and functions: top-level wrappers such as `ntvfs_connect`, `ntvfs_open`, `ntvfs_read`, `ntvfs_write`, `ntvfs_trans`, `ntvfs_notify`, and `ntvfs_cancel` dispatch to `req->ctx->modules`. `ntvfs_next_*` variants dispatch to `ntvfs->next` for stacked modules. Address and oplock helpers are `ntvfs_set_addresses`, `ntvfs_get_local_address`, `ntvfs_get_remote_address`, `ntvfs_set_oplock_handler`, and `ntvfs_send_oplock_break`.

Control flow: each wrapper checks whether the target module and operation callback exist, returns `NT_STATUS_NOT_IMPLEMENTED` if absent, and otherwise calls the callback with the module context, request, and operation union. `ntvfs_disconnect` also validates a non-null context. Pass-through functions are mechanically parallel to top-level wrappers but advance one module down the linked list.

State and persistence: this file stores copied local/remote socket addresses under the NTVFS context and installs an oplock callback pointer/private data. It otherwise persists no filesystem data and does not own backend state.

Dependencies and integration points: integrates frontends with backend modules and stacked filters. Uses tsocket address copying and the oplock callback stored in `struct ntvfs_context`.

Risks: the wrappers assume `req`, `ctx`, and the first module are valid; missing callbacks surface as `NOT_IMPLEMENTED`; stacked modules must choose top-level versus `next` dispatch correctly or may recurse or bypass filters. Test signals include every operation returning `NOT_IMPLEMENTED` when absent, pass-through to next module, address copy lifetime, oplock break callback invocation, and invalid-context disconnect handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ntvfs_interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ntvfs_util.c -->
# sources/user-network-fs/samba/source4/ntvfs/ntvfs_util.c

Purpose: implements common helpers for request creation, async-state stacking, and NTVFS handle backend-data management.

Important APIs and functions: `ntvfs_request_create` allocates and initializes a request plus its first async state. `ntvfs_async_state_push` and `ntvfs_async_state_pop` let mapping/filter layers wrap backend async replies. `ntvfs_handle_new`, `ntvfs_handle_set_backend_data`, `ntvfs_handle_get_backend_data`, `ntvfs_handle_remove_backend_data`, `ntvfs_handle_search_by_wire_key`, and `ntvfs_set_handle_callbacks` abstract frontend handle allocation/lookup/destruction.

Control flow: request creation copies context, session, SMB PID, client capabilities, statistics time, frontend private data, send function, and initial state. Async push clones the current state flags, stores layer private data and send callback, and links it at the head. Pop removes the current state, propagates its state/status to the next layer, and frees it. Backend-data setters either replace an existing owner record or allocate a new one; the first backend-data insertion calls the frontend `make_valid` callback.

State and persistence: all state is in-memory and talloc-scoped. Handle backend-data records are owned by the handle and tagged with the module owner. Removing the last backend-data record calls the frontend destroy callback.

Dependencies and integration points: relies on callbacks installed in `ntvfs_context.handles`, dlink list helpers, and the async semantics defined in `ntvfs.h`. IPC and POSIX modules use these helpers to bind backend objects to protocol handles.

Risks: `ntvfs_async_state_pop` assumes a lower async state exists; handle callbacks may be unset and must return `NOT_IMPLEMENTED`/NULL; replacing backend data steals ownership and can alter lifetimes. Test signals include first backend-data `make_valid`, last removal `destroy`, wire-key lookup, async push/pop status propagation, and missing callback behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/ntvfs_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/posix_eadb.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/posix_eadb.c

Purpose: provides a TDB-backed extended-attribute database for POSIX NTVFS deployments that cannot or do not use native xattrs. Attributes are keyed by device/inode plus attribute name and include a synthetic per-file list for cleanup.

Important APIs and functions: `get_ea_tdb_key` builds binary keys from `st_dev`, `st_ino`, and `attr_name`. Raw APIs are `pull_xattr_blob_tdb_raw`, `push_xattr_blob_tdb_raw`, `delete_posix_eadb_raw`, `unlink_posix_eadb_raw`, and `list_posix_eadb_raw`. `posix_eadb_add_list` maintains the special `.xattr_list` record. Under `WITH_NTVFS_FILESERVER`, wrapper functions route through `pvfs_state->ea_db`.

Control flow: reads stat/fstat the path or fd, fetch the key from TDB, and talloc-copy results. Writes create a temporary context, chain-lock the target key, update `.xattr_list` unless writing the list itself, then `tdb_store` the blob. Unlink reads `.xattr_list`, deletes each named attribute, and then deletes the list.

State and persistence: persistent state lives in the TDB database referenced by `struct tdb_wrap`. Keys follow files by inode/device, not path. The `.xattr_list` value is a packed NUL-separated string list used to remove orphaned records during unlink.

Dependencies and integration points: used by PVFS xattr hooks and exposed through `posix_eadb.h` prototypes. Depends on TDB, `stat`/`fstat`, Samba `DATA_BLOB`, and NTSTATUS error mapping.

Risks: keying by inode/device means replacement files get different keys while hard links share attributes; delete path uses fd `-1` for listed attributes during unlink, so path/inode state must still resolve; malformed `.xattr_list` could affect cleanup iteration; `tdb_chainlock` protects writes for one key but the list and attribute updates are not a wider transaction. Test signals include write/read/delete/list, hard-link behavior, unlink cleanup, missing file/status mapping, memory failures, and concurrent writers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/posix_eadb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/posix_eadb.h -->
# sources/user-network-fs/samba/source4/ntvfs/posix/posix_eadb.h

Purpose: declares the POSIX EADB interface by forward-declaring `struct pvfs_state` and including the generated `posix_eadb_proto.h` prototypes.

Important APIs and types: the header itself defines no functions beyond including generated prototypes. The important surface is the raw TDB-backed xattr API and, when file-server support is enabled, the `pvfs_state` wrapper API implemented in `posix_eadb.c`.

Control flow: consumers include this header to call EADB routines without needing the full `vfs_posix.h` definition at declaration time. The generated prototype header supplies signatures for pull, push, delete, unlink, and list routines.

State and persistence: no state is stored here. Persistence is in the TDB database managed by the implementation.

Dependencies and integration points: bridges POSIX NTVFS code and generated prototype infrastructure under `source4/ntvfs/posix`. The forward declaration reduces include coupling.

Risks: correctness depends on generated prototypes matching implementation signatures and compile flags such as `WITH_NTVFS_FILESERVER`. Test signals are compile-time: include this header from translation units with and without full `pvfs_state` definition and verify no signature drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/posix_eadb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_acl.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_acl.c

Purpose: implements PVFS ACL backend registration, default ACL synthesis from Unix mode bits, ACL query/set operations, access checks, parent/create checks, inheritance, and maximal-access calculation.

Important APIs and functions: backend registry functions are `pvfs_acl_register`, `pvfs_acl_backend_byname`, and `pvfs_acl_init`. Security paths include `pvfs_default_acl`, `pvfs_acl_set`, `pvfs_acl_query`, `pvfs_access_check`, `pvfs_access_check_simple`, `pvfs_access_check_create`, `pvfs_access_check_parent`, `pvfs_acl_inherited_sd`, `pvfs_acl_inherit`, and `pvfs_access_maximal_allowed`. Helpers translate generic access bits, detect read-only shares, group membership, privileged owner access, and inheritable ACE behavior.

Control flow: query/set first try configured ACL ops, then fall back to default ACLs when no stored ACL exists. Set enforces `WRITE_OWNER`, `WRITE_DAC`, and `SYSTEM_SECURITY`, maps SIDs to Unix IDs for chown/fchown, optionally escalates with restore/take-ownership privileges, and saves only changed descriptors. Access checks reject write access on read-only shares, process delete-child from the parent, translate masks, load NT ACL xattrs where present, otherwise use Unix mode bits, and apply SMB1 read-attribute compatibility. Create checks validate parent rights, optionally build inherited security descriptors, and expand maximum allowed. Inheritance copies parent inheritable ACEs with creator-owner/group substitution and container/object flag rules.

State and persistence: registry is process-global. Stored ACL persistence is delegated to selected `pvfs_acl_ops` backends. Unix owner/group changes are persistent via chown. `name->allow_override` is set when permission override is allowed after NT ACL checks.

Dependencies and integration points: uses winbind ID mapping, Samba security descriptor helpers, security tokens/privileges, root privilege elevation, PVFS name resolution, xattr ACL load/save, and bracketing share flags.

Risks: this is security-critical. SID/XID mapping failures, privilege escalation handling, read-only enforcement, delete-child semantics, ACL fallback to Unix mode, and inheritance flag handling must match Windows expectations. Test signals include default ACL from modes, ACL set/query round trips, owner/group chown with and without privileges, NT ACL versus Unix fallback checks, SMB1/SMB2 access-mask differences, inheritance RAW-ACLS cases, and maximal-access results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_acl_nfs4.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_acl_nfs4.c

Purpose: registers a PVFS ACL backend named `nfs4acl` that stores NT-style security descriptors in the `system.nfs4acl` NDR xattr format and translates between NFSv4 ACE IDs and Samba SIDs.

Important APIs and functions: `pvfs_acl_load_nfs4` reads `NFS4ACL_NDR_XATTR_NAME`, maps file owner/group and ACE UID/GID values to SIDs, and builds a `security_descriptor`. `pvfs_acl_save_nfs4` maps ACE trustee SIDs to Unix IDs and writes a `struct nfs4acl`. `pvfs_acl_nfs4_init` registers the backend with `pvfs_acl_register`. `ACE4_IDENTIFIER_GROUP` marks group principals.

Control flow: load allocates an NFS4 ACL object, calls `pvfs_xattr_ndr_load`, initializes an SD, prepares an `id_map` array for owner, group, and each ACE, calls `wbc_xids_to_sids`, assigns owner/group SIDs, and appends DACL ACEs. Save initializes NFS4 metadata from the SD, duplicates each trustee SID, calls `wbc_sids_to_xids`, fills ACE type/flags/mask/id, elevates with `root_privileges`, and writes with `pvfs_xattr_ndr_save`.

State and persistence: ACLs persist as NDR-encoded xattrs. Owner/group SIDs are reconstructed from current file `stat` UID/GID on load; ACEs persist their numeric IDs and group flag.

Dependencies and integration points: depends on PVFS xattr NDR helpers, generated NFS4 ACL NDR code, winbind ID mapping, security descriptor helpers, and root privilege elevation.

Risks: mapping failures block load/save; non-UID trustee mappings are saved as group ACEs; xattr write requires privilege; only DACL ACEs are represented. Test signals include load/save round trips, group ACE flag preservation, owner/group reconstruction, invalid or missing xattr handling, and permission failures on system xattrs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_acl_nfs4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_acl_xattr.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_acl_xattr.c

Purpose: registers a PVFS ACL backend named `xattr` that stores Samba `xattr_NTACL` security descriptors in native filesystem xattrs.

Important APIs and functions: `pvfs_acl_load_xattr` checks `PVFS_FLAG_XATTR_ENABLE`, reads `XATTR_NTACL_NAME` via `pvfs_xattr_ndr_load`, validates version `1`, and returns the embedded security descriptor. `pvfs_acl_save_xattr` wraps the SD in version `1`, elevates privileges, and writes via `pvfs_xattr_ndr_save`. `pvfs_acl_xattr_init` registers the backend.

Control flow: disabled xattrs behave as `NT_STATUS_NOT_FOUND`, allowing callers to fall back to default Unix-derived ACLs. Load failures free the temporary ACL wrapper. Save is a no-op success when xattrs are disabled; otherwise it writes to the system namespace under root privileges.

State and persistence: persisted state is the NDR-encoded `xattr_NTACL` xattr on each file. No process-global state exists except backend registration.

Dependencies and integration points: called through `pvfs_acl_ops` from `pvfs_acl.c`; depends on PVFS xattr helpers, generated `ndr_xattr` support, and privilege elevation.

Risks: disabled xattrs silently skip persistence on save; invalid versions return `NT_STATUS_INVALID_ACL`; root privilege boundaries and system-xattr support vary by platform. Test signals include disabled-xattr fallback, missing xattr, invalid version, save/load round trip, privilege failure, and integration with `pvfs_acl_query`/`pvfs_acl_set`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_acl_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_dirlist.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_dirlist.c

Purpose: implements PVFS directory enumeration, wildcard matching, resume offsets, name-based seeks, and directory-empty checks.

Important APIs and types: `struct pvfs_dir` tracks open DIR handle, wildcard pattern, fake/real offsets, cached names, and end-of-search state. Public functions include `pvfs_list_start`, `pvfs_list_next`, `pvfs_list_unix_path`, `pvfs_list_eos`, `pvfs_list_seek`, `pvfs_list_seek_ofs`, and `pvfs_directory_empty`. `dcache_add` maintains a 100-entry resume cache.

Control flow: `pvfs_list_start` splits the resolved Unix path into directory plus pattern. Non-wildcard searches use `pvfs_list_no_wildcard` and avoid `opendir`; wildcard searches open the directory, initialize fake offsets for `.` and `..`, and allocate the cache. `pvfs_list_next` returns dot entries first if they match, then scans `readdir`, skipping dot entries, matching long names or generated short names, and maps `telldir` offsets by adding `DIR_OFFSET_BASE`. Seek operations first consult special dot offsets and the cache, then rescan from the start.

State and persistence: state is per-search and talloc-scoped; the destructor closes `DIR *`. No persistent state is written.

Dependencies and integration points: uses PVFS name resolution output, `ms_fnmatch_protocol`, short-name generation, POSIX directory APIs, and protocol selection from the NTVFS context.

Risks: resume offsets are inherently OS-dependent, so fake base constants avoid collisions with observed end-of-directory values; non-wildcard path handling mutates `name->full_name` at the final slash; short-name matching adds cost. Test signals include wildcard/no-wildcard enumeration, dot ordering, protocol-specific matching, resume by name and offset, cache wraparound, empty-directory behavior, and platforms with unusual `telldir` values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_dirlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_fileinfo.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_fileinfo.c

Purpose: converts POSIX `stat` data and PVFS share flags into DOS/NT file metadata and computes Unix permissions for new files/directories.

Important APIs and functions: `dos_mode_from_stat` maps Unix mode bits to DOS readonly/archive/system/hidden/directory attributes. `pvfs_fill_dos_info` populates `pvfs_filename.dos` timestamps, attributes, allocation size, link count, EA size, file ID, xattr-backed DOS attributes, and open-database write-time overrides. `pvfs_fileperms` derives creation mode from requested DOS attributes plus share masks and force modes.

Control flow: directories are forced to size `0` and link count `1`; default stream names are cleared for base files. Timestamps are converted to NT time and augmented with nanoseconds. `pvfs_dosattrib_load` can override simple stat-derived attributes. Unless `PVFS_RESOLVE_NO_OPENDB` is set, the file locking key is queried in the open database and a non-null ODB write time overrides stat mtime. Permission creation starts from broad read/write bits, maps DOS attributes into execute bits only when native xattrs are disabled, and then applies create/dir masks and force modes.

State and persistence: this file reads persistent stat/xattr/ODB state but mostly fills in-memory `pvfs_filename` fields. New-file modes later become persistent through create/mkdir/open operations.

Dependencies and integration points: used by PVFS resolve/info/open paths. Depends on time helpers, DOS attribute xattr loading, allocation rounding, locking-key generation, and ODB file info.

Risks: attribute mapping changes when xattrs are enabled; SMB2 EA size differs from SMB1; ODB errors are logged and returned; file ID combines device and inode. Test signals include mapped archive/system/hidden bits, readonly mode creation with and without xattrs, nanosecond timestamp precision, ODB write-time override, and directory metadata normalization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_fileinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_flush.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_flush.c

Purpose: implements SMB flush semantics for PVFS open files, optionally syncing file descriptors to disk when strict sync is enabled.

Important APIs and functions: `pvfs_flush_file` calls `fsync` on a file handle if it has a real fd and `PVFS_FLAG_STRICT_SYNC` is set. `pvfs_flush` handles `RAW_FLUSH_FLUSH`, `RAW_FLUSH_SMB2`, and `RAW_FLUSH_ALL`.

Control flow: single-file flush resolves the NTVFS handle with `pvfs_find_fd`, rejects invalid handles, calls `pvfs_flush_file`, initializes SMB2 reserved output, and returns OK. Flush-all returns OK immediately unless strict sync is enabled; when enabled it iterates all open PVFS files and flushes those whose stored SMB PID matches the request.

State and persistence: no state is stored. With strict sync, dirty kernel state may be persisted to disk via `fsync`. Without strict sync, flush is effectively acknowledged without forcing storage.

Dependencies and integration points: depends on PVFS file tracking and share flags. Used by NTVFS flush dispatch for SMB1/SMB2 callers.

Risks: `fsync` errors are ignored; directories or non-fd handles are skipped by `pvfs_flush_file`; flush-all filters by SMB PID rather than session. Test signals include invalid handle, SMB2 reserved output, strict-sync off no-op, strict-sync on `fsync` invocation, and flush-all PID filtering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_fsinfo.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_fsinfo.c

Purpose: answers filesystem information queries for PVFS shares, including space usage, volume labels, attributes, quotas, object IDs, and sector size.

Important APIs and functions: `pvfs_fsinfo` is the main dispatcher. `pvfs_blkid_fs_uuid` optionally obtains a filesystem UUID through libblkid. `pvfs_cache_base_fs_uuid` caches the base filesystem GUID in `pvfs->base_fs_uuid`.

Control flow: only space-related info levels call `sys_statvfs`; all levels stat the base directory for device/inode/time. DSKATTR scales block counts to fit legacy fields and caps old LANMAN clients at 2 GiB. Allocation/size/full-size levels return statvfs-derived counts with 512-byte sectors. Volume levels use base inode as serial and share name as label. Attribute info returns PVFS filesystem attributes and NTVFS fs type. Object ID zeroes fields, caches the UUID, and returns it. Sector-size info reports aligned 512-byte logical/physical sectors.

State and persistence: reads filesystem state via stat/statvfs and caches the base UUID in memory. No persistent writes occur.

Dependencies and integration points: used by NTVFS fsinfo dispatch. Depends on PVFS share state, libndr GUID parsing, optional libblkid, statvfs compatibility helpers, and protocol version.

Risks: reports fixed 512-byte sectors regardless of actual hardware; UUID lookup may silently return zero GUID; statvfs is skipped for levels that do not need it; LANMAN compatibility intentionally clips values. Test signals include every query level, stat/statvfs failure mapping, object ID with and without libblkid, LANMAN DSKATTR cap, share-name volume label, and invalid generic/unknown levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_fsinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_ioctl.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_ioctl.c

Purpose: handles PVFS ioctl requests with minimal supported behavior, mostly returning compatibility statuses.

Important APIs and functions: `pvfs_ioctl` dispatches by raw ioctl level. `pvfs_ioctl_old` returns a DOS server error for the old ioctl interface. `pvfs_ntioctl` validates an open file handle and supports `FSCTL_SET_SPARSE` as a successful no-op with an empty output blob.

Control flow: old SMB ioctl returns `ERRSRV/ERRerror`. NT ioctl resolves the file via `pvfs_find_fd`, rejects invalid handles, recognizes sparse-file marking, and otherwise returns `NT_STATUS_NOT_SUPPORTED`. SMB2 ioctl with or without a handle returns `NT_STATUS_INVALID_DEVICE_REQUEST` to satisfy compatibility tests.

State and persistence: no persistent state is changed. `FSCTL_SET_SPARSE` does not mark sparse state on disk.

Dependencies and integration points: called through the NTVFS POSIX backend ioctl callback and uses SMB constants plus PVFS file lookup.

Risks: sparse support is only nominal; callers expecting actual sparse allocation behavior will not get it. SMB2 returns a deliberately different status from NT ioctl unsupported cases. Test signals include invalid handle, successful `FSCTL_SET_SPARSE` empty blob, unsupported NT functions, old ioctl DOS status, SMB2 invalid-device status, and invalid level handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_lock.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_lock.c

Purpose: implements byte-range locking for PVFS, including strict I/O lock checks, synchronous and timed async locks, unlocks, cancellation, close cleanup, and oplock release forwarding.

Important APIs and types: `pvfs_check_lock` tests I/O ranges when strict locking is enabled. `struct pvfs_pending_lock` tracks timed lock requests. Public operations are `pvfs_lock`, `pvfs_lock_close`, and internal helpers `pvfs_pending_lock_continue`, `pvfs_lock_async_failed`, and `pvfs_lock_cancel`.

Control flow: non-generic lock levels are mapped with `ntvfs_map_lock`. Generic lock dispatch handles oplock release, validates file handle and non-directory fd, breaks level-2 oplocks, creates pending state for nonzero timeouts when async is allowed, processes unlocks first, then attempts locks through `brlock_lock`. On immediate failure it rolls back acquired locks. For timed locks it registers a `pvfs_wait_message` for `MSG_BRL_RETRY` until retry, timeout, or cancel; continuation retries and either completes, requeues, or rolls back. Close removes all brlocks and replies to pending requests with range-not-locked.

State and persistence: lock state lives in Samba brlock context and per-file `lock_count`/`pending_list`. It is transient server coordination state, not persistent filesystem metadata.

Dependencies and integration points: uses brlock subsystem, messaging, wait helpers, NTVFS async state, PVFS file handles, and oplock break/release code.

Risks: rollback correctness is critical for multi-lock batches; cancel requires exact match; SMB1 and SMB2 cancellation statuses differ; pending lock lifetime is tied to file and wait handles; strict-locking off bypasses read/write lock checks. Test signals include lock/unlock ordering, failed-batch rollback, timed lock retry/timeout/cancel, close with active locks, directory lock rejection, shared/exclusive mapping, strict-lock I/O checks, and oplock release path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_mkdir.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_mkdir.c

Purpose: implements directory creation and removal for PVFS, including T2 mkdir with EAs, access checks, inherited ACL setup, xattr cleanup hooks, and change notifications.

Important APIs and functions: `pvfs_mkdir` handles normal `RAW_MKDIR_MKDIR` and delegates `RAW_MKDIR_T2MKDIR` to `pvfs_t2mkdir`. `pvfs_rmdir` removes directories. Both rely on `pvfs_resolve_name`, `pvfs_access_check_parent` or `pvfs_access_check_simple`, `pvfs_fileperms`, `pvfs_sys_mkdir`, `pvfs_sys_rmdir`, `pvfs_acl_inherit`, `pvfs_xattr_unlink_hook`, and `notify_trigger`.

Control flow: mkdir resolves the CIFS path, rejects existing targets, checks parent add rights, computes directory mode, creates the directory, clears stale xattr state for the path, applies inherited ACLs, and triggers directory-added notification. T2 mkdir repeats that flow, re-resolves after creation, verifies the result is a directory, applies inherited ACLs, then writes requested EAs; failures after creation remove the directory. Rmdir resolves the path, checks existence, verifies delete access, runs xattr unlink hook, calls rmdir, maps `EEXIST` to directory-not-empty, and triggers removal notification.

State and persistence: creates/removes real directories, writes inherited ACL/xattr/EA state through helper calls, and emits notify events. Rollback tries to remove partially created directories on ACL/EA failure.

Dependencies and integration points: integrates PVFS path resolution, ACL, xattr, EA, POSIX syscall wrappers, permission override, and notification subsystems.

Risks: mkdir checks `SEC_DIR_ADD_FILE` rather than add-subdir; stale xattr cleanup is required after path reuse; T2 mkdir rollback must handle partial metadata writes; rmdir maps platform-specific errors. Test signals include existing target, access denied, ACL inheritance failure rollback, T2 EA failure rollback, stale xattr cleanup, notify added/removed events, directory-not-empty mapping, and invalid mkdir levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_mkdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_notify.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_notify.c

Purpose: implements change notify for open PVFS directory handles. It buffers notify events, manages pending requests, handles overflow, and maps SMB2 notify through the generic NTVFS mapper.

Important APIs and types: `struct pvfs_notify_buffer` is attached to `struct pvfs_file` for directory handles and stores changes, pending requests, max buffer size, current encoded size, and overflow state. Main functions are `pvfs_notify`, `pvfs_notify_setup`, `pvfs_notify_callback`, `pvfs_notify_send`, `pvfs_notify_end`, and the destructor `pvfs_notify_destructor`.

Control flow: `pvfs_notify` maps non-NTTRANS levels, resolves the directory handle, requires async-capable requests, rejects non-directory fds, creates a notify buffer if needed, queues the request, and either waits for future events or sends buffered changes asynchronously. `pvfs_notify_setup` registers with `notify_add` using recursive filter settings. The callback appends events, converts `/` to `\\`, estimates encoded length, and sends immediately except for old-name rename halves. `pvfs_notify_send` handles overflow by returning no changes and draining waiters, steals changes into the request, sets status, and either sends immediately or schedules next-event-loop send to avoid freeing active requests.

State and persistence: notify buffers are transient per open directory handle. Events are stored in memory until delivered or overflowed. The destructor unregisters from notify context and wakes pending requests.

Dependencies and integration points: depends on Samba notify context, PVFS wait/cancel messaging, tevent timers, dlink lists, and NTVFS async state. Directory mutation code such as mkdir/rmdir triggers events consumed here.

Risks: notify requires async permission; buffer overflow deliberately returns an empty change list; recursive/filter settings are not updated after initial setup except buffer size; old-name rename events are held until paired. Test signals include invalid handle, non-directory rejection, async-required behavior, event delivery, overflow drain, cancellation status, close cleanup, SMB2 mapping, recursive filter behavior, and rename old/new sequencing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_notify.c -->
