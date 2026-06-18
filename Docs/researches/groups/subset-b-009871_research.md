# Research: subset-b-009871

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_reply.c -->
## sources/user-network-fs/samba/source3/smbd/smb1_reply.c

### Purpose
`smb1_reply.c` is the central SMB1 command-reply implementation for `smbd`. It converts decoded `struct smb_request` packets into SMB1 responses for tree connections, attribute operations, legacy directory search, file open/create/delete, raw and normal reads/writes, close/logoff/tree disconnect, printer commands, directory changes, rename/copy stubs, byte-range locking, and several obsolete multiplex commands. The file is compatibility-heavy: many branches explicitly preserve DOS/LANMAN/NT1 wire behavior, historical error mappings, and client quirks.

### Important APIs, Types, And Functions
- Handle validation helpers: `check_fsp_open()` verifies `connection_struct`, `files_struct`, connection identity, and VUID ownership; `check_fsp()` additionally rejects directories and pathref-only handles without I/O fds, then increments `fsp->num_smb_operations`.
- Path helper: `smb1_strip_dfs_path()` removes `\\server\share` style DFS prefixes after SMB1 path syntax conversion and clears `UCF_DFS_PATHNAME`.
- Tree and session lifecycle replies: `reply_tcon()`, `reply_tcon_and_X()`, `reply_ulogoffX()`, `reply_exit()`, `reply_close()`, and `reply_tdis()` create or tear down tcons, sessions, per-PID opens, individual opens, and tree connections.
- File and directory replies: `reply_checkpath()`, `reply_getatr()`, `reply_setatr()`, `reply_open()`, `reply_open_and_X()`, `reply_mknew()`, `reply_ctemp()`, `reply_unlink()`, `reply_mkdir()`, `reply_rmdir()`, and `reply_mv()` wrap path conversion and VFS calls.
- Search helpers: `make_dir_struct()`, `mask_match_search()`, `mangle_mask_match()`, `smbd_dirptr_8_3_match_fn()`, `get_dir_entry()`, `reply_search()`, `reply_fclose()`, `reply_findclose()`, and `reply_findnclose()` implement old 8.3 directory search and dptr cleanup.
- I/O replies: `reply_readbraw()`, `reply_lockread()`, `reply_read()`, `setup_readX_header()`, `reply_read_and_X()`, `reply_writebraw()`, `reply_writeunlock()`, `reply_write()`, `is_valid_writeX_buffer()`, `reply_write_and_X()`, `reply_lseek()`, `reply_flush()`, and `reply_writeclose()`.
- Locking replies: `reply_lock()`, `reply_unlock()`, `reply_lockingX()`, plus exported parsers `get_lock_pid()` and `get_lock_count()`.
- Printer replies: `reply_printopen()`, `reply_printclose()`, `reply_printqueue()`, and `reply_printwrite()` connect SMB1 print operations to Samba spool/open/write/query paths.

### Control Flow
Most handlers follow a common pattern: validate `wct`/buffer lengths, parse fields from `req->vwv` and `req->buf`, resolve handles or paths, enforce access and locking, call VFS or server subsystems, then build an SMB1 response with `reply_smb1_outbuf()` and `SSVAL`/`SIVAL` field writes. Path-based commands usually compute UCF flags, optionally extract snapshot tokens, call `smb1_strip_dfs_path()`, then use `filename_convert_dirfsp()` or related helpers before operating.

Tree connect flow parses service/password/device strings, finds or creates a tcon through `make_connection()`, sets `req->conn`, writes `smb_tid`, and returns optional NT1 extended response information such as share permissions, DFS, CSC, and extended-signature support. `reply_tcon_and_X()` also performs the SMB1 application-key setup on the first tree connect when a signing key exists, deriving extended signatures when requested.

Open/create flows map legacy open flags to NT create semantics, use `SMB_VFS_CREATE_FILE()`, defer on sharing violations where possible, fall back to FCB/DOS open compatibility for some opens, reject directory opens where the command expects files, set allocation size for `openX`, and report oplock grant bits in both core and extended forms.

Read paths split into raw, core, lockread, and AndX variants. Raw reads send direct NetBIOS-length-prefixed data and must return four zero bytes on many errors. `reply_read_and_X()` computes safe read sizes, tries scheduled AIO for smaller reads, and otherwise sends synchronously, using `sendfile` only when the packet is unchained, unencrypted, not signed, not an alternate stream, and the share/client policy allows it. Write paths similarly distinguish raw two-phase writes, core writes, zero-length truncation for `SMBwrite`, no-truncate zero writes for `SMBwriteX`, optional recvfile-style unread bytes, strict lock checks, and write-through sync.

Close, exit, ulogoff, and tree-disconnect paths are tevent-aware. If affected files have outstanding AIO, they mark relevant `fsp` objects as closing, enqueue waiters on each `fsp->aio_requests`, move the SMB request to a longer-lived context, and send the SMB response only after the wait queue drains.

### State And Persistence Behavior
The file mutates live SMB server state rather than persistent configuration. It creates and frees `smbXsrv_tcon`, `connection_struct`, `smbXsrv_session`, `files_struct`, directory pointer, oplock, and byte-range-lock state. Persistent filesystem changes occur through VFS create, write, truncate, mkdir, rmdir via delete-on-close, rename, unlink, timestamp updates, DOS attribute updates, and printer spool writes. Session state changes include marking sessions deleted on logoff, updating application/session keys during tree connect, clearing VUID caches on reauth elsewhere, and setting tree status to `NT_STATUS_NETWORK_NAME_DELETED` during disconnect. It also updates request/user-visible compatibility state such as current file position with `fh_set_pos()`, dptr resume status, close write times, oplock type, and `req->outbuf` ownership for async/direct-send paths.

### Dependencies And Integration Points
This file integrates with Samba's VFS (`SMB_VFS_CREATE_FILE`, `SMB_VFS_SENDFILE`, stat, lseek, delete-on-close), path conversion and DFS handling, `smbXsrv_session` and `smbXsrv_open` lookup, tcon management, locking/brlock async helpers, AIO queues, oplock helpers, signing state, encryption flags, IPC pipe handlers, printing/spoolss RPC, share configuration (`lp_*`), protocol profiling, and SMB1 packet construction/sending. It also depends on error translation helpers that map NTSTATUS to DOS/legacy errors, which is important for old dialect compatibility.

### Risks
- Wire length arithmetic is high risk. Many handlers parse client-supplied offsets and lengths; several comments call out CVE-2017-12163 protections. Any future change must preserve overflow and bounds checks around `smb_doff`, `numtowrite`, raw write data, print data, and search status blobs.
- Signing/encryption restrictions are security-sensitive. Raw reads/writes and `sendfile` are disabled when signing or sealing is active; relaxing this would break integrity/confidentiality guarantees.
- Async teardown is race-sensitive. `reply_ulogoffX`, `reply_exit`, `reply_close`, and `reply_tdis` rely on marking files closing, queueing AIO waits, and moving request ownership correctly.
- Compatibility branches intentionally return odd errors or behaviors for LANMAN/DOS/OS2/Win9x/NT clients. Seemingly cleaner NTSTATUS mappings or zero-length write semantics can regress client interoperability.
- Path conversion must preserve DFS, snapshot token, stream, POSIX pathname, and symlink/reparse-point behavior; inconsistent UCF flags can create security or namespace bugs.

### Test Signals
Relevant tests should include Samba torture coverage for SMB1 open/create/read/write, LARGE_READX, raw read/write disabled under signing/sealing, strict byte-range lock conflicts, delayed sharing violation deferral, old search/dptr resume and close, DFS path stripping, snapshot-token paths, print queue/write behavior, `BASE-SAMBA3ERROR` style DOS error mappings, `lock11` cancel behavior, and AIO close/logoff/tree-disconnect completion. Fuzz-style tests around `wct`, byte counts, offsets, and chained AndX forms are especially valuable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_reply.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_reply.h -->
## sources/user-network-fs/samba/source3/smbd/smb1_reply.h

### Purpose
`smb1_reply.h` declares the SMB1 command handlers and small exported helpers implemented primarily in `smb1_reply.c`. It is the dispatch-facing interface for legacy SMB1 replies.

### Important APIs, Types, And Functions
The header exports `reply_*` handlers for tree connect, IOCTL, path/attribute operations, legacy searches, opens, session logoff, creates, deletes, reads, writes, seeks, flush, close, locking, echo, printing, directory management, rename/copy, obsolete multiplex commands, extended attributes, and find close commands. It also exports `setup_readX_header()`, `error_to_writebrawerr()`, `is_valid_writeX_buffer()`, `get_lock_pid()`, and `get_lock_count()`. All handlers take `struct smb_request *`; lock parsers operate on wire data and a large-file-format flag.

### Control Flow
The header has no runtime control flow. Its structure mirrors the SMB1 command dispatch surface and groups helpers near the commands that need them.

### State And Persistence Behavior
No state is stored in the header. The declarations imply mutations performed by implementation files: request output buffers, file/session/tree state, VFS state, locks, and printer state.

### Dependencies And Integration Points
Consumers must include definitions for `struct smb_request`, `struct smbXsrv_connection`, `connection_struct`, `DATA_BLOB`, and Samba scalar types. The file integrates with SMB1 dispatch tables and with recvfile/signing logic through `is_valid_writeX_buffer()`.

### Risks
Because this is a broad exported surface, prototype drift can break SMB1 dispatch or helper callers. Exporting raw helper names without namespacing beyond SMB1 also means new helper additions should avoid conflicts.

### Test Signals
Compile/link coverage is the main direct signal. Behavioral coverage comes from command-dispatch tests that ensure every declared handler still matches the implementation signature and is callable by the SMB1 switch layer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_reply.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_service.c -->
## sources/user-network-fs/samba/source3/smbd/smb1_service.c

### Purpose
`smb1_service.c` opens SMB1 tree connections to configured shares. It translates a client-supplied service name and device type into a Samba service number, allocates `smbXsrv_tcon` and `connection_struct` state, enforces per-share limits, and delegates share initialization to common connection code.

### Important APIs, Types, And Functions
- `make_connection_smb1()` is the internal constructor for a known service number. It checks `lp_max_connections()`, creates an SMB1 tcon with `smb1srv_tcon_create()`, allocates a `connection_struct` via `conn_new()`, links `conn->cnum` and `conn->tcon`, calls `make_connection_snum()`, then stores the connection under `tcon->compat`.
- `make_connection()` is the exported SMB1 tree-connect entry point. It validates root execution assumptions, open connection count, and session presence; handles `[homes]`; normalizes service names; resolves services with `find_service()`; rejects missing IPC/ADMIN access and DFS proxy shares; and calls `make_connection_smb1()`.

### Control Flow
The public function starts from `req->session` and `service_in`. `[homes]` has fast paths based on `session->homes_snum`, avoiding repeated passwd/winbind lookup. Other services are duplicated, lowercased, and resolved. Invalid or intentionally hidden services return NTSTATUS failures. Successful resolution passes through the internal constructor, which allocates the tcon before the compatibility `connection_struct`, then calls the common share attach logic.

### State And Persistence Behavior
The file creates in-memory tree connection state only. It increments the server's live tcon/connection set by allocating an `smbXsrv_tcon` and `connection_struct`, sets `conn->cnum` to the wire tree id, assigns `conn->tcon`, and marks `tcon->status = NT_STATUS_OK` after `make_connection_snum()` succeeds. On failure it frees partially created tcon/connection state. It reads configuration and live connection counts but does not write persistent files.

### Dependencies And Integration Points
It depends on Samba loadparm share lookup, connection accounting, session state from SMB1 session setup, `smbXsrv_tcon` management, common `make_connection_snum()` share setup, `[homes]` registration done during session setup, DFS proxy configuration, and remote-address/debug helpers.

### Risks
- `make_connection()` assumes it is called as root in normal mode and panics otherwise; callers must preserve privilege expectations.
- The `[homes]` path relies on `session->homes_snum` being created during session setup; regressions there surface as bad network name on tree connect.
- Tcon and connection allocation are split; failure cleanup must keep ownership correct to avoid dangling `tcon->compat` or leaked tcon ids.
- Service name lowercasing and `find_service()` mutation require care with talloc ownership and NULL handling.

### Test Signals
Useful tests include SMB1 tree connect to normal shares, `[homes]` by literal name and concrete username share, unknown shares, IPC$/ADMIN$ refusal paths, `max connections` enforcement, DFS proxy refusal for non-DFS clients, and failure-injection/valgrind coverage around tcon allocation and `make_connection_snum()` failure cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_service.h -->
## sources/user-network-fs/samba/source3/smbd/smb1_service.h

### Purpose
`smb1_service.h` exposes the SMB1 tree-connect service opener `make_connection()` to the SMB1 reply layer.

### Important APIs, Types, And Functions
The single declaration is `connection_struct *make_connection(struct smb_request *req, NTTIME now, const char *service_in, const char *pdev, uint64_t vuid, NTSTATUS *status)`. It returns a live `connection_struct` on success and returns NULL with `*status` set on failure.

### Control Flow
The header has no executable logic. Its API shape shows that callers provide request/session context, current time, service and device strings from the wire, VUID, and a status out-parameter.

### State And Persistence Behavior
No state is stored here. The implementation creates in-memory tcon/connection state and may trigger common share setup side effects.

### Dependencies And Integration Points
The declaration depends on Samba request, time, status, and connection types. It is consumed by `reply_tcon()` and `reply_tcon_and_X()` in the SMB1 reply implementation.

### Risks
The function leaves the process as root according to implementation comments, so callers must not assume user impersonation on return. API changes would affect SMB1 tree-connect handlers directly.

### Test Signals
Compile coverage plus SMB1 tree-connect integration tests validate this header's contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_sesssetup.c -->
## sources/user-network-fs/samba/source3/smbd/smb1_sesssetup.c

### Purpose
`smb1_sesssetup.c` handles SMB1 `SMBsesssetupX` authentication. It supports extended-security SPNEGO and legacy plaintext/NTLM response flows, creates and updates `smbXsrv_session` records, installs session/auth info, negotiates or activates SMB1 signing, registers homes shares, updates client capability state, and builds the SMB1 session setup response.

### Important APIs, Types, And Functions
- `push_signature()` appends native OS, Samba version, and workgroup strings to session setup replies.
- `reply_sesssetup_and_X_spnego()` implements the extended-security path using GENSEC/SPNEGO. It accepts continuation on an existing VUID, creates or finds a session auth context, calls `gensec_update()`, finalizes `auth_session_info`, creates SMB1 signing keys, sets expiration for dynamic reauth, claims and updates the session, and returns a token plus server signature strings.
- `shutdown_other_smbds()` and `setup_new_vc_session()` implement the optional `VC == 0` behavior that can signal other smbd processes from the same client IP to shut down when `reset on zero vc` is enabled.
- `struct reply_sesssetup_and_X_state` owns temporary authentication material; its destructor clears LM/NT/plaintext blobs.
- `reply_sesssetup_and_X()` is the exported command handler. It detects SPNEGO vs legacy forms, parses password blobs and user/domain/client strings, prepares `auth_usersupplied_info`, checks credentials, creates the session, installs keys and auth state, activates signing where possible, and updates the SMB UID fields.

### Control Flow
At entry, the handler records client signing flags and calls `smb1_srv_set_signing_negotiated()`. If the packet is a 12-word extended-security request and SPNEGO was negotiated, it optionally runs zero-VC cleanup and delegates to `reply_sesssetup_and_X_spnego()`.

The legacy path branches by negotiated protocol. Pre-NT1 packets remove 32-bit status support and parse a single password blob plus username. NT1 packets parse LM and NT response lengths, client capabilities, username, domain, native OS, native LANMAN, and optional primary-domain strings. The code includes compatibility repairs for old clients that misreport plaintext password lengths. It then handles anonymous, encrypted NTLM response, and plaintext authentication setup paths, calls `auth_check_password_session_info()`, and builds the response.

On success, both SPNEGO and legacy paths create or update an `smbXsrv_session`, configure SMB1 signing algorithm metadata, create a signing key from the auth session key, create or preserve the SMB1 application key, set `auth_session_info`, increment auth sequence numbers, register `[homes]` for real users, call `session_claim()` and `smbXsrv_session_update()`, adjust `xconn->smb1.sessions.max_send` on first session setup, reload services, and set response VUID/action fields.

### State And Persistence Behavior
The file mutates connection-wide client capability state (`global_client_caps`, common flags2, remote architecture), SMB1 signing negotiation/activation state, `xconn->smb1.sessions.done_sesssetup` and `max_send`, server user count, current user info, session records, session auth contexts, auth sequence numbers, auth time, expiration time, signing/application key blobs, and `[homes]` share registration. It can send process shutdown messages to other smbd instances for zero-VC reset. Sensitive temporary credential blobs are cleared in the state destructor and session keys are cleared or moved after derivation.

### Dependencies And Integration Points
This file integrates with auth4 and GENSEC, NTLM challenge creation, `smbXsrv_session` create/update/claim/auth APIs, SMB signing key creation, SMB1 signing activation, server messaging, remote architecture detection, loadparm workgroup/version/share reload behavior, and profile auth counters. It is upstream of `smb1_service.c` because successful authenticated sessions populate `session->homes_snum` for `[homes]` tree connects.

### Risks
- Credential parsing is wire-exposed and highly compatibility-sensitive. Password lengths, Unicode/plaintext handling, and capability-driven status flags must remain bounded and historically compatible.
- SPNEGO continuation reuses sessions and pending auth; incorrect state clearing can break reauth or leak partial auth contexts.
- Session key/application key handling is security-critical. The code intentionally clears raw session keys and defers/derives application keys differently in SPNEGO vs legacy paths.
- Signing negotiation depends on both client flags and server policy; incorrect activation can either reject clients or leave signed-required sessions unsigned.
- `VC == 0` reset can signal other smbd processes; address matching and configuration gating must remain conservative.

### Test Signals
Important coverage includes SMB1 SPNEGO multi-leg authentication, legacy encrypted NTLM, plaintext fallback when configured, anonymous/guest logons, signing-required and signing-optional clients, first-session `max_send` setup, dynamic reauth expiration, `[homes]` registration, session update/claim failure handling, malformed password lengths, Unicode/plaintext password variants, zero-VC reset behavior, and auth profile success/failure counters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_sesssetup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_sesssetup.h -->
## sources/user-network-fs/samba/source3/smbd/smb1_sesssetup.h

### Purpose
`smb1_sesssetup.h` exposes the SMB1 session setup command handler.

### Important APIs, Types, And Functions
The single declaration is `void reply_sesssetup_and_X(struct smb_request *req)`. It is the dispatch entry point for SMB1 `SMBsesssetupX`.

### Control Flow
The header has no executable control flow. The implementation decides between SPNEGO and legacy authentication based on word count, flags, negotiated protocol, and connection state.

### State And Persistence Behavior
No state is stored in the header. The implementation creates and updates authenticated SMB1 session state, signing keys, client capability state, and homes share registration.

### Dependencies And Integration Points
The declaration depends on `struct smb_request` and is consumed by SMB1 command dispatch. It connects authentication to later tree-connect and file-access paths because `req->session`, VUID, signing, and `session->homes_snum` are established by the implementation.

### Risks
Any signature change would affect the SMB1 dispatch table. The handler must remain callable with `req->conn == NULL`, as session setup occurs before tree connect.

### Test Signals
Compile coverage and SMB1 authentication integration tests validate this header's contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_sesssetup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_signing.c -->
## sources/user-network-fs/samba/source3/smbd/smb1_signing.c

### Purpose
`smb1_signing.c` adapts Samba's generic SMB1 signing engine to the `smbXsrv_connection` server connection. It validates incoming signatures, signs outgoing packets, initializes signing state according to server policy, supports shared-memory signing state for async echo handling, records negotiated signing flags, and activates signing after session setup provides keys.

### Important APIs, Types, And Functions
- `smb1_srv_check_sign_mac()` validates an incoming SMB1 PDU and returns the sequence number. It has a trusted-channel shortcut that reads sequence/status fields directly from the security signature field.
- `smb1_srv_calculate_sign_mac()` signs outgoing SMB1 PDUs for a supplied sequence number.
- `smb1_srv_cancel_sign_response()` cancels a one-way reply in the signing sequence.
- `struct smbd_shm_signing`, `smbd_shm_signing_alloc()`, `smbd_shm_signing_free()`, and `smbd_shm_signing_destructor()` provide a tiny two-allocation shared-memory allocator used when the async SMB echo handler needs signing state visible across processes/contexts.
- `smb1_srv_init_signing()` creates `conn->smb1.signing_state` with allowed/desired/mandatory policy from loadparm and optional shared memory allocation.
- `smb1_srv_set_signing_negotiated()`, `smb1_srv_is_signing_active()`, `smb1_srv_is_signing_negotiated()`, and `smb1_srv_set_signing()` expose negotiation, state checks, and activation.

### Control Flow
Incoming signing checks ignore non-session NetBIOS messages. Normal packets compute the next expected sequence with `smb1_signing_next_seqnum()` and validate via `smb1_signing_check_pdu()`. Trusted-channel packets must be long enough, must carry an OK status in the signature field, and pass through the embedded sequence number.

Outgoing signing similarly ignores non-session messages, strips the NBT header for signing, and delegates to `smb1_signing_sign_pdu()`. Initialization asks loadparm whether server signing is allowed and mandatory; if async echo handling is enabled it allocates 4096 bytes of anonymous shared memory and initializes the generic signing engine with custom alloc/free callbacks. Activation requires a non-empty user session key and either negotiated or mandatory signing, then calls `smb1_signing_activate()`.

### State And Persistence Behavior
The main state is `conn->smb1.signing_state`. In async echo mode, a `struct smbd_shm_signing` talloc child owns anonymous shared memory and tracks up to two allocation regions used by the signing engine. No persistent disk state is written. Sequence numbers and active/negotiated/mandatory flags live in the signing engine.

### Dependencies And Integration Points
This file depends on `../libcli/smb/smb_signing.h`, loadparm server-signing policy, `lp_async_smb_echo_handler()`, anonymous shared memory helpers, and SMB packet length/header macros. It is used by session setup to negotiate/activate signing and by the SMB1 receive/send paths to check and calculate MACs. `smb1_reply.c` also queries active signing to disable raw I/O and sendfile paths.

### Risks
- Sequence-number handling is integrity-critical; incorrect cancellation or trusted-channel parsing can desynchronize signing or accept forged packets.
- Shared-memory allocation assumes the signing engine only allocates two chunks. If the engine allocation pattern changes, the custom allocator can fail unexpectedly.
- Non-session-message bypass relies on correct NetBIOS message type interpretation.
- Activation deliberately returns without error when signing was not negotiated and not mandatory; callers must enforce mandatory policy elsewhere.

### Test Signals
Tests should cover signing initialization under allowed/disabled/mandatory policy, activation after valid session keys, mandatory client/server combinations, bad signature rejection, sequence cancellation for one-way requests, raw I/O/sendfile disabled when active, trusted-channel validation with short packets and non-OK embedded statuses, and async echo-handler shared-memory initialization/failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_signing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_signing.h -->
## sources/user-network-fs/samba/source3/smbd/smb1_signing.h

### Purpose
`smb1_signing.h` declares the SMB1 server-signing adapter API used by SMB1 receive/send, negotiation, and session setup code.

### Important APIs, Types, And Functions
It forward-declares `struct smbXsrv_connection` and declares functions to check incoming MACs, calculate outgoing MACs, cancel a response in the signing stream, mark signing as negotiated, query active/negotiated state, activate signing with session key and response blobs, and initialize signing state for a connection.

### Control Flow
The header has no executable logic. The API sequence is: initialize signing during negotiation, update negotiated flags from session setup/client flags, activate after authentication yields a session key, then check/sign packets during I/O.

### State And Persistence Behavior
No state is stored in the header. The implementation owns `conn->smb1.signing_state` and optional anonymous shared memory.

### Dependencies And Integration Points
The declarations depend on Samba `DATA_BLOB`, `NTSTATUS`, `loadparm_context`, and `smbXsrv_connection` types. The API is consumed by SMB1 session setup, SMB1 packet send/receive code, and reply handlers that need to know whether signing disables raw/direct I/O.

### Risks
The API exposes security-sensitive state transitions. Callers must not call activation with the wrong key material or assume `set_signing()` reports hard failure. Query functions should be used consistently before permitting optimizations that bypass normal packet signing.

### Test Signals
Compile coverage plus SMB1 signing negotiation/authentication/integrity tests validate this header. Tests that exercise sendfile/raw I/O decisions indirectly validate consumers of `smb1_srv_is_signing_active()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_signing.h -->
