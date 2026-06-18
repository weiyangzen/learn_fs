# subset-b-009884 research

Grouped research for Samba `source3/torture` VFS/winbind test helpers and `source3/utils` administrative utilities in this work item. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/utable.c -->
# sources/user-network-fs/samba/source3/torture/utable.c

## Purpose
`utable.c` provides two smbtorture tests for server-side Unicode filename handling. `torture_utable()` probes which UTF-16 code points can be converted into Unix names, created through SMB1 client calls, and represented in 8.3 alternate names. `torture_casetable()` probes server case-folding/equivalence behavior by repeatedly creating single-character names and storing matching character sets in the file content.

## Important APIs, types, and functions
- `torture_utable(int)` opens a test SMB connection, creates `\utable`, iterates code points `1..0xffff`, converts each `smb_ucs2_t` with `convert_string(CH_UTF16LE, CH_UNIX, ...)`, creates a file with `cli_openx`, queries its short name with `cli_qpathinfo_alt_name`, and writes a 64 KiB `valid.dat` bitmap of characters whose alternate name is not the default `X_A_L...` pattern.
- `form_name(int)` converts one UTF-16 code point to a `\utable\<char>` path in a static `fstring`.
- `torture_casetable(int)` uses `cli_ntcreate`, `cli_qfileinfo_basic`, `cli_read`, and `cli_writeall` to discover which later character opens/aliases an existing earlier character on the server.

## Control flow
Both tests open a torture connection, recreate the `\utable` directory, loop through the Basic Multilingual Plane, and skip characters that fail charset conversion or SMB create/open. `torture_utable()` treats successful file creation as "allowed" and treats alternate names that differ from the common `X_A_L` prefix as meaningful short-name candidates. `torture_casetable()` creates or opens a single-character file using `FILE_OPEN_IF`; if the file already has content, that content is interpreted as previously matching code points, then the current code point is appended for future matches.

## State and persistence behavior
Remote state is temporary under the SMB share path `\utable` and is removed with `torture_deltree` or `cli_rmdir` at the end. Local state includes a generated `valid.dat` file in the process working directory and the in-memory `valid[0x10000]` bitmap or `equiv[0x10000][8]` table. The tests intentionally mutate remote files as probes rather than validating a pre-existing fixture.

## Dependencies and integration points
The file depends on smbtorture connection helpers from `torture/proto.h`, SMB client APIs from `libsmb/clirap.h`, Samba charset conversion, `fstring` helpers, NT status checks, and ordinary POSIX file I/O for `valid.dat`. It is compiled into `smbtorture` by `source3/torture/wscript_build`.

## Risks and edge cases
- `torture_utable()` performs up to 65,535 remote create/query/delete cycles, so it is slow and sensitive to server throttling.
- `form_name()` returns a static buffer and is not reentrant.
- `torture_casetable()` stores raw host-endian `int` code points in remote file content, so output is a local diagnostic rather than a portable data format.
- Characters such as `.` and `\` are skipped only in `torture_casetable`; other problematic path characters depend on server behavior.
- A fixed `MAX_EQUIVALENCE` of 8 can abort if a server maps too many characters together.

## Test signals
Successful runs print progress and discovered equivalences, create and remove files on the target share, and return `True`. Failures include inability to open the torture connection, create `\utable`, create `valid.dat`, or write the full bitmap.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/utable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/vfstest.c -->
# sources/user-network-fs/samba/source3/torture/vfstest.c

## Purpose
`vfstest.c` is the interactive and scripted harness for testing Samba VFS modules without running a full smbd worker. It initializes a synthetic smbd connection rooted at the current directory, registers command sets, parses user commands, and invokes VFS command handlers from `cmd_vfs.c` and optional SMB1 chain tests.

## Important APIs, types, and functions
- `completion_fn()` provides readline command completion from the registered `cmd_list`.
- `next_command()` splits semicolon-delimited `-c` command strings.
- Built-in commands include `cmd_conf`, `cmd_help`, `cmd_debuglevel`, `cmd_freemem`, and `cmd_quit`.
- `add_command_set()`, `do_cmd()`, and `process_cmd()` register command tables, tokenize arguments, dispatch `struct cmd_set` handlers, and report non-OK `NTSTATUS` values.
- `process_file()` executes commands from a script file or stdin.
- `vfstest_get_smbreq()` builds a minimal `struct smb_request` with the synthetic connection and incrementing MID for VFS routines that need request context.
- `main()` handles popt options, Samba command-line/config setup, smbd shim setup, security/locking/file initialization, connection wrapper creation, and command execution.

## Control flow
Startup initializes locale and Samba client/server command-line state, parses `--file`, `--command`, and `--memreport`, sets `umask(0)`, reloads services, installs local smbd exit shims, adds command sets, initializes guest security and locking, creates a `vfs_state`, and calls `create_conn_struct_chdir()` for the current directory. It then executes a command file, a semicolon-separated command string, or an interactive `smb_readline` loop. Every command receives a fresh talloc stackframe, parsed argv array, and the shared `vfs_state`.

## State and persistence behavior
Long-lived state is in `struct vfs_state`: the synthetic `connection_struct`, monotonically increasing SMB message id, up to 1024 open `files_struct` slots, current directory pointer, and command-owned data buffer. `freemem` releases `vfs->data`; `--memreport` reports leaks after each command. Persistent effects are the actual filesystem mutations performed by VFS command handlers under the current working directory and any loaded smb.conf state.

## Dependencies and integration points
The harness integrates with smbd internals (`smbd/smbd.h`, globals, share-mode locks, shim hooks), command-line/config helpers, `SMBREADLINE`, Samba security/session setup, messaging context, `create_conn_struct_chdir()`, POSIX locking, and the external `vfs_commands[]` table. It is built as the `vfstest` binary by `wscript_build`.

## Risks and edge cases
- It runs smbd/VFS internals in a synthetic process; behavior that depends on a real client session, share definition, or daemon lifecycle may not be perfectly represented.
- Command parsing is simple whitespace tokenization and does not provide shell-like quoting semantics beyond `next_token_talloc`.
- `cmd_quit` exits directly from inside command dispatch.
- `process_cmd()` indexes `cmd[strlen(cmd)-1]`, so empty strings should be avoided by callers.
- The process intentionally sets `umask(0)`, so command scripts can create files with broad permissions.

## Test signals
The main signal is whether `vfstest` can initialize and execute command handlers with `NT_STATUS_OK`. Scripted runs via `-f` or `-c` are deterministic entry points for selftests, and `--memreport` exposes command-scoped talloc leaks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/vfstest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/vfstest.h -->
# sources/user-network-fs/samba/source3/torture/vfstest.h

## Purpose
`vfstest.h` declares the shared structures and command interface used by the VFS test harness and its command modules.

## Important APIs, types, and functions
- `struct func_entry` names a simple VFS function callback taking `struct connection_struct *` and a path.
- `struct vfs_state` carries harness state: connection, message id, open file table, current directory, and scratch data buffer.
- `vfstest_get_smbreq()` is declared for command modules that need a synthetic `struct smb_request`.
- `struct cmd_set` defines a command name, handler callback, description, and usage text.
- `cmd_test_chain()` is declared for the optional SMB1 chain parser command.

## Control flow
The header itself has no control flow. It defines the ABI between `vfstest.c`, `cmd_vfs.c`, and `vfstest_chain.c`: command tables expose `struct cmd_set` entries, and command handlers receive the same `vfs_state` and talloc context shape.

## State and persistence behavior
The main state contract is `struct vfs_state`. Ownership is shared by the harness: command modules may inspect and update `files`, `currentdir`, `data`, and `data_size`, while the harness owns allocation and teardown.

## Dependencies and integration points
The header relies on forward declarations from included Samba headers in users of the file: `connection_struct`, `files_struct`, `smb_Dir`, `smb_request`, `TALLOC_CTX`, and `NTSTATUS`. It is included by `vfstest.c`, `cmd_vfs.c`, and `vfstest_chain.c`.

## Risks and edge cases
- `files[1024]` is a fixed-size open-file registry; command modules must avoid unchecked indexes.
- `data` is an untyped scratch pointer, so producers and consumers must agree on representation.
- The header has no include guard in the excerpted file, so multiple inclusion safety depends on local include patterns.

## Test signals
Compile success of `vfstest` and optional SMB1 chain support is the primary signal. Runtime command tests validate that command handlers interpret `vfs_state` consistently.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/vfstest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/vfstest_chain.c -->
# sources/user-network-fs/samba/source3/torture/vfstest_chain.c

## Purpose
`vfstest_chain.c` adds a `cmd_test_chain()` command that regression-tests SMB1 chained request detection, chain length calculation, and parsing using embedded packet byte arrays, including malformed examples.

## Important APIs, types, and functions
- Static byte arrays such as `nonchain1_data`, `nonchain2_data`, `chain1_data`, `chain2_data`, `bug_8360_data`, `invalid1_data`, and `invalid2_data` are captured SMB1/NBSS request buffers.
- `cmd_test_chain()` calls `smb1_is_chain()`, `smb1_chain_length()`, and `smb1_parse_chain()` and accumulates boolean success.

## Control flow
The command first verifies that known single requests are not chains, then verifies chain status and exact chain lengths for known chained requests and a bug 8360 regression packet. It then checks invalid buffers return non-chain and expected lengths, and finally parses two valid chains into `struct smb_request **` arrays. It returns `NT_STATUS_OK` only if every predicate passes.

## State and persistence behavior
There is no persistent state. The only allocations are parser outputs under `talloc_tos()` during `smb1_parse_chain()`. The packet fixtures are static read-only data.

## Dependencies and integration points
This file depends on `vfstest.h` and smbd SMB1 parser helpers from `smbd/smbd.h`. It is conditionally compiled into `vfstest` by `wscript_build` only when `WITH_SMB1SERVER` is configured.

## Risks and edge cases
- The test relies on hard-coded binary packets; fixture corruption or endian-sensitive parser changes can make failures difficult to diagnose.
- It does not inspect parsed request contents, only parse success and count.
- `requests` is reused without explicit freeing inside the command, relying on the surrounding talloc stack behavior.

## Test signals
The command itself is a focused selftest: `NT_STATUS_OK` means chain detection, length calculation, invalid-buffer handling, and basic parsing still match the embedded fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/vfstest_chain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/wbc_async.c -->
# sources/user-network-fs/samba/source3/torture/wbc_async.c

## Purpose
`wbc_async.c` implements an asynchronous winbind client transport used by torture tests. It wraps winbind UNIX socket connection setup, nonblocking request/response exchange, optional privileged-pipe upgrade, serialized transaction dispatch through `tevent_queue`, retry handling, and debug callbacks.

## Important APIs, types, and functions
- `map_wbc_err_from_errno()`, `tevent_req_is_wbcerr()`, and `tevent_req_simple_recv_wbcerr()` convert system and tevent errors to `wbcErr`.
- `struct wb_context` holds a `tevent_queue`, active socket fd, privileged-state flag, socket directory, and debug callback.
- `make_nonstd_fd()` and `make_safe_fd()` duplicate descriptors away from stdin/stdout/stderr, set nonblocking mode, and set close-on-exec.
- `wb_context_init()` creates the context and chooses either a caller-supplied socket directory, `SELFTEST_WINBINDD_SOCKET_DIR` under nss-wrapper, or `WINBINDD_SOCKET_DIR`.
- `wb_connect_send/recv()` validates socket directory ownership, validates the socket, creates a safe AF_UNIX stream socket, and performs `async_connect_send`.
- `wb_open_pipe_send/recv()` connects to the nonprivileged pipe, performs an interface-version ping, optionally requests the privileged pipe directory, and reconnects there.
- `wb_trans_send/recv()` queues one winbind request, opens or reuses the pipe, sends with `wb_simple_trans_send`, retries transient failures after one second, and returns a talloc-moved response.
- `wbcSetDebug()`, `wbcSetDebugStderr()`, and `wbcDebug()` provide caller-controlled logging.

## Control flow
Callers allocate a `wb_context`, then submit requests through `wb_trans_send()`. Queue dispatch checks whether the cached fd appears closed with a zero-timeout `select()`, opens a pipe if needed or if privileged access is required, sends the request with the caller's pid, and completes when `wb_simple_trans_recv()` returns a response. Connection setup is a state machine: connect nonprivileged, ping interface version, optionally ask winbind for the privileged directory, close the old fd, reconnect privileged, and mark `is_priv`.

## State and persistence behavior
Runtime state is the cached winbind socket fd and whether it is privileged. Requests are serialized by `tevent_queue`, preventing concurrent writes on one fd. No persistent files are written by this code; it depends on winbindd's socket files and may read an environment variable in selftest mode.

## Dependencies and integration points
The file uses talloc, tevent async requests, `async_connect_send`, winbind protocol structs, `wb_simple_trans_send/recv` from `nsswitch/wb_reqtrans.h`, `set_blocking`, UNIX sockets, and nss-wrapper detection. The header declares additional async ID mapping, PAM, SID, and utility APIs implemented elsewhere.

## Risks and edge cases
- Directory and socket ownership checks allow root or the effective uid only; unusual test setups can fail as winbind unavailable.
- `closed_fd()` treats readable fds as closed, which is a pragmatic health check but can race with peer behavior.
- Transient transaction failures retry forever in one-second increments except for `WBC_ERR_WINBIND_NOT_AVAILABLE`, so a badly wedged daemon can stall callers.
- `strlcpy()` into `sun_path` truncation is not explicitly checked.
- One `wb_context` serializes requests; callers needing parallelism require multiple contexts.

## Test signals
Consumers should observe successful async completion through `wb_trans_recv()` and correct error mapping for unavailable winbind, auth errors, no memory, and unknown failures. Selftests can override the socket directory with `SELFTEST_WINBINDD_SOCKET_DIR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/wbc_async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/wbc_async.h -->
# sources/user-network-fs/samba/source3/torture/wbc_async.h

## Purpose
`wbc_async.h` is the public interface for the asynchronous winbind client helper used by Samba torture code and related async wbclient wrappers.

## Important APIs, types, and functions
- `enum wbcDebugLevel` defines fatal, error, warning, and trace levels.
- `wb_context_init()` creates the reusable transport context.
- `wb_trans_send()` and `wb_trans_recv()` provide the generic async winbind request/response primitive with optional privileged-pipe access.
- `wbcSetDebug()`, `wbcSetDebugStderr()`, and `wbcDebug()` control debug output.
- Error helpers expose `map_wbc_err_from_errno()`, `tevent_req_is_wbcerr()`, and `tevent_req_simple_recv_wbcerr()`.
- The header declares async wrappers for SID/UID/GID mapping, authentication, name/SID lookup, ping, interface version/details, netbios/domain names, and domain info.

## Control flow
The send/recv declarations follow tevent conventions: allocate a request with `_send`, drive the event loop, then call the matching `_recv` to collect outputs and a `wbcErr`. Higher-level async functions are layered on top of `wb_trans_send()`.

## State and persistence behavior
`struct wb_context` is opaque to callers. The header implies callers own output memory through talloc contexts passed to receive functions. No persistent state is declared.

## Dependencies and integration points
The header includes talloc, tevent, `nsswitch/libwbclient/wbclient.h`, and `nsswitch/wb_reqtrans.h`. It bridges Samba's tevent style with libwbclient data types such as `wbcDomainSid`, `wbcAuthUserParams`, `wbcDomainInfo`, and `winbindd_response`.

## Risks and edge cases
- All APIs depend on correct tevent loop ownership and matching send/recv calls.
- The transport can require privileged pipe access for some operations; callers must set `need_priv` correctly in generic transactions or use higher-level wrappers.
- Debug callbacks receive a `va_list` and must obey the printf attribute contract.

## Test signals
Compile-time interface conformance and successful async wbclient torture tests validate the header. Error helper tests should confirm tevent errors map to stable `wbcErr` values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/wbc_async.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/wscript_build -->
# sources/user-network-fs/samba/source3/torture/wscript_build

## Purpose
`wscript_build` defines Samba source3 torture/test binaries for waf, including `smbtorture3`, standalone message and passdb tests, `locktest2`, `vfstest`, and an RPC SAMR test.

## Important APIs, types, and functions
- `bld.SAMBA3_BINARY()` entries describe binary names, source lists, dependencies, install/selftest flags, and cflags.
- `TORTURE3_ADDITIONAL_SOURCE` conditionally adds `test_ctdbd_conn.c` when CTDB support is enabled.
- `SMB1_SOURCES` conditionally adds `vfstest_chain.c` when `WITH_SMB1SERVER` is configured.
- `smbtorture` receives `-DWINBINDD_SOCKET_DIR="..."` for async winbind tests.

## Control flow
The build script evaluates feature flags, composes source-list strings, and registers targets. `smbtorture` aggregates many torture source files including `utable.c` and `wbc_async.c`. `vfstest` always includes `cmd_vfs.c` and `vfstest.c`, and includes SMB1 chain tests only for SMB1 server builds.

## State and persistence behavior
This is build metadata rather than runtime code. It controls which generated build outputs exist and which binaries are marked for selftest. Runtime persistence is unaffected except through compiled feature availability.

## Dependencies and integration points
The targets depend on Samba build-system facilities and libraries such as `talloc`, `smbconf`, `libsmb`, `msrpc3`, `WB_REQTRANS`, `LOCKING`, `vfs`, `CMDLINE_S3`, `SMBREADLINE`, `pdb`, `AUTH_COMMON`, `auth`, and `cmocka`.

## Risks and edge cases
- Conditional source inclusion must match C declarations; building `vfstest_chain.c` without SMB1 parser support would fail.
- `smbtorture` has a broad source list, so dependency omissions can appear only under specific feature configurations.
- `WINBINDD_SOCKET_DIR` is compiled into `smbtorture`; selftests override it at runtime through `wbc_async.c` only when nss-wrapper is enabled.

## Test signals
Successful waf configuration/build and Samba selftest discovery of `smbtorture`, `vfstest`, `locktest2`, and `test_rpc_samr` are the main signals. Feature matrix builds with and without CTDB and SMB1 validate conditional paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/clirap2.c -->
# sources/user-network-fs/samba/source3/utils/clirap2.c

## Purpose
`clirap2.c` implements additional client-side RAP (Remote Administration Protocol) calls over SMB transaction `\PIPE\LANMAN`. These functions support legacy management operations for groups, users, open files, shares, servers, print queues, services, sessions, and connections, mainly for Samba's `net rap` and related utilities.

## Important APIs, types, and functions
- Buffer helpers and macros (`PUTBYTE`, `GETWORD`, `PUTSTRING`, `PUTSTRINGP`, `rap_getstring*`, `make_header`) marshal and unmarshal RAP's fixed and pointer-style ASCII structures.
- `cli_api()` wraps `cli_trans()` to send SMBtrans requests and returns heap-duplicated response parameter/data buffers.
- Group APIs include `cli_NetGroupDelete`, `cli_NetGroupAdd`, `cli_RNetGroupEnum`, `cli_RNetGroupEnum0`, `cli_NetGroupDelUser`, `cli_NetGroupAddUser`, `cli_NetGroupGetUsers`, and `cli_NetUserGetGroups`.
- User APIs include `cli_NetUserDelete`, `cli_NetUserAdd`, `cli_RNetUserEnum`, and `cli_RNetUserEnum0`.
- File/share/server APIs include `cli_NetFileClose`, `cli_NetFileGetInfo`, `cli_NetFileEnum`, `cli_NetShareAdd`, `cli_NetShareDelete`, `cli_get_pdc_name`, and `cli_get_server_name`.
- Print/service/session/connection APIs include `cli_NetPrintQEnum`, `cli_NetPrintQGetInfo`, `cli_RNetServiceEnum`, `cli_NetSessionEnum`, `cli_NetSessionGetInfo`, `cli_NetSessionDel`, and `cli_NetConnectionEnum`.

## Control flow
Each public function constructs a RAP parameter block with an API number, request format string, response format string, and fixed arguments. Calls that send structured records also build a data block with fixed fields and pointer offsets into a free-string area. `cli_api()` sends the SMB transaction, then the caller checks the 16-bit RAP result code, decodes converter/count values from response parameters, walks returned records in `rdata`, converts strings into local memory, and invokes a caller-supplied callback for each returned item.

## State and persistence behavior
The file itself keeps no global state. Remote state changes occur on the target SMB server: creating/deleting users and groups, adding/removing group members, closing files, adding/deleting shares, deleting sessions, and similar management operations. Memory returned from `cli_api()` is freed in each function with `SAFE_FREE`; transient talloc frames hold converted strings while callbacks run.

## Dependencies and integration points
It depends on `struct cli_state`, `cli_trans()`, RAP constants and structs from generated `rap.h`, service constants, Samba string conversion helpers, little-endian access macros, overflow/range helpers, and callback signatures declared in `clirap2.h`. `net rap` command modules are the primary consumers.

## Risks and edge cases
- RAP is legacy, ASCII-oriented, and limited by 16-bit counts and caller-provided buffer sizes; many functions note incomplete `ERRmoredata` resume handling.
- Manual marshalling uses fixed arrays and pointer arithmetic; every bounds check around `endp` matters.
- Some callbacks ignore the `state` parameter and pass `cli` instead in older functions, preserving historical behavior but surprising new callers.
- Error reporting maps only selected numeric RAP errors to messages.
- A few code paths show duplicated local declarations or duplicated `if (res == 0)` blocks, so this file benefits from compiler warnings and focused tests.

## Test signals
Remote integration tests using `net rap` against Samba or compatible SMB servers are the main validation signal. Useful checks include group/user add/delete/enumerate, file/session listing, share add/delete, PDC discovery, print queue enumeration, and malformed/large response handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/clirap2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/clirap2.h -->
# sources/user-network-fs/samba/source3/utils/clirap2.h

## Purpose
`clirap2.h` declares the public client RAP helper functions implemented in `clirap2.c`.

## Important APIs, types, and functions
- Forward declarations for `rap_group_info_1`, `rap_user_info_1`, and `rap_share_info_2` keep callers independent of full RAP struct definitions.
- Group, user, file, share, server, print queue, service, session, and connection functions expose legacy remote administration operations over an existing `struct cli_state`.
- Callback-heavy enum/get-info functions return decoded RAP records to caller-supplied function pointers.

## Control flow
The header has no runtime control flow. It defines call signatures used by utility modules, especially `net rap` helpers, to route decoded RAP records into display or command-specific callbacks.

## State and persistence behavior
State is external: callers provide an authenticated SMB client connection and callbacks. Functions may mutate remote server administrative state depending on the operation.

## Dependencies and integration points
The header includes `../libsmb/clirap.h` for `struct cli_state` and related client definitions. It is a bridge between Samba utility code and low-level RAP marshalling in `clirap2.c`.

## Risks and edge cases
- Many callbacks use long positional parameter lists, making accidental argument order mistakes easy.
- Most functions return integer RAP result codes rather than `NTSTATUS`, so callers must interpret legacy error values correctly.
- Header/API stability matters because multiple `net` modules may include it.

## Test signals
Build coverage of `net` RAP utilities and successful remote RAP integration commands validate this interface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/clirap2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/conn_tdb.c -->
# sources/user-network-fs/samba/source3/utils/conn_tdb.c

## Purpose
`conn_tdb.c` provides a compatibility-style iterator over active Samba tree connections, returning `connections_data` records for utilities such as `smbstatus`. Modern Samba connection state is collected from `smbXsrv_session_global` and `smbXsrv_tcon_global` records rather than directly from an old `connections.tdb` layout.

## Important APIs, types, and functions
- `struct connections_forall_state` holds an in-memory session lookup database, caller callback, private data, and emitted count.
- `struct connections_forall_session` is the compact per-session data cached by session id.
- `collect_sessions_fn()` converts each global SMB session into cached uid/gid, machine, address, cipher, dialect, signing algorithm, and authenticated flag.
- `traverse_tcon_fn()` combines each tree connection with its cached session data and calls the caller callback with `struct connections_data`.
- `connections_forall_read()` creates the temporary db, traverses sessions, traverses tree connects, and returns the number of callbacks or `-1` on traversal errors.

## Control flow
`connections_forall_read()` first builds a `session_by_pid` rbt db keyed by `session_global_id`. It then traverses all tree connections. Empty share names are skipped because a tcon can exist briefly before details are filled. For each complete tree connect, the matching session record is fetched if available, a `connections_data` struct is populated, the count is incremented, and the caller callback is invoked.

## State and persistence behavior
The function reads Samba server global state and stores only transient data in an in-memory db opened with `db_open_rbt()`. It does not write persistent databases. Returned `connections_data` contains copied fstrings and scalar values valid for the callback call.

## Dependencies and integration points
The file depends on dbwrap, in-memory rbt dbwrap, `smbXsrv_session_global_traverse`, `smbXsrv_tcon_global_traverse`, messaging/server-id structures, Samba session security helpers, and `conn_tdb.h`. It supports status/reporting utilities that need a stable connection-record abstraction.

## Risks and edge cases
- A session can disappear between the session and tcon traversals; missing session data falls back to uid/gid `-1` and empty strings.
- `memcpy()` assumes fetched session record size matches `struct connections_forall_session`.
- Only channel 0 is used for remote name/address and crypto fields.
- Callback return values propagate through traversal, so callback semantics affect overall traversal.

## Test signals
`smbstatus`-style output with active SMB sessions and tree connects is the key integration signal. Tests should cover authenticated and guest sessions, encrypted/signed sessions, empty/in-progress tcons, and disappearing sessions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/conn_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/conn_tdb.h -->
# sources/user-network-fs/samba/source3/utils/conn_tdb.h

## Purpose
`conn_tdb.h` defines the connection summary record and traversal API shared by smbd and status utilities.

## Important APIs, types, and functions
- `struct connections_data` contains server id, tree id, session id, uid/gid, service name, client address/machine, start time, SMB encryption/signing fields, dialect, and authentication flag.
- `connections_forall_read()` iterates active connection records and invokes a callback with optional private data.

## Control flow
The header does not implement control flow; it documents the callback shape consumed by readers of active connection state.

## State and persistence behavior
`connections_data` is a snapshot representation. It is not the persistent database format; current implementations synthesize it from live SMB session/tcon global state.

## Dependencies and integration points
It includes Samba source3 base headers for `server_id`, `fstring`, `NTTIME`, and related scalar types. Consumers include server status/reporting code and the implementation in `conn_tdb.c`.

## Risks and edge cases
- The structure is shared across utilities, so field additions can affect ABI expectations inside the tree.
- `uid_t` and `gid_t` may use `-1` sentinel values in practice even though their signedness is platform-dependent.
- Crypto fields are compact numeric representations that callers must format with the right dialect/signing/cipher lookup.

## Test signals
Compile coverage plus status utilities displaying all fields correctly are the main validation signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/conn_tdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/dbwrap_tool.c -->
# sources/user-network-fs/samba/source3/utils/dbwrap_tool.c

## Purpose
`dbwrap_tool.c` is a low-level command-line tool for inspecting and mutating Samba dbwrap/TDB databases. It supports typed fetch/store, delete, existence checks, wiping a database, and listing keys.

## Important APIs, types, and functions
- `enum dbwrap_op` and `enum dbwrap_type` classify supported operations and data encodings.
- Fetch/store helpers handle `int32`, `uint32`, NUL-terminated `string`, and `hex` data via dbwrap typed helpers or raw `TDB_DATA`.
- `dbwrap_tool_delete()`, `dbwrap_tool_exists()`, `dbwrap_tool_erase()`, and `dbwrap_tool_listkeys()` perform non-typed operations.
- `listkey_fn()` prints keys with printable bytes preserved and other bytes backslash-escaped as hex.
- `dispatch_table` maps operation/type pairs to implementation functions.
- `main()` parses `--persistent`/`--non-persistent`, validates operands, opens the database, and dispatches.

## Control flow
The program initializes Samba command-line context with log level 0, parses options, requires exactly one persistence mode, validates the operation-specific positional arguments, parses the requested type, initializes tevent and messaging, opens the named db with `db_open()`, and runs the matching dispatch entry. Persistent databases use transaction-aware store/delete helpers; non-persistent mode adds `TDB_CLEAR_IF_FIRST`, which may wipe data.

## State and persistence behavior
The target database is opened read/write with create mode `0644`. Store/delete/erase mutate it; fetch/list/exists read it. Non-persistent mode can clear the database when first opened, as warned by the option description. Hex store converts a string to binary data; string store writes a terminating NUL.

## Dependencies and integration points
The tool depends on dbwrap/dbwrap_open, util_tdb typed helpers, Samba command-line and loadparm context, messaging setup, talloc, tevent, popt, and data-blob hex helpers. It is useful for debugging Samba private and lock databases outside their owning daemons.

## Risks and edge cases
- `--non-persistent` may wipe the database because of `TDB_CLEAR_IF_FIRST`.
- Numeric parsing uses `strtol` without strict validation of trailing characters or range.
- `OP_DELETE`, `OP_ERASE`, and `OP_LISTKEYS` are registered only with `TYPE_INT32`, so user-specified alternate types will not dispatch.
- `exists` returns process status 1 when a key is absent, which is useful for scripts but different from operational failure.

## Test signals
Smoke tests can create a temporary db, store/fetch each type, list escaped keys, check exists exit codes, delete keys, and erase the db. Persistent mode should preserve records across invocations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/dbwrap_tool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/dbwrap_torture.c -->
# sources/user-network-fs/samba/source3/utils/dbwrap_torture.c

## Purpose
`dbwrap_torture.c` is a simple stress tool for persistent dbwrap/TDB transaction semantics. Multiple instances can update a shared counter array keyed by `"testkey"` and verify counters are monotonically increasing.

## Important APIs, types, and functions
- Global options include `timelimit`, `torture_delay`, `verbose`, `no_trans`, `db_name`, and `unsafe_writes`.
- `print_counters()` displays the last observed counter array.
- `each_second()` periodically prints counters for node 0 in non-verbose mode.
- `check_counters()` verifies no counter decreases and updates `old_data`.
- `do_sleep()` injects delays between operations for race amplification.
- `test_store_records()` performs the transaction/fetch-lock/increment/store/commit loop.
- `main()` parses options, opens the db, determines the local virtual node number, and runs the test.

## Control flow
After command-line setup, the program opens the test database. If running outside a cluster, it forces VNN 0. The test loop runs until `timelimit` expires or forever when zero. Each iteration optionally starts a dbwrap transaction, fetch-locks `testkey`, grows the record to include this node's counter, increments that counter, stores the record, commits if needed, checks monotonicity for verbose or node 0, and sleeps at configured points.

## State and persistence behavior
The database record `testkey` persists a packed array of `uint32_t` counters. `old_data` is process-local history used for monotonic checks. `--no-trans` switches to fetch-lock/record-store without explicit transactions and uses `TDB_CLEAR_IF_FIRST|TDB_INCOMPATIBLE_HASH`; `--unsafe-writes` uses `TDB_NOSYNC`.

## Dependencies and integration points
The file depends on dbwrap/dbwrap_open, transactions, record locks, Samba command-line/loadparm, messaging, tevent timers, cluster node helpers `get_my_vnn()`/`set_my_vnn()`, and util_tdb helpers. It is a diagnostic for dbwrap backends and CTDB-like multi-node behavior.

## Risks and edge cases
- Counter data is raw host-endian `uint32_t` array and not portable storage.
- `old_data` starts empty; printing before enough data exists can show no counters.
- `unsafe_writes` and `no_trans` deliberately weaken persistence/atomicity and are for torture scenarios only.
- The event timer is scheduled but the main loop is synchronous and sleeps, so timer progress depends on operations that pump events elsewhere being absent; this is mostly a diagnostic print hook.

## Test signals
The key signal is final `SUCCESS!` versus `The test FAILED`. Running several instances against the same db with delays increases coverage of locking and transaction behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/dbwrap_torture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/destroy_netlogon_creds_cli.c -->
# sources/user-network-fs/samba/source3/utils/destroy_netlogon_creds_cli.c

## Purpose
`destroy_netlogon_creds_cli.c` is a targeted test utility that intentionally corrupts the stored netlogon client credential session key for a workstation/domain/DC tuple. It is used to exercise recovery and failure paths around `netlogon_creds_cli` state.

## Important APIs, types, and functions
- `main()` is the only function. It expects `cli_computer domain dc`.
- It initializes Samba config, loadparm, tevent, messaging, and opens the private `netlogon_creds_cli` db.
- `netlogon_creds_cli_set_global_db()` installs the opened db.
- `netlogon_creds_cli_context_global()` constructs the credential context for `cli_computer$`, workstation secure channel, DC, and domain.
- `netlogon_creds_cli_lock()` obtains the stored credential state, then the utility increments `creds->session_key[0]` and stores it back with `netlogon_creds_cli_store()`.

## Control flow
The program validates the argument count, initializes required Samba contexts, opens or creates the `netlogon_creds_cli` private database with `0600` permissions, creates a global credential context, locks/fetches credentials, mutates one byte of the session key, stores the corrupted state, frees the credential state, and exits 0 on success.

## State and persistence behavior
This utility deliberately persists corrupted netlogon credential state in Samba's private `netlogon_creds_cli` database. It is destructive for that credential tuple and should be run only in test contexts.

## Dependencies and integration points
It integrates with loadparm, messaging, dbwrap, private db path resolution, and `libcli/auth/netlogon_creds_cli.h`. The target state is later consumed by netlogon secure-channel clients.

## Risks and edge cases
- It has no confirmation prompt and intentionally damages authentication state.
- The machine account name is formed by appending `$` to `argv[1]`.
- A missing existing credential record causes lock/fetch failure rather than creating a useful test state.
- DB open uses create mode, but the semantic target must already be meaningful to the netlogon credential layer.

## Test signals
Success is exit 0 after `netlogon_creds_cli_store()`. Downstream tests should observe secure-channel credential verification or recovery failures caused by the modified session key.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/destroy_netlogon_creds_cli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/eventlogadm.c -->
# sources/user-network-fs/samba/source3/utils/eventlogadm.c

## Purpose
`eventlogadm.c` is a Samba command-line utility for managing Windows-style event logs backed by TDB and Samba registry data. It can write event records from stdin, dump stored records, and add event source registry entries.

## Important APIs, types, and functions
- `usage()` and `display_eventlog_names()` present command help and configured event logs.
- `eventlog_add_source()` validates an event log, updates its `Sources` `REG_MULTI_SZ`, creates the source subkey, and writes `EventMessageFile`.
- `DoAddSourceCommand()` initializes registry access, wraps `eventlog_add_source()` in a registry transaction, and commits/cancels.
- `DoWriteCommand()` opens an eventlog TDB, parses log-entry text from stdin with `parse_logentry()`, normalizes records with `fixup_eventlog_record_tdb()`, and stores them using `evlog_push_record_tdb()`.
- `DoDumpCommand()` reads records by number with `evlog_pull_record_tdb()` and prints them with NDR formatting.
- `main()` parses `-o`, `-s`, `-d`, and `-h`, loads configuration, and dispatches `write`, `addsource`, or `dump`.

## Control flow
Default operation is `write`. After getopt parsing and config load, `main()` dispatches by operation name. `write` reads stdin line by line until `parse_logentry()` marks end-of-record, then writes non-null timestamped records. `addsource` starts a registry transaction before updating source metadata. `dump` starts at record 1 or the supplied record number and prints records until no record is returned.

## State and persistence behavior
`write` persists event records into the named eventlog TDB. `addsource` persists registry changes under `KEY_EVENTLOG\<eventlog>`, including the `Sources` list and source subkey. `dump` is read-only. The configured eventlog list comes from smb.conf.

## Dependencies and integration points
The file depends on Samba eventlog APIs, registry APIs, admin token creation, registry DB backend transactions, NDR printing for eventlog records, loadparm, `fstring`, and string wrappers. It is an administrative bridge between textual event records, eventlog TDBs, and registry metadata.

## Risks and edge cases
- `write` uses a fixed 1024-byte input line buffer, so long fields may be truncated by `fgets`.
- `eventlog_add_source()` expects an existing valid eventlog registry key and an existing `Sources` value of type `REG_MULTI_SZ`.
- Failure while setting `EventMessageFile` returns directly rather than flowing through the final cleanup path, although the talloc frame is process-scoped.
- `dump` loops until a missing record, so sparse records stop output.

## Test signals
Useful tests create a configured eventlog, add a source, write sample stdin records, dump from record 1 and later offsets, and verify registry `Sources` and `EventMessageFile` values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/eventlogadm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/interact.c -->
# sources/user-network-fs/samba/source3/utils/interact.c

## Purpose
`interact.c` provides small user-interaction helpers for Samba command-line tools: single-character prompts and edit-in-external-editor workflows.

## Important APIs, types, and functions
- `get_editor()` chooses `$VISUAL`, then `$EDITOR`, then `vi`, caching the result in a static 64-byte buffer.
- `interact_prompt()` disables canonical input and echo, prompts until the user enters an accepted character or newline for the default, restores terminal settings, and returns the character or EOF.
- `interact_edit()` writes an initial string to a secure temporary file, runs the selected editor on it, reads the edited content into a talloc string, unlinks the file, and returns it.

## Control flow
`interact_prompt()` temporarily changes terminal flags with `tcgetattr`/`tcsetattr`, loops with `getchar()`, validates against a lowercase accept string, and restores flags before returning. `interact_edit()` creates `/tmp/net_idmap_check.XXXXXX` with group/other permissions masked off, writes the initial string, launches `system("<editor> <file>\n")`, reads the file back in 128-byte chunks, and steals the result onto the caller's talloc context.

## State and persistence behavior
The editor helper creates a temporary file and unlinks it after reading or on most error paths. The chosen editor is cached in process-static memory. No persistent application state is written unless the external editor or environment causes side effects.

## Dependencies and integration points
The file uses Samba `d_printf`/`DEBUG`, talloc string append/steal, POSIX termios, `mkstemp`, stdio, `system()`, and environment variables. It is declared by `interact.h` and used by interactive `net` subcommands.

## Risks and edge cases
- `system()` builds a shell command from the editor string and temp path, so unusual editor values can invoke shell metacharacters.
- `interact_prompt()` does not check terminal API failures and may misbehave on non-TTY stdin.
- `tolower(c)` should be used carefully for EOF and locale behavior.
- The temporary filename is hard-coded under `/tmp` and named for net idmap.

## Test signals
Manual tests can verify default selection, accepted-character filtering, terminal restoration after invalid input, editor selection through environment variables, and cleanup of temp files. Automated tests should mock stdin/editor behavior where possible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/interact.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/interact.h -->
# sources/user-network-fs/samba/source3/utils/interact.h

## Purpose
`interact.h` declares interactive helper functions for Samba utilities.

## Important APIs, types, and functions
- `interact_edit(TALLOC_CTX *mem_ctx, const char *str)` opens an external editor on initial text and returns edited content allocated under `mem_ctx`.
- `interact_prompt(const char *msg, const char *accept, char def)` asks for one accepted character with a default.

## Control flow
No control flow is implemented in the header. It defines a small API for command modules that need human confirmation or text editing.

## State and persistence behavior
The header implies returned memory ownership through talloc. Runtime state and temporary-file behavior live in `interact.c`.

## Dependencies and integration points
It includes talloc and is consumed by utility modules such as net/idmap tooling that need interactive edits or prompts.

## Risks and edge cases
- Callers must handle `NULL` from `interact_edit()` and EOF or unexpected return values from `interact_prompt()`.
- The API assumes synchronous terminal/editor interaction.

## Test signals
Compile coverage and command-level interactive tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/interact.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/log2pcaphex.c -->
# sources/user-network-fs/samba/source3/utils/log2pcaphex.c

## Purpose
`log2pcaphex.c` extracts SMB packet traces from high-debug Samba logs and emits either raw-IP pcap data or text2pcap-compatible hex output.

## Important APIs, types, and functions
- `struct tcpdump_file_header` and `struct tcpdump_packet` describe pcap headers.
- Static IP/TCP header templates wrap SMB/NBSS payloads for raw-IP pcap output.
- `print_pcap_header()`, `print_pcap_packet()`, `print_hex_packet()`, and `print_netbios_packet()` produce the output formats.
- `read_log_msg()` reconstructs an SMB header/parameter section from `show_msg()` log output.
- `read_log_data()` reads byte dumps from `dump_data()` log output into the SMB data area.
- `main()` parses `--quiet` and `--hex`, opens optional input/output files, scans log headers, reconstructs packets, and writes output.

## Control flow
The scanner reads the input log line by line. On `show_msg` headers it starts or advances packet reconstruction and reads the structured SMB metadata lines. On `dump_data` headers during a packet, it reads the logged data bytes. When another header appears, it flushes the current packet in hex or pcap format and resets. Without `--hex`, it writes a pcap file header first.

## State and persistence behavior
Global state includes `quiet`, `hexformat`, `curpacket`, `curpacket_len`, and `line_num`. The tool writes only to the chosen output file/stdout. It allocates packet buffers dynamically and frees them after flushing.

## Dependencies and integration points
It depends on Samba SMB header offset macros from `includes.h`, popt, stdio, POSIX file APIs, endian helpers (`htons`), and the historical `show_msg()`/`dump_data()` log format. Output can be consumed by Wireshark directly as pcap or via text2pcap in hex mode.

## Risks and edge cases
- It uses `assert(fscanf(...))`, so malformed logs can abort the process.
- The NBSS length copy has a TODO about platform endian correctness.
- pcap output uses dummy IPs, ports, timestamps, and checksums.
- Samba log level 10 may truncate packets, and the tool reports incomplete traces unless quiet.
- The final packet is not flushed after EOF unless another header triggers flushing, so trailing packet handling is fragile.

## Test signals
Fixture logs containing `show_msg` and `dump_data` blocks should produce parseable pcap/hex output. Tests should cover truncated dumps, malformed lines, stdin/stdout paths, and `--quiet` warning suppression.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/log2pcaphex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/mdsearch.c -->
# sources/user-network-fs/samba/source3/utils/mdsearch.c

## Purpose
`mdsearch.c` is a command-line client for Samba's Spotlight/metadata search service (`mdssvc`). It connects to a server over SMB IPC, opens the mdssvc RPC pipe, runs a metadata query for a share/path, and prints matching paths.

## Important APIs, types, and functions
- Global options `opt_path` and `opt_live` select server-relative base path and live query mode.
- `main()` handles all behavior: Samba command-line and credential setup, full IPC connection, mdssvc RPC pipe opening, `mdscli_connect`, search creation, result polling, path lookup, close, and disconnect.

## Control flow
The program parses options and positional `<server> <share> <query>`, strips leading `//` or `\\` from the server, initializes tevent and messaging, obtains credentials, connects to `IPC$`, opens the mdssvc RPC pipe without auth, and creates an mdssvc client context for the target share. It chooses a base path from `--path` or `mdscli_get_basepath()`, starts the search, sleeps briefly for non-live searches, then repeatedly calls `mdscli_get_results()`. CNIDs are resolved to paths with `mdscli_get_path()` and printed. Non-live searches stop on no more matches; live searches poll indefinitely.

## State and persistence behavior
The utility is mostly read-only from the client's perspective, but it creates server-side mdssvc search state that is closed with `mdscli_close_search()` and a service context closed with `mdscli_disconnect()`. It does not persist local files.

## Dependencies and integration points
It integrates with Samba command-line credentials, SMB client full connection, transport parsing, IPC tree connect, RPC client pipe code, generated mdssvc NDR table, and `rpc_client/cli_mdssvc.h` helpers. It relies on the server exposing mdssvc for the target share.

## Risks and edge cases
- Usage validation checks `server == NULL || mds_query == NULL` but does not explicitly require `share != NULL` before passing it to mdssvc.
- Live mode is an infinite polling loop until interrupted.
- It opens the mdssvc pipe with noauth after authenticating the SMB connection; server policy must allow that pipe behavior.
- Errors after messaging initialization must free global command-line messaging context, which the fail labels handle.

## Test signals
Integration tests require a Samba server with mdssvc enabled and indexed content. Expected signals are successful query results, no-more-matches handling for non-live mode, and stable path resolution for returned CNIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/mdsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/mvxattr.c -->
# sources/user-network-fs/samba/source3/utils/mvxattr.c

## Purpose
`mvxattr.c` recursively renames an extended attribute from one name to another on one or more filesystem paths. It is an administrative migration helper for xattr namespace/key changes.

## Important APIs, types, and functions
- Global `state` stores `follow_symlink`, `print`, `force`, `verbose`, `xattr_from`, and `xattr_to`.
- `rename_xattr()` is the `nftw()` callback. It reads the source xattr, writes the destination xattr with create or replace semantics, removes the source xattr, and optionally prints the rename.
- `main()` enforces root, parses `--from`, `--to`, `--follow-symlinks`, `--print`, `--verbose`, and `--force`, validates paths, and invokes `nftw()` for each path.

## Control flow
The program exits unless run as root. After option parsing, each positional path is traversed with `nftw()` using `FTW_PHYS` unless symlink following is requested. The callback ignores symlink entries, skips files without the source xattr, copies the exact xattr value into a variable-length stack buffer, creates the destination xattr, optionally replaces it under `--force`, removes the source xattr, and returns nonzero on error.

## State and persistence behavior
The tool mutates filesystem xattrs in place. A successful operation removes `state.xattr_from` and writes `state.xattr_to` with the same bytes. If destination write succeeds but source removal fails, both xattrs may remain. It does not maintain rollback state.

## Dependencies and integration points
It depends on POSIX/nftw traversal, platform xattr APIs (`getxattr`, `setxattr`, `removexattr`), popt, talloc, and Samba output helpers. It is intended for local filesystem administration, not SMB protocol access.

## Risks and edge cases
- Must run as root, likely because xattrs of interest may be privileged.
- The xattr value is stored in a variable-length stack array sized from `getxattr`; very large xattrs can stress stack limits.
- Symlink handling is partly duplicated: traversal can avoid following symlinks and the callback also ignores `FTW_SL`.
- Return status for multiple paths is overwritten by the last `nftw()` call.
- No rollback exists for partial failures.

## Test signals
Tests can create temporary files with source xattrs, run forced and non-forced destination cases, verify source removal and byte preservation, confirm missing source xattrs are skipped, and validate symlink traversal modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/mvxattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net.c -->
# sources/user-network-fs/samba/source3/utils/net.c

## Purpose
`net.c` is the top-level entry point and command dispatcher for Samba's `net` utility. It parses global options and credentials, initializes Samba client context, defines the root command table, and implements several local trust/SID/auth-user commands directly.

## Important APIs, types, and functions
- `get_sec_channel_type()` maps textual secure-channel parameters to `netr_SchannelType`.
- Trust/password helpers include `net_changetrustpw()`, `net_primarytrust_dumpinfo()`, `net_primarytrust()`, and `net_changesecretpw()`.
- Auth-user helpers include `net_setauthuser()` and `net_getauthuser()` for winbind IPC credentials in secrets.
- SID/RID helpers include `net_getlocalsid()`, `net_setlocalsid()`, `net_setdomainsid()`, `net_getdomainsid()`, `search_maxrid()`, `get_maxrid()`, and `net_maxrid()`.
- `net_func[]` is the root `struct functable` dispatch table for `rpc`, `rap`, `ads`, `file`, `share`, `session`, `user`, `group`, `idmap`, `status`, `registry`, `eventlog`, `vfs`, `witness`, and many other subcommands.
- `main()` parses global popt options into `struct net_context`, sets credentials and Kerberos ccache, initializes messaging, and calls `net_run_function()`.

## Control flow
Startup blocks SIGPIPE, initializes locale/gettext, initializes Samba command-line context with client config, sets default log level 0, creates a popt context with many global options, and records parsed values in `net_context`. It derives explicit-credential state from the credentials object, chooses the workgroup/domain, handles legacy NTLM ccache features, determines the Kerberos credential cache name, initializes command-line messaging, applies requester netbios name and default target workgroup, loads network interfaces, initializes security, burns command-line secrets, then dispatches the remaining argv through `net_run_function()`.

## State and persistence behavior
Most persistent state changes are delegated to subcommands. Direct functions here can mutate `secrets.tdb` machine trust data, auth-user credentials, local/domain SIDs, keytab synchronization state, and passdb-derived RID state. `net_context` is request-scoped talloc state carrying all global options and shared contexts.

## Dependencies and integration points
The file integrates with nearly every Samba source3 management subsystem: credentials, gensec, Kerberos, loadparm, messaging, secrets, passdb, libnetapi, ADS/RPC/RAP modules, registry/eventlog/vfs/witness helpers, gettext, and generated `net_proto.h`. Subcommand implementations live across many sibling `net_*.c` files.

## Risks and edge cases
- Many global options are meaningful only to specific subcommands; invalid combinations are often handled downstream.
- `changesecretpw` is intentionally dangerous and requires `-f`, but it directly changes domain member machine account secrets.
- Kerberos ccache selection has several fallback layers and exits if no cache name can be established.
- `get_sec_channel_type("PDC")` maps to `SEC_CHAN_BDC`, preserving historical semantics that can surprise readers.
- Root command dispatch relies on generated prototypes and a large command table, so build coverage across optional features is important.

## Test signals
Command-level tests should cover `net help`, global option parsing, credential handling, `getlocalsid`/`setlocalsid`, `getdomainsid`, `setauthuser`/`getauthuser`, `maxrid`, and representative dispatch into RPC/RAP/ADS/local subcommands. Dangerous secret-changing commands should be tested only in isolated fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net.h -->
# sources/user-network-fs/samba/source3/utils/net.h

## Purpose
`net.h` defines shared data structures, constants, transport flags, translation helpers, and includes for Samba's `net` utility and its many subcommand modules.

## Important APIs, types, and functions
- `struct net_context` is the central option/context object passed to all `net` subcommands. It contains parsed CLI options, credentials, messaging, netlogon, loadparm, output flags, witness options, VFS traversal options, and private data.
- `struct net_dc_info` summarizes domain controller properties.
- `NET_TRANSPORT_*` flags classify local, RAP, RPC, and ADS command transports.
- `struct functable` defines command dispatch entries with function pointer, valid transports, description, and usage.
- `rpc_command_fn` is the common RPC command callback signature.
- `copy_clistate`, `rpc_sh_ctx`, and `rpc_sh_cmd` support share-copy and interactive RPC shell state.
- `_()` wraps gettext when available.
- Constants such as `NET_FLAGS_*` and `NET_MODE_SHARE_MIGRATE` are shared option/mode flags.

## Control flow
The header has no runtime control flow. It establishes the shared ABI: `net.c` fills a `net_context`, command tables refer to `struct functable`, and subcommands inspect flags and context fields to choose transport-specific behavior.

## State and persistence behavior
`net_context` is transient per process invocation, but many fields reference contexts that can mutate persistent Samba state, such as credentials, netlogon credential contexts, messaging, and loadparm. The header itself does not persist data.

## Dependencies and integration points
It forward-declares `struct cli_state`, includes generated LSA types, gettext/libintl support, `utils/net_proto.h`, and `utils/net_help_common.h`. It is included by most `source3/utils/net_*.c` modules.

## Risks and edge cases
- `net_context` has grown into a broad option bag; adding fields can increase coupling and accidental option reuse across subcommands.
- Many boolean options are `int`, reflecting popt storage patterns rather than strict typed state.
- Transport flags must be kept consistent with command implementations or help/dispatch can advertise unsupported modes.
- Header changes can trigger broad recompiles and subtle ABI issues across utility modules.

## Test signals
Successful compilation of all `net_*` modules is the primary interface signal. Runtime `net help` output and subcommand dispatch validate `functable` and transport metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net.h -->
