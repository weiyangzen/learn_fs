# subset-b-009863 research

Grouped research for Samba `source3/smbd` locking, close, connection, directory, DOS attribute, durable handle, fake file, fd handle, access, and file I/O support. Each section preserves the source path and uses reconciliation markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/blocking.c -->
# sources/user-network-fs/samba/source3/smbd/blocking.c

## Purpose
`blocking.c` implements SMB1 blocking byte-range lock handling. It tries multi-lock requests atomically, queues requests that cannot complete immediately, waits on share-mode/locking database notifications or retry timers, and exposes cancellation helpers used by legacy SMB1 lock/cancel paths.

## Important APIs, types, and functions
- `smbd_do_locks_try()` loops over `struct smbd_lock_element` entries, calls `do_lock()`, records the blocker, and unwinds already acquired locks with `do_unlock()` if any later lock fails.
- `smbd_smb1_do_locks_send()` creates a `tevent_req` for a lock request, moves the `smb_request` into request state, performs the first try, and appends in-progress requests to `fsp->blocked_smb1_lock_reqs`.
- `smbd_smb1_do_locks_try_fn()` is the locked share-mode callback. It checks older blocked requests for fairness, calls `smbd_do_locks_try()`, and sets up `share_mode_watch_send()` plus timeout/backoff behavior.
- `smbd_smb1_do_locks_recv()` returns the final status and records repeated lock failure offset hints on the FSP.
- `smbd_smb1_brl_finish_by_req()`, `smbd_smb1_brl_finish_by_lock()`, and `smbd_smb1_brl_finish_by_mid()` complete blocked requests by direct request, matching lock tuple, or SMB1 MID.

## Control flow
A lock request enters `smbd_smb1_do_locks_send()`. Empty lock batches complete immediately. Otherwise the request tries to acquire locks under `share_mode_do_locked_brl()`. The callback first checks older requests in the same FSP blocked-list so a younger request cannot bypass a conflicting older one. If the byte-range lock backend grants all locks, the request completes. If it returns `NT_STATUS_RETRY`, Samba waits either for locking database wakeups or a retry timer, ignoring the client timeout until the backend gives a definitive result. If it returns a lock-denied status, Samba computes an end time from client timeout, `lp_lock_spin_time()`, ancient large-offset heuristics, and prior failure offset state. POSIX lock conflicts use polling because the backend identifies them with `blocking_smblctx == UINT64_MAX`.

## State and persistence behavior
The persistent lock state lives in Samba locking/share-mode databases via the byte-range locking layer, not in this file. This file owns transient tevent state and the per-FSP `blocked_smb1_lock_reqs` array. Request cleanup removes entries from that array unless the request was already received. `fsp->fsp_flags.lock_failure_seen` and `fsp->lock_failure_offset` store a short-lived hint to delay repeated lock attempts on the same offset.

## Dependencies and integration points
The file depends on byte-range locking (`do_lock`, `do_unlock`, `brl_*`), share-mode locking/watch APIs, messaging server IDs, tevent, request lifetime management, and SMB1 cancel/lock reply code. It integrates with `close.c`, which drains blocked lock requests before closing a normal file.

## Risks and edge cases
- `smbd_smb1_do_locks_check_blocked()` indexes `blocked[li]` inside the `bi` loop; this deserves review because it appears intended to inspect `blocked[bi]`.
- Incorrect cleanup of `fsp->blocked_smb1_lock_reqs` can leave waiters on dead FSPs or complete the wrong SMB1 request.
- Backend `NT_STATUS_RETRY` can wait indefinitely by design; backends must eventually return another status.
- POSIX lock polling and share-mode wakeups can retry on unrelated database changes.
- Cancellation by MID walks all FSPs and is intentionally expensive but legacy-only.

## Test signals
Useful tests cover multi-lock atomic rollback, lock denial versus timeout status mapping, FIFO behavior among blocked SMB1 locks, MID cancellation, matching lock cancellation, POSIX lock polling, and close-time draining of blocked locks with `NT_STATUS_RANGE_NOT_LOCKED`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/blocking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/close.c -->
# sources/user-network-fs/samba/source3/smbd/close.c

## Purpose
`close.c` is the main SMB file-handle teardown implementation. It closes normal files, directories, alternate streams, fake files, print files, and non-FSA/path reference handles while coordinating share-mode removal, oplock release, durable disconnects, pending AIO, delete-on-close, write-time updates, magic scripts, change notifications, and recursive deletion of veto-hidden directory contents.

## Important APIs, types, and functions
- `delete_all_streams()` enumerates named streams with `vfs_fstreaminfo()` and unlinks all non-default streams relative to a directory FSP.
- `has_other_nonposix_opens()`, `has_nonposix_opens()`, and `has_delete_opens()` inspect share-mode entries for delete-on-close decisions and open-conflict reporting.
- `close_share_mode_lock_prepare()` and `close_share_mode_lock_cleanup()` are callbacks around `share_mode_entry_prepare_lock_del()`/unlock that decide whether deletion must happen while holding the global share lock.
- `close_remove_share_mode()` handles normal file share-mode teardown and delete-on-close file unlinking.
- `close_normal_file()` handles durable disconnect, pending SMB1 lock cleanup, write-time update, fd close, and magic-script execution.
- `recursive_rmdir_fsp()`, `rmdir_internals()`, and `close_directory()` implement directory close and delete-on-close directory removal.
- `close_file_smb()`, `close_file_free()`, and `msg_close_file()` are the public close dispatch and messaging entry points.

## Control flow
For normal files, `close_normal_file()` first refuses unsafe close with outstanding AIO except controlled shutdown cleanup, completes any blocked SMB1 locks, and attempts a durable disconnect only for shutdown closes on durable opens. Durable success updates the open database and schedules the scavenger instead of doing a full close. Otherwise it clears durable state, sends directory-lease break notifications for modified files, removes share modes, applies SMB1 explicit close write time, closes the fd, optionally runs a magic script, and returns the first meaningful status.

Delete-on-close is decided under the share-mode lock. If this is the last relevant non-POSIX open and the close is normal or shutdown, the close path retrieves the security tokens associated with the delete disposition, temporarily becomes that user if needed, validates that the pathname still names the same file ID, deletes streams, removes kernel share modes, unlinks the file or directory, resets delete-on-close, unlocks share modes, and sends remove notifications. Directory deletion first tries `unlinkat(..., AT_REMOVEDIR)`, then, if configured, verifies that only veto/invisible entries remain and recursively removes them before retrying.

## State and persistence behavior
Persistent filesystem state changes include unlinking files/directories/streams, chmod/execution of magic scripts, write-time updates, and possible spool file finalization. Shared open state is removed or marked disconnected in share-mode and `smbXsrv_open` databases. In-memory state on `files_struct` is cleared through `fd_close()`, `file_free()`, alternate-stream base FSP cleanup, and `fsp_unbind_smb()`. Delete-on-close token state and parent lease keys are read from share-mode records.

## Dependencies and integration points
The file integrates tightly with locking/share-mode code, durable handle VFS hooks, SMBX open records, scavenger scheduling, byte-range lock cleanup from `blocking.c`, stream VFS, notification, leases, pathref helpers, security tokens, print spool, fake files, and directory helpers from `dir.c`.

## Risks and edge cases
- Delete-on-close must retain the share lock through deletion to prevent recreate races.
- Stale names after rename are tolerated by validating file IDs before unlink.
- `rmdir_internals()` declares a local `struct stat_ex st` but uses `SMB_VFS_LSTAT(conn, smb_dname)` without visibly filling that local in the shown code; reviewers should confirm macro semantics or a latent bug.
- Shutdown close with pending AIO uses careful talloc ordering because AIO destructors mutate the FSP AIO array.
- Magic scripts run from share paths and create output files; configuration and permissions must prevent unintended command execution.
- Alternate stream close recursively frees the base FSP, so stream/base ownership invariants are critical.

## Test signals
Exercise normal/error/shutdown close, durable disconnect success and fallback, delete-on-close for files/directories with other opens, stream deletion, veto-file recursive directory deletion, pending AIO shutdown, SMB1 close write time, magic script output, print/fake file close dispatch, and `MSG_SMB_CLOSE_FILE` handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/close.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/conn.c -->
# sources/user-network-fs/samba/source3/smbd/conn.c

## Purpose
`conn.c` allocates, initializes, tracks, and tears down `connection_struct` instances, which represent per-share tree connections inside an smbd server connection.

## Important APIs, types, and functions
- `conn_new()` allocates a connection, `share_params`, VUID cache, connect path, and synthetic `cwd_fsp`, then links it into `sconn->connections`.
- `conn_num_open()`, `conn_snum_used()`, `conn_protocol()`, and `conn_using_smb2()` expose connection counts, service-use checks, and negotiated protocol checks.
- `conn_clear_vuid_caches()` clears a logged-off VUID from all connections and delegates to `conn_clear_vuid_cache()`.
- `conn_free_internal()` releases VFS handles, pending transaction buffers, zeroes the connection, and resets cwd cache state.
- `conn_setup_case_options()` applies share case-sensitivity and case-preservation options.

## Control flow
Connections are talloc roots linked into the owning `smbd_server_connection`. The talloc destructor removes the connection from the server list, decrements `num_connections`, nulls `sconn`, and runs internal cleanup. VUID cache clearing preserves `conn->session_info` in the special case where it is still referenced for later SMBulogoff/SMBtdis diagnostics and audit paths.

## State and persistence behavior
All state here is in-memory. `conn_new()` initializes `cwd_fsp` as a pseudo FSP with fd `-1` and invalid fnum. `conn_free_internal()` frees VFS per-connection private data and pending trans buffers, then zeroes the structure, so consumers must not access a connection after talloc free.

## Dependencies and integration points
This file depends on talloc, DLIST, loadparm case options, VFS handle lifetime callbacks, `fd_handle_create()`, and server connection globals. It is used by tree connect/disconnect, service reload decisions, SMB1 and SMB2 protocol conditionals, and VUID invalidation.

## Risks and edge cases
- `conn_protocol()` defaults to `PROTOCOL_COREPLUS` if no client connection is available to preserve older behavior.
- Zeroing `connection_struct` in the destructor requires removal from lists first.
- Session info retention for VUID cache clearing is intentional but can surprise ownership readers.
- `cwd_fsp` is a synthetic object; code that assumes all FSPs have real fds must use helper accessors.

## Test signals
Tests should cover connection allocation/free count updates, VUID invalidation across multiple connections, protocol fallback and SMB2 detection, VFS handle `free_data` calls, pending transaction cleanup, and case option setup for auto and explicit case-sensitive shares.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/conn_idle.c -->
# sources/user-network-fs/samba/source3/smbd/conn_idle.c

## Purpose
`conn_idle.c` detects fully idle server connections and implements asynchronous forced tree disconnect for shares, waiting for outstanding AIO before disconnecting tree connections and reloading services.

## Important APIs, types, and functions
- `conn_idle_all()` updates last-used timestamps and returns true only when every connection has no open files and exceeds `deadtime`.
- `conn_force_tdis()` scans tree connections and starts an async forced disconnect for those accepted by a caller-supplied predicate.
- `conn_force_tdis_send()` marks a TCON as `NT_STATUS_NETWORK_NAME_DELETED`, marks associated FSPs closing, and queues waiters behind any outstanding AIO.
- `conn_force_tdis_done()` disconnects the SMBX TCON, frees it, switches to root, and reloads services.

## Control flow
Idle detection uses `lastused_count` as an activity counter: if it changed, the connection's `lastused` timestamp is refreshed. Forced disconnect is deliberately asynchronous. The TCON is marked unusable first so no new request should attach to it. Existing FSPs for that connection are marked closing, and if they have AIO, the code waits on a per-request `tevent_queue`. A final waiter at the end of the queue fires when all prior AIO waiters are gone, then `smbXsrv_tcon_disconnect()` performs the actual tree disconnect.

## State and persistence behavior
State is mostly in-memory TCON/FSP status plus SMBX TCON database updates performed by `smbXsrv_tcon_disconnect()`. Service reload after disconnect can refresh in-memory loadparm state. The async request is allocated on the NULL context and freed in completion.

## Dependencies and integration points
The file depends on tevent queues, SMBX TCON state, AIO request destructors, FSP lists, `change_to_root_user()`, and `reload_services()`. It is triggered by message handlers in `conn_msg.c` and by idle/deadtime server logic.

## Risks and edge cases
- Forced disconnect must prevent new I/O before waiting for old AIO; otherwise FSP close can race with new operations.
- `conn_force_tdis_done()` stores `tcon` before disconnect and sets `conn = NULL`, so later code must not dereference the freed connection.
- Service reload explicitly disables reload caching to avoid repeated-call suppression.
- Idle detection returns false as soon as one connection is active or has open files.

## Test signals
Tests should simulate no-deadtime, active-file, and all-idle cases; force-disconnect shares with and without AIO; verify TCON status changes reject new operations; and verify service reload after disconnect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/conn_idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/conn_msg.c -->
# sources/user-network-fs/samba/source3/smbd/conn_msg.c

## Purpose
`conn_msg.c` handles smbcontrol messaging requests that force tree disconnects by share name, either unconditionally or only when access after a service reload is no longer valid.

## Important APIs, types, and functions
- `msg_force_tdis()` validates a NUL-terminated share name and calls `conn_force_tdis()` with `force_tdis_check()`.
- `force_tdis_check()` matches a literal share name or `*` for all shares.
- `msg_force_tdis_denied()` reloads services as root and then forces disconnects selected by `force_tdis_denied_check()`.
- `force_tdis_denied_check()` re-runs `check_user_share_access()` and closes only if access fails, share access bits changed, or read-only state changed.

## Control flow
Both message handlers treat message data as a C string and reject empty or non-NUL-terminated payloads. The unconditional path just compares the requested name against each connection's service name. The denied path first reloads service definitions, then for matching connections recomputes access and closes only sessions whose effective access no longer matches the connection's stored `share_access`/`read_only` fields.

## State and persistence behavior
This file does not persist state directly. It can trigger async TCON disconnects, connection closing, and service reload through `conn_force_tdis()`. The message payload is transient.

## Dependencies and integration points
It depends on smbd messaging, loadparm service names, user share access checks, and `conn_idle.c`'s forced disconnect implementation. It is typically driven by administrative smbcontrol operations and share/service reload notifications.

## Risks and edge cases
- Message payload validation is critical because the share name is read directly from `DATA_BLOB`.
- `*` closes all shares and logs a warning for each matching connection.
- Access-revalidation close behavior depends on current service reload state and session security tokens.
- Failure in `check_user_share_access()` intentionally closes the share.

## Test signals
Tests should send valid and invalid message payloads, force-disconnect a named share and all shares, change share ACL/read-only configuration and verify only denied or changed connections close, and verify unaffected connections remain active.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/conn_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/connection.c -->
# sources/user-network-fs/samba/source3/smbd/connection.c

## Purpose
`connection.c` counts active tree connections for a share using Samba's global SMBX TCON database and exposes a service-number based "in use" check for reload logic.

## Important APIs, types, and functions
- `count_current_connections(sharename, verify)` traverses `smbXsrv_tcon_global.tdb` and counts entries whose `share_name` matches.
- `connections_snum_used()` maps a service number to its configured service name and returns whether any verified current connection uses it.
- `count_fn()` optionally filters dead server IDs with `process_exists()`.

## Control flow
The count path initializes a `count_stat`, traverses all global TCON records with `smbXsrv_tcon_global_traverse()`, and increments for matching share names. The comment explicitly accepts a race rather than chain-locking first because locking would risk deadlock.

## State and persistence behavior
The file reads global TCON database state but does not write it. Returned counts are snapshots and can be stale immediately due to concurrent connect/disconnect.

## Dependencies and integration points
It depends on SMBX TCON global traversal, server ID liveness checks, loadparm service-name substitution, and service reload code. It is distinct from `conn_snum_used()` in `conn.c`, which only checks the current server process.

## Risks and edge cases
- Counting without pre-locking is intentionally racy.
- Traversal failure logs at level 0 and returns zero, which may make reload logic think a share is unused.
- `verify=true` trades accuracy for process liveness checks and may ignore stale database records.

## Test signals
Useful tests create multiple TCON records for one share, include dead server IDs, check `verify` behavior, simulate traversal errors, and compare global count behavior with current-process `conn_snum_used()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/connection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/dfree.c -->
# sources/user-network-fs/samba/source3/smbd/dfree.c

## Purpose
`dfree.c` computes disk free-space information returned to SMB clients. It supports administrator-provided `dfree command`, VFS `disk_free`, quota clamping, max disk size normalization, broken-platform fallbacks, and optional per-path memcache caching.

## Important APIs, types, and functions
- `get_dfree_info()` is the public entry point. It returns free 1 KiB blocks and fills block size, free blocks, and total blocks.
- `sys_disk_free()` performs uncached computation by external command or VFS and quota APIs.
- `handle_dfree_command()` runs the configured external command with the path and parses `dsize dfree bsize` from the first output line.
- `disk_norm()` enforces `max disk size`.
- `flush_dfree_cache()` clears `DFREE_CACHE`.

## Control flow
If caching is disabled, `get_dfree_info()` calls `sys_disk_free()` directly. With caching enabled, it builds a full path from the connection path and FSP name, uses the parent directory for regular files to reduce cardinality, and looks up a `struct dfree_cached_info` in `smbd_memcache()`. Valid entries are keyed by path and expire by `conn->lastused`. On cache miss, `sys_disk_free()` tries the external command first, otherwise calls `SMB_VFS_DISK_FREE()`, folds in quota values with a common minimum block size, repairs implausibly small block sizes and zero disk sizes, normalizes max disk size, and returns free space as 1 KiB blocks.

## State and persistence behavior
No persistent state is written. The only stored state is process-local memcache entries and a static `dfree_broken` flag used to log the broken-dfree warning only once.

## Dependencies and integration points
It depends on loadparm settings (`dfree command`, cache time, max disk size), VFS disk-free hooks, quota helpers, full-path utilities, and Samba memcache. SMB query filesystem information paths consume its output.

## Risks and edge cases
- External command output is trusted enough to affect reported capacity; bad values fall back only by missing fields, not semantic validation.
- Cache keys depend on full path construction and `conn->lastused`; stale values can be visible until cache expiry.
- Quota and filesystem block-size conversion must avoid overflow and preserve minimum block size semantics.
- Returning `(uint64_t)-1` signals failure and is not cached.

## Test signals
Tests should cover external command parsing with 1/2/3 fields, VFS fallback failure, quota clamping, max disk size cap, regular-file parent keying, cache hit/expiry/flush, and broken zero-total fallback behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/dfree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/dir.c -->
# sources/user-network-fs/samba/source3/smbd/dir.c

## Purpose
`dir.c` implements smbd directory handles and directory search pointers. It opens directory FSPs, allocates SMB1 directory pointer IDs, reads and filters entries, performs access-based visibility checks, tracks opens below a directory, and verifies whether directories can be deleted.

## Important APIs, types, and functions
- `struct smb_Dir` wraps a VFS `DIR *`, directory `smb_filename`, file-number offset, case-sensitivity state, and back pointer to the owning FSP.
- `struct dptr_struct` stores SMB search handle state: dnum, wildcard, attributes, wildcard/stat optimization flags, privilege flag, overflow entry, and resume name.
- `init_dptrs()`, `dptr_create()`, `dptr_CloseDir()`, `dptr_closecnum()`, and dptr accessors manage SMB1/SMB2 directory pointer state.
- `dptr_ReadDirName()` optimizes non-wildcard searches by `fstatat()` and falls back to scanning for mangled or case-insensitive matches.
- `smbd_dirptr_get_entry()` is the main entry enumeration/filtering loop.
- `OpenDir()`, `OpenDir_from_pathref()`, `ReadDirName()`, and `RewindDir()` expose lower-level directory handles.
- `is_visible_fsp()`, `have_file_open_below()`, `opens_below_forall[_read]()`, and `can_delete_directory_hnd()/fsp()` implement visibility and delete checks.

## Control flow
Directory searches begin by checking `SEC_DIR_LIST`, opening a directory handle from an FSP, allocating an SMB1 dnum if needed, and storing wildcard/attribute matching state. Enumeration returns `.` and `..` first, then VFS names. It skips veto paths, stale smbd temporary names, invisible files, DFS/symlink cases that should be hidden, and entries whose DOS mode does not match requested attributes. For non-wildcard queries, Samba avoids scanning where possible by using `FSTATAT`, then scans only for mangled-name or case-insensitive fallback.

Visibility is option-driven: `hide unreadable`, `hide unwriteable files`, `hide special files`, and `hide new files timeout` can suppress entries after approximate ACL/write/special-file checks. Directory deletion scans entries, optionally ignores veto/invisible entries when `delete veto files = yes`, treats DFS links as non-empty, handles dangling symlinks specially, and finally denies deletion if share-mode records or local FSPs show open files below the directory.

## State and persistence behavior
Directory search state is in-memory under `sconn->searches` and per-FSP `dptr`. The VFS directory fd is closed by `smb_Dir_destructor()`, which also invalidates the FSP fd. `ReadDirName()` can persistently unlink stale smbd temporary names as root. Delete-check helpers read share-mode databases but do not update them.

## Dependencies and integration points
This file depends on VFS directory/open/stat/unlink APIs, bitmap allocation, name mangling, DFS/reparse helpers, ACL/security checks, DOS mode mapping from `dosmode.c`, close helpers from `close.c`, share-mode traversal, and loadparm visibility/delete settings. SMB1 trans2/search and SMB2 query-directory code use the exported dptr APIs.

## Risks and edge cases
- Search handle numbering is biased by one and has separate old-SMB 1-255 versus new 256+ ranges.
- `dptr_closecnum()` closes files while iterating directory pointers, so it copies the FSP pointer before close invalidates dptr memory.
- Visibility checks are intentionally approximate and must not be treated as authorization.
- Symlink, DFS, POSIX path, and case-insensitive fallback behavior is subtle and protocol/configuration dependent.
- Open-below checks are path-prefix based and race with renames/connectpath changes.

## Test signals
Tests should cover old/new dptr allocation limits, wildcard and non-wildcard query behavior, mangled and case-insensitive lookup fallback, veto/invisible/hidden-new-file filtering, DFS symlink masquerading, POSIX symlink visibility, stale temp-name cleanup, directory delete with veto files, and strict rename/open-below checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/dir.h -->
# sources/user-network-fs/samba/source3/smbd/dir.h

## Purpose
`dir.h` declares the public directory-handle, directory-pointer, visibility, open-below traversal, and delete-check interfaces implemented by `dir.c`.

## Important APIs, types, and functions
The header forward-declares opaque `struct smb_Dir` and `struct dptr_struct`, then exports `OpenDir()`, `OpenDir_from_pathref()`, `ReadDirName()`, `RewindDir()`, dptr lifecycle/accessor functions, `smbd_dirptr_get_entry()`, overflow/resume helpers, `is_visible_fsp()`, `have_file_open_below()`, `opens_below_forall[_read]()`, and `can_delete_directory_hnd()/fsp()`.

## Control flow
Consumers use this header to create directory handles from paths or pathref FSPs, attach search state to SMB request processing, enumerate filtered directory entries, preserve one overflow entry when a response buffer fills, and ask whether a directory is deletable before setting delete-on-close or completing rmdir.

## State and persistence behavior
The header itself has no state. It intentionally hides the layout of `smb_Dir` and `dptr_struct` so ownership and fd cleanup remain centralized in `dir.c`.

## Dependencies and integration points
It depends on core smbd types from `includes.h` and is included by close/delete code, query-directory reply code, access checks, and other path traversal components.

## Risks and edge cases
- Callers must respect ownership conventions: returned names and `smb_filename` objects may be moved, and directory handles must be freed to close fds.
- `dptr_*` APIs are meaningful only for FSPs and server connections initialized with directory pointer bitmap state.
- `is_visible_fsp()` is not an authorization function.

## Test signals
Build coverage should catch prototype drift. Runtime tests are those for `dir.c`, especially public API use from close/rmdir and SMB query-directory paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/dir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/dmapi.c -->
# sources/user-network-fs/samba/source3/smbd/dmapi.c

## Purpose
`dmapi.c` provides optional DMAPI/HSM integration. When compiled without DMAPI support, it returns no-op values. With DMAPI, it creates or reconnects to a long-lived kernel DMAPI session and reports offline file attributes by checking whether read events are registered on a file.

## Important APIs, types, and functions
- Non-DMAPI builds export stub `dmapi_file_flags()`, `dmapi_have_session()`, and `dmapi_get_current_session()`.
- `struct smbd_dmapi_context` stores the current `dm_sessid_t` and a numeric suffix for new session names.
- `dmapi_have_session()` lazily allocates global `dmapi_ctx` and initializes a session as root.
- `dmapi_new_session()` destroys/recreates an invalid session with an incremented name suffix.
- `dmapi_destroy_session()` tears down the kernel session during master smbd exit.
- `dmapi_file_flags()` maps DMAPI read-event interest to `FILE_ATTRIBUTE_OFFLINE`.

## Control flow
DMAPI initialization calls `dm_init_service()`, enumerates kernel sessions with a growable buffer, queries names looking for `samba` or `sambaN`, and creates a session if none matches. File flag lookup obtains the current session, optionally becomes root on systems without POSIX capabilities, converts a path to a DMAPI handle, retries after re-enabling capability on `EPERM`, reads the event list, and sets the offline bit if `DM_EVENT_READ` is present.

## State and persistence behavior
DMAPI sessions are persistent kernel resources and can outlive smbd worker processes. Samba caches the session in global `dmapi_ctx`. The file does not persist user data, but session creation/destruction affects kernel/HSM state.

## Dependencies and integration points
It depends on platform DMAPI headers, Samba privilege switching, `set_dmapi_capability()`, and VFS offline-attribute paths. GPFS or other HSM VFS modules may override or complement the default flag logic.

## Risks and edge cases
- Session lifetime is intentionally long; destroying too early can affect other smbd children, while never destroying can block HSM shutdown.
- Capability handling differs by platform and user ID changes can drop effective capabilities.
- `dmapi_file_flags()` receives a path string and can race with rename/unlink.
- DMAPI stubs mean callers must tolerate all-zero/no-session behavior.

## Test signals
Build tests should cover DMAPI and non-DMAPI configurations. Integration tests on a DMAPI/HSM-capable filesystem should verify session reuse, invalid-session recreation, offline flag detection, permission/capability retry, and master-process session destruction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/dmapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/dnsregister.c -->
# sources/user-network-fs/samba/source3/smbd/dnsregister.c

## Purpose
`dnsregister.c` optionally registers smbd as an `_smb._tcp` service through DNS Service Discovery/mDNS. Without DNSSD support it exposes a successful no-op setup function.

## Important APIs, types, and functions
- `smbd_setup_mdns_registration()` is the public setup API.
- With `WITH_DNSSD_SUPPORT`, `struct dns_reg_state` stores tevent context, port, `DNSServiceRef`, timer, socket fd, and fd event.
- `dns_register_smbd_schedule()` resets old registration state and schedules an immediate or delayed retry.
- `dns_register_smbd_retry()` calls `DNSServiceRegister()` and registers the DNS-SD socket with tevent.
- `dns_register_smbd_fde_handler()` processes mDNS daemon results and retries on failure.

## Control flow
Setup allocates a state object, installs a destructor, and schedules immediate registration. Each retry destroys any existing DNS-SD ref/timer/fd event, attempts registration on any interface with service type `_smb._tcp` and the configured port, then adds a tevent fd watcher for the DNS-SD socket. If registration or result processing fails, a new retry is scheduled five minutes later. On a successful processed result, the state object is freed.

## State and persistence behavior
The file holds transient tevent and DNS-SD registration state. Actual advertised service state is maintained by the local mDNS daemon while the `DNSServiceRef` is active. No repository or TDB state is written.

## Dependencies and integration points
It depends on Apple's/Avahi-compatible `dns_sd.h`, tevent timers/fds, and smbd startup code that calls `smbd_setup_mdns_registration()`. It supports browsing via SMB clients using service discovery.

## Risks and edge cases
- The destructor clears both timer and fd event and deallocates `DNSServiceRef`; retry code relies on this idempotence.
- Registration failures are logged and retried indefinitely at a fixed interval.
- The callback argument to `DNSServiceRegister()` is NULL, so only socket result processing errors are observed.
- Non-DNSSD builds silently report success.

## Test signals
Tests should build with and without DNSSD, verify immediate schedule, simulate registration failure and retry timer creation, process-result failure retry, destructor cleanup, and advertised `_smb._tcp` service visibility on DNSSD-capable systems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/dnsregister.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/dosmode.c -->
# sources/user-network-fs/samba/source3/smbd/dosmode.c

## Purpose
`dosmode.c` translates between Windows/DOS file attributes, UNIX mode bits, xattr-stored Samba DOS metadata, VFS DOS attribute hooks, compression/sparse flags, and file timestamp semantics.

## Important APIs, types, and functions
- `unix_mode()`, `apply_conf_file_mask()`, and `apply_conf_dir_mask()` derive UNIX modes for creates from DOS attributes and share masks.
- `fdos_mode()` returns DOS attributes for an open FSP, using fake-file handling, VFS DOS attributes, UNIX-mode fallback, name-based hidden rules, protocol filtering, compression, streams, symlinks, and cached attributes.
- `dos_mode_at_send()/recv()` asynchronously obtains attributes through VFS query-directory support and falls back to `fdos_mode()`.
- `parse_dos_attribute_blob()`, `fget_ea_dos_attribute()`, and `set_ea_dos_attribute()` decode/encode `SAMBA_XATTR_DOS_ATTRIB` NDR blobs including create time.
- `file_set_dosmode()` writes DOS attributes through VFS or UNIX chmod fallback.
- `file_set_sparse()`, `file_ntimes()`, `set_create_timespec_ea()`, and `get_create_timespec()` handle sparse flag and timestamp behavior.

## Control flow
On reads, `fdos_mode()` first rejects invalid stat data, handles fake files and non-regular/non-directory types, returns cached DOS attributes when present, asks the VFS for stored DOS attributes, or falls back to mapping UNIX mode bits. `dos_mode_post()` normalizes stream directory bits, compression, hidden-by-name/path, directory/normal defaults, and old protocol masks. On writes, `file_set_dosmode()` rejects read-only shares, symlinks, invalid temporary directories, and missing FSPs, then prefers `SMB_VFS_FSET_DOS_ATTRIBUTES()`. If unimplemented, it computes a UNIX mode, preserves file type/sticky/setuid/setgid and configured execute bits, protects setgid directory chmod rules, and optionally retries as root for DOS filemode semantics.

EA parsing supports multiple `xattr_DOSATTRIB` versions. New writes use version 5 with valid flags for attributes and create time. Attribute setting and time setting both support DOS semantics where write permission can allow changes that POSIX ownership would deny, subject to Samba configuration and access checks.

## State and persistence behavior
Persistent state can be stored in xattrs, UNIX mode bits, filesystem sparse/compression metadata through VFS, and timestamps. `smb_fname->st.cached_dos_attributes` caches computed attributes in memory. `set_create_timespec_ea()` persists create time by rewriting DOS attribute EA. Notifications are emitted on attribute changes and sparse changes.

## Dependencies and integration points
The file depends on loadparm mapping options, generated NDR xattr structures, VFS xattr/DOS/compression/time hooks, ACL access checks, fake files, lease notifications, DMAPI/offline handling through VFS defaults, and protocol selection from connection state. Directory enumeration and open/create paths consume these APIs.

## Risks and edge cases
- DOS attributes may be represented by xattrs or UNIX execute/write bits depending on configuration, making migration and mixed clients sensitive.
- Create time is stored in the same xattr as attributes; failed xattr writes can lose expected Windows metadata.
- Named streams inherit base file attributes except directory is stripped.
- Async VFS attribute failure semantics intentionally collapse many errors to last-resort mode mapping.
- Root fallback for chmod/xattr/time changes must remain gated by share write access and DOS semantics options.

## Test signals
Tests should cover DOS-to-UNIX create modes, readonly/archive/system/hidden mappings, xattr versions 1-5 parse/write including create time, old protocol filtering, stream attributes, symlink/reparse behavior, compression and sparse flags, async fallback paths, chmod root fallback, DOS file times, and notification emission.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/dosmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/durable.c -->
# sources/user-network-fs/samba/source3/smbd/durable.c

## Purpose
`durable.c` implements the default VFS durable handle cookie, disconnect, and reconnect logic. It serializes enough file/open/stat state to let an SMB durable handle survive a clean disconnect, then validates and reopens it only if share-mode and filesystem state prove the file was not changed by another opener.

## Important APIs, types, and functions
- `vfs_default_durable_cookie()` creates an NDR `vfs_default_durable_cookie` with file ID, service path, base name, allocation size, file position, write-time-forced flag, and stat data.
- `vfs_default_durable_disconnect()` validates the old cookie, marks share mode and byte-range locks disconnected, stats the file, builds a reconnectable cookie, and closes the fd.
- `vfs_default_durable_reconnect()` decodes the cookie, converts the stored name to a dirfsp-relative path, creates a new FSP, and calls `share_mode_do_locked_brl()`.
- `vfs_default_durable_reconnect_fn()` finds the unique disconnected share-mode entry, restores FSP open state/lease/locks, opens the file, checks stat/file ID, restores oplock, and creates a fresh cookie.
- `vfs_default_durable_reconnect_check_stat()` compares cookie stat fields to current stat fields.

## Control flow
Cookie creation refuses unsupported situations: disabled durable handles, kernel share modes/oplocks, POSIX locks, directories, streams, and fake files. Disconnect requires handle leases, supported lock/write conditions, no delete-on-close, valid regular-file stat, and successful share-mode/BRL disconnected marking. Reconnect requires durable handles enabled, cookie magic/version/allow flag, same share path, same file ID, a unique disconnected share-mode entry matching the persistent open ID, compatible write access, matching client GUID for leases, BRL reconnection, successful fd reopen, stat equality, and successful oplock restoration.

## State and persistence behavior
Durable state persists in SMBX open records and share-mode/byte-range lock databases, with the VFS cookie stored as an opaque blob in the open record. Disconnect closes the local fd but leaves durable open state for scavenging/reconnect. Reconnect mutates the share-mode entry from disconnected server ID to current server ID/MID and reattaches the `smbXsrv_open` to a new `files_struct`.

## Dependencies and integration points
The file depends on generated NDR open-files structures, share-mode and BRL APIs, leases database, server ID disconnected markers, `fd_openat()`/`fd_close()`, `fdos_mode()`, fake-file detection, loadparm durable/kernel settings, and SMB request chain FSP fields. `close.c` invokes durable disconnect on shutdown close.

## Risks and edge cases
- Durable reconnect is intentionally conservative; any stat mismatch denies reconnect to avoid missed oplock breaks.
- Multiple matching disconnected share entries invalidate reconnect.
- Reconnect failure after share-mode reset deletes the share-mode entry to avoid corrupted state.
- The disconnect cookie stores `base_name = fsp_str_dbg(fsp)` in the shown code; reviewers should confirm this is always a valid reopen path, not just a debug string.
- Durable handles are incompatible with several kernel/stream/directory/delete-on-close scenarios.

## Test signals
Tests should cover successful durable disconnect/reconnect, cookie magic/version/servicepath/file ID failures, stat mismatch denial, duplicate share-mode entry denial, write access changed denial, lease GUID mismatch, BRL reconnect, POSIX lock rejection, stream/directory/fake-file rejection, and scavenger cleanup after disconnect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/durable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/error.c -->
# sources/user-network-fs/samba/source3/smbd/error.c

## Purpose
`error.c` builds SMB1 error replies and selects whether errors are sent as NTSTATUS or legacy DOS error class/code values.

## Important APIs, types, and functions
- `use_nt_status()` returns whether NTSTATUS replies are enabled and the client advertised `CAP_STATUS32`.
- `error_packet_set()` writes NT or DOS error fields into an SMB1 outbuf and updates `FLAGS2_32_BIT_ERROR_CODES`.
- `error_packet()` creates a minimal SMB1 error packet and delegates to `error_packet_set()`.
- `reply_nt_error()`, `reply_force_dos_error()`, and `reply_both_error()` reset the request outbuf and install the desired error.
- `reply_openerror()` preserves specific Windows-compatible mappings for object-name collision and too-many-open-files.

## Control flow
Callers can request pure NT status, forced DOS status, or a combined NT/DOS mapping. If eclass is `-1`, NT status is forced. If `ntstatus` is an encoded DOS status, DOS is forced. Otherwise Samba sends NT status only when both server configuration and client capability allow it; legacy clients receive DOS class/code. For DOS replies, `ntstatus_to_dos()` maps NT status when needed. For NT replies, `dos_to_ntstatus()` maps nonzero DOS inputs when no NT status was supplied.

## State and persistence behavior
This file mutates only outgoing SMB1 response buffers. It reads global client capabilities and loadparm status support.

## Dependencies and integration points
It depends on SMB1 buffer macros, error mapping helpers, request output buffer helpers, and optional SMB1 command name lookup. All SMB1 reply paths that need error packets use these helpers or macros wrapping them.

## Risks and edge cases
- Wire compatibility depends on special mappings in `reply_openerror()`, especially `NT_STATUS_OBJECT_NAME_COLLISION` and `NT_STATUS_TOO_MANY_OPENED_FILES`.
- Debug messages avoid starting with the word `error` to keep subunit test streams clean.
- Forced DOS and forced NT modes are encoded through sentinel values and must be used consistently by macros.

## Test signals
Tests should verify NT-capable and legacy client replies, forced DOS behavior, DOS-to-NT and NT-to-DOS mappings, `FLAGS2_32_BIT_ERROR_CODES` changes, and `reply_openerror()`'s special mappings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/fake_file.c -->
# sources/user-network-fs/samba/source3/smbd/fake_file.c

## Purpose
`fake_file.c` implements pseudo-files that Windows clients expect but that are backed by Samba internal state rather than real filesystem objects, currently quota files when quota support is compiled in.

## Important APIs, types, and functions
- `struct fake_file_type` maps fake path prefixes to `enum FAKE_FILE_TYPE` and optional private-data initializers.
- `is_fake_file_path()` and `is_fake_file()` detect fake files by full SMB filename.
- `open_fake_file()` creates a `files_struct` with fd `-1`, initializes a fake-file handle, and calculates the effective access mask.
- `dosmode_from_fake_filehandle()` returns Windows-compatible attributes for quota fake files.
- `close_fake_file()` is a no-op because fake files hold no fd resources.

## Control flow
Path detection compares the start of the full SMB filename to configured fake-file names. Opening requires the effective UID to be Samba's initial/root UID, allocates a normal FSP, marks it non-lockable, sets fnum/vuid/access/name state, initializes type-specific private data, and calls `smbd_calculate_access_mask_fsp()` to enforce normal access semantics before returning the FSP.

## State and persistence behavior
Fake file state is in-memory in `fsp->fake_file_handle` and its optional private data. No real fd is opened and `close_fake_file()` does not persist anything. Quota private data may reflect quota subsystem state outside this file.

## Dependencies and integration points
It depends on `fake_file.h`, auth/current UID helpers, file allocation, access-mask calculation, and optional quota initialization. Close dispatch in `close.c` and DOS mode logic in `dosmode.c` special-case fake file handles.

## Risks and edge cases
- Prefix matching means fake names must be unique and not collide with ordinary paths.
- Open is allowed only while privileged; wrong privilege state causes access denied.
- Non-quota fake-handle type in `dosmode_from_fake_filehandle()` logs an error and returns normal attributes.
- Fake FSPs have fd `-1` and cannot lock; callers must route operations through fake-file-aware paths.

## Test signals
Tests should cover fake path detection, non-fake paths, open privilege failure, quota fake file open with expected attributes, access-mask calculation failure cleanup, and close dispatch without fd operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/fake_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/fd_handle.c -->
# sources/user-network-fs/samba/source3/smbd/fd_handle.c

## Purpose
`fd_handle.c` implements the opaque shared fd-handle object used by `files_struct` instances to store an fd, reference count, current seek position, SMB position information, and generation ID.

## Important APIs, types, and functions
- `fd_handle_create()` allocates a handle initialized with fd `-1` and installs a destructor.
- `fh_get/set_refcount()`, `fh_get/set_position_information()`, `fh_get/set_pos()`, and `fh_get/set_gen_id()` expose opaque fields.
- `fsp_get_io_fd()` returns the fd for real I/O FSPs and rejects pathref FSPs.
- `fsp_get_pathref_fd()` returns the fd regardless of pathref status.
- `fsp_set_fd()` enforces fd assignment invariants.

## Control flow
The destructor asserts the fd has already been closed or is `AT_FDCWD`. `fsp_get_io_fd()` logs and, in developer builds, panics if a path-reference FSP is accidentally used for I/O. `fsp_set_fd()` allows setting the same fd, clearing to `-1`, assigning from `-1`, or setting `AT_FDCWD`, which accommodates VFS modules that assign the fd before the canonical helper does.

## State and persistence behavior
All state is process memory. The fd itself references kernel state but this file does not close it; close is handled by fd/FSP close paths.

## Dependencies and integration points
It depends on talloc and `files_struct` definitions. It is used throughout smbd for I/O position tracking, durable handle generation IDs, duplicate/open reference tracking, and pathref-versus-I/O separation.

## Risks and edge cases
- The destructor assertion catches leaked fds only when teardown reaches the handle.
- Pathref FSP misuse can become invalid-handle errors or developer panics.
- Reference count is manually managed by higher-level FSP code; this file does not enforce ownership.

## Test signals
Tests should validate initial values, getter/setter round trips, destructor assertion behavior with open fds, `fsp_get_io_fd()` rejecting pathrefs, and allowed/disallowed `fsp_set_fd()` transitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/fd_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/fd_handle.h -->
# sources/user-network-fs/samba/source3/smbd/fd_handle.h

## Purpose
`fd_handle.h` declares the opaque fd-handle API used by smbd file structures.

## Important APIs, types, and functions
The header forward-declares `struct fd_handle` and exposes constructor, refcount, position-information, POSIX offset, generation-ID, and FSP fd helper functions: `fd_handle_create()`, `fh_get/set_refcount()`, `fh_get/set_position_information()`, `fh_get/set_pos()`, `fh_get/set_gen_id()`, `fsp_get_io_fd()`, `fsp_get_pathref_fd()`, and `fsp_set_fd()`.

## Control flow
Callers include the header to create handles for new FSPs and interact with fd-related state without knowing the struct layout. The opaque design keeps invariants in `fd_handle.c`.

## State and persistence behavior
No state is stored in the header. Runtime state lives in `struct fd_handle` instances allocated by `fd_handle_create()`.

## Dependencies and integration points
It includes `replace.h` and talloc declarations and depends on `files_struct` being visible to callers that use FSP helpers. It is included by connection/FSP allocation and I/O/close code.

## Risks and edge cases
- Because the struct is opaque, all new field access must be represented by explicit helpers.
- Callers must choose `fsp_get_io_fd()` versus `fsp_get_pathref_fd()` correctly.

## Test signals
Build coverage catches ABI/prototype drift. Runtime behavior is covered by `fd_handle.c` tests and higher-level FSP open/close/pathref tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/fd_handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/file_access.c -->
# sources/user-network-fs/samba/source3/smbd/file_access.c

## Purpose
`file_access.c` implements higher-level access helpers for delete permission, write permission, default ACL inheritance detection, and delete-on-close validation.

## Important APIs, types, and functions
- `can_delete_file_in_directory()` emulates kernel delete checks against parent directory write/delete-child permissions, sticky-bit semantics, share writability, and ACL configuration.
- `can_write_to_fsp()` checks `FILE_WRITE_DATA` through `smbd_check_access_rights_fsp()`.
- `directory_has_default_acl_fsp()` scans a directory DACL for inheritable ACEs.
- `can_set_delete_on_close()` validates readonly attributes, writable share, delete access, root-of-share directories, and non-empty directory status.

## Control flow
Delete-in-directory first rejects read-only shares unless ACL checks are disabled or caller is root. If the supplied dirfsp is not the connection cwd FSP it uses that parent; otherwise it obtains a parent pathref. It verifies the parent is a directory, applies sticky-bit ownership rules, then checks `FILE_DELETE_CHILD` on the parent directory. Delete-on-close validation additionally requires the target not be readonly unless configured, the handle have `DELETE_ACCESS`, and directories be non-root and deletable via `can_delete_directory_fsp()`.

## State and persistence behavior
The file reads security descriptors and stat data but does not persist changes. It can allocate temporary pathrefs/security descriptors that are freed before return.

## Dependencies and integration points
It depends on security descriptor/VFS ACL retrieval, smbd access-right checks, pathref helpers, loadparm ACL/delete settings, and directory deletion checks from `dir.c`. Open/create/set-disposition paths use these checks before granting delete capabilities.

## Risks and edge cases
- Delete permission can come from the file's DELETE bit or parent DELETE_CHILD; this file only checks the parent-side part.
- Sticky-bit directories require owner-of-file or owner-of-directory before ACL checks can help.
- ACL check disabling and root bypass are deliberate configuration/security shortcuts.
- `can_set_delete_on_close()` calls directory emptiness checks, which can race with concurrent creates/deletes.

## Test signals
Tests should cover writable/read-only shares, ACL checks disabled, root bypass, sticky-bit owner/non-owner cases, parent DELETE_CHILD access, default ACL detection, readonly delete policy, delete access missing, root directory delete-on-close denial, and non-empty directory denial.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/file_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/fileio.c -->
# sources/user-network-fs/samba/source3/smbd/fileio.c

## Purpose
`fileio.c` provides core synchronous read, write, modification bookkeeping, write-time update, and fsync helpers for `files_struct` objects.

## Important APIs, types, and functions
- `read_file()` validates range, rejects print files, calls `SMB_VFS_PREAD()`, and updates fd-handle position and SMB position information.
- `write_file()` routes print spool writes, checks write capability, contends level2 oplocks, preserves sticky write times, calls `real_write_file()`, and marks files modified.
- `real_write_file()` validates write ranges, optionally fills sparse gaps under strict allocation, and calls `vfs_pwrite_data()`.
- `trigger_write_time_update_immediate()` updates mtime or forces a ctime change unless POSIX open or sticky write time blocks it.
- `prepare_file_modified()` and `mark_file_modified()` restore forced write times, set modified flags, and set archive attributes after writes.
- `sync_file()` conditionally calls `smb_vfs_fsync_sync()` for strict sync/write-through requests.

## Control flow
Reads and writes both validate VFS ranges and update `fh->pos`. Writes to print files bypass filesystem write and call `print_spool_write()`. Normal writes check `fsp_flags.can_write`, trigger level2 oplock contention, snapshot mtime if write time is forced, perform the pwrite, then mark the FSP modified. Modification bookkeeping restores sticky mtime by calling `smb_set_file_time()` if needed, sets `fsp_flags.modified` once, and sets the archive bit through DOS mode code when configured and not already set.

## State and persistence behavior
Persistent state changes include file data writes, optional sparse preallocation/fill, timestamp changes, archive attribute changes, print spool writes, and fsync. In-memory state includes fd-handle position, position information after reads, `fsp_flags.modified`, and cached stat timestamps updated through lower layers.

## Dependencies and integration points
It depends on VFS pread/pwrite/fsync/range helpers, print spool APIs, oplock contention, DOS mode/attribute setting, timestamp setting, fd-handle accessors, and share options such as strict allocate, store DOS attributes, map archive, strict sync, and sync always.

## Risks and edge cases
- Writes intentionally do not update SMB position information, matching Samba test expectations.
- Sticky write time restoration temporarily clears cached mtime to force lower layers to set the requested time.
- Strict allocation can fail before write if sparse gap filling fails.
- `sync_file()` returns invalid handle for fd `-1`; pathref and fake/print routes must avoid inappropriate sync.
- Archive-bit updates after write can introduce extra metadata failures/notifications.

## Test signals
Tests should cover range validation, read position updates, write position but not position-information behavior, print file writes, permission denial, strict allocation failure, sticky write-time restoration, archive bit setting, modified close notification behavior, immediate mtime/ctime updates, and strict sync/write-through combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/fileio.c -->
