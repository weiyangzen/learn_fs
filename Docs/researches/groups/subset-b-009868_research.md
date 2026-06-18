# Research Report: subset-b-009868

This grouped report covers the Samba `source3/smbd` server lifecycle, security-context, SMB1 AIO, SMB1 IPC, session, reload, and share-access files listed for work item `subset-b-009868`. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/sec_ctx.c -->
# sources/user-network-fs/samba/source3/smbd/sec_ctx.c

## Purpose

`sec_ctx.c` implements the source3 smbd UNIX/security-token context stack. It lets smbd temporarily become root, become an authenticated user, restore previous credentials, and keep the global `current_user` structure synchronized with effective UID/GID, supplementary groups, and NT security tokens. This is central to safe file-service execution because most path, VFS, and share operations rely on the process effective credentials matching the SMB session or temporary root context.

## Important APIs, Types, And Functions

- `unix_token_equal()` compares `security_unix_token` values by UID, GID, group count, and group array bytes.
- `push_sec_ctx()` snapshots the current effective UID/GID, group list, and duplicate NT token into `sec_ctx_stack[++sec_ctx_stack_ndx]`.
- `set_sec_ctx()` and `set_root_sec_ctx()` switch the effective process credentials and update the active stack frame.
- `pop_sec_ctx()` frees the top frame, restores the previous frame's UNIX credentials, and repoints `current_user`.
- `init_sec_ctx()` initializes `sec_ctx_stack[0]` from the process credentials and current groups.
- `sec_ctx_active_token()` walks down the stack to find the most recent non-NULL token during temporary root escalation.
- Static helpers include `become_uid()`, `become_gid()`, `gain_root()`, `get_current_groups()`, and platform-specific `set_unix_security_ctx()`.

The core state comes from `sec_ctx_stack`, `sec_ctx_stack_ndx`, `MAX_SEC_CTX_DEPTH`, `struct sec_ctx`, `struct security_token`, `struct security_unix_token`, and the external `struct current_user current_user`.

## Control Flow

Initialization zeroes the stack, marks all slots invalid, records the initial effective user/group, obtains the supplementary groups through `get_current_groups()`, and initializes `current_user` as guest-like with a NULL NT token. A caller that needs a temporary identity calls `push_sec_ctx()`, then `set_sec_ctx()` or `set_root_sec_ctx()`, and finally `pop_sec_ctx()`. Switching credentials first calls `gain_root()` unless running in non-root mode, then updates supplementary groups with `sys_setgroups()` or Darwin `initgroups`, and finally sets effective GID and UID. After the OS credential switch, the active stack frame is rebuilt and `current_user` is rewritten.

Darwin receives a specialized path because its kernel group list can be a cache; the code follows the required setegid, initgroups, seteuid sequence and caps the group list at `NGROUPS_MAX`.

## State And Persistence Behavior

The file owns in-memory process state only. It mutates real OS effective credentials, group membership, the global context stack, and `current_user`, but does not write persistent storage. The top stack frame owns duplicated group memory and duplicated tokens. A subtle aliasing point is that `current_user.ut.groups` is set to the caller-provided `groups` pointer in `set_sec_ctx_internal()`, while the stack frame stores its own copy. On `pop_sec_ctx()`, `current_user.ut.groups` is repointed to the restored stack frame's group list.

## Dependencies And Integration Points

This module depends on Samba setid wrappers, security token duplication/debugging, profiling macros, global smbd state, `smb_panic()`, `sys_getgroups()`, `sys_setgroups()`, and `reset_chdir_lastconn_cache()`. It integrates with authentication and VFS paths through `current_user`, with root escalation wrappers such as `become_root()`/`unbecome_root()`, and with path access behavior by clearing cached current-directory assumptions after identity changes.

## Risks

Credential switching is high-risk. Stack overflow/underflow panics are intentional safeguards. Failure to restore root in `gain_root()` logs trapdoor warnings but later operations may still be unsafe on unusual systems. Group-list failures panic outside non-root mode. The UID/GID `-1` and 16-bit `65535` warnings flag historically dangerous values but still permit the switch. Any unbalanced push/pop can leave smbd under the wrong credentials. The chdir cache reset is security-relevant because a previously accessible working directory may be inaccessible or misleading under a new user.

## Test Signals

Useful tests include nested `push_sec_ctx()`/`pop_sec_ctx()` balance, `set_sec_ctx()` updating `current_user` and OS effective IDs, root escalation returning to prior tokens, max-depth and underflow panic coverage, Darwin group-list behavior where applicable, and access-control tests that verify VFS operations run under the expected user after session setup and temporary root sections.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/sec_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/server.c -->
# sources/user-network-fs/samba/source3/smbd/server.c

## Purpose

`server.c` is the main smbd parent-process implementation and program entry point. It parses daemon options, initializes global Samba state, starts helper daemons, opens listening sockets for configured SMB transports, accepts clients, forks per-client smbd children, supervises children, fans out parent messages, handles dynamic address changes, and runs the parent tevent loop. It is the central lifecycle coordinator for source3 file serving.

## Important APIs, Types, And Functions

Key local types are `struct smbd_parent_context`, `struct smbd_open_socket`, and `struct smbd_child_pid`. The parent context owns the event and messaging contexts, configured transports, listener list, child PID list, helper daemon server IDs, cleanup timer state, and optional QUIC TLS parameters.

Important functions include `main()`, `open_sockets_smbd()`, `smbd_open_one_socket()`, `smbd_accept_connection()`, `smbd_parent_loop()`, `smbd_setup_sig_chld_handler()`, `remove_child_pid()`, `smbd_notifyd_init()`, `cleanupd_init()`, `smbd_claim_version()`, `smbd_init_addrchange()`, `smbd_addr_changed()`, `smbd_parent_conf_updated()`, `smbd_msg_debug()`, and message fan-out helpers such as `messaging_send_to_children()`.

## Control Flow

`main()` initializes talloc, locale, smbd shims, globals, command-line parsing, logging, random source validation, security context state, signals, clustering, event and messaging contexts, `smb.conf`, loadparm context, daemonization, parent context allocation, transports, optional QUIC TLS state, signal handlers, databases, session/tcon/client global tables, locking, leases, notifyd, cleanupd, scavenger, registry, share-info DB, system and guest session info, and global file/open state. It rejects unsupported standalone AD DC mode unless inhibited and claims a cluster-wide Samba version lock when clustered upgrades are not allowed.

For daemon mode, it opens listener sockets according to `server smb transports` or `--port`; for inetd mode, it duplicates fd 0 and directly calls `smbd_process()`. Listener setup binds either configured interfaces only or wildcard IPv6/IPv4 addresses, registers parent messaging handlers, optionally starts mDNS registration, and enters `tevent_loop_wait()`.

On accept, interactive mode handles the connection in-process after reinit. Normal daemon mode checks `max smbd processes`, forks, frees the parent context in the child, reinitializes after fork, optionally performs a synchronous QUIC TLS handshake, and calls `smbd_process()`. The parent closes the accepted fd, records the child PID, and checks log size. `SIGCHLD` reaps exits and `remove_child_pid()` restarts `cleanupd` or `notifyd` if those helper daemons died; ordinary children are stored in `cleanupdb` and may trigger cleanupd.

## State And Persistence Behavior

The file maintains in-memory parent state and process state. It creates pid files, lock/pid/ncalrpc directories, named-pipe directories, global messaging/server/session/tcon/client/open databases, share-info DB handles, locks, memcache, registry state, and helper daemon identities. `smbd_claim_version()` uses `g_lock` to store and hold the running Samba version in a cluster-sensitive lock record. Dynamic interface handling adds/removes listener sockets and sends `MSG_SMB_IP_DROPPED` when a bound address disappears.

## Dependencies And Integration Points

The file integrates with almost every smbd subsystem: loadparm, secrets/passdb, messaging, server IDs, profile, cluster/CTDB, notifyd, cleanupd, scavenger, leases, locking, share modes, registry, DCERPC endpoint setup, QUIC/TLS, socket helpers, mDNS/Avahi/DNSSD, auth session info, global contexts, and child `smbd_process()`. Parent message handlers propagate config reloads, debug changes, forced tree disconnects, client-kill requests, ID cache invalidations, notify-start events, TLS reloads, and dynamic IP drops to children.

## Risks

This file has high blast radius. Initialization order matters: event context before messaging, password DB before global SAM SID, ncalrpc directory before endpoint mapper races, daemonization before parent-child pipe setup, and QUIC filtering before listener bind. Fork paths must not retain parent-only talloc state. Child-count enforcement depends on reliable SIGCHLD reaping. Helper daemon restart loops can hide repeated startup failures but log them. Listener binding tolerates individual socket failures, but inconsistent partial binding across transports can abort startup. QUIC support depends on compile-time `HAVE_LIBQUIC`, TLS parameter preparation, and runtime enablement.

## Test Signals

Coverage signals include daemon and inetd startup tests, foreground stdin EOF shutdown, reload-on-SIGHUP, parent-to-child message fan-out, max-process limit behavior, helper daemon restart after exit, listener binding under `bind interfaces only`, dynamic address add/drop handling, QUIC requested/enabled/disabled paths, clustered version conflict rejection, and failure injection for database or directory initialization order. Integration tests should observe pidfile creation/removal and successful client fork/process cleanup.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/server_exit.c -->
# sources/user-network-fs/samba/source3/smbd/server_exit.c

## Purpose

`server_exit.c` centralizes smbd shutdown and post-fork reinitialization. It provides clean and abnormal server-exit entry points, tears down client connections, sessions, tree connects, global contexts, locking, profiling, and pidfiles, and wraps `reinit_after_fork()` with password database reinitialization for smbd forks.

## Important APIs, Types, And Functions

The main local enum is `enum server_exit_reason` with `SERVER_EXIT_NORMAL` and `SERVER_EXIT_ABNORMAL`. `exit_server_common()` is the `_NORETURN_` implementation behind `smbd_exit_server()` and `smbd_exit_server_cleanly()`. `log_writeable_file_fn()` is a `files_forall()` callback used when `log writeable files on exit` is enabled. `smbd_reinit_after_fork()` calls the generic fork reinit path and then `initialize_password_db(true, ev_ctx)`.

## Control Flow

`exit_server_common()` is guarded by `exit_firsttime` so recursive shutdown exits immediately. It chooses a disconnect status based on clean or abnormal shutdown, removes the global SMBX client from the multichannel registry early, repeatedly returns to root context, disconnects transports, optionally logs writable files, disconnects SMB1 tree connects, logs off all SMBX sessions, frees remaining connection objects, destroys DMAPI session for the parent when compiled, frees `sconn`, closes netlogon credentials DB, dumps profiling, frees global messaging and event contexts, frees smbd memcache, and ends locking. Abnormal shutdown calls `smb_panic(reason)`; normal shutdown logs a notice, removes the smbd pidfile if this is the parent, and exits with code 0.

## State And Persistence Behavior

The function mutates global singleton state: `global_smbXsrv_client`, `global_messaging_context`, `global_event_context`, `smbd_memcache_ctx`, locking state, DMAPI session state, netlogon credentials global DB state, and the parent pidfile. It also disconnects transport/session/tcon state that may have persistent TDB records elsewhere. The writable-file logging path is observational and does not close files directly.

## Dependencies And Integration Points

This file depends on SMBX client/session/tcon APIs, file table traversal, pidfile helpers, profiling, global context free routines, locking teardown, netlogon credential DB management, password DB initialization, and optional DMAPI. It is reached through smbd shim functions, signal/message handlers, child process exits, AIO/IPC send failures, and fatal initialization errors.

## Risks

Shutdown ordering is critical because messaging and event contexts are not direct talloc children of the server connection. Calling transport disconnect after removing the client prevents new multichannel work during teardown. Many cleanup operations log but continue on failure; incomplete tcon/session cleanup may require later cleanupd/scavenger work. Abnormal exits deliberately panic after cleanup, so code paths must avoid calling the abnormal wrapper for normal transport termination. Reentrant exit is flattened to `exit(0)`, which avoids loops but can mask a second failure.

## Test Signals

Tests should exercise clean child exit, abnormal panic path, recursive exit guard, writable-file-on-exit logging, tcon/session cleanup failure logging, pidfile unlink only for parent, and fork reinitialization refreshing passdb state. Integration signals include no leaked global messaging/event contexts after clean exit and expected client disconnect statuses.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/server_exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/server_reload.c -->
# sources/user-network-fs/samba/source3/smbd/server_reload.c

## Purpose

`server_reload.c` handles runtime service/printer reloads for smbd. It detects changed configuration files, reloads `smb.conf` shares, refreshes socket options, invalidates caches, and manages auto-loaded printer shares from the persistent pcap cache populated by the background print process.

## Important APIs, Types, And Functions

- `snum_is_shared_printer()` identifies browseable, valid, printable services.
- `delete_and_reload_printers()` reloads printer services from pcap state and removes stale auto-loaded printer shares not currently used.
- `reload_services()` reloads the active services file and share definitions, kills unused services, reopens logs, refreshes interfaces, reapplies socket options to active SMBX connections, and resets name-mangling and free-space caches.
- Static state `reload_last_pcap_time` suppresses duplicate printer reloads when the pcap cache has not changed.

## Control Flow

Printer reload first checks `load printers`, creates a stack frame, validates that pcap cache is loaded, compares pcap timestamp against `reload_last_pcap_time`, calls `load_printers()`, iterates existing services, skips the special `printers` service and non-printer services, and kills stale auto-loaded printer services when the printer name no longer exists and no connection uses that service. It then calls `load_printers()` again to ensure deleted printers are gone.

`reload_services()` checks for `include`/next-config changes through `lp_next_configfile()`, updates the dynamic config path if needed, reopens logs, short-circuits test reloads when the file list has not changed, kills unused services, loads config with shares, recursively retests when the config path was not a test reload, reopens logs again, reloads interfaces, reapplies keepalive and configured socket options to each active connection, and flushes mangle/free-space caches.

## State And Persistence Behavior

This file changes in-memory loadparm service tables, dynamic config filename state, printer service state, interface lists, socket options, and process caches. It does not directly persist config, but it consumes persistent pcap cache metadata and affects whether auto-loaded printer service definitions remain present. The `reload_last_pcap_time` static timestamp is per-process state, so each smbd can independently decide whether pcap-backed printer inventory changed.

## Dependencies And Integration Points

Dependencies include loadparm, pcap cache, printer list/load APIs, connection service-use checks, logging, interface loading, socket option setters, mangle cache, and dfree cache. Parent and child smbd processes call `reload_services()` from SIGHUP or `MSG_SMB_CONF_UPDATED` paths, while printer enumeration or pcap callbacks call `delete_and_reload_printers()`.

## Risks

Reload behavior must avoid removing services still in use; `connections_snum_used()` is the guard for printer services. Recursive `reload_services(..., true)` after a non-test load depends on `lp_file_list_changed()` to prevent unnecessary work. Socket option application assumes active connection sockets remain valid. Printer cache timestamp handling can skip reloads if the pcap producer fails to update time correctly.

## Test Signals

Test signals include SIGHUP/config-update reloads, included config-file path changes, unchanged test reload short-circuit, stale auto-loaded printer removal, active printer service preservation, socket option refresh on existing connections, and cache invalidation after share changes. Printer tests should cover disabled `load printers` and missing pcap cache.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/server_reload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/session.c -->
# sources/user-network-fs/samba/source3/smbd/session.c

## Purpose

`session.c` handles smbd session registration with PAM and utmp and provides APIs to list or filter recorded SMB sessions. It bridges SMBX session lifecycle with system login/session accounting, while avoiding expensive PAM work for guest or lower-than-user security contexts.

## Important APIs, Types, And Functions

- `session_claim()` is called when a session is created and claims PAM/utmp state for non-guest users.
- `session_yield()` is called when a session is destroyed and releases utmp/PAM state.
- `list_sessions()` returns active sessionid records.
- `find_sessions()` returns active sessionid records matching username and remote machine filters.
- `gather_sessioninfo()` is the traversal callback that filters sessionid DB records and drops records whose process no longer exists.
- `struct session_list` carries traversal memory context, count, filters, and the accumulated `struct sessionid` array.

## Control Flow

On claim, the function fetches `auth_session_info` from `session->global`, skips registration unless `security_session_user_level()` is at least `SECURITY_USER`, formats an ID string as `smb/<session_global_id>`, asserts that source3 has a `unix_token`, obtains the Unix username and first channel remote name, calls `smb_pam_claim_session()`, and optionally writes utmp if `lp_utmp()` is enabled. On yield, it formats the same ID, asserts the Unix token, obtains username/hostname, removes utmp if configured, and closes the PAM session.

Listing and finding sessions traverse the sessionid database through `sessionid_traverse_read()`. The callback applies optional exact user and machine filters, skips dead PIDs using `process_exists()`, reallocates the output array under the caller's context, copies the record, and increments the count.

## State And Persistence Behavior

This file writes to external system/session accounting through PAM and utmp helpers. It reads the Samba sessionid database for list/find operations but does not itself create sessionid records in this file. Returned arrays are talloc-owned by the caller's context. PAM/utmp identifiers derive from `session_global_id`, making claim/yield pairing dependent on stable SMBX session global state.

## Dependencies And Integration Points

It depends on `smbXsrv_session`, `auth_session_info`, security session-level helpers, PAM wrappers, utmp wrappers, sessionid DB traversal, process-existence checks, loadparm `utmp`, and tsocket/security headers. It integrates with session setup/logoff and administrative session enumeration features.

## Risks

Guest-session skip is intentional for performance, but any incorrect security level could skip accounting. The code assumes `channels[0].remote_name` is valid. `SMB_ASSERT(session_info->unix_token)` makes missing Unix-token setup a hard failure in source3. Listing silently filters dead PIDs, so stale DB records may not be visible to callers. `talloc_realloc()` failure resets count and aborts traversal with `-1`; callers receive zero sessions after the error path logs.

## Test Signals

Tests should cover non-guest claim/yield invoking PAM and utmp with matching IDs, guest skip behavior, disabled utmp behavior, PAM claim rejection returning false, list/find filtering by user and machine, dead-PID filtering, traversal failure handling, and missing Unix-token assertions in developer/selftest builds.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/share_access.c -->
# sources/user-network-fs/samba/source3/smbd/share_access.c

## Purpose

`share_access.c` evaluates share-level access rules against a user's security token. It implements membership checks for `invalid users`, `valid users`, `read list`, and `write list`, using expanded names and SID-based token comparisons rather than trusting text names directly.

## Important APIs, Types, And Functions

- `token_contains_name_in_list()` iterates a NULL-terminated list of configured names/groups, expands/evaluates each through `token_contains_name()`, and reports whether any entry matches the token.
- `user_ok_token()` denies users listed in `invalid users`, requires membership in `valid users` when configured, and otherwise permits access.
- `is_share_read_only_for_token()` starts from `conn->read_only`, forces read-only on `read list` match, and allows write on `write list` match.

Inputs include username, domain, share name/service number, `struct security_token`, loadparm list values, and connection state.

## Control Flow

The shared helper starts with `*match = false`, treats a NULL list as success/no match, and for each entry creates a stackframe, calls `token_contains_name()` with username/domain/share/token/list entry, frees the frame, returns false on lookup/evaluation failure, returns true immediately on match, and otherwise continues.

`user_ok_token()` first checks `invalid users`; a match denies immediately. It then checks `valid users`; if configured and no match is found, access is denied. `is_share_read_only_for_token()` checks `read list` first and sets `read_only = true` on match, then checks `write list` and sets `read_only = false` on match, so `write list` can override a prior read-list match.

## State And Persistence Behavior

No persistent state is written. The functions read live loadparm share parameters and connection state and return decisions through booleans or `_read_only`. Temporary talloc stackframes isolate substitution/lookup allocations for each list entry. The final read-only decision is not stored here; the caller must apply it to connection/session behavior.

## Dependencies And Integration Points

This file depends on loadparm share accessors, loadparm global substitution context, `token_contains_name()`, security tokens, `connection_struct`, and debug logging. It integrates with tree connect/share access setup and with later file-open decisions through the share read-only result.

## Risks

Access decisions rely on SID comparisons after name lookup, which is safer than text comparison but sensitive to lookup failures. The helper returns false on lookup error, and callers treat that as denial. List ordering is simple OR matching; there is no negative entry precedence inside a single list. `write list` overriding `read list` is an intentional semantic that tests should preserve. Repeated `lp_servicename(talloc_tos(), ...)` calls depend on the surrounding talloc stack behavior.

## Test Signals

Tests should cover NULL lists, direct user entries, domain-qualified names, group/netgroup entries, lookup failure denial, `invalid users` precedence over `valid users`, configured `valid users` requiring membership, `read list` forcing read-only, `write list` overriding read-only, and substituted share/user names in list entries.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/share_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_aio.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_aio.c

## Purpose

`smb1_aio.c` schedules and completes asynchronous SMB1 ReadX and WriteX operations using the VFS async interfaces and tevent callbacks. It builds SMB1 replies ahead of time, holds strict-lock context for the operation, tracks outstanding requests on the file handle, updates file offsets/modification state, and sends the final SMB1 response when the async operation completes.

## Important APIs, Types, And Functions

- `schedule_aio_read_and_X()` validates and schedules an async pread for SMB1 ReadX.
- `aio_pread_smb1_done()` completes the pread, builds success/error response, updates file position, and sends the reply.
- `schedule_aio_write_and_X()` validates and schedules async pwrite/fsync work for SMB1 WriteX.
- `aio_pwrite_smb1_done()` completes the write, marks file modified, handles write-behind semantics, and sends the reply when required.

The code uses `struct aio_extra`, `struct smb_request`, `files_struct`, `connection_struct`, strict-lock structs, `vfs_aio_state`, and VFS async request APIs.

## Control Flow

Read scheduling rejects invalid ranges, alternate streams, reads below `aio read size` unless forced, and chained SMB requests. It allocates `aio_extra` with enough output buffer space, constructs a fixed SMB1 ReadX reply, initializes a read strict lock, checks the lock, records byte count and offset, starts `SMB_VFS_PREAD_SEND()`, attaches the callback, adds the tevent request to the file's AIO list, moves ownership of the SMB request under `aio_extra`, and returns `NT_STATUS_OK`.

Read completion receives the VFS result, handles the file-closed-while-outstanding case, maps errors to SMB status, or calls `setup_readX_header()` on success and updates file position. It sets the NetBIOS length, logs/shows the message, sends through `smb1_srv_send()`, and frees `aio_extra`.

Write scheduling follows similar gating for streams, minimum size, and chains. It constructs a WriteX reply, initializes a write strict lock, prepares modified state, sends `pwrite_fsync_send()`, records the request, triggers level2 oplock contention hooks, and optionally sends an immediate success reply for write-behind when not write-through, not `sync always`, and `aio_write_behind` is set.

Write completion receives the write/fsync result, handles closed files, marks the file modified, logs write-behind errors without notifying the client, or builds/sends normal success/error/disk-full responses.

## State And Persistence Behavior

The module keeps per-operation state in `aio_extra` and outstanding tevent requests linked to `fsp` by `aio_add_req_to_fsp()`. It updates file handle position and position-information state after successful reads/writes and marks modification state for writes. It does not persist metadata directly; persistence happens through the VFS write/fsync path. Write-behind can acknowledge before data durability is known.

## Dependencies And Integration Points

Dependencies include SMB1 reply builders, VFS async read/write/fsync functions, strict locking, AIO request tracking, oplock contention hooks, file-handle position helpers, error mapping, encryption checks, and server exit on send failure. It integrates with SMB1 ReadX/WriteX handlers that fall back to synchronous behavior on `NT_STATUS_RETRY`.

## Risks

Write-behind is explicitly risky: later errors are logged as potential corruption and the TODO notes success should not be returned on error. Strict locks are checked at scheduling time and held conceptually until completion; incorrect lifetime can violate locking. Chained SMB requests are rejected to avoid complex reply ordering. The file-closed callback path drops the reply, so higher layers must tolerate closed handles with outstanding AIO. Send failure exits the server cleanly.

## Test Signals

Tests should cover minimum-size retry, forced AIO, alternate-stream retry, chained-request retry, invalid read range, strict-lock conflict, allocation failure, VFS send failure fallback, read success/error response formatting, partial write disk-full mapping, write-through/fsync behavior, write-behind early reply and later error logging, closed-file completion, encrypted connection send flag, and file-position updates.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_aio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_aio.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_aio.h

## Purpose

`smb1_aio.h` declares the SMB1 asynchronous ReadX and WriteX scheduling entry points implemented by `smb1_aio.c`. It is the narrow interface used by SMB1 command handling code to attempt async I/O and fall back to normal synchronous handling when async scheduling is not applicable.

## Important APIs, Types, And Functions

The header exports:

- `NTSTATUS schedule_aio_read_and_X(connection_struct *conn, struct smb_request *req, files_struct *fsp, off_t startpos, size_t smb_maxcnt);`
- `NTSTATUS schedule_aio_write_and_X(connection_struct *conn, struct smb_request *req, files_struct *fsp, const char *data, off_t startpos, size_t numtowrite);`

The declarations depend on `connection_struct`, `struct smb_request`, `files_struct`, `off_t`, `size_t`, and `NTSTATUS` types provided by the broader smbd include environment.

## Control Flow

This header has no executable control flow. Its integration contract is status-driven: callers invoke a scheduler during SMB1 ReadX/WriteX processing. `NT_STATUS_OK` means the request ownership has moved into async state and a later callback will send the SMB1 reply. `NT_STATUS_RETRY` means async was declined and the caller should use the synchronous path. Other errors such as invalid parameter, no memory, or file-lock conflict can be returned directly to the client.

## State And Persistence Behavior

The header owns no state. Its prototypes imply that the implementation may take ownership of `req` on success and may write data through VFS async mechanisms for writes. Callers must not assume the request remains available after successful scheduling.

## Dependencies And Integration Points

The header integrates SMB1 command dispatch with the async implementation. It should be included only where the smbd core types are already visible. Its main dependency is the ABI consistency with `smb1_aio.c`; parameter order and ownership expectations are part of the implicit contract.

## Risks

The largest risk is caller misuse of the status/ownership contract. Treating `NT_STATUS_OK` as if a reply still needs to be sent synchronously would duplicate responses, while using `req` after successful scheduling could become a lifetime bug. Adding parameters or changing return semantics requires auditing SMB1 ReadX/WriteX callers.

## Test Signals

Build tests should catch prototype drift. Behavioral tests should assert that SMB1 ReadX/WriteX callers fall back on `NT_STATUS_RETRY`, return immediate errors for hard failures, and do not send duplicate replies after `NT_STATUS_OK`.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_aio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_ipc.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_ipc.c

## Purpose

`smb1_ipc.c` implements SMB1 `SMBtrans` and `SMBtranss` handling for IPC named-pipe and mailslot-style transaction paths. It assembles multi-packet transaction requests, dispatches LANMAN or named-pipe operations, performs async DCE/RPC write/read cycles on pipe handles, and fragments transaction replies according to the negotiated SMB1 max send size.

## Important APIs, Types, And Functions

- `send_trans_reply()` sends one or more SMBtrans reply packets with parameter/data offsets and optional buffer-overflow status.
- `reply_trans()` parses the primary SMBtrans request, allocates a `trans_state`, copies initial params/data/setup, and either waits for secondary packets or dispatches.
- `reply_transs()` handles secondary SMBtrans packets and dispatches when all bytes arrive.
- `handle_trans()` validates `\PIPE` names and routes to `named_pipe()`.
- `named_pipe()` routes `LANMAN` to `api_reply()` and known pipe names or empty names to `api_fd_reply()`.
- `api_fd_reply()` validates pipe handle/VUID and dispatches pipe subcommands.
- `api_dcerpc_cmd()` writes request data to a named pipe and asynchronously reads the response.
- `api_dcerpc_cmd_write_done()` and `api_dcerpc_cmd_read_done()` complete the pipe I/O.
- `api_WNPHS()`, `api_SNPHS()`, and `api_no_reply()` handle minor pipe commands or unsupported calls.

Important local state includes `struct dcerpc_cmd_state` and the externally defined `struct trans_state`.

## Control Flow

`reply_trans()` validates word count and offsets, rejects duplicate/invalid transaction state through `allow_new_trans()`, allocates request buffers with 100 bytes of zero slack for legacy core routines, parses setup words, and either stores incomplete state in `conn->pending_trans` with an interim response or calls `handle_trans()`. `reply_transs()` finds the matching pending transaction by MID, optionally shrinks totals if the client revised them downward, validates displacement/count ranges with `smb_buffer_oob()`, copies bytes into the accumulated buffers, and dispatches once complete.

`handle_trans()` accepts WinCE-style local-machine prefixes, requires a `\PIPE` path, normalizes optional slash behavior, and calls `named_pipe()`. `named_pipe()` treats `LANMAN` as the old RAP/LANMAN API path; selected pipe names from Win9x are routed through an already-open pipe handle path; empty names also use fd dispatch. After dispatch, `close_on_completion` can disconnect the tree connection and free the tcon.

For DCE/RPC pipe commands, `api_fd_reply()` validates setup count, file handle, named-pipe type, and VUID. `api_dcerpc_cmd()` rejects concurrent pipe reads, copies request data, sends `np_write_send()`, then reads up to the requested max with `np_read_send()`. Completion maps named-pipe NTSTATUS values with `nt_status_np_pipe()`, sends errors directly, or uses `send_trans_reply()` with `is_data_outstanding` as the buffer-overflow/more-data signal.

## State And Persistence Behavior

The module stores incomplete transactions on `conn->pending_trans` and owns malloc-allocated param/data buffers until completion or error. Async DCE/RPC state is attached to `req->async_priv` and the request is moved under the connection until callbacks finish. It mutates tree-connect state when `close_on_completion` is set. It does not persist data itself; named-pipe I/O talks to the RPC pipe subsystem and connection/session state.

## Dependencies And Integration Points

Dependencies include SMB1 request/reply helpers, transaction state management, named-pipe fake file handles, RPC pipe handlers, LANMAN `api_reply()`, profile macros, security/encryption send flags, file lookup by FID, SMBX tcon disconnect, and buffer-boundary helpers. It integrates with SMB1 command dispatch and with the source3 RPC server pipe machinery.

## Risks

SMBtrans parsing is boundary-sensitive. Incorrect offsets, displacements, or revised totals can corrupt buffers; this file uses `smb_buffer_oob()` guards before copies. Memory ownership is mixed between talloc and `SMB_MALLOC`, so every bad-parameter path must free both correctly. Async pipe requests require careful request lifetime management. `send_trans_reply()` fragments by `max_send` with a fixed overhead hack; regressions can break old SMB1 clients. `close_on_completion` disconnects the tcon after dispatch and exits the server on disconnect failure, so outstanding request cancellation remains a TODO risk.

## Test Signals

Tests should cover complete primary transactions, multi-packet primary/secondary assembly, duplicate MID rejection, offset/displacement OOB rejection, downward total revision, LANMAN routing, `\PIPE` prefix normalization, unknown pipe rejection, invalid pipe handle/VUID, DCE/RPC write/read success, pipe busy, pipe error mapping, more-data/buffer-overflow replies, fragmented replies under small max-send values, and close-on-completion tcon disconnect.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_ipc.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_ipc.h

## Purpose

`smb1_ipc.h` declares the public SMB1 IPC transaction functions implemented by `smb1_ipc.c`. It exposes the reply-fragmentation helper and the primary/secondary SMBtrans command handlers used by SMB1 dispatch.

## Important APIs, Types, And Functions

The header exports:

- `send_trans_reply(connection_struct *conn, struct smb_request *req, char *rparam, int rparam_len, char *rdata, int rdata_len, bool buffer_too_large);`
- `reply_trans(struct smb_request *req);`
- `reply_transs(struct smb_request *req);`

The prototypes depend on `connection_struct`, `struct smb_request`, integer lengths, and the boolean type supplied by the smbd include environment.

## Control Flow

The header itself has no executable control flow. Its contract is that SMB1 command dispatch calls `reply_trans()` for primary `SMBtrans` packets and `reply_transs()` for secondary packets. Other IPC/RPC code can use `send_trans_reply()` to emit correctly formatted SMBtrans responses, including fragmented replies and buffer-overflow/more-data signaling.

## State And Persistence Behavior

No state is owned by the header. The declared implementation may mutate request output buffers, pending transaction lists, connection/tcon state, and async request ownership. Callers must treat these functions as SMB request handlers that may send replies immediately, defer replies asynchronously, or disconnect state on close-on-completion.

## Dependencies And Integration Points

This header is the interface between SMB1 protocol dispatch and the IPC transaction implementation. It also allows named-pipe/RPC paths to share transaction response formatting without duplicating SMB1 wire-layout code.

## Risks

Because `send_trans_reply()` accepts raw parameter/data pointers and signed lengths, callers must pass valid buffers and lengths that match the negotiated transaction semantics. Misuse can produce malformed SMB1 replies. Command handlers own complex request lifetimes; dispatch code must not send additional replies after handlers defer or complete a transaction.

## Test Signals

Build tests catch prototype drift. Protocol tests should verify that dispatch reaches `reply_trans()`/`reply_transs()` for the right SMB commands and that users of `send_trans_reply()` produce correctly fragmented responses for normal and buffer-too-large cases.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_ipc.h -->
