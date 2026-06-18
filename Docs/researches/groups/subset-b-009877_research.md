# subset-b-009877 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_session.c -->
# sources/user-network-fs/samba/source3/smbd/smbXsrv_session.c

## Purpose
Implements Samba smbd's SMB1/SMB2 session lifecycle. It creates local session objects, persists cluster-visible global session records, handles multi-channel attachment/removal, coordinates SMB2 previous-session closure, shuts sessions down without racing outstanding requests, and exposes lookup/traversal helpers used by request validation and status enumeration.

## Important APIs, Types, and Functions
- `struct smbXsrv_session_table` owns a local in-memory `dbwrap_rbt` table of `local_id -> struct smbXsrv_session *` plus a shared global `smbXsrv_session_global.tdb`.
- `smbXsrv_session_global_init()` opens the volatile watched global TDB with mode `0600` because records contain session keys.
- `smbXsrv_session_create()`, `smbXsrv_session_add_channel()`, `smbXsrv_session_update()`, `smbXsrv_session_remove_channel()`, and `smbXsrv_session_logoff()` form the main lifecycle.
- `smb1srv_session_*` and `smb2srv_session_*` wrappers provide protocol-specific ID ranges and lookup semantics.
- `smb2srv_session_shutdown_send/recv()` implements async cancellation/waiting for in-flight requests and lease-break waits.
- `smb2srv_session_close_previous_send/recv()` uses watched dbwrap records plus messaging to close a previous authenticated SMB2 session for the same user SID.
- `smbXsrv_session_global_traverse()` and `smbXsrv_session_local_traverse()` expose enumeration hooks.

## Control Flow
Global init creates a watched dbwrap wrapper over `smbXsrv_session_global.tdb`; per-client table init creates a local rbt db and starts a persistent `messaging_read_send()` loop for `MSG_SMBXSRV_SESSION_CLOSE`. Creating a session allocates a local object, reserves a random global 32-bit ID, selects SMB2 wire IDs directly from the global ID or SMB1 IDs from the bounded local range, creates the SMB2 tcon table when needed, adds the initial channel, stores a local pointer record, then NDR-serializes the global record. Lookups parse local pointer records, reject deleted/expired sessions, and optionally verify the incoming connection is still a registered channel.

Shutdown marks the session `NT_STATUS_USER_SESSION_DELETED`, cancels other pending SMB2 subrequests, queues waiters until those requests drain, and waits for delete-on-close handle lease breaks. Logoff closes files by user ID, disconnects SMB2 tcons, invalidates the vuid, deletes global and local records, and decrements the local count. Multi-channel removal deletes pending auth/channel entries; if the last channel disappears, it starts async session shutdown and keeps the transport shutdown queue blocked until the session object is freed.

## State and Persistence
Local session state is process-local and stores raw pointers in the rbt db, so it is valid only in the owning smbd process. Global state is volatile TDB under the lock path, NDR encoded as `smbXsrv_session_globalB`, carries a sequence number, server IDs, channel metadata, auth session info, and secret key blobs. The verifier treats empty or stale records as free and deletes records whose primary channel server ID no longer exists. Secret blobs are marked with `talloc_keep_secret()`.

## Dependencies and Integration Points
Depends on dbwrap/rbt/watched TDB, messaging, serverid liveness, tevent, NDR generated `smbXsrv` types, gensec expiration constants, SMB2 signing/cipher constructors, share-mode/lease-break helpers, file close helpers, and tcon lifecycle from `smbXsrv_tcon.c`. It is used by SMB request validation, UID switching through `smbXsrv_session_info_lookup()`, SRVSVC-style global traversal, and SMB2 session setup/logoff paths.

## Risks
The local table stores raw pointers, so db corruption or misuse outside object lifetime is fatal. Session records include secrets and must remain `0600` and volatile. Correctness depends on dbwrap record locks and watched-record fairness in previous-session closure. Async shutdown must avoid cancelling the current request while guaranteeing all other requests and lease breaks drain. The code has many status-specific branches; treating `MORE_PROCESSING_REQUIRED`, expired, and deleted sessions interchangeably would break authentication or request validation.

## Test Signals
Exercise SMB1 and SMB2 login/logoff, invalid/zero/high-bit session IDs, session expiration, multi-channel disconnects, previous-session reconnect for the same SID, server crash cleanup of stale global records, and request cancellation during logoff. Tests should also inspect that global TDB records are removed on logoff and that uid switching can retrieve `auth_session_info` only after authentication completes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_session.h -->
# sources/user-network-fs/samba/source3/smbd/smbXsrv_session.h

## Purpose
Public interface for smbd session management. It hides the internal table/global-record implementation while exposing session creation, authentication tracking, lookup, shutdown, logoff, traversal, previous-session closure, and lease-break wait helpers.

## Important APIs, Types, and Functions
Forward-declares `messaging_context`, `smbXsrv_client`, `smbXsrv_connection`, `smbXsrv_session`, `smbXsrv_session_global0`, `smbXsrv_channel_global0`, and `smbXsrv_session_auth0`. Exports `smbXsrv_session_global_init()`, `smbXsrv_session_create()`, `smbXsrv_session_add_channel()`, `smbXsrv_session_remove_channel()`, lookup helpers for SMB1/SMB2/global/local contexts, `smbXsrv_session_info_lookup()`, `get_valid_smbXsrv_session()`, traversal callbacks, async shutdown, async close-previous, and `smbXsrv_wait_for_handle_lease_break()`.

## Control Flow
Callers initialize protocol-specific tables after negotiation, create sessions during session setup, create pending auth records for in-progress authentication, update global records once keys/auth state change, and use lookup wrappers to validate incoming request session IDs. Logoff and disconnect paths call the exported shutdown/logoff/remove-channel routines. Internal consumers can traverse local or global session records through callback-based APIs.

## State and Persistence
The header itself owns no state, but its API boundary distinguishes local live process state from global persisted state. `smbXsrv_session_info_lookup()` intentionally exposes authenticated session info to consumers such as UID switching, while `get_valid_smbXsrv_session()` is documented as an internal post-validation helper rather than a request validator.

## Dependencies and Integration Points
Includes `replace.h`, `tevent.h`, NTSTATUS utilities, and time types. Its types are completed by smbd global/session structures and generated NDR headers in implementation files. It is included by UID handling, request processing, SMB2 session setup/logoff, connection teardown, and service enumeration code.

## Risks
The API has similarly named lookup helpers with different validation strength. Using `get_valid_smbXsrv_session()` for wire request validation would bypass channel/status checks. Async APIs require callers to follow tevent ownership and recv conventions. Functions returning borrowed session/auth info depend on live session object lifetime.

## Test Signals
Compile-time coverage should catch signature drift across smbd callers. Runtime coverage should validate that SMB1, SMB2 connection-local, client-local, and global lookups return distinct expected statuses for deleted, unauthenticated, expired, and wrong-channel sessions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_tcon.c -->
# sources/user-network-fs/samba/source3/smbd/smbXsrv_tcon.c

## Purpose
Implements tree-connection lifecycle for smbd. A tcon represents a client connection to a share; this file allocates IDs, stores global tcon records for server-wide enumeration, maps local IDs to live tcon pointers, updates records, and disconnects one or all tcons for SMB1 clients or SMB2 sessions.

## Important APIs, Types, and Functions
- `struct smbXsrv_tcon_table` mirrors the session table pattern with local rbt and global volatile TDB stores.
- `smbXsrv_tcon_global_init()` opens `smbXsrv_tcon_global.tdb`.
- `smbXsrv_tcon_create()`, `smbXsrv_tcon_update()`, and `smbXsrv_tcon_disconnect()` implement lifecycle.
- `smb1srv_tcon_table_init/create/lookup/disconnect_all()` operate on the client-level SMB1 table.
- `smb2srv_tcon_table_init/create/lookup/disconnect_all()` operate under an SMB2 session.
- `smbXsrv_tcon_global_traverse()` enumerates global records as `smbXsrv_tcon_global0`.

## Control Flow
Table initialization validates ID bounds, opens an rbt local table, and attaches the shared global TDB. Creation allocates a random global ID, stores share name, session global ID, encryption flags, server ID, creation time, and protocol-specific wire/local IDs, then stores a local pointer record and NDR-encoded global record. SMB1 uses 16-bit local tree IDs; SMB2 uses the low 32-bit global ID while keeping the maximum live tcon count aligned with SMB1.

Disconnect first closes the compatibility `connection_struct` with `close_cnum()` after changing to the service directory, marks the tcon deleted, deletes the global and local records, and decrements the count. Disconnect-all traverses local records, extracts each live pointer, selects the right vuid, and calls the single-disconnect path.

## State and Persistence
Local state is an in-memory pointer table scoped to a client or session. Global state is volatile TDB encoded as `smbXsrv_tcon_globalB`, storing IDs, share name, server ID, encryption flags, and sequence number. Verification removes stale records when the owning server ID no longer exists. The compatibility connection pointer links tcon lifetime to the older service/connection layer.

## Dependencies and Integration Points
Depends on dbwrap/rbt/open, generated NDR `smbXsrv` types, serverid liveness, messaging server IDs, service close/chdir helpers, and session lifecycle. SMB2 session logoff calls `smb2srv_tcon_disconnect_all()`, and SMB1 client teardown calls `smb1srv_tcon_disconnect_all()`.

## Risks
As with sessions, local records store raw pointers and require strict object lifetime. Disconnect must always call `close_cnum()` when `compat` exists, even after `chdir_current_service()` failure, otherwise the connection list can retain a soon-to-be-freed pointer. Global verification does not mark malformed records free in all branches, so corrupt TDB records may cause allocation pressure or traversal warnings. SMB1 tcons may have stale or wrong vuids, a behavior explicitly preserved for compatibility.

## Test Signals
Test SMB1/SMB2 tree connect and disconnect, tcon ID exhaustion, stale global records after process death, disconnect-all on session logoff, share close failure paths, and global traversal output for active shares. Include coverage for encrypted share flags and share-name persistence in global records.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_tcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_version.c -->
# sources/user-network-fs/samba/source3/smbd/smbXsrv_version.c

## Purpose
Maintains a cluster-visible version gate for smbd internal `smbXsrv_*_global` record formats. It prevents nodes with incompatible supported structure versions from concurrently reading and writing volatile internal databases.

## Important APIs, Types, and Functions
`smbXsrv_version_global_init(const struct server_id *server_id)` opens `smbXsrv_version_global.tdb`, validates existing version records, filters dead nodes, records the local node's min/max/current version, stores the updated NDR blob, and caches the current version. `smbXsrv_version_global_current()` returns that cached version for session and tcon global stores.

## Control Flow
Initialization opens the TDB with `TDB_CLEAR_IF_FIRST` and incompatible hash flags, locks the fixed key `smbXsrv_version_global`, creates an empty version object if missing, or parses and validates an existing object. Each live node must advertise a range containing the global blob version; otherwise startup fails with corruption or revision mismatch. The local node entry is found by VNN or appended, then the record sequence number is incremented and stored.

## State and Persistence
State lives in volatile lock-path TDB and is cached process-wide in `smbXsrv_version_global_db_ctx` and `smbXsrv_version_global_current_version`. The global record stores node server IDs and version ranges; dead server IDs are pruned during init.

## Dependencies and Integration Points
Depends on dbwrap, TDB, generated NDR `smbXsrv_version_globalB`, serverid liveness, and lock-path helpers. Session and tcon stores call `smbXsrv_version_global_current()` to stamp their record version.

## Risks
Passing a null or stale `server_id` would undermine the node compatibility gate. If version init is skipped before session/tcon stores, `UINT32_MAX` could leak as the current version. Strict failure on range mismatch protects data but can block startup during rolling upgrades unless migration glue is added.

## Test Signals
Test first-node initialization, restart with existing compatible records, pruning dead nodes, rejection of min/max ranges that exclude current version, malformed NDR blobs, unsupported blob versions, and use of the cached version in session/tcon stores.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbd.h -->
# sources/user-network-fs/samba/source3/smbd/smbd.h

## Purpose
Central smbd header that pulls together VFS, generated prototypes, locking, file-handle, and SMB1-specific declarations. It also defines transaction state and flags for Unix path conversion behavior.

## Important APIs, Types, and Functions
`struct trans_state` tracks SMB transaction/trans2/nttrans aggregation: vuid, MID, return limits, command/call fields, setup words, accumulated parameter/data buffers, and completion behavior. Defines `UCF_POSIX_PATHNAMES`, `UCF_PREP_CREATEFILE`, `UCF_LCOMP_LNK_OK`, `UCF_GMT_PATHNAME`, and `UCF_DFS_PATHNAME` for `unix_convert`-style path processing.

## Control Flow
This header has no executable flow. It shapes compile-time inclusion for smbd modules, conditionally includes SMB1 server headers, and gives path-conversion callers shared flag constants.

## State and Persistence
`trans_state` instances are runtime request state, usually linked in per-connection lists and freed after transaction completion. The path flags are stateless compile-time constants.

## Dependencies and Integration Points
Includes `vfs.h`, `smbd/proto.h`, locking prototypes, share-mode locks, and fd handles. SMB1 includes are guarded by `WITH_SMB1SERVER`, making this header a compatibility aggregation point for older protocol code.

## Risks
Because this header is broad, changes can trigger widespread rebuilds and subtle include-order issues. Transaction buffer fields carry byte counts and pointers, so users must validate total/received lengths. Path flags intentionally reuse SMB flag bits for GMT and DFS pathnames, so accidental value changes can alter wire-visible behavior.

## Test Signals
Build both with and without `WITH_SMB1SERVER`. Exercise transaction request assembly and path conversion modes for POSIX, DFS, GMT, symlink-last-component, and create-file preparation cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbd_cleanupd.c -->
# sources/user-network-fs/samba/source3/smbd/smbd_cleanupd.c

## Purpose
Implements the smbd cleanup daemon request. It listens for shutdown and cleanup notifications, drains child cleanup records, removes stale child entries, cleans profiling and messaging resources, and completes its tevent request on shutdown.

## Important APIs, Types, and Functions
`smbd_cleanupd_send()` creates state and registers handlers for `MSG_SHUTDOWN` and `MSG_SMB_NOTIFY_CLEANUP`. `smbd_cleanupd_shutdown()` completes the request. `smbd_cleanupd_process_exited()` traverses `cleanupdb`, collects child PID records, then performs cleanup outside the traverse. `smbd_cleanupd_recv()` follows the standard tevent recv pattern.

## Control Flow
The send function returns an in-progress tevent request after message registration. On cleanup notification, the handler traverses `cleanupdb` read-only into a temporary linked list, avoiding writer interactions while locked. It then deletes each child record, calls `smbprofile_cleanup(child_pid, parent_pid)`, runs `messaging_cleanup()`, tolerates `ENOENT`, logs, and frees the frame.

## State and Persistence
Persistent input is `cleanupdb`, which records child PIDs and an `unclean` flag. Runtime state stores only the parent PID. Cleanup removes records and messaging/profile leftovers associated with dead children.

## Dependencies and Integration Points
Depends on Samba messaging, tevent NTSTATUS helpers, `cleanupdb`, server ID/process utilities, smbd profiling cleanup, and locking prototypes. It is triggered by parent/child smbd process management when workers exit.

## Risks
Cleanup runs asynchronously in response to messages; missed notifications can leave records until the next notification. Failure to delete cleanupdb records is logged but does not stop other child cleanup. The `unclean` flag is collected but not used here, so any differentiated cleanup policy must live elsewhere or be added carefully.

## Test Signals
Test message registration failures, shutdown completion, cleanup of multiple child records, cleanupdb traverse failure, deletion failure logging, idempotent behavior when messaging cleanup returns `ENOENT`, and profile cleanup with the expected parent PID.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbd_cleanupd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbd_cleanupd.h -->
# sources/user-network-fs/samba/source3/smbd/smbd_cleanupd.h

## Purpose
Declares the async cleanup daemon API used by smbd process-management code.

## Important APIs, Types, and Functions
Exports `smbd_cleanupd_send(TALLOC_CTX *, tevent_context *, messaging_context *, pid_t parent_pid)` and `smbd_cleanupd_recv(struct tevent_req *)`. Includes `replace.h`, `tevent.h`, and `messages.h`.

## Control Flow
Callers start cleanup handling by invoking `send`, keep the request alive while the daemon should process messages, and call `recv` after request completion, normally after shutdown.

## State and Persistence
No direct state. The implementation retains parent PID in request state and uses cleanupdb/messaging state outside the header.

## Dependencies and Integration Points
The signature ties cleanupd to Samba's tevent request model and messaging subsystem. It is integrated wherever the parent smbd starts helper daemons or message-driven maintenance tasks.

## Risks
Consumers must preserve the returned request lifetime because message registrations use it as private data. Calling `recv` before completion follows tevent semantics and should be avoided.

## Test Signals
Compile consumers against the send/recv signatures and exercise start/shutdown paths through the implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbd_cleanupd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/srvstr.c -->
# sources/user-network-fs/samba/source3/smbd/srvstr.c

## Purpose
Provides a server-specific safe string push helper for encoding strings into SMB response buffers while mapping conversion errors to appropriate NTSTATUS values.

## Important APIs, Types, and Functions
`srvstr_push_fn()` wraps `push_string_base()`, accepts SMB flags, destination pointer/length, source string, conversion flags, and returns the encoded length through `ret_len`.

## Control Flow
The function rejects negative destination lengths, preserves the caller's `errno`, clears `errno`, calls `push_string_base()`, and interprets any resulting errno. Character conversion failures (`E2BIG`, `EILSEQ`, `EINVAL`) become `NT_STATUS_ILLEGAL_CHARACTER`; other errors are mapped through Unix-to-NT conversion, with `STATUS_MORE_ENTRIES` filtered to `NT_STATUS_UNSUCCESSFUL`. On success, it restores the saved errno and returns the pushed byte count.

## State and Persistence
No persistent state. It mutates the destination buffer and temporarily manipulates process-local `errno`.

## Dependencies and Integration Points
Depends on `push_string_base()` from string wrappers, SMB flags2 encoding behavior, Unix errno mapping, and smbd globals/includes. Used by SMB response construction paths that need bounded OEM/Unicode string encoding.

## Risks
Because success restores errno, callers must rely on NTSTATUS rather than errno after success. Conversion failures expose source string in debug logs. Incorrect `base_ptr` or flags can still produce protocol encoding bugs even with length protection.

## Test Signals
Test Unicode/OEM conversions, zero-length and negative destination lengths, too-small buffers, illegal byte sequences, errno preservation on success, and non-conversion errno mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/srvstr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/uid.c -->
# sources/user-network-fs/samba/source3/smbd/uid.c

## Purpose
Manages effective Unix/NT security context switching for smbd request handling. It validates share access for a session, caches per-vuid connection authorization state, applies force group/admin user semantics, switches to users or root, and exposes current effective token accessors.

## Important APIs, Types, and Functions
`change_to_guest()`, `check_user_share_access()`, `change_to_user_and_service()`, `change_to_user_and_service_by_fsp()`, `smbd_change_to_root_user()`, `smbd_become_authenticated_pipe_user()`, `smbd_unbecome_authenticated_pipe_user()`, `smbd_become_root()`, `smbd_unbecome_root()`, `become_user_without_service*()`, `unbecome_user_without_service()`, and `get_current_uid/gid/utok/nttok()` form the exported behavior. Internally, `check_user_ok()` populates the vuid cache and `change_to_user_impersonate()` applies the selected session token.

## Control Flow
Request paths lookup `auth_session_info` via `smbXsrv_session_info_lookup()`, call `change_to_user_impersonate()`, then optionally `chdir_current_service()`. `check_user_ok()` first reuses a matching vuid cache entry, otherwise validates `valid users`/share ACL/read-only state, calculates share access, handles admin users by mapping to initial uid, builds veto/hide lists including token-qualified parametric entries, and stores the result in a ring cache. Impersonation applies force group rules, updates the Unix token/security token group SID when forced, calls `set_sec_ctx()`, and updates global `current_user`.

Root and temporary user transitions push both the security context stack and a parallel connection context stack; pop restores current user metadata. Pipe impersonation uses only the security context stack and intentionally does not modify `current_user`.

## State and Persistence
Runtime state includes global `current_user`, `conn->session_info`, `conn->vuid_cache`, veto/hide lists, connection read-only/share access flags, and the connection context stack. No on-disk persistence is performed. Decisions are derived from smb.conf, passdb/session tokens, and share security descriptors.

## Dependencies and Integration Points
Depends on passdb lookups, auth/session info, security tokens and privileges, Samba loadparm substitution/parametrics, share access helpers, `smbXsrv_session_info_lookup()`, current security context stack helpers, and service chdir. It is central to VFS calls, file operations, named pipe operations, and SMB request execution.

## Risks
Incorrect stack push/pop pairing can leave smbd running as root or the wrong user. Vuid cache ownership is subtle because `conn->session_info` may point into cache entries; `free_conn_state_if_unused()` prevents double/free-live state mistakes. Force group changes mutate token fields and must stay consistent with SID updates. `UID_FIELD_INVALID` is deliberately allowed for internal no-service impersonation, but using it on wire-authenticated paths would weaken cache semantics.

## Test Signals
Test valid/invalid vuid switching, share ACL denial, read-only fallback from security descriptor, admin users, force group with and without `+`, dynamic force-group config changes on existing connections, veto/hide parametric entries matching token names, nested become/unbecome root/user calls, pipe impersonation, and current token accessors inside root override blocks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/uid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/utmp.c -->
# sources/user-network-fs/samba/source3/smbd/utmp.c

## Purpose
Reflects Samba connection claim/yield events into platform utmp/wtmp or utmpx/wtmpx accounting files when compiled with `WITH_UTMP`. Provides no-op stubs otherwise.

## Important APIs, Types, and Functions
Exports `sys_utmp_claim()` and `sys_utmp_yield()`. Internal helpers include `uw_pathname()` for configured/default file paths, `utmp_nox_update()` for utmp/wtmp APIs, `sys_utmp_update()` for utmpx-preferred updates, `utmp_strcpy()` for fixed-size fields, `ut_id_encode()` for four-byte IDs, and `sys_utmp_fill()` for portable struct population.

## Control Flow
Without `WITH_UTMP`, claim/yield immediately return. With utmp enabled, claim/yield zero a `struct utmp`, set user/dead process type where available, fill username, host, line, pid, timestamp, and encoded ID, then call `sys_utmp_update()`. The update path prefers utmpx only when all required APIs and paths are available; otherwise it falls back to utmp/wtmp. Wtmp without `updwtmp()` appends records directly and truncates back on partial writes.

## State and Persistence
Writes OS accounting files selected by `lp_utmp_directory()` and `lp_wtmp_directory()` or platform defaults such as `UTMP_FILE`/`WTMP_FILE`/`UTMPX_FILE`/`WTMPX_FILE`. The ID encodes Samba's session number into utmp's constrained `ut_id` field.

## Dependencies and Integration Points
Depends on configure-time platform feature macros, utmp/utmpx headers, Samba loadparm directories, time helpers, debug logging, and smbd session accounting callers. It integrates with Unix tools such as `who`/`last` indirectly through accounting files.

## Risks
The file is highly platform-conditional; unsupported combinations silently fall back or log low-level warnings. Direct wtmp append has limited locking semantics. Fixed-size string fields truncate without multibyte awareness. The 4-byte ID encoding intentionally ignores overflow because input is effectively random/session-derived.

## Test Signals
Build with and without `WITH_UTMP`, with utmp-only and utmpx-capable feature sets. Test custom utmp/wtmp directories, login/logout record content, hostname truncation, ID uniqueness across many session numbers, and fallback when default utmpx paths are empty.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/utmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/vfs.c -->
# sources/user-network-fs/samba/source3/smbd/vfs.c

## Purpose
Provides smbd's VFS module registration/loading, per-file VFS extension storage, common file operation helpers, and dispatch wrappers for the full `vfs_fn_pointers` interface. It is the central bridge between SMB server logic and filesystem/module backends.

## Important APIs, Types, and Functions
Key module APIs include `smb_register_vfs()`, `vfs_init_custom()`, `smbd_vfs_init()`, and the backend list of `vfs_init_function_entry`. File extension APIs include `vfs_add_fsp_extension_notype()`, remove/fetch helpers, and extension destructors. Common helpers include range validation, `vfs_pwrite_data()`, allocation/truncation/sparse-fill helpers, `vfs_set_blocking()`, `vfs_readdirname()`, `vfs_ChDir_shareroot()`, `vfs_stat*()`, `vfs_fstreaminfo()`, `vfs_fake_fd()`, `vfs_at_fspcwd()`, and `vfs_get_fs_capabilities()`. The large `smb_vfs_call_*` block dispatches every VFS operation through the module stack, including async pread/pwrite/fsync, DOS attributes, xattrs, offload, durable handles, ACLs, snapshots, locks, and DFS operations.

## Control Flow
VFS initialization registers static backends if needed, loads the default backend, optionally adds `widelinks`, then loads configured `vfs objects` in reverse order so the first configured module becomes the outermost handler. Each dispatch wrapper uses `VFS_FIND()` to skip modules that do not implement the requested operation and panic if VFS calls are currently denied.

Write helpers validate offsets and lengths before invoking backend operations. `vfs_pwrite_data()` either drains unread request bytes through `SMB_VFS_RECVFILE()` with a blocking retry on EAGAIN/EWOULDBLOCK, or loops over `SMB_VFS_PWRITE()` until complete. Allocation helpers contend level2 oplocks around shrink/grow/zero-fill operations and use fallocate when possible. Async wrappers capture backend recv function pointers, install callbacks, translate backend errors into tevent Unix or NT errors, and return stored results through recv functions. Some async completion paths re-impersonate the file user before receiving backend results.

## State and Persistence
Process state includes the registered backend list, per-connection VFS handle chains, per-files_struct extension linked lists, the `chdir_lastconn_cache`, and a global VFS-deny stack pointer. Filesystem state is modified through backend calls for allocation, truncate, rename, ACL, xattr, durable-handle, and snapshot operations. The module parameter string is stored on the connection's talloc context.

## Dependencies and Integration Points
Depends on Samba module loading, loadparm share settings, `files_struct`, `connection_struct`, SMB filename/stat abstractions, oplock contention, notify, tevent, Unix I/O helpers, fd handles, memcache globals, and UID switching. Almost every smbd file operation reaches this layer through `SMB_VFS_*` macros.

## Risks
Module order is behavior-critical. `VFS_FIND()` assumes a later module implements every operation; developer builds can assert full function coverage, but production relies on stack correctness. Range validation must prevent overflow and invalid append-offset usage. Blocking retry in `vfs_pwrite_data()` must restore socket flags or request processing can be disrupted. Async completion paths assume `change_to_user_and_service_by_fsp()` succeeds and assert if it does not. Global `chdir_lastconn_cache` can become stale unless reset after cwd-affecting events.

## Test Signals
Test module registration version/name collisions, loading module paths with parameters, default/widelinks/configured order, per-fsp extension add/fetch/remove/destroy, pread/pwrite/allocation range boundaries, append mode, recvfile socket-drain behavior, fallocate fallback, truncate notifications, POSIX lstat behavior, fake fd behavior, fs capability/timestamp detection, VFS deny panic paths in developer tests, async pread/pwrite/fsync/xattr/DOS attribute error propagation, and representative wrapper calls across modules that implement/pass through operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/vfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/bench_pthreadpool.c -->
# sources/user-network-fs/samba/source3/torture/bench_pthreadpool.c

## Purpose
Small torture benchmark for Samba's `pthreadpool_pipe` implementation. It measures repeated submit/finish cycles using a no-op job and reports failure on pool, submission, completion, or destruction errors.

## Important APIs, Types, and Functions
`null_job()` is the empty worker callback. `run_bench_pthreadpool(int dummy)` initializes a pool with one worker, loops `torture_numops` times calling `pthreadpool_pipe_add_job()` and `pthreadpool_pipe_finished_jobs()`, destroys the pool, and returns boolean success.

## Control Flow
The benchmark initializes the pool, submits one no-op job, waits for exactly one finished job, and repeats. On any nonzero add/init error or negative finished-jobs result, it prints an error and breaks. After the loop, it requires the final `ret` to equal `1`, then destroys the pool and returns whether destroy succeeded.

## State and Persistence
No persistent state. Runtime state is the pool object, loop counter, returned job ID, and global `torture_numops` controlling workload size.

## Dependencies and Integration Points
Depends on `../lib/pthreadpool/pthreadpool_pipe.h`, torture `proto.h`, global torture settings, and diagnostic output via `d_fprintf(stderr, ...)`. It is integrated as a torture command/benchmark rather than production smbd behavior.

## Risks
The final `ret != 1` check assumes the last `pthreadpool_pipe_finished_jobs()` returns one completed job; if `torture_numops` is zero, the benchmark returns false because `ret` is still the init result. The benchmark serializes submit/wait with a one-thread pool, so it tests overhead and correctness more than parallel throughput.

## Test Signals
Run with positive `torture_numops`, zero operations, injected pool init/add/finish failures, and under leak/thread sanitizers to validate pool destruction and no-op callback execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/bench_pthreadpool.c -->
