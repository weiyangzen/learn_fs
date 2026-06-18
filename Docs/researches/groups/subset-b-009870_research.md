# subset-b-009870 research

Grouped research for Samba SMB1 named-pipe reply helpers and SMB1 request-processing entry points. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_pipes.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_pipes.c

## Purpose
`smb1_pipes.c` implements SMB1 named-pipe reply routines for the smbd server. It handles opening IPC named pipes via `SMBopenX` pipe paths and adapts SMB1 pipe read/write commands into the asynchronous named-pipe server API used for RPC-over-SMB.

## Important APIs, types, and functions
- `reply_open_pipe_and_X(connection_struct *conn, struct smb_request *req)` parses an incoming `\PIPE\...` name, validates the pipe namespace, opens the pipe with `open_np_file()`, and formats the SMB1 OpenAndX response for a message-mode named pipe.
- `reply_pipe_write_and_X(struct smb_request *req)` handles `SMBwriteX` requests directed at named pipes, including the `PIPE_START_MESSAGE | PIPE_RAW_MODE` quirk where the first two client bytes are treated as an untrusted PDU-length field and skipped.
- `pipe_write_andx_done()` receives the async `np_write_send()` result, verifies the full payload was written, builds the WriteAndX reply, and completes the request with `smb_request_done()`.
- `reply_pipe_read_and_X(struct smb_request *req)` builds a read reply buffer up front, detaches `req->outbuf` to mark the SMB request async, and starts `np_read_send()` into the SMB output data area.
- `pipe_read_andx_done()` maps named-pipe status via `nt_status_np_pipe()`, restores the detached output buffer, sizes the SMB response, and fills the read count and data offset.
- `reply_pipe_write(struct smb_request *req)` and `pipe_write_done()` provide the older non-AndX write path, using `np_write_send()` and then sending directly through `smb1_srv_send()`.
- Small state structs (`pipe_write_andx_state`, `pipe_read_andx_state`, `pipe_write_state`) keep request-local async metadata under `req->async_priv`.

## Control flow
The open path pulls the pipe name from the request byte buffer with `srvstr_pull_req_talloc()`, strips leading backslashes, requires the `PIPE\` prefix, and passes the remaining pipe endpoint name to `open_np_file()`. A missing pipe maps to the DOS `ERRbadpipe` compatibility error, while other open failures return the NT status. Success creates a 15-word OpenAndX reply, marks the object as an existing message-mode named pipe, and returns the new file number.

The write paths validate that the FID resolves to a named-pipe `files_struct` and that the file was opened by the same VUID as the request. They allocate per-request state, locate the client payload in the SMB request, and start an async named-pipe write against `fsp->fake_file_handle`. Completion callbacks own the suspended `smb_request` after `talloc_move(req->conn, &req)`. The AndX callback uses `smb_request_done()` so the request can participate in normal chained-response handling; the legacy write callback calls `smb1_srv_send()` itself and frees the request.

The read path similarly validates the pipe handle and VUID, allocates the maximum-sized SMB output buffer immediately, and passes the final data area to `np_read_send()`. Detaching `req->outbuf` is the signal to higher SMB1 processing that the request has suspended. The callback restores and resizes the output buffer once the named-pipe server returns data.

## State and persistence behavior
This file does not persist state outside the live smbd connection. It mutates transient request state (`req->async_priv`, `req->outbuf`, request ownership), uses the open file table via `file_fsp()`, and operates on the named-pipe fake file handle stored in `files_struct`. Opened named pipes persist only as smbd file handles and underlying RPC pipe state managed by the named-pipe server layer.

## Dependencies and integration points
The file depends on core smbd request/buffer helpers, `files_struct` handle lookup, Samba's `talloc` ownership model, `tevent_req` async callbacks, SMB1 wire helpers (`SSVAL`, `SVAL`, `smb_buf`, `reply_smb1_outbuf`), named-pipe helpers from `rpc_server/srv_pipe_hnd.h`, and pipe status mapping from DCERPC support. It is called from SMB1 reply dispatch for pipe-specific `openX`, `readX`, and `write` handling, and it calls back into `smb_request_done()`/`smb1_srv_send()` from `smb1_process.c` to ship replies.

## Risks and edge cases
- Pointer-derived payload locations (`smb_doff`, `req->buf + 3`) trust earlier SMB request validation; malformed offsets are dangerous if upstream bounds checks regress.
- The `PIPE_START_MESSAGE | PIPE_RAW_MODE` path subtracts two bytes only after checking length; this is important for underflow and protocol-compatibility behavior.
- Async ownership is delicate: AndX callbacks rely on `smb_request_done()` after moving `req` under the connection, while the legacy callback sends and frees manually.
- Write completion treats partial writes as errors, including a legacy `ACCESS_DENIED` mapping that comments already question.
- The read path allocates `smb_maxcnt + 1` bytes in the output buffer before async completion, so maximum-count validation in request parsing matters.
- The disabled `STATUS_BUFFER_OVERFLOW` branch notes unresolved interaction with chained error fixups; changing this may affect clients that expect more-data signaling.

## Test signals
Relevant signals are SMB1/IPC integration tests that open `\\PIPE\\...`, issue RPC traffic over `SMBwrite`, `SMBwriteX`, and `SMBreadX`, and exercise chained AndX behavior. Regression coverage should include invalid pipe names, wrong VUID handles, short raw-message writes, partial named-pipe write failures, read responses with outstanding pipe data, and encrypted/signed connections where the final send path is owned by `smb1_process.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_pipes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_pipes.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_pipes.h

## Purpose
`smb1_pipes.h` declares the SMB1 named-pipe reply routines implemented in `smb1_pipes.c`. It is the narrow interface by which the broader SMB1 reply/dispatch code invokes pipe-specific open, read, and write handlers.

## Important APIs, types, and functions
- `reply_open_pipe_and_X(connection_struct *conn, struct smb_request *req)` opens a named pipe from an OpenAndX request and formats the pipe-specific OpenAndX response.
- `reply_pipe_write_and_X(struct smb_request *req)` handles async AndX pipe writes.
- `reply_pipe_read_and_X(struct smb_request *req)` handles async AndX pipe reads.
- `reply_pipe_write(struct smb_request *req)` handles the older non-AndX SMB pipe write form.

## Control flow
This header has no executable control flow. Its prototypes allow SMB1 reply code to dispatch pipe operations without exposing the callback state structs or helper functions used internally by `smb1_pipes.c`.

## State and persistence behavior
The header defines no state. State is carried through `connection_struct`, `struct smb_request`, `files_struct`, and named-pipe handles owned by the implementation and surrounding smbd subsystems.

## Dependencies and integration points
The declarations depend on Samba's smbd types being visible to includers, especially `connection_struct` and `struct smb_request`. The main integration point is SMB1 command dispatch in files such as `smb1_reply.c`, which detects IPC named-pipe operations and calls these functions. Completion is integrated with `smb_request_done()` and `smb1_srv_send()` declared from the SMB1 processing layer.

## Risks and edge cases
- There are no include guards or local includes in this header fragment; it relies on the existing Samba include discipline.
- The interface exposes only request-level entry points, so callers must already have parsed enough SMB state to choose the pipe path correctly.
- Since the functions may suspend requests asynchronously, callers must honor the `req->outbuf == NULL` convention used by SMB1 processing.

## Test signals
Header-level test signals are compile/link coverage: all pipe reply callers should build with the declared signatures. Behavioral tests belong to `smb1_pipes.c` and should verify that these entry points interoperate with SMB1 command dispatch, chained request completion, and named-pipe RPC traffic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_pipes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_process.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_process.c

## Purpose
`smb1_process.c` is the central SMB1 packet-processing loop for smbd. It receives and validates SMB1 packets, verifies signing and encryption, dispatches commands through the SMB1 command table, manages AndX chaining, sends responses, queues deferred opens, limits outstanding transaction state, sends keepalives, and optionally runs a forked SMB echo handler that can answer one-reply echo probes while forwarding non-echo traffic to the parent smbd.

## Important APIs, types, and functions
- `struct pending_message_list` stores deferred SMB1 open requests, including original request time, connection pointers, sequence number, encryption flag, copied input buffer, and optional deferred-open metadata.
- `smbd_echo_init()`, `smbd_lock_socket()`, and `smbd_unlock_socket()` initialize and coordinate the optional async echo handler's cross-process socket lock, using a robust process-shared mutex when available or an fcntl lock file otherwise.
- `smb1_srv_send()` signs, optionally encrypts, and writes an SMB1 response to the transport socket while holding the echo-handler socket lock.
- `receive_smb_raw_talloc()`, `receive_smb_raw_talloc_partial_read()`, and `smb1_receive_talloc()` read SMB1 packets, implement the large WriteAndX partial-read optimization, decrypt encrypted packets, and verify SMB1 signatures.
- `push_deferred_open_message_smb1()` and `push_queued_message()` copy a request into `sconn->deferred_open_queue` for later processing.
- `allow_new_trans()` rejects duplicate transaction MIDs and caps pending transaction requests to reduce memory-DoS exposure.
- `smb_messages[256]` maps SMB command bytes to names, reply handlers, and dispatch flags such as `AS_USER`, `NEED_WRITE`, `CAN_IPC`, `AS_GUEST`, and `DO_CHDIR`.
- `switch_message()` validates negotiation/session/tree context, changes process credentials/service directory, enforces write/IPC/encryption requirements, updates session/tcon crypto flags for smbstatus, and invokes the selected reply function.
- `construct_reply()`, `construct_reply_chain()`, `smb_request_done()`, and `process_smb1()` build request objects, handle normal versus AndX-chained dispatch, splice chained responses, and ship final replies.
- `smb1_is_chain()`, `smb1_walk_chain()`, `smb1_chain_length()`, and `smb1_parse_chain()` inspect and materialize SMB1 AndX request chains with strict offset and length validation.
- `smbd_smb1_server_connection_read_handler()` is the event-loop read entry point for SMB1 sockets and the echo-handler trusted pipe.
- `keepalive_fn()` sends SMB1 NetBIOS keepalives for non-SMB2 connections.
- `fork_echo_handler()` and its helpers (`smbd_echo_read_send()`, `smbd_echo_reply()`, `smbd_echo_loop()`, `smbd_echo_got_packet()`) implement the optional forked echo responder and forwarding channel.
- `req_is_in_chain()` reports whether a request is an AndX chain member or the head of a still-chained packet.

## Control flow
Incoming SMB1 I/O enters through `smbd_smb1_server_connection_read_handler()`. When async echo handling is enabled, it prefers packets already forwarded by the echo child and locks the socket when reading directly from the client so parent and child do not race. It calls `receive_smb_talloc()` with trusted-channel awareness; in this source tree that resolves to the SMB1 receive implementation, which reads the NetBIOS length, optionally performs a partial large-WriteAndX read, decrypts packets, and verifies signing. Successful packets are passed to `process_smb()`, which reaches `process_smb1()`.

`process_smb1()` rejects short or invalid SMB headers, with a guarded test-only suicide packet escape, then chooses chained or unchained construction. `construct_reply()` allocates a single `smb_request`, initializes it, and calls `switch_message()`. `construct_reply_chain()` parses all AndX members into linked request objects, dispatches the first, and relies on `smb_request_done()` to continue through the rest of the chain.

`switch_message()` is the dispatch gate. Before negotiation completes, only `SMBnegprot` and legacy mailslot messenger commands are allowed. Unknown or unimplemented commands get `reply_unknown_new()`. Implemented commands are run under the user, guest, or root context implied by the dispatch flags. For user commands it requires a valid tree connection, sets case-sensitivity policy from the service and client flags, calls `change_to_user_and_service()`, enforces write permissions and IPC restrictions, and checks service encryption requirements. It also updates session and tree encryption/signing status flags, persisting those global records when needed, then invokes the command handler from `smb_messages`.

`smb_request_done()` is both the normal response shipper and the continuation mechanism for AndX chains. For chained requests it finds the completed request, dispatches later chain members while earlier responses are successful, propagates UID/TID and `chain_fsp`, then appends each subresponse with `smb_splice_chain()`. It finally copies the last response's UID/TID/error-code style/error values to the first response, fixes the SMB length, signs/encrypts as needed, sends with `smb1_srv_send()`, and frees either the single request or the request array.

The chain parser walks the initial command and each AndX link using offsets from the SMB header. It rejects non-growing offsets, offsets beyond the total packet, too-short word arrays, and byte counts that would exceed the packet. Response splicing performs the inverse operation, aligning appended word-count fields to a 4-byte boundary and specially fixing ReadAndX data offsets after appending.

When the optional echo handler is forked after negotiation, the child waits for client readability, gives the parent one second to handle the packet, then locks the shared socket and reads if the parent did not. One-reply `SMBecho` probes are answered directly by the child. Any other SMB packet has its sequence number placed into the SMB security-signature field and is forwarded over a pipe to the parent, where the parent read handler treats the pipe as a trusted channel.

## State and persistence behavior
Persistent protocol state is held outside this file in `smbXsrv_connection`, sessions, tree connections, open files, signing/encryption contexts, and the smbd server connection. This file mutates that state by updating session/tcon crypto flags, connection encryption requirements, per-connection operation counts, deferred-open queues, echo-handler descriptors, echo-handler shared lock state, and transport status-dependent I/O behavior.

Most allocations are request-scoped with `talloc`; async handlers signal suspension by clearing `req->outbuf` and later call `smb_request_done()`. Deferred opens copy the full input buffer into a `pending_message_list` so processing can resume after oplock/share-mode conditions change. The echo handler adds process-level state: a child process, a parent pipe, a trusted event fd, a socket lock fd or process-shared mutex, pending `iovec` writes to the parent, and a ref-counted lock protocol to support nested send/read sections.

## Dependencies and integration points
This file is integrated with nearly every SMB1 smbd subsystem: session and tree lookup/update (`smbXsrv_session`, `smbXsrv_tcon`), signing and encryption (`smb1_srv_check_sign_mac`, `smb1_srv_calculate_sign_mac`, `srv_encrypt_buffer`, `srv_decrypt_buffer`), transport I/O helpers, command reply implementations from the SMB1 reply/transaction/printing/IPC code, loadparm configuration, credential switching, message/CTDB support, deferred open records, profiling/debug dump hooks, and the tevent async framework.

Other files call the exported functions declared in `smb1_process.h`: SMB2 receive glue delegates SMB1 packet receive handling to `smb1_receive_talloc()` in mixed negotiation paths; SMB1 transaction implementations use `allow_new_trans()`; negotiation starts `fork_echo_handler()` when async echo is configured; event-loop code calls `smbd_smb1_server_connection_read_handler()`; named-pipe callbacks call `smb_request_done()` or `smb1_srv_send()`.

## Risks and edge cases
- Packet length, AndX offset, and byte-count validation are security-critical because this file parses untrusted network input and performs pointer arithmetic into request buffers.
- The large WriteAndX partial-read optimization intentionally drains unread payload and spoofs a shorter SMB buffer; regressions can corrupt subsequent packet framing or break zero-copy write paths.
- Signing/encryption sequencing depends on correct sequence numbers, trusted-channel handling for echo-forwarded packets, and consistent final send encryption decisions.
- `switch_message()` combines authentication, service chdir, IPC restrictions, write checks, encryption policy, and dispatch; small flag mistakes in `smb_messages` can expose commands under the wrong credentials or tree type.
- AndX chaining across async handlers is fragile: suspended requests must preserve the request array, `chain_fsp`, input buffer ownership, and response-success state until `smb_request_done()` resumes.
- `smb_splice_chain()` has to maintain 16-bit response-size constraints except for WriteX and has a special ReadAndX offset fixup that is easy to break.
- The echo handler uses fork, shared locks, pipes, event fds, and direct SMB replies from a child process; lock leaks or incorrect trusted-channel decisions can race socket reads, duplicate replies, or desynchronize signing state.
- `allow_new_trans()` caps only after `count > 5`, allowing six existing entries before rejecting the next request; callers should understand that exact threshold.
- Debug packet dumping writes to `/tmp` at high debug levels, so it is useful for diagnosis but sensitive in production due to packet contents.

## Test signals
Strong signals include Samba selftests that exercise SMB1 negotiation, session setup, tree connect, signed/encrypted SMB1 traffic, IPC and transaction commands, deferred open behavior, AndX command chains, large WriteAndX requests, invalid malformed chains, and async echo handling. `source3/torture/vfstest_chain.c` directly references `smb1_parse_chain()` with canned chain data. Useful targeted tests would fuzz `smb1_walk_chain()` offsets/lengths, assert `smb_request_done()` chained error propagation, verify `allow_new_trans()` duplicate and limit behavior, and run echo-handler tests with signing enabled and disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_process.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_process.h

## Purpose
`smb1_process.h` declares the exported SMB1 processing functions shared across smbd. It exposes packet receive/send helpers, AndX chain parsing utilities, request completion, transaction throttling, echo-handler setup, deferred-open requeueing, keepalive handling, and the main SMB1 processing entry points.

## Important APIs, types, and functions
- `smb1_srv_send()` sends an SMB1 response buffer with optional signing and encryption.
- `allow_new_trans()` validates that a new transaction MID is not duplicated and that pending transaction state remains bounded.
- `smb_request_done()` completes a request, including chained-request continuation and final response send.
- `smb_fn_name()`, `add_to_common_flags2()`, and `remove_from_common_flags2()` expose command-name and shared FLAGS2 helpers.
- `smb1_is_chain()`, `smb1_walk_chain()`, `smb1_chain_length()`, and `smb1_parse_chain()` expose SMB1 AndX chain inspection and request materialization.
- `req_is_in_chain()` reports whether a request belongs to an AndX chain.
- `fork_echo_handler()` and `smbd_echo_init()` manage the optional forked echo responder.
- `smb1_receive_talloc()` reads, decrypts, and verifies an SMB1 packet into a talloc buffer.
- `push_deferred_open_message_smb1()` queues a request for later deferred-open processing.
- `process_smb1()`, `construct_reply()`, `smbd_smb1_server_connection_read_handler()`, and `keepalive_fn()` expose the core packet-processing and event-loop hooks.

## Control flow
The header has no executable control flow, but its declarations mirror the principal SMB1 lifecycle. Event-loop code reads with `smbd_smb1_server_connection_read_handler()` or lower-level `smb1_receive_talloc()`, passes packets to `process_smb1()`/`construct_reply()`, dispatches through implementation-private command tables, and completes via `smb_request_done()` or `smb1_srv_send()`. Utility callers can inspect AndX chains before dispatch and can queue deferred opens when a reply needs to wait.

## State and persistence behavior
The declarations operate on long-lived smbd objects (`smbXsrv_connection`, `smbd_server_connection`, `smb_request`, `trans_state`, file IDs, deferred open records), but the header itself owns no storage. Implementations mutate transport state, session/tree crypto flags, deferred-open queues, and echo-handler descriptors.

## Dependencies and integration points
This interface is consumed by SMB1 command handlers, SMB2/SMB1 negotiation glue, transaction handlers, named-pipe code, event-loop setup, and torture tests. It depends on common Samba types such as `TALLOC_CTX`, `NTSTATUS`, `DATA_BLOB`-style buffers through `char **buffer`, `struct timeval`, `struct file_id`, and `struct deferred_open_record`.

## Risks and edge cases
- Several functions have ownership-sensitive contracts: `smb1_receive_talloc()` returns talloc-owned packet buffers, `smb1_parse_chain()` returns a talloc-owned request array, and `smb_request_done()` may free request objects after sending.
- Callers of `smb1_srv_send()` must pass the right signing/encryption flags and sequence number; mistakes affect SMB1 security state.
- Chain-walking callbacks receive pointers into the original SMB buffer and must not outlive it.
- `construct_reply()` and `process_smb1()` are SMB1-specific and should not be used for SMB2 packets despite shared connection structures.

## Test signals
Compile-time coverage should ensure all cross-file users agree on the function signatures. Behavioral signals come from tests of the implementation in `smb1_process.c`: chained request parsing, transaction throttling, deferred open replay, SMB1 receive signing/encryption, echo-handler forwarding, and final response send behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_process.h -->
