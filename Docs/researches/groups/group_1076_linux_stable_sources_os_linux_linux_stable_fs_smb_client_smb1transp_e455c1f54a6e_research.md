# Group Research: group_1076_linux_stable_sources_os_linux_linux_stable_fs_smb_client_smb1transp_e455c1f54a6e

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux-stable/fs/smb/client/*`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb1transport.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smb1transport.c

## Purpose
Implements SMB1/CIFS transport helpers for request setup, send/receive wrappers, response validation, signature verification, MID queue management, and multi-part TRANSACTION2 response coalescing.

## Main Responsibilities
- Allocate and initialize SMB1 MID queue entries.
- Enforce session state constraints before sending SMB1 requests.
- Sign SMB1 requests and verify signed responses.
- Provide legacy `SendReceive*()` wrappers around the shared CIFS transport path.
- Validate SMB1 response headers and lengths.
- Detect and merge multi-response TRANSACTION2 replies.

## Key Functions
- `alloc_mid()` creates a `mid_q_entry`, initializes refcount/lock, records MID, PID, command, allocation time, creator task, default callback, and state.
- `allocate_mid()` checks `SES_NEW`/`SES_EXITING` state rules, then adds the MID to `server->pending_mid_q`.
- `cifs_setup_async_request()` enables signing when needed, allocates a MID, and signs an async request.
- `cifs_setup_request()` is the synchronous setup path with session-aware MID allocation and request signing.
- `SendReceiveNoRsp()`, `SendReceive2()`, and `SendReceive()` adapt older CIFS call sites to `cifs_send_recv()`.
- `cifs_check_receive()` dumps the SMB, verifies signatures when signing is enabled, handles reconnect on optional signing failure, then maps SMB errors.
- `check2ndT2()` detects incomplete SMB1 TRANSACTION2 replies and returns missing byte count.
- `coalesce_t2()` appends secondary TRANSACTION2 data into the first response while updating `DataCount`, BCC, and PDU length.
- `cifs_check_trans2()` coordinates multi-response TRANSACTION2 state on the MID.
- `check_smb_hdr()` validates SMB1 protocol signature and permits only legitimate server-to-client exceptions.
- `checkSMB()` validates SMB1 frame length, word count/BCC reachability, protocol header, calculated size, RFC1001 length, and tolerated legacy over-padding.

## Important Data Flow
1. SMB1 callers build a request buffer and pass it through setup/send wrappers.
2. A MID is allocated and queued before the request is sent.
3. Signing state is applied before transmission.
4. Responses are checked for SMB framing consistency and, when needed, signature validity.
5. TRANSACTION2 responses may remain queued until all secondary fragments are coalesced.
6. Final status is converted to Linux/POSIX errors by the common SMB error mapping path.

## Edge Cases and Defensive Logic
- Rejects oversized outbound frames.
- Allows negotiate/session setup during `SES_NEW`, and logoff during `SES_EXITING`.
- Handles legacy servers that return short error packets or one-byte BCC quirks.
- Allows certain malformed-looking but historically observed TRANSACTION2 error responses.
- Caps tolerated trailing data to 512 bytes except for known BCC wrap cases.
- Prevents TRANSACTION2 coalescing overflows in `DataCount`, BCC, and response buffer length.

## Dependencies
Uses CIFS core structures and helpers from `cifsglob.h`, `cifsproto.h`, `smb1proto.h`, `smb2proto.h`, `cifs_debug.h`, `smbdirect.h`, and `compress.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb1transport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2file.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2file.c

## Purpose
Implements SMB2 file open helpers, symlink error-response parsing, target normalization, resilient handle setup, inode-number fallback retrieval, and byte-range lock replay/unlock support.

## Main Responsibilities
- Parse SMB2 symlink reparse error contexts.
- Normalize symlink targets for file-vs-directory semantics.
- Open SMB2 files and populate `cifs_open_info_data`.
- Request network resiliency for opened handles when configured.
- Unlock byte-range lock sets in batches.
- Re-push cached mandatory locks after reconnect or reopen.

## Key Functions
- `symlink_data()` locates and validates `smb2_symlink_err_rsp` inside either SMB2 error contexts or legacy error data.
- `smb2_fix_symlink_target_type()` appends a trailing slash to directory symlinks, rejects file symlinks with trailing slash, and skips these adjustments for POSIX paths.
- `smb2_parse_symlink_response()` validates substitute/print-name bounds and delegates native symlink target parsing.
- `smb2_open_file()` converts paths to UTF-16, adds `FILE_READ_ATTRIBUTES` when useful, retries without it on `-EACCES`, handles stopped-on-symlink responses, performs reopen with `OPEN_REPARSE_POINT`, optionally requests resiliency, and fills open metadata.
- `smb2_unlock_range()` scans cached locks, filters by requested range and owner semantics, batches SMB2 unlock elements, and restores local lock state on server-side unlock failure.
- `smb2_push_mand_fdlocks()` sends one file descriptor’s mandatory locks in bounded batches.
- `smb2_push_mandatory_locks()` iterates inode lock lists and replays mandatory locks using server `maxBuf` sizing.

## Important Data Flow
1. Path strings are converted with `cifs_convert_path_to_utf16()`.
2. `SMB2_open()` returns create/open metadata or an error iov.
3. `STATUS_STOPPED_ON_SYMLINK` is treated as structured data, not a plain error, when the caller asked for open info.
4. Successful opens may trigger resiliency IOCTL and server inode-number lookup.
5. Lock operations use local lock lists as the source of truth, updating them only after server success.

## Edge Cases and Defensive Logic
- Validates symlink context bounds against `iov_len`.
- Rejects malformed symlink tags and unexpected reparse tags.
- Avoids retry-without-read-attributes unless it intentionally added that access bit.
- Handles servers that do not support resiliency by disabling it for the tcon.
- Caps lock vector allocation by both server `maxBuf` and `PAGE_SIZE`.
- Preserves local locks if a batched unlock request fails.

## Dependencies
Relies on SMB2 protocol helpers from `smb2proto.h`, CIFS inode/session structures, lock-list helpers, UTF-16 conversion helpers, common SMB2 status definitions, and FSCTL constants.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2glob.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2glob.h

## Purpose
Defines small SMB2-global constants and structures shared by SMB2 client implementation files.

## Main Contents
- `enum smb2_compound_ops` enumerates operation IDs consumed by `smb2inode.c:smb2_compound_op()`.
- Compound operation IDs cover delete, set/query info, query directory, mkdir, rename, hardlink, EOF set, unlink, POSIX query info, reparse set/get, WSL EA query, and open-query.
- Chained request flags define start/end/related request state for compound/chained SMB2 operations.
- `struct status_to_posix_error` stores NT status code, Linux errno, and printable status string for SMB2 error mapping.

## Role in This Group
This header is the shared contract between:
- `smb2inode.c`, which dispatches `enum smb2_compound_ops`.
- `smb2maperror.c`, which uses `struct status_to_posix_error`.
- KUnit map-error tests that inspect the exported mapping table shape.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2glob.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2inode.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2inode.c

## Purpose
Implements SMB2/SMB3 inode-path operations using compound open-operation-close request chains. This is the central file for SMB2 path metadata queries, mkdir/rmdir/unlink, rename, hardlink, truncation, basic info updates, reparse point creation/query, WSL EA handling, and pending-delete rename behavior.

## Main Responsibilities
- Build and send SMB2 compound operations around an open file handle.
- Reuse existing `cifsFileInfo` handles when available.
- Query standard and POSIX metadata.
- Validate and copy reparse, POSIX SID, and WSL EA responses.
- Implement directory/file create-delete-rename-hardlink operations.
- Retry replayable compounds and retry without leases when lease keys are invalid.
- Clean up intermediate server objects after partial reparse creation failure.

## Key Helpers
- `reparse_buf_ptr()` validates IOCTL output bounds and returns a reparse data buffer.
- `file_create_options()` adds `OPEN_REPARSE_POINT` when a dentry inode is already marked reparse.
- `parse_posix_sids()` extracts owner/group SIDs from SMB3.1.1 POSIX query info.
- `check_wsl_eas()` validates WSL EA response layout, names, lengths, alignment, and allowed value sizes.
- `set_next_compound()` marks `NextCommand` and related-request bits while accounting for implicit close.
- `smb2_compound_op()` is the main dispatcher and transport wrapper for compound path operations.
- `parse_create_response()` extracts reparse/symlink state from SMB2 create responses.
- `ea_unsupported()` distinguishes tolerated WSL EA query failure after earlier compound commands succeeded.
- `free_rsp_iov()` frees response buffers and resets iov/buftype slots.

## `smb2_compound_op()` Behavior
The function accepts a tcon, mount info, path, open parameters, input iovs, operation command IDs, optional existing file handle, optional output response arrays, and optional dentry.

It:
1. Picks a channel and allocates per-compound variable storage.
2. Sets encryption flags when required.
3. Opens the path unless an existing `cfile` handle is supplied.
4. Reuses a lease key from the inode when available.
5. Builds operation requests based on `enum smb2_compound_ops`.
6. Adds close when it opened the handle itself.
7. Sends via `compound_send_recv()`.
8. Frees request buffers, maps each response’s error status, traces operation success/failure, copies requested output data, and frees or transfers response buffers.
9. Replays on replayable errors using `smb2_should_replay()`.
10. Drops the passed `cfile` reference before returning.

Supported operation cases include:
- `SMB2_OP_QUERY_INFO`
- `SMB2_OP_POSIX_QUERY_INFO`
- `SMB2_OP_MKDIR`
- `SMB2_OP_UNLINK`
- `SMB2_OP_SET_EOF`
- `SMB2_OP_SET_INFO`
- `SMB2_OP_RENAME`
- `SMB2_OP_HARDLINK`
- `SMB2_OP_SET_REPARSE`
- `SMB2_OP_GET_REPARSE`
- `SMB2_OP_QUERY_WSL_EA`

## Public Operations
- `smb2_query_path_info()` queries metadata, uses cached root handle when possible, supports POSIX query info, handles `-EACCES` fallback through open-query, handles reparse points and symlink parsing, and detects DFS links on invalid-name errors.
- `smb2_mkdir()` creates a directory through compound create semantics.
- `smb2_mkdir_setinfo()` sets readonly attributes after mkdir when needed.
- `smb2_rmdir()` drops cached directory state and marks the directory delete-pending.
- `smb2_unlink()` uses a two-request open/delete-on-close plus close compound, sets `FILE_SHARE_DELETE`, retries replayable errors, retries without lease on `-EINVAL`, and marks open handles for deleted files.
- `smb2_rename_path()` performs rename via `FILE_RENAME_INFORMATION`, invalidates cached dir entries, and retries without lease on invalid lease-key errors.
- `smb2_create_hardlink()` clears tmpfile attributes when needed and sends `FILE_LINK_INFORMATION`.
- `smb2_set_path_size()` sends `FILE_END_OF_FILE_INFORMATION` to truncate/extend by path, with invalid-lease retry.
- `smb2_set_file_info()` sends `FILE_BASIC_INFORMATION` for timestamps/attributes, skipping pure no-op updates.
- `smb2_create_reparse_inode()` creates an object with `OPEN_REPARSE_POINT`, sets its reparse buffer, queries resulting inode info, and unlinks the intermediate object if set-reparse fails after create succeeds.
- `smb2_query_reparse_point()` opens with `OPEN_REPARSE_POINT`, retrieves reparse IOCTL output, and transfers the response buffer to caller.
- `smb2_rename_pending_delete()` implements CIFS silly-rename style pending delete: clears readonly, optionally hides last-link files, renames to a generated delete-pending name, unlinks, and sets `CIFS_INO_DELETE_PENDING`.

## Important Data Flow
- Path inputs are converted to UTF-16 for SMB2 create/open and rename/link targets.
- Existing open handles avoid extra open/close compounds where possible.
- Compound responses are indexed relative to open + operation + close; callers that request output buffers receive ownership of selected response iovs.
- Metadata results are copied into `cifs_open_info_data`, with flags marking whether POSIX info, symlink target, WSL EA, or reparse data is present.
- Reparse-point handling bridges SMB IOCTL buffers to Linux inode creation/query paths.

## Edge Cases and Defensive Logic
- Reparse buffers are bounds-checked with overflow detection.
- POSIX SID and WSL EA parsers reject truncated, misaligned, unknown, or overlong data.
- Compound replay marks every replayed request with SMB2 replay flags.
- `-EREMCHG` marks the tree connection for reconnect after share deletion.
- Hardlink lease-key mismatch is explicitly documented and handled by retrying without the inode lease.
- WSL EA failures are tolerated for non-block/non-char reparse tags after other commands succeed.
- Reparse object creation cleans up empty server-side artifacts after partial failure.
- Pending-delete rename maps failure through SMB EIO tracing.

## Dependencies
This file depends on CIFS VFS state, SMB2 PDU construction/free helpers, compound send/receive, cached directory handling, reparse constants, POSIX info parsing, WSL EA constants, tracepoints, and inode update helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2maperror.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2maperror.c

## Purpose
Maps SMB2/SMB3 NT status codes to Linux/POSIX errno values and emits associated logging/tracing.

## Main Responsibilities
- Define the SMB2 status-to-errno mapping table.
- Perform fast lookup by NT status code.
- Convert SMB2 response header status into Linux return codes.
- Validate mapping table sort order at init.
- Export internals for KUnit testing when SMB tests are enabled.

## Key Functions and Data
- `smb2_error_map_table[]` includes generated entries from `smb2_mapping_table.c`, sorted by CPU-endian NT status code.
- `cmp_smb2_status()` compares a search key against a table entry.
- `smb2_get_err_map()` uses `__inline_bsearch()` over the sorted table.
- `map_smb2_to_linux_error()` returns `0` for success, suppresses noisy logging for expected statuses, maps known statuses, defaults unknown statuses to `-EIO`, emits trace events, and records SMB EIO trace when mapping falls back to `-EIO`.
- `smb2_init_maperror()` verifies ascending table order at module/init time.
- KUnit-only exports provide access to lookup, table pointer, and table length.

## Important Data Flow
1. Caller passes an SMB2 response buffer.
2. Header `Status` is read as little-endian NT status.
3. Zero status emits success trace and returns `0`.
4. Non-zero status is searched in `smb2_error_map_table`.
5. Known statuses return their configured Linux errno; unknown statuses return `-EIO`.
6. Error tracepoints include TreeId, SessionId, Command, MessageId, NT status, and errno.

## Edge Cases and Defensive Logic
- `STATUS_MORE_PROCESSING_REQUIRED` and `STATUS_END_OF_FILE` avoid normal error logging unless CIFS return-code debugging is enabled.
- Table order is checked because binary search correctness depends on it.
- Unknown status codes deliberately degrade to `-EIO`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2maperror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2maperror_test.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2maperror_test.c

## Purpose
Provides KUnit coverage for SMB2 status-code lookup correctness.

## Main Responsibilities
- Verify that every generated SMB2 status mapping can be found by `smb2_get_err_map_test()`.
- Compare each returned entry against the expected status code, POSIX error, and status string.

## Key Test Logic
- `test_cmp_map()` performs one lookup and asserts:
  - result is non-null,
  - `smb2_status` matches,
  - `posix_error` matches,
  - `status_string` matches.
- `maperror_test_check_search()` iterates from `0` to `smb2_error_map_num - 1`, checking every exported table entry.
- `maperror_suite` registers the single KUnit case as `smb2_maperror`.

## Coverage Value
This test verifies the binary-search lookup path against every table element. Combined with `smb2_init_maperror()` sort validation, it protects the generated mapping table from broken ordering or lookup regressions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2maperror_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2misc.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2misc.c

## Purpose
Implements SMB2/SMB3 miscellaneous protocol validation and support helpers: response structure validation, size calculation, path conversion, lease/oplock break handling, cancelled-command cleanup, and SMB3.1.1 preauth hash updates.

## Main Responsibilities
- Validate SMB2 headers and response structure sizes.
- Calculate SMB2 message sizes from fixed and variable-length areas.
- Handle SMB3.1.1 negotiate-context length accounting.
- Convert CIFS paths to SMB2 UTF-16 path strings.
- Derive lease state from CIFS inode caching flags.
- Process server oplock and lease break notifications.
- Queue close work for cancelled opens/closes to avoid server handle leaks.
- Update SMB3.1.1 preauthentication integrity hash.

## Key Functions
- `check_smb2_hdr()` validates protocol ID, message ID, response flag, and allows oplock-break requests from the server.
- `get_neg_ctxt_len()` computes SMB3.1.1 negotiate context length, including padding/SPNEGO layout validation.
- `smb2_check_message()` validates full SMB2 response framing: transform header handling, header structure size, command range, fixed response size, calculated length, padding exceptions, symlink create exception, and max length.
- `smb2_get_data_area_len()` returns variable data offset/length for commands with data areas.
- `smb2_calc_size()` computes expected SMB2 frame size from header, fixed parameter area, and variable data area.
- `cifs_convert_path_to_utf16()` strips leading slash/backslash when required and converts to UTF-16 using mount charset/remapping.
- `smb2_get_lease_state()` converts CIFS cache/oplock flags into SMB2 lease-state bits.
- `smb2_is_valid_oplock_break()` handles classic oplock break messages and delegates lease breaks when structure size indicates a lease break.
- `smb2_is_valid_lease_break()` searches sessions/tcons/open files/pending opens/cached dirs for a matching lease key and queues appropriate break handling.
- `smb2_cancelled_close_fid()` performs async close for handles left open after interrupted operations.
- `smb2_handle_cancelled_close()` safely takes a tcon ref and queues close retry for interrupted close.
- `smb2_handle_cancelled_mid()` queues close retry for successful create responses whose MID was cancelled before normal processing.
- `smb311_update_preauth_hash()` updates session preauth SHA-512 hash for negotiate/session-setup traffic as required by SMB3.1.1.

## Important Tables and Structures
- `smb2_rsp_struct_sizes[]` maps each SMB2 command to expected response `StructureSize2`.
- `has_smb2_data_area[]` marks which SMB2 commands include variable response data.
- `struct smb2_lease_break_work` carries lease break ack work to `cifsiod_wq`.

## Important Data Flow
- Incoming SMB2 frames are validated by protocol ID, MID, command, fixed structure size, and computed variable payload length.
- Lease/oplock breaks are correlated through tcon open-file lists, pending-open lists, and cached directory lease state.
- Cancelled create/close recovery captures persistent/volatile FIDs and asynchronously closes them on the server.
- Preauth hashing chains the prior hash with each relevant request/response iov.

## Edge Cases and Defensive Logic
- Accepts known server padding quirks, including compound 8-byte padding, Windows oplock extra bytes, implied BCC byte behavior, and macOS write-response padding.
- Treats SMB2 transform frames specially to locate matching sessions before decryption handling.
- Rejects impossible data offsets/lengths with conservative limits.
- Skips preauth update after final successful session setup response.
- Avoids async close retry when tcon refcount indicates the tree is closing.
- Handles lease breaks for pending opens by queueing a separate lease-break ack worker after dropping locks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2misc.c -->