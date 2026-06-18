# subset-b-009824 research

Grouped research report for the Samba `source3/libsmb` and `source3/locale` subset. Each section is delimited for reconciliation into its source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/proto.h -->
# sources/user-network-fs/samba/source3/libsmb/proto.h

Purpose: `proto.h` is the central prototype header for the legacy Samba3 `libsmb` client API. It forward-declares client-side connection, DFS, file, metadata, quota, I/O, security descriptor, transaction, symlink, and password-change entry points implemented across multiple `libsmb/*.c` files. It is not an implementation unit and has no direct persistence, but it is a high-value ABI/API surface because many C users include it to call synchronous and tevent-based SMB1/SMB2 client helpers.

Important APIs and types: the header forward-declares `struct cli_state`, `struct cli_credentials`, `struct smbXcli_transport`, `struct smb_transports`, `struct client_dfs_referral`, `struct file_info`, `struct print_job_info`, `struct smb_create_returns`, and other protocol helper types. Most operations follow Samba's async triplet pattern: `*_send(TALLOC_CTX *, struct tevent_context *, ...)`, `*_recv(struct tevent_req *, ...)`, and a synchronous wrapper, for example `cli_session_setup_creds_send/recv/cli_session_setup_creds`, `cli_tcon_andx_send/recv/cli_tcon_andx`, `cli_ntcreate_send/recv/cli_ntcreate`, `cli_list_send/recv/cli_list`, `cli_read_send/recv/cli_read`, and `cli_writeall_send/recv/cli_writeall`. `NONNULL()` annotations on selected connection calls encode API contract expectations for static analysis and compiler checking.

Control flow and integration: callers use connection helpers such as `cli_start_connection`, `cli_connect_nb`, `cli_full_connection_creds_send`, or `cli_full_connection_creds` to establish a `cli_state`, then session setup/tree-connect helpers, then file and metadata calls. DFS resolution flows through `cli_cm_open`, `cli_dfs_get_referral_ex`, `cli_resolve_path`, and `cli_dfs_target_check`. File operations cover path and fnum metadata updates, POSIX extension operations, NT create/open/close, locking, disk attributes, EAs, notify, and NT transact create. Security descriptor operations expose query/set helpers; transaction helpers expose generic `cli_trans_send/recv`; symlink helpers expose reparse point creation, readlink, and raw reparse data fetch. The header integrates with Samba's tevent/talloc memory model and NTSTATUS-based error reporting rather than errno-only APIs.

State and persistence: all state is owned by the underlying `cli_state`, `tevent_req`, talloc context, or returned structures. The header itself stores nothing. Callers must preserve event contexts until async requests finish and must allocate output storage under suitable talloc parents. Several functions take mutable output pointers and transfer ownership via talloc.

Dependencies: consumers need Samba client headers, SMB protocol constants, security descriptor definitions, quota structures, tevent, talloc, NTSTATUS, and transport definitions. Because this header aggregates many modules, changing it has broad rebuild and compatibility impact.

Risks: stale prototypes can silently break link-time or runtime behavior if implementation signatures drift. Many interfaces expose raw protocol buffers or caller-provided lengths, so tests should cover bounds, ownership, and NTSTATUS propagation in the implementation files. The API mixes SMB1-specific helpers with SMB2-capable wrappers, so callers must check negotiated protocol support before assuming an operation is valid.

Test signals: compile coverage for all `libsmb` users is the main signal. Functional tests should exercise connection/session setup, DFS referral resolution, file create/read/write/close, listing, notify, quotas, security descriptor round-trips, symlink/reparse handling, and sync wrappers around async calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/pylibsmb.c -->
# sources/user-network-fs/samba/source3/libsmb/pylibsmb.c

Purpose: `pylibsmb.c` implements Samba's internal Python C extension module `libsmb_samba_cwrapper`. It exposes a `LibsmbCConn` Python type backed by a `struct cli_state`, giving Samba Python code direct access to SMB client operations such as connect, create/open, read/write, listing, notify, security descriptors, POSIX extension calls, FSCTLs, reparse/symlink handling, and server-side copy. The file explicitly notes this binding is internal to Samba and may change without external ABI guarantees.

Important APIs and types: `struct py_cli_state` is the core Python object and owns `cli`, `ev`, a request wait function, optional threaded event state, an oplock waiter, pending oplock-break records, and a condition pointer. With pthread support, `struct py_cli_thread` owns a shutdown pipe, `tevent_fd`, shutdown flag, pthread id, and saved Python thread state. `struct py_cli_notify_state` represents a pending change-notify request exposed as a Python object with `get_changes(wait=...)`. Public Python methods are registered in `py_cli_state_methods`, including `settimeout`, `echo`, `create`, `create_ex`, `close`, `write`, `read`, `truncate`, `delete_on_close`, `notify`, `list`, `get_oplock_break`, `unlink`, `mkdir`, `rmdir`, `rename`, `chkpath`, `savefile`, `loadfile`, `get_sd`, `set_sd`, `protocol`, `have_posix`, `smb1_posix`, `smb1_readlink`, `smb1_symlink`, `smb1_stat`, `fsctl`, `qfileinfo`, `mknod`, and `copy_chunk`. Module-level helpers include `unix_mode_to_wire` and `wire_mode_to_unix`.

Control flow: `py_cli_state_init` parses `host`, `share`, loadparm, optional credentials, multi-threaded flag, SMB1 forcing, IPC mode, POSIX request mode, and SMB2 negotiate contexts. It configures a normal tevent context or a `poll_mt` context plus background thread, builds `struct smb_transports` from loadparm, then calls `cli_full_connection_creds_send` and waits through `py_tevent_req_wait_exc`. In threaded mode it also starts `cli_smb_oplock_break_waiter_send`; callbacks enqueue oplock breaks and wake Python waiters. Most methods allocate a talloc stack frame, submit a `cli_*_send` request, wait through the selected wait function, call the matching `*_recv`, translate `NTSTATUS` to Python `NTSTATUSError`, and return Python scalars, bytes, dicts, lists, or pytalloc-wrapped NDR objects.

State and persistence: the Python object owns the live SMB connection and event context until deallocation; `py_cli_state_dealloc` frees the thread state and waiter, frees the event context, then shuts down `cli`. In threaded mode, the destructor writes to a shutdown pipe and joins the poll thread while releasing the GIL. Oplock breaks are persisted only in an in-memory talloc array until consumed. Notify objects own one pending tevent request and hold a reference to the connection until the request completes or the object is destroyed. Remote file state is server-side and is manipulated via fnums returned from create/open calls.

Dependencies and integration: this module bridges Python's C API, Samba's py3compat helpers, credentials and loadparm Python adapters, tevent/talloc, `libsmb/proto.h`, `cli_smb2_fnum`, SMB2 negotiate/create context helpers, NDR security descriptors, POSIX/reparse helpers, and NTSTATUS Python exception helpers. During module init it imports `samba.dcerpc.security.dom_sid`, exports many SMB protocol constants and FSCTL values, and registers the `LibsmbCConn` type.

Risks: GIL and tevent threading are delicate. The trace callback saves/restores the Python thread state around poll waits, and destructor order must avoid closing sockets while requests are live. Several raw protocol surfaces (`qfileinfo`, `fsctl`, create contexts, negotiate contexts) accept bytes and numeric levels from Python; malformed inputs must be rejected without memory misuse. `loadfile` sizes a Python bytes object from server-reported file size, so huge files can drive memory pressure. Some paths use `NULL` talloc parents for requests and depend on immediate cleanup. Error paths in create/reparse handling build rich `NTSTATUSError` values and must avoid reference leaks. SMB1 POSIX helpers require negotiated support and should not be assumed on SMB2-only connections.

Test signals: Python integration tests should create a temporary share connection, exercise anonymous and credentialed connection paths, single-threaded and multi-threaded wait paths, read/write/truncate/list/rename/delete workflows, create contexts and returned create metadata, notify `wait=False` and `wait=True`, oplock-break retrieval on threaded connections, security descriptor round-trips, POSIX info/listing when supported, SMB1 POSIX methods on SMB1-capable servers, invalid negotiate/create context input, invalid qfileinfo lengths, and module constant availability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/pylibsmb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/samlogon_cache.c -->
# sources/user-network-fs/samba/source3/libsmb/samlogon_cache.c

Purpose: `samlogon_cache.c` manages Samba's persistent Netlogon `netr_SamInfo3` cache in `netsamlogon_cache.tdb`. The cache stores user logon information by SID for later lookup by winbind and related authentication/account code, while deliberately removing session keys before writing data to disk.

Important APIs: `netsamlogon_cache_init` opens the TDB under `cache_path()`, checks it, and retries once after truncating a corrupt database. `netsamlogon_clear_cached_user` deletes the user SID key. `netsamlogon_cache_store` writes a domain marker and a serialized `netsamlogoncache_entry` containing timestamp and sanitized `netr_SamInfo3`. `netsamlogon_cache_get` fetches and NDR-decodes a user entry. `netsamlogon_cache_have` checks existence for a SID key. `netsamlog_cache_for_all` traverses user-like SID records and invokes a callback with SID string, timestamp, and decoded info3.

Control flow: initialization is lazy and global through static `netsamlogon_tdb`. Store first records a domain SID marker with dummy data using `TDB_INSERT`, composes the user SID from domain SID plus RID, fills missing `full_name` from the current cache if possible, fills missing `account_name` from the supplied username, zeros credential/session key fields, NDR-serializes the cache entry, and stores by SID string with `TDB_REPLACE`. Get computes the same SID string key, fetches raw TDB data, NDR-decodes the complete blob, deletes corrupt entries, and returns a talloc copy of `r.info3`. Traversal filters out malformed keys, non-null-terminated keys, invalid SIDs, and non-user-looking SIDs (`num_auths != 5`) before decoding and calling the consumer.

State and persistence: persistent state lives in `netsamlogon_cache.tdb` with file mode `0600`. Keys are textual SID strings. Domain-marker records contain only a dummy byte and are intentionally separate from full user entries. Cache entries carry a timestamp but this file does not enforce expiration. The static TDB handle remains open after first initialization.

Dependencies and integration: the file depends on Samba TDB utilities, NDR generated PAC/cache structures, SID helpers, talloc stack frames, debug logging, and `cache_path`. It is exported through `samlogon_cache.h` and used by authentication/winbind paths that need cached logon information.

Risks: truncating a corrupt cache is destructive but intentionally limited to one retry. `netsamlog_cache_traverse_cb` allocates `mem_ctx` but decodes into `state->mem_ctx`, so the temporary child context mainly bounds callback-local allocations; decode lifetime should be watched if this code changes. The cache intentionally strips secrets, and regressions there would be security-sensitive. Global `netsamlogon_tdb` has no explicit locking in this file beyond TDB's own behavior.

Test signals: tests should cover first-open success, corrupt TDB truncation/reopen, store/get round-trip, missing username/full-name filling, zeroing of key fields in serialized data, delete by SID, domain marker existence, corrupt record deletion on get, traversal filtering of marker and malformed keys, and callback error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/samlogon_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/samlogon_cache.h -->
# sources/user-network-fs/samba/source3/libsmb/samlogon_cache.h

Purpose: `samlogon_cache.h` declares the public interface for the Netlogon `netr_SamInfo3` cache implemented in `samlogon_cache.c`. It gives other Samba components a small API for initializing, storing, reading, deleting, existence-checking, and traversing cached logon records.

Important APIs and types: the header forward-declares `struct dom_sid` and `struct netr_SamInfo3` and includes `talloc.h` for ownership contracts. Exported functions are `netsamlogon_cache_init`, `netsamlogon_clear_cached_user`, `netsamlogon_cache_store`, `netsamlogon_cache_get`, `netsamlogon_cache_have`, and `netsamlog_cache_for_all`. The traversal callback receives a SID string, cache timestamp, decoded `netr_SamInfo3`, and caller private data.

Control flow and state: callers normally do not need to call init directly because implementation functions lazily initialize the TDB, but explicit initialization is available. Returned `netr_SamInfo3` values are talloc-owned by the caller-supplied context. Store accepts a mutable `info3` pointer because the implementation may fill missing account/full-name fields before serialization.

Dependencies and integration: this header sits at the boundary between libsmb cache code and consumers in auth/winbind-style code. It depends on SID and Netlogon generated RPC types without including their full definitions, reducing header coupling.

Risks: API consumers must understand that the cache is persistent and security-sensitive, and that stored entries are sanitized by implementation rather than by the header contract. The function name `netsamlog_cache_for_all` omits `on` unlike the other functions, so callers should avoid introducing parallel spellings.

Test signals: compile tests should catch prototype drift. Integration tests should include store/get/delete/traverse behavior through the header rather than only static implementation tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/samlogon_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/smbclient.pc.in -->
# sources/user-network-fs/samba/source3/libsmb/smbclient.pc.in

Purpose: `smbclient.pc.in` is the pkg-config template for the installed `libsmbclient` development package. Configure/waf substitution fills installation prefixes, version, rpath flags, and include/lib directories.

Important fields: it defines `prefix`, `exec_prefix`, `libdir`, and `includedir`; package metadata `Name: smbclient`, `Description: A SMB library interface`, `Version: @PACKAGE_VERSION@`, and `URL`; linker flags `Libs: @LIB_RPATH@ -L${libdir} -lsmbclient`; and compiler flags `Cflags: -I${includedir}`.

Control flow and integration: this file is consumed by Samba's build/install process, referenced by the `libsmb/wscript` `pc_files='smbclient.pc'` setting. Downstream projects use the generated `smbclient.pc` via `pkg-config --cflags --libs smbclient`.

State and persistence: no runtime state. The generated `.pc` file is an installed build artifact and encodes the installation layout.

Dependencies: depends on build-time substitution variables and the installed `libsmbclient` library/header set.

Risks: incorrect `libdir`, `includedir`, version, or rpath substitution breaks downstream builds. Overly broad `Libs` can leak private dependencies; here the template exposes only `-lsmbclient` plus configured rpath.

Test signals: packaging tests should run `pkg-config --exists smbclient`, check version output, compile a tiny program including `libsmbclient.h`, and verify link flags resolve `libsmbclient`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/smbclient.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/smberr.c -->
# sources/user-network-fs/samba/source3/libsmb/smberr.c

Purpose: `smberr.c` maps legacy SMB DOS error classes/codes to human-readable names and maps Unix errno values to Win32 `WERROR`. It is a support module for diagnostics and error translation in SMB client code.

Important APIs and data: static `err_code_struct` arrays define DOS (`ERRDOS`), server (`ERRSRV`), and hard (`ERRHRD`) error names/messages. `err_classes` maps class bytes such as `0x01`, `0x02`, `0x03`, and `0xFF` to class names and optional message tables. Exported functions are `smb_dos_err_name(uint8_t e_class, uint16_t num)`, `get_dos_error_msg(WERROR result)`, `smb_dos_err_class(uint8_t e_class)`, and `map_werror_from_unix(int error)`.

Control flow: `smb_dos_err_name` scans `err_classes`, then scans the matching table for the numeric error. If not found in a known class, it returns a talloc-stack string containing the numeric code; if the class is unknown, it returns a talloc-stack string naming the unknown class/code. `get_dos_error_msg` extracts the low WERROR value and resolves it under `ERRDOS`. `smb_dos_err_class` scans class mappings and formats unknown classes similarly. `map_werror_from_unix` delegates Unix-to-NTSTATUS mapping to `map_nt_error_from_unix` and then converts to WERROR via `ntstatus_to_werror`.

State and persistence: no persistent state. Fallback strings are allocated on `talloc_tos()`, so callers must not assume static lifetime for unknown-code returns.

Dependencies and integration: depends on Samba's legacy SMB error constants, NTSTATUS/WERROR mapping helpers, and talloc stack context. It integrates with client diagnostics and any code that still reports SMB1 DOS class/code errors.

Risks: the table is partial and legacy-oriented; consumers needing precise Windows error text should not treat these strings as exhaustive. Fallback allocations assert non-null, so out-of-memory can abort in those rare paths. Since messages in table entries are currently unused by exported functions, updating message text alone may not affect visible output.

Test signals: unit tests should verify known mappings across ERRDOS/ERRSRV/ERRHRD, unknown code formatting in known classes, unknown class formatting, `get_dos_error_msg` behavior for representative WERRORs, and Unix errno mapping parity with NTSTATUS conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/smberr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/smbsock_connect.c -->
# sources/user-network-fs/samba/source3/libsmb/smbsock_connect.c

Purpose: `smbsock_connect.c` implements asynchronous and synchronous SMB transport connection establishment for NetBIOS-over-TCP port 139, direct TCP port 445 or configured ports, and optionally SMB over QUIC. It returns an `smbXcli_transport` ready for higher-level SMB negotiation.

Important APIs and types: `smbsock_transports_from_port` converts a port into an `smb_transports` list or parses configured client transports when port is zero. `smbsock_connect_send/recv` and sync `smbsock_connect` connect one address across one or more transports. `smbsock_any_connect_send/recv` and sync `smbsock_any_connect` race multiple addresses and return the chosen index. The global `smbsock_connect_require_bsd_socket` disables ngtcp2 QUIC for callers such as libsmbclient that need BSD socket behavior. Internal states include `cli_session_request_state`, `nb_connect_state`, `smbsock_connect_substate`, `smbsock_connect_state`, and `smbsock_any_connect_state`.

Control flow: for NetBIOS, `nb_connect_send` opens a TCP socket, sends an RFC1002 session request built from mangled called/calling NetBIOS names, reads the session response, and retries once with `*SMBSERVER` type `0x20` if the server rejects the requested called name. For generic transport connection, `smbsock_connect_send` normalizes names, chooses BSD transport creation strategy from loadparm, prepares QUIC TLS parameters if any QUIC transport is requested and a target name exists, filters unsupported transports, submits the first subrequest, then after 5 ms submits remaining transport attempts. TCP and NBT callbacks create BSD-backed `smbXcli_transport` objects on success and leave cleanup to cancel/close losers. QUIC uses either kernel `IPPROTO_QUIC` plus TLS handshake or ngtcp2 over a connected UDP socket, depending on compile-time support and loadparm toggles.

State and persistence: connection state is per tevent request. Sockets are kept open only for the winning transport; cleanup frees pending subrequests and closes losing or failed sockets. `smbsock_any_connect` maintains an array of per-address requests, staggers address attempts every 10 ms, and frees outstanding requests when one succeeds. No disk persistence is involved.

Dependencies and integration: the file depends on tevent async request helpers, `open_socket_out_send`, `read_smb_send`, NetBIOS name utilities, loadparm configuration, socket option helpers, `smbXcli_transport` constructors, Samba TLS/QUIC helpers, and optional `HAVE_LIBQUIC`/`HAVE_LIBNGTCP2` support. It is exposed through `smbsock_connect.h` and used by higher-level client connection code such as `cliconnect.c`.

Risks: this is timing- and cleanup-sensitive code. Cleanup must free pending requests before closing sockets, as comments reference bug #11141. Racing transports means failure status can be whichever final request failed, so diagnostics may be coarse. QUIC peer verification state differs between non-QUIC (`TLS_VERIFY_PEER_NO_CHECK`) and QUIC TLS-derived transport. NetBIOS retry semantics intentionally collapse detailed RFC1002 negative session responses. The address-racing code increments `num_received` only for failed completed subrequests; pending cleanup must handle all remaining requests when a winner appears.

Test signals: tests should cover port-to-transport conversion, NBT positive session response, NBT negative response fallback to `*SMBSERVER`, direct TCP success/failure, multiple transport racing and cleanup of losers, all-transports-fail status, no-transports/disabled-NetBIOS errors, synchronous timeout behavior, multi-address chosen index, optional QUIC disabled/enabled/fallback paths under feature builds, and socket leak checks under cancellation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/smbsock_connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/smbsock_connect.h -->
# sources/user-network-fs/samba/source3/libsmb/smbsock_connect.h

Purpose: `smbsock_connect.h` declares the SMB transport connection API implemented by `smbsock_connect.c`. It separates socket/transport establishment from higher-level SMB session negotiation.

Important APIs and types: it forward-declares `struct smbXcli_transport` and declares `smbsock_transports_from_port`, the `smbsock_connect_require_bsd_socket` policy flag, one-address async/sync connection functions, and multi-address async/sync connection functions. The async APIs return `struct tevent_req *`; recv APIs move an `smbXcli_transport` into caller memory. `smbsock_any_connect_recv` can also return the selected address index.

Control flow and state: callers pass a `tevent_context`, `loadparm_context`, sockaddr(s), transport list, optional called/calling NetBIOS names and types, and talloc output context. The implementation owns transient sockets and returns one transport on success. The `NONNULL` annotations document required inputs.

Dependencies and integration: the header depends on Samba transport types, NTSTATUS, tevent, talloc, loadparm, and socket address structures through included/consumer context. It is used by client connection code that wants configured SMB transports, including TCP/NBT/QUIC when available.

Risks: the global `smbsock_connect_require_bsd_socket` changes behavior process-wide, so users must set it deliberately. Passing a transport list inconsistent with the address/target name can yield `NT_STATUS_PORT_NOT_SET` or skip QUIC.

Test signals: compile tests should validate async and sync prototypes. Integration tests should connect by single address and address list, verify chosen index, and exercise the global BSD socket policy in code paths that require it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/smbsock_connect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/unexpected.c -->
# sources/user-network-fs/samba/source3/libsmb/unexpected.c

Purpose: `unexpected.c` implements a Unix-domain socket broker for NetBIOS packets that `nmbd` receives but that client code is waiting for asynchronously. Clients register interest in an NMB transaction id or datagram mailslot name, receive an acknowledgment, and then receive matching packets serialized over the local socket.

Important APIs and types: exported APIs are `nb_packet_server_create`, `nb_packet_dispatch`, `nb_packet_reader_send/recv`, and `nb_packet_read_send/recv`. `struct nb_packet_server` owns the listening socket, tevent fd, max client count, and client list. `struct nb_packet_client` stores query filters, tstream socket, and output queue. `struct nb_packet_reader` is the client-side read handle. Wire-local structs include `nb_packet_query`, `nb_packet_client_header`, `nb_packet_client_state`, and `nb_packet_read_state`.

Control flow: server creation calls `create_pipe_sock(nmbd_socket_dir, "unexpected", 0755)`, listens, and registers a tevent read fd. On accept, the listener wraps the socket in a tstream, creates an output queue, reads a `nb_packet_query` plus optional mailslot name, acknowledges with one zero byte, and starts a one-byte read to detect client disconnect/protocol misuse. Client count is capped by `max_clients`; when exceeded, the oldest client is dropped. `nb_packet_dispatch` extracts transaction id from NMB or datagram packet headers, filters clients by packet type plus transaction id or mailslot, and queues matching packets. Queued sends prepend metadata (`len`, type, timestamp, IP, port) and serialized packet bytes from `build_packet`. Reader setup connects to the Unix socket, sends the query, waits for the one-byte ack, then `nb_packet_read_send` reads header plus body and `nb_packet_read_recv` parses it with `parse_packet_talloc`.

State and persistence: all state is in memory and tied to talloc lifetimes. The server persists only as a listening Unix-domain socket path while alive. Client output queues are throttled: if queue length exceeds 10, additional packets are skipped as a denial-of-service guard. Packet payload buffers are capped by `build_packet`'s fixed 1024-byte local buffer on send.

Dependencies and integration: the file depends on tevent, tstream/tsocket Unix sockets, Samba NetBIOS packet structures and `build_packet`/`parse_packet_talloc`, `match_mailslot_name`, Unix close-on-exec helpers, DLIST macros, and NTSTATUS/errno mapping. It integrates with `nmbd` and name service client code via `unexpected.h`.

Risks: the local protocol uses native C struct layouts (`size_t`, enum, `time_t`, `struct in_addr`) over a Unix socket, so it is only safe intra-build/intra-host and not a stable external protocol. `nb_packet_client_more` rejects mailslot names over 1024 bytes, but packet send serialization also uses a fixed 1024-byte packet buffer. Slow clients can drop packets once their queue exceeds 10. `nb_packet_read_recv` copies a header into `hdr` but then uses `state->hdr` for parse fields; this is functionally equivalent after earlier copy but should be kept clear if refactored.

Test signals: tests should create a temporary socket dir, register readers for NMB transaction ids and datagram mailslots, dispatch matching and nonmatching packets, verify ack behavior, read/parse round-trip metadata and payload, enforce max-client dropping, simulate disconnect/protocol error cleanup, verify oversized mailslot rejection, and check queue-throttling behavior for slow readers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/unexpected.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/unexpected.h -->
# sources/user-network-fs/samba/source3/libsmb/unexpected.h

Purpose: `unexpected.h` declares the NetBIOS unexpected-packet broker API from `unexpected.c`. It provides opaque server and reader types plus async request functions for creating a local packet subscription channel and reading matching packets.

Important APIs and types: `struct nb_packet_server` and `struct nb_packet_reader` are opaque. `nb_packet_server_create` creates the local broker under an `nmbd_socket_dir`. `nb_packet_dispatch` pushes an incoming `packet_struct` to interested clients. `nb_packet_reader_send/recv` connects a reader and registers filters by packet type, transaction id, and optional mailslot name. `nb_packet_read_send/recv` reads one matched packet.

Control flow and state: callers create a server in a tevent context, dispatch NetBIOS packets as they arrive, and client-side code opens readers that produce tevent requests for matching packet delivery. The header keeps lifetime ownership explicit through talloc contexts and NTSTATUS recv functions.

Dependencies and integration: it includes `replace.h`, tevent, NTSTATUS definitions, and `nameserv.h` for `enum packet_type` and `struct packet_struct`. It is consumed by nmb/name-service code rather than external applications.

Risks: the API is asynchronous and lifetime-sensitive; freeing the server or reader invalidates pending local socket activity. Filtering semantics differ by packet type: NMB uses transaction id, datagrams use mailslot matching.

Test signals: compile tests should cover all declarations. Functional tests should create server/readers, dispatch both NMB and datagram packets, and verify no delivery for mismatched filters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/unexpected.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/wscript -->
# sources/user-network-fs/samba/source3/libsmb/wscript

Purpose: this waf build script defines the Samba3 `smbclient` shared library target for `libsmbclient`.

Important build API: `build(bld)` calls `bld.SAMBA3_LIBRARY('smbclient', ...)` with source files `libsmb_cache.c`, compatibility/context/dir/file/misc/path/printjob/server/stat/xattr/setget modules, public dependencies, public header `../include/libsmbclient.h`, ABI directory `ABI`, ABI symbol match `smbc_*`, version `0.8.1`, and pkg-config file `smbclient.pc`.

Control flow and integration: waf imports and executes `build` during Samba configuration/build. The target aggregates the public libsmbclient API rather than the internal Python binding or socket helper files in this subset. Public dependencies include `pthread`, `talloc`, `smbconf`, `libsmb`, `KRBCLIENT`, `msrpc3`, and `libcli_lsa3`.

State and persistence: no runtime state. The script produces build artifacts, installed public headers, ABI checks, and pkg-config output.

Risks: changing the source list can omit part of libsmbclient or accidentally expose private code. ABI metadata matters because public `smbc_*` symbols are versioned. Dependency changes affect downstream link behavior.

Test signals: waf configure/build should generate `libsmbclient`, run ABI checks against `ABI`, install `libsmbclient.h`, generate `smbclient.pc`, and link a downstream sample via pkg-config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/wscript -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locale/net/genmsg -->
# sources/user-network-fs/samba/source3/locale/net/genmsg

Purpose: `locale/net/genmsg` is a shell helper for regenerating gettext `.po` files for Samba's `net` command translations.

Important logic: `add_basedir_to_filelist` prefixes each listed source file with `../../utils`. `FILES` enumerates many `net*.c` sources. `LANGS` lists supported locale directories. The script runs `xgettext` with domain `net`, comment extraction, `_` and `N_` keywords, and width 256, then iterates languages, preserving existing translations through `msgmerge` from each old language file into the new `net.po` template.

Control flow and state: the script creates or touches each `${lang}.po`, renames it to `${lang}.po.old`, merges, writes the new `${lang}.po`, removes the old temporary, and deletes the generated `net.po` template. It mutates translation files in the current directory.

Dependencies and integration: requires POSIX shell, `xgettext`, `msgmerge`, the locale directory layout, and the listed source files under `source3/utils`. It integrates with gettext translation maintenance, while `locale/wscript` handles build-time compilation/install when gettext is enabled.

Risks: running from the wrong directory will update or create files in the wrong place. The unquoted file iteration assumes no spaces in paths/language names. Missing source files or gettext tools will fail midway and may leave `.po.old` files. The source list can become stale as `net` command files are added or removed.

Test signals: run from `source3/locale/net` with gettext tools installed, verify `net.po` is removed at the end, all language `.po` files remain parseable with `msgfmt -c`, and new translatable strings from listed `net*.c` files appear in merged catalogs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locale/net/genmsg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locale/pam_winbind/genmsg -->
# sources/user-network-fs/samba/source3/locale/pam_winbind/genmsg

Purpose: `locale/pam_winbind/genmsg` regenerates gettext `.po` catalogs for the `pam_winbind` component.

Important logic: `FILES` points at `../../../nsswitch/pam_winbind.c`, `../../../nsswitch/pam_winbind.h`, and `../../../libcli/util/nterr.c`. `LANGS` lists the maintained translation languages. The script ensures `pam_winbind.po` exists, runs `xgettext` with domain `pam_winbind`, `_` and `N_` keywords, and width 256, then loops over languages and uses `msgmerge` to merge the generated template into each existing language file.

Control flow and state: each language file is touched, moved to `${lang}.po.old`, merged back to `${lang}.po`, and the old file is removed. The generated `pam_winbind.po` template is removed at completion. It mutates files in the current locale directory.

Dependencies and integration: requires shell, gettext tools, source files in `nsswitch` and `libcli/util`, and locale build support. `locale/wscript` later compiles/install these catalogs when gettext is enabled.

Risks: like the `net` script, it assumes it is run from the correct directory and that paths have no spaces. Failure during `msgmerge` can leave temporary files or incomplete catalogs. Including `nterr.c` means NT error string changes affect pam_winbind translations; stale source lists can miss messages.

Test signals: run the script in `source3/locale/pam_winbind`, verify all listed language catalogs exist, validate with `msgfmt -c`, confirm `pam_winbind.po` cleanup, and inspect that changed PAM/NT-error strings are represented.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locale/pam_winbind/genmsg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locale/wscript -->
# sources/user-network-fs/samba/source3/locale/wscript

Purpose: `source3/locale/wscript` wires Samba locale catalogs into the waf build.

Important API: `build(bld)` imports `Options` and checks both `not Options.options.disable_gettext` and presence of `MSGFMT` in `bld.env`. If enabled, it registers two `intltool_po` build features: appname `net` with `podir='net'`, and appname `pam_winbind` with `podir='pam_winbind'`, both installed under `${LOCALEDIR}`.

Control flow and state: build registration is conditional. If gettext is disabled or `msgfmt` was not found, no locale build tasks are registered. No runtime state is created by this script itself; generated/installed `.mo` files are build artifacts.

Dependencies and integration: depends on waflib `Options`, waf gettext/intltool support, `MSGFMT` detection, locale directories, and Samba's `LOCALEDIR` install variable. It integrates with the `genmsg` scripts that refresh source `.po` files.

Risks: missing `MSGFMT` silently prevents catalog builds under this condition, which may surprise package builders expecting translations. Adding a new catalog requires updating this script. Incorrect `appname` or `podir` breaks install paths or domain names.

Test signals: configure/build with gettext enabled and `msgfmt` present should register and install `net` and `pam_winbind` catalogs. Builds with `--disable-gettext` or no `MSGFMT` should skip them cleanly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locale/wscript -->
