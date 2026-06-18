# Research: subset-b-009812

Grouped research for Samba source3 NetAPI user/workstation support, transfer helpers, server identity/session/share-security helpers, smbconf registry bindings, and smbd shim files. Each section preserves the source path and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/user.c -->
# sources/user-network-fs/samba/source3/lib/netapi/user.c

## Purpose
This file implements source3 libnetapi user-management calls on top of remote SAMR RPC. It covers `NetUserAdd`, `NetUserDel`, `NetUserEnum`, `NetQueryDisplayInformation`, `NetUserGetInfo`, `NetUserSetInfo`, `NetUserModalsGet`, `NetUserModalsSet`, `NetUserGetGroups`, `NetUserSetGroups`, and `NetUserGetLocalGroups`; local entry points redirect to localhost through `LIBNETAPI_REDIRECT_TO_LOCALHOST`.

## Important APIs, Types, And Functions
The central internal type is `USER_INFO_X`, a normalized view of many NetAPI `USER_INFO_*` input levels. `construct_USER_INFO_X()` reads caller buffers for levels 0, 1, 2, 3, 1003, 1006, 1007, 1009, 1011, 1012, 1014, 1024, 1051, 1052, and 1053. `convert_USER_INFO_X_to_samr_user_info21()` marks SAMR fields present and builds `samr_UserInfo21`; `set_user_info_USER_INFO_X()` sends it via SAMR info level 21, 23, or 25 depending on whether a password is supplied and whether `SetUserInfo2` supports encrypted password level 25.

Read paths use `libnetapi_samr_lookup_user()` and `libnetapi_samr_lookup_user_map_USER_INFO()` to open users, query level 21, query DACLs, derive builtin alias membership auth flags, and map to NetAPI levels 0, 1, 2, 3, 4, 10, 11, 20, and 23. Domain policy helpers map SAMR domain info classes 1, 3, 5, 6, 7, and 12 to `USER_MODALS_INFO_*` structures. Group helpers create `GROUP_USERS_INFO_0/1` and `LOCALGROUP_USERS_INFO_0` arrays.

## Control Flow
Every remote public function opens a SAMR pipe, opens the account domain and sometimes the builtin domain, validates level-specific access masks, performs lookup/open/query/set calls, maps `NTSTATUS` to `WERROR`, and conditionally closes cached handles when `ctx->disable_policy_handle_cache` is set. `NetUserAdd_r()` creates a user with `samr_CreateUser2`, validates the account flags, obtains the transport session key for password encryption, sets attributes, and deletes the created user on post-create failure. `NetUserDel_r()` removes the SID from the foreign builtin domain before deleting the user. Enumeration first calls `samr_EnumDomainUsers`, then expands every returned RID through the same per-user mapper. Group setting computes add and delete RID lists by diffing requested group membership against `samr_GetGroupsForUser`.

## State And Persistence
The file itself stores no durable state. Persistent effects are SAMR account database changes: users, passwords, attributes, domain password/lockout policy, and group membership. It also depends on libnetapi policy-handle caches and talloc ownership for output buffers. Password setting depends on the RPC transport session key and encrypted SAMR password blobs.

## Dependencies And Integration Points
It integrates `librpc/gen_ndr/libnetapi.h`, source3 libnetapi private helpers, generated SAMR client stubs, LSA string initialization, DS account flag mappings, SID utilities, security descriptors, and RPC pipe/session-key helpers. Builtin alias checks use well-known alias RIDs to emulate NetAPI auth flags such as print/server/account operators.

## Risks And Test Signals
Risk concentrates around incomplete level support, level-to-access-mask mismatches, stale policy-handle cache behavior, password encryption fallback, time conversions, memory ownership of ADD_TO_ARRAY outputs, and correctness of builtin/domain SID membership mapping. `NetUserGetLocalGroups_r()` collects aliases from both domain and builtin handles but then resolves all RIDs through the builtin handle, which is worth regression coverage for domain-local aliases. Tests should exercise supported and rejected info levels, add rollback, delete with builtin membership, pagination/resume status from enumeration, modals get/set levels 0/3/1001-1005, password set level 1003, group diff add/delete idempotence, and SAMR partial status such as `STATUS_SOME_UNMAPPED`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/wkstainfo.c -->
# sources/user-network-fs/samba/source3/lib/netapi/wkstainfo.c

## Purpose
This file implements `NetWkstaGetInfo` for source3 libnetapi. It exposes workstation metadata levels 100, 101, and 102 by calling the WKSSVC RPC endpoint and mapping generated `wkssvc_NetWkstaInfo` unions into libnetapi `WKSTA_INFO_*` output buffers.

## Important APIs, Types, And Functions
`NetWkstaGetInfo_l()` redirects local calls to localhost. `NetWkstaGetInfo_r()` validates `r->out.buffer`, accepts only levels 100, 101, and 102, obtains a WKSSVC binding handle with `libnetapi_get_binding_handle()`, calls `dcerpc_wkssvc_NetWkstaGetInfo()`, and maps RPC output through `map_wksta_info_to_WKSTA_INFO_buffer()`. The mapper populates platform id, computer name, workgroup/domain, version major/minor, LAN root for 101/102, and logged-on user count for 102.

## Control Flow
The remote wrapper is linear: validate level, bind, call RPC, check both transport `NTSTATUS` and returned `WERROR`, then allocate the requested NetAPI structure into the caller's buffer with `ADD_TO_ARRAY`. Unsupported levels return `WERR_INVALID_LEVEL`; mapper unsupported cases return `NT_STATUS_NOT_SUPPORTED`, converted to `WERROR`.

## State And Persistence
The file has no durable state. Outputs are talloc-allocated from the libnetapi context passed to the mapper. Remote state is read-only workstation service state from the target server.

## Dependencies And Integration Points
It depends on generated libnetapi and WKSSVC NDR headers, source3 libnetapi binding helpers, and talloc array utilities. It includes smbconf headers but does not directly use smbconf functions in this file.

## Risks And Test Signals
Risk is modest: null `out.buffer`, level validation, correct union member use for each level, and string allocation failures. Tests should call levels 100/101/102 against a local server, verify fields are copied, verify invalid levels fail, and inject RPC/binding failures if the test harness supports mocks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/wkstainfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/per_thread_cwd.c -->
# sources/user-network-fs/samba/source3/lib/per_thread_cwd.c

## Purpose
This file provides a runtime gate for per-thread current working directories on platforms that support `unshare(CLONE_FS)`. Samba helper threads can isolate their CWD from the process main thread when the platform and container policy allow it.

## Important APIs, Types, And Functions
`per_thread_cwd_check()` must be called first, normally before threads are created. It attempts `unshare(CLONE_FS)` once when `HAVE_UNSHARE_CLONE_FS` is available, caches support in `_per_thread_cwd_supported`, and disables activation for the calling main thread. `per_thread_cwd_supported()` asserts the check was done and returns the cached result. `per_thread_cwd_disable()` marks the current thread as not allowed to activate. `per_thread_cwd_activate()` asserts prior checking/support and calls `unshare(CLONE_FS)` once per helper thread.

## Control Flow
Support discovery is cached globally in `_per_thread_cwd_checked`. Per-thread state uses `__thread` booleans for disabled and activated state. Activation is idempotent per thread but forbidden after disabling. Without compile-time support, activation panics.

## State And Persistence
State is only process memory. The externally visible effect is kernel task filesystem-context separation, affecting future `chdir` behavior for the calling thread. There is no disk persistence.

## Dependencies And Integration Points
The file depends on Samba assertions and optionally Linux `<sched.h>`. It is intended for startup and helper-thread code paths that need CWD changes without disturbing other threads.

## Risks And Test Signals
The runtime check can permanently unshare the main thread during probing, which is intentional but means call order matters. Container security policy can block `unshare` even when headers expose it. Tests should verify check-before-query assertions, unsupported platform panic behavior, idempotent activation, disable-before-activate assertion, and behavior after fork where `per_thread_cwd_disable()` marks the new main thread.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/per_thread_cwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/privileges.c -->
# sources/user-network-fs/samba/source3/lib/privileges.c

## Purpose
This file implements source3 privilege assignment storage and lookup. It maps SIDs to Samba security privilege bitmasks in the account policy database and exposes helpers used by LSA privilege enumeration, grant, revoke, and account management paths.

## Important APIs, Types, And Functions
Records are keyed as `PRIV_<SID>` and store an eight-byte little-endian privilege mask. `map_old_SE_PRIV()` preserves compatibility with older 16-byte `SE_PRIV` records written in native byte order. `get_privileges()` and `set_privileges()` are the private database accessors gated by `lp_enable_privileges()` and `get_account_pol_db()`. Public APIs include `get_privileges_for_sids()`, `get_privileges_for_sid_as_set()`, `privilege_enumerate_accounts()`, `privilege_enum_sids()`, `grant_privilege_by_name()`, `grant_privilege_set()`, `revoke_privilege_set()`, `revoke_all_privileges()`, `revoke_privilege_by_name()`, `privilege_create_account()`, `privilege_delete_account()`, `is_privileged_sid()`, and `grant_all_privileges()`.

## Control Flow
Lookup fetches one SID record, decodes old or current formats, and returns false for disabled privileges, absent database, absent key, or malformed data. Enumeration traverses the account policy DB, filters keys by prefix, optionally filters by a requested privilege mask, rejects the invalid `S-0-0` SID, parses SIDs, and accumulates them in a talloc-owned array. Grants OR new masks into existing masks; revokes clear bits; deleting an account removes the key.

## State And Persistence
Privilege assignments are durable in Samba's account policy database through dbwrap. No transaction grouping is used around read-modify-write grant/revoke operations in this file, so concurrent updates can race unless callers serialize them elsewhere.

## Dependencies And Integration Points
It depends on dbwrap, passdb account-policy access, SID utilities, privilege conversion helpers from `libcli/security/privileges_private.h`, and loadparm `enable privileges`. It feeds LSA RPC semantics through `PRIVILEGE_SET` conversion.

## Risks And Test Signals
Important risks include disabled privilege mode silently returning no records, malformed legacy records, read-modify-write lost updates, accepting zero-mask accounts as privileged accounts, and byte-order compatibility. Tests should cover current and old record formats, grant/revoke by name and set, enumeration filtered by one privilege, malformed SID/key rejection, `lp_enable_privileges()` false behavior, and concurrent grant/revoke if a higher layer promises serialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/privileges.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/privileges.h -->
# sources/user-network-fs/samba/source3/lib/privileges.h

## Purpose
This header declares the source3 privilege management API implemented by `privileges.c`. It is the include point for code that needs to query, enumerate, grant, revoke, create, or delete privilege records associated with SIDs.

## Important APIs, Types, And Functions
It includes `../libcli/security/privileges.h` for core privilege definitions and declares functions for SID-list privilege aggregation, conversion to `PRIVILEGE_SET`, account enumeration, privilege-specific SID enumeration, grant/revoke by name or LSA privilege set, account create/delete, privileged-SID check, and granting all privileges.

## Control Flow
There is no runtime control flow in the header. It fixes function signatures and exposes Samba's `NTSTATUS`/boolean return conventions to callers.

## State And Persistence
No state is defined in the header. Persistence is handled by the implementation in the account policy database under `PRIV_<SID>` keys.

## Dependencies And Integration Points
Callers must have Samba security types such as `struct dom_sid`, `PRIVILEGE_SET`, `struct lsa_PrivilegeSet`, and `enum sec_privilege` visible through included headers. The API integrates with LSA server code, passdb/account-policy code, and administrative tools.

## Risks And Test Signals
Header risks are ABI/API drift with `privileges.c` and missing prototypes for new implementation helpers. Build tests should compile all callers with this header, and functional tests belong with the implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/privileges.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/readdir_attr.h -->
# sources/user-network-fs/samba/source3/lib/readdir_attr.h

## Purpose
This header defines extra filesystem metadata that can be carried during readdir/marshalling contexts. It currently supports no attributes or Apple-specific attributes.

## Important APIs, Types, And Functions
`enum readdir_attr_type` has `RDATTR_NONE` and `RDATTR_AAPL`. `struct readdir_attr_data` stores the active type and a union with an `aapl` payload containing resource fork size, 16 bytes of Finder info, maximum access, and Unix mode.

## Control Flow
The header has no functions or control flow. Consumers switch on `type` and read the corresponding union member.

## State And Persistence
The structure is transient per directory entry or marshalling operation. It does not own heap memory and does not persist data.

## Dependencies And Integration Points
It relies on standard fixed-width integer types and `mode_t` already made visible by included Samba/system headers. It integrates with SMB directory enumeration paths that need AAPL extension metadata.

## Risks And Test Signals
Risks are uninitialized union contents and consumers reading `aapl` fields without checking `type`. Tests should cover directory enumeration with no attributes and AAPL metadata enabled, including stable struct initialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/readdir_attr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/recvfile.c -->
# sources/user-network-fs/samba/source3/lib/recvfile.c

## Purpose
This file implements Samba's low-level receive-file helper: read bytes from a socket/file descriptor and write them to a destination fd below the VFS layer. It optionally uses Linux `splice` and otherwise falls back to a buffered userspace loop.

## Important APIs, Types, And Functions
`sys_recvfile(int fromfd, int tofd, off_t offset, size_t count)` returns bytes written or `-1` on read/initial-write error. `default_sys_recvfile()` seeks the output fd unless appending or pipe-like, reads chunks up to `TRANSFER_BUF_SIZE`, and writes with `sys_write()`. `drain_socket()` consumes and discards bytes from a blocking socket, restoring original flags afterward.

## Control Flow
The fallback loop handles `EINTR` on reads, distinguishes first-read `EAGAIN/EWOULDBLOCK` from partial progress, stops writing after a write error while continuing to drain already-read input, and returns the saved write errno. The Linux `splice` branch is effectively disabled initially by `try_splice_call = false`; if enabled, it splices from input to a static pipe and then to the output fd, falling back on unsupported errors and draining the socket when output fails after some input has been consumed.

## State And Persistence
Durable state is file content written to `tofd`. Static state in the splice path includes `pipefd` and `try_splice_call`, shared process-wide and not thread-protected. Socket blocking flags are temporarily changed only by `drain_socket()`.

## Dependencies And Integration Points
It uses Samba `sys_read`, `sys_write`, `set_blocking`, and `VFS_PWRITE_APPEND_OFFSET` constants, plus Linux `splice` when available. SMB server write paths use this for efficient network-to-file transfer.

## Risks And Test Signals
Risk areas are short read/write semantics, preserving errno after write failure, static pipe sharing, blocking-mode restoration, and the disabled splice path. Tests should cover zero count, non-blocking first-read EAGAIN, partial progress before EAGAIN, write failure after input consumption, append offset, ESPIPE seek tolerance, and `drain_socket()` flag restoration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/recvfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sendfile.c -->
# sources/user-network-fs/samba/source3/lib/sendfile.c

## Purpose
This file wraps platform-specific `sendfile` APIs behind `sys_sendfile()`, optionally sending an SMB header before file data. It provides implementations for Linux, Solaris, HP-UX, FreeBSD/Darwin, AIX, and an `ENOSYS` fallback.

## Important APIs, Types, And Functions
`sys_sendfile(int tofd, int fromfd, const DATA_BLOB *header, off_t offset, size_t count)` returns bytes sent or `-1`. Linux sends the header with `sys_send(..., MSG_MORE)` before calling `sendfile`. Solaris uses `sendfilev` vectors; HP-UX uses header/trailer iovecs; FreeBSD/Darwin uses `sf_hdtr`; AIX uses `send_file`.

## Control Flow
All implementations loop until requested file/header data is sent, retry `EINTR` where appropriate, and switch the socket to blocking mode on `EAGAIN/EWOULDBLOCK` because header plus file data must remain ordered. Socket flags are restored on exit. Linux maps unsupported `ENOSYS`/`EINVAL` after a header was sent to `errno = EINTR` as a signal to upper layers to emulate without disabling sendfile immediately.

## State And Persistence
There is no file-local persistent state. The function advances kernel socket output and reads from the source file at the requested offset. It may temporarily mutate socket blocking flags.

## Dependencies And Integration Points
It depends on platform sendfile headers, Samba `DATA_BLOB`, `sys_send`, and `set_blocking`. It is integrated with SMB read response paths that can avoid copying file data through userspace.

## Risks And Test Signals
Risks include platform API semantic differences, header partial-send accounting, incorrect return values on EOF, blocking flag restoration, AIX null-header handling where the return expression uses `header->length`, and upper-layer interpretation of Linux's artificial `EINTR`. Tests should cover header/no-header sends, non-blocking sockets, partial sends, EOF before count, unsupported syscall fallback, and build coverage for each configured platform branch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sendfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/server_id_db_util.c -->
# sources/user-network-fs/samba/source3/lib/server_id_db_util.c

## Purpose
This file adds a higher-level exclusive-name helper around `server_id_db`. It lets a process register a named role while pruning stale records for dead processes.

## Important APIs, Types, And Functions
`server_id_db_set_exclusive(struct server_id_db *db, const char *name)` adds the current process to the name, looks up all registered servers for that name, verifies exclusivity with `server_id_db_check_exclusive()`, and removes its own registration on failure. The checker compares each record with the current process, calls `serverid_exists()` for peers, returns `EEXIST` if another live process owns the name, and prunes dead peers with `server_id_db_prune_name()`.

## Control Flow
The function performs add, lookup, check/prune, cleanup-on-error. The source comment explicitly accepts a race where two simultaneous registrants can both see each other live and both fail with `EEXIST`.

## State And Persistence
State lives in the passed `server_id_db`. The helper mutates it by adding the caller, pruning stale peers, and removing the caller if exclusivity is not achieved.

## Dependencies And Integration Points
It depends on `lib/util/server_id_db.h`, current process identity from `server_id_db_pid()`, process liveness from `serverid_exists()`, and talloc temporary ownership. Daemon startup paths can use it to prevent duplicate singleton services.

## Risks And Test Signals
Known risk is the accepted concurrent registration race. Other risks are stale records when pruning fails and liveness false positives. Tests should simulate only-self registration, live peer `EEXIST`, dead peer pruning, lookup failure cleanup, and concurrent starts if singleton behavior matters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/server_id_db_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/server_id_db_util.h -->
# sources/user-network-fs/samba/source3/lib/server_id_db_util.h

## Purpose
This header exposes the source3 utility function for exclusive registration in a `server_id_db`.

## Important APIs, Types, And Functions
It includes `lib/util/server_id_db.h` and declares `int server_id_db_set_exclusive(struct server_id_db *db, const char *name);`.

## Control Flow
No control flow exists in the header. The return code contract is the implementation's errno-style integer: zero on success, nonzero such as `EEXIST` or lower-level database errors on failure.

## State And Persistence
The header defines no state. The implementation mutates the supplied server ID database.

## Dependencies And Integration Points
Callers must link with `server_id_db_util.c` and the lower-level server-id DB and liveness modules. It is intended for daemon singleton/name ownership logic.

## Risks And Test Signals
Risks are API drift and callers ignoring errno-style failures. Build tests should include this header wherever exclusive registration is used; behavior tests belong to the `.c` file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/server_id_db_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/server_id_watch.c -->
# sources/user-network-fs/samba/source3/lib/server_id_watch.c

## Purpose
This file implements an asynchronous tevent request that completes when a target `server_id` no longer exists. It is a polling process-death watcher with optional diagnostics for long waits.

## Important APIs, Types, And Functions
`server_id_watch_send()` allocates `server_id_watch_state`, records start/warn timestamps, reads debug options from loadparm, immediately completes if `serverid_exists()` is already false, or schedules a 500 ms `tevent_wakeup`. `server_id_watch_waited()` repeats the liveness check and reschedules until the process is gone. `server_id_watch_recv()` returns any unix error and optionally copies the watched ID.

## Control Flow
The request is callback-driven. Every wakeup frees the subrequest, checks liveness, and either completes the parent request or schedules another wakeup. If debug is enabled and ten seconds elapsed since the last warning, it either runs a configured debug script as root or reads `/proc/<pid>/stack` for local processes with procfs support, then logs the output.

## State And Persistence
State is only in the tevent request. External side effects are debug script execution and log messages; no database is mutated.

## Dependencies And Integration Points
It depends on `serverid_exists()`, tevent, Samba loadparm, root privilege helpers, `smbrun`, `fd_load`, `/proc` stack reading, and server ID formatting. It integrates with code that needs nonblocking wait-for-process-exit semantics.

## Risks And Test Signals
Risks include polling latency, debug script privilege and output handling, procfs availability, clustered ID formatting, and repeated warnings for long-lived targets. Tests should cover already-dead completion, delayed completion, wakeup failure/oom, debug disabled/enabled paths, custom debug script invocation, and local/nonlocal process handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/server_id_watch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/server_id_watch.h -->
# sources/user-network-fs/samba/source3/lib/server_id_watch.h

## Purpose
This header declares the asynchronous server-id watch API used to wait for process death through tevent.

## Important APIs, Types, And Functions
It includes tevent, talloc, and generated `server_id` definitions. `server_id_watch_send()` starts the request, and `server_id_watch_recv()` completes it and can return the watched `server_id`.

## Control Flow
The header encodes the standard tevent send/recv pattern but has no executable control flow.

## State And Persistence
It defines no persistent state. State is private to the implementation's request object.

## Dependencies And Integration Points
Callers must run a tevent loop and link with the implementation plus server-id liveness support.

## Risks And Test Signals
Header-level risks are API mismatch with the implementation and missing tevent/talloc includes in callers. Functional tests belong with `server_id_watch.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/server_id_watch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/server_mutex.c -->
# sources/user-network-fs/samba/source3/lib/server_mutex.c

## Purpose
This file provides a named process-wide mutex backed by `mutex.tdb`. It serializes access to remote servers that behave poorly when multiple SMB connections operate concurrently.

## Important APIs, Types, And Functions
`struct named_mutex` owns a `tdb_wrap` handle and lock name. `grab_named_mutex(TALLOC_CTX *mem_ctx, const char *name, int timeout)` opens `lock_path("mutex.tdb")`, locks the named key with timeout, and returns a talloc object whose destructor unlocks. `unlock_named_mutex()` calls `tdb_unlock_bystring()`.

## Control Flow
The function allocates state, initializes loadparm to obtain tdb sizing/flags, opens `mutex.tdb` with `TDB_CLEAR_IF_FIRST` and `TDB_INCOMPATIBLE_HASH`, attempts the named lock, and installs a destructor on success. Any allocation, path, open, or lock failure frees partial state and returns NULL.

## State And Persistence
The tdb file is persistent under Samba's lock path, but the actual mutex state is advisory tdb locking tied to the process and talloc lifetime. Unlock happens when the returned object is freed.

## Dependencies And Integration Points
It depends on tdb_wrap, source3 loadparm helpers, `lock_path`, and talloc destructors. Callers use it as an RAII-like lock object around serialized remote operations.

## Risks And Test Signals
Risks include forgetting to keep/free the returned talloc object at the right scope, lock timeout behavior, tdb open failures, and stale expectations around `TDB_CLEAR_IF_FIRST`. Tests should cover successful lock/unlock, contention timeout, destructor unlock, missing lock path errors, and multiple lock names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/server_mutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/serverid.c -->
# sources/user-network-fs/samba/source3/lib/serverid.c

## Purpose
This file implements reliable `serverid_exists()` checks for local and clustered Samba server IDs.

## Important APIs, Types, And Functions
`serverid_exists_local()` first checks PID existence, then optionally verifies the `unique_id` through `messaging_dgm_get_unique()` unless the ID requests no verification. `serverid_exists()` dispatches to local checks for local proc IDs, to CTDB process existence when clustering is enabled, and otherwise returns false for nonlocal IDs.

## Control Flow
Local control flow is conservative: if the process exists and unique-id lookup fails with `EACCES`, the code logs and assumes the process still exists. Other unique-id lookup failures return false. Clustered flow uses `ctdbd_process_exists()` through the messaging CTDB connection.

## State And Persistence
The file does not persist state. It observes process state, messaging datagram lock/unique-id state, and CTDB cluster process state.

## Dependencies And Integration Points
It depends on process existence helpers, procid locality checks, loadparm clustering, CTDB messaging, and datagram messaging unique IDs. It is used by server-id databases, watchers, and cleanup code to avoid stale process references.

## Risks And Test Signals
Risks are PID reuse without unique-id verification, permission-denied false positives, CTDB connectivity failures, and nonlocal IDs when clustering is disabled. Tests should cover local pid exists/dead, unique-id match/mismatch/not-to-verify, `EACCES` behavior, and clustered vs nonclustered dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/serverid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sessionid_tdb.c -->
# sources/user-network-fs/samba/source3/lib/sessionid_tdb.c

## Purpose
This file provides the legacy `sessionid_traverse_read()` interface by traversing modern `smbXsrv_session_global` records and adapting them into `struct sessionid` values.

## Important APIs, Types, And Functions
`struct sessionid_traverse_read_state` carries the caller callback and private data. `sessionid_traverse_read_fn()` maps each `smbXsrv_session_global0` to a `sessionid`: uid/gid, global session id, connect start time, server id, dialect, authentication status, remote name/address, id string, encryption flags/cipher, and signing flags/algorithm. `sessionid_traverse_read()` calls `smbXsrv_session_global_traverse()`.

## Control Flow
Traversal is callback-based. For sessions with `auth_session_info`, Unix identity and authenticated status are filled; otherwise uid/gid remain `-1`. String fields are copied with bounded `strncpy`/`snprintf`, and the adapted record is passed to the caller's callback.

## State And Persistence
This file does not directly access `sessionid.tdb` despite its name. It reads current global session state from the smbXsrv subsystem and produces transient callback records.

## Dependencies And Integration Points
It depends on dbwrap/session headers, smbd globals, `smbXsrv_session_global_traverse`, security session helpers, and NTTIME conversion. It preserves compatibility for tools expecting sessionid traversal.

## Risks And Test Signals
Risks include channel array assumptions (`channels[0]`), truncation of fstring fields, unauthenticated session defaults, and callback error propagation through the traverse layer. Tests should cover authenticated and unauthenticated sessions, encryption/signing fields, long remote names, and callback failure behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sessionid_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sharesec.c -->
# sources/user-network-fs/samba/source3/lib/sharesec.c

## Purpose
This file manages per-share security descriptors stored in `share_info.tdb`, provides default share ACLs, checks share access against security tokens, and parses usershare ACL strings.

## Important APIs, Types, And Functions
`share_info_db_init()` opens and upgrades the global `share_db`. Versions move through V1/V2/V3, with V3 canonicalizing share names under `SECDESC/`. `get_share_security()` fetches and unmarshals a descriptor or returns a default Everyone descriptor. `set_share_security()` marshals and stores a descriptor transactionally. `delete_share_security()` removes a descriptor. `share_access_check()` calls `se_file_access_check()`. `parse_usershare_acl()` parses strings like `SID:F`, `SID:R`, or `SID:D` into a security descriptor.

## Control Flow
Initialization opens `state_path("share_info.tdb")`, starts a transaction for upgrades, deletes unknown old-version contents, rewrites V2 keys to canonical names, and commits V3. Fetch/set/delete canonicalize service names before building keys. Usershare ACL parsing counts comma-separated ACEs, parses SIDs and access letters, maps generic access through `file_generic_mapping`, and builds an ACL/security descriptor.

## State And Persistence
The global `share_db` caches the database handle. Durable state is tdb records with key `SECDESC/<canonical_share>` and marshalled self-relative security descriptors plus `INFO/version`.

## Dependencies And Integration Points
It depends on dbwrap, state paths, security descriptor NDR marshalling, generic file mapping, SID parsing, and security-token access checks. It integrates with share management, usershares, and SMB tree-connect authorization.

## Risks And Test Signals
Risks include upgrade transaction failure, duplicate canonical names during V2-to-V3 migration, fallback-to-open-default on corrupt descriptors, global handle lifetime, and ACL parser strictness. Tests should cover DB version upgrades, mixed-case share canonicalization, corrupt/missing descriptor fallback, set/get/delete round trips, access allow/deny decisions, empty usershare ACL default read, malformed ACL strings, and deny ACE parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sharesec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbconf/pys3smbconf.c -->
# sources/user-network-fs/samba/source3/lib/smbconf/pys3smbconf.c

## Purpose
This file implements the Python extension module for source3-specific smbconf initialization. It creates Python `SMBConf` objects backed by Samba's source3 registry or generic smbconf backends.

## Important APIs, Types, And Functions
The module exports `init_reg(path)` and `init(source)`. `py_new_SMBConf()` imports and calls `samba.smbconf.SMBConf` to create the common Python wrapper object. `py_raise_SMBConfError()` delegates error creation to `samba.smbconf._smbconf_error`. `py_init_reg()` accepts `None` or a registry path and calls `smbconf_init_reg()`. `py_init_str()` accepts a backend source string and calls `smbconf_init()`.

## Control Flow
Each initializer parses Python args, imports `samba.smbconf`, creates an object, extracts its talloc context from `py_SMBConf_Object`, initializes a C `smbconf_ctx`, stores it in the Python object, and returns it. On smbconf errors it raises the common Python exception and clears temporary references.

## State And Persistence
The module stores no global mutable state. Returned Python objects own a C smbconf context, which may read or write registry-backed configuration depending on backend operations.

## Dependencies And Integration Points
It depends on Python C API, Samba py3 compatibility, common `lib/smbconf/pysmbconf.h`, source3 `smbconf_reg.h`, and `smbconf_init.h`. It bridges `samba.samba3.smbconf` module users to C backends.

## Risks And Test Signals
Risks include Python reference leaks on error paths, assuming object layout from the common module, type parsing (`z` for nullable registry path, `s` for non-null source), and exception creation failure. Tests should import the module, call `init_reg(None)`, call `init("registry:")` and `init("file:/path")`, verify exceptions for invalid sources, and run under Python leak/debug builds if available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbconf/pys3smbconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbconf/smbconf_init.c -->
# sources/user-network-fs/samba/source3/lib/smbconf/smbconf_init.c

## Purpose
This file implements the smbconf backend dispatcher. It parses a configuration source string and initializes the registry or text/file backend.

## Important APIs, Types, And Functions
`smbconf_init(TALLOC_CTX *mem_ctx, struct smbconf_ctx **conf_ctx, const char *source)` is the only function. It recognizes `registry:`/`reg:` and `file:`/`txt:` prefixes, accepts empty path after the colon as NULL, and falls back to text backend behavior for unprefixed strings or unknown prefixed strings that may be file names containing colons.

## Control Flow
The function validates `conf_ctx` and nonempty source, duplicates the source on a stackframe, splits at the first colon, and dispatches to `smbconf_init_reg()` or `smbconf_init_txt()`. If there is no separator and no known backend, it treats the whole source as a file path. If there is an unknown backend with a separator, it tries the original string as a file path.

## State And Persistence
No persistent state is stored here. It creates backend-specific `smbconf_ctx` objects whose state and persistence are owned by the selected backend.

## Dependencies And Integration Points
It depends on smbconf private APIs plus text and registry backend initializers. It is used by C and Python wrappers as a single entry point for backend selection.

## Risks And Test Signals
Risks include ambiguous strings with colons, empty sources, backend aliases, and fallback masking typos in backend names by attempting file open. Tests should cover `registry:`, `reg:PATH`, `file:PATH`, `txt:PATH`, bare file path, unknown backend with colon, NULL/empty source, and NULL output pointer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbconf/smbconf_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbconf/smbconf_init.h -->
# sources/user-network-fs/samba/source3/lib/smbconf/smbconf_init.h

## Purpose
This header declares the generic smbconf initialization dispatcher.

## Important APIs, Types, And Functions
It forward-declares `struct smbconf_ctx` and declares `sbcErr smbconf_init(TALLOC_CTX *mem_ctx, struct smbconf_ctx **conf_ctx, const char *source);`. The source string contract is documented as `backend:path`.

## Control Flow
There is no executable flow. The header describes dispatch semantics implemented in `smbconf_init.c`.

## State And Persistence
No state is defined. Backend-specific contexts and persistence are created by the implementation.

## Dependencies And Integration Points
Consumers need `sbcErr` and `TALLOC_CTX` definitions from surrounding smbconf/Samba headers. It integrates C callers and Python wrappers with registry/text backend initialization.

## Risks And Test Signals
Risks are signature drift and ambiguous ownership expectations for returned contexts. Build tests and dispatcher tests in `smbconf_init.c` cover this header's contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbconf/smbconf_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbconf/smbconf_reg.c -->
# sources/user-network-fs/samba/source3/lib/smbconf/smbconf_reg.c

## Purpose
This file implements the read-write registry backend for libsmbconf. It maps smbconf services and parameters to registry keys and values under the SMB configuration registry path.

## Important APIs, Types, And Functions
`struct reg_private_data` stores the base registry key and whether this backend opened the registry database. `smbconf_reg_parameter_is_valid()` filters loadparm-valid parameters and forbids state/lock/config backend/include internals. Helper functions open/create service keys, test value existence, set `REG_SZ` parameters with canonicalized names/values, set `REG_MULTI_SZ` include lists, format registry values back to strings, enumerate values, and delete values. The exported initializer is `smbconf_init_reg()`, which calls `smbconf_init_internal()` with `smbconf_ops_reg`.

## Control Flow
Initialization creates an admin registry token, initializes the smbconf registry path, opens regdb, and opens the base key. Operations implement the `smbconf_ops` table: open/close, change-sequence number, drop/reset subtree, enumerate share names with `global` first, create/get/delete shares, set/get/delete parameters, get/set/delete includes, and transaction start/commit/cancel. Service `NULL` means the base/global key for several helpers; non-NULL service names map to subkeys. `get_share()` preserves actual registry key case by enumerating base subkeys.

## State And Persistence
Persistent configuration lives in the Samba registry database. Ordinary parameters are stored as `REG_SZ`; include lists are stored internally as `REG_MULTI_SZ` under the special value name `includes` but are exposed as repeated `include` parameters. The backend tracks open/closed state in the context private data and uses regdb sequence numbers as CSNs.

## Dependencies And Integration Points
It depends on source3 registry APIs, registry database backend, admin token creation, loadparm parameter validation/canonicalization, smbconf private operation contracts, and clustering/loadparm checks for messaging needs. It is the writable config backend for tools and Python bindings.

## Risks And Test Signals
Risk areas are registry permission/token assumptions, reserved parameter filtering, canonicalization/value validation differences from text backend, deleting while enumerating values, treating registry open state as context-local over a process-global regdb, CTDB registry messaging requirements, and fallback error mapping that often collapses registry errors to generic smbconf errors. Tests should cover parameter validation, global-only parameter rejection in services, include round trips, share create/get/delete/drop, transaction commit/cancel, CSN changes, clustered `requires_messaging`, and Python/C initialization using default and explicit paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbconf/smbconf_reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbconf/smbconf_reg.h -->
# sources/user-network-fs/samba/source3/lib/smbconf/smbconf_reg.h

## Purpose
This header declares the registry smbconf backend entry points.

## Important APIs, Types, And Functions
It forward-declares `struct smbconf_ctx`, declares `smbconf_init_reg()` for creating a registry-backed context, and declares `smbconf_reg_parameter_is_valid()` for checking whether a parameter may be stored in the registry backend.

## Control Flow
No control flow exists in the header. It exposes backend initialization and validation contracts to C callers and Python bindings.

## State And Persistence
No state is defined here. Registry persistence and context private data are handled in `smbconf_reg.c`.

## Dependencies And Integration Points
Consumers must include definitions for `sbcErr`, `TALLOC_CTX`, and bool through Samba headers. The header integrates registry-backed configuration with the generic dispatcher and testsuite.

## Risks And Test Signals
Risks are API mismatch with implementation and callers assuming validation is identical to loadparm validation. Tests should include both compile coverage and validation cases from the implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbconf/smbconf_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbconf/testsuite.c -->
# sources/user-network-fs/samba/source3/lib/smbconf/testsuite.c

## Purpose
This file is a small standalone smbconf testsuite executable. It exercises include-list operations for both text and registry smbconf backends and basic command-line initialization.

## Important APIs, Types, And Functions
`print_strings()` prints arrays. `test_get_includes()`, `test_set_get_includes()`, and `test_delete_includes()` validate global include retrieval, set/get equality, deletion, and idempotent delete. `create_conf_file()` writes a temporary `/tmp/smb.conf.smbconf_testsuite`. `torture_smbconf_txt()` initializes the text backend and checks includes. `torture_smbconf_reg()` initializes the registry backend and checks include operations. `main()` initializes Samba command-line context and runs both backend tests.

## Control Flow
The executable parses common Samba options with popt, runs text backend setup/test/cleanup, then registry backend tests, and exits zero on success or `-1` on failure. Each test prints `TEST`, `OK`, and `FAIL` messages and uses talloc stackframes for temporary allocations.

## State And Persistence
It writes and unlinks a temporary smb.conf in `/tmp`. Registry backend tests mutate the configured smbconf registry include values and then delete them, but they run against the real registry backend path selected by `smbconf_init_reg(NULL)`.

## Dependencies And Integration Points
It depends on Samba command-line initialization, popt, text and registry smbconf backends, and the public smbconf include APIs. It is a direct integration signal for the backend files in this subset.

## Risks And Test Signals
Risks include using a fixed `/tmp` filename, mutating real registry configuration during tests, limited assertion coverage outside include APIs, and returning `-1` as process status. Useful additions would isolate the registry path, test parameter CRUD and share CRUD, cover dispatcher aliases, and avoid fixed temp paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbconf/testsuite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbd_shim.c -->
# sources/user-network-fs/samba/source3/lib/smbd_shim.c

## Purpose
This file implements a runtime shim table for library code that may be linked into smbd or non-smbd utilities. smbd can install real callbacks; other binaries get safe dummy behavior or process exit fallbacks.

## Important APIs, Types, And Functions
`set_smbd_shim()` copies a caller-provided `struct smbd_shim` into the file-static `shim`. Wrapper functions include `change_to_root_user()`, `become_authenticated_pipe_user()`, `unbecome_authenticated_pipe_user()`, `contend_level2_oplocks_begin()`, `contend_level2_oplocks_end()`, `become_root()`, `unbecome_root()`, `exit_server()`, and `exit_server_cleanly()`.

## Control Flow
Each wrapper checks whether the corresponding function pointer is non-NULL. Boolean wrappers return false when unset. Oplock and privilege wrappers no-op when unset. Exit wrappers call the installed callback if present and otherwise call `exit(1)` or `exit(0)`.

## State And Persistence
State is a single process-global `struct smbd_shim`. There is no persistence. Installing a shim changes behavior process-wide and is not synchronized.

## Dependencies And Integration Points
It depends on `smbd_shim.h` and Samba auth/files types. It breaks dependency cycles by letting common library code refer to smbd-specific privilege, authenticated pipe user, oplock contention, and exit behavior without linking all smbd internals into utilities.

## Risks And Test Signals
Risks include process-global mutable callbacks, no thread-safety during installation, dummy false/no-op behavior hiding missing setup, and exit callback contracts marked noreturn but not enforced after callback return. Tests should verify default behavior in utility builds, installed callback dispatch, exit fallbacks, and shim installation before worker threads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbd_shim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbd_shim.h -->
# sources/user-network-fs/samba/source3/lib/smbd_shim.h

## Purpose
This header defines the `struct smbd_shim` callback table and declares the installer used by smbd to provide daemon-specific behavior to shared library code.

## Important APIs, Types, And Functions
`struct smbd_shim` contains callbacks for root-user changes, authenticated pipe user impersonation, level2 oplock contention begin/end hooks, root privilege enter/leave, and clean/unclean server exit. `set_smbd_shim()` installs the table. Function pointer signatures reference `auth_session_info`, `files_struct`, and `enum level2_contention_type`.

## Control Flow
The header has no executable logic, but it defines which operations can be dynamically dispatched by `smbd_shim.c`.

## State And Persistence
No state is declared here. The implementation stores a process-global copy of the table.

## Dependencies And Integration Points
The header expects surrounding Samba includes to provide bool, auth, file, and noreturn annotations. It is included by library code and smbd setup code to avoid hard dependencies on smbd internals.

## Risks And Test Signals
Risks are callback signature drift, missing declarations for the wrapper functions in this header, and caller confusion over default behavior. Build coverage across smbd and utility binaries is the main signal, with runtime tests in `smbd_shim.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbd_shim.h -->
