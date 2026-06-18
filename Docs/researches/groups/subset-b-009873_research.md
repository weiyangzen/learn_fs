# Research: subset-b-009873

Grouped research for Samba `source3/smbd` SMB2 create, flush, getinfo, glue, IOCTL, IPC, keepalive, lock, negotiate, and notify handlers. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_create.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_create.c

Purpose: implements the SMB2 CREATE command in the source3 file server. It decodes the SMB2 create request, validates dynamic name and create-context buffers, converts the UTF-16 pathname, opens files/directories/pipes/printer handles through the existing SMB1-compatible `smb_request` and VFS layers, handles durable handles, leases, replay cache records, POSIX create context data, reparse/symlink errors, and builds the SMB2 CREATE response.

Important APIs and types: `smbd_smb2_request_process_create()` is the packet entry point. `smbd_smb2_create_send()` / `smbd_smb2_create_recv()` are the tevent async operation. `struct smbd_smb2_create_state` carries decoded create contexts, durable/replay fields, lease state, VFS result `files_struct`, output attributes, and symlink error data. `map_smb2_oplock_levels_to_samba()` and `map_samba_oplock_levels_to_smb2()` bridge wire oplock levels to Samba internal oplock flags. `smbd_smb2_create_fetch_create_ctx()`, `smbd_smb2_create_before_exec()`, `smbd_smb2_create_after_exec()`, and `smbd_smb2_create_finish()` split create-context parsing, backend execution setup, response-context construction, and final response field capture. Deferred-open helpers include `push_deferred_open_message_smb2()`, `open_was_deferred_smb2()`, `schedule_deferred_open_message_smb2()`, and `remove_deferred_open_message_smb2()`.

Control flow: the request processor verifies the fixed body size `0x39`, extracts access masks, disposition/options, name and context offsets, checks both dynamic buffer ranges against the incoming iovec, converts the name from UTF-16 to Unix charset, rejects embedded NUL/name-size mismatches, parses create contexts with `smb2_create_blob_parse()`, then starts `smbd_smb2_create_send()`. The send path creates a fake SMB1 request with `smbd_smb2_fake_smb_request()`, strips DFS prefixes when requested, records the request GUID, disables ignored sync/async alert bits, collects create contexts, and handles fast paths for IPC named pipes and printer shares. Normal filesystem opens run `windows_name_trailing_check()`, pre-execute parsing of contexts such as DHNQ/DH2Q/DHNC/DH2C/RQLS/EXTA/MXAC/SECD/ALSI/TWRP/QFID/POSX, then choose one of three backend modes: replay an existing open, durable reconnect, or fresh `SMB_VFS_CREATE_FILE()`. After VFS open, it checks reparse behavior, durable cookies, replay cache updates, maximum-access/QFID/lease/POSIX response contexts, then finalizes timestamps, allocation size, EOF, attributes, and persistent/volatile file IDs. The done callback serializes output create contexts and the `0x58` CREATE response body or returns a symlink-specific SMB2 error context for `NT_STATUS_STOPPED_ON_SYMLINK`.

State and persistence: durable and replay behavior persists in `smbXsrv_open` records, backend cookies, create GUIDs, replay cache entries, durable timeout fields, and the open-global durable/replay flags. Lease state is persisted via `files_struct->lease` and `smbXsrv_open` metadata. Deferred opens store request time, file ID, `deferred_open_record`, timeout/cancel state, and can be redispatched via tevent immediate callbacks. POSIX path state is carried by `smb_request.posix_pathnames` and later by `fsp` flags. File-system side effects are delegated to VFS create, durable reconnect, allocation, EA, security descriptor, and reparse helpers.

Dependencies and integration: depends on SMB2 packet helpers, create-context marshalling, NDR security and SMB3 POSIX structures, leases/oplocks, `smbXsrv_open`, DFS path stripping, filename conversion, `SMB_VFS_CREATE_FILE()`, `SMB_VFS_DURABLE_RECONNECT()`, `SMB_VFS_DURABLE_COOKIE()`, EA parsing, security descriptor NDR, reparse helpers, print spool open, named-pipe open, share-mode/deferred-open messaging, and the compatibility `smb_request` bridge in `smb2_glue.c`. Other SMB2 commands consume the resulting `files_struct` through persistent/volatile IDs and compound chaining.

Risks: dynamic buffer validation allows name and context ranges to overlap by design, so downstream parsing must be robust. Durable/replay logic has many protocol-specific status distinctions (`OBJECT_NAME_NOT_FOUND`, `DUPLICATE_OBJECTID`, `FILE_NOT_AVAILABLE`, `HANDLE_NO_LONGER_VALID`) that are easy to regress. Replay plus lease validation depends on exact lease-key matching. Reparse/symlink error response shape differs before and after SMB 3.1.1. Deferred-open redispatch deliberately clears callbacks before reprocessing; mistakes here can double-complete a tevent request. Fresh opens enforce leading slash/backslash rules after durable-reconnect exceptions, so path validation tests need to distinguish reconnect from local open. POSIX create context changes filename syntax and EA validation behavior.

Test signals: Samba selftest lists SMB2 create-path suites such as `SMB2-BASIC`, `SMB2-PATH-SLASH`, DFS path tests, durable-open/durable-v2/replay/durable-v2-delay, `smb2.create_no_streams`, `smb2.twrp`, `smb2.lease`, `smb2.dirlease`, `smb2.fileid`, stream and EA suites, plus symlink traversal and `samba.tests.smb2symlink`. Focused coverage should exercise malformed create contexts, durable reconnect with/without matching lease, replay flag behavior, DFS prefix stripping, POSIX create contexts, stopped-on-symlink error buffers, IPC/printer non-durable fast paths, deferred-open cancellation/redispatch, and compound create error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_flush.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_flush.c

Purpose: implements SMB2 FLUSH for an open file or directory handle. It validates the handle, checks access, optionally issues an asynchronous VFS fsync, and returns the SMB2 flush response body.

Important APIs and types: `smbd_smb2_request_process_flush()` is the packet entry point. `smbd_smb2_flush_send()` / `smbd_smb2_flush_recv()` wrap the operation. `struct smbd_smb2_flush_state` stores the SMB2 request and target `files_struct`. `smbd_smb2_flush_done()` receives `SMB_VFS_FSYNC_SEND()` completion.

Control flow: the processor verifies fixed size `0x18`, reads persistent and volatile file IDs, resolves them with `file_fsp_smb2()`, starts the tevent helper, and queues the SMB2 request pending. The helper creates a fake SMB1 request, rejects IPC handles, requires write or append access, permits directory flush only when opened with `FILE_ADD_FILE` or `FILE_ADD_SUBDIRECTORY`, rejects handles without an I/O fd, and returns immediately when `strict sync` is disabled. With strict sync enabled it starts `SMB_VFS_FSYNC_SEND()`, forces synchronous completion for non-last compound requests by marking the request async-internal, adds the request to the fsp AIO list so close waits for it, and maps VFS errors back to NT status. The done callback emits the `0x04` response body.

State and persistence: no durable state is created by this file. State is temporary tevent state plus the outstanding AIO registration on the `files_struct`. Persistent effects are the VFS-level flush/sync side effects on backend storage when strict sync is enabled.

Dependencies and integration: depends on SMB2 body helpers, `file_fsp_smb2()`, fake SMB1 request creation, access checks, loadparm `lp_strict_sync()`, VFS async fsync hooks, AIO tracking, compound request helpers, and NT/unix error mapping. It integrates with close by adding outstanding fsync operations to the fsp async list.

Risks: access rules for directory flush are subtle because directories are not conventionally writable but Windows-compatible flush allows add-file/add-subdirectory access. Compound handling matters because only the last compound element can safely go fully async. If a VFS module returns an unexpected errno, the client-visible status depends on `map_nt_error_from_unix()`. Handles without I/O fds must return `INVALID_HANDLE` rather than silently succeeding.

Test signals: SMB2 basic and directory fsync suites (`SMB2-DIR-FSYNC`) should cover file and directory flush behavior. Additional useful cases include strict-sync on/off, IPC flush, read-only handle denial, directory handle with and without add permissions, compound non-last flush, invalid/closed file IDs, and close waiting for an outstanding async fsync.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_getinfo.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_getinfo.c

Purpose: implements SMB2 GETINFO for file, filesystem, security, and quota information. It bridges SMB2 query requests into existing source3 query path, filesystem, security descriptor, and quota helpers while enforcing SMB2 max-transfer and credit-charge rules.

Important APIs and types: `smbd_smb2_request_process_getinfo()` decodes the packet. `smbd_smb2_getinfo_send()` / `smbd_smb2_getinfo_recv()` carry the async-compatible operation. `struct smbd_smb2_getinfo_state` stores the output blob and a call status that can differ from transport success. `smb2_ipc_getinfo()` provides the named-pipe `SMB2_FILE_STANDARD_INFO` compatibility response.

Control flow: the processor verifies size `0x29`, extracts info type/class, output length, input-buffer offset/length, additional information, flags, and file ID. It enforces that non-empty input begins exactly after the fixed body, bounds input and output lengths by negotiated `max_trans`, verifies credit charge for the larger input/output length, resolves the handle, and queues the send helper. The helper creates a fake SMB1 request and handles IPC standard info. For `SMB2_0_INFO_FILE` it enforces read-attribute/read-EA access for selected classes, maps SMB2 classes to passthrough/trans2 levels, validates POSIX and normalized-name availability, refreshes stat data, optionally queries share-mode delete-pending state, and calls `smbd_do_qfilepathinfo()`. Filesystem info maps classes to passthrough or POSIX levels and calls `smbd_do_qfsinfo()`. Security info calls `smbd_do_query_security_desc()` and returns a 4-byte needed-size blob for `BUFFER_TOO_SMALL`. Quota info, when compiled with quotas, validates a quota fake handle, pulls `smb2_query_quota_info` with NDR, rejects unsupported single-start-SID form, and calls `smbd_do_query_getinfo_quota()`. The done callback returns error-with-data for non-OK call statuses except `STATUS_BUFFER_OVERFLOW`, otherwise emits an `0x08` response body and dynamic output.

State and persistence: mostly read-only. It refreshes `fsp->fsp_name->st` via stat/fstat and reads share-mode delete-pending state. Quota query may maintain scan state in the quota subsystem, but this file only passes query flags and SID lists through. Output buffers are talloc-owned and moved to the SMB2 response.

Dependencies and integration: depends on trans2 query implementations, generated quota/security NDR, VFS stat/fstat, access checks, share-mode info, security descriptor helpers, quota helpers, and fake SMB1 request compatibility. It integrates with file opens from `smb2_create.c` through `files_struct` and with negotiated limits from `smb2_negprot.c`.

Risks: `fixed_portion` versus output-buffer length handling decides whether to return `INFO_LENGTH_MISMATCH` or truncated `STATUS_BUFFER_OVERFLOW`. Class mapping must preserve Windows-compatible status translations from `INVALID_LEVEL` to `INVALID_INFO_CLASS`. POSIX information must only work for POSIX opens. Security descriptor `BUFFER_TOO_SMALL` is intentionally returned as an error with a data payload. Quota support is compile-time conditional, so behavior differs across builds.

Test signals: Samba selftest entries include SMB2 basic, quota (`SMB2-QUOTA1`), fileid, POSIX/Unix extension paths, ACL/security descriptor tests, and broad `smb2.*` torture suites. Focus tests on max-trans violations, malformed input offsets, each info type, partial-buffer overflow, security descriptor too-small payload, IPC pipe standard info, normalized-name dialect gating, POSIX info on non-POSIX handles, and quota SID-list parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_getinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_glue.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_glue.c

Purpose: provides compatibility glue that lets SMB2 command handlers reuse source3 SMB1-era request, connection, chain-FSP, DFS, and unread-byte infrastructure.

Important APIs and functions: `smbd_smb2_fake_smb_request()` creates or reuses `struct smb_request` for an SMB2 request and fills request time, vuid, tid, connection, server connection, xconn, session, PID, flags2, message ID, compound chain fsp, POSIX pathname flag, and backpointer. `smbd_smb2_unread_bytes()` exposes `smb_request.unread_bytes` to recvfile paths. `remove_smb2_chained_fsp()` clears compound chain references when a `files_struct` is freed.

Control flow: fake request creation pulls fields from the SMB2 header and current tree/session. It always enables Unicode, 32-bit errors, long path components, and long names. It only sets `FLAGS2_DFS_PATHNAMES` when the share is an msdfs root and the incoming SMB2 header has the DFS flag. If an fsp is provided, it mirrors POSIX pathname state from the fsp name flags. Chain cleanup walks every SMB2 connection and request under the server connection's client and clears both `smb2req->compat_chain_fsp` and `smb1req->chain_fsp` if they point to the freed handle.

State and persistence: the fake SMB1 request is talloc-owned by the SMB2 request and cached in `req->smb1req`. Chain-FSP state is in-memory compound request state only. No persistent storage is touched.

Dependencies and integration: used by create, flush, getinfo, ioctl, lock, notify, and other SMB2 handlers before calling source3 helpers that expect `struct smb_request`. Depends on SMB2 header macros, loadparm DFS settings, `files_struct`, `smbd_server_connection`, and `smbXsrv_connection` lists.

Risks: incorrect fake request fields can subtly break authorization, DFS parsing, POSIX path handling, message IDs for deferred operations, or compound chaining. Chain cleanup must scan all SMB2 requests because a freed fsp may still be referenced by pending compound state. Reusing an existing `req->smb1req` means later calls must tolerate previously filled fields.

Test signals: broad SMB2 compound, DFS, POSIX, and pipe tests exercise this glue indirectly. Specific coverage should include DFS flag only on DFS shares, POSIX flag propagation from fsp, compound create/query chains, unread-byte propagation for recvfile, and fsp free during pending compound requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_ioctl.c

Purpose: implements the SMB2 IOCTL/FSCTL front door. It validates wire buffer offsets, max input/output lengths, credit charge, FSCTL flags, handle requirements, dispatches by device type to specialized modules, and formats SMB2 IOCTL success or allowed-status responses.

Important APIs and types: `smbd_smb2_request_process_ioctl()` is the packet entry point. `smbd_smb2_ioctl_send()` / `smbd_smb2_ioctl_recv()` wrap dispatch. `struct smbd_smb2_ioctl_state`, declared in `smb2_ioctl_private.h`, carries shared IOCTL state. `smbd_smb2_ioctl_is_failure()` decides which NT statuses are protocol-level failures versus valid IOCTL responses with data.

Control flow: the processor verifies body size `0x39`, extracts control code, file IDs, input/output offsets and lengths, maximum lengths, and flags. It checks that input and output buffers live inside the incoming dynamic area, permits Windows clients to set arbitrary input offset when input length is zero, rejects output ranges that overlap before the input data end, detects integer overflow when computing credit-charge length, and enforces `SMB2_IOCTL_FLAG_IS_FSCTL`. Some control codes are handleless and require both file IDs to be all ones; all other codes resolve a handle with `file_fsp_smb2()`. The send helper creates a fake SMB1 request and dispatches on `in_ctl_code & IOCTL_DEV_TYPE_MASK` to DFS, filesystem, named pipe, network filesystem, or smbtorture modules. The done callback receives output, handles a backend-requested disconnect, enforces `in_max_output_length` unless the backend explicitly returned truncated overflow, maps failures to SMB2 error packets, and otherwise emits the `0x30` response body plus optional body padding and output data.

State and persistence: state is per-request talloc data. If an IOCTL goes async against an fsp, it is added to the fsp AIO list so close/logoff/tree disconnect can wait or cancel consistently. The front door itself does not persist data, but dispatched FSCTLs may mutate files, compression, sparse extents, pipe state, connection validation, or torture flags.

Dependencies and integration: depends on SMB2 packet helpers, `include/ntioctl.h`, generated `ioctl` NDR for structures used by submodules, fake SMB1 request glue, AIO tracking, and the private IOCTL module interface. It integrates with `smb2_ioctl_dfs.c`, `smb2_ioctl_filesys.c`, `smb2_ioctl_named_pipe.c`, `smb2_ioctl_network_fs.c`, and `smb2_ioctl_smbtorture.c`.

Risks: buffer offset arithmetic is security-sensitive and has multiple edge cases around zero-length input/output, overlap, and uint32 overflow. Handleless FSCTLs must reject real handles while handle-bound FSCTLs must reject closed handles. The allowed-status list must preserve protocol behavior for `STATUS_BUFFER_OVERFLOW` and copychunk responses. Body padding exists only for torture controls and can alter response layout. If an async subrequest is not added to the fsp list, close may free state too early.

Test signals: Samba selftest lists `smb2.ioctl`, `smb2.ioctl-on-stream`, `NTTRANS-FSCTL`, DFS referral tests, network interface/multichannel tests, named-pipe async disconnect tests, copychunk/offload tests, and smbtorture-specific FSCTLs. Targeted tests should fuzz offset/length combinations, non-FSCTL flags, handleless controls with real handles, handle-bound controls with all-ones IDs, output overflow, allowed error-with-data responses, async close behavior, and body padding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl_dfs.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_ioctl_dfs.c

Purpose: handles DFS-related SMB2 FSCTLs, especially `FSCTL_DFS_GET_REFERRALS`, and falls back to VFS FSCTL dispatch for other DFS-device controls.

Important APIs and functions: `smb2_ioctl_dfs()` is the module dispatcher called by `smb2_ioctl.c`. `fsctl_dfs_get_refers()` decodes the referral request, converts the UTF-16 path, calls DFS referral generation, and packages the response.

Control flow: `FSCTL_DFS_GET_REFERRALS` first requires `lp_host_msdfs()`, a minimum 4-byte input, then reads the max referral level and converts the rest of the input buffer from UTF-16 to Unix string. It calls `setup_dfs_referral()` on the current connection. If the referral data exceeds `in_max_output`, it truncates to the advertised max and returns `STATUS_BUFFER_OVERFLOW`; otherwise it returns OK. Unknown DFS control codes dispatch to `SMB_VFS_FSCTL()` if an fsp exists, then translate `NOT_SUPPORTED` to `FS_DRIVER_REQUIRED` on IPC or `INVALID_DEVICE_REQUEST` elsewhere.

State and persistence: no persistent state is written. It reads DFS configuration and builds a transient output blob from `setup_dfs_referral()` data.

Dependencies and integration: depends on DFS loadparm settings, UTF-16 conversion, `setup_dfs_referral()`, `SAFE_FREE`, VFS FSCTL fallback, and the shared IOCTL state. It is selected for control codes whose device type is `FSCTL_DFS`.

Risks: referral output truncation is explicitly marked as needing more test coverage. Path conversion errors must return `ILLEGAL_CHARACTER`. Host DFS disabled maps to `FS_DRIVER_REQUIRED`, while fallback unsupported behavior depends on IPC versus filesystem share. Memory ownership crosses from `setup_dfs_referral()` allocated buffers into a talloc data blob.

Test signals: selftest includes `SMB2-DFS-PATHS`, `SMB2-DFS-FILENAME-LEADING-BACKSLASH`, `SMB2-NON-DFS-SHARE`, `SMB2-DFS-SHARE-NON-DFS-PATH`, and msdfs attribute tests. Add cases for malformed short input, invalid UTF-16, disabled host DFS, output truncation/overflow, referral level variants, and unsupported DFS control fallback status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl_dfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl_filesys.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_ioctl_filesys.c

Purpose: handles filesystem-device FSCTLs for compression, sparse/zero data, allocated range queries, and duplicate extents/reflink-like cloning, with fallback to VFS FSCTL for unhandled controls.

Important APIs and types: `smb2_ioctl_filesys()` dispatches filesystem controls. `fsctl_get_cmprn()` and `fsctl_set_cmprn()` implement `FSCTL_GET_COMPRESSION` and `FSCTL_SET_COMPRESSION`. `fsctl_zero_data()` implements `FSCTL_SET_ZERO_DATA`. `fsctl_qar()` plus `fsctl_qar_seek_fill()` and `fsctl_qar_buf_push()` implement `FSCTL_QUERY_ALLOCATED_RANGES`. `fsctl_dup_extents_send()` / `fsctl_dup_extents_recv()` and helpers implement async `FSCTL_DUP_EXTENTS_TO_FILE` through VFS offload read/write.

Control flow: compression query returns the VFS compression format when filesystem capabilities advertise `FILE_FILE_COMPRESSION`; otherwise it returns `COMPRESSION_FORMAT_NONE` for Windows-compatible behavior. Compression set requires `FILE_WRITE_DATA`, NDR-pulls a `compression_state`, calls VFS set when supported, and accepts setting `NONE` even when compression is unsupported. Zero-data requires `FILE_WRITE_DATA`, NDR-pulls `file_zero_data_info`, checks range ordering, validates strict write-lock compatibility, punches a hole with keep-size semantics, and optionally reallocates the range under strict allocation for non-sparse files. Allocated range query requires `FILE_READ_DATA`, NDR-pulls the request, handles zero/out-of-EOF requests as empty, validates overflow and minimum response size, returns one full range for non-sparse files, or uses `SEEK_DATA`/`SEEK_HOLE` when available for sparse files, returning truncated `STATUS_BUFFER_OVERFLOW` when output fills. Duplicate extents requires a destination fsp on a block-refcounting filesystem, NDR-pulls source fid/off/target/length, resolves source fsp on the same device, validates source/target sizes, caps target length to existing target EOF to match Windows, rejects overlapping same-file ranges and sparse source to non-sparse target, obtains an offload token, then sends `SMB_VFS_OFFLOAD_WRITE_SEND()` and verifies all requested bytes cloned.

State and persistence: compression and zero-data mutate file metadata/data through VFS. Duplicate extents mutates target file extents through offload write while tracking async state in `struct fsctl_dup_extents_state`. Query allocated ranges is read-only but depends on live file size and sparse flags. No repository-level persistent state is maintained here.

Dependencies and integration: depends on generated `ndr_ioctl` structures, VFS compression/fallocate/lseek/offload hooks, strict lock checks, access checks, `file_fsp_get()`, filesystem capability flags, `sys_io_ranges_overlap()`, and common IOCTL response handling. Fallback uses `SMB_VFS_FSCTL()` and maps unsupported status using IPC/filesystem context.

Risks: range arithmetic must avoid overflow and off-by-one errors around EOF. `FSCTL_SET_ZERO_DATA` uses fallocate hole-punch behavior that varies by filesystem and must not extend file size. Query allocated ranges has build-dependent behavior when `HAVE_LSEEK_HOLE_DATA` is absent. Duplicate extents deliberately caps target length when the request exceeds target size, which is Windows-compatible but non-obvious. Same-file overlap, sparse-flag compatibility, and source/destination volume checks are correctness-sensitive.

Test signals: `smb2.ioctl`, `smb2.ioctl-on-stream`, VFS copy/offload, sparse-file, and filesystem capability suites should hit these paths. Focused tests should cover compression unsupported vs supported, set compression `NONE` without support, zero-length and reversed zero-data ranges, strict-lock conflict, strict allocation after hole punch, allocated ranges on sparse/non-sparse files, too-small QAR output, duplicate extents invalid source fid, cross-volume source, overlapping same-file clone, zero byte clone, target EOF capping, and VFS offload short-write error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl_filesys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl_named_pipe.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_ioctl_named_pipe.c

Purpose: handles named-pipe FSCTLs, primarily `FSCTL_PIPE_TRANSCEIVE`, by asynchronously writing request bytes to a named pipe and reading the reply, while falling back to VFS FSCTL for other named-pipe device controls.

Important APIs and functions: `smb2_ioctl_named_pipe()` dispatches named-pipe controls. `smbd_smb2_ioctl_pipe_write_done()` handles `np_write_send()` completion. `smbd_smb2_ioctl_pipe_read_done()` handles `np_read_send()` completion and overflow signaling.

Control flow: `FSCTL_PIPE_TRANSCEIVE` requires an IPC connection, a non-null fsp, and `fsp_is_np()`. It writes the input buffer to `fsp->fake_file_handle` with `np_write_send()`. The write callback maps pipe transport errors through `nt_status_np_pipe()`, checks that the full input length was written, allocates an output buffer of `in_max_output`, and starts `np_read_send()`. The read callback maps pipe errors, shrinks output length to bytes read, returns `STATUS_BUFFER_OVERFLOW` when more pipe data remains, and completes otherwise. Other named-pipe controls use `SMB_VFS_FSCTL()` when an fsp exists, then map unsupported status to `FS_DRIVER_REQUIRED` on IPC or `INVALID_DEVICE_REQUEST` elsewhere.

State and persistence: per-request state lives in the shared IOCTL state. Pipe state is external to this file in the named-pipe server/fake file handle. Output buffers are talloc-owned by the IOCTL state.

Dependencies and integration: depends on IPC checks, named-pipe fake file handles, `np_write_send/recv`, `np_read_send/recv`, pipe status mapping in `smb2_ipc.c`, VFS FSCTL fallback, and common IOCTL error-with-data handling. It integrates with SMB2 CREATE on IPC shares, which opens pipe handles.

Risks: partial pipe write is treated as `PIPE_NOT_AVAILABLE`; changing this can alter client retry behavior. `STATUS_BUFFER_OVERFLOW` is an allowed IOCTL response with partial data, so the front door must not convert it into a generic error. The async read/write pair must survive close correctly via the front-door AIO registration. Non-IPC status mapping must distinguish unsupported pipe controls from invalid devices.

Test signals: selftest includes named-pipe SMB2/RPC tests such as invalid pipe name, SMB2 pipe async disconnect, and broad RPC-over-SMB2 tests. Add cases for transceive on non-IPC, null/closed fsp, non-pipe fsp, partial pipe output overflow, pipe disconnect/reset mapping, zero max output, and close while transceive is pending.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl_named_pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl_network_fs.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_ioctl_network_fs.c

Purpose: handles network-filesystem FSCTLs for server-side copy chunk, resume-key generation, network interface enumeration for multichannel, and validate-negotiate-info connection checks.

Important APIs and types: `smb2_ioctl_network_fs()` dispatches network FS controls. `fsctl_srv_copychunk_send()` / `fsctl_srv_copychunk_recv()` and `struct fsctl_srv_copychunk_state` implement `FSCTL_SRV_COPYCHUNK` and `FSCTL_SRV_COPYCHUNK_WRITE`. `copychunk_check_limits()` and `copychunk_pack_limits()` enforce and report server copy limits. `fsctl_network_iface_info()` emits interface data. `fsctl_validate_neg_info()` validates client replay of negotiation properties. `smb2_ioctl_network_fs_offload_read_done()` packages `FSCTL_SRV_REQUEST_RESUME_KEY` responses.

Control flow: copychunk requires enough output space for `srv_copychunk_rsp`, NDR-pulls a copychunk request, validates chunk count, per-chunk length, non-zero lengths, and total length. It stores the source token from the request and loops over chunks, sending `SMB_VFS_OFFLOAD_WRITE_SEND()` to the destination fsp for each chunk. Zero-chunk requests still call VFS once to support macOS copyfile semantics and then return zero chunks written. On limit failure it returns a packed limit response even with an error status. Network interface info requires empty input and multichannel enabled, refreshes local interfaces, optionally collects CTDB public movable IPs, skips movable public IPs except the current connection address, skips non-IP and zero-link-speed interfaces, creates a linked list of `fsctl_net_iface_info`, and NDR-pushes it. Validate negotiate info parses capabilities, client GUID, security mode, and dialect list, computes the dialect match, and disconnects the transport on mismatch with connection dialect, GUID, security mode, or capabilities; on success it returns server capabilities, GUID, security mode, and dialect. Resume-key calls `SMB_VFS_OFFLOAD_READ_SEND()` and packages the returned token into `req_resume_key_rsp`.

State and persistence: copychunk mutates destination file data/extents through VFS offload writes and tracks progress in tevent state. Network interface info reads dynamic interface/CTDB state and does not persist. Validate negotiate reads stored `xconn->smb2.client/server` negotiation state and may set `state->disconnect`, causing the front door to terminate the connection. Resume-key exposes backend offload token state without persisting anything in this file.

Dependencies and integration: depends on generated IOCTL NDR, VFS offload hooks, negotiated connection state from `smb2_negprot.c`, multichannel client state, interface discovery, tsocket address helpers, CTDB public IP iteration, and common IOCTL response handling. Copychunk and resume-key depend on backend VFS modules implementing offload semantics.

Risks: `fsctl_srv_copychunk_send()` assumes a valid destination fsp; the front door resolves handles for these codes, but defensive null handling is limited. Copychunk responses intentionally include data on some error paths; front-door status classification must stay aligned. Interface enumeration must not advertise cluster movable addresses incorrectly or clients may open useless multichannel connections. Validate-negotiate mismatch intentionally disconnects the transport, so parsing or comparison bugs can drop valid clients or fail security checks. Copychunk total length accumulation uses a uint32 total and relies on configured max constants; overflow assumptions should be reviewed if limits change.

Test signals: selftest references `smb2.ioctl`, multichannel/network-interface behavior, durable/replay, and clustered SMB2 tests. Focus tests on copychunk limit errors with packed limits, partial chunk failure with response data, zero-chunk/macOS copyfile path, resume key token size mismatch, multichannel disabled status mapping, CTDB movable IP filtering, validate-negotiate success, and each validate-negotiate mismatch causing disconnect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl_network_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl_private.h -->
# sources/user-network-fs/samba/source3/smbd/smb2_ioctl_private.h

Purpose: defines the private shared state and dispatcher prototypes used by the SMB2 IOCTL front door and its device-specific FSCTL modules.

Important APIs and types: `struct smbd_smb2_ioctl_state` carries the parent `smbd_smb2_request`, compatibility `smb_request`, optional `files_struct`, input blob, maximum output length, output blob, optional response body padding, and a disconnect flag. The header declares `smb2_ioctl_dfs()`, `smb2_ioctl_filesys()`, `smb2_ioctl_named_pipe()`, `smb2_ioctl_network_fs()`, and `smb2_ioctl_smbtorture()`, all taking a control code, event context, parent tevent request, and shared state.

Control flow and integration: `smb2_ioctl.c` allocates `struct smbd_smb2_ioctl_state`, fills common request fields, then dispatches to one of the declared functions based on the device type bits in the FSCTL code. Device modules mutate `state->out_output`, `state->body_padding`, or `state->disconnect`, then complete or error the shared tevent request.

State and persistence: the struct is per-request transient state. It can point to an fsp and SMB1 compatibility request but owns no persistent resources itself. Output data ownership is talloc-based and later stolen by the front door into the SMB2 response.

Dependencies: requires Samba core types (`DATA_BLOB`, `files_struct`, `tevent_req`, `tevent_context`, `smb_request`, `smbd_smb2_request`) from normal include ordering. It is intentionally private to `source3/smbd` IOCTL implementation files.

Risks: because all submodules share this struct, adding fields or changing ownership expectations can break async callbacks. `body_padding` and `disconnect` are rare paths and easy to overlook. Prototype drift is caught at build time, but semantic drift around who completes/posts the parent tevent request needs review.

Test signals: build coverage across all IOCTL modules is the primary header test. Runtime signals come from DFS, filesystem, named-pipe, network FS, and smbtorture FSCTL suites verifying that shared output, disconnect, and padding fields reach `smb2_ioctl.c` correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl_smbtorture.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_ioctl_smbtorture.c

Purpose: implements Samba-specific smbtorture FSCTLs gated by the `smbd:FSCTL_SMBTORTURE` parameter. These controls deliberately alter connection/request behavior to test SMB2 timeout, response padding, read response padding, and close-vs-async-handle behavior.

Important APIs and types: `smb2_ioctl_smbtorture()` dispatches torture controls. `struct async_sleep_state` stores the server connection and target fsp for delayed fsp-validity tests. `smbd_fsctl_torture_async_sleep_send()` creates a timed tevent request. `smbd_fsctl_torture_async_sleep_done()` checks whether the original fsp still exists with `files_forall()`.

Control flow: the dispatcher first checks `lp_parm_bool(-1, "smbd", "FSCTL_SMBTORTURE", false)` and otherwise returns device-appropriate unsupported status. `FSCTL_SMBTORTURE_FORCE_UNACKED_TIMEOUT` requires empty input and sets `xconn->ack.force_unacked_timeout`. `FSCTL_SMBTORTURE_IOCTL_RESPONSE_BODY_PADDING8` requires empty input, optionally fills output with byte value 8, sets `body_padding = 8`, and completes. `FSCTL_SMBTORTURE_GLOBAL_READ_RESPONSE_BODY_PADDING8` sets a connection-global read response padding value. `FSCTL_SMBTORTURE_FSP_ASYNC_SLEEP` requires one input byte and a valid fsp, starts a timed request, and on timeout returns OK only if the fsp is still in the server connection's open file list; otherwise it returns `FILE_CLOSED`.

State and persistence: most state is transient, but the unacked-timeout and global read-padding controls set fields on the live SMB2 connection that affect later responses. Async sleep stores a raw fsp pointer intentionally only for existence testing and does not own it.

Dependencies and integration: depends on loadparm private parameter lookup, the shared IOCTL state, tevent endtime handling, `files_forall()`, connection ack/read-padding fields, and common IOCTL response formatting. It integrates with smbtorture client tests rather than normal production clients.

Risks: these FSCTLs intentionally expose non-production behavior and must remain disabled by default. The async fsp test stores a pointer that may be freed; it must only compare identity through `files_forall()` and not dereference after close. Time unit naming is confusing: the comment says microseconds/seconds in places, while the input byte is passed to `timeval_current_ofs(0, msecs)` as microseconds. Padding controls must not leak into production paths unless explicitly enabled.

Test signals: smbtorture-specific SMB2 IOCTL tests should verify disabled-by-default behavior, each input-length validation, response body padding layout, global read padding on subsequent reads, forced unacked timeout behavior, and that async sleep blocks file closure or returns `FILE_CLOSED` when the close wins.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ioctl_smbtorture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ipc.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_ipc.c

Purpose: provides named-pipe status normalization used by SMB2 IPC/named-pipe paths.

Important API: `nt_status_np_pipe()` maps transport-oriented pipe errors to SMB named-pipe statuses: `NT_STATUS_CONNECTION_DISCONNECTED` becomes `NT_STATUS_PIPE_DISCONNECTED`, and `NT_STATUS_CONNECTION_RESET` becomes `NT_STATUS_PIPE_BROKEN`; all other statuses pass through unchanged.

Control flow: the function is a simple status translation helper. It is called after named-pipe read/write operations in `smb2_ioctl_named_pipe.c` so clients receive pipe-domain errors rather than lower-level connection errors.

State and persistence: no state or persistent data.

Dependencies and integration: depends on Samba `NTSTATUS` helpers/macros and is integrated with SMB2 named-pipe transceive and other IPC paths that need Windows-compatible pipe status mapping.

Risks: the mapping is intentionally narrow. Adding or removing translations can change client-visible named-pipe behavior and RPC retry/disconnect logic. Because the helper accepts and returns `NTSTATUS`, build-time checks will not catch semantically wrong mappings.

Test signals: named-pipe/RPC SMB2 tests, especially pipe disconnect/reset and async disconnect cases, should observe `PIPE_DISCONNECTED` or `PIPE_BROKEN` rather than generic connection statuses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_keepalive.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_keepalive.c

Purpose: implements the SMB2 KEEPALIVE/ECHO-style request handler that validates an empty fixed body and returns a minimal success response.

Important API: `smbd_smb2_request_process_keepalive()` is the whole handler. It verifies request size `0x04`, generates a `0x04` response body, sets the structure size and reserved field, and completes the request.

Control flow: invalid size returns an SMB2 error. Allocation failure while generating the response body returns `NO_MEMORY`. On success it calls `smbd_smb2_request_done()` with no dynamic output. A TODO notes that timestamp updates may belong here in the future.

State and persistence: no explicit state changes today. It does not update keepalive timestamps despite the TODO.

Dependencies and integration: depends on SMB2 request size verification, response body allocation, and request completion helpers. It integrates with the SMB2 command dispatch table as a lightweight liveness command.

Risks: because the handler is simple, main risk is protocol conformance around body size and potential future timestamp/idle-time interactions. If timestamps are later added, tests should ensure echo traffic affects idle timeout as intended without masking dead sessions.

Test signals: SMB2 connection/basic tests should cover a successful keepalive, malformed body size, and behavior while signed/encrypted/session states are active.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_keepalive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_lock.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_lock.c

Purpose: implements SMB2 byte-range lock and unlock processing, including multi-lock validation, durable/multichannel lock-sequence replay detection, blocking lock waits, share-mode watch retries, POSIX-versus-Windows lock flavors, and cancellation semantics.

Important APIs and types: `smbd_smb2_request_process_lock()` decodes the packet. `smbd_smb2_lock_send()` / `smbd_smb2_lock_recv()` run the operation. `struct smbd_smb2_lock_element` mirrors wire lock entries; `struct smbd_smb2_lock_state` carries SMB2/SMB1 request pointers, fsp, blocking state, retry/poll intervals, converted `smbd_lock_element` array, and lock sequence tracking. Retry/cancel helpers include `smbd_smb2_lock_try()`, `smbd_smb2_lock_retry()`, `smbd_smb2_lock_cancel()`, and cleanup state update.

Control flow: the request processor verifies size `0x30`, reads lock count, optional SMB2.1+ lock sequence, file IDs, and the first lock entry from the fixed body plus remaining entries from dynamic data. It permits unlocks even when session status is `NETWORK_SESSION_EXPIRED`, resolves the fsp, and queues the send helper. The send helper creates fake SMB1 state, decides whether lock-sequence checking applies based on multichannel capability or durable handles unless disabled by loadparm, detects replayed sequences from `fsp->op->global->lock_sequence_array`, validates flags and blocking rules, converts each entry to `smbd_lock_element` with request GUID, persistent open ID, offset/count, lock flavor, and read/write/unlock type. Unlock batches call `smbd_do_unlocking()` synchronously. Lock batches call `smbd_smb2_lock_try()`, which checks lock capability and calls `share_mode_do_locked_brl()`. Backend retry/status handling may set timers, watch share-mode changes with `share_mode_watch_send()`, poll POSIX locks, or fail non-blocking locks. Successful async locks update the lock-sequence element in cleanup. Cancellation returns `RANGE_NOT_LOCKED` for close/logoff/tree-disconnect induced cancellation and `CANCELLED` otherwise.

State and persistence: locks persist in Samba byte-range lock/share-mode databases via backend lock helpers. Lock-sequence replay state persists in the `smbXsrv_open` global lock sequence array for durable/multichannel behavior. Pending blocking locks are tracked as tevent requests added to the fsp async list and wake on share-mode watch events or timers.

Dependencies and integration: depends on `share_mode_lock`, byte-range lock helpers, `dbwrap_watch`, generated open-files structures, messages, fake SMB1 requests, loadparm lock settings, access/open flags, and `smbXsrv_open` durable/multichannel state. It integrates with close/logoff/tdis cancellation and with negotiated multichannel capability from `smb2_negprot.c`.

Risks: lock flag validation is protocol-sensitive, especially mixed unlock/lock batches and multi-lock blocking rules. Lock sequence behavior intentionally differs from Windows in some cases unless `smb2 disable lock sequence checking` is set. POSIX handles use POSIX lock flavor and reject write locks on read-only handles, while macOS fruit POSIX-open behavior intentionally follows Windows flavor based on filename flags. Retry loops can wait indefinitely if a backend keeps returning `NT_STATUS_RETRY`. Cancellation status must reflect whether the file/session/tree is closing.

Test signals: selftest lists `smb2.lock`, raw/base lock suites, `raw.samba3posixtimedlock`, clustered SMB2 deny tests, durable/persistent handle tests, and multichannel-related suites. Focus tests on zero lock count, dynamic lock array length, expired session unlock vs lock, invalid mixed flags, blocking versus fail-immediately, replayed lock sequence, durable and multichannel sequence buckets, POSIX read-only write lock denial, close/logoff cancellation status, backend retry timer, and share-mode wakeups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_negprot.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_negprot.c

Purpose: implements SMB2 negotiation, including SMB1 multi-protocol handoff to SMB2, dialect selection, SMB 3.1.1 negotiate context parsing/creation, signing/encryption/preauth capability selection, POSIX extension negotiation, max I/O sizing, multichannel client-guid handling, and SPNEGO security blob generation.

Important APIs and types: `reply_smb2002()` and `reply_smb20ff()` convert SMB1 negotiate selections into synthetic SMB2 negotiate requests through `reply_smb20xx()`. `smbd_smb2_protocol_dialect_match()` chooses the highest allowed dialect. `smbd_smb2_request_process_negprot()` is the SMB2 negotiate handler. `smb2_negotiate_context_process_posix()` handles the POSIX extension context. `smbd_smb2_request_process_negprot_mc_done()` completes multichannel client-guid negotiation. `negprot_spnego()` builds the server GUID/name plus SPNEGO OID list blob. `smb2_multi_protocol_reply_negprot()` parses SMB1 dialect strings and selects SMB2 when SMB1 negotiation is used.

Control flow: direct SMB2 negotiation verifies body size `0x24`, reads dialect count, security mode, capabilities, client GUID, validates dialect list length, and selects a protocol within server min/max settings. SMB 2.??? (`0x02ff`) is allowed only through the SMB1 handoff path that set `xconn->smb2.allow_2ff`. For SMB 3.1.1 it validates negotiate-context offset alignment, parses contexts, and processes POSIX extension request. It records remote architecture/protocol, reloads services, requires preauth context for SMB 3.1.1, obtains the SPNEGO blob, computes server security mode and capabilities (DFS, leasing, encryption, directory leasing, large MTU, multichannel), clamps max transact/read/write sizes by dialect/transport limits, selects preauth SHA512, encryption cipher, signing algorithm, and QUIC transport-level-security acceptance when applicable, checks configured SMB3 capability consistency, builds output negotiate contexts, then emits the `0x40` response body and dynamic security/context blobs. For real dialects it initializes SMB2 connection tables, records client and server negotiation state on `xconn`, and either completes immediately or starts multichannel client GUID database negotiation; a retrieved existing connection may cause transport handoff and clean server exit. SMB1 multi-protocol negotiation parses NUL-terminated dialect names from the SMB1 buffer, chooses `SMB 2.???` or `SMB 2.002` within min/max protocol bounds, and calls the selected synthetic reply function.

State and persistence: writes live connection state: `xconn->protocol`, client capabilities/security mode/GUID/dialect list, server capabilities/security mode/GUID/dialect/max sizes/signing/cipher, preauth state pointer, POSIX negotiation flag, credit multicredit flag, trusted QUIC flag, and multichannel client global GUID. It also updates remote architecture cache from the client GUID and may interact with the multichannel client database via `smb2srv_client_mc_negprot_send()`. No file data is persisted.

Dependencies and integration: depends on SMB2 negotiate-context helpers, tsocket transport state, NDR, signing/encryption capability parsing, auth/gensec SPNEGO generation, loadparm protocol/capability settings, server service reload, remote architecture tracking, multichannel connection/client tables, QUIC transport settings, and SMB1 server send/negotiation compatibility. Later SMB2 handlers use these negotiated capabilities for leases, directory leases, encryption, multichannel lock sequence checks, validate-negotiate-info, POSIX create contexts, and max transfer sizes.

Risks: negotiate-context offset/alignment parsing is security-sensitive. SMB 3.1.1 must require preauth and select a mutually supported hash or fail with the right status. Capability bits are conditional on server config, client bits, dialect, transport, and clustering/multichannel state; incorrect bits enable unsupported later behavior. Validate-negotiate-info depends on exact state recorded here. Multichannel handoff can terminate the process intentionally; errors around `NT_STATUS_MESSAGE_RETRIEVED` or connection pass semantics are high impact. The SPNEGO blob prepends a 16-byte server GUID/name field, and callers assume that layout.

Test signals: selftest lists `SMB2-NEGPROT`, SMB client basic for SMB2_02/SMB2_10, SMB2 connect/credits/rw/bench, auth SPNEGO/NTLM variations, SMB3/multichannel-related suites, POSIX extension tests, and validate-negotiate-info through IOCTL tests. Focus coverage on dialect order and min/max protocol, SMB 2.??? handoff, malformed SMB3.1.1 context offsets, missing preauth, no hash overlap, cipher/signing preference selection, encryption disabled/required, QUIC transport capabilities, max I/O sizes over NBT vs direct TCP, client GUID all-zero behavior, multichannel enabled/disabled, and SPNEGO generation failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_negprot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_notify.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_notify.c

Purpose: implements SMB2 CHANGE_NOTIFY on directory handles by bridging SMB2 requests into Samba's change-notify subsystem, supporting immediate replies, queued async notifications, cancellation, and output marshalling.

Important APIs and types: `smbd_smb2_request_process_notify()` decodes and queues the request. `smbd_smb2_notify_send()` / `smbd_smb2_notify_recv()` are the operation wrappers. `struct smbd_smb2_notify_state` stores the SMB2 request, fake SMB1 request, queued-request state, skip flag, status, and output blob. `smbd_smb2_notify_reply()` is the callback from the notify subsystem. Destructors `smbd_smb2_notify_state_destructor()` and `smbd_smb2_notify_smbreq_destructor()` manage cancellation and talloc parent recovery.

Control flow: the request processor verifies body size `0x20`, extracts watch flags, max output size, file IDs, and completion filter, enforces negotiated `max_trans` and credit charge, resolves the directory handle, and queues the send helper. The send helper creates fake SMB1 state, logs the filter, rejects non-directory or wrong-connection fsp, creates `fsp->notify` state if needed, and either replies immediately when changes are already pending or queues the request with `change_notify_add_request()`. Because the notify subsystem talloc-moves the `smb_request`, the file sets a destructor that moves it back under the SMB2 request when the notify request completes. The notify callback marks async profile busy, maps zero-length successful replies to `NOTIFY_ENUM_DIR`, copies non-empty output, defers callback to the SMB2 event context, and completes or errors the tevent request. The done callback formats the SMB2 `0x08` output response.

State and persistence: queued notify requests live in the change-notify subsystem associated with the fsp. This file tracks whether the request is queued and cancels it from the state destructor or explicit cancel function. Output is transient. No persistent filesystem state is written.

Dependencies and integration: depends on SMB2 size/credit helpers, fake SMB1 request glue, change-notify creation/request/reply/cancel APIs, notify filter formatting, talloc destructors, tevent cancellation, and async profiling. It integrates with directory handles created by `smb2_create.c` and with backend notify implementations such as inotify when available.

Risks: talloc ownership is subtle because `change_notify_add_request()` moves `smbreq`; the destructor returns `-1` to keep it and moves it back. Incorrect destructor behavior can leak, double-free, or use-after-free queued notify state. Cancellation sets `skip_reply` to avoid completing an already destroyed request. Zero-length OK replies become `NOTIFY_ENUM_DIR`, which affects client rescan behavior. `in_completion_filter` is read with `IVAL()` into a 64-bit field, so only low 32 bits are populated.

Test signals: selftest includes `smb2.notify`, `raw.notify`, `smb2.change_notify_disabled`, `smb2.notify-inotify` when inotify is available, and RPC spoolss notify. Targeted tests should cover non-directory handles, wrong-connection fsp, max-trans/credit violations, immediate pending changes, queued change delivery, zero-length enumeration status, cancellation, close while notify is pending, recursive watch flag, and inotify-enabled versus fallback behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_notify.c -->
