# Research: subset-b-009874

Grouped research for Samba source3 smbd SMB2 security, oplock/lease, named-pipe, POSIX metadata, process-loop, directory-query, read, and common reply helper code. Each section preserves the source path and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_nttrans.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_nttrans.c

## Purpose
This file implements shared NT transaction helpers used by SMB1 and SMB2 paths for security descriptors, copy operations, and quota query support. The major responsibilities are setting and querying NT ACLs through the VFS, translating a special SMB2 POSIX chmod ACL form into `fchmod`, copying files while preserving DOS attributes and timestamps, and, when quota support is compiled in, marshalling quota results for fake quota file handles.

## Important APIs, Types, And Functions
`set_sd()` validates write capability, `nt acl support`, symlink policy, and per-component rights before calling `SMB_VFS_FSET_NT_ACL()` on `metadata_fsp(fsp)`. `set_sd_blob()` unmarshals a security descriptor and either delegates to `set_sd()` or detects the SMB2 POSIX chmod ACE through `check_smb2_posix_chmod_ace()`. `smbd_do_query_security_desc()` is the external query entry point; it uses `smbd_fetch_security_desc()` and `smbd_marshall_security_desc()` to enforce access checks, fetch or synthesize a descriptor, and marshal it with NDR helpers. `copy_internals()` opens source and destination handles through `SMB_VFS_CREATE_FILE()`, transfers data with `vfs_transfer_file()`, and fixes timestamps and DOS mode. Under `HAVE_SYS_QUOTAS`, `smbd_do_query_getinfo_quota()` uses `SMB_NTQUOTA_HANDLE`, `SMB_NTQUOTA_LIST`, `extract_sids_from_buf()`, `fill_qtlist_from_sids()`, `vfs_get_ntquota()`, `vfs_get_user_ntquota_list()`, and `fill_quota_buffer()`.

## Control Flow
ACL set flow starts by rejecting read-only shares, disabled NT ACL support, and symlink ACL operations. It then drops owner/group bits absent from the descriptor, enforces `WRITE_OWNER`, `WRITE_DAC`, and `SYSTEM_SECURITY` access as requested, maps generic bits in DACL/SACL entries, canonicalizes inheritance flags, and writes the descriptor through the VFS. Query flow mirrors this with `READ_CONTROL` and SACL access checks, optional null descriptor synthesis for label-only or ACL-disabled responses, requested-component pruning, present-bit normalization, and buffer-size validation before marshalling. Copy flow rejects invalid source, hidden/system attribute mismatches, existing destination, and directories, then opens both files, transfers bytes, closes in the right order, restores write time, and repairs the archive bit side effect from create. Quota flow either builds a SID-specific quota list from client-provided NDR entries, restarts a full quota scan, or continues from `tmp_list`.

## State And Persistence
Persistent effects are VFS ACL updates, chmod mode changes, destination file creation, DOS attribute changes, file timestamps, and quota-list cursor state stored in `fsp->fake_file_handle->private_data`. The file itself has no global durable state. It relies heavily on talloc ownership for unmarshalled descriptors, marshalled blobs, synthetic pathrefs, quota lists, and SID arrays. Notifications are emitted on successful security changes.

## Dependencies And Integration Points
This code integrates with smbd file handles, `connection_struct`, access-check helpers, share configuration, fake quota files, VFS ACL/chmod/quota/copy entry points, NDR security and quota marshalling, SID lookup, DOS mode helpers, notification delivery, and SMB2 POSIX create/chmod conventions. It is called from SMB transaction and SMB2 information paths rather than parsing full requests itself.

## Risks And Test Signals
Risk concentrates around exact Windows-compatible ACL semantics, especially SACL requiring both `SYSTEM_SECURITY` and `WRITE_DAC`, label-only security descriptor behavior, inheritance flag canonicalization, and symlink refusal. The POSIX chmod ACE path is intentionally narrow and should reject malformed ACLs. Copy paths need regression coverage for hidden/system filtering, zero-length files, partial transfers, close-time disk-full errors, and archive bit restoration. Quota tests should cover SID-list offset validation, integer wrap detection, empty SID lists, restart versus continuation scans, buffer-too-small responses, and stale fake quota handle state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_nttrans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_oplock.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_oplock.c

## Purpose
This file implements smbd oplock and SMB2 lease coordination. It grants, downgrades, removes, breaks, times out, and waits for oplocks and leases across local `files_struct` state, shared share-mode records, the lease database, kernel oplock backends, and inter-process messaging. It also handles directory lease contention and handle lease break delays before operations such as rename or open can proceed.

## Important APIs, Types, And Functions
Public entry points include `set_file_oplock()`, `release_file_oplock()`, `remove_oplock()`, `downgrade_oplock()`, `downgrade_lease()`, `contend_dirleases()`, `smbd_contend_level2_oplocks_begin()`, `init_oplocks()`, `init_kernel_oplocks()`, `delay_for_handle_lease_break_send()`, `delay_for_handle_lease_break_recv()`, and `fsp_get_smb2_lease()`. Key state lives in `files_struct` fields such as `oplock_type`, `sent_oplock_break`, `oplock_timeout`, and `lease`; in `struct fsp_lease`; in `struct share_mode_entry`; and in `leases_db` records keyed by client GUID, lease key, and file id. Internal callbacks include `process_oplock_break_message()`, `process_kernel_oplock_break()`, `lease_timeout_handler()`, `oplock_timeout_handler()`, and recursive handle-lease wait callbacks.

## Control Flow
Granting an oplock optionally asks the kernel backend to set an oplock, refuses level II with kernel oplocks, initializes break state, and updates per-connection counters. Releasing or downgrading updates the kernel backend, share-mode entry, local counters, local oplock type, and timers. Break messages are received through Samba messaging, decoded from `oplock_break_message`, resolved to the current `files_struct`, normalized for client capabilities and configuration, and then sent to the client as SMB2 or SMB1 breaks. Lease breaks additionally update `leases_db`, epoch, break flags, requested and required target states, and local fsp lease mirrors. If clients do not answer, lease and oplock timeout handlers force downgrade/removal and wake waiters.

## State And Persistence
The durable cross-process state is the share-mode database and `leases_db`; local process state is held in open file objects, timers, pending tevent requests, connection oplock counters, and queued break records. `share_mode_wakeup_waiters()` is used to release blocked opens after state changes. Recursive handle-lease waiting may hold or reacquire share-mode locks while watching records for changes. Kernel oplock state is external to Samba and is accessed through `kernel_oplocks`.

## Dependencies And Integration Points
The file depends on Samba messaging, share-mode lock helpers, `leases_db`, file table traversal, kernel oplock implementations, SMB1/SMB2 break senders, directory helpers, tevent timers and watchers, and server configuration such as kernel oplocks, level II oplocks, directory leases, strict rename, and oplock break wait time. It is on the critical path for create/open conflict handling, write and lock contention, directory notifications, and lease-aware rename/delete behavior.

## Risks And Test Signals
This is high-risk concurrency code. Tests should cover exclusive-to-level-II downgrade, level-II/read lease break-to-none, async read-only breaks that require no ACK, timeout-forced removal, kernel break races after close, stale PID filtering, repeated break messages, lease epoch changes, multistep handle/write lease breaks, dynamic-share multi-file-id lease updates, directory lease parent breaks, and recursive handle lease waits below directories. Important failure signals include leaked share-mode locks, negative open counters, `leases_db_get()` failures on live entries, waits that never complete, clients being disconnected by failed break sends, and incorrect `NT_STATUS_ACCESS_DENIED` versus timeout mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_oplock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_pipes.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_pipes.c

## Purpose
This file opens named pipe fake files for SMB requests. It adapts an SMB request and pipe name into a `files_struct` backed by the RPC named-pipe subsystem rather than a real filesystem fd, and adds SMB3 encryption context information to the session token when encrypted SMB2 pipe access is used.

## Important APIs, Types, And Functions
`open_np_file()` is the only function. It allocates a new file with `file_new()`, marks it fd-less via `fsp_set_fd(fsp, -1)`, disables byte-range locking, sets read/write data access, stores the pipe basename with `fsp_set_smb_fname()`, and finally calls `np_open()` to create `fsp->fake_file_handle`. When the SMB2 request was encrypted, it uses `copy_session_info()`, edits the copied `security_token`, appends an SMB3 SID made from `global_sid_Samba_SMB3`, dialect, encryption-required marker, and cipher, and marks `fsp->fsp_flags.encryption_required`.

## Control Flow
The function is linear: allocate fsp, initialize fsp fields from `smb_request` and connection, copy the basename, optionally augment session security for encrypted SMB2, then call `np_open()` with remote/local addresses, event context, messaging context, DCE context, and the selected session info. Every allocation or pipe-open failure frees the partially created fsp before returning an NTSTATUS.

## State And Persistence
There is no disk persistence. State is the live fake file handle, fsp metadata, copied session info for encrypted requests, and the named-pipe server state behind `np_open()`. The SMB3 SID insertion is scoped to the copied session info, not the original connection session.

## Dependencies And Integration Points
This code integrates smbd file-handle management with `rpc_server/srv_pipe_hnd.h`, DCE/RPC helpers, auth token utilities, connection addresses, and SMB2 encryption metadata. The resulting fake file is consumed by SMB2 read/write/ioctl paths and named-pipe RPC server code.

## Risks And Test Signals
Tests should verify successful pipe open, cleanup on every allocation and `np_open()` failure, encrypted SMB2 pipe open adding exactly one SMB3 SID, rejection if an SMB3 SID is already present, correct dialect/encryption/cipher RID construction, and `encryption_required` propagation to later pipe I/O. A key risk is accidentally mutating shared session security instead of the per-fsp copy, or allowing duplicate SMB3 marker SIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_pipes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_posix.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_posix.c

## Purpose
This file builds SMB3 POSIX file information responses from Samba stat data and reparse point metadata. It maps Unix file type, ownership, link count, inode/device ids, timestamps, allocation size, DOS attributes, and special-file reparse details into `struct smb3_file_posix_information`.

## Important APIs, Types, And Functions
`smb3_file_posix_information_init()` is the exported initializer. `reparse_buffer_parse_posix_type()` maps `IO_REPARSE_TAG_SYMLINK` to `S_IFLNK`, non-NFS arbitrary reparse tags to regular files, and NFS reparse buffer types to character, block, FIFO, or socket mode bits. It parses NFS reparse data with `reparse_data_buffer_parse()`. The output embeds `smb3_file_posix_information` and its `cc` create-context-like fields, including owner and group SIDs generated by `uid_to_sid()` and `gid_to_sid()`.

## Control Flow
The initializer starts from `smb_fname->st.st_ex_mode`. Regular files and directories need no special handling. Other file types are expected to have `FILE_ATTRIBUTE_REPARSE_POINT` already set. If the DOS attributes contain the reparse bit, the function fetches reparse data with `fsctl_get_reparse_point()`, parses the POSIX type, replaces the stat-derived type bits, and records the reparse tag. It then fills size, allocation, inode, device, birth/access/write/change times, attributes, link count, wire-format POSIX mode, and owner/group SIDs.

## State And Persistence
The function is read-only. It allocates temporary reparse buffers and parser state with talloc, but persists nothing. Its observable state is the populated output structure returned to SMB3 POSIX query/create callers.

## Dependencies And Integration Points
It integrates POSIX stat metadata, Samba VFS allocation and file-id helpers, reparse-point FSCTL support, NFS reparse parsing utilities, SMB3 POSIX generated NDR types, and SID mapping. It is used by SMB3 POSIX information query or create response paths that need to present Unix metadata through SMB.

## Risks And Test Signals
Tests should cover regular files, directories, symlinks, NFS character/block/FIFO/socket reparse points, arbitrary non-NFS reparse tags, malformed NFS reparse buffers, uid/gid equal to `(uid_t)-1`, and allocation-size/file-id behavior across VFS modules. Risk areas include asserts when non-regular special files are missing the reparse attribute, incorrect fallback for unknown reparse tags, and returning `NT_STATUS_REPARSE_POINT_NOT_RESOLVED` for unsupported NFS types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_posix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_process.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_process.c

## Purpose
Despite the SMB2 filename, this file is the smbd per-client process and packet-dispatch bootstrap for SMB1/SMB2. It receives initial packets, negotiates SMB1 versus SMB2, constructs SMB1 replies, maintains deferred open retry queues, creates connection/session/open tables, registers cluster and messaging handlers, sets up timers/signals/profiling, and runs the main tevent loop for a client connection.

## Important APIs, Types, And Functions
Key entry points include `receive_smb_talloc()`, `process_smb()`, `smbXsrv_connection_init_tables()`, `init_smb1_request()`, `smbd_add_connection()`, and `smbd_process()`. Deferred-open helpers include `push_deferred_open_message_smb()`, `schedule_deferred_open_message_smb()`, `remove_deferred_open_message_smb()`, `open_was_deferred()`, and `get_deferred_open_message_state()`, backed by `struct pending_message_list`. Connection setup uses `struct smbXsrv_client`, `struct smbd_server_connection`, and `struct smbXsrv_connection`. Messaging handlers cover forced disconnects, config reload, id-cache invalidation, CTDB IP release, and IP-dropped events.

## Control Flow
Connection setup starts in `smbd_process()`: create client and server-connection objects, initialize the pthread pool, install signals, call `smbd_add_connection()`, copy local/remote address metadata, reload services, optionally chroot, initialize file tables, oplocks, messaging handlers, keepalive/deadtime/housekeeping timers, directory pointers, profiling, and then enter `tevent_loop_wait()`. The first packet read handler only accepts NBSS session requests, SMB1 negprot bootstrap, or SMB2 negprot. Later `process_smb()` handles NBSS special messages, detects SMB2 headers when allowed, disables SMB2 for non-negprot SMB1 traffic, and dispatches to SMB1 or SMB2 processors. Deferred-open timers redispatch saved SMB1 buffers through `process_smb()` and remove processed queue entries.

## State And Persistence
State is per-process and mostly talloc-owned: connection lists, session/open tables, deferred open queue, event fds, timers, message registrations, id cache entries, profiling trace state, account policy handles, pthread pool, and address metadata. Persistent external state can be affected indirectly through CTDB IP registration, account policy DB initialization, log reopening/rotation, service reloads, and optional process chroot.

## Dependencies And Integration Points
This file sits between socket transport, NetBIOS session handling, SMB1/SMB2 protocol processors, CTDB clustering, Samba messaging, authentication/session tables, id cache, file and directory subsystems, oplocks, printing queues, loadparm configuration, pthreadpool tevent, and profiling. It also includes fallback SMB2-only receive/send code when SMB1 support is compiled out.

## Risks And Test Signals
High-value tests include SMB2-only initial negotiation, SMB1 negprot bootstrap into SMB2, rejection of invalid initial packet types, host allow/deny negative session response, deferred open scheduling/removal/retry ordering, CTDB release-IP clean termination, id-cache kill only when an id is in use, SIGHUP reload, deadtime idle shutdown, housekeeping reload/log checks, and chroot failure handling. Watch for connection state races during forced disconnect, use-after-free in deferred buffers, table initialization rollback leaving `protocol` stale, and event trace stackframe leaks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_query_directory.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_query_directory.c

## Purpose
This file implements SMB2 QUERY_DIRECTORY handling. It parses the SMB2 request, validates file ids and buffer sizes, maps SMB2 find information classes to source3 directory enumeration levels, maintains per-handle directory pointer state, marshals directory entries, and optionally fetches DOS mode and creation time asynchronously.

## Important APIs, Types, And Functions
The request entry point is `smbd_smb2_request_process_query_directory()`. The async implementation is `smbd_smb2_query_directory_send()`/`recv()` with state in `struct smbd_smb2_query_directory_state`. Enumeration is driven by `smb2_query_directory_next_entry()`, which calls `smbd_dirptr_lanman2_entry()`. Async DOS mode support uses `fetch_dos_mode_send()`/`recv()`, `dos_mode_at_send()`, `dos_mode_at_recv()`, and callbacks `smb2_query_directory_dos_mode_done()` and `fetch_dos_mode_done()`.

## Control Flow
The top-level parser verifies a 0x21-byte body, input name offset/length, minimum output buffer size, UTF-16 to Unix conversion, NUL safety, credit charge, and fsp lookup. The send path rejects non-directory handles, empty or slash-containing masks, shadow-copy timestamp masks, oversized buffers, unsupported find classes, and POSIX information on non-POSIX handles. It can reopen a directory for `SMB2_CONTINUE_FLAG_REOPEN`, canonicalizes non-wildcard last components, creates or rewinds `fsp->dptr`, allocates an output buffer with a safety margin, applies `dont descend`, configures async DOS mode, then loops entries until full, single-entry, no-more-files, async backpressure, or injected delay. The done path emits an 8-byte SMB2 body plus the dynamic output buffer.

## State And Persistence
Enumeration state persists on the open directory handle via `fsp->dptr`; subsequent calls distinguish first empty status `NT_STATUS_NO_SUCH_FILE` from later `STATUS_NO_MORE_FILES`. The tevent request tracks output buffer pointers, last entry offset, async DOS-mode job count, `max_count`, and delay state. No durable disk state is modified.

## Dependencies And Integration Points
This code integrates SMB2 request framing, file-id lookup, source3 directory pointer APIs, wildcard/case handling, `dont descend` share configuration, trans2 find marshalling, POSIX directory handles, pthreadpool-backed DOS mode lookup, per-thread CWD support, VFS stat/create-time helpers, and SMB2 async internal request marking.

## Risks And Test Signals
Tests should cover all supported find classes, invalid info class, POSIX find class gating, restart/single/reopen flags, empty first scan versus exhausted later scan, wildcard and case-preserved masks, illegal UTF-16 and embedded NUL names, shadow-copy timestamp masks, client max-trans violations, credit-charge failures, async DOS-mode completion ordering, DFS-link DOS mode preservation, and delay injection. Key risks are output buffer overrun/truncation, wrong last-entry next offset, leaked `smb_fname` during async mode, incorrect status mapping when the buffer is too small, and request lifetime while async jobs are attached to an fsp.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_query_directory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_read.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_read.c

## Purpose
This file implements SMB2 READ handling for regular files and IPC named pipes. It validates read requests, enforces maximum read and credit charge rules, dispatches named-pipe reads asynchronously, tries VFS AIO for file reads, falls back to strict-lock-checked synchronous reads, and can use a sendfile fast path when the response can be sent directly from the file to the socket.

## Important APIs, Types, And Functions
The request entry point is `smbd_smb2_request_process_read()`. Async file logic lives in `smbd_smb2_read_send()`/`recv()` and `struct smbd_smb2_read_state`. Completion and error normalization are handled by `smb2_read_complete()`. Sendfile setup and transfer use `schedule_smb2_sendfile_read()` and `smb2_sendfile_send_data()`, with fallback helpers `fake_sendfile()` and `sendfile_short_send()` from the reply helper file. Named pipes use `np_read_send()`/`np_read_recv()` and cancellation through `smbd_smb2_read_ipc_cancel()`. File AIO cancellation calls `cancel_smb2_aio()`.

## Control Flow
The top-level parser verifies the 0x31-byte body, reads SMB3 flags when applicable, checks `max_read`, verifies credit charge, resolves the volatile/persistent file id, starts `smbd_smb2_read_send()`, and queues the request pending. The send path rejects directories, creates a fake SMB request, routes IPC handles to `np_read_send()` with an fsp async link, checks file read access, tries `schedule_smb2_aio_read()`, falls back to strict byte-range lock checking, tries sendfile if signing, encryption, compounding, streams, file type, offset, and file size permit it, and otherwise reads into a talloc data blob with `read_file()`. The done callback builds the SMB2 read response body and dynamic data blob.

## State And Persistence
The operation is read-only for file contents, but it creates transient tevent state, pipe subrequests, fsp AIO links, output blobs, and sendfile queue metadata. The sendfile path deliberately transfers ownership of the read state to the SMB2 send queue and uses a destructor to perform socket I/O after headers are built. No persistent Samba database state is updated.

## Dependencies And Integration Points
This file integrates SMB2 request/response helpers, file-id lookup, access macros, strict locking, VFS AIO and sendfile hooks, named-pipe RPC handles, cancellation infrastructure, talloc lifetimes, and lower-level socket write helpers. It also depends on server signing/encryption/compound state to decide whether zero-copy sendfile is legal.

## Risks And Test Signals
Tests should cover max-read and credit violations, closed handles, directory read rejection, access denied, strict lock conflict, zero-length reads, EOF versus minimum-count behavior, AIO success/cancel/error, named-pipe success/cancel/broken pipe/status mapping, sendfile eligibility exclusions, sendfile `ENOSYS`/`ENOTSUP`/`EINTR` fallback, file truncation during sendfile causing zero-fill, and torture body padding. Risks include wrong lifetime for sendfile state, sending data on encrypted or signed requests, returning EOF too aggressively for pipe reads, and failing to detach outstanding async activity during close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_reply.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_reply.c

## Purpose
This file contains common smbd reply helpers used by SMB1 and SMB2 paths. It normalizes and validates paths, strips DFS prefixes, handles NetBIOS session-level special messages, validates quota fake handles, implements unlink/delete-on-close, supports read/write sendfile fallback helpers, performs rename and copy internals, and executes byte-range unlocks.

## Important APIs, Types, And Functions
Path helpers include `check_path_syntax()`, `smb2_strip_dfs_path()`, `srvstr_get_path()`, `srvstr_get_path_posix()`, `srvstr_get_path_req()`, and `srvstr_pull_req_talloc()`. Session helpers include `reply_special()`, `netbios_session_retarget()`, and `reply_called_name_not_present()`. File operation helpers include `unlink_internals()`, `fake_sendfile()`, `sendfile_short_send()`, `rename_internals_fsp()`, `rename_internals()`, `copy_file()`, `get_lock_offset()`, and `smbd_do_unlocking()`. Rename support uses `can_rename()`, `rename_open_files()`, `notify_rename()`, and share-mode rename messaging.

## Control Flow
Path syntax checking rewrites separators, collapses `.` and `..` components, rejects invalid Windows characters and stream syntax, preserves multibyte characters, and optionally follows POSIX pathname rules. DFS path handling strips server/share prefixes for SMB2 or normalizes SMB1/DFS strings before local validation. `reply_special()` answers NetBIOS session requests, keepalives, called-name rejection, and retarget responses. `unlink_internals()` stats and filters attributes, opens the target with `DELETE_ACCESS`, checks delete-on-close, sets delete-on-close across all opens for the file id, and closes. Rename opens or uses a source fsp, resolves destination and case-change semantics, rejects open streams and parent-to-child renames, checks destination collisions/open targets/parent access, calls VFS rename, updates local and remote open-file names through share-mode messaging, sets archive bit, and emits notify events. Unlocking validates lock-capable fsp state, runs under the share-mode byte-range lock, unlocks each element, and wakes waiters.

## State And Persistence
Persistent effects include delete-on-close marking, filesystem rename/copy operations, DOS attribute updates, close write time changes, notification delivery, byte-range lock removal, and open-file name updates in local and remote smbd processes. Transient state includes talloc path buffers, NetBIOS output buffers, synthetic `smb_filename` objects, share-mode locks, and copied old filenames for notifications.

## Dependencies And Integration Points
The file integrates string conversion, DFS and POSIX path handling, NetBIOS name service helpers, loadparm retarget configuration, VFS create/rename/copy/stat/sendfile operations, share-mode and byte-range lock databases, SMB2 POSIX create contexts, notification and directory lease break signaling, alternate stream handling, fake quota files, and low-level socket writes. It supplies helpers directly consumed by SMB2 read, setinfo, create, lock, and directory code as well as SMB1 compatibility paths.

## Risks And Test Signals
Tests should cover path normalization for repeated separators, `..`, POSIX `.` handling, streams, wildcards before streams, invalid control characters, DFS server/share stripping, NetBIOS retarget and invalid names, unlink hidden/system/directory/POSIX symlink behavior, delete-on-close sharing checks, same-directory case-only rename, replace-if-exists with open destination, stream rename, directory parent-to-child rejection, rename notification pairs, archive-bit updates, copy partial transfer/disk-full handling, large lock offset parsing, and unlock invalid-element failure. Risks include Windows compatibility edge cases, open-file rename propagation across shares, incorrect status codes for attribute mismatches, and socket termination after partial sendfile headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_reply.c -->
