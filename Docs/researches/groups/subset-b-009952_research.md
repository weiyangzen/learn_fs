# subset-b-009952 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/negprot.c -->
# sources/user-network-fs/samba/source4/smb_server/smb/negprot.c

## Purpose
Implements SMB1 dialect negotiation for the source4 SMB server and the transition point from SMB1 negotiation to the SMB2 server. It parses the client's dialect list, chooses the most preferred dialect allowed by server min/max protocol settings, initializes negotiated capability state, prepares authentication challenge or GENSEC/SPNEGO bootstrap data, and rejects unsupported or repeated negotiation.

## Important APIs, Types, And Functions
- `smbsrv_reply_negprot()` is the wire entry point for `SMBnegprot`; it reads ASCII4 dialect strings using `req_pull_ascii4()`, checks `done_negprot`, and dispatches through `supported_protocols`.
- `supported_protocols[]` encodes preference order from `SMB 2.002` down to core dialects, with per-dialect reply functions and protocol levels.
- `reply_nt1()` builds the NT LM 0.12 negotiation response, including capabilities such as Unicode, status32, DFS, raw mode, large read/write, large files, extended security, and signing flags.
- `reply_smb2()` tears down SMB1 session/tcon/signing state, initializes SMB2 state, switches the packet callback to `smbsrv_recv_smb2_request`, and calls `smb2srv_reply_smb_negprot()`.
- `get_challenge()` creates `auth4_context` and obtains the 8-byte challenge for challenge-response authentication.
- Legacy reply helpers (`reply_corep`, `reply_coreplus`, `reply_lanman1`, `reply_lanman2`, `reply_nt1_orig`) serialize dialect-specific fixed fields, workgroup/server strings, raw-mode bits, and DOS/NT time formats.

## Control Flow
Negotiation is one-shot: `smbsrv_reply_negprot()` marks `done_negprot`, then loops through offered dialect strings. The server iterates its own preference table first, respecting `lpcfg_server_max_protocol()` and `lpcfg_server_min_protocol()`, so the selected dialect is the best mutually supported dialect. Legacy dialect handlers set `smb_conn->negotiate.protocol`, calculate raw-mode support from configuration, optionally allocate a challenge, and terminate the connection if mandatory signing is enabled for dialects that cannot sign. NT1 adds capability negotiation and either emits old-style challenge data or starts server-side GENSEC with SPNEGO/NTLMSSP. SMB2 selection discards SMB1-specific state and changes the receive path.

## State And Persistence
The file mutates connection-level negotiation state: `done_negprot`, `protocol`, `encrypted_passwords`, `auth_context`, `server_credentials`, `oid`, `max_recv`, `zone_offset`, and negotiated capability exposure. `auth_context` and `server_credentials` are deliberately reparented to the connection because session setup needs them after the request is gone. The large-file capability probe creates and unlinks a temporary lock-path file named `large_test.dat`.

## Dependencies And Integration Points
Depends on Samba loadparm, auth, credentials, GENSEC, packet, SMB2 server, and request serialization helpers from `request.c` and `srvtime.c`. It feeds `sesssetup.c` by preparing the auth context, challenge, selected OID, and server credentials. It feeds `receive.c` by setting the negotiated protocol/capabilities used by later dispatch and signing.

## Risks
Negotiation is security-sensitive because it advertises signing, raw mode, extended security, DFS, Unicode, and status-code behavior. `large_file_support()` performs a filesystem probe in the lock directory, so unusual permissions or filesystems can affect advertised large-file capability. NT1 negotiation sends the response with `smbsrv_send_reply_nosign()`, which is correct before signing setup but should remain explicit. Multiple negotiation attempts terminate the connection; tests should cover that behavior. Fallback from SPNEGO to raw NTLMSSP is compatibility-driven and depends on later session setup enforcing raw NTLMv2 policy.

## Test Signals
Useful tests include dialect preference under min/max protocol bounds, repeated negprot termination, mandatory-signing rejection for legacy dialects, NT1 capability flags for Unicode/status32/DFS/raw/large I/O, challenge generation with encrypted passwords, SPNEGO token and NTLMSSP fallback paths, and SMB2 negotiate handoff changing the packet callback and clearing SMB1 state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/negprot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/nttrans.c -->
# sources/user-network-fs/samba/source4/smb_server/smb/nttrans.c

## Purpose
Handles SMB1 NT transaction commands (`SMBnttrans` and `SMBnttranss`). It reconstructs potentially multi-packet NT transaction requests, dispatches transaction subcommands, calls NTVFS backends, marshals NT transaction replies, and fragments large replies across multiple SMB responses.

## Important APIs, Types, And Functions
- `struct nttrans_op` keeps the active transaction, backend operation object, and optional send marshaller.
- `smbsrv_reply_nttrans()` parses primary NT transaction headers, setup words, params, and data blobs.
- `smbsrv_reply_nttranss()` appends secondary params/data to a pending primary transaction.
- `reply_nttrans_complete()` wraps a reconstructed transaction in an NTVFS request and calls `nttrans_backend()`.
- `reply_nttrans_send()` runs any subcommand-specific send function, clamps output to requested max param/data sizes, and splits output into chunks.
- Subcommand parsers support `NT_TRANSACT_CREATE`, `IOCTL`, `RENAME`, `QUERY_SECURITY_DESC`, `SET_SECURITY_DESC`, and `NOTIFY_CHANGE`.
- Security descriptor paths use NDR helpers `ndr_pull_security_descriptor()` and `ndr_push_security_descriptor()`.

## Control Flow
The primary request parser validates word count, extracts max sizes, offsets, counts, setup count, and function ID, copies setup words, and range-checks params/data via `req_pull_blob()`. If totals exceed counts, `reply_nttrans_continue()` registers a `smbsrv_trans_partial` and sends an empty continue reply. Secondary packets are matched to a partial transaction, required to be contiguous by displacement, appended with `talloc_realloc()`, and discarded without a direct reply. Once totals are satisfied, the original request is completed through NTVFS. Async completion returns to `reply_nttrans_send()`, which invokes a subcommand send marshaller, builds the NT transaction response header, adds alignment padding, copies params/data, and clones the request for all but the last fragment.

## State And Persistence
Partial transaction state persists on `smb_conn->trans_partial` until complete or destroyed by `smbsrv_trans_partial_destructor()` from `trans2.c`. The primary request is retained as the owner of the partial state. Secondary packets update the primary request sequence number so the final response signs with the last secondary's sequence. Created file handles persist through the common SMB handle callback layer.

## Dependencies And Integration Points
Integrates with NTVFS operations: `ntvfs_open`, `ntvfs_qfileinfo`, `ntvfs_setfileinfo`, `ntvfs_rename`, `ntvfs_ioctl`, and `ntvfs_notify`. It shares partial transaction infrastructure and destructor with `trans2.c`, request parsing/string/blob helpers with `request.c` and `blob.c`, and handle validation with `smbsrv_pull_fnum()`.

## Risks
The secondary matching check only compares command and MID and includes a TODO to also check VUID, PID, and TID; cross-request confusion is the notable protocol-state risk. The flood limit allows more than 100 partials before rejecting, so resource pressure should be tested. Offset/count parsing is range-checked, but integer totals and realloc sizes are attack surface. `NTTRANS_CREATE` uses `MIN(fname_len+1, params.length - 53)` after a minimum-length check, so maintaining that guard is important. Notify response string sizing assumes a worst-case character multiplier and then shrinks to actual length.

## Test Signals
Exercise primary-only and secondary-completed NT transactions, non-contiguous secondary rejection, missing partial rejection, oversized response fragmentation, max-param/max-data truncation with `BUFFER_TOO_SMALL`, invalid setup counts, security descriptor NDR failures, handle validation for per-handle operations, notify-change async completion, and cancellation/connection cleanup of pending partials.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/nttrans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/receive.c -->
# sources/user-network-fs/samba/source4/smb_server/smb/receive.c

## Purpose
Provides the SMB1 receive and dispatch path for a connection. It validates NBT/SMB framing, initializes `smbsrv_request`, computes request buffer metadata, checks SMB signing, enforces session/tree requirements, dispatches commands through the SMB command table, supports AndX chaining, emits oplock breaks, and initializes SMB1 connection defaults.

## Important APIs, Types, And Functions
- `smb_messages[256]` maps SMB command bytes to names, handler functions, and flags (`NEED_SESS`, `NEED_TCON`, `SIGNING_NO_REPLY`, `AND_X`, `LARGE_REQUEST`).
- `smbsrv_recv_smb_request()` is the packet callback for SMB1 requests.
- `switch_message()` resolves tcon/session, performs authorization preconditions, adjusts special signing no-reply sequence behavior, and calls the handler.
- `smbsrv_chain_reply()` advances a single request through an AndX chain by replacing `req->in.vwv`, `req->in.data`, and related metadata.
- `smbsrv_send_oplock_break()` builds an async `SMBlockingX` oplock break packet.
- `smbsrv_init_smb_connection()` initializes max transmit values, time zone offset, NT status support, session/tcon tables, and signing state.

## Control Flow
NBT session packets with nonzero type are diverted to `smbsrv_reply_special()`. Normal packets must contain the SMB magic and enough bytes for the header. The receive path creates a request, points it into the packet buffer, reads word count/data count, handles oversized large requests for flagged commands, validates word/data bounds, sets `flags2`, initializes `request_bufinfo`, then verifies incoming signing. Dispatch performs table lookup, resolves TID and UID to `req->tcon` and `req->session`, returns command-dependent errors for missing session/tcon, and runs the handler. Chaining validates the next command offset and word/data bounds, writes the previous response's AndX continuation fields, clears per-leg NTVFS/io state, and recursively dispatches the chained command.

## State And Persistence
Active async requests are linked in `smb_conn->requests` by the NTVFS macros, and the request destructor removes them. Chained requests reuse the same request object and carry `chain_count`, `chained_fnum`, current session, and output buffer. Connection initialization persists session and tree ID allocators plus signing settings. Oplock break packets are synthetic requests with MID/PID/UID values set to wildcard-style constants.

## Dependencies And Integration Points
Dispatches into handlers implemented by `reply.c`, `negprot.c`, `search.c`, `trans2.c`, and `nttrans.c`. Uses request helpers from `request.c`, signing helpers from `signing.c`, session/tcon lookup helpers, packet termination/send infrastructure, and NTVFS oplock callbacks configured by `service.c`.

## Risks
This is a primary wire-input boundary. Bounds checks on `wct`, data size, AndX offsets, and large request sizing are critical. Missing session/tcon errors intentionally vary by command and negotiated NT-status capability, so compatibility tests matter. `SIGNING_NO_REPLY` has special behavior for `SMBntcancel`; incorrect sequence adjustment can break signing. Chaining mutates request internals and frees per-leg NTVFS/io state, so handler assumptions about lifetime are important.

## Test Signals
Cover invalid NBT/SMB headers, truncated word/data sections, large WriteX and NTTrans sizing, unsupported commands, missing session/tcon error mapping, signed and unsigned requests, `SMBntcancel` no-reply signing sequence behavior, valid and invalid AndX chains, and SMB connection initialization under different loadparm settings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/receive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/reply.c -->
# sources/user-network-fs/samba/source4/smb_server/smb/reply.c

## Purpose
Contains most SMB1 command handlers. It translates individual SMB wire commands into Samba raw/NTVFS operation unions, validates request shapes and handles, invokes backends synchronously or asynchronously, and serializes command-specific SMB replies including AndX continuations, raw reads, session setup replies, tree disconnects, logoff/exit cleanup, and NetBIOS session packets.

## Important APIs, Types, And Functions
- Generic send helpers such as `reply_simple_send()`, `reply_tcon_send()`, and per-operation async callbacks consume NTVFS results and call `smbsrv_send_reply()`.
- Tree/session functions: `smbsrv_reply_tcon`, `smbsrv_reply_tcon_and_X`, `smbsrv_reply_sesssetup`, `smbsrv_reply_sesssetup_send`, `smbsrv_reply_ulogoffX`, and `smbsrv_reply_exit`.
- File operations: open/create/temp/NTCreateX, read/readX/readbraw, write/writeX/writeclose, close/flush/seek, lock/unlock/lockingX, getattr/setattr/getattrE/setattrE, unlink, mkdir/rmdir, rename/copy.
- Print and legacy commands: `SMBsplopen`, `SMBsplwr`, `SMBsplclose`, `SMBsplretq`, `SMBreadBmpx`, `SMBwriteBmpx`, `SMBwriteBs`.
- `smbsrv_reply_ntcancel()` scans pending requests and invokes `ntvfs_cancel()`.
- `smbsrv_reply_special()` handles NBT session request and keepalive packets.

## Control Flow
Handlers follow a consistent pattern: check word count, allocate `req->io_ptr`, parse VWV/data fields with endian macros and request helpers, create an NTVFS request with `SMBSRV_SETUP_NTVFS_REQUEST`, validate file handles with `smbsrv_pull_fnum()`, then call the appropriate NTVFS backend. Async callbacks inspect backend status, build a reply with `smbsrv_setup_reply()`, push fields, and send or chain. AndX handlers set `SMB_CHAIN_NONE` placeholders and finish through `smbsrv_chain_reply()`. `readbraw` is special: it sends only an NBT header plus raw bytes and must complete synchronously. Session setup parsing is split by WCT into old, NT1, and SPNEGO variants, then delegated to `sesssetup.c`.

## State And Persistence
Successful opens create persistent SMB handles through the NTVFS handle callbacks configured on the tcon. `req->chained_fnum` lets chained operations reuse the just-opened FID. `tdis` destroys all handles under a tree and frees the tcon. `exit` destroys handles for the request PID and notifies all tcon backends. `ulogoffX` destroys all session handles, calls backend logoff, frees the session, and prevents chained reuse. NBT session request parsing stores called/calling names in negotiation state.

## Dependencies And Integration Points
Uses almost every NTVFS frontend operation: connect, open, close, read, write, lock, seek, flush, fsinfo, path/file info, mkdir, rmdir, rename, copy, ioctl, lpq, search close, exit, logoff, and cancel. Integrates with `service.c` for tree setup, `sesssetup.c` for authentication, `request.c` for buffer/string/error/send helpers, `srvtime.c` for DOS time conversion, and `receive.c` for dispatch/chaining.

## Risks
This file is broad and wire-exposed. Each handler's WCT, offset, length, and block-type validation is significant. Some legacy paths return placeholder statuses such as `NT_STATUS_FOOBAR` and `ERRuseSTD`, which are compatibility-sensitive. Raw reads bypass SMB signing and normal SMB headers by design. Chained open/NTCreateX handle propagation depends on `req->chained_fnum`. `ntcancel` matches pending requests by TID/UID/MID/PID and sends no reply. Cleanup paths have TODOs for canceling pending requests, so async operations during logoff/tree disconnect are a risk area.

## Test Signals
Test representative command families rather than every opcode only through unit tests: tree connect AndX followed by chained command, session setup variants, NTCreateX with Unicode alignment, raw read success/failure, readX/writeX large counts and 64-bit offsets, malformed data block lengths, handle/session ownership rejection, lockX large-file lock arrays, tdis/logoff/exit cleanup, print queue truncation to max transmit, NBT session request/keepalive behavior, and backend async vs sync completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/reply.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/request.c -->
# sources/user-network-fs/samba/source4/smb_server/smb/request.c

## Purpose
Implements `struct smbsrv_request` lifecycle and low-level SMB1 packet utilities: request allocation/destruction, reply buffer construction/growth, signing-aware send, error serialization, string/blob parsing and writing, bounds checking, and SMB file handle mapping.

## Important APIs, Types, And Functions
- `smbsrv_init_request()` allocates a request under the connection and installs a destructor that unlinks it from `smb_conn->requests`.
- `smbsrv_setup_reply()` and `req_setup_chain_reply()` build normal and chained reply buffers and initialize SMB headers, VWV/data pointers, flags, IDs, and BCC.
- `req_grow_data()` and `req_grow_allocation()` resize output buffers while preserving internal pointers.
- `smbsrv_send_reply()` signs and sends; `smbsrv_send_reply_nosign()` sends manually constructed or negotiation/raw packets.
- `smbsrv_setup_error()` maps NTSTATUS to NT or DOS error encoding based on negotiated support.
- `req_push_str()`, `req_append_bytes()`, `req_append_var_block()`, `req_pull_string()`, `req_pull_ascii4()`, `req_pull_blob()`, and `req_data_oob()` are the primary wire buffer helpers.
- `smbsrv_pull_fnum()`, `smbsrv_push_fnum()`, and handle callback functions map 16-bit SMB FIDs to NTVFS handles.

## Control Flow
Receive code initializes request input pointers, then calls `smbsrv_setup_bufinfo()` so string/blob helpers know the active data range and Unicode mode. Reply handlers allocate output with the needed word count and initial data size; append/grow helpers update BCC and total packet size. Sending writes the NBT length, queues the packet through `packet_send()`, and frees the request. Error sending constructs a zero-word reply and then serializes status. Handle creation is two-phase: allocate a frontend handle and NTVFS handle during backend open, then make it valid only after backend success.

## State And Persistence
Request objects are talloc-owned and usually freed after send; async NTVFS requests steal them under the tcon backend context until completion. Output pointer fields must always track reallocations. `request_bufinfo` holds per-request parsing state. Valid SMB handles persist under the tcon after `smbsrv_handle_make_valid()` steals the handle away from the request. Handle lookup enforces that the opening session matches the current request session.

## Dependencies And Integration Points
Used by all SMB1 handlers and transaction code. It depends on packet streaming, NTVFS handle callbacks, Samba charset conversion, DOS/NT status mapping, signing, and talloc memory ownership. The callback functions are registered in `service.c` during tree connection setup.

## Risks
Buffer growth uses size deltas and panics if a normal reply exceeds negotiated max transmit unless `SMBSRV_REQ_CONTROL_LARGE` is set. String conversion is complex because of Unicode alignment, null termination, explicit byte lengths, and legacy ASCII4 prefixes. `req_data_oob()` is the central defense against pointer/count wraparound. Handle lookup must preserve session isolation even though SMB permits mixed sessions and tree IDs. `smbsrv_send_reply_nosign()` is necessary for special packets but should not leak into normal signed responses.

## Test Signals
Cover Unicode and ASCII string parsing, malformed unterminated strings, ASCII4 empty behavior, blob bounds and wraparound checks, chained reply buffer growth, negotiated max transmit enforcement, NTSTATUS-to-DOS conversion, no-sign negotiation/raw responses, file handle creation/make-valid/destroy/search-by-wire-key, and cross-session FID rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/search.c -->
# sources/user-network-fs/samba/source4/smb_server/smb/search.c

## Purpose
Implements legacy SMB directory search commands (`SMBsearch`, `SMBffirst`, `SMBfunique`) and `SMBfclose`. This predates Trans2 search and uses fixed 43-byte result entries plus 21-byte resume keys.

## Important APIs, Types, And Functions
- `struct search_state` carries the active request and minimal callback state.
- `find_fill_info()` appends one 43-byte legacy search result to the output data if it fits `req_max_data()`.
- `find_callback()` adapts NTVFS search callbacks to the legacy result formatter.
- `smbsrv_reply_search()` parses first/next style requests and chooses `RAW_SEARCH_SEARCH`, `RAW_SEARCH_FFIRST`, or `RAW_SEARCH_FUNIQUE`.
- `reply_search_first_send()` and `reply_search_next_send()` write the returned entry count.
- `smbsrv_reply_fclose()` parses a resume key and calls `ntvfs_search_close()`.

## Control Flow
The search handler requires WCT 2, parses an ASCII4 pattern, then requires a type-5 variable block containing a resume key length. It prebuilds a one-word reply with an empty variable block. If resume key length is zero, it starts `ntvfs_search_first()` with search attributes and max count. If a 21-byte resume key is present, it rejects `SMBfunique`, decodes the legacy ID fields, and calls `ntvfs_search_next()`. Backend callbacks append entries until the output would exceed negotiated reply capacity. `SMBfclose` requires an empty pattern plus a 21-byte resume key and maps it to `RAW_FINDCLOSE_FCLOSE`.

## State And Persistence
Legacy search state itself is backend-owned; the frontend only serializes and returns the resume key fields supplied by NTVFS. No long-lived frontend search object is stored here. The output data grows per returned entry under the request context.

## Dependencies And Integration Points
Depends on request parsing/growth helpers, DOS time serialization from `srvtime.c`, and NTVFS search operations. It is dispatched from `receive.c` for command bytes 0x81-0x84 and coexists with Trans2 findfirst/findnext in `trans2.c`.

## Risks
The fixed legacy structures have strict sizes and weak typing. Incorrect resume key validation can desynchronize client and backend search state. Result truncation is callback-driven; count returned by the backend must match entries actually serialized. Names are copied into a 12-byte padded field, so short-name formatting and null termination behavior are compatibility-sensitive.

## Test Signals
Test search first, search next with a valid 21-byte key, invalid block type, invalid key lengths, `SMBfunique` with resume key rejection, max transmit truncation, empty pattern requirements for fclose, and backend errors in async callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/search.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/service.c -->
# sources/user-network-fs/samba/source4/smb_server/smb/service.c

## Purpose
Builds SMB1 tree connections. It resolves a requested share, checks access and device type, creates `smbsrv_tcon`, initializes the selected NTVFS backend, and installs frontend callbacks for oplock breaks and handle management.

## Important APIs, Types, And Functions
- `smbsrv_tcon_backend()` is called by `reply.c` for `SMBtcon` and `SMBtconX`.
- `make_connection()` normalizes `\\SERVER\SHARE` paths, resolves `share_config`, checks hosts allow/deny, determines `NTVFS_DISK`, `NTVFS_IPC`, or `NTVFS_PRINT`, and validates client device strings.
- `make_connection_scfg()` allocates the tcon, derives NTVFS client capability flags, calls `ntvfs_init_connection()`, and registers oplock, address, and handle callbacks.

## Control Flow
For old `SMBtcon`, the caller passes service/password/device strings and receives `max_xmit` plus TID. For `SMBtconX`, the caller passes path/password/device blob fields and receives TID plus share options such as search bits, CSC policy, and DFS-root indication. On backend initialization failure, the partially created tcon is freed and `req->tcon` is cleared.

## State And Persistence
A successful tree connect creates a persistent `smbsrv_tcon` under the connection. The tcon owns its NTVFS context and later owns valid frontend file handles. Per-share type, share config, local/remote addresses, server ID, event context, message context, protocol level, and client capability bits are transferred into NTVFS initialization.

## Dependencies And Integration Points
Depends on Samba share configuration, socket access checks, loadparm, NTVFS initialization, and callback functions from `receive.c` and `request.c`. It is the bridge that lets later file operations in `reply.c`, `search.c`, `trans2.c`, and `nttrans.c` call the correct backend.

## Risks
The TODO for share-level password checking means share security semantics depend on higher layers or are incomplete in this path. Device type matching is compatibility-sensitive (`?????` wildcard vs `A:`, `IPC`, `LPT:`). Failure handling must not leave a half-valid tcon in `req->tcon`. DFS option bits are only advertised when both share and global DFS settings allow it.

## Test Signals
Cover disk/IPC/printer share type mapping, `\\server\share` normalization, missing share returning `BAD_NETWORK_NAME`, hosts allow/deny rejection, wrong device type rejection, level-II oplock capability propagation, NTVFS initialization failure cleanup, callback registration, and DFS/CSC option bits in `tconX` replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/sesssetup.c -->
# sources/user-network-fs/samba/source4/smb_server/smb/sesssetup.c

## Purpose
Implements backend authentication and authorization for SMB1 session setup variants. It handles legacy LM response, NT1 bare NTLM response, and SPNEGO/GENSEC exchanges, creates SMB session objects, logs successful non-SPNEGO authz events, derives session info, and enables SMB signing after authentication.

## Important APIs, Types, And Functions
- `smbsrv_sesssetup_backend()` dispatches `RAW_SESSSETUP_OLD`, `RAW_SESSSETUP_NT1`, and `RAW_SESSSETUP_SPNEGO`.
- `sesssetup_old()` and `sesssetup_nt1()` build `auth_usersupplied_info` and call `auth_check_password_send()`.
- `sesssetup_old_send()` and `sesssetup_nt1_send()` receive auth results, generate `auth_session_info`, allocate `smbsrv_session`, mark setup complete, and set the VUID.
- `sesssetup_spnego()` starts or resumes a GENSEC context and disables packet receive while async auth is in flight.
- `sesssetup_spnego_send()` consumes GENSEC output, obtains session info and session key, and finalizes the SMB session.
- `smbsrv_not_spengo_sesssetup_authz_log()` logs successful bare-NTLM authorization events.

## Control Flow
The parser in `reply.c` fills a `union smb_sesssetup`; this file handles authentication. Old and NT1 flows gather remote/local socket addresses, workstation name, account/domain, and password response blobs, then submit an async auth check. On success they generate session info, create a frontend session, log authz, mark the session valid for normal use, set `req->session` for possible AndX tree connect, and return through `smbsrv_reply_sesssetup_send()`. NT1 also configures signing using the session key and NT response. SPNEGO creates a temporary session with a GENSEC context on first leg, updates it with the input token, returns `MORE_PROCESSING_REQUIRED` as needed, and finalizes when GENSEC completes.

## State And Persistence
Successful session setup sets `smb_conn->negotiate.done_sesssetup`, reparents the session to the connection, stores `session_info` on the session, and may establish the connection signing key. In-progress SPNEGO sessions are lookupable by VUID before final session info exists. Packet receive is disabled during async SPNEGO processing and re-enabled in the callback.

## Dependencies And Integration Points
Depends on auth4, GENSEC, tsocket address APIs, packet receive control, loadparm raw NTLMv2 policy, and session helpers. It consumes negotiation state prepared by `negprot.c`, especially challenge/auth context and selected GENSEC OID, and returns serialized responses through `reply.c`.

## Risks
This is a security-critical path. Raw NTLMv2 is rejected unless `raw_ntlmv2_auth` allows it, while SPNEGO is preferred when negotiated. The old-style path appears to pass `req->smb_conn->negotiate.auth_context` to `auth_check_password_send()` even when a local `state->auth_context` was created, which is worth regression attention. SPNEGO packet receive suppression prevents EOF/reentrancy crashes but must always re-enable. Partial SPNEGO sessions must be freed on terminal failure.

## Test Signals
Test successful and failed old/NT1 auth, anonymous or missing server credentials fallback, raw NTLMv2 rejection policy, signing setup after NT1 and SPNEGO, SPNEGO multi-leg `MORE_PROCESSING_REQUIRED`, invalid VUID continuation, logoff of partially authenticated sessions, socket address failures, packet receive disable/enable balance, and AndX tree connect immediately after session setup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/sesssetup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/signing.c -->
# sources/user-network-fs/samba/source4/smb_server/smb/signing.c

## Purpose
Provides SMB1 signing setup, incoming signature validation, outgoing signature generation, and sequence-number bookkeeping for normal replies and no-reply commands.

## Important APIs, Types, And Functions
- `smbsrv_init_signing()` initializes the signing blob, turns signing off, and reads server signing policy via `lpcfg_server_signing_allowed()`.
- `smbsrv_setup_signing()` installs the signing key after authentication using `set_smb_signing_common()` and `smbcli_simple_set_signing()`.
- `smbsrv_signing_check_incoming()` allocates a sequence number and verifies signed incoming packets.
- `smbsrv_sign_packet()` signs outgoing replies or emits the legacy `BSRSPYL ` marker mode.
- `smbsrv_signing_no_reply()` adjusts sequence numbers for commands that consume a request but do not send a reply.

## Control Flow
Every normal SMB1 packet passes through `smbsrv_signing_check_incoming()` in `receive.c`. That assigns `req->seq_num` from `next_seq_num` and increments the connection sequence by two when signing is active. If signing is off, validation succeeds. If signing is on, the function checks the packet is long enough to contain the signature field, validates the MAC using the current key and request sequence, and updates signing-good state. Before normal send, `smbsrv_send_reply()` calls `smbsrv_sign_packet()`, which signs with `req->seq_num + 1`.

## State And Persistence
All persistent signing state lives on `smb_conn->signing`: `mac_key`, engine state, mandatory/allowed flags, and `next_seq_num`. Per-request state is only `seq_num`. Session setup is responsible for moving the connection from off to active signing after authentication.

## Dependencies And Integration Points
Uses raw SMB client signing helpers from `libcli/raw`. Integrated by `receive.c` for validation/no-reply adjustment, `request.c` for outgoing signing, `negprot.c` for advertising signing policy, and `sesssetup.c` for installing the authenticated session key.

## Risks
Sequence numbers are easy to desynchronize around no-reply commands, multi-packet transactions, and secondary transaction requests. `SMB_SIGNING_ENGINE_BSRSPYL` intentionally writes a fixed marker instead of a normal signature. Incoming packets shorter than the security signature field fail when signing is active. Signing setup must be called only after a valid session key exists.

## Test Signals
Cover unsigned connections, mandatory signing negotiation through auth, valid and invalid signed packet MACs, short signed packets, outgoing signature sequence `seq_num + 1`, `SMBntcancel`/no-reply sequence adjustment, and multi-packet transaction secondary sequence handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/signing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/srvtime.c -->
# sources/user-network-fs/samba/source4/smb_server/smb/srvtime.c

## Purpose
Wraps DOS time serialization and parsing helpers so SMB1 command handlers consistently apply the negotiated server time-zone offset stored on the connection.

## Important APIs, Types, And Functions
- `srv_push_dos_date()` writes time/date format with `push_dos_date()`.
- `srv_push_dos_date2()` writes date/time word-reversed format with `push_dos_date2()`.
- `srv_push_dos_date3()` writes the 32-bit "unix-like" DOS format with `push_dos_date3()`.
- `srv_pull_dos_date()`, `srv_pull_dos_date2()`, and `srv_pull_dos_date3()` parse the corresponding formats back to GMT `time_t`.

## Control Flow
Handlers pass the active `smbsrv_connection`, destination/source buffer, offset, and Unix timestamp. These wrappers do not branch beyond selecting the underlying format; they simply pass `smb_server->negotiate.zone_offset`.

## State And Persistence
No state is stored here. The only state consumed is `smb_conn->negotiate.zone_offset`, initialized in `smbsrv_init_smb_connection()` and used throughout the lifetime of the connection.

## Dependencies And Integration Points
Used by negotiation, legacy file info replies, open/read/write metadata handlers, print queue serialization, and Trans2 file/fs info conversions. It depends on the lower-level time helpers declared through Samba includes and on `smb_server.h` for the connection type.

## Risks
The risk is semantic rather than structural: SMB1 legacy time fields are local-time encoded, so using the wrong wrapper or offset shifts file timestamps. DST and zone offset behavior should remain aligned with the lower-level `push_dos_*`/`pull_dos_*` helpers. Because this file is tiny, regressions usually come from call-site misuse.

## Test Signals
Test round trips for all three DOS date formats using nonzero time-zone offsets, timestamps around DST transitions if supported by the lower-level helpers, and representative call sites such as negotiate, getatr, open, setattr, and print queue entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/srvtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/trans2.c -->
# sources/user-network-fs/samba/source4/smb_server/smb/trans2.c

## Purpose
Implements SMB1 `SMBtrans`, `SMBtranss`, `SMBtrans2`, and `SMBtranss2` handling. It reconstructs multi-packet transaction requests, passes named `SMBtrans` calls to NTVFS, implements Trans2 subcommands for filesystem/file info, open, mkdir, directory search, set info, and DFS referrals, marshals replies, and fragments large transaction responses.

## Important APIs, Types, And Functions
- `struct trans_op` stores request, transaction, command, backend object, and optional send marshaller.
- `reply_trans_generic()` parses primary transaction requests; `reply_transs_generic()` appends secondary chunks.
- `reply_trans_complete()` dispatches either `ntvfs_trans()` or `trans2_backend()`.
- `reply_trans_send()` serializes and fragments transaction replies.
- `trans2_backend()` first offers direct passthrough via `ntvfs_trans2()`, then handles specific setup subcommands.
- File/fs info helpers: `trans2_push_fsinfo()`, `trans2_push_fileinfo()`, `trans2_parse_sfileinfo()`.
- Search helpers: `struct find_state`, `find_fill_info()`, `trans2_findfirst()`, `trans2_findnext()`.
- `trans2_getdfsreferral()` implements DFS referral lookup and NDR marshaling.
- `smbsrv_trans_partial_destructor()` removes partial transaction records from the connection list.

## Control Flow
Primary transaction parsing validates WCT, totals, max sizes, setup count, setup words, optional transaction name, and param/data blobs. Incomplete requests are stored on `smb_conn->trans_partial` and receive an empty continue response. Secondary requests are matched by command and MID, required to be contiguous by displacement, appended to the primary blobs, and freed without reply. On completion, an NTVFS request is created. Trans2 dispatch handles direct backend implementation first; otherwise setup word zero selects DFS referral, findfirst/findnext, qpath/qfile info, setfile/setpath info, qfsinfo, open, or mkdir. Async completion marshals params/data, applies status if needed, and chunks according to negotiated max transmit with SMB transaction alignment padding.

## State And Persistence
Partial transactions persist under the primary request until complete. Secondary packets update the primary request signing sequence. Directory search handles are backend state; the frontend keeps only per-call callback state and last-entry offsets for resume reporting. DFS referral processing opens SAM DB context transiently. Open and mkdir operations may create persistent backend/file state via NTVFS.

## Dependencies And Integration Points
Depends on NTVFS, raw protocol structures, SMB blob helpers, EA parsing/writing, passthrough info/search marshaling in `blob.c`, DFS NDR generated code, SAM DB, auth system session, loadparm DFS settings, and request/signing infrastructure. It shares partial-transaction storage with `nttrans.c`.

## Risks
Like NTTrans, secondary matching only checks command and MID and has a TODO for VUID/PID/TID. Transaction totals are 16-bit in Trans2, but realloc and copy paths still need malformed-length coverage. `trans2_getdfsreferral()` can produce large blobs and has logic to trim referrals only in the 56 KiB max-response case. File-info level mapping accepts many passthrough levels while explicitly rejecting unsupported Unix and special levels; level regressions are common compatibility risks. Search callback truncates by rolling back the last entry when output exceeds `max_data`, so counts and last offsets must match serialized data.

## Test Signals
Cover primary-only and secondary transaction assembly, non-contiguous secondary rejection, partial flood limit, response fragmentation and alignment, direct `ntvfs_trans2()` passthrough, each implemented Trans2 subcommand, EA list parsing and output, unsupported info levels, DFS referral disabled/enabled/oversized behavior, findfirst/findnext truncation at `max_data`, setfile rename/disposition/allocation/EOF parsing, and signing sequence across secondary completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/trans2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/wscript_build -->
# sources/user-network-fs/samba/source4/smb_server/smb/wscript_build

## Purpose
Defines the Waf build subsystem for the SMB1 protocol implementation under `source4/smb_server/smb`. It collects the C files in this directory into the `SMB_PROTOCOL` subsystem, declares generated prototypes, and gates the subsystem on the NTVFS file server build option.

## Important APIs, Types, And Functions
- `bld.SAMBA_SUBSYSTEM('SMB_PROTOCOL', ...)` is the only build declaration.
- `source=` lists `receive.c`, `negprot.c`, `nttrans.c`, `reply.c`, `request.c`, `search.c`, `service.c`, `sesssetup.c`, `srvtime.c`, `trans2.c`, and `signing.c`.
- `autoproto='smb_proto.h'` requests automatic prototype generation for the subsystem.
- `deps='dfs_server_ad'` and `public_deps='ntvfs LIBPACKET samba-credentials samba_server_gensec'` encode internal and public link dependencies.
- `enabled=bld.CONFIG_SET('WITH_NTVFS_FILESERVER')` builds the subsystem only when the NTVFS file server is enabled.

## Control Flow
There is no runtime control flow. At build configuration time Waf evaluates `WITH_NTVFS_FILESERVER`; if true, it compiles the listed source files as `SMB_PROTOCOL` and exposes their generated prototypes.

## State And Persistence
No runtime state. Build state includes the subsystem membership and dependency graph. Changes here affect which source files participate in generated prototypes and linking.

## Dependencies And Integration Points
Integrates the SMB1 frontend with NTVFS, packet streaming, credentials, GENSEC, and DFS referral support. The generated `smb_proto.h` is included by `smb_server.h`, making functions visible across the source files in this subsystem.

## Risks
Forgetting to add a new source file here would produce missing symbols or missing prototypes. Removing a dependency can create link or configuration-only failures. Because `trans2.c` depends on DFS AD support, the explicit `dfs_server_ad` dependency is significant. The entire SMB1 protocol frontend disappears when `WITH_NTVFS_FILESERVER` is disabled, so packaging/tests must account for that configuration.

## Test Signals
Build with `WITH_NTVFS_FILESERVER` enabled and disabled, verify `smb_proto.h` generation, and run link checks for references to NTVFS, packet, credentials, GENSEC, and DFS referral symbols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/fileinfo.c -->
# sources/user-network-fs/samba/source4/smb_server/smb2/fileinfo.c

## Purpose
Implements SMB2 GETINFO and SETINFO request handling for file, filesystem, and security information. It maps SMB2 info classes to Samba raw/passthrough levels, calls NTVFS backends, marshals output blobs, parses input blobs, validates handles, and serializes SMB2 replies/errors.

## Important APIs, Types, And Functions
- `struct smb2srv_getinfo_op` and `struct smb2srv_setinfo_op` carry request-local operation state.
- `smb2srv_getinfo_recv()` parses SMB2 GETINFO body fields, pulls input buffer, resolves the file handle, and dispatches to `smb2srv_getinfo_backend()`.
- `smb2srv_getinfo_file()`, `smb2srv_getinfo_fs()`, and `smb2srv_getinfo_security()` map info type/class to NTVFS qfileinfo/fsinfo/security calls.
- `smb2srv_getinfo_send()` remaps `NT_STATUS_INVALID_LEVEL` to `NT_STATUS_INVALID_INFO_CLASS`, marshals output, checks output buffer length, and sends the response blob.
- `smb2srv_setinfo_recv()` parses SMB2 SETINFO body fields and dispatches to `smb2srv_setinfo_backend()`.
- `smb2srv_setinfo_file()`, `smb2srv_setinfo_fs()`, and `smb2srv_setinfo_security()` parse input and call NTVFS setfileinfo or return SMB2-specific status.

## Control Flow
GETINFO checks the fixed body size, allocates both the public `smb2_getinfo` and private operation state, creates an NTVFS request, reads info type/class, output length, additional information, flags, handle, and input buffer. File info handles SMB2 all-EAs and all-information specially; other file and filesystem classes map to raw level `class + 1000`. Security info class 0 uses NDR to push a security descriptor. On completion, the output blob must fit the requested output buffer or `INFO_LENGTH_MISMATCH` is returned. SETINFO similarly parses level, blob, flags, and handle. File levels map to passthrough setfileinfo, with SMB2 rename using a distinct raw level; filesystem setinfo mostly denies or rejects; security class 0 pulls an NDR security descriptor and calls `ntvfs_setfileinfo()`.

## State And Persistence
No state persists beyond the request except whatever the NTVFS backend changes: file metadata, filesystem metadata if ever implemented, delete-on-close, rename, allocation/EOF, security descriptors, etc. The request holds output/input blobs and operation state until async completion.

## Dependencies And Integration Points
Uses SMB2 server request helpers, SMB2 blob offset/length helpers, NTVFS, passthrough marshaling/parsing from `blob.c`, and NDR security descriptor routines. It shares the same backend raw information model as SMB1 Trans2/NTTrans.

## Risks
SMB2 status mapping differs from SMB1; preserving `INVALID_INFO_CLASS` behavior is important. Output buffer length is enforced after backend marshaling, so large metadata paths must return `INFO_LENGTH_MISMATCH` cleanly. The TODO in filesystem GETINFO notes qfsinfo should be limited to the share root directory handle. SETINFO filesystem classes are deliberately denied/not implemented for selected levels. Rename parsing differs between SMB1 and SMB2 because SMB2 uses an 8-byte root FID field in the blob.

## Test Signals
Test GETINFO file passthrough levels, SMB2 all-EAs/all-information, filesystem info levels, security descriptor query, output buffer too small, invalid info type/class mapping, SETINFO basic/disposition/allocation/EOF/rename paths, security descriptor set, unsupported quota, denied filesystem set classes, invalid handles, and async backend completion status translation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/smb2/fileinfo.c -->
