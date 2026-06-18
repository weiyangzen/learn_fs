# subset-b-009872 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_trans2.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_trans2.c

## Purpose

`smb1_trans2.c` implements Samba's SMB1 Transaction2 request path. It parses primary `SMBtrans2` and secondary `SMBtranss2` packets, accumulates fragmented parameter/data payloads in `struct trans_state`, dispatches Transaction2 subcommands, and serializes one or more Transaction2 responses. The file is a major compatibility surface for SMB1 clients: open, directory search, filesystem information, file/path information, POSIX extensions, DFS referrals, OS/2 printing ioctl support, and legacy find-notify stubs are all handled here.

## Important APIs, Types, and Functions

- `reply_trans2(struct smb_request *req)`: entry point for primary SMB1 trans2 packets. It validates word count and offsets, enforces IPC$ call restrictions, allocates `trans_state`, copies initial params/data, either dispatches immediately or queues the partial transaction on `conn->pending_trans`.
- `reply_transs2(struct smb_request *req)`: entry point for secondary trans2 fragments. It finds a matching pending transaction by MID, bounds-checks displacements, copies fragments, and dispatches when all params/data have arrived.
- `handle_trans2(...)`: central subcommand dispatcher for `TRANSACT2_OPEN`, `FINDFIRST`, `FINDNEXT`, `QFSINFO`, `SETFSINFO`, `QPATHINFO`, `QFILEINFO`, `SETPATHINFO`, `SETFILEINFO`, `MKDIR`, DFS referral, notify, and ioctl operations.
- `send_trans2_replies(...)`: response serializer and fragmenter. It obeys `max_data_bytes` and SMB1 `max_send`, calculates parameter/data offsets and displacements, applies SMB1 alignment padding, maps NTSTATUS to DOS error fields, and sends each packet with `smb1_srv_send`.
- Query handlers: `call_trans2qfsinfo`, `call_trans2qpathinfo`, `call_trans2qfileinfo`, `call_trans2qfilepathinfo`, `handle_trans2qfilepathinfo_result`, `call_trans2qpipeinfo`.
- Set handlers: `call_trans2setfsinfo`, `call_trans2setpathinfo`, `call_trans2setfileinfo`, `handle_trans2setfilepathinfo_result`.
- Directory enumeration: `call_trans2findfirst`, `call_trans2findnext`, `get_lanman2_dir_entry`, `smbd_dptr_name_equal`.
- POSIX extension helpers: `smb_set_posix_lock`, `smb_q_posix_lock`, `get_posix_fsp`, `smb_q_unix_basic`, `smb_q_unix_info2`, `smb_q_posix_acl`, `smb_q_posix_symlink`, `smb_posix_open`, `smb_posix_mkdir`, `smb_posix_unlink`, `smb_set_file_unix_link`, `smb_set_file_unix_hlink`, `smb_unix_mknod`, `smb_set_file_unix_basic`, `smb_set_file_unix_info2`, `smb_set_posix_acl`.

## Control Flow

Incoming primary requests enter `reply_trans2`. The function reads SMB parameter/data counts and offsets from `req->vwv`, validates them with `smb_buffer_oob`, copies payload bytes into heap buffers, and records transaction metadata such as return limits, setup count, call id, `mid`, `vuid`, and flags. Complete requests call `handle_trans2` immediately. Incomplete requests are linked into `conn->pending_trans` and get an interim empty response while later `reply_transs2` calls fill the missing ranges.

`reply_transs2` is the fragment continuation path. It rewrites the command code to `SMBtrans2` for Windows compatibility, finds the pending state by MID, clamps total counts if a client revises them downward, bounds-checks param/data displacements, updates received byte counters, and dispatches once the transaction is complete. Both primary and secondary paths free `state->data`, `state->param`, and the talloc state after dispatch or parameter failure.

`handle_trans2` enforces long-name flags for NT1-or-newer sessions and denies most calls when transport encryption is required but the request is not encrypted. It then dispatches to subcommand-specific handlers wrapped in profiling macros. Most handlers follow the same pattern: validate fixed parameter size, parse request-specific values with little-endian helpers, convert SMB1 strings into Samba path structures, call common smbd/VFS helpers, reallocate output parameter/data buffers, and finish through `send_trans2_replies`.

Directory enumeration opens a directory FSP, creates a `dptr` search handle, saves wildcard and attribute state in that handle, fills entries through `smbd_dirptr_lanman2_entry`, and optionally closes the search handle based on find flags. `FINDNEXT` retrieves the saved dptr, optionally rewinds to a resume name, continues filling entries, and closes the handle when requested or at end of search.

Path and file information handlers split into native/common info levels and SMB1 UNIX extension levels. Common levels delegate to `smbd_do_qfilepathinfo` and `smbd_do_setfilepathinfo`; UNIX levels use local helpers to marshal POSIX wire formats or perform POSIX open, unlink, ACL, symlink, hardlink, mode, owner, group, size, time, and flag changes.

## State and Persistence Behavior

The file persists partial transaction state in `conn->pending_trans` until all fragments arrive or an error removes the state. Directory searches persist through `dptr` handles attached to directory `files_struct` instances, including wildcard, attr mask, last name sent, case sensitivity, and backup-privilege state. `SETFSINFO` persists client UNIX capability negotiation in `xconn->smb1.unix_info` and may switch name mangling to POSIX path mode. SMB1 POSIX lock requests persist byte-range lock state through Samba's locking subsystem. File/path setters update persistent filesystem state through the VFS: metadata, ACLs, link creation, unlink/delete-on-close, truncation, mknod, quota data, and timestamps. Transport encryption setup can transition the connection into encrypted mode.

## Dependencies and Integration Points

This file integrates with the core smbd request stack (`struct smb_request`, `connection_struct`, `smbXsrv_connection`), SMB1 packet helpers, Transaction2 constants from `trans2.h`, VFS create/stat/link/ACL APIs, common query/set helpers in smbd, directory pointer code from `source3/smbd/dir.h`, DFS referral setup, quota and print helpers, byte-range locking, share mode locks, server encryption setup, POSIX create contexts from SMB2 POSIX helpers, and Samba configuration checks such as `lp_smb1_unix_extensions`, `lp_ea_support`, `lp_blocking_locks`, `lp_follow_symlinks`, `lp_dont_descend`, and encryption policy. `file_fsp` and `filename_convert_smb1_search_path` come from `smb1_utils.c`.

## Risks and Edge Cases

The highest-risk areas are packet sizing, offset/displacement validation, and response fragmentation. `send_trans2_replies` must keep SMB offsets, padding, `max_send`, and `max_data_bytes` consistent or clients can misparse responses. The request assembly paths guard against out-of-bounds copies, but they depend on correct `smb_buffer_oob` use for every fragment. Directory enumeration deliberately overallocates by `DIR_ENTRY_SAFETY_MARGIN`; regressions around max-data handling can leak uninitialized bytes or truncate entries incorrectly. POSIX extensions are sensitive because they map SMB1 wire requests to real UNIX metadata changes and special file creation. Symlink/hardlink handling, snapshot token stripping, backup privilege escalation, and root transitions must preserve share boundaries and restore privileges. Async POSIX lock handling returns `NT_STATUS_EVENT_PENDING`; callers must not send a second response while the lock callback owns completion.

## Test Signals

Useful test coverage includes SMB1 trans2 fragmentation with primary and secondary packets, invalid offset/displacement/count fuzzing, `raw.search` and OS/2 resume-name behavior, findfirst/findnext close flag combinations, EA list validation, encrypted-share denial/allowance for `QFSINFO` and `SETFSINFO`, IPC$ allowed-call matrix, DFS referral on IPC$, SMB1 UNIX extension negotiation, POSIX open/mkdir/unlink/link/ACL/lock query and set operations, delete-pending handling for streams, sharing-violation deferral, quota setting, OS/2 print ioctl job id handling, and response truncation with `STATUS_BUFFER_OVERFLOW`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_trans2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_trans2.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_trans2.h

## Purpose

`smb1_trans2.h` is the small public interface for the SMB1 Transaction2 implementation. It exposes the two SMB1 command handlers implemented in `smb1_trans2.c` so the SMB1 server dispatch layer can route primary and secondary Transaction2 commands.

## Important APIs, Types, and Functions

- `void reply_trans2(struct smb_request *req)`: handles primary `SMBtrans2` requests, including full requests and first fragments of multi-packet transactions.
- `void reply_transs2(struct smb_request *req)`: handles `SMBtranss2` secondary fragments for pending SMB1 Transaction2 requests.

The header intentionally declares no local structs or constants. The request type comes from the included smbd/server headers used by compilation units that include this file.

## Control Flow

The file has no control flow of its own. Its declarations bind the SMB command dispatch table to the concrete implementation in `smb1_trans2.c`.

## State and Persistence Behavior

No state is defined in the header. Runtime state is held by the implementation through `struct smb_request`, `connection_struct`, pending transaction lists, directory pointers, and VFS/file structures.

## Dependencies and Integration Points

This header depends on the surrounding smbd type environment for `struct smb_request`. It is consumed by SMB1 dispatch code that needs to call the Transaction2 handlers without knowing their internal helper functions.

## Risks and Edge Cases

The main risk is API drift: changing either prototype must be synchronized with the SMB1 command dispatch and the definitions in `smb1_trans2.c`. Because these functions own packet replies and memory cleanup, callers must treat them as terminal request handlers.

## Test Signals

Build coverage is the primary signal for this header. Runtime signals come indirectly from SMB1 Transaction2 command tests that prove the dispatch layer still reaches `reply_trans2` and `reply_transs2`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_trans2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_utils.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_utils.c

## Purpose

`smb1_utils.c` contains helper routines used by SMB1 server code, especially compatibility helpers that are shared outside one command implementation. The file supports legacy FCB/DOS sharing behavior, RFC1002 keepalive sending, string growth in SMB buffers, SMB1 search path conversion where the terminal component can be a wildcard, and 16-bit SMB1 FID lookup.

## Important APIs, Types, and Functions

- `fcb_or_dos_open(...)`: on sharing violation, searches existing opens for the same file, vuid, pid, name, stream, and DOS/FCB deny flags, then creates a new `files_struct` sharing the existing file handle.
- `send_keepalive(int client)`: writes a four-byte NBSS keepalive packet to a client socket.
- `message_push_string(uint8_t **outbuf, const char *str, int flags)`: grows an SMB output buffer, appends a server-string encoded string using `srvstr_push`, clears unused overallocated bytes, and updates BCC.
- `filename_convert_smb1_search_path(...)`: separates the wildcard terminal component from an SMB1 search path, converts the parent directory with `filename_convert_dirfsp`, and returns the directory FSP, converted parent name, and mask.
- `file_fsp(struct smb_request *req, uint16_t fid)`: resolves a 16-bit SMB1 FID to a non-closing `files_struct`, honoring chained requests via `req->chain_fsp`.

## Control Flow

`fcb_or_dos_open` first rejects calls without DOS/FCB private flags. It computes the file id from the stat buffer, iterates matching file-id opens on the server connection, and checks request identity, deny flags, write access, base name, and stream name. When a match is found, executable names are refused for `DENY_DOS`, then `file_new` creates a second FSP whose `fh` pointer and selected metadata are copied from the original. The file-handle refcount is incremented and permissions are recalculated from the requested access mask.

`message_push_string` calculates an intentionally generous growth amount for encoded output, reallocates the buffer with talloc, pushes the string at the old buffer end, validates wrap/size assumptions, zeroes unused growth, updates SMB BCC, and returns the encoded byte count.

`filename_convert_smb1_search_path` extracts an optional snapshot token, obtains the original last component as the wildcard mask, maps empty masks to `"*"`, removes the terminal component from the input string in-place, and converts the remaining parent path. Ownership of the returned `smb_filename` and mask is moved to the caller's context.

`file_fsp` first returns a valid chained FSP if present. Otherwise it looks up the SMB1 open record with `smb1srv_open_lookup`, rejects missing or closing FSPs, caches the result on `req->chain_fsp`, invalidates cached DOS attributes, and returns the FSP.

## State and Persistence Behavior

`fcb_or_dos_open` creates a new open record that shares an existing underlying file handle and increments the handle refcount, so close semantics depend on balanced `file_free`/close behavior later. `file_fsp` mutates `req->chain_fsp` as a per-request cache and invalidates cached DOS attributes on the FSP name. `filename_convert_smb1_search_path` mutates `name_in` by truncating the terminal path component. `message_push_string` reallocates and replaces the caller's output-buffer pointer.

## Dependencies and Integration Points

The file integrates with file-id lookup, Samba file handle refcounting, `smbXsrv_open` SMB1 open lookup, VFS file-id generation, SMB string conversion, path conversion, snapshot-token extraction, and low-level write helpers. `smb1_trans2.c` uses `fcb_or_dos_open`, `filename_convert_smb1_search_path`, and `file_fsp`.

## Risks and Edge Cases

`fcb_or_dos_open` deliberately implements legacy semantics by aliasing an existing file handle; bugs here can produce incorrect access rights, leaked references, or surprising sharing behavior. The helper assumes names and streams compare as expected and refuses executable DOS-deny reuse. `message_push_string` must preserve buffer ownership and BCC correctness after realloc; failure after realloc returns `-1` without assigning `*outbuf` to the temporary buffer, which callers must handle. `filename_convert_smb1_search_path` edits its input path in place, so callers must pass mutable storage and not expect the original full path afterwards. `file_fsp` caches a pointer in the request; callers must not use it after the FSP begins closing.

## Test Signals

Signals include SMB1 open tests for DOS/FCB deny fallback, chained SMB1 commands that reuse `chain_fsp`, wildcard search tests for root and nested directories, snapshot path searches, Unicode and ASCII string append tests for BCC/length consistency, and keepalive write error handling on disconnected sockets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_utils.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_utils.h

## Purpose

`smb1_utils.h` declares utility functions valid in the SMB1 server. It provides shared prototypes for legacy open fallback, keepalive sending, SMB output string appending, SMB1 search-path conversion, and FID-to-FSP lookup.

## Important APIs, Types, and Functions

- `fcb_or_dos_open`: legacy sharing-violation fallback for DOS/FCB deny modes.
- `send_keepalive`: RFC1002 keepalive packet sender.
- `message_push_string`: encoded string append helper for SMB response buffers.
- `filename_convert_smb1_search_path`: converts a search path while preserving the terminal wildcard mask separately.
- `file_fsp`: resolves a 16-bit SMB1 FID from an SMB request.

The header includes `includes.h`, `vfs.h`, `proto.h`, and string wrapper definitions, so consumers inherit Samba core types such as `NTSTATUS`, `TALLOC_CTX`, `connection_struct`, `files_struct`, and `smb_filename`.

## Control Flow

The header has no executable control flow. It establishes the cross-file contract consumed by SMB1 command handlers such as Transaction2, NT create, search, and related reply code.

## State and Persistence Behavior

No state is declared here. The declared functions can mutate request caches, file-handle references, caller-owned buffers, and mutable input paths in their implementation.

## Dependencies and Integration Points

This header is part of the smbd internal API. It connects SMB1-specific code to common VFS and string conversion types while keeping implementation details in `smb1_utils.c`.

## Risks and Edge Cases

Because these helpers have side effects that are not visible from prototypes alone, call sites need to know ownership rules: `message_push_string` may replace the buffer pointer, `filename_convert_smb1_search_path` edits the path string, `file_fsp` may cache `chain_fsp`, and `fcb_or_dos_open` returns a new FSP sharing an underlying handle.

## Test Signals

Build checks catch prototype drift. Functional coverage comes from SMB1 tests that exercise each declared helper through command handlers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_aio.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_aio.c

## Purpose

`smb2_aio.c` implements shared asynchronous I/O support for smbd, with SMB2-specific read/write scheduling and generic helpers also used by SMB1 AIO paths. It manages lifetime metadata for in-flight operations, attaches tevent requests to `files_struct` objects so close/flush/lock paths can wait for them, and wraps asynchronous writes with optional fsync behavior.

## Important APIs, Types, and Functions

- `aio_write_through_requested(struct aio_extra *aio_ex)`: exposes the write-through flag stored in AIO metadata.
- `create_aio_extra(...)`: allocates `struct aio_extra`, optional output buffer storage, and records the FSP.
- `struct aio_req_fsp_link` plus `aio_add_req_to_fsp(...)` and destructor `aio_del_req_from_fsp(...)`: maintain the dynamic `fsp->aio_requests` array.
- `pwrite_fsync_send`, `pwrite_fsync_recv`: tevent wrapper for async pwrite followed by conditional async fsync.
- `cancel_smb2_aio(struct smb_request *smbreq)`: SMB2 cancel hook that currently never cancels underlying AIO and therefore returns false.
- `schedule_smb2_aio_read(...)`: validates and schedules an SMB2 async read through `SMB_VFS_PREAD_SEND`.
- `schedule_aio_smb2_write(...)`: validates and schedules an SMB2 async write through `pwrite_fsync_send`.
- Completion callbacks `aio_pread_smb2_done` and `aio_pwrite_smb2_done`: translate VFS completion into SMB2 read/write completion.

## Control Flow

Read scheduling validates the requested offset/length, rejects alternate streams and internal opens, checks the configured `aio read size` unless the VFS forces AIO, prevents async execution for non-final compound requests, allocates the read buffer, creates `aio_extra`, checks strict byte-range locks, starts `SMB_VFS_PREAD_SEND`, attaches a completion callback, links the request to `fsp->aio_requests`, and stores `aio_extra` in `smbreq->async_priv`. Completion receives the VFS result, calls `smb2_read_complete`, updates file handle position for positive reads, and completes or errors the SMB2 subrequest.

Write scheduling follows the same shape with write-specific checks: alternate streams/internal opens/minimum size/non-final compound/recvfile unread data are rejected, `write_through` is stored, a write strict-lock range is checked, file modification tracking is prepared, `pwrite_fsync_send` starts the write, the request is linked to the FSP, and level-II oplock contention is signaled. Completion receives write/fsync status, marks the file modified, calls `smb2_write_complete_nosync`, and completes the SMB2 subrequest.

`pwrite_fsync_send` validates the write range, completes immediately for zero-length writes, otherwise starts `SMB_VFS_PWRITE_SEND`. Its write callback stores bytes written and, when `strict sync` and either `sync always` or write-through apply, chains an `SMB_VFS_FSYNC_SEND`; otherwise it completes after the write.

## State and Persistence Behavior

Each AIO request owns an `aio_extra` object for request-private state: FSP, offset, byte count, strict lock descriptor, write-through flag, modification state, and SMB request pointer. `aio_add_req_to_fsp` persists the tevent request pointer in `fsp->aio_requests`; its talloc destructor removes the pointer when the link is freed, shrinking or freeing the array. File close uses this state to mark the FSP closing and wait for in-flight AIO. Successful reads update `fh` position and position information. Successful writes mark the file modified and may persist data through fsync depending on configuration.

## Dependencies and Integration Points

The file depends on tevent request primitives, VFS async read/write/fsync operations, Samba strict locking, SMB2 read/write completion helpers, file-handle position helpers, oplock contention, loadparm settings for AIO and sync behavior, and `files_struct` AIO tracking consumed by close and other smbd operations. Prototypes are exported through `proto.h` and are used by `smb2_read.c`, `smb2_write.c`, SMB1 AIO, flush, ioctl, lock, query-directory, and oplock paths.

## Risks and Edge Cases

The AIO list/destructor relationship is critical: losing the link can make close proceed while I/O is still active; double removal can corrupt `fsp->aio_requests`. `cancel_smb2_aio` intentionally does not cancel underlying work, so callers must continue normal processing and not send a cancel response. Compound requests are restricted to the last element because async completion would otherwise disturb compound response ordering. Write-through correctness depends on `pwrite_fsync_send` honoring strict sync policy. Alternate streams and internal opens fall back to synchronous paths. Range validation and strict-lock checks protect against invalid offsets and lock conflicts before handing control to VFS async backends.

## Test Signals

Coverage should include async read/write above and below configured thresholds, VFS-forced AIO, strict lock conflict denial, non-final compound fallback, alternate stream fallback, internal open fallback, recvfile fallback for writes, zero-length writes, write-through plus strict-sync fsync behavior, close waiting for pending AIO, request-list destructor cleanup, and cancel requests against in-flight SMB2 reads/writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_aio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_break.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_break.c

## Purpose

`smb2_break.c` handles SMB2 oplock and lease break acknowledgements from clients and sends asynchronous oplock/lease break notifications to clients. It converts wire-level SMB2 break packets into Samba oplock or lease state transitions and delegates persistence changes to the oplock and leases database subsystems.

## Important APIs, Types, and Functions

- `smbd_smb2_request_process_break(struct smbd_smb2_request *req)`: entry point for SMB2 BREAK. It first tries the oplock-break packet size and falls back to lease-break parsing when the size matches lease semantics.
- `smbd_smb2_oplock_break_send/recv`: tevent wrapper that maps the client-requested oplock level, removes or downgrades Samba oplock state, and returns the resulting SMB2 oplock level.
- `smbd_smb2_request_process_lease_break(...)`: parses lease key and requested lease state and starts lease downgrade handling.
- `smbd_smb2_lease_break_send/recv`: looks up leased file ids in `leases_db`, calls `downgrade_lease`, and returns the acknowledged lease state.
- `lease_parser(...)` and `struct lease_lookup_state`: callback state for copying file ids out of the leases database.
- `send_break_message_smb2(files_struct *fsp, uint32_t break_from, uint32_t break_to)`: sends server-initiated oplock or lease break notifications.

## Control Flow

Oplock acknowledgements validate the 0x18 request body, read the requested oplock level and file id pair, resolve the FSP with `file_fsp_smb2`, reject closed files or a missing pending break timeout, and require the requested level to be NONE or LEVEL_II. The async send helper creates a fake SMB request, maps SMB2 level to Samba oplock level, and either removes the oplock or downgrades it. Completion builds a 0x18 response body echoing file ids and the resulting oplock level.

Lease acknowledgements validate the 0x24 body, parse the 128-bit lease key and requested lease state, and run a tevent helper. The helper parses the leases database for the client GUID plus lease key, copies associated file ids, rejects missing records, and calls `downgrade_lease`. `NT_STATUS_OPLOCK_BREAK_IN_PROGRESS` is treated as a successful acknowledgement path. Completion sends a 0x24 response with the lease key, resulting lease state, zero flags, and zero lease duration.

Server-initiated notifications enter `send_break_message_smb2`. If the open record status is not OK the notification is skipped. Lease oplocks compute whether ACK is required and preserve lease epoch for v2 leases before calling `smbd_smb2_send_lease_break`. Non-lease oplocks map the target break level to SMB2 LEVEL_II or NONE and call `smbd_smb2_send_oplock_break`. Transport send failure disconnects the client.

## State and Persistence Behavior

Client break acknowledgements mutate Samba oplock or lease state through `remove_oplock`, `downgrade_oplock`, and `downgrade_lease`. Lease lookup state is temporary, but the authoritative lease-to-file-id mapping lives in `leases_db`. The FSP's `oplock_timeout`, `sent_oplock_break`, `oplock_type`, `op`, and `lease` fields drive validation and notification behavior. Notifications do not persist new state directly but are part of the state machine that expects later acknowledgements.

## Dependencies and Integration Points

The file integrates with SMB2 request parsing/response helpers, FSP lookup by persistent/volatile file id, Samba oplock mapping helpers, fake SMB request creation, `leases_db`, `downgrade_lease`, `smbd_smb2_send_lease_break`, `smbd_smb2_send_oplock_break`, and client disconnect/error handling. `smb2_server.c` dispatches SMB2 BREAK to this file; `smb2_oplock.c` invokes `send_break_message_smb2`.

## Risks and Edge Cases

The size-based fallback from oplock to lease break must keep wire-structure validation exact; accepting malformed packets could corrupt state or produce wrong errors. Oplock acknowledgements require `oplock_timeout` to be set, so state-machine ordering matters. A failure in `remove_oplock` or `downgrade_oplock` panics as an internal TDB error, making database consistency critical. Lease break handling must map missing lease records to client-visible object-not-found behavior. Notification code must avoid sending breaks for stale or failed open records and must disconnect on transport failure to avoid inconsistent client/server cache state.

## Test Signals

Useful tests include SMB2 oplock acknowledgement to NONE and LEVEL_II, invalid requested levels, closed-file ids, acknowledgements without pending break timeout, lease acknowledgements for existing and missing lease keys, multi-file lease keys, `NT_STATUS_OPLOCK_BREAK_IN_PROGRESS` downgrade behavior, v1 versus v2 lease epoch notification fields, ACK-required lease notifications, non-lease oplock notifications, and client disconnect behavior on notification send failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_break.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_close.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_close.c

## Purpose

`smb2_close.c` implements SMB2 CLOSE request processing. It validates the close packet, resolves the open file id, waits for in-flight AIO when needed, handles delete-on-close lease-break delay, closes and frees the FSP, and optionally returns full file information captured around close.

## Important APIs, Types, and Functions

- `smbd_smb2_request_process_close(struct smbd_smb2_request *req)`: parses SMB2 CLOSE, resolves the FSP, starts async close processing, and queues the request pending.
- `smbd_smb2_close_send/recv`: tevent wrapper around close state, AIO waiting, lease-break delay, and output metadata capture.
- `smbd_smb2_request_close_done(...)`: builds the 0x3c SMB2 CLOSE response body from close state.
- `smbd_smb2_close(...)`: performs the actual close via a fake SMB request, `close_file_smb`, optional full-info collection, and `file_free`.
- `setup_close_full_information(...)`: marshals timestamps, allocation size, EOF, and close flags from `smb_filename` stat data.
- `smbd_smb2_close_wait_done(...)`: resumes close after pending AIO requests drain.
- `smbd_smb2_close_delay_lease_break_done(...)`: resumes close after waiting for a handle lease break and restores user/service context.
- `struct smbd_smb2_close_state`: holds input FSP/flags, output metadata, and optional wait queue.

## Control Flow

The request entry validates a 0x18 body, reads close flags and file ids, resolves the FSP with `file_fsp_smb2`, and starts `smbd_smb2_close_send`. The send helper marks the FSP closing, tries to cancel each tracked AIO request, and if any remain creates a tevent queue that completes only after all AIO request destructors remove their waiters. When the wait completes, `smbd_smb2_close_wait_done` calls the real close.

If there is no pending AIO but `initial_delete_on_close` is set, the send helper checks share mode state. If delete-on-close is not already set, it delays for a handle lease break up to `OPLOCK_BREAK_TIMEOUT`; synchronous completion falls through, and asynchronous completion resumes in `smbd_smb2_close_delay_lease_break_done` after restoring the session's user/service context.

The actual close creates a fake SMB request, optionally records DOS attributes and sets `fstat_before_close` for full-information responses, calls `close_file_smb`, then uses still-available `fsp->fsp_name` stat data to fill full information before `file_free`. The completion callback receives state, generates the response body, serializes times using the connection timestamp resolution, and calls `smbd_smb2_request_done`.

## State and Persistence Behavior

The FSP is marked `closing` before waiting, preventing later lookup/use as an active handle. `close_file_smb` and `file_free` remove open-file state, release share modes, and finalize filesystem side effects such as delete-on-close. `fsp->aio_requests` controls whether close must wait for asynchronous operations started by `smb2_aio.c` or related paths. Full close information is copied into the close state before the FSP is freed. Delete-on-close lease-delay logic reads and updates behavior through share mode locks and lease-break handling.

## Dependencies and Integration Points

The file integrates with SMB2 server dispatch, SMB2 request body helpers, FSP lookup by SMB2 file id, fake SMB request creation, `close_file_smb`, `file_free`, AIO tracking on `files_struct`, tevent queues, share mode locks, handle lease-break delay helpers, user/service context switching, DOS attribute/stat helpers, allocation-size VFS calls, and timestamp conversion. Its AIO wait semantics depend on `aio_add_req_to_fsp` destructors from `smb2_aio.c`.

## Risks and Edge Cases

Close must not free an FSP while AIO callbacks still reference it; the wait-queue and `fsp->aio_requests` destructor protocol is the key safety mechanism. The loop that cancels AIO requests only advances when cancellation fails, relying on successful cancellation to remove entries. Full-information responses depend on stat data being available after `close_file_smb` but before `file_free`. Delete-on-close handling must not race lease break acknowledgement or lose user context after asynchronous delay. On close failure, the code frees the FSP with `file_free`, so callers must treat the handle as consumed even on some errors.

## Test Signals

Test coverage should include basic close, close of already closed file ids, full-information close for files and directories, DOS filetime resolution behavior, pending AIO close waits, cancellable and non-cancellable AIO requests, delete-on-close with and without existing share mode delete state, handle lease-break delay timeout/success, user-context restoration after delay, close failure paths, and response serialization of 0x3c body fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_close.c -->
