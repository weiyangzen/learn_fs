# Research: subset-b-009953

Grouped research for Samba source4 SMB server SMB2 handling, common SMB server connection/tcon support, and related auth/basic torture tests. Each section is source-tree aligned and wrapped for reconciliation into the required per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/fileio.c -->
# sources/user-network-fs/samba/source4/smb_server/smb2/fileio.c

## Purpose
This file implements the SMB2 file-oriented command adapters for the source4 SMB server. It parses SMB2 CREATE, CLOSE, FLUSH, READ, WRITE, LOCK, IOCTL, NOTIFY, and BREAK request bodies into Samba raw/NTVFS request unions, validates handles and dynamic buffers, calls the NTVFS backend, and serializes SMB2 replies.

## Important APIs, Types, And Functions
The public entry points are `smb2srv_create_recv`, `smb2srv_close_recv`, `smb2srv_flush_recv`, `smb2srv_read_recv`, `smb2srv_write_recv`, `smb2srv_lock_recv`, `smb2srv_ioctl_recv`, `smb2srv_notify_recv`, and `smb2srv_break_recv`. Each has a matching static send callback, such as `smb2srv_create_send` or `smb2srv_read_send`, reached through `SMB2SRV_SETUP_NTVFS_REQUEST`. The code relies on `union smb_open`, `union smb_close`, `union smb_read`, `union smb_write`, `union smb_lock`, `union smb_ioctl`, and `union smb_notify`, plus SMB2 blob helpers and NTVFS operations.

## Control Flow
Receive functions first enforce the SMB2 fixed structure size with `SMB2SRV_CHECK_BODY_SIZE`, allocate an IO union under the request, decode little-endian fields and offset/length dynamic areas, resolve file handles with `smb2srv_pull_handle`, and dispatch via `SMB2SRV_CALL_NTVFS_BACKEND`. Send callbacks check async completion, build replies with `smb2srv_setup_reply`, write fixed fields, append dynamic data where needed, and call `smb2srv_send_reply`. CREATE additionally parses create-context blobs for EAs, security descriptors, durable-handle fields, allocation size, maximal access, timewarp, and query-on-disk-id, and emits MXAC/QFID reply blobs.

## State And Persistence
The file does not persist data itself. It mutates per-request state, especially `req->io_ptr`, `req->ntvfs`, chained file-handle storage, and sometimes `req->tcon` through handle resolution. Persistent effects are delegated to NTVFS backends: file creation, writes, locks, flushes, notification registrations, ioctl work, and oplock break acknowledgement.

## Dependencies And Integration Points
It depends on `libcli/smb2` framing helpers, raw SMB unions, NDR security descriptor decoding, EA parsing, `ntvfs_*` calls, and the common SMB2 request macros in `smb2_server.h`. It is invoked from `receive.c` dispatch after session and tree-connect validation. Handle format and chained-handle behavior integrate with `smb2/tcon.c`.

## Risks And Test Signals
Important risks are exact SMB2 structure-size compliance, offset/length validation in dynamic blobs, memory pressure when preallocating read buffers, CREATE context length checks, NULL-name fallback behavior, lock-count overflow, wildcard or stale handle handling, and TODO-marked extra copies. Test signals include SMB2 create contexts, reads with one-byte dynamic tail, writes with dynamic payloads, multi-lock requests, no-handle IOCTLs, notifications with Unicode names and alignment, oplock breaks, chained requests reusing a CREATE handle, and malformed length/handle cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/fileio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/find.c -->
# sources/user-network-fs/samba/source4/smb_server/smb2/find.c

## Purpose
This file implements SMB2 QUERY_DIRECTORY handling. It translates SMB2 find levels and request fields into the legacy raw search-first/search-next NTVFS interfaces, accumulates directory entries into a passthrough SMB2 blob, and serializes the find reply.

## Important APIs, Types, And Functions
The public entry point is `smb2srv_find_recv`. Internal support centers on `struct smb2srv_find_state`, `smb2srv_find_backend`, `smb2srv_find_callback`, and `smb2srv_find_send`. The state object tracks the original request, current `struct smb2_find`, optional `union smb_search_first` or `union smb_search_next`, and the last entry offset that must have its next-entry link cleared before the reply is sent.

## Control Flow
`smb2srv_find_recv` validates a dynamic 0x20 request, allocates both a `struct smb2_find` and a wrapper state, decodes find level, flags, file index, directory handle, pattern, and max response size, normalizes NULL patterns to the empty string, validates the handle, and dispatches. `smb2srv_find_backend` maps SMB2 find information classes to raw search data levels, then chooses `ntvfs_search_first` when `SMB2_CONTINUE_FLAG_REOPEN` is present, otherwise `ntvfs_search_next`. The callback appends entries using `smbsrv_push_passthru_search`; if the blob would exceed the max response, it rolls back and stops enumeration.

## State And Persistence
State is per request only. Directory enumeration cursor semantics are owned by the NTVFS backend and the handle. The reply blob is grown under the request state and trimmed by resetting the final next-entry offset to zero. No durable storage is directly changed.

## Dependencies And Integration Points
The file depends on SMB2 helpers, raw search unions, `smbsrv_push_passthru_search`, and NTVFS search calls. It is dispatched by `receive.c` for `SMB2_OP_QUERY_DIRECTORY` after session, tcon, and handle validation support from other modules.

## Risks And Test Signals
Risks include incomplete information-class mapping, returning `NT_STATUS_FOOBAR` for unknown levels, off-by-one response sizing, last-entry offset corruption, and empty pattern behavior. Useful tests cover every SMB2 find class, small `max_response_size`, reopen vs next modes, wildcard and empty patterns, invalid handles, and backend callbacks that stop mid-enumeration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/find.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/keepalive.c -->
# sources/user-network-fs/samba/source4/smb_server/smb2/keepalive.c

## Purpose
This file implements SMB2 KEEPALIVE/ECHO-style request handling. It validates the minimal fixed body, currently performs no connection-side bookkeeping, and returns a four-byte SMB2 response unless the caller requested no reply.

## Important APIs, Types, And Functions
The public entry point is `smb2srv_keepalive_recv`. `smb2srv_keepalive_backend` returns `NT_STATUS_OK` and is explicitly marked for future connection-flag updates. `smb2srv_keepalive_send` serializes the response or converts backend errors into SMB2 error replies.

## Control Flow
The receive path requires `req->in.body_size == 0x04` and the first body word equal to `0x04`. Invalid values produce `NT_STATUS_INVALID_PARAMETER`. On success, it records the backend status in `req->status`; if `SMB2SRV_REQ_CTRL_FLAG_NOT_REPLY` is set, it frees the request, otherwise it emits a fixed-size response with a zero reserved word.

## State And Persistence
The only state mutation is `req->status`. Unlike the dispatcher, this file does not update last-request timestamps, idle timers, or negotiated connection state. There is no persistence.

## Dependencies And Integration Points
It depends on SMB2 reply setup and error helpers from the SMB2 server layer. `receive.c` dispatches `SMB2_OP_KEEPALIVE` here without requiring a valid session or tcon.

## Risks And Test Signals
Risks are small but protocol-sensitive: accepting wrong body sizes would mask malformed clients, while not updating connection liveness may matter if future idle tracking expects this command. Tests should send valid keepalive packets, wrong fixed-size values, truncated bodies, no-reply internal requests, and keepalives before session setup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/keepalive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/negprot.c -->
# sources/user-network-fs/samba/source4/smb_server/smb2/negprot.c

## Purpose
This file handles SMB2 negotiation and the SMB1-to-SMB2 negotiation bridge for dialect `SMB 2.002`. It selects the SMB2 dialect, computes signing mode and transfer limits, initializes the first SPNEGO security blob, and serializes the negotiate response.

## Important APIs, Types, And Functions
The public entry points are `smb2srv_negprot_recv` and `smb2srv_reply_smb_negprot`. Internal functions include `smb2srv_negprot_secblob`, `smb2srv_negprot_backend`, and `smb2srv_negprot_send`. The implementation uses `struct smb2_negprot`, GENSEC/SPNEGO APIs, server credentials, loadparm signing settings, GUID and NTTIME helpers, and `req->smb_conn->negotiate`.

## Control Flow
`smb2srv_negprot_recv` validates the body, decodes dialect count, client GUID, start time, and dialect list, then calls the backend and sends the reply unless suppressed. The backend only accepts `SMB2_DIALECT_REVISION_202`, sets `PROTOCOL_SMB2_02`, derives signing requirements from `server signing` and server role, sets max transact/read/write sizes from smb2 parameters, and obtains a SPNEGO blob. `smb2srv_negprot_secblob` initializes server credentials, starts a server GENSEC context for `cifs`, selects SPNEGO, and asks for the initial token. `smb2srv_reply_smb_negprot` fabricates an SMB2 negprot request from an SMB1 dialect negotiation path.

## State And Persistence
Negotiation persists on the connection: selected protocol, server credentials, max sizes, zone/time-related values initialized elsewhere, and `smb2_signing_required` when signing is mandatory. No disk state is changed.

## Dependencies And Integration Points
This module integrates authentication (`gensec`, credentials), loadparm policy, SMB1 negotiation fallback, and SMB2 request framing. It is reached from `receive.c` for native SMB2 and from the SMB1 negotiate code through `smb2srv_reply_smb_negprot`.

## Risks And Test Signals
Risks include support for only SMB2.002, no real boot-time value, fallback anonymous credentials for standalone/spoolss tests, hard connection termination on GENSEC startup failures, and signing policy regressions for AD DC roles. Tests should cover no dialects, unsupported dialects, SMB2.002, SMB1 negotiate upgrade, signing off/desired/required/default on DC and non-DC roles, max-size loadparm overrides, and SPNEGO token creation failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/negprot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/receive.c -->
# sources/user-network-fs/samba/source4/smb_server/smb2/receive.c

## Purpose
This file is the SMB2 receive, dispatch, reply, chaining, async-pending, cancel, and connection-initialization core. It turns incoming NBT-framed SMB2 packets into `smb2srv_request` objects, validates framing, routes opcodes to command handlers, signs replies when required, and tracks asynchronous requests for cancellation.

## Important APIs, Types, And Functions
Key public functions are `smb2srv_setup_bufinfo`, `smb2srv_init_request`, `smb2srv_setup_reply`, `smb2srv_send_reply`, `smb2srv_send_error`, `smbsrv_recv_smb2_request`, `smb2srv_queue_pending`, `smb2srv_cancel_recv`, and `smbsrv_init_smb2_connection`. Important internal pieces are request destructors, `smb2srv_chain_reply`, `smb2srv_reply`, and `smb2srv_init_pending`.

## Control Flow
`smbsrv_recv_smb2_request` validates the NBT byte, minimum length, SMB2 magic, body size, dynamic area, and first-request related flag, then calls `smb2srv_reply`. The dispatcher checks header length, monotonic message IDs, related-request session/tcon inheritance, session/tcon lookup, signing verification/enforcement, prior chain failure state, and opcode requirements before calling command-specific receive functions. Replies are built by `smb2srv_setup_reply`, queued by `packet_send`, optionally signed, and followed by chained-request dispatch if `NextCommand` is set. Async backends call `smb2srv_queue_pending`, which allocates an async id, emits `NT_STATUS_PENDING`, and keeps the request protected until final completion. CANCEL looks up async ids and calls `ntvfs_cancel`.

## State And Persistence
The file owns transient request lifetime and mutates connection state: highest SMB2 sequence number, pending request id tree/list, request timestamps, and SMB2 connection defaults. Persistent file/session/share effects are elsewhere. Request destructors remove pending ids and linked-list entries.

## Dependencies And Integration Points
It depends on packet transport, idtree, signing helpers, session and tcon lookup, NTVFS cancellation, command handlers from sibling SMB2 files, and common server structures from `smb_server.h`. `smb_server.c` installs `smbsrv_recv_smb2_request` as the packet callback after protocol detection.

## Risks And Test Signals
Risks include strict sequence-number handling under replay or compounding, dynamic-size underflow, related-request propagation bugs, signing state mismatches, async destructor denial while pending, and always using `NT_STATUS_INVALID_PARAMETER` as chain failure after error replies. Tests should include malformed NBT/SMB2 headers, chained compounds with and without related flags, signed and unsigned session traffic, async pending plus cancel, out-of-order message ids, invalid session/tcon ids, and socket teardown during send.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/receive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/sesssetup.c -->
# sources/user-network-fs/samba/source4/smb_server/smb2/sesssetup.c

## Purpose
This file implements SMB2 SESSION_SETUP and LOGOFF. It drives SPNEGO/GENSEC authentication, allocates and finalizes SMB2 sessions, activates signing when required, serializes security blobs, and schedules session destruction after logoff replies.

## Important APIs, Types, And Functions
Public entry points are `smb2srv_sesssetup_recv` and `smb2srv_logoff_recv`. Internal flow uses `smb2srv_sesssetup_backend`, `smb2srv_sesssetup_callback`, `smb2srv_sesssetup_send`, `smb2srv_logoff_backend`, `smb2srv_logoff_send`, and `smb2srv_cleanup_session_destructor`. The callback context carries the request, IO union, and target `smbsrv_session`.

## Control Flow
`smb2srv_sesssetup_recv` validates and decodes the SMB2 session setup body and security blob. The backend either starts a new GENSEC SPNEGO server context when the session id is zero, or resumes an in-progress setup session. New sessions get SMB2 tcon storage initialized. It rejects already-authenticated sessions and missing GENSEC state, sends `gensec_update_send`, disables packet receive while authentication is in flight, and stores signing requirements from client security mode. The async callback re-enables packet receive, receives the output token, obtains session info on success, finalizes the session, enables signing for authenticated users when required, and sends success or `MORE_PROCESSING_REQUIRED`. LOGOFF validates its tiny body and attaches a destructor that frees the session after the reply is sent.

## State And Persistence
Authentication state persists in `smbsrv_session`: `gensec_ctx`, `session_info`, vuid, tcon context, signing required/active flags, and timestamps managed by session helpers. LOGOFF frees the session and by extension session-owned tcons/handles. No disk state is directly changed.

## Dependencies And Integration Points
The file depends on GENSEC, auth session info, packet receive flow control, socket address capture, session allocation helpers, and SMB2 reply helpers. It is dispatched by `receive.c`; signing results are later consumed by `receive.c` and `smb2srv_send_reply`.

## Risks And Test Signals
Risks include receive being disabled during long authentication, subtle handling of partially established sessions, cleanup TODOs for open files on logoff, ignoring client `SIGNING_ENABLED`, and squashing auth statuses. Tests should cover multi-leg SPNEGO, wrong/resumed session ids, already-authenticated session setup, required signing activation, failed GENSEC update cleanup, logoff with open tcons, and no-reply internal paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/sesssetup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/smb2_server.h -->
# sources/user-network-fs/samba/source4/smb_server/smb2/smb2_server.h

## Purpose
This header defines the SMB2 request context and the core macros used by source4 SMB2 command handlers. It centralizes request lifetime fields, chaining state, signing flags, inbound/outbound buffers, NTVFS request setup, body validation, error propagation, and async completion checks.

## Important APIs, Types, And Functions
The primary type is `struct smb2srv_request`, which links into connection pending lists and stores `smb_conn`, `tcon`, `session`, control flags, request time, IO pointer, NTVFS request, status, sequence number, pending id, chain metadata, chained file/session/tree data, signing state, and SMB2 input/output buffers. It includes generated `smb2_proto.h`. Macros include `SMB2SRV_CHECK_BODY_SIZE`, `SMB2SRV_CHECK`, `SMB2SRV_TALLOC_IO_PTR`, `SMB2SRV_SETUP_NTVFS_REQUEST`, `SMB2SRV_CHECK_FILE_HANDLE`, `SMB2SRV_CALL_NTVFS_BACKEND`, and async status variants.

## Control Flow
Command handlers use the macros as structured control flow: validate body and fixed-size tag, allocate request-local IO, build an NTVFS request attached to the tcon backend and session info, dispatch either synchronously or asynchronously, and convert errors into SMB2 error replies. Async send callbacks use the check macros to retrieve `req` and the typed IO object, terminate connections on close/write-fault states, and either propagate errors or continue serialization.

## State And Persistence
The header defines only in-memory state. The request object is central to per-packet state, chained request propagation, pending async identity, and reply signing. Persistence is delegated to session/tcon/NTVFS structures referenced from it.

## Dependencies And Integration Points
It depends on `smb_server.h`, generated prototypes, NTVFS async semantics, talloc, NTSTATUS helpers, and SMB2 buffer structs. Nearly every file in `source4/smb_server/smb2` depends on these definitions.

## Risks And Test Signals
Risks include macros that early-return and obscure cleanup, assumptions that `req->tcon` and `req->session` are valid before NTVFS setup, exact fixed-size tag arithmetic for dynamic bodies, and divergent behavior between `_ERR` and strict OK async checks. Tests should exercise every command’s malformed body path, async success/error/close paths, no-memory simulation, invalid handle translation, and compounded requests that carry chained session/tree/file state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/smb2_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/tcon.c -->
# sources/user-network-fs/samba/source4/smb_server/smb2/tcon.c

## Purpose
This file implements SMB2 tree connect/disconnect, SMB2 wire-handle translation, NTVFS handle callbacks, and unsolicited oplock-break sending. It bridges SMB2 sessions and tree ids to Samba share configuration and NTVFS connections.

## Important APIs, Types, And Functions
Public functions are `smb2srv_pull_handle`, `smb2srv_push_handle`, `smb2srv_tcon_recv`, and `smb2srv_tdis_recv`. Key internal functions include `smb2srv_send_oplock_break`, handle callbacks `smb2srv_handle_create_new`, `smb2srv_handle_make_valid`, `smb2srv_handle_destroy`, wire-key stubs, `smb2srv_tcon_backend`, `smb2srv_tcon_send`, `smb2srv_tdis_backend`, and `smb2srv_tdis_send`.

## Control Flow
Tree connect decodes the UNC path, strips leading server components, looks up share config, applies hosts allow/deny, maps share type to NTVFS disk/print/IPC, allocates an SMB2 tcon under the session, initializes an NTVFS connection, registers oplock/address/handle callbacks, creates an NTVFS request, calls `ntvfs_connect`, and replies with share type, flags, capabilities, access mask, and TID. Handle push encodes HID/TID/VUID into SMB2’s 128-bit handle. Pull validates VUID, finds the referenced tcon by embedded TID, finds the handle, updates `req->tcon`, and returns the NTVFS handle. Tree disconnect frees the tcon after a success status.

## State And Persistence
This file creates and destroys session-owned tcons and handle front-end objects. It updates `req->tcon`, sets `handle->ntvfs` once backends make a handle valid, moves valid handles under the tcon memory context, and frees handle wrappers on destroy. Share/file persistence is through NTVFS.

## Dependencies And Integration Points
It depends on share configuration, socket access checks, NTVFS connection and callbacks, common tcon/handle allocation in `smb_server/tcon.c` and handle modules, packet send from `receive.c`, and SMB2 file operations that call `smb2srv_pull_handle`.

## Risks And Test Signals
Risks include incomplete durable handle wire-key callbacks, wildcard handle returning NULL, related/chained handle TODO semantics, share path parsing edge cases, tcon lifetime with open handles, and forcing broad `SEC_RIGHTS_FILE_ALL` access in replies. Tests should cover UNC path forms, hosts allow/deny, disk/IPC/printer shares, handle use through a different header TID, invalid VUID/TID/HID, oplock break emission, tree disconnect with open handles, and chained create/read/write.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/tcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/wscript_build -->
# sources/user-network-fs/samba/source4/smb_server/smb2/wscript_build

## Purpose
This Waf build fragment defines the source4 SMB2 protocol subsystem build target. It collects SMB2 server implementation files into `SMB2_PROTOCOL`, declares generated prototypes, dependencies, and the feature gate for the NTVFS file server.

## Important APIs, Types, And Functions
The file calls `bld.SAMBA_SUBSYSTEM('SMB2_PROTOCOL', ...)` with source files `receive.c negprot.c sesssetup.c tcon.c fileio.c fileinfo.c find.c keepalive.c`, `autoproto='smb2_proto.h'`, and public dependencies `ntvfs LIBPACKET LIBCLI_SMB2 samba_server_gensec NDR_DFSBLOBS`.

## Control Flow
At configure/build time, Waf evaluates this fragment when recursing into `smb2`. The subsystem is enabled only when `bld.CONFIG_SET('WITH_NTVFS_FILESERVER')` is true. Autoproto generation produces declarations consumed by `smb2_server.h`.

## State And Persistence
It changes build graph state, not runtime state. Generated prototype headers and compiled objects are build artifacts outside source logic.

## Dependencies And Integration Points
The target is pulled in by `source4/smb_server/wscript_build`, and the parent `SMB_SERVER` subsystem publicly depends on `SMB2_PROTOCOL`. Dependency declarations expose NTVFS, packet transport, SMB2 client/common helpers, GENSEC server support, and DFS blob NDR support to these sources.

## Risks And Test Signals
Risks include source-list drift when adding SMB2 commands, missing public dependencies masked by include order, and the subsystem disappearing when `WITH_NTVFS_FILESERVER` is false. Build tests should verify autoproto generation, a full `WITH_NTVFS_FILESERVER` build, and disabled-feature builds that omit SMB2 server objects cleanly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb_server.c -->
# sources/user-network-fs/samba/source4/smb_server/smb_server.c

## Purpose
This file is the connection-level entry point for the source4 SMB service. It accepts stream sockets, configures packet framing, detects SMB1 vs SMB2 on the first request, installs the protocol-specific receive callback, manages socket send/receive events, and creates listening sockets for configured SMB transports.

## Important APIs, Types, And Functions
The exported function is `smbsrv_add_socket`. Internal functions include `smbsrv_recv_generic_request`, `smbsrv_terminate_connection`, event handlers `smbsrv_recv` and `smbsrv_send`, `smbsrv_recv_error`, and `smbsrv_accept`. It uses `stream_server_ops smb_stream_ops` to bind accept/recv/send behavior.

## Control Flow
On accept, the code allocates `smbsrv_connection`, initializes a packet context with NBT full-request detection and serialized output, stores loadparm and stream connection pointers, initializes management, registers the `smb_server` IRPC name, and obtains the share context. The first packet is inspected: nonzero NBT marker or SMB magic selects SMB1, SMB2 magic selects SMB2 if the configured max protocol permits it, and invalid packets terminate the stream. `smbsrv_add_socket` parses configured SMB transports, ignores unsupported QUIC/unknown entries, and calls `stream_setup_socket` for NBT/TCP ports.

## State And Persistence
The file initializes per-connection state: packet context, share context, connection statistics, loadparm reference, and protocol-specific callbacks. It does not persist disk data.

## Dependencies And Integration Points
It integrates service_stream, service_task, packet transport, SMB1 and SMB2 initialization paths, loadparm transport configuration, share configuration, messaging/IRPC, and network socket setup. Downstream protocol handlers live in `smb/` and `smb2/`.

## Risks And Test Signals
Risks include first-packet protocol confusion, max-protocol gating for SMB2, transport parsing that silently ignores unsupported entries, share context initialization failure terminating accepted sockets, and packet serialization limiting concurrency on a connection. Tests should cover SMB1 first packets, SMB2 first packets, invalid magic, special NBT session packets, disabled SMB2 max protocol, multiple configured transports, and share-init failure handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb_server.h -->
# sources/user-network-fs/samba/source4/smb_server/smb_server.h

## Purpose
This header defines the shared source4 SMB server object model for connections, sessions, tree connects, handles, SMB1 requests, and common request/NTVFS macros. It is the central structure contract consumed by both SMB1 and SMB2 server code.

## Important APIs, Types, And Functions
Important types include `smbsrv_tcons_context`, `smbsrv_sessions_context`, `smbsrv_handles_context`, `smbsrv_session`, `smbsrv_tcon`, `smbsrv_handle`, `smbsrv_request`, and `smbsrv_connection`. It declares `smbsrv_add_socket` and includes generated prototypes. Macros include `SMBSRV_CHECK_WCT`, `SMBSRV_TALLOC_IO_PTR`, `SMBSRV_SETUP_NTVFS_REQUEST`, file-handle checks, `SMBSRV_CHECK`, `SMBSRV_CALL_NTVFS_BACKEND`, async status checks, and `SMBSRV_VWV_RESERVED`.

## Control Flow
The header itself has no runtime flow, but its macros define much of the SMB1 adapter flow: allocate typed IO, create an NTVFS request with session info and PID, attach frontend private data, dispatch synchronously or queue for async completion, and convert errors into SMB replies. Its structures determine how protocol handlers find sessions, tcons, handles, pending requests, signing context, packet state, share context, and negotiated parameters.

## State And Persistence
The defined structures hold all per-connection state: negotiated protocol/options, sessions, SMB1 tcons, SMB2 session-owned tcons, pending SMB1/SMB2 requests, signing contexts, partial transaction requests, statistics, share/loadparm pointers, SMB2 signing requirement, and highest SMB2 sequence number. Persistence beyond process memory is delegated to NTVFS/share/auth layers.

## Dependencies And Integration Points
The header depends on raw request/interface definitions, sockets, roles, dlink lists, NBT NDR, NTVFS forward declarations, and generated SMB server prototypes. It is included by SMB1, SMB2, session, tcon, handle, management, and service code.

## Risks And Test Signals
Risks include tight coupling through mutable structs, macro early returns, SMB1/SMB2 semantic differences in shared fields, id-tree limits, handle lifetime across session/tcon cleanup, and signing state consistency. Tests should stress connection teardown, multiple sessions, multiple tcons, handle enumeration/removal, SMB1 async operations, SMB2 pending request cleanup, and management/statistics visibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/tcon.c -->
# sources/user-network-fs/samba/source4/smb_server/tcon.c

## Purpose
This file manages common `smbsrv_tcon` allocation, lookup, initialization, and destruction for both SMB1 and SMB2. It owns TID id-tree setup and ensures NTVFS disconnect is called when a tree connection is freed.

## Important APIs, Types, And Functions
Public functions are `smbsrv_smb_init_tcons`, `smbsrv_smb2_init_tcons`, `smbsrv_smb_tcon_find`, `smbsrv_smb2_tcon_find`, `smbsrv_smb_tcon_new`, and `smbsrv_smb2_tcon_new`. Internal support includes `smbsrv_init_tcons`, `smbsrv_tcon_find`, `smbsrv_tcon_destructor`, and `smbsrv_tcon_new`.

## Control Flow
Initialization creates an idr context, masks the requested limit to 24 bits, stores the limit, and clears the list. Lookup rejects zero and out-of-range TIDs, fetches from idr, type-checks, and updates last-request time. Allocation chooses memory owner and handle id limit based on SMB1 connection vs SMB2 session, allocates the tcon, stores share name, initializes handle tracking, assigns a random TID in range, links it, sets a destructor, and records connect time. Destruction logs remote address/share, disconnects NTVFS if present, removes the TID from the correct context, and unlinks the tcon.

## State And Persistence
The file mutates in-memory tcon id trees and linked lists and owns tcon lifetime. It does not persist share state, but NTVFS disconnect may flush/close backend state.

## Dependencies And Integration Points
It depends on idtree random allocation, talloc destructors, dlink lists, NTVFS disconnect, stream connection remote addresses, and handle initialization from the common handle module. SMB2 `tcon.c` and SMB1 tree-connect code allocate and find tcons through these APIs.

## Risks And Test Signals
Risks include 24-bit id limit truncation, random TID allocation exhaustion, destructor behavior with already-cleared NTVFS contexts, SMB2 session-owned memory assumptions, and handle cleanup ordering. Tests should create many tcons, find invalid/zero/out-of-range TIDs, disconnect with active NTVFS, compare SMB1 vs SMB2 ownership, and verify TID reuse after free.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/tcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/wscript_build -->
# sources/user-network-fs/samba/source4/smb_server/wscript_build

## Purpose
This Waf fragment defines the source4 SMB server service module and core SMB server subsystem, then recurses into SMB1 and SMB2 protocol subdirectories. It controls whether the NTVFS file server SMB service is built.

## Important APIs, Types, And Functions
It declares `service_smb` with source `service_smb.c`, generated `service_smb_proto.h`, service subsystem integration, init function `server_service_smb_init`, dependencies `SMB_SERVER netif shares samba-hostconfig cmdline`, and non-internal module visibility. It declares `SMB_SERVER` with sources `handle.c tcon.c session.c blob.c management.c smb_server.c`, generated `smb_server_proto.h`, and public dependencies `share LIBPACKET SMB_PROTOCOL SMB2_PROTOCOL`.

## Control Flow
At build time, Waf evaluates the module and subsystem declarations when `WITH_NTVFS_FILESERVER` is set. It then recurses into `smb` and `smb2`, where protocol-specific subsystem fragments extend the build graph.

## State And Persistence
This file affects build graph and generated prototype artifacts only. It has no runtime state.

## Dependencies And Integration Points
It ties service registration to the core SMB server subsystem and exposes both SMB1 and SMB2 protocol subsystems to the common server. It is a parent build node for the files researched in this subset.

## Risks And Test Signals
Risks include missing source files in subsystem lists, disabled builds omitting expected service registration, dependency order problems between `SMB_SERVER`, `SMB_PROTOCOL`, and `SMB2_PROTOCOL`, and stale autoproto output. Test signals are full configure/build with `WITH_NTVFS_FILESERVER`, disabled-feature builds, service module load tests, and incremental builds after changing exported functions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/auth/ntlmssp.c -->
# sources/user-network-fs/samba/source4/torture/auth/ntlmssp.c

## Purpose
This torture test validates NTLMSSP signing behavior through Samba’s GENSEC NTLMSSP implementation. It checks deterministic signatures for known session keys and negotiation flags and verifies expected failure modes for wrong endpoint direction, missing session keys, and shortened signatures.

## Important APIs, Types, And Functions
The main test is `torture_ntlmssp_self_check`; `torture_ntlmssp` registers it as `"NTLMSSP self check"`. The test uses `gensec_client_start`, `gensec_set_credentials`, `gensec_want_feature`, `gensec_start_mech_by_oid`, `gensec_ntlmssp_sign_packet`, `gensec_ntlmssp_check_packet`, and `ntlmssp_sign_init`. It inspects `struct gensec_ntlmssp_context` and `struct ntlmssp_state`.

## Control Flow
The test starts a client GENSEC context with command-line credentials, requests sign and seal, selects NTLMSSP, injects a known session key and flags, initializes signing, signs a fixed data blob, and compares with an expected signature. It then asserts that checking the just-generated packet fails because it is the wrong end and that clearing the session key produces `NT_STATUS_NO_USER_SESSION_KEY`. A second context repeats the test with a shorter key and different flags, comparing the non-sequence portion of the signature and checking truncated signature failure.

## State And Persistence
State is confined to talloc-owned GENSEC contexts and injected NTLMSSP state. No external files or server state are modified.

## Dependencies And Integration Points
The file integrates torture assertions, command-line credentials, loadparm GENSEC settings, NTLMSSP private state, and auth/gensec signing code. It is part of the auth torture suite.

## Risks And Test Signals
Risks include dependence on internal NTLMSSP structs, fixed expected bytes changing if signing algorithms or sequence handling changes, and use of command-line credentials even though the test mostly injects keys. Passing this test signals stable NTLMSSP signature generation, correct error mapping for missing keys and direction mismatch, and robust handling of short signatures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/auth/ntlmssp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/auth/pac.c -->
# sources/user-network-fs/samba/source4/torture/auth/pac.c

## Purpose
This torture test validates Kerberos PAC generation, decoding, checksum verification, Samba/Heimdal PAC parsing agreement, and byte-for-byte compatibility with a saved Windows Server 2003 PAC. It includes both generated self-checks and saved-blob compatibility checks.

## Important APIs, Types, And Functions
The test functions are `torture_pac_self_check`, `torture_pac_saved_check`, and suite factory `torture_pac`. It uses Kerberos keyblock helpers, `kerberos_create_pac`, `kerberos_decode_pac`, `kerberos_pac_blob_to_user_info_dc`, `kerberos_pac_logon_info`, `kerberos_encode_pac`, `make_user_info_dc_netlogon_validation`, NDR PAC parsing, SID comparison, and torture settings such as `pac_kdc_key`, `pac_member_key`, `pac_file`, `pac_client_principal`, and `pac_authtime`.

## Control Flow
The self-check initializes a Kerberos context, creates random ARCFOUR server and krbtgt keys, builds anonymous DC user info, parses a no-realm principal, creates a PAC, decodes and validates it, decodes it through Heimdal-style user-info extraction, extracts logon info, converts it back to auth user info, and compares primary SIDs. The saved check loads either the embedded `saved_pac` or an external PAC, builds configured keyblocks and principal/authtime, verifies decode and Heimdal extraction, checks expected SID for the embedded blob, re-encodes and regenerates PACs byte-for-byte when a KDC key is available, and negative-tests altered authtime and corrupted checksum.

## State And Persistence
The test uses talloc memory, Kerberos keyblock contents that must be freed, and optional file input through `pac_file`. It does not write persistent data.

## Dependencies And Integration Points
It depends on Samba Kerberos wrappers, Heimdal PAC handling, auth user-info conversion, NDR-generated PAC structures, Samba3 password hex parsing, and torture configuration. It directly exercises authentication code used by Kerberos service-ticket validation.

## Risks And Test Signals
Risks include crypto/library-version differences, embedded PAC assumptions, memory cleanup across many early failure paths, optional KDC key paths that skip encoding checks, and exact byte-for-byte comparisons that are intentionally strict. Passing tests signal PAC generation/parse compatibility, checksum enforcement, auth-time validation, SID preservation, and stable NDR layout/padding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/auth/pac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/auth/smbencrypt.c -->
# sources/user-network-fs/samba/source4/torture/auth/smbencrypt.c

## Purpose
This file provides a focused torture test for the legacy SMB DES password hash helper `E_deshash`. It checks known outputs and length behavior for LANMAN-style password hashing.

## Important APIs, Types, And Functions
The main test is `torture_deshash`; `torture_smbencrypt` registers it as `"deshash check"`. The tested API is `E_deshash` from `libcli/auth/libcli_auth.h`.

## Control Flow
The test iterates over hard-coded input strings, expected 16-byte hash outputs, and expected boolean return values. For each case it calls `E_deshash`, asserts that the boolean result matches, and compares the 16-byte output buffer regardless of pass/fail expectation.

## State And Persistence
All state is stack-local test data and result buffers. No persistent data is read or written.

## Dependencies And Integration Points
It integrates the torture framework with the low-level SMB authentication crypto helper. It is registered in the auth torture suite and protects compatibility for legacy hash calculations.

## Risks And Test Signals
Risks include reliance on legacy DES behavior, uppercase/truncation semantics in the underlying helper, and the subtle case where overlong input is expected to return false while leaving deterministic output. Passing this test signals stable empty-password, 8-byte, 13/14-byte, and overlong password hash behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/auth/smbencrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/aliases.c -->
# sources/user-network-fs/samba/source4/torture/basic/aliases.c

## Purpose
This torture helper scans SMB1 TRANS2 information levels to discover query/set aliases. It brute-forces many info-level values, records successful responses, compares blobs for identical results, and reports potential alias levels for qfsinfo, qfileinfo, qpathinfo, findfirst, setfileinfo, and setpathinfo.

## Important APIs, Types, And Functions
The suite factory is `torture_trans2_aliases`. Core helpers are `gen_aliases`, `gen_set_aliases`, and test cases `qfsinfo_aliases`, `qfileinfo_aliases`, `qpathinfo_aliases`, `findfirst_aliases`, `setfileinfo_aliases`, and `setpathinfo_aliases`. `struct trans2_blobs` stores a level and output parameter/data blobs for comparison. The file references external `create_complex_file`.

## Control Flow
Query scans initialize an `smb_trans2` request for a specific TRANS2 setup code, create a test file where needed, set the info level field repeatedly, call `smb_raw_trans2`, store successful output blobs, and then compare all success pairs for identical parameter and data blobs. Set scans iterate levels and even data sizes up to 1024 bytes, distinguishing invalid-level errors from size/content errors, and report levels that can reach OK or invalid-parameter responses.

## State And Persistence
The tests create and delete temporary files under the tested share. Alias results live only in talloc lists and torture output. No repository state is changed.

## Dependencies And Integration Points
It depends on raw TRANS2 client APIs, smbcli helpers, dlink lists, blob comparison, and the basic torture suite registration in `base.c`. It exercises server TRANS2 dispatch and info-level compatibility.

## Risks And Test Signals
Risks include long brute-force runtime, server-side side effects from malformed set buffers, reliance on all-zero input buffers, and cleanup after assertion failures. Test signals are the set of accepted levels, aliases with identical output, expected invalid-level behavior, and regressions in TRANS2 compatibility across SMB servers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/aliases.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/attr.c -->
# sources/user-network-fs/samba/source4/torture/basic/attr.c

## Purpose
This file tests Windows file attribute behavior for SMB opens and setattr/getattr operations. It covers how truncate opens combine initial and requested attributes, and whether changing file/directory attributes preserves security descriptors.

## Important APIs, Types, And Functions
The public tests are `torture_openattrtest` and `torture_winattrtest`. Static tables `open_attrs_table` and `attr_results` define attribute combinations and expected truncate-open outcomes. The tests use `smbcli_nt_create_full`, `smbcli_setatr`, `smbcli_getatr`, `smb_raw_fileinfo` with `RAW_FILEINFO_SEC_DESC`, and `security_ace_equal`.

## Control Flow
`torture_openattrtest` iterates initial attribute combinations, creates a file, then iterates truncate-open attribute combinations and checks whether failures are `NT_STATUS_ACCESS_DENIED` unless the combination is listed as expected-success. Successful opens are closed and followed by `getatr` checks against `attr_results`. `torture_winattrtest` creates a file, stores its security descriptor, repeatedly sets attributes and confirms attributes and ACL ACEs remain stable, then repeats similar checks for a directory with `FILE_ATTRIBUTE_DIRECTORY` expected in returned attributes.

## State And Persistence
The tests create/delete `\openattr.file`, `\winattr1.file`, and `\winattr1.dir` on the target share. They modify file and directory attributes during execution and clean them up at exit labels.

## Dependencies And Integration Points
It depends on SMB client raw and convenience APIs, security descriptor structures, torture failure limits, and the basic suite that registers these tests. It exercises server create/open, attribute storage, descriptor retrieval, and directory handling.

## Risks And Test Signals
Risks include broad nested loops producing many failures, cleanup needing attribute reset before unlink, assumptions about archive bit normalization, and comparing ACE lists without first checking both DACL shapes in all cases. Passing tests signal Windows-compatible attribute preservation, truncate-open result attributes, directory attribute composition, and ACL stability across attribute changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/base.c -->
# sources/user-network-fs/samba/source4/torture/basic/base.c

## Purpose
This large file registers and implements many foundational SMB1 torture tests. It covers connection setup, TID/VUID isolation, attributes and TRANS2 metadata, negotiation behavior, tree-connect device types, read/write integrity, deferred opens, open/share/delete semantics, xcopy/iometer patterns, path checking, Samba3 error mappings, birth time stability, timewarp root opens, and GMT search masks.

## Important APIs, Types, And Functions
The exported initializer is `torture_base_init`. Major local tests include `open_nbt_connection`, `run_fdpasstest`, `run_attrtest`, `run_trans2test`, `run_negprot_nowait`, `run_tcon_test`, `run_tcon_devtype_test`, `rw_torture2`, `run_readwritetest`, `run_deferopen`, `run_vuidtest`, `run_opentest`, `run_xcopy`, `run_iometer`, `torture_chkpath_test`, `torture_samba3_errorpaths`, `run_birthtimetest`, `torture_smb1_twrp_openroot`, and `torture_smb1_find_gmt_mask`. It also registers many tests implemented in sibling files.

## Control Flow
Most tests open one or two SMB connections, create temporary files/directories, perform protocol operations, assert status codes and side effects, then clean up. `run_opentest` is the densest path, checking invalid control characters, readonly error selection, truncate behavior on readonly opens, temporary file creation, non-IO opens with delete access, sharing behavior, and lock/truncate interactions. `torture_base_init` creates the `"base"` suite and registers one-SMB, two-SMB, multi-SMB, nested-suite, benchmark, scan, and simple tests.

## State And Persistence
The file deliberately mutates target SMB shares by creating, opening, writing, locking, listing, setting attributes, and deleting temporary paths. It temporarily changes client loadparm settings in the Samba3 error-path test and restores them. Repository state is not changed.

## Dependencies And Integration Points
It depends on `libcli`, raw SMB APIs, torture utility helpers, loadparm, events, resolver support, filesystem/time wrappers, and many sibling torture suites. It is a central integration point for SMB1 server/client behavior and is used to detect regressions in both Samba and third-party SMB servers.

## Risks And Test Signals
Risks include timing-sensitive sleeps, environment changes such as `TZ=GMT`, benchmark tests depending on `torture_numops`, cleanup after early failures, broad server-specific assumptions, and skipped timewarp tests without settings. Test signals include exact NTSTATUS/DOS mappings, data integrity across connections, no cross-VC handle leakage, correct TID/VUID rejection, create/open/share-mode compatibility, metadata timestamp behavior, and suite registration coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/charset.c -->
# sources/user-network-fs/samba/source4/torture/basic/charset.c

## Purpose
This file implements SMB torture tests for Unicode filename handling. It creates names from explicit UTF-16 code units to check composed characters, naked diacritical marks, surrogate halves/pairs, and fullwidth ASCII equivalence behavior.

## Important APIs, Types, And Functions
The suite factory is `torture_charset`. Helper `unicode_open` converts an array of UTF-16 code units into a Unix string through the configured iconv handle, prefixes `\\chartest\\`, and performs a raw NTCreateX. Test cases are `test_composed`, `test_diacritical`, `test_surrogate`, and `test_widea`.

## Control Flow
Each test prepares `BASEDIR` with `torture_setup_dir`, then calls `unicode_open` with specific codepoint sequences. The composed test creates `a` plus combining diaeresis and precomposed `ä`. The diacritical test creates one and two naked combining marks. The surrogate test creates high surrogate, low surrogate, and a pair. The wide-a test creates ASCII `a`, fullwidth lowercase `a`, and expects fullwidth uppercase `A` to collide.

## State And Persistence
The tests create files under `\\chartest\\` on the target share. Memory for converted names is talloc-scoped. No repository state is changed.

## Dependencies And Integration Points
It depends on raw SMB open, charset conversion via `lpcfg_iconv_handle`, torture setup helpers, and the basic suite registration in `base.c`. It exercises server filename normalization/casefolding and Samba client charset conversion.

## Risks And Test Signals
Risks include platform filesystem normalization differences, iconv behavior for invalid surrogate code units, expectations around fullwidth case collisions, and cleanup being delegated to directory setup rather than each test. Passing tests signal that the server accepts edge Unicode names and applies expected equivalence/collision behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/basic/charset.c -->
