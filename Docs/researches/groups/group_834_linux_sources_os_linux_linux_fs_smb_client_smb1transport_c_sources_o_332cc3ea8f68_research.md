# Group Research: group_834_linux_sources_os_linux_linux_fs_smb_client_smb1transport_c_sources_o_332cc3ea8f68

Scope: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1transport.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb1transport.c

This file implements SMB1/CIFS transport-side request setup, send/receive wrappers, response validation, signing verification, MID tracking, and multi-response Transaction2 coalescing.

Primary responsibilities:
- Allocate and initialize SMB1 `mid_q_entry` objects through `alloc_mid()` and `allocate_mid()`.
- Enforce session state rules before queuing requests: normal commands are rejected while sessions are new or exiting, except negotiate/session-setup/logoff cases.
- Prepare signed synchronous and asynchronous SMB requests with `cifs_setup_request()` and `cifs_setup_async_request()`.
- Provide legacy send helpers: `SendReceiveNoRsp()`, `SendReceive2()`, and `SendReceive()`.
- Validate received SMB1 frames with `checkSMB()`.
- Verify SMB signatures in `cifs_check_receive()` and map SMB errors to Linux errors.
- Detect and merge multi-part SMB_COM_TRANSACTION2 responses via `check2ndT2()`, `coalesce_t2()`, and `cifs_check_trans2()`.

Important control flow:
- `alloc_mid()` assigns MID, PID, command, allocation time, default wakeup callback, creator task reference, refcount, and initial `MID_REQUEST_ALLOCATED` state.
- `allocate_mid()` protects session-status checks with `ses_lock`, then inserts the MID into `server->pending_mid_q` under `mid_queue_lock`.
- `cifs_setup_async_request()` enables signature flags when required, signs the request, and returns an `ERR_PTR()` on failure.
- `SendReceive()` validates transmit length, session/server pointers, maximum CIFS buffer size, sends via `cifs_send_recv()`, copies the response into caller storage when requested, and frees the response buffer.
- `cifs_check_trans2()` stores the first large Transaction2 response, then coalesces later secondary responses until all data is present or a malformed response ends the MID.

Validation and safety:
- Transmit requests larger than the SMB1/RFC1001 frame limit or `CIFSMaxBufSize + MAX_CIFS_HDR_SIZE` are rejected.
- `check_smb_hdr()` verifies the SMB1 protocol signature and rejects unexpected server-to-client requests except oplock/locking and known malformed Transaction2 error replies.
- `checkSMB()` validates minimum header/BCC availability, `WordCount`, calculated SMB size, RFC1001 length, BCC wraparound for large reads, and limits tolerated trailing server padding to 512 bytes.
- `coalesce_t2()` checks total data counts, 16-bit field overflow, final PDU size bounds, and target buffer capacity before appending secondary response data.
- Signature mismatch triggers reconnect when signing was not mandatory; mandatory-signing failures remain hard errors.

Dependencies:
- CIFS MID pool, server pending queue, SMB1 header helpers, request signing/verification, `cifs_send_recv()`, response buffer lifetime helpers, error mapping, and trace/error helpers.

Research notes:
- This is the SMB1 transport guardrail layer. Most higher-level SMB1 operations depend on it to reject malformed frames early and keep request/MID lifecycle state coherent.
- Transaction2 coalescing is security-sensitive because it adjusts in-buffer lengths and copies server data into the first response buffer.
- Several compatibility branches intentionally tolerate historical server bugs, including missing BCC bytes, absent response flags on some errors, BCC wraparound, and limited extra trailing data.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1transport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2file.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb2file.c

This file contains SMB2/SMB3 file-open helpers, symlink error-response parsing, resilient-handle setup, server inode-number fallback, and SMB2 byte-range lock batching.

Primary responsibilities:
- Parse SMB2 symlink error responses from `STATUS_STOPPED_ON_SYMLINK`.
- Normalize parsed symlink targets for file vs directory behavior.
- Open SMB2 files through `smb2_open_file()`.
- Request network resiliency on opens when the tree connection enables it.
- Query a server file number when the open response lacks `IndexNumber`.
- Unlock SMB2 byte-range lock ranges in batches.
- Replay locally tracked mandatory byte-range locks to the server.

Important control flow:
- `symlink_data()` supports both SMB2 error-context responses and older direct `ErrorData` symlink layouts, validating byte counts, context lengths, tags, and bounds.
- `smb2_parse_symlink_response()` checks substitute/print name offsets and lengths before calling `smb2_parse_native_symlink()`.
- `smb2_fix_symlink_target_type()` appends a trailing slash to directory symlink targets on non-POSIX mounts and rejects file symlink targets that end in `/`.
- `smb2_open_file()` converts the path to UTF-16, may temporarily add `FILE_READ_ATTRIBUTES`, opens with batch oplock request, retries without `FILE_READ_ATTRIBUTES` after `-EACCES`, and handles stopped-on-symlink by reopening with `OPEN_REPARSE_POINT`.
- After a successful open, resilient opens issue `FSCTL_LMR_REQUEST_RESILIENCY`; `-EOPNOTSUPP` disables future resiliency attempts for the tcon.
- If metadata was requested and `IndexNumber` is zero, the helper calls `SMB2_get_srv_num()` and lets higher layers handle unsupported inode numbers.

Lock handling:
- `smb2_unlock_range()` walks locally tracked locks for a file, selects locks fully covered by the requested unlock range and matching owner rules, removes locally cached locks without sending, or batches SMB2 unlock elements to `smb2_lockv()`.
- On server unlock failure, moved locks are restored to the file lock list; on success, temporary lock records are freed.
- `smb2_push_mandatory_locks()` allocates a page-bounded array of `smb2_lock_element` objects and replays all per-FID mandatory locks through `smb2_push_mand_fdlocks()`.

Validation and safety:
- Path conversion failure returns `-ENOMEM`.
- Symlink parsing validates every server-provided offset/length against the actual response iov.
- Lock batch sizing snapshots `server->maxBuf`, rejects too-small values, caps allocation at `PAGE_SIZE`, and uses `BUILD_BUG_ON()` for element size assumptions.
- The unlock path holds `cinode->lock_sem` while mutating lock lists.

Dependencies:
- SMB2 open/ioctl/query helpers, CIFS path conversion, open-info data structures, tcon/session/server state, lock-list helpers, inode lock state, and SMB2 symlink/reparse constants.

Research notes:
- The file bridges VFS open semantics and SMB2 open semantics, especially for symlink traversal and metadata access-denied fallbacks.
- Lock batching is carefully written to preserve local lock state if remote unlocks fail.
- The `FILE_READ_ATTRIBUTES` retry path is important for servers/share ACLs that allow opening but deny explicit attribute-read access.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2glob.h -->
# File Research: sources/os/linux/linux/fs/smb/client/smb2glob.h

This header defines shared SMB2 constants and small data structures used by SMB2 client implementation files.

Primary contents:
- `enum smb2_compound_ops`: identifiers for the open-operation-close compound helper in `smb2inode.c`.
- Chained request flags: `CHAINED_REQUEST`, `START_OF_CHAIN`, `END_OF_CHAIN`, and `RELATED_REQUEST`.
- `struct status_to_posix_error`: SMB2/NT status code to Linux errno mapping entry, including status string.

Compound operation enum:
- Includes operations for delete disposition, set/query info, query directory, mkdir, rename, hardlink, set EOF, unlink, POSIX query info, set/get reparse point, WSL EA query, and open-query fallback.
- These enum values are consumed by `smb2_compound_op()` to construct SMB2 compound request chains.

Dependencies:
- Basic Linux fixed-width types and SMB2 implementation files that include this header.

Research notes:
- This is a small cross-file contract header. Changes to `enum smb2_compound_ops` must stay synchronized with the switch handling in `smb2inode.c`.
- `status_to_posix_error` is the public shape used by `smb2maperror.c`, generated mapping data, and KUnit test exports.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2glob.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2inode.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb2inode.c

This file implements SMB2/SMB3 path and inode metadata operations using compound open-operation-close request chains. It covers path stat, mkdir/rmdir/unlink, rename, hardlink, truncate, attribute update, reparse-point creation/query, POSIX query info, WSL EA handling, and pending-delete rename.

Primary responsibilities:
- Build reusable SMB2 compound requests in `smb2_compound_op()`.
- Query path metadata through regular SMB2 `FILE_ALL_INFORMATION` or SMB3.1.1 POSIX info.
- Parse POSIX owner/group SIDs from POSIX query responses.
- Validate and copy WSL EA metadata for special file emulation.
- Validate FSCTL reparse responses and transfer reparse response-buffer ownership to callers.
- Implement mkdir, rmdir, unlink/delete-on-close, rename, hardlink, set-size, and set-file-info operations.
- Create and query reparse-point inodes.
- Rename a file to a hidden temporary “silly” name and mark it pending delete.

Important control flow:
- `smb2_compound_op()` optionally opens a path, appends one or more operations, optionally closes the compound FID, sends through `compound_send_recv()`, parses each response, frees request buffers, transfers selected output buffers, and retries replayable errors with `smb2_should_replay()`.
- When a caller already has `cifsFileInfo`, the helper skips open/close and sends only the operation portion using the existing persistent/volatile FID.
- Lease reuse is attempted when a dentry has an existing lease key; callers retry without lease on `-EINVAL` for hardlink/path alias edge cases.
- `smb2_query_path_info()` uses cached root directory metadata when possible, otherwise compounds query info. It falls back to `SMB2_OP_OPEN_QUERY` with `MAXIMUM_ALLOWED` when `FILE_READ_ATTRIBUTES` open/query fails with `-EACCES`.
- Reparse handling for `-EOPNOTSUPP` parses create response status, optionally gets the reparse point, optionally queries WSL EAs, and fixes symlink target type.
- `smb2_unlink()` is specialized: it opens with `CREATE_DELETE_ON_CLOSE | OPEN_REPARSE_POINT`, adjusts share access to `FILE_SHARE_DELETE`, compounds close, retries replayable errors, retries without lease on `-EINVAL`, and marks open handles deleted after success.
- `smb2_create_reparse_inode()` creates the object with `OPEN_REPARSE_POINT`, sets reparse data, queries inode metadata, and unlinks the intermediate object if create succeeded but setting reparse data failed.

Validation and safety:
- `reparse_buf_ptr()` checks output offset/count addition overflow, iov bounds, minimum reparse buffer length, and `ReparseDataLength`.
- `parse_posix_sids()` validates POSIX query output length and SID lengths before copying owner/group SIDs.
- `check_wsl_eas()` enforces minimum/maximum EA response sizes, bounds every EA entry, validates name length, value length, expected WSL xattr names, alignment, and next-entry overflow.
- `smb2_validate_and_copy_iov()` is used for query-info response copying.
- Response buffers are freed via `free_rsp_iov()` unless ownership is explicitly transferred for reparse data.
- Compound response arrays account for implicit open and close responses around the requested operation list.

Notable operations:
- `smb2_mkdir()` creates a directory through SMB2 CREATE parameters; `smb2_mkdir_setinfo()` follows with attribute update for read-only directory state.
- `smb2_rmdir()` drops cached directory handles before delete disposition.
- `smb2_rename_path()` and `smb2_create_hardlink()` share `smb2_set_path_attr()` for UTF-16 target-name set-info operations.
- `smb2_set_path_size()` sends `FILE_END_OF_FILE_INFORMATION`.
- `smb2_set_file_info()` skips no-op all-zero timestamp/attribute updates.
- `smb2_query_reparse_point()` returns both tag and response iov/buffer type to the caller.
- `smb2_rename_pending_delete()` clears readonly, may set hidden for last-link deletes, renames to a generated silly path, then sets delete disposition.

Dependencies:
- CIFS VFS/inode structures, tcon/session/server state, cached directory handles, SMB2 request init/free helpers, compound send/receive, path conversion, reparse constants, POSIX query structures, WSL EA constants, tracepoints, and inode metadata refresh helpers.

Research notes:
- `smb2_compound_op()` is the central abstraction in this file; the correctness of many VFS path operations depends on its response indexing, buffer ownership, replay logic, and cfile reference handling.
- Reparse and symlink behavior is one of the most subtle areas because successful create/open responses can carry reparse status, and some follow-up queries intentionally open with `OPEN_REPARSE_POINT`.
- WSL EA handling is deliberately strict because the server response is copied into client metadata used to represent Unix-like special files.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2maperror.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb2maperror.c

This file maps SMB2/NT status codes from server responses to Linux errno values.

Primary responsibilities:
- Include the generated `smb2_mapping_table.c` as `smb2_error_map_table`.
- Locate mapping entries by binary search.
- Convert SMB2 response status codes to POSIX errors in `map_smb2_to_linux_error()`.
- Validate mapping-table sort order at module initialization.
- Export test-only mapping symbols for KUnit when `CONFIG_SMB_KUNIT_TESTS` is enabled.

Important control flow:
- `cmp_smb2_status()` compares a searched status key with a `status_to_posix_error` table pivot.
- `smb2_get_err_map()` uses `__inline_bsearch()` over the sorted mapping table.
- `map_smb2_to_linux_error()` returns zero for successful SMB2 statuses and emits `trace_smb3_cmd_done()`.
- Nonzero statuses default to `-EIO` when no mapping exists.
- Logging suppresses noisy notices for `STATUS_MORE_PROCESSING_REQUIRED` and `STATUS_END_OF_FILE` unless CIFS FYI/error logging is enabled.
- Error paths trace `trace_smb3_cmd_err()` and call `smb_EIO1()` for unmapped `-EIO`.

Validation and safety:
- `smb2_init_maperror()` walks the generated mapping table and returns `-EINVAL` if the array is not sorted ascending by status code, which is required for binary search correctness.

Dependencies:
- Generated SMB2 mapping table, `struct status_to_posix_error` from `smb2glob.h`, SMB2 status constants, tracepoints, CIFS logging, and Linux errno values.

Research notes:
- The correctness of all SMB2 error handling depends on the generated table remaining sorted.
- The test-only exports are narrow and exist specifically so `smb2maperror_test.c` can verify binary-search coverage over every table entry.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2maperror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2maperror_test.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb2maperror_test.c

This file provides KUnit coverage for SMB2 status-to-errno mapping lookup.

Primary responsibilities:
- Iterate every exported SMB2 mapping-table entry.
- Look up each status with `smb2_get_err_map_test()`.
- Assert that the returned mapping matches status code, POSIX errno, and status string.

Important control flow:
- `test_cmp_map()` performs one lookup and validates all fields with KUnit assertions/expectations.
- `maperror_test_check_search()` loops from `0` to `smb2_error_map_num - 1`.
- `maperror_suite` registers the single test case under suite name `smb2_maperror`.

Dependencies:
- KUnit, CIFS/SMB2 test exports from `smb2maperror.c`, `smb2glob.h` mapping structure, and SMB2 prototype declarations.

Research notes:
- This test is primarily a regression check for binary-search reachability across the generated sorted table.
- It does not test unmapped statuses or logging behavior; it verifies that every table entry can be found and returned intact.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2maperror_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2misc.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb2misc.c

This file contains SMB2/SMB3 miscellaneous protocol helpers: response validation, SMB2 length calculation, data-area discovery, path conversion, lease-state conversion, oplock/lease-break dispatch, cancelled-open cleanup, cancelled-close retry, and SMB3.1.1 preauth hash updates.

Primary responsibilities:
- Validate SMB2 response headers and fixed structure sizes.
- Calculate expected SMB2 response lengths and tolerate documented server padding quirks.
- Locate variable-length data areas for SMB2 response types.
- Convert CIFS paths to SMB2 UTF-16 paths, trimming leading separators where required.
- Translate CIFS cache/oplock flags into SMB2 lease-state flags.
- Match server oplock/lease break notifications to open files, pending opens, or cached directory handles.
- Queue async lease-break acknowledgements and cancelled-handle closes.
- Maintain SMB3.1.1 preauthentication integrity hash.

Important control flow:
- `check_smb2_hdr()` verifies protocol ID, message ID, and response direction, with an exception for server oplock-break requests.
- `smb2_check_message()` validates header size, command range, maximum buffer size, response `StructureSize2`, calculated length, negotiate-context length, and known compatibility exceptions.
- `get_neg_ctxt_len()` validates SMB3.1.1 negotiate context count/offset and returns negotiate-context plus padding length.
- `smb2_get_data_area_len()` extracts response-specific offset/length fields for negotiate, session setup, create, query info, read, query directory, ioctl, and change notify.
- `smb2_calc_size()` combines SMB2 header size, fixed response body size, and variable data-area length while rejecting overlapping data offsets.
- `smb2_is_valid_oplock_break()` handles classic FID-based oplock breaks and delegates 44-byte lease breaks to `smb2_is_valid_lease_break()`.
- Lease-break matching walks sessions and tcons on the primary server, checks open files, pending opens, and cached directories, then queues the proper oplock-break or lease-break work.
- `smb2_handle_cancelled_mid()` schedules an async close if a successful SMB2 CREATE response arrives for an interrupted MID and the command was not already a create-close compound.
- `smb311_update_preauth_hash()` updates the session preauth SHA-512 hash for negotiate and relevant session setup packets.

Validation and compatibility:
- The response-size table mirrors expected SMB2 response `StructureSize2` values by command.
- Error packets with SMB2 error structure size are allowed where fixed sizes otherwise mismatch.
- Special cases tolerate symlink create errors with extra data, Windows 7 oplock-break padding, implied one-byte BCC differences, 8-byte compound padding, and macOS write-response junk padding.
- Data-area offsets are bounded to `4096` and lengths to `128 KiB`; invalid offset/length pairs cause the data area to be ignored.
- Cancelled close retry checks tcon refcount and skips async close if the tree connection is already closing.

Dependencies:
- SMB2 PDU structures, CIFS session/tcon/open-file lists, cached directory lease handling, workqueues, tracepoints, SHA-512 crypto, SMB2 close/lease-break helpers, and SMB3 dialect/session state.

Research notes:
- This is the main SMB2 receive-side sanity checker and asynchronous notification router.
- The validation code balances strict structure checks with practical exceptions for real server behavior.
- Lease-break handling is concurrency-sensitive because it walks global session/tcon state while coordinating open-file locks and pending-open state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2misc.c -->