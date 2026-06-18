# subset-b-005758 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1transport.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb1transport.c

## Purpose

This file implements the SMB1/CIFS transport-side request setup, response validation, synchronous send/receive wrappers, and special handling for multi-response Transaction2 replies. It sits between higher-level SMB1 operations in `cifssmb.c`/`smb1ops.c` and the generic CIFS transport engine in `transport.c`, providing SMB1-specific MID allocation, signing checks, response copying, and frame sanity checks.

## Important APIs, types, and functions

- `alloc_mid()` initializes a `struct mid_q_entry` from an SMB1 header: MID, PID, command, allocation timestamp, refcount, callback, creator task, and initial `MID_REQUEST_ALLOCATED` state.
- `allocate_mid()` gates request allocation against `cifs_ses::ses_status`, allowing only negotiate/session-setup while new and only logoff while exiting, then appends the MID to `server->pending_mid_q`.
- `cifs_setup_async_request()` and `cifs_setup_request()` prepare signed SMB1 requests. The synchronous path allocates and queues the MID; the async path allocates and signs but leaves queueing to the caller.
- `SendReceiveNoRsp()`, `SendReceive2()`, and `SendReceive()` are compatibility wrappers over `cifs_send_recv()`.
- `cifs_check_receive()` dumps and verifies received SMB1 responses, including signature validation when signing is enabled, then maps SMB errors.
- `check2ndT2()`, `coalesce_t2()`, and `cifs_check_trans2()` detect and merge fragmented Transaction2 responses.
- `checkSMB()` validates SMB1 wire frames against protocol signature, header/word-count/bcc sizes, RFC1001 length, calculated SMB size, and tolerated server quirks.

## Control flow

The common send path builds an `smb_rqst`, allocates a MID, signs the request through `cifs_sign_rqst()`, sends through `cifs_send_recv()`, and later checks the received response through `cifs_check_receive()` or the server operation table. `SendReceive()` additionally copies the response into the caller's output buffer and frees the transport-owned response buffer.

Multi-part Transaction2 handling is stateful: `check2ndT2()` identifies whether more data is expected; `cifs_check_trans2()` marks `mid->multiRsp`, captures the first large buffer if needed, and calls `coalesce_t2()` for later fragments. When the last fragment arrives, it sets `mid->multiEnd` and dequeues the MID.

## State and persistence behavior

The file updates in-memory transport/session state only. Important state includes `pending_mid_q`, `mid_count`, `mid->multiRsp`, `mid->multiEnd`, `mid->resp_buf`, `mid->large_buf`, `server->bigbuf`, and signing sequence numbers. It does not persist to disk. Memory ownership is explicit: response buffers are returned through `resp_iov` and released with `free_rsp_buf()`, while Transaction2 coalescing may transfer `server->bigbuf` ownership to `mid->resp_buf`.

## Dependencies and integration points

It depends on CIFS core types from `cifsglob.h`, request helpers from `cifsproto.h`, SMB1 declarations from `smb1proto.h`, shared SMB2 signing declarations, `smbdirect.h`, compression hooks, and trace/error helpers. It is wired into SMB1 through declarations in `smb1proto.h` and the SMB1 operation table (`smb1ops.c` uses `checkSMB`). Higher-level SMB1 commands call `SendReceive*()` throughout `cifssmb.c`.

## Risks and edge cases

Frame validation is security-sensitive because malformed lengths can otherwise cause out-of-bounds reads or writes. The Transaction2 coalescing path must keep `DataCount`, BCC, and PDU length synchronized and must reject oversized totals. Session state gating returns `-EAGAIN` for requests sent during setup/teardown, so callers must tolerate retry. Signature verification reconnects opportunistically only when signing is not required; required-signing failures propagate. `SendReceive()` copies into caller-provided `out_buf` without checking that the caller allocated enough for `resp_iov.iov_len`, so the contract relies on legacy callers passing an adequate buffer.

## Test signals

There is no direct KUnit file for this source in this subset. Useful validation signals are SMB1 mount smoke tests, signing-required mounts, request cancellation/reconnect tests, and SMB1 Transaction2 directory/query tests that force secondary responses. Fuzzing or packet-replay tests should target `checkSMB()` length combinations and `coalesce_t2()` count/offset arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2file.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb2file.c

## Purpose

This file contains SMB2/SMB3 file-open helpers that handle symlink error payloads, resilient-handle setup, server inode-number completion, and byte-range lock replay/unlock batching. It provides higher-level file operations with a cleaner `smb2_open_file()` API around `SMB2_open()` while preserving CIFS-specific behavior for symlinks, leases, resiliency, and local lock bookkeeping.

## Important APIs, types, and functions

- `symlink_data()` extracts and validates `struct smb2_symlink_err_rsp` from either SMB2 error contexts or legacy error data, checking byte counts, context lengths, `SYMLINK_ERROR_TAG`, and `IO_REPARSE_TAG_SYMLINK`.
- `smb2_fix_symlink_target_type()` normalizes parsed symlink targets for non-POSIX mounts by appending a slash for directory symlinks and rejecting file symlinks ending in slash.
- `smb2_parse_symlink_response()` validates the symlink path buffers and delegates native target conversion to `smb2_parse_native_symlink()`.
- `smb2_open_file()` converts paths to UTF-16, adjusts access masks, calls `SMB2_open()`, handles `STATUS_STOPPED_ON_SYMLINK`, optionally reopens with `OPEN_REPARSE_POINT`, applies network resiliency through `FSCTL_LMR_REQUEST_RESILIENCY`, and fills `cifs_open_info_data`.
- `smb2_unlock_range()` removes or batches unlocks for local `cifsLockInfo` entries covered by a VFS lock range.
- `smb2_push_mandatory_locks()` and `smb2_push_mand_fdlocks()` replay cached mandatory byte-range locks to the server with `smb2_lockv()`.

## Control flow

The open path first converts the mount-relative path to UTF-16. If the requested access lacks `FILE_READ_ATTRIBUTES` and does not already imply it, the helper adds that bit to retrieve metadata, with a retry path that removes it on `-EACCES`. On symlink-stop errors, the function parses the symlink target from the error response, reopens the object as a reparse point to collect metadata, and adjusts the target based on directory/file type. After a successful open, it may issue a resiliency ioctl and may fetch a server inode number if the create response omitted `IndexNumber`.

Lock removal scans `cfile->llist->locks` under `cinode->lock_sem`. If byte-range locks are locally cacheable, matching entries are deleted without network I/O. Otherwise matching locks are moved to a temporary list, batched into SMB2 unlock elements up to the negotiated buffer/page limit, sent to the server, and restored to the original list if the network unlock fails.

## State and persistence behavior

This file mutates open parameters, `cifs_fid` metadata, `cifs_open_info_data`, `tcon->use_resilient`, symlink target ownership, and in-memory CIFS lock lists. There is no durable local persistence. Remote persistence occurs through SMB2 create/open, ioctl resiliency requests, and lock/unlock requests on the server. Error-buffer ownership is carefully tracked with `err_buftype` and released via `free_rsp_buf()`.

## Dependencies and integration points

The file depends on CIFS mount/session structures, UTF-16 conversion, SMB2 PDU helpers, status constants, and SMB FSCTL constants. `smb2_open_file()` is part of the SMB2 operation surface declared in `smb2proto.h` and used by file create/open flows. Symlink parsing is reused by `smb2inode.c` for compound path queries and reparse handling.

## Risks and edge cases

Symlink error parsing is length-sensitive and must reject malformed contexts before dereferencing nested payloads. Access-mask retry changes `oparms->desired_access` in place, so callers see the final adjusted value. Resiliency failures are intentionally suppressed except for disabling unsupported resiliency, which can hide server-side configuration issues. Lock batching must preserve local lock state on partial failures; restoring the temporary list on failed unlock is essential for consistency. Range matching uses start/end arithmetic, so overflow-sensitive lock ranges should be covered by tests.

## Test signals

Relevant signals include symlink traversal tests for absolute and relative targets, directory symlink slash behavior, open without read-attributes permissions, resilient-handle mounts, and byte-range lock stress tests across reconnects. No direct KUnit file is present here; behavior is mostly integration-tested through SMB2 file operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2glob.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb2glob.h

## Purpose

This header provides small shared SMB2 definitions used by multiple SMB2 client implementation files. Its main roles are to enumerate compound-operation identifiers consumed by `smb2inode.c`, define flags for chained/related request construction, and define the status-to-POSIX-error mapping record used by `smb2maperror.c`.

## Important APIs, types, and constants

- `enum smb2_compound_ops` assigns stable integer identifiers for open-operation-close compounds: set-delete, set-info, query-info, query-dir, mkdir, rename, hardlink, set-eof, unlink, POSIX query-info, set/get reparse point, WSL EA query, and open-query.
- `CHAINED_REQUEST`, `START_OF_CHAIN`, `END_OF_CHAIN`, and `RELATED_REQUEST` are request-construction flags for chained SMB2 read/request sequencing.
- `struct status_to_posix_error` stores an SMB2/NT status code, a Linux negative errno value, and a printable status string. It is shared by the generated mapping table and KUnit exports.

## Control flow

The header has no runtime control flow. Its values drive switch statements and table lookups in implementation files. Most notably, `smb2_compound_op()` switches on `enum smb2_compound_ops` to decide which SMB2 request initializer to add to a compound chain, and `smb2maperror.c` uses `struct status_to_posix_error` as the element type for binary search.

## State and persistence behavior

No state is stored here. The enum values are part of an internal source-level ABI between SMB2 client files; changing values or adding entries without updating switch handling can break compound operation behavior.

## Dependencies and integration points

The header relies on Linux integer typedefs such as `__u32`. It is included by `smb2inode.c`, `smb2maperror.c`, `smb2maperror_test.c`, and other SMB2 client files that need shared operation IDs or mapping types.

## Risks and edge cases

The main risk is enum drift: adding an `SMB2_OP_*` value requires corresponding request construction, response parsing/freeing, tracepoints, and final status handling in `smb2_compound_op()`. Because `SMB2_OP_SET_DELETE` and `SMB2_OP_QUERY_DIR` appear in the enum but are not handled in the observed `smb2_compound_op()` switch, callers must not pass unsupported values there unless the implementation is extended. Mapping records expose `char *status_string`; generated table storage must outlive all users.

## Test signals

Compile coverage catches missing type definitions. Functional coverage comes from callers of compound operations and from `smb2maperror_test.c`, which validates every generated `struct status_to_posix_error` entry can be found through the exported lookup wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2glob.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2inode.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb2inode.c

## Purpose

This file implements SMB2/SMB3 inode and path operations using compound open-operation-close request chains. It covers path metadata queries, mkdir/rmdir/unlink, rename, hardlink creation, file-size and attribute updates, reparse-point creation/query, POSIX metadata, WSL EA handling, and pending-delete rename flows. It is one of the main bridges between Linux VFS inode operations and SMB2 protocol primitives.

## Important APIs, types, and functions

- `smb2_compound_op()` is the central helper. It builds optional `CREATE`, one or more operation requests selected by `enum smb2_compound_ops`, and optional `CLOSE`, sends them with `compound_send_recv()`, maps each response, parses output data, frees request buffers, and handles replayable errors.
- `smb2_query_path_info()` obtains file metadata through cached-root handles, normal query-info, POSIX query-info, open-query fallback for access-denied cases, reparse-point probing, WSL EA fetches, and DFS invalid-name handling.
- `smb2_mkdir()`, `smb2_mkdir_setinfo()`, `smb2_rmdir()`, `smb2_unlink()`, `smb2_rename_path()`, `smb2_create_hardlink()`, `smb2_set_path_size()`, and `smb2_set_file_info()` wrap common VFS operations.
- `smb2_create_reparse_inode()` creates a file/directory with `OPEN_REPARSE_POINT`, sets reparse data, queries metadata, builds an inode, and deletes the intermediate object if setting the reparse point fails.
- `smb2_query_reparse_point()` returns reparse data and tag ownership to the caller.
- `smb2_rename_pending_delete()` implements a silly-rename style pending-delete sequence: clear attributes, rename to a generated hidden name, then mark delete pending.
- Helper validators include `reparse_buf_ptr()`, `parse_posix_sids()`, `check_wsl_eas()`, `parse_create_response()`, and `ea_unsupported()`.

## Control flow

Most exported functions prepare `CIFS_OPARMS`, optional input `kvec`s, and an array of `SMB2_OP_*` commands, then call `smb2_compound_op()`. The compound helper chooses a channel, allocates `smb2_compound_vars`, optionally converts the path to UTF-16, may reuse a lease key from the inode, appends request initializers, marks related/next commands, sends the compound, parses per-command responses, and frees or transfers output buffers. If `cfile` is provided, the helper skips explicit open/close and uses the existing FID.

Replay control is built into both `smb2_compound_op()` and the specialized `smb2_unlink()` path: replayable errors trigger `smb2_should_replay()`, optional backoff, and `smb2_set_replay()` on each request. Lease-key hardlink/rename/truncate failures with `-EINVAL` are retried without the inode lease key.

## State and persistence behavior

Local state mutations include inode CIFS attributes, cached directory invalidation, `tcon->need_reconnect`, transferred reparse IO buffers in `cifs_open_info_data`, symlink targets, WSL EA buffers, `CIFS_INO_DELETE_PENDING`, and open-handle deletion marking. Remote persistence is significant: create, delete-on-close, rename, hardlink, EOF update, basic-info update, FSCTL reparse point set/get, and query operations all change or observe server-side namespace and metadata. Buffer ownership is subtle when reparse query succeeds: response ownership is moved to `data.reparse.io` and removed from the normal free path.

## Dependencies and integration points

The file depends on CIFS superblock/tcon/session state, UTF-16 conversion, cached directory handles, SMB2 PDU initializers/free routines, compound transport, status mapping, POSIX SID helpers, WSL EA constants, tracepoints, and inode population functions (`cifs_get_inode_info()` and `smb311_posix_get_inode_info()`). It shares symlink handling with `smb2file.c` and operation IDs with `smb2glob.h`.

## Risks and edge cases

The compound path is high-risk because request count, response index, and free index must remain aligned across optional open/close, explicit open-query, existing `cfile`, and retry cases. Adding a new `SMB2_OP_*` requires construction, response parsing, trace, free, and output ownership handling. Reparse and WSL EA parsing are length-sensitive. Access-denied metadata fallback intentionally relies on create responses instead of query-info and may return reduced metadata. Lease reuse with hardlinks can provoke `STATUS_INVALID_PARAMETER`, so retry without lease is required. Failed reparse creation must clean up the server object to avoid leaving unusable empty files.

## Test signals

Strong test signals include VFS stat/open on normal files, roots, DFS links, symlinks, and unsupported reparse points; POSIX extension stat including owner/group SID parsing; WSL special-file EA queries; mkdir/rmdir/unlink/rename/hardlink/truncate integration tests; replay/reconnect tests for compound operations; and negative tests for malformed reparse or EA response lengths. No direct KUnit file is present in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2maperror.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb2maperror.c

## Purpose

This file maps SMB2/NT status codes from response headers to Linux negative errno values. It wraps a generated sorted mapping table, performs binary search lookups, emits optional diagnostics and tracepoints, and exposes test-only symbols for KUnit verification.

## Important APIs, types, and functions

- `smb2_error_map_table[]` is built from generated `smb2_mapping_table.c` entries of `struct status_to_posix_error`.
- `cmp_smb2_status()` compares a raw status key with a table pivot for `__inline_bsearch()`.
- `smb2_get_err_map()` returns the mapping record for a CPU-endian SMB2 status code or `NULL`.
- `map_smb2_to_linux_error()` reads `struct smb2_hdr::Status`, returns `0` for success, maps known failures to POSIX errors, defaults unmapped failures to `-EIO`, and emits trace/debug output.
- `smb2_init_maperror()` verifies at init time that the generated table is sorted ascending by status code.
- Under `CONFIG_SMB_KUNIT_TESTS`, `smb2_get_err_map_test`, `smb2_error_map_table_test`, and `smb2_error_map_num` are exported to `smb2maperror_test`.

## Control flow

Successful responses immediately emit `trace_smb3_cmd_done()` and return `0`. Error responses suppress ordinary notice logging for expected continuation/EOF statuses unless CIFS FYI/RC logging is enabled. The CPU-endian status is looked up in the generated table; found entries supply `rc` and optional `pr_notice()`. All error exits emit debug mapping output and `trace_smb3_cmd_err()`. Unmapped or deliberately `-EIO` mappings also call `smb_EIO1()` for EIO tracing.

## State and persistence behavior

The mapping table is static read-only after compilation. The file changes no persistent state. It reads global logging flags such as `cifsFYI` and contributes to tracing/logging side effects.

## Dependencies and integration points

It depends on Linux errno definitions, CIFS debug and trace helpers, SMB2 protocol declarations, `smb2glob.h` for the mapping struct, and common SMB2 status constants. `smb2transport.c` calls this through the server operation mapping path after SMB2 responses arrive. Tests use the conditional exports.

## Risks and edge cases

The binary search depends on table sort order; `smb2_init_maperror()` catches generation/order errors at module init. Missing mappings collapse distinct server statuses to `-EIO`, which is safe but can reduce user-visible accuracy. Logging must avoid noisy expected statuses such as `STATUS_MORE_PROCESSING_REQUIRED` and `STATUS_END_OF_FILE`. The function assumes `buf` points to at least an SMB2 header; callers must validate frame length before mapping.

## Test signals

`smb2maperror_test.c` validates lookup coverage for every generated table row. Additional useful tests are module init failure injection with unsorted generated data, spot checks for important statuses, and integration tests verifying session setup continuations and EOF do not produce excessive notice logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2maperror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2maperror_test.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb2maperror_test.c

## Purpose

This is a KUnit test module for SMB2 error mapping. It verifies that every generated `status_to_posix_error` table entry exported by `smb2maperror.c` can be found through the same binary-search lookup used by production code.

## Important APIs, types, and functions

- `test_cmp_map()` calls `smb2_get_err_map_test()` for one expected record and checks non-null result, status code equality, errno equality, and status-string equality.
- `maperror_test_check_search()` iterates from `0` to `smb2_error_map_num - 1` over `smb2_error_map_table_test`.
- `maperror_test_cases` registers the single exhaustive search test.
- `maperror_suite` names the KUnit suite `smb2_maperror`.

## Control flow

When the KUnit suite runs, it executes `maperror_test_check_search()`. The test loops over the exported generated table and delegates each row to `test_cmp_map()`. A missing lookup aborts that row with `KUNIT_ASSERT_NOT_NULL`; mismatched fields are reported with `KUNIT_EXPECT_*` checks.

## State and persistence behavior

The test does not mutate SMB client state and performs no I/O. It relies on read-only exported pointers/counts from the production mapping file when `CONFIG_SMB_KUNIT_TESTS` is enabled. It registers as a kernel test module with GPL metadata.

## Dependencies and integration points

The file includes KUnit, CIFS global definitions, `smb2glob.h`, and `smb2proto.h`. It depends on the production file exporting `smb2_get_err_map_test`, `smb2_error_map_table_test`, and `smb2_error_map_num` only for the `smb2maperror_test` module.

## Risks and edge cases

The test proves table rows are searchable, which indirectly detects sort/order problems and comparator mismatches. It does not check behavior for unknown statuses, log suppression, trace emission, `map_smb2_to_linux_error()` header parsing, or init-time order validation. Because it compares `status_string` with `KUNIT_EXPECT_STREQ`, table strings must be valid non-null C strings.

## Test signals

The direct signal is the KUnit suite `smb2_maperror`. A pass indicates every generated mapping row round-trips through `smb2_get_err_map_test()`. Complementary coverage should exercise unmapped status fallback and selected user-visible errno mappings through `map_smb2_to_linux_error()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2maperror_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2misc.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb2misc.c

## Purpose

This file provides miscellaneous SMB2/SMB3 protocol helpers: response header and length validation, data-area sizing, path conversion, lease-state construction, oplock/lease break dispatch, cleanup for cancelled creates/closes, and SMB3.1.1 preauthentication hash updates. It is a shared support layer for SMB2 transport and file/inode code.

## Important APIs, types, and functions

- `smb2_check_message()` validates a received SMB2 frame: protocol signature, server-to-client flag or allowed oplock-break request, header structure size, command range, response `StructureSize2`, maximum length, calculated length, negotiate context sizing, and known server padding quirks.
- `smb2_get_data_area_len()` extracts variable data offset/length for commands with payloads, with caps for suspicious offsets and lengths.
- `smb2_calc_size()` calculates expected SMB2 frame size from header, fixed parameter area, and optional data area.
- `cifs_convert_path_to_utf16()` strips disallowed leading separators for Windows/POSIX-extension paths and converts to UTF-16 using mount NLS/remapping.
- `smb2_get_lease_state()` maps CIFS cache flags and mount cache options to SMB2 lease-state bits.
- `smb2_is_valid_oplock_break()` and `smb2_is_valid_lease_break()` locate matching open files, pending opens, or cached directories and queue the appropriate break handling.
- `smb2_handle_cancelled_close()` and `smb2_handle_cancelled_mid()` schedule asynchronous closes for handles that might otherwise leak after interrupted commands.
- `smb311_update_preauth_hash()` updates the SMB3.1.1 preauth SHA-512 chain for negotiate and session setup traffic.

## Control flow

Receive validation begins with `smb2_check_message()`, which handles transform headers enough to find the session, checks the SMB2 header, validates fixed sizes from `smb2_rsp_struct_sizes`, calculates frame length, and tolerates documented server padding/excess cases. Size calculation delegates to `smb2_get_data_area_len()` based on command-specific offset/length fields.

Oplock-break handling distinguishes classic oplock responses from lease-break responses by structure size. It walks sessions and tree connections on the primary server, searches open file lists under `open_file_lock`, updates file/inode oplock state, sets pending-break flags, increments stats, and queues break work. Pending opens requiring acknowledgment are handled by copying the lease key and queuing `SMB2_lease_break()` work.

Cancelled handle cleanup allocates a `close_cancelled_open`, takes/owns a tcon reference when safe, and queues `SMB2_close()` on `cifsiod_wq`. Preauth hashing updates the session hash only for negotiate and relevant SMB3.1.1 session-setup messages.

## State and persistence behavior

Local state includes lease/oplock levels and epochs on `cifsFileInfo`, `CIFS_INODE_PENDING_OPLOCK_BREAK`, pending-open oplock values, tcon statistics, tcon references, queued work items, and `ses->preauth_sha_hash`. Remote state can be changed by queued lease-break acknowledgments and asynchronous closes. No local disk persistence is performed.

## Dependencies and integration points

The file depends on crypto SHA-512, CIFS core/session/tcon/open-file structures, cached directory lease handling, SMB2 status/PDU definitions, tracepoints, workqueues, and path conversion helpers. `transport.c` uses `smb311_update_preauth_hash()` during send/receive; SMB2 transport validation uses `smb2_check_message()`; cancellation paths use the handle cleanup helpers.

## Risks and edge cases

Length validation must balance strictness against real server padding quirks; accepting too much risks malformed-frame bugs, while rejecting tolerated padding can break interoperability. Lease-break scanning holds global session and per-tcon locks, so ordering and early unlock paths must stay correct. Cancelled close handling must not resurrect a closing tcon or leak a reference. Preauth hashing must skip the final successful session setup response and non-SMB3.1.1 traffic or authentication will fail.

## Test signals

Useful signals include packet-level validation tests for malformed SMB2 lengths and structure sizes, interoperability tests against servers with negotiate contexts and compound padding, oplock/lease-break integration tests, cancelled create/close interruption tests that watch server handle counts, and SMB3.1.1 authentication tests that verify preauth hash behavior. No direct KUnit file is included in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2misc.c -->
