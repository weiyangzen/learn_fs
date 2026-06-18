# subset-b-009809 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages_ctdb_ref.h -->
## sources/user-network-fs/samba/source3/lib/messages_ctdb_ref.h

Purpose: Declares the source3 messaging hook used to hold a CTDB messaging reference and receive CTDB-delivered messages.

Important APIs/types/functions: `messaging_ctdb_ref(TALLOC_CTX *, struct tevent_context *, const char *sockname, int timeout, uint64_t unique_id, recv_cb, void *private_data, int *err)` returns an opaque talloc-owned reference. The callback receives the tevent context, raw message bytes, optional file descriptors, and caller-private state.

Control flow: This header only exports the constructor. Callers provide the event loop, CTDB socket name, timeout, unique process id, and receive callback; implementation lifetime is represented by the returned pointer.

State and persistence behavior: State is event-loop and talloc-lifetime based, not file-persistent. The callback boundary can transfer fd state.

Dependencies and integration points: Depends on `replace.h`, `tevent.h`, talloc ownership, and source3 messaging/CTDB integration.

Risks: The API is opaque, so callers must handle NULL returns and `err`. Callback fd ownership and timeout semantics need implementation-level care.

Test signals: CTDB messaging tests should exercise connect failure, timeout, callback dispatch with bytes/fds, and talloc teardown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages_ctdb_ref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages_util.c -->
## sources/user-network-fs/samba/source3/lib/messages_util.c

Purpose: Serializes and deserializes Samba internal messaging headers into a fixed 52-byte wire/storage buffer.

Important APIs/types/functions: `message_hdr_put()` writes destination `server_id`, source `server_id`, and `msg_type`. `message_hdr_get()` reads those fields back. The code relies on `SERVER_ID_BUF_LENGTH`, `server_id_put()`, `server_id_get()`, `SIVAL()`, and `IVAL()`.

Control flow: Put writes destination at offset zero, source at `SERVER_ID_BUF_LENGTH`, and the 32-bit type after two server-id slots. Get performs the inverse and intentionally returns source and destination through distinct pointers.

State and persistence behavior: No durable state beyond the caller-provided byte array. The exact byte order and fixed length are the compatibility contract.

Dependencies and integration points: Used by source3 messaging paths that prepend message metadata before payload bytes. Depends on Samba byteorder and NDR/server-id utilities.

Risks: Header length must match serialized `server_id` size. Field order is easy to reverse, so tests should round-trip asymmetric source/destination ids.

Test signals: Unit tests should validate buffer length, message type endian behavior, and round trips for unique, broadcast, and disconnected server ids.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages_util.h -->
## sources/user-network-fs/samba/source3/lib/messages_util.h

Purpose: Publishes the internal messaging header layout contract for source3 messaging utilities.

Important APIs/types/functions: Defines `MESSAGE_HDR_LENGTH` as `52` and declares `message_hdr_put()` and `message_hdr_get()` over a fixed-size `uint8_t buf[MESSAGE_HDR_LENGTH]`. It forward-declares `struct message_hdr`, although the exposed helpers operate on raw bytes and `struct server_id`.

Control flow: Consumers include this header to build or parse message headers before sending through messaging transport code.

State and persistence behavior: The constant is persistent protocol state for in-memory and IPC message frames. No storage is owned here.

Dependencies and integration points: Coupled to `lib/util/server_id.h` users and `messages_util.c`; included by messaging implementations and tests that need deterministic header construction.

Risks: Changing the constant or prototype breaks ABI/source consumers and serialized headers.

Test signals: Compile coverage plus `message_hdr_put/get` round-trip tests are the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/ms_fnmatch.c -->
## sources/user-network-fs/samba/source3/lib/ms_fnmatch.c

Purpose: Implements Microsoft/SMB filename pattern matching, including DOS wildcard behavior that differs from POSIX `fnmatch`.

Important APIs/types/functions: `ms_fnmatch()` is the public entry point. `ms_fnmatch_core()` recursively matches UCS-2 pattern/name pairs. `null_match()` accepts trailing wildcard-only patterns. `struct max_n` memoizes recursion progress for `*` and `<` wildcards.

Control flow: `ms_fnmatch()` normalizes `..`, fast-paths patterns without SMB wildcards via `strcmp`/`strcasecmp_m`, converts pattern and string to UCS-2, optionally translates legacy `?`, `.*`, and `*.` into Windows-style `>`, `"`, and `<`, allocates recursion guards, and calls the core matcher with the last-dot pointer. The core matcher handles `*`, `<`, `?`, `>`, `"`, literal characters, case folding, and end-of-string success.

State and persistence behavior: No persistent state. Temporary UCS-2 allocations use `talloc_tos()` and wildcard memo state uses stack or heap allocation.

Dependencies and integration points: Used by SMB pathname matching and directory enumeration filters. Depends on Samba charset conversion, wide-character helpers, talloc stack, and SMB wildcard constants.

Risks: Wildcard semantics are compatibility-sensitive, especially last-dot behavior and LANMAN1 fast path. Recursive matching can become expensive without `max_n`. Conversion failure returns mismatch.

Test signals: Filename matching tests should cover `*`, `?`, `<`, `>`, `"`, dot/no-dot names, `..`, case-sensitive and insensitive modes, old-protocol translation, Unicode case folding, and long wildcard-heavy patterns.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/ms_fnmatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/namemap_cache.c -->
## sources/user-network-fs/samba/source3/lib/namemap_cache.c

Purpose: Caches SID-to-name and name-to-SID mappings in Samba gencache for name lookup acceleration.

Important APIs/types/functions: `namemap_cache_set_sid2name()`, `namemap_cache_find_sid()`, `namemap_cache_set_name2sid()`, and `namemap_cache_find_name()` are exported. Parser state structs carry caller callbacks and parse status. Values are stored as Samba string vectors containing domain/name/type or sid/type.

Control flow: Set functions normalize NULL inputs, handle unknown SID types specially, construct keys `SID2NAME/<sid>` or uppercase `NAME2SID/<domain>\<name>`, serialize fields with `strv_add()`, and call `gencache_set_data_blob()`. Find functions call `gencache_parse()`, parse string-vector fields, validate SID/type conversion, invoke the caller callback with an expired flag, and delete corrupt SID2NAME entries.

State and persistence behavior: Data persists in gencache until timeout. Expired entries can still be returned with an explicit expired boolean. Corrupt SID2NAME entries are deleted; corrupt NAME2SID entries fail lookup but are not explicitly deleted in this function.

Dependencies and integration points: Integrates with winbind/name lookup code, `gencache`, `dom_sid` parsing/formatting, talloc stack, charset uppercasing, `smb_strtoul`, and debug logging.

Risks: Uppercasing controls name-key canonicalization and must stay locale/charset-safe. Unknown SID type stores empty identity. Callback contracts must tolerate expired values. Corrupt cache data can cause lookup misses.

Test signals: `source3/torture/test_namemap_cache.c` is the direct test target. Coverage should include NULL domain/name, unknown types, expired entries, invalid blobs, invalid SID/type fields, and case-insensitive name lookup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/namemap_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/namemap_cache.h -->
## sources/user-network-fs/samba/source3/lib/namemap_cache.h

Purpose: Declares the public source3 name-map cache API for bidirectional SID/name cache operations.

Important APIs/types/functions: Exposes set/find functions for `sid2name` and `name2sid`. Find calls are callback-based and return parsed `domain`, `name`, `lsa_SidType`, `dom_sid`, and an `expired` flag.

Control flow: Callers set cache entries with a timeout and later request parsed values by key. The header leaves persistence details to `namemap_cache.c`.

State and persistence behavior: The API describes gencache-backed state indirectly through timeout and expired reporting. Ownership of callback values is transient.

Dependencies and integration points: Includes `replace.h`, `time.h`, `dom_sid`, and generated LSA SID type definitions. Used by authentication/name lookup layers.

Risks: Callback consumers must not retain transient pointers without copying. Passing NULL or null SID has special behavior in implementation.

Test signals: Compile users plus cache torture tests should verify all four declarations and callback signatures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/namemap_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/cm.c -->
## sources/user-network-fs/samba/source3/lib/netapi/cm.c

Purpose: Provides libnetapi connection management for IPC$ SMB sessions and cached DCERPC pipes.

Important APIs/types/functions: `client_ipc_connection` holds a server name, `cli_state`, and pipe list. `client_pipe_connection` wraps `rpc_pipe_client`. Exported functions are `libnetapi_shutdown_cm()`, `libnetapi_open_pipe()`, and `libnetapi_get_binding_handle()`. Internal helpers find/open IPC sessions and pipes.

Control flow: Opening a pipe first finds or creates an IPC connection for the server, collecting username/password, configuring credential callbacks and Kerberos state, and calling `cli_cm_open()`. Pipe lookup validates connection liveness and abstract syntax. Missing pipes are opened with `cli_rpc_pipe_open_noauth()` and cached under the IPC connection. Shutdown iterates cached IPC sessions and closes SMB connections.

State and persistence behavior: State lives under `libnetapi_ctx` as talloc-owned linked lists. No disk persistence. Cached connections preserve authenticated sessions and pipe handles for the context lifetime.

Dependencies and integration points: Integrates libnetapi APIs with Samba client SMB, credentials, RPC pipe, `smbXcli`, `ndr_table`, WERROR/NTSTATUS conversion, and error-string storage.

Risks: Cached pipes can go stale and are checked before reuse. Kerberos state is mutated when credentials are incomplete. Server-name matching relies on remote names from SMB connections.

Test signals: Integration tests need repeated calls against the same server/interface, credential prompting paths, Kerberos/no-password behavior, stale pipe recovery, and `libnetapi_shutdown_cm()` cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/common.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/common.c

Purpose: Shared command-line and file helpers for the libnetapi example programs.

Important APIs/types/functions: `popt_common_callback()` applies `--user`, `--password`, `--debuglevel`, and `--kerberos` to the global libnetapi context. `popt_common_netapi_examples[]` publishes the popt option table. `netapi_read_file()`, `netapi_save_file()`, and `netapi_save_file_ucs2()` support offline domain join payload examples.

Control flow: Popt invokes the callback during option parsing. `-U user%pass` splits credentials and masks the password in argv. File read grows a heap buffer in chunks and NUL-terminates it. UCS-2 save emits a UTF-16LE BOM and converts ASCII through iconv before writing.

State and persistence behavior: Mutates the process libnetapi context and overwrites password text in the argument string. File helpers read or write local payload files.

Dependencies and integration points: Used by all examples through `POPT_COMMON_LIBNETAPI_EXAMPLES`; depends on popt, netapi, POSIX I/O, and iconv.

Risks: `netapi_read_file()` double-closes fd after `fdopen()`/`fclose()`. `netapi_save_file_ucs2()` writes the full allocated buffer, not just converted bytes. Password masking mutates argv memory.

Test signals: Example smoke tests with each common option, read/write payload round trips, and UCS-2 output inspection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/common.h -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/common.h

Purpose: Declares the shared popt callback table and file helpers used by libnetapi examples.

Important APIs/types/functions: Declares `popt_common_callback()`, `popt_common_netapi_examples[]`, and macros `POPT_COMMON_LIBNETAPI_EXAMPLES`. Also declares `netapi_read_file()`, `netapi_save_file()`, and `netapi_save_file_ucs2()`.

Control flow: Example `long_options[]` arrays include `POPT_COMMON_LIBNETAPI_EXAMPLES`, making credential/debug/Kerberos parsing consistent across samples.

State and persistence behavior: Header owns no state; implementation mutates libnetapi context and local files.

Dependencies and integration points: Depends on popt and is included by nearly every file under `netapi/examples`.

Risks: Macro inclusion hides callback side effects; command examples must call `libnetapi_init()` before parsing.

Test signals: Build failures catch signature drift; command smoke tests catch option-table wiring.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/dsgetdc/dsgetdc.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/dsgetdc/dsgetdc.c

Purpose: Demonstrates `DsGetDcName()` discovery of a domain controller and prints returned controller metadata.

Important APIs/types/functions: Uses `DOMAIN_CONTROLLER_INFO`, accepts hostname/domain/site flags, parses flags as hex, and frees the result with `NetApiBufferFree()`.

Control flow: Initializes libnetapi, parses common options, requires a domain argument, optionally reads server/site/flags, calls `DsGetDcName()`, prints DC name/address/domain/forest/flags/site fields, then frees buffers and context.

State and persistence behavior: No persistent state; discovery is network/RPC state.

Dependencies and integration points: Integrates popt examples with domain discovery APIs used by join and netlogon workflows.

Risks: Flags are parsed with `sscanf("%x")` without strong validation. Output assumes non-NULL strings from the API.

Test signals: Run against a known AD domain with default and site/flag variants; verify graceful error when no DC is reachable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/dsgetdc/dsgetdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_close.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_close.c

Purpose: Demonstrates closing an open remote file handle by id with `NetFileClose()`.

Important APIs/types/functions: Parses hostname and numeric `fileid`; calls `NetFileClose(hostname, fileid)`.

Control flow: Initializes context, parses common options, requires hostname and file id arguments, converts the id with `atoi()`, calls the API, reports the libnetapi error string on failure, and releases context/popt state.

State and persistence behavior: The remote server state changes by closing a listed open file. No local files are persisted.

Dependencies and integration points: Complements `file_enum` and `file_getinfo` examples for server open-file administration.

Risks: `atoi()` lacks validation and may treat malformed ids as zero. Operation is administrative and can disrupt remote users.

Test signals: Enumerate open files, close a test file id, then re-enumerate to confirm removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_close.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_enum.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_enum.c

Purpose: Demonstrates paged enumeration of open files on a remote server with `NetFileEnum()`.

Important APIs/types/functions: Handles levels 2 and 3, `FILE_INFO_2`, `FILE_INFO_3`, resume handles, `entries_read`, and `total_entries`.

Control flow: Parses hostname, optional base path/user/level, then loops while status is success or `ERROR_MORE_DATA`. Each page casts the returned buffer by level, prints file ids and level-specific lock/path/user fields, frees the buffer, and continues with the resume handle.

State and persistence behavior: Read-only remote administrative query. Resume handle maintains server-side enumeration position.

Dependencies and integration points: Uses common libnetapi context and NetAPI buffer ownership.

Risks: Only levels 2 and 3 are printed. Resume loops depend on server returning progress. Optional path/user filters are positional and easy to omit incorrectly.

Test signals: Run against a server with known open files, with and without path/user filters, and force multi-page enumeration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_enum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_getinfo.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_getinfo.c

Purpose: Demonstrates querying one open remote file record by id with `NetFileGetInfo()`.

Important APIs/types/functions: Accepts hostname, file id, and level. Prints `FILE_INFO_2` id or `FILE_INFO_3` id, permissions, lock count, path, and username.

Control flow: Initializes, parses options and positional args, converts id/level through `atoi()`, calls `NetFileGetInfo()`, switches on level, prints known structures, frees the API buffer, and cleans up.

State and persistence behavior: Read-only remote server query; local state is limited to allocated result buffer.

Dependencies and integration points: Pairs with `file_enum` output, where ids can be discovered.

Risks: Invalid levels silently produce no detail after successful calls. Numeric parsing is weak.

Test signals: Query ids from `file_enum` at levels 2 and 3 and verify error path for a nonexistent id.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_getinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/getdc/getdc.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/getdc/getdc.c

Purpose: Demonstrates legacy `NetGetDCName()` domain-controller lookup.

Important APIs/types/functions: Calls `NetGetDCName(hostname, domain, &buffer)` and prints the returned string.

Control flow: Initializes libnetapi, parses common options, requires hostname, optionally accepts a domain, calls the API, prints the DC name on success, frees `buffer`, and releases context.

State and persistence behavior: Read-only network discovery with no local persistence.

Dependencies and integration points: Shows the older NetAPI DC lookup beside the richer `DsGetDcName()` sample.

Risks: Requires correct positional arguments; prints `libnetapi_errstr()` rather than context error string.

Test signals: Run against domain member and standalone contexts; compare with `dsgetdc` results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/getdc/getdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_add.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_add.c

Purpose: Demonstrates creating a global/domain group with `NetGroupAdd()`.

Important APIs/types/functions: Uses `GROUP_INFO_1` with name and comment and passes level 1 plus `parm_err`.

Control flow: Parses hostname, group name, and optional comment, initializes `GROUP_INFO_1`, calls `NetGroupAdd()`, reports context error strings, then frees context and popt state.

State and persistence behavior: Creates persistent group state on the target server/domain.

Dependencies and integration points: Part of the group administration example suite with adduser, setinfo, enum, and delete.

Risks: No client-side validation of group naming rules or duplicate handling beyond server error. Requires suitable credentials.

Test signals: Add a test group, query it with `group_getinfo`, then remove it with `group_del`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_add.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_adduser.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_adduser.c

Purpose: Demonstrates adding a user account to a global/domain group through `NetGroupAddUser()`.

Important APIs/types/functions: Calls `NetGroupAddUser(hostname, groupname, username)`.

Control flow: Initializes libnetapi, parses common options, requires hostname, group, and username, performs the membership update, reports failures, and releases context.

State and persistence behavior: Mutates remote group membership. No local persistence.

Dependencies and integration points: Complements `group_deluser`, `group_getusers`, and user/group management examples.

Risks: Server-side semantics decide domain resolution and duplicate membership. Requires privileges and valid account/group names.

Test signals: Add a known user to a test group, verify via `group_getusers`, then remove with `group_deluser`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_adduser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_del.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_del.c

Purpose: Demonstrates deleting a global/domain group with `NetGroupDel()`.

Important APIs/types/functions: Calls `NetGroupDel(hostname, groupname)`.

Control flow: Parses hostname and group name, calls the API, prints error details on failure, and cleans up libnetapi/popt state.

State and persistence behavior: Removes persistent group state from the remote server/domain.

Dependencies and integration points: Cleanup counterpart for `group_add` and setup for group administration tests.

Risks: Destructive operation with minimal confirmation or validation. Existing memberships and ACL references are not inspected.

Test signals: Create a disposable group, delete it, and verify `group_getinfo` fails afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_del.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_deluser.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_deluser.c

Purpose: Demonstrates removing a user from a global/domain group with `NetGroupDelUser()`.

Important APIs/types/functions: Calls `NetGroupDelUser(hostname, groupname, username)`.

Control flow: Initializes, parses common options and positional hostname/group/user arguments, calls the API, reports context error strings, and releases resources.

State and persistence behavior: Mutates remote group membership only.

Dependencies and integration points: Mirrors `group_adduser` and is verified by `group_getusers`.

Risks: No pre-check that the member exists in the group. Server may distinguish nonexistent users, groups, and absent membership.

Test signals: Add then remove a disposable user membership and enumerate members after each step.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_deluser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_enum.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_enum.c

Purpose: Demonstrates paged enumeration of global/domain groups with `NetGroupEnum()`.

Important APIs/types/functions: Supports levels 0, 1, 2, and 3 using `GROUP_INFO_0/1/2/3`; level 3 converts group SIDs with `sid_string_tos()`.

Control flow: Parses hostname and optional level, loops on success or `ERROR_MORE_DATA`, casts returned buffers by level, prints group name/comment/rid/SID/attributes, frees each page, and advances resume state.

State and persistence behavior: Read-only query. Resume handle tracks enumeration position.

Dependencies and integration points: Uses NetAPI buffer allocation rules and SID formatting from Samba headers.

Risks: Printing assumes level-specific structures match server response. Large domains rely on correct resume handling.

Test signals: Enumerate at each supported level against a test domain and compare counts with known group inventory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_enum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_getinfo.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_getinfo.c

Purpose: Demonstrates querying one global/domain group with `NetGroupGetInfo()`.

Important APIs/types/functions: Handles `GROUP_INFO_0`, `_1`, `_2`, and `_3`, including SID conversion for level 3.

Control flow: Parses hostname, group name, and level, calls `NetGroupGetInfo()`, switches on the requested level to print name/comment/id/attributes/SID, then frees the result.

State and persistence behavior: Read-only remote group metadata query.

Dependencies and integration points: Used after create or modify examples to verify group state.

Risks: Unsupported levels produce little feedback. Output formatting is demonstration-oriented, not machine stable.

Test signals: Query a known group at levels 0-3 and verify fields match enumeration output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_getinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_getusers.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_getusers.c

Purpose: Demonstrates paged enumeration of users in a global/domain group with `NetGroupGetUsers()`.

Important APIs/types/functions: Supports levels 0 and 1 using `GROUP_USERS_INFO_0` and `GROUP_USERS_INFO_1`; level 1 prints membership attributes.

Control flow: Parses hostname/group/level, loops through result pages with a resume handle, prints member names and optional attributes, frees buffers, then reports final errors.

State and persistence behavior: Read-only membership query; no local persistence.

Dependencies and integration points: Verifies `group_adduser`, `group_deluser`, and `group_setusers` examples.

Risks: Only global group membership is represented; nested/local group semantics are server-defined.

Test signals: Compare output before and after membership mutation and exercise multi-page membership results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_getusers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_setinfo.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_setinfo.c

Purpose: Demonstrates updating global/domain group metadata with `NetGroupSetInfo()`.

Important APIs/types/functions: Supports levels 0, 1, 2, 3, 1002, and 1005 over `GROUP_INFO_*` structures and `parm_err`.

Control flow: Parses hostname, group, level, and value fields, fills the level-specific structure with new name/comment/attributes as applicable, calls `NetGroupSetInfo()`, and reports failures.

State and persistence behavior: Mutates remote group metadata.

Dependencies and integration points: Pairs with `group_getinfo` for validation and with domain group administration APIs.

Risks: Positional input is level-dependent and lightly validated. Rename/comment/attribute semantics vary by server support.

Test signals: Change a disposable group's comment/name where supported and verify through `group_getinfo`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_setinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_setusers.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_setusers.c

Purpose: Demonstrates replacing a global/domain group's user list with `NetGroupSetUsers()`.

Important APIs/types/functions: Allocates `GROUP_USERS_INFO_0` or `_1` arrays with `NetApiBufferAllocate()`, fills names and optional attributes, then calls `NetGroupSetUsers()`.

Control flow: Parses hostname, group, level, and member tokens. It computes entry count, allocates a NetAPI-owned buffer, populates entries from positional args, submits the replacement, frees the buffer, and cleans up.

State and persistence behavior: Replaces persistent remote membership state for the target group.

Dependencies and integration points: Uses NetAPI buffer allocator because structures are passed to NetAPI calls.

Risks: Destructive replacement can remove existing members. Input parsing assumes pairs for level 1. No rollback on partial server-side failure.

Test signals: Set a disposable group to a known membership list and verify exactly with `group_getusers`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_setusers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/djoin.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/join/djoin.c

Purpose: Demonstrates both phases of offline domain join: provisioning a computer account and requesting local offline join.

Important APIs/types/functions: Calls `NetProvisionComputerAccount()`, `netapi_save_file_ucs2()`, `netapi_read_file()`, and `NetRequestOfflineDomainJoin()`. Options include domain, machine name, save/load file, and request/provision mode.

Control flow: Parses mode and join parameters. Provision mode validates domain and machine name, requests provision text data, prints/saves it, and frees it. Request mode reads a provision blob from file and submits it to `NetRequestOfflineDomainJoin()`.

State and persistence behavior: Provision mode creates/updates domain account state and may write a local join blob. Request mode changes local machine join state for next reboot.

Dependencies and integration points: Combines the two smaller offline join examples and common file helpers.

Risks: Offline join data contains sensitive material and is written as files. Mode/argument validation is minimal.

Test signals: Provision a disposable computer account, save payload, request offline join in a controlled test machine, and verify join information after reboot.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/djoin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/getjoinableous.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/join/getjoinableous.c

Purpose: Demonstrates querying organizational units available for domain join with `NetGetJoinableOUs()`.

Important APIs/types/functions: Retrieves username and password from libnetapi context via `libnetapi_get_username()` and `libnetapi_get_password()`, then calls `NetGetJoinableOUs()`.

Control flow: Parses host and domain, obtains credentials already set by common options, calls the API, prints OU strings from the returned array, frees it, and exits.

State and persistence behavior: Read-only directory query; credentials are context state.

Dependencies and integration points: Used by join tools and GUI OU selection before `NetJoinDomain()`.

Risks: Requires credentials; missing credentials are reported as libnetapi errors. Returned OU count and array must be trusted.

Test signals: Query a domain with known joinable OUs and validate output count and cleanup under failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/getjoinableous.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/getjoininformation.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/join/getjoininformation.c

Purpose: Demonstrates reading current machine join status with `NetGetJoinInformation()`.

Important APIs/types/functions: Uses `NetSetupUnknownStatus`, `NetSetupUnjoined`, `NetSetupWorkgroupName`, and `NetSetupDomainName` result types.

Control flow: Parses optional host, calls `NetGetJoinInformation()`, switches on the returned join type, prints human-readable status and name, frees the name buffer, and cleans up.

State and persistence behavior: Read-only machine/domain membership query.

Dependencies and integration points: Baseline status check for join/unjoin/offline join examples and GUI initialization.

Risks: Unknown types are printed but not interpreted. Name buffer ownership must be released with `NetApiBufferFree()`.

Test signals: Run on unjoined, workgroup, and domain-joined systems and compare status labels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/getjoininformation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/netdomjoin.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/join/netdomjoin.c

Purpose: Demonstrates online domain join through `NetJoinDomain()`.

Important APIs/types/functions: Accepts host, domain, account OU, account, password, and join flags; defaults flags to `NETSETUP_JOIN_DOMAIN | NETSETUP_ACCT_CREATE`.

Control flow: Initializes context, parses options/positionals, calls `NetJoinDomain()`, prints context error string on failure or success notice, and frees resources.

State and persistence behavior: Mutates local/remote machine join state and domain computer account state depending on flags.

Dependencies and integration points: Online counterpart to offline join samples and GUI join workflow.

Risks: Requires privileged credentials and may require reboot. Incorrect flags can create or reuse computer accounts unexpectedly.

Test signals: Join a disposable test host or container to a test domain, verify with `getjoininformation`, then unjoin through other tools.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/netdomjoin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/provision_computer_account.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/join/provision_computer_account.c

Purpose: Demonstrates generating offline-domain-join provisioning data with `NetProvisionComputerAccount()`.

Important APIs/types/functions: Accepts domain, machine name, optional machine password, OU, domain controller, reuse flag, and save file. Uses `netapi_save_file_ucs2()` for persisted payloads.

Control flow: Parses options, validates required domain/machine name, calls provisioning API, prints the returned text data, optionally writes it as UTF-16LE, frees result data, and exits.

State and persistence behavior: Creates or reuses a domain computer account and can persist sensitive provisioning text locally.

Dependencies and integration points: First half of offline domain join; feeds `request_offline_domain_join`.

Risks: Provision payload is sensitive. Reuse behavior and account password choices affect domain security.

Test signals: Provision in a test OU, inspect account creation, save payload, and use it with request/offline join tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/provision_computer_account.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/rename_machine.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/join/rename_machine.c

Purpose: Demonstrates renaming a domain-joined machine with `NetRenameMachineInDomain()`.

Important APIs/types/functions: Gets username/password from the libnetapi context and calls `NetRenameMachineInDomain(host, new_name, username, password, flags)`.

Control flow: Parses host, new machine name, and optional flags, retrieves credentials, calls the rename API, reports errors, and releases resources.

State and persistence behavior: Mutates domain/local computer name state and generally requires reboot or follow-up system changes.

Dependencies and integration points: Related to GUI hostname-change flow, though the GUI has this path mostly disabled.

Risks: Credentials are required; incorrect names can break domain trust. Flag parsing uses simple integer conversion.

Test signals: Rename a disposable joined machine and verify join information/DNS/account state after reboot.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/rename_machine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/request_offline_domain_join.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/join/request_offline_domain_join.c

Purpose: Demonstrates applying offline domain join data through `NetRequestOfflineDomainJoin()`.

Important APIs/types/functions: Reads a provision blob using `netapi_read_file()`, then calls `NetRequestOfflineDomainJoin(provision_bin_data, provision_bin_data_size, flags, NULL)`.

Control flow: Parses `--loadfile` and optional flags, requires the file, loads it into memory, submits the request, reports errors, frees context, and exits.

State and persistence behavior: Changes local machine join configuration using supplied provision data; no new local output is written.

Dependencies and integration points: Consumes data from `provision_computer_account` or `djoin`.

Risks: The payload is sensitive and must match the target machine/domain. Read size is stored in `uint32_t`.

Test signals: Apply a known-good test payload and verify domain membership after required reboot.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/join/request_offline_domain_join.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_add.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_add.c

Purpose: Demonstrates creating a local group with `NetLocalGroupAdd()`.

Important APIs/types/functions: Supports levels 0 and 1 using `LOCALGROUP_INFO_0` and `LOCALGROUP_INFO_1` with optional comment and `parm_err`.

Control flow: Parses hostname, group name, level, and optional comment; fills the matching structure; calls the API; reports errors and cleanup.

State and persistence behavior: Creates persistent local group state on the target server.

Dependencies and integration points: Local-group administration suite with membership and info examples.

Risks: Level-dependent positional parsing is minimal. Requires administrative rights.

Test signals: Add a disposable local group, query with `localgroup_getinfo`, delete with `localgroup_del`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_add.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_addmembers.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_addmembers.c

Purpose: Demonstrates adding members to a local group through `NetLocalGroupAddMembers()`.

Important APIs/types/functions: Supports level 0 SID members (`LOCALGROUP_MEMBERS_INFO_0`) and level 3 domain/name strings (`LOCALGROUP_MEMBERS_INFO_3`). Uses `string_to_sid()` and `NetApiBufferAllocate()`.

Control flow: Parses hostname, group, level, and member list, allocates a structure array, converts or assigns each member, calls the API with entry count, frees buffer, and exits.

State and persistence behavior: Mutates local group membership on the remote server.

Dependencies and integration points: Complements get/set/delete member examples; bridges textual SID parsing into NetAPI structures.

Risks: Level 0 rejects invalid SID strings client-side; level 3 leaves name resolution to the server. Operation is additive and may partially fail server-side.

Test signals: Add SID and domain-name members to a test local group and verify via all `localgroup_getmembers` levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_addmembers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_del.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_del.c

Purpose: Demonstrates deleting a local group with `NetLocalGroupDel()`.

Important APIs/types/functions: Calls `NetLocalGroupDel(hostname, groupname)`.

Control flow: Parses hostname and group name, calls the delete API, prints context error details on failure, and frees context/popt.

State and persistence behavior: Removes local group state from the target server.

Dependencies and integration points: Cleanup counterpart to local group creation examples.

Risks: Destructive and lacks confirmation. Existing ACL references are outside the sample's scope.

Test signals: Delete a disposable group and confirm `localgroup_getinfo` fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_del.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_delmembers.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_delmembers.c

Purpose: Demonstrates removing local group members with `NetLocalGroupDelMembers()`.

Important APIs/types/functions: Supports member level 0 SID arrays and level 3 domain/name arrays, allocated via `NetApiBufferAllocate()`.

Control flow: Parses hostname/group/level/member args, builds the matching member array, converts SIDs for level 0, calls the delete API, frees the array, and exits.

State and persistence behavior: Mutates remote local group membership.

Dependencies and integration points: Mirrors `localgroup_addmembers` and is verified by `localgroup_getmembers`.

Risks: Weak input validation except SID conversion. Removing wrong members affects local authorization.

Test signals: Add then remove known local group members and enumerate after each step.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_delmembers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_enum.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_enum.c

Purpose: Demonstrates paged local group enumeration with `NetLocalGroupEnum()`.

Important APIs/types/functions: Supports levels 0 and 1 using `LOCALGROUP_INFO_0` and `_1`, with resume-handle paging.

Control flow: Parses hostname and optional level, loops on success or `ERROR_MORE_DATA`, prints group names and optional comments, frees each page, and handles final status.

State and persistence behavior: Read-only remote local group query.

Dependencies and integration points: Verifies create/delete/setinfo local group examples.

Risks: Only two levels are interpreted. Large result sets depend on resume behavior.

Test signals: Enumerate before and after creating a test local group and force small preferred lengths if supported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_enum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_getinfo.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_getinfo.c

Purpose: Demonstrates querying local group details with `NetLocalGroupGetInfo()`.

Important APIs/types/functions: Handles `LOCALGROUP_INFO_0`, `_1`, and `_1002` for name/comment data.

Control flow: Parses hostname, group, and level, calls the API, switches on level to print fields, frees the result buffer, and cleans up.

State and persistence behavior: Read-only remote metadata query.

Dependencies and integration points: Used to validate local group add/setinfo operations.

Risks: Unsupported levels are not described. Output is sample/debug oriented.

Test signals: Query a known group at levels 0, 1, and 1002 and compare comment changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_getinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_getmembers.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_getmembers.c

Purpose: Demonstrates paged enumeration of local group members with `NetLocalGroupGetMembers()`.

Important APIs/types/functions: Supports levels 0, 1, 2, and 3. Prints SIDs with `sid_string_tos()`, SID usage, resolved names, and domain-qualified names.

Control flow: Parses hostname/group/level, loops over result pages with a resume handle, casts buffer by level, prints member fields, frees each page, and reports final errors.

State and persistence behavior: Read-only membership query.

Dependencies and integration points: Primary verifier for add/delete/set localgroup member examples.

Risks: SID conversion may fail and suppress SID text. Name resolution behavior depends on server/domain state.

Test signals: Query groups containing SID-only and resolved domain members at all supported levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_getmembers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_setinfo.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_setinfo.c

Purpose: Demonstrates updating local group metadata with `NetLocalGroupSetInfo()`.

Important APIs/types/functions: Supports levels 0, 1, and 1002 using `LOCALGROUP_INFO_0`, `_1`, and `_1002`; accepts `--newname` and `--newcomment`.

Control flow: Parses hostname/group/level/options, verifies enough input for the requested level, fills the structure, calls `NetLocalGroupSetInfo()`, reports `parm_err` failures, and cleans up.

State and persistence behavior: Mutates local group name/comment state.

Dependencies and integration points: Paired with `localgroup_getinfo`.

Risks: Rename/comment support may vary by server. The sample does not prefetch existing values, so omitted fields may become NULL where the level uses them.

Test signals: Change a disposable local group's comment/name and verify by getinfo and enum.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_setinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_setmembers.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_setmembers.c

Purpose: Demonstrates replacing all local group members through `NetLocalGroupSetMembers()`.

Important APIs/types/functions: Builds `LOCALGROUP_MEMBERS_INFO_0` SID arrays or `_3` domain/name arrays using `NetApiBufferAllocate()`.

Control flow: Parses hostname/group/level/member tokens, allocates and fills the level-specific array, calls `NetLocalGroupSetMembers()`, frees the buffer, and exits.

State and persistence behavior: Replaces remote local group membership state.

Dependencies and integration points: Stronger mutation counterpart to add/delete member examples.

Risks: Destructive replacement can remove administrators or required service accounts. Input is positional and only SID conversion is validated.

Test signals: Apply a known member list to a disposable local group and verify exact membership with `localgroup_getmembers`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_setmembers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/netdomjoin-gui/netdomjoin-gui.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/netdomjoin-gui/netdomjoin-gui.c

Purpose: Provides a GTK graphical sample for viewing and changing Samba/Windows-style computer name, workgroup/domain membership, description, and join options.

Important APIs/types/functions: `join_state` stores libnetapi context, GTK widgets, current/new join names, credentials, description, hostname/domain details, server role, and change flags. Key callbacks include credential prompts, description changes, join/unjoin flow, OU scanning, hostname/domain/workgroup entry handlers, and UI construction. NetAPI calls include `NetServerGetInfo()`, `NetServerSetInfo()`, `NetGetJoinInformation()`, `DsGetDcName()`, `NetGetJoinableOUs()`, `NetJoinDomain()`, `NetUnjoinDomain()`, and partly disabled `NetRenameMachineInDomain()`.

Control flow: `main()` initializes GTK and join state, parses options, initializes libnetapi credentials, gathers server properties/join status, draws the main window, and enters `gtk_main()`. User actions mutate `join_state`, may prompt for credentials, discover DCs/OUs, perform unjoin/join, update labels, and show modal error/info dialogs.

State and persistence behavior: Maintains in-process GUI state and mutates remote/local machine state through NetAPI calls. Credential strings are stored in heap memory until cleared. Successful join/unjoin marks settings changed and prompts for reboot.

Dependencies and integration points: Bridges GTK/glib widgets and libnetapi domain-join APIs. Reuses common NetAPI concepts from CLI examples but owns custom UI state.

Risks: Old GTK API usage, manual memory management, modal callback complexity, and disabled hostname rename path. Credentials live in process memory. Operations can change domain trust and require reboot.

Test signals: Manual/GUI integration tests should cover initialization on workgroup/domain hosts, credentials prompt cancel/continue, OU scan, join failure/success, unjoin, description change, and cleanup on exit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/netdomjoin-gui/netdomjoin-gui.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/netlogon_control.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/netlogon_control.c

Purpose: Demonstrates querying Netlogon control state with `I_NetLogonControl()`.

Important APIs/types/functions: Supports result levels 1-4 and prints `NETLOGON_INFO_1/2/3/4` fields such as flags, trusted DC, connection status, trust verification, and logon attempts.

Control flow: Parses hostname, function code, and level, calls `I_NetLogonControl()`, casts the returned buffer by level, prints diagnostics using `libnetapi_errstr()`, frees the buffer, and exits.

State and persistence behavior: Mostly read-only diagnostics, though function codes may trigger netlogon actions depending on server implementation.

Dependencies and integration points: Netlogon administrative sample; related to `netlogon_control2` and `nltest`.

Risks: Function code is numeric and not constrained by the sample. Some codes may have side effects.

Test signals: Query levels 1-4 against a domain member/DC and compare status fields with server logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/netlogon_control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/netlogon_control2.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/netlogon_control2.c

Purpose: Demonstrates `I_NetLogonControl2()`, the Netlogon control API variant that accepts data such as a domain name.

Important APIs/types/functions: Uses levels 1-4 with `NETLOGON_INFO_*` structures and passes a hardcoded `"TEST"` domain buffer to the API.

Control flow: Parses hostname, optional function code and level, duplicates the domain string, calls `I_NetLogonControl2()`, prints the same level-specific diagnostics as `netlogon_control`, frees the NetAPI buffer and context.

State and persistence behavior: Diagnostic/control RPC with possible server-side effects depending on function code; local domain string is heap allocated but not freed in the sample.

Dependencies and integration points: Simple precursor to the more complete `nltest` sample.

Risks: Hardcoded data makes many control codes unrealistic. Numeric function codes are unchecked. Small memory leak for `domain`.

Test signals: Exercise query and trust-verification function codes with expected domain data and validate returned status structures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/netlogon_control2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/nltest.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/nltest.c

Purpose: Provides a richer `nltest`-style sample for netlogon control, secure-channel operations, DC discovery, and flag decoding.

Important APIs/types/functions: Defines option ids for server, db flags, secure-channel query/reset/verify, DC discovery flags, site/account fields, and DNS return controls. Helpers print `NETLOGON_INFO_1/2` results, DC flags, and `DOMAIN_CONTROLLER_INFO`. Main calls `I_NetLogonControl2()` for several operations and `DsGetDcName()` for discovery.

Control flow: Parses many popt options into operation flags. It initializes libnetapi, executes the selected control path, passes optional domain/account data to Netlogon control calls, prints status or DC information, and exits through shared cleanup.

State and persistence behavior: Some operations are read-only, but secure-channel reset, rediscovery, and db flag operations can alter Netlogon runtime state on the target server.

Dependencies and integration points: Combines libnetapi, Netlogon control, and DC locator behavior in one diagnostic tool.

Risks: Administrative side effects are exposed through command flags. Flag combinations can be invalid and are only lightly validated. Returned NetAPI buffers are not explicitly freed on every path before process exit. Output is human-oriented.

Test signals: Run query-only flags in CI-like integration, and reserve reset/dbflag operations for isolated domain controller/member tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/nltest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/server/remote_tod.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/server/remote_tod.c

Purpose: Demonstrates querying remote server time with `NetRemoteTOD()`.

Important APIs/types/functions: Uses `TIME_OF_DAY_INFO` and prints year/month/day/hour/minute/second fields.

Control flow: Parses hostname, calls `NetRemoteTOD()`, prints the returned timestamp on success, frees the result buffer, and cleans up.

State and persistence behavior: Read-only server query with no local persistence.

Dependencies and integration points: Server administration example using standard libnetapi setup/teardown.

Risks: Displays server-provided fields without timezone explanation. Requires reachable remote service.

Test signals: Compare output against server clock within acceptable skew and verify error path for unreachable host.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/server/remote_tod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/server/server_getinfo.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/server/server_getinfo.c

Purpose: Demonstrates querying server metadata through `NetServerGetInfo()`.

Important APIs/types/functions: Handles levels 100, 101, 102, and 1005; recognizes but does not print full details for 402, 403, 502, and 503.

Control flow: Parses hostname and level, calls the API, switches on level to print platform/name/version/type/comment/session fields or comment-only data, frees the buffer, and exits.

State and persistence behavior: Read-only server metadata query.

Dependencies and integration points: Used by GUI initialization and server administration examples.

Risks: Some supported levels are placeholders. Fields like passwords/userpath are printed directly where structures expose them.

Test signals: Query common levels against Samba and Windows servers and validate unsupported-level behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/server/server_getinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_add.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_add.c

Purpose: Demonstrates creating a share with `NetShareAdd()`.

Important APIs/types/functions: Uses `SHARE_INFO_2` with netname, type, remark, permissions, max/current uses, path, and password fields.

Control flow: Parses hostname, share name, path, and optional comment, fills `SHARE_INFO_2`, calls level 2 `NetShareAdd()`, reports `parm_err` failures, and exits.

State and persistence behavior: Creates persistent share configuration on the target server.

Dependencies and integration points: Share administration suite with enum/get/set/delete.

Risks: No path existence or permission validation before RPC. Password field is set NULL; share type defaults are sample-specific.

Test signals: Add a disposable share, query with `share_getinfo`, enumerate, then delete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_add.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_del.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_del.c

Purpose: Demonstrates deleting a share with `NetShareDel()`.

Important APIs/types/functions: Calls `NetShareDel(hostname, netname, reserved)` with reserved value zero.

Control flow: Parses hostname and share name, calls the API, prints error string on failure, and releases resources.

State and persistence behavior: Removes remote share configuration.

Dependencies and integration points: Cleanup counterpart to `share_add`.

Risks: Destructive and lacks confirmation. Existing client connections and filesystem contents are outside the sample's scope.

Test signals: Delete a disposable share and verify it no longer appears in `share_enum`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_del.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_enum.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_enum.c

Purpose: Demonstrates paged share enumeration with `NetShareEnum()`.

Important APIs/types/functions: Supports levels 0, 1, and 2 using `SHARE_INFO_0/1/2`, resume handle, entries read, and total entries.

Control flow: Parses hostname and level, loops on success or `ERROR_MORE_DATA`, prints share names and level-specific type/remark/permission/path/user fields, frees buffers, and handles final status.

State and persistence behavior: Read-only remote share query.

Dependencies and integration points: Verifies share add/delete/set operations.

Risks: Level 2 may expose paths and share passwords if a server returns them. Large enumerations rely on resume progress.

Test signals: Enumerate known shares at levels 0-2 and verify new share visibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_enum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_getinfo.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_getinfo.c

Purpose: Demonstrates querying one share through `NetShareGetInfo()`.

Important APIs/types/functions: Handles levels 0, 1, 2, 501, and 1005 using corresponding `SHARE_INFO_*` structures.

Control flow: Parses hostname/share/level, calls the API, casts and prints level-specific netname/type/remark/permission/user/path/password/flags fields, frees the buffer, and exits.

State and persistence behavior: Read-only share metadata query.

Dependencies and integration points: Validation target for `share_add` and `share_setinfo`.

Risks: May print sensitive share password fields when present. Unsupported levels are not fully described.

Test signals: Query a disposable share at supported levels and compare with enumeration output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_getinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_setinfo.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_setinfo.c

Purpose: Demonstrates updating share metadata with `NetShareSetInfo()`.

Important APIs/types/functions: Supports level 1004 through `SHARE_INFO_1004` to set a share remark/comment.

Control flow: Parses hostname, share name, level, and comment value, fills the structure, calls `NetShareSetInfo()`, reports `parm_err` failures, and cleans up.

State and persistence behavior: Mutates persistent share configuration on the remote server.

Dependencies and integration points: Paired with `share_getinfo` level 1/2/501-style comment verification.

Risks: Only level 1004 is handled. Missing comment input can leave NULL data.

Test signals: Set a disposable share comment and verify via `share_getinfo` and `share_enum`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_setinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/shutdown/shutdown_abort.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/shutdown/shutdown_abort.c

Purpose: Demonstrates aborting a pending remote shutdown with `NetShutdownAbort()`.

Important APIs/types/functions: Calls `NetShutdownAbort(hostname)`.

Control flow: Parses hostname, submits the abort request, reports libnetapi error strings, and releases resources.

State and persistence behavior: Mutates remote shutdown scheduler state if a shutdown is pending.

Dependencies and integration points: Counterpart to `shutdown_init`.

Risks: Administrative operation with visible system impact. Requires privileges and correct target.

Test signals: Start a delayed shutdown on an isolated test host, abort it, and confirm the host remains up.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/shutdown/shutdown_abort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/shutdown/shutdown_init.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/shutdown/shutdown_init.c

Purpose: Demonstrates initiating remote shutdown through `NetShutdownInit()`.

Important APIs/types/functions: Accepts hostname, optional message, timeout, force-apps flag, and reboot-after-shutdown flag.

Control flow: Parses arguments, converts numeric flags with `atoi()`, calls `NetShutdownInit()`, prints error string on failure, and cleans up.

State and persistence behavior: Schedules remote machine shutdown/reboot state.

Dependencies and integration points: Pairs with `shutdown_abort`.

Risks: Destructive administrative operation. Weak numeric parsing and no confirmation make accidental shutdown easy.

Test signals: Use only in isolated integration tests with a short timeout and abort path coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/shutdown/shutdown_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_add.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_add.c

Purpose: Demonstrates creating a user account with `NetUserAdd()`.

Important APIs/types/functions: Uses `USER_INFO_1` with name, password, privilege, home directory, comment, flags, and script path. Sets flags such as `UF_SCRIPT`.

Control flow: Parses hostname, username, password, and optional comment, fills the structure, calls level 1 `NetUserAdd()`, reports `parm_err` failures, and exits.

State and persistence behavior: Creates persistent user account state on the target server/domain.

Dependencies and integration points: User administration suite with get/set/groups/delete examples.

Risks: Password is passed on command line and may be exposed. Defaults are sample-oriented and not policy-aware.

Test signals: Add a disposable user, query with `user_getinfo`, then remove with `user_del`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_add.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_chgpwd.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_chgpwd.c

Purpose: Demonstrates changing a user password with `NetUserChangePassword()`.

Important APIs/types/functions: Calls `NetUserChangePassword(hostname, username, oldpassword, newpassword)`.

Control flow: Parses hostname, username, old password, and new password, calls the API, prints context error details on failure, and releases resources.

State and persistence behavior: Mutates remote account password state.

Dependencies and integration points: Complements user add/setinfo examples and tests password-change policy behavior.

Risks: Passwords are command-line arguments and may appear in process listings/history. Server password policy errors are only printed.

Test signals: Change a disposable user's password and verify authentication with the new secret.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_chgpwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_del.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_del.c

Purpose: Demonstrates deleting a user account with `NetUserDel()`.

Important APIs/types/functions: Calls `NetUserDel(hostname, username)`.

Control flow: Parses hostname and username, calls the delete API, prints error information, and frees libnetapi/popt resources.

State and persistence behavior: Removes persistent user account state from the target server/domain.

Dependencies and integration points: Cleanup counterpart for `user_add`.

Risks: Destructive and lacks confirmation. Does not inspect profile/home directories or group references.

Test signals: Delete a disposable user and verify `user_getinfo` fails afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_del.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_dispinfo.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_dispinfo.c

Purpose: Demonstrates display-oriented user enumeration through `NetQueryDisplayInformation()`.

Important APIs/types/functions: Uses level 1 and `NET_DISPLAY_USER`, index paging, preferred length, and returned entry counts.

Control flow: Parses hostname, repeatedly queries display information starting at an index, prints user name/full name/comment/flags-style fields, frees each page, and advances by entries read until completion.

State and persistence behavior: Read-only directory/account query.

Dependencies and integration points: Alternative to `NetUserEnum()` for UI-style user lists.

Risks: Paging is index-based and must avoid infinite loops if server returns no progress. Only user display level is covered.

Test signals: Compare output with `user_enum` for known accounts and exercise multi-page results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_dispinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_enum.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_enum.c

Purpose: Demonstrates paged user account enumeration with `NetUserEnum()`.

Important APIs/types/functions: Supports levels 0, 10, 20, and 23 with `USER_INFO_*`; level 23 prints user SID via `sid_string_tos()`.

Control flow: Parses hostname and level, loops with resume handle through all pages, casts by level, prints user fields, frees buffers, and reports final error status.

State and persistence behavior: Read-only account query.

Dependencies and integration points: Verifies user create/delete/set operations and SID formatting.

Risks: Large domains depend on resume progress. Level selection controls sensitive field exposure.

Test signals: Enumerate at all supported levels before/after disposable user creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_enum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getgroups.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getgroups.c

Purpose: Demonstrates retrieving global/domain groups for a user with `NetUserGetGroups()`.

Important APIs/types/functions: Supports levels 0 and 1 using `GROUP_USERS_INFO_0` and `_1`, with attributes at level 1.

Control flow: Parses hostname, username, and level, loops through result pages, prints group names/attributes, frees buffers, and handles errors.

State and persistence behavior: Read-only membership query.

Dependencies and integration points: Verifies `user_setgroups`, `group_adduser`, and `group_deluser`.

Risks: Only global group memberships are represented; local groups use a separate API.

Test signals: Add/set user group memberships and confirm output reflects changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getgroups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getinfo.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getinfo.c

Purpose: Demonstrates querying detailed user account information with `NetUserGetInfo()`.

Important APIs/types/functions: Handles many levels, including `USER_INFO_0/1/2/3/4/10/11/20/23`. Prints password age, privilege, home/script/profile fields, flags, logon times, logon hours, counts, SIDs, and primary group data where present.

Control flow: Parses hostname, username, and level, calls the API, switches on level to cast and print fields, frees the returned buffer, and cleans up.

State and persistence behavior: Read-only account metadata query.

Dependencies and integration points: Primary verifier for user add/setinfo/modals/group operations.

Risks: Some levels expose sensitive fields such as password placeholders, workstation restrictions, and account policy data. Large switch must stay aligned with NetAPI structures.

Test signals: Query a disposable user across all supported levels and compare selected fields after `user_setinfo`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getlocalgroups.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getlocalgroups.c

Purpose: Demonstrates retrieving local groups containing a user with `NetUserGetLocalGroups()`.

Important APIs/types/functions: Supports level 0 using `LOCALGROUP_USERS_INFO_0`; accepts flags and resume paging.

Control flow: Parses hostname, username, level, and optional flags, loops through pages, prints local group names, frees buffers, and handles final status.

State and persistence behavior: Read-only membership query.

Dependencies and integration points: Verifies local group membership operations from the user perspective.

Risks: Only level 0 is printed. Flag semantics are server-defined and lightly validated.

Test signals: Add a user to local groups, query with relevant flags, and compare with `localgroup_getmembers`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getlocalgroups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_modalsget.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_modalsget.c

Purpose: Demonstrates querying domain/user policy modal information with `NetUserModalsGet()`.

Important APIs/types/functions: Handles `USER_MODALS_INFO_0/1/2/3`, including password age/length/history, role, primary server, domain SID/name, and lockout policy.

Control flow: Parses hostname and level, calls the API, switches on level to print policy fields, converts domain SID where present, frees the buffer, and exits.

State and persistence behavior: Read-only policy query.

Dependencies and integration points: Complements `user_modalsset` and account policy administration.

Risks: Units are printed as days/seconds based on sample assumptions. Unsupported levels are not explained.

Test signals: Query all supported levels before/after modal policy changes in a test domain.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_modalsget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_modalsset.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_modalsset.c

Purpose: Demonstrates setting user/domain modal policy with `NetUserModalsSet()`.

Important APIs/types/functions: Supports levels 0, 1, 2, 3, and single-parameter levels 1001-1007 through `USER_MODALS_INFO_*` structures.

Control flow: Parses hostname, level, and numeric/string policy values, fills the matching modal structure, calls `NetUserModalsSet()`, reports `parm_err`, and cleans up.

State and persistence behavior: Mutates persistent account/domain policy on the target server/domain.

Dependencies and integration points: Paired with `user_modalsget`.

Risks: Policy changes are security-sensitive and global. Numeric parsing is weak, and some case labels are accepted without fully populated structures.

Test signals: Apply policy changes only in isolated domains, then verify exact fields with `user_modalsget`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_modalsset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_setgroups.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_setgroups.c

Purpose: Demonstrates replacing a user's global/domain group list with `NetUserSetGroups()`.

Important APIs/types/functions: Allocates `GROUP_USERS_INFO_0` or `_1` arrays through `NetApiBufferAllocate()` and submits member count to `NetUserSetGroups()`.

Control flow: Parses hostname, username, level, and group tokens, allocates the level-specific array, fills group names and optional attributes, calls the API, frees the buffer, and exits.

State and persistence behavior: Replaces persistent user group membership.

Dependencies and integration points: Verified by `user_getgroups` and group membership examples.

Risks: Destructive replacement can remove required memberships. Level 1 expects name/attribute pairs and parsing is positional.

Test signals: Set memberships for a disposable user and compare exactly with `user_getgroups`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_setgroups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_setinfo.c -->
## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_setinfo.c

Purpose: Demonstrates updating user account fields with `NetUserSetInfo()`.

Important APIs/types/functions: Supports many levels and parameter levels, including `USER_INFO_0`, `USER_INFO_1003`, `_1005`, `_1006`, `_1007`, `_1008`, `_1009`, `_1010`, `_1011`, `_1012`, `_1014`, `_1017`, `_1024`, `_1051`, `_1052`, and `_1053`.

Control flow: Parses hostname, username, level, and a value, fills the level-specific structure for password, privilege, home directory, comment, flags, script path, auth flags, full name, user comment, parameters, workstations, account expiration, max storage, logon server, country/code page, profile, home-drive, or password-expired fields, calls `NetUserSetInfo()`, reports errors, and cleans up.

State and persistence behavior: Mutates persistent user account properties on the target server/domain.

Dependencies and integration points: Main mutation counterpart to `user_getinfo`.

Risks: Security-sensitive fields are changed from minimally validated strings/integers. Some whole-structure levels are accepted but only small portions are populated, so parameter levels are safer.

Test signals: Update one field at a time on a disposable user and verify through `user_getinfo`; include policy rejection cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_setinfo.c -->
