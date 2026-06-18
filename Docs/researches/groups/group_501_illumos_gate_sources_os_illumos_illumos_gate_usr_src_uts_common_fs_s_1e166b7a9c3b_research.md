# Group Research: group_501_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_1e166b7a9c3b

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is in subset A. All 14 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_opipe.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_opipe.c

## Purpose

`smb_opipe.c` implements the SMB server's named-pipe bridge for IPC shares. It maps SMB message pipe opens, reads, writes, ioctl/FSCTL operations, and synthetic attributes onto AF_UNIX sockets under `SMB_PIPE_DIR`, allowing in-kernel SMB request handling to communicate with userland NDR/RPC pipe services.

## Main Interfaces

- `smb_opipe_open()` allocates an `smb_opipe_t`, connects to the named pipe service, sends authenticated user/client metadata, and installs the pipe on an SMB ofile.
- `smb_opipe_close()` shuts down and closes the underlying socket when the ofile closes.
- `smb_opipe_write()` and `smb_opipe_read()` move request/response bytes between SMB uios and the socket.
- `smb_opipe_ioctl()` forwards ioctl operations such as `FIONREAD`.
- `smb_opipe_getattr()` and `smb_opipe_getname()` provide synthetic pipe metadata.
- `smb_opipe_fsctl()` dispatches SMB2 named-pipe FSCTLs, with `FSCTL_PIPE_TRANSCEIVE` handled by `smb_opipe_transceive()` and `FSCTL_PIPE_WAIT` handled by `smb_opipe_wait()`.
- `smb_opipe_dealloc()` frees pipe state and closes a still-attached socket in open error paths.

## Behavior And Data Flow

Open handling creates a socket with the request credential, normalizes names such as `\PIPE\foo` to lowercase `foo`, connects to `${SMB_PIPE_DIR}/foo`, then sends an XDR-encoded `smb_netuserinfo_t` preceded by `smb_pipehdr_t`. The pipe service replies with an NT status, so access checks can be delegated to the service.

Pipe reads are intentionally single `recvmsg` calls: if no data is available they block, but they do not loop to fill the whole buffer. Pipe writes loop until the caller's uio is drained or the socket errors. Both take a socket hold under `p_mutex` so concurrent close can null `p_socket` safely while active I/O completes.

Blocking user-info exchange and pipe reads integrate with request cancellation. The request is moved to `SMB_REQ_STATE_WAITING_PIPE`, `cancel_method` is set to `smb_opipe_cancel`, and disconnect/termination can wake blocked socket reads by shutting down the socket. The cancellation path waits out `SMB_REQ_STATE_CANCEL_PENDING` before restoring state.

`FSCTL_PIPE_TRANSCEIVE` decodes input into an SMB VDB, writes it to the pipe, allocates mbufs for the response, reads once, attaches the mbuf to the FSCTL output, and approximates `NT_STATUS_BUFFER_OVERFLOW` by checking whether the output buffer filled and `FIONREAD` says more data remains.

## Dependencies

This file depends on illumos kernel socket APIs, SMB request/ofile/tree state, request-specific memory, SMB mbuf chains, XDR helpers from `smb_xdr.h`, `smb_user_netinfo_*`, and Windows named-pipe FSCTL constants from `smb/winioctl.h`.

## Notable Invariants And Risks

- `smb_opipe_t` objects are protected by `SMB_OPIPE_MAGIC`; socket lifetime is protected by `p_mutex` plus `ksocket_hold/rele`.
- `smb_opipe_cancel()` only shuts down the socket for session disconnect or termination, not normal SMB cancel requests.
- A blocked pipe operation can make the socket unusable after cancellation, so the logic is intentionally limited to teardown paths.
- `smb_opipe_open()` checks `smb_tree_is_connected()` after connect/userinfo because tree disconnect may race with slow pipe service startup.
- `smb_opipe_wait()` does not truly wait for pipe instance availability; it verifies existence and optionally delays briefly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_opipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_oplock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_oplock.c

## Purpose

`smb_oplock.c` contains SMB1-specific oplock support. It adapts SMB1 oplock requests, acknowledgements, and break notifications to the common SMB oplock engine while preserving SMB1 wire encodings and dialect-specific behavior.

## Main Interfaces

- `smb1_oplock_ack_break()` handles SMB1 `Locking_andX` oplock break acknowledgements.
- `smb1_oplock_send_break()` sends an SMB1 oplock break notification or performs a local break if the client cannot be reached or does not acknowledge.
- `smb1_oplock_acquire()` translates requested SMB1 oplock levels into internal oplock levels, calls common oplock request logic, and translates the result back to SMB1.

## Behavior And Data Flow

Break acknowledgement maps SMB1 `oplock_level == 0` to `OPLOCK_LEVEL_NONE` and any nonzero level to `OPLOCK_LEVEL_TWO`. It enters the node ofile list, takes `node->n_oplock.ol_mutex`, clears `og_breaking`, wakes waiters on `og_ack_cv`, calls common `smb_oplock_ack_break()`, and updates `ofile->f_oplock.og_state`.

Break notification composes a full SMB1 `SMB_COM_LOCKING_ANDX` response in the request reply chain, including a synthetic header and `LOCKING_ANDX_OPLOCK_RELEASE`. Internal break levels are converted to SMB1 values: none is `0`, level II is `1`.

`smb1_oplock_send_break()` downgrades level-II breaks to none for pre-NT dialect clients lacking level-II support. If `smb_session_send()` fails, it closes the ofile. If an acknowledgement is required and `smb_oplock_wait_ack()` fails, it performs the acknowledgement locally, always breaking to none.

Acquire logic rejects non-disk trees and trees without oplocks, honors session level-II capability, maps `SMB_OPLOCK_BATCH`, `SMB_OPLOCK_EXCLUSIVE`, and `SMB_OPLOCK_LEVEL_II` to internal states, optionally forces level-II for `SMB_TREE_FORCE_L2_OPLOCK`, tries exclusive/batch first, then level-II fallback if allowed.

## Dependencies

This file relies on common oplock helpers (`smb_oplock_request`, `smb_oplock_ack_break`, `smb_oplock_wait_ack`, `smb_oplock_wait_break`), SMB1 message encoding, session send, ofile close, tree feature flags, and per-node oplock locks.

## Notable Invariants And Risks

- All state mutation of `ofile->f_oplock` during ack/local-ack occurs under `node->n_oplock.ol_mutex`.
- SMB1 never has durable handles or granular oplocks; this file intentionally avoids SMB2 lease/durable semantics.
- `og_dialect` records whether the client can receive level-II breaks, independent of the negotiated SMB dialect.
- Failure to send a break closes the ofile rather than leaving stale caching rights.
- Timeout/no-ack handling logs in debug builds and falls back to local break-to-none.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_oplock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_pathname.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_pathname.c

## Purpose

`smb_pathname.c` implements SMB pathname normalization, reduction, lookup, stream parsing, validation, CATIA translation, DFS preprocessing, short-name unmangling, VSS snapshot lookup adjustment, and share-root confinement. It is the core adapter between Windows path semantics and illumos vnode/name lookup semantics.

## Main Interfaces

- `smb_is_executable()` marks `.EXE`, `.COM`, `.DLL`, and `.SYM` files as executable.
- `smb_pathname_reduce()` returns the directory node for the penultimate path component and the last component name.
- `smb_pathname()` walks a path component by component, handles symlinks, case-insensitive lookup, short-name unmangling, CATIA translation, reparse-point detection, and optional VSS mount replay.
- `smb_lookuppathvptovp()` performs a direct vnode-to-vnode lookup from a start vnode and root vnode.
- `smb_pathname_init()` parses a request path into directory path, filename, stream name, and stream type fields.
- `smb_pathname_validate()`, `smb_validate_dirname()`, `smb_validate_object_name()`, and `smb_validate_stream_name()` enforce SMB-visible name restrictions and set SMB error status.
- `smb_stream_parse_name()`, `smb_is_stream_name()`, and `smb_strname_restricted()` support named stream parsing and classification.

## Behavior And Data Flow

`smB_pathname_reduce()` converts backslashes to slashes, canonicalizes duplicate separators, handles DFS root paths when DFS operation flags are present, optionally extracts VSS GMT tokens, then either strips the last component or preserves it for VSS discovery. It uses `smb_pathname()` to resolve the parent path and then optionally remaps the resolved node to a snapshot node through `smb_vss_lookup_nodes()`. It also enforces mount traversal policy unless `SMB_TREE_TRAVERSE_MOUNTS` is enabled.

`smB_pathname()` allocates pathname buffers and walks `upn` one component at a time. Each component is translated from CATIA v5 to v4 if enabled, looked up with `lookuppnvp()` via `smb_pathname_lookup()`, and retried through `smb_unmangle()` if short names are supported and the input may be mangled. It treats filesystem reparse-point attributes as `EREMOTE`, resolves symlinks itself so SMB nodes can be created for each component, enforces `MAXSYMLINKS`, and creates/returns `smb_node_t` objects with the correct parent directory node.

`smB_pathname_init()` first preprocesses paths: blank paths become `\`, old dialect wildcard conversion is applied, `/` becomes `\`, duplicate separators collapse, trailing slashes are removed, `$EXTEND` is hidden as `.$EXTEND` at filesystem root, and admin share `C$` paths are lowercased. It then splits the path into `pn_pname`, `pn_fname`, `pn_sname`, and `pn_stype`, treating `::$DATA` as the unnamed stream and defaulting missing stream type to `:$DATA`.

Validation rejects leading `..`, wildcards in directory path components, `.` as a filename, colons in directory names, DOS device-style names like `COM1:`, and stream types outside `$CA`, `$DATA`, and `$INDEX_ALLOCATION`.

## Dependencies

This file depends on illumos `pathname_t` and `lookuppnvp`, SMB node lookup/reference management, `smb_fsops`, CATIA helpers, VSS helpers, DFS UNC parsing, access-based enumeration flags, short-name mangling/unmangling, request-specific memory, and SMB error-reporting helpers.

## Notable Invariants And Risks

- `smb_pathname_reduce()` returns `*dir_node` held on success and releases it on error.
- `smb_pathname()` returns `*ret_node` held and optionally `*dir_node` held.
- `lookuppnvp()` consumes holds on `dvp` and `rootvp`; `smb_pathname_lookup()` explicitly takes those holds first.
- CATIA v5-to-v4 translation that introduces `/` is rejected with `EILSEQ`.
- Reparse points are detected before symlink handling because they use `VLNK` but have different SMB semantics.
- VSS handling intentionally tries snapshot conversion even after some lookup errors so previous versions can survive live-tree renames.
- Path parsing and validation are security-sensitive because mistakes can cross share roots, expose hidden quota directories, mishandle streams, or turn Windows path syntax into unintended vnode lookups.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_pathname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_print.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_print.c

## Purpose

`smb_print.c` implements legacy SMB print-share commands. It creates print spool files on printer shares, tracks spool documents for userland print handling, queues closed FIDs for printing, provides a minimal print queue response, and appends print data.

## Main Interfaces

- `smb_pre_open_print_file()`, `smb_post_open_print_file()`, and `smb_com_open_print_file()` handle `SMB_COM_OPEN_PRINT_FILE`.
- `smb_pre_close_print_file()`, `smb_post_close_print_file()`, and `smb_com_close_print_file()` close and queue spool files.
- `smb_pre_get_print_queue()`, `smb_post_get_print_queue()`, and `smb_com_get_print_queue()` return a minimal optional queue response.
- `smb_pre_write_print_file()`, `smb_post_write_print_file()`, and `smb_com_write_print_file()` append data to a spool file.

## Behavior And Data Flow

Open-print preprocessing decodes setup length, mode, and identifier string, synthesizes a unique path from the identifier plus an atomic temporary id, and configures the open as `FILE_OVERWRITE_IF` and `FILE_NON_DIRECTORY_FILE`. The command path requires print support enabled and a printer tree, calls `smb_common_create()`, returns the FID, then creates an `smb_kspooldoc_t` with physical spool path, client IP, username, FID, and a spool number assigned by `smb_spool_add_doc()`.

Close-print decodes a FID, verifies printer tree type, delegates actual close to `smb_com_close()`, and calls `smb_spool_add_fid()` so the server spooldoc ioctl path can wake userland spool monitoring.

Write-print allocates an `smb_rw_param_t`, decodes the FID, verifies print support and handle validity, gets current file size, decodes data into a VDB, sets the write offset to append at EOF, and delegates to `smb_common_write()`.

## Dependencies

This file depends on open/create/write/close common SMB handlers, share lookup for `SMB_SHARE_PRINT`, server spool helpers in `smb_server.c`, request-specific memory, DTrace SMB probes, and printer-share configuration in `sv_cfg.skc_print_enable`.

## Notable Invariants And Risks

- Print commands are rejected unless print support is enabled and the tree is `STYPE_PRN`.
- Spool document ownership uses the SMB user name from `sr->uid_user`.
- `smb_com_close_print_file()` still closes the FID if printing becomes disabled while the FID is open.
- Queue enumeration is intentionally minimal and optional.
- The generated spool path uses client-provided identifier text plus an atomic id; correctness depends on upstream path sanitization and normal create semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_process_exit.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_process_exit.c

## Purpose

`smb_process_exit.c` implements the legacy SMB `SMB_COM_PROCESS_EXIT` command. The command tells the server a client process id has exited, allowing the server to close files and release locks associated with that SMB PID.

## Main Interfaces

- `smb_pre_process_exit()` starts DTrace accounting.
- `smb_post_process_exit()` finishes DTrace accounting.
- `smb_com_process_exit()` performs UID lookup and closes matching PID resources.

## Behavior And Data Flow

The command has no parameter or data words. `smb_com_process_exit()` looks up `sr->smb_uid`; if no user exists, it still returns an empty success response as the protocol expects limited errors. If the user exists, it gets the user's credential, attempts to look up the request TID, and closes resources for `sr->smb_pid` either within that tree or across the full session when no valid tree is supplied.

## Dependencies

This file depends on session UID lookup, user credentials, session/tree PID close helpers, SMB result encoding, and DTrace probes.

## Notable Invariants And Risks

- This is mainly for old SMB clients and tests; modern LANMAN-era clients typically close resources explicitly.
- Missing UID is not treated as a hard error.
- If a valid TID is present, cleanup is scoped to that tree; otherwise it scans all session trees.
- It relies on lower-level `smb_tree_close_pid()` and `smb_session_close_pid()` to release locks and ofiles correctly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_process_exit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_query_fileinfo.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_query_fileinfo.c

## Purpose

`smb_query_fileinfo.c` implements SMB1 file and path information query commands, including Trans2 query by FID/path, legacy query information commands, passthrough NT information levels, named-pipe metadata, stream enumeration, short-name reporting, compression info stubs, and response encoding.

## Main Interfaces

- `smb_com_trans2_query_file_information()` handles Trans2 query by FID.
- `smb_com_trans2_query_path_information()` handles Trans2 query by path.
- `smb_pre_query_information()`, `smb_post_query_information()`, and `smb_com_query_information()` implement legacy path getattr.
- `smb_pre_query_information2()`, `smb_post_query_information2()`, and `smb_com_query_information2()` implement legacy FID getattr.
- `smb_query_encode_response()` encodes all supported information levels from `smb_queryinfo_t`.
- `smb_query_stream_info()` enumerates unnamed and named streams.
- `smb_query_fileinfo()` fills query data for disk files.
- `smb_query_shortname()` generates or uppercases alternate 8.3 names.

## Behavior And Data Flow

FID queries look up `sr->smb_fid`, reject invalid name-valid queries, validate pipe information levels for message pipes, then fill `smb_queryinfo_t` from either `smb_query_fileinfo()` or pipe-specific synthetic state before encoding.

Path queries reject IPC trees, reject by-path `SMB_FILE_ACCESS_INFORMATION` as unsupported, initialize and validates the path, reduce it to parent plus leaf name, look up the node, reject DFS links as `NT_STATUS_PATH_NOT_COVERED` when DFS flags apply, populate file info, reject delete-pending objects, encode the response, and release the node.

Response encoding covers legacy 16/32-bit time and size formats, EA-size placeholders, basic/standard/name/all/internal/network/open/attr-tag passthrough levels, short names, stream info, compression info with no compression, and 32-bit size saturation for older responses.

Stream enumeration follows observed Windows behavior: regular files include `::$DATA` even with no named streams; directories omit unnamed stream entries; named streams are appended from `smb_odir_read_streaminfo()` with 8-byte alignment and `NextEntryOffset` patching. Buffer exhaustion returns partial entries with `NT_STATUS_BUFFER_OVERFLOW`.

## Dependencies

This file depends on SMB path processing, SMB filesystem operations, node getattr/path helpers, short-name mangle helpers, stream directory enumeration, mbuf-chain encoding, pipe attribute helpers, and SMB status/error mapping.

## Notable Invariants And Risks

- `smb_query_by_path()` expects `sr->fid_ofile == NULL`; mixed chained commands that leave a FID set are treated cautiously as errors.
- Message pipes support only a subset of information levels and use synthetic attributes.
- Short-name queries fail with object-not-found when short names are disabled.
- Delete-on-close decrements reported link count and by-path queries return delete-pending.
- Stream enumeration treats read-stream errors as end-of-stream after already encoded entries, matching Windows-style tolerance.
- Incorrect padding or `NextEntryOffset` values in stream info can break Windows clients.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_query_fileinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_quota.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_quota.c

## Purpose

`smb_quota.c` implements SMB quota query/set support helpers. It decodes SID lists and quota entries from SMB wire buffers, encodes quota responses, maintains per-ofile quota resume state, maps local UIDs to SIDs for user quota queries, and calls userland quota services via SMB kernel door upcalls.

## Main Interfaces

- `smb_quota_init_sids()` initializes a query SID list based on query operation.
- `smb_quota_free_sids()` releases decoded SID lists.
- `smb_quota_decode_sids()` decodes client-provided SID entries.
- `smb_quota_max_quota()` derives maximum requested quota entries from response buffer size and query flags.
- `smb_quota_decode_quotas()` decodes quota entries for set operations.
- `smb_quota_free_quotas()` releases quota lists.
- `smb_quota_encode_quotas()` encodes quota query responses and updates resume SID.
- `smb_quota_query_user_quota()` queries quota for a single local UID.
- `smb_quota_query()` and `smb_quota_set()` perform door upcalls.

## Behavior And Data Flow

SID-list and quota-list decoders walk variable-length entries using `next_offset`, shadow the mbuf chain at each entry, decode fixed fields, decode SIDs from calculated offsets, convert them to SID strings, and append typed objects to illumos lists. Query initialization either decodes explicit SID lists, decodes a start SID, or resumes from the ofile's stored quota resume SID for query-all.

Quota encoding converts SID strings back to `smb_sid_t`, calculates fixed size plus SID length plus 8-byte padding, checks output room, encodes fixed fields and SIDs, pads entries, sets the last entry's `next_offset` to zero, and stores the last emitted SID as resume state for start/all queries.

Single-user quota lookup maps a local UID to a SID, constructs a SID-list query rooted at the tree mount path, calls the userland quota door service, validates that the returned quota matches the requested SID, copies it out, and frees XDR-owned reply structures.

## Dependencies

This file depends on SMB mbuf-chain shadowing and encoding, SID encode/decode/string conversion, idmap UID-to-SID mapping, SMB tree mount path helpers, `smb_kdoor_upcall`, XDR routines for quota requests/responses, and ofile quota resume accessors.

## Notable Invariants And Risks

- Quota wire entries use fixed fields plus variable SID data and 8-byte alignment.
- Decode loops trust `next_offset` progression and `bytes_left`; malformed offsets must be rejected by mbuf shadow/decode failures.
- Query-all without restart requires a valid stored resume SID or returns `NT_STATUS_INVALID_PARAMETER`.
- `SMB_QUOTA_QUERY_SIDLIST` ignores `qq_max_quota`; start/all derive it from response buffer capacity unless single-entry is requested.
- Door call return `0` means transport/XDR success; operation status is carried separately in the reply.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_read.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_read.c

## Purpose

`smb_read.c` implements SMB1 read command variants and common read logic for disk files and IPC named pipes. It decodes request parameters, handles lock-and-read, rejects obsolete raw read, encodes read responses, checks access/locks, and updates ofile seek position.

## Main Interfaces

- `smb_pre_read()`, `smb_post_read()`, and `smb_com_read()` implement core `SMB_COM_READ`.
- `smb_pre_lock_and_read()`, `smb_post_lock_and_read()`, and `smb_com_lock_and_read()` implement core-plus lock-and-read.
- `smb_pre_read_raw()`, `smb_post_read_raw()`, and `smb_com_read_raw()` provide an unsupported read-raw handler for tracing and proper errors.
- `smb_pre_read_andx()`, `smb_post_read_andx()`, and `smb_com_read_andx()` implement `SMB_COM_READ_ANDX`, including 64-bit offset and large-read count decoding.
- `smb_common_read()` performs the actual disk or pipe read.

## Behavior And Data Flow

Core reads decode 32-bit offsets and 16-bit counts, cap core read size at `SMB_CORE_READ_MAX`, call common read, and encode returned raw data. Lock-and-read validates a disk tree, applies a 16-bit SMB1 PID byte-range lock with no waiting, then reads only if the lock succeeds.

Read-andX decodes either 10-word or 12-word forms. The 12-word LM 0.12 form combines high and low offset fields and can combine high and low count fields when `CAP_LARGE_READX` is negotiated, ignoring `maxcnt_high == 0xFF`. Requests at or above `SMB_READX_MAX` are clamped to zero before common read. Response encoding differs for IPC versus disk: IPC uses named-pipe semantics and regular files encode `-1` in the reserved field.

`smB_common_read()` initializes a VDB/uio and routes by tree type. Disk reads reject conflicting byte-range locks, enforce execute-only access unless `SMB_FLAGS2_READ_IF_EXECUTE` is set, allocate mbufs, call `smb_fsop_read()`, trim and attach returned data. IPC reads allocate mbufs and call `smb_opipe_read()`. Both update `param->rw_count`, optional `rw_mincnt`, `rw_offset`, and `ofile->f_seek_pos`.

## Dependencies

This file depends on SMB request decoding/encoding, file lookup/release, byte-range locking, `smb_fsop_read`, named-pipe read support, mbuf allocation/trimming, tree share type macros, and ofile credentials/state.

## Notable Invariants And Risks

- All command handlers must look up and validate the FID before calling `smb_common_read()`.
- Lock-and-read uses SMB1 16-bit PID semantics.
- Directory reads skip byte-range checks but still go through filesystem read behavior.
- Execute-only handles can be read only when the request explicitly sets `SMB_FLAGS2_READ_IF_EXECUTE`.
- Named-pipe reads may block and rely on pipe cancellation/teardown behavior from `smb_opipe.c`.
- `f_seek_pos` is advisory legacy state; SMB read/write requests carry explicit offsets.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_rename.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_rename.c

## Purpose

`smb_rename.c` implements legacy SMB1 rename, NT rename, hard-link creation via NT rename information level, and a no-op NT transact rename compatibility handler.

## Main Interfaces

- `smb_pre_rename()`, `smb_post_rename()`, and `smb_com_rename()` handle `SMB_COM_RENAME`.
- `smb_pre_nt_rename()`, `smb_post_nt_rename()`, and `smb_com_nt_rename()` handle `SMB_COM_NT_RENAME`.
- `smb_nt_transact_rename()` validates a handle for NT transact rename and returns success without renaming, matching Windows behavior.

## Behavior And Data Flow

Legacy rename decodes source search attributes and source/destination paths, requires a disk tree, initializes and validates both pathnames, then delegates to `smb_common_rename()`. Wildcard rename is documented but not supported here.

NT rename decodes search attributes, information level, cluster count, and paths. It rejects non-disk trees, validates paths, rejects wildcard source paths with `NT_STATUS_OBJECT_PATH_SYNTAX_BAD`, then dispatches by information level: hard link uses `smb_make_link()`, rename/move use `smb_common_rename()`, move-cluster returns invalid parameter, and unknown levels return access denied.

NT transact rename only decodes a FID, validates that it exists, releases it, and returns success. The comment states this mirrors Windows servers, which do not rename in this path.

## Dependencies

This file depends on SMB path parsing/validation, common rename and hard-link filesystem helpers, FID lookup/release, tree type checks, request decode/encode, DTrace probes, and SMB error mapping.

## Notable Invariants And Risks

- Rename commands are valid only on disk trees.
- Path validation occurs before common filesystem operations.
- NT rename disallows wildcard source paths explicitly.
- Actual rename collision, delete-pending, share-mode, link, and filesystem semantics live in `smb_common_rename()` and `smb_make_link()`, not this adapter file.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_rename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_sd.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_sd.c

## Purpose

`smb_sd.c` converts between Windows security descriptors and filesystem security structures. It reads filesystem owner/group/ACL data into an absolute SMB security descriptor, converts absolute SMB descriptors back to filesystem/ZFS ACL structures, maps SIDs to local ids and local ids to SIDs, and manages descriptor memory.

## Main Interfaces

- `smb_sd_init()` initializes an absolute security descriptor.
- `smb_sd_term()` frees owner, group, DACL, and SACL members.
- `smb_sd_len()` computes encoded security descriptor length for requested security information.
- `smb_sd_get_secinfo()` infers security information bits from a descriptor, used by create-with-SD.
- `smb_sd_read()` reads filesystem security and converts it to SMB form.
- `smb_sd_write()` converts SMB form to filesystem form and writes it.
- `smb_sd_tofs()` converts Windows SD owner/group/DACL/SACL into `smb_fssd_t`.
- `smb_fssd_init()` and `smb_fssd_term()` manage filesystem SD wrappers.

## Behavior And Data Flow

Reads initialize an `smb_fssd_t` with requested `secinfo` and directory flag, call `smb_fsop_sdread()`, then `smb_sd_fromfs()` builds an absolute Windows descriptor. Owner and group IDs are mapped to SIDs with `smb_idmap_getsid`; ZFS ACLs are converted to Windows ACLs with `smb_acl_from_zfs`; DACLs are sorted before returning to Windows clients; present/defaulted/auto-inherit/protected control bits are reconstructed from filesystem ACL flags.

Writes initialize an `smb_fssd_t`, call `smb_sd_tofs()`, and then `smb_fsop_sdwrite()`. Owner and group SIDs are validated and mapped to UID/GID with `smb_idmap_getid`. DACL and SACL conversion uses `smb_acl_to_zfs()` with flags derived from descriptor control bits and directory status. `EBADE` from filesystem write is mapped to `NT_STATUS_INVALID_OWNER`.

## Dependencies

This file depends on SMB filesystem SD operations, SMB/ZFS ACL conversion helpers, SMB SID validation and memory management, idmap, security descriptor control flags, and node type helpers.

## Notable Invariants And Risks

- `smb_sd_term()` assumes an absolute descriptor, not a self-relative descriptor.
- `secinfo` controls which descriptor parts the client intends to read or write; it also controls removal of present bits.
- Filesystem DACL cannot be absent in the same way Windows can represent it; the code treats a NULL DACL as equivalent to everyone-full for filesystem conversion.
- SID/idmap failures return `NT_STATUS_NONE_MAPPED` or `NT_STATUS_INVALID_SID`.
- DACL order matters to Windows GUI behavior, so DACLs are sorted on read.
- SACL handling preserves present/protected/auto-inherit-style flags but only converts when SACL is present.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_sd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_seek.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_seek.c

## Purpose

`smb_seek.c` implements the legacy SMB seek command, which sets and returns the current file pointer associated with a FID. It exists for old clients; modern SMB reads and writes carry explicit offsets.

## Main Interfaces

- `smb_pre_seek()` starts DTrace accounting.
- `smb_post_seek()` finishes DTrace accounting.
- `smb_com_seek()` decodes and executes the seek.

## Behavior And Data Flow

`smB_com_seek()` decodes FID, seek mode, and signed 32-bit offset. It validates the FID, gets the ofile credential, delegates offset calculation and state update to `smb_ofile_seek()`, maps `EINVAL` to `ERRbadfunc` and other errors to server error, then encodes the resulting 32-bit offset.

Supported modes are start-of-file, current position, and end-of-file. Attempts to seek before the file start clamp to start via lower-level seek behavior. The file comment notes that offsets beyond 32-bit range are treated as errors rather than returning truncated low bits.

## Dependencies

This file depends on FID lookup, ofile credentials, `smb_ofile_seek()`, SMB result encoding, SMB error reporting, and DTrace probes.

## Notable Invariants And Risks

- The wire protocol exposes only 32-bit offsets, so this command is inappropriate for large-file positioning.
- Seek state is advisory and can be overwritten by subsequent read/write/seek requests.
- Correct large-offset rejection depends on `smb_ofile_seek()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_seek.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_server.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_server.c

## Purpose

`smb_server.c` is the SMB server management core. It owns global initialization, per-zone server lifecycle, service configuration, startup/shutdown, listener sockets, session creation/destruction, kstats, counters, event wait/notify objects, spool queues, share disconnect, server lookup/refcounting, and ioctl-facing management operations.

## Main Interfaces

- Global lifecycle: `smb_server_g_init()`, `smb_server_g_fini()`, `smb_server_get_count()`.
- Per-server lifecycle: `smb_server_create()`, `smb_server_delete()`, `smb_server_configure()`, `smb_server_start()`, `smb_server_stop()`, `smb_server_is_stopping()`.
- Management ioctls: `smb_server_spooldoc()`, `smb_server_set_gmtoff()`, `smb_server_numopen()`, `smb_server_enum()`, `smb_server_session_close()`, `smb_server_file_close()`.
- Share/session operations: `smb_server_share_lookup()`, `smb_server_unshare()`, `smb_server_lookup_user()`, `smb_server_logoff_ssnid()`.
- Lookup/reference: `smb_server_lookup()`, `smb_server_release()`.
- Counters: `smb_server_inc_*`, `smb_server_dec_*`, `smb_server_add_rxb()`, `smb_server_add_txb()`, `smb_server_inc_req()`.
- Event API: `smb_event_create()`, `smb_event_destroy()`, `smb_event_txid()`, `smb_event_wait()`, `smb_event_notify()`, `smb_server_cancel_event()`.
- Spool API: `smb_spool_add_fid()`, `smb_spool_add_doc()`.

## Behavior And Data Flow

Global init initializes VOP/FEM layers, share/codepage/mbc/node/lease subsystems, kmem caches for core SMB object types, and global server/session-zombie lists. Global fini asserts no servers remain and tears those subsystems down in reverse.

`smB_server_create()` enforces one server per zone, allocates and initializes `smb_server_t`, persistent handle and lease hash tables, session/event/spool lists, dispatch stats arrays, timers, request queue, kdoor/kshare/kstat state, threshold counters, and inserts the server into the global list.

`smB_server_start()` transitions configured servers to running. It may create a kernel process to own SMB worker LWPs, initializes root SMB node state, creates a special server session and root user, starts kshare, creates notify/worker/receiver taskqs, opens userland doors, starts the timer thread, creates TCP and optional NetBIOS listeners, and starts SMB export. On failure it calls `smb_server_shutdown()`.

Shutdown stops listeners first, disconnects all sessions, cancels events and threshold waits, waits for the session list to drain, closes doors, stops exports and shares, stops timers, logs off root/server-session state, destroys taskqs, shuts down durable handles, releases root node state, and stops the optional server process.

Listener code creates AF_INET/AF_INET6 sockets, sets socket options, binds/listens on port 445 and optionally 139, accepts connections, sets TCP options, creates sessions, inserts them under max-connection enforcement, and dispatches receiver tasks. Receiver completion destroys or quarantines sessions depending on whether they reached clean shutdown.

## Kstats And Configuration

`smB_server_kstat_init()` creates raw and legacy kstats. Updates report active sessions, users, trees, files, pipes, bytes sent/received, request counts, server utilization, and SMB1/SMB2 dispatch stats. Configuration storage copies all relevant daemon-provided knobs including worker limits, keepalive, signing, oplocks, sync, NetBIOS/IPv6/printing, mount traversal, protocol min/max, encryption, ciphers, signing algorithms, credits, machine UUID, negotiation token, native strings, domain, FQDN, hostname, and comments. Required encryption forces max protocol to at least SMB 3.0.

## Event And Spool Handling

Event objects are server-list members with txids, timeouts, mutex/cv state, notification and cancellation flags. `smb_event_wait()` loops in one-second increments until notified, canceled, or timed out. Shutdown cancels all events.

Print spool handling maintains one list of spool documents and another list of closed FIDs. Close queues a FID and wakes `smb_server_spooldoc()`, which pops a FID, finds/removes the matching spool document, and returns path/user/IP/spool number to userland.

## Dependencies

This file coordinates nearly every SMB subsystem: nodes, shares, sessions, users, trees, ofiles, oplocks/durable handles, leases, kdoors, filesystem ops, taskq, kernel sockets, kstats, DTrace, thresholds, request queues, exports, and printing.

## Notable Invariants And Risks

- Server state transitions are guarded by `sv_mutex`; deletion waits for `sv_refcnt` to drain.
- New server lookup refuses `SMB_SERVER_STATE_DELETING`.
- Shutdown must stop listeners before disconnecting sessions to prevent new work during teardown.
- It waits for session readers/workers to finish before destroying taskqs and shared server-session resources.
- Session objects that fail clean shutdown are moved to a zombie list for debugging instead of being freed.
- `smb_server_logoff_ssnid()` is careful to wait for durable handles to become orphaned before reconnect can reuse them.
- Socket listener failures during startup can leave partial listener state; shutdown handles cleanup.
- The file is concurrency-critical: global lists, server lists, session lists, event lists, spool lists, and refcounts all have distinct locking expectations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_server.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_session.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_session.c

## Purpose

`smb_session.c` implements SMB session transport, request receive/dispatch, session object lifecycle, cancellation, tree/user lookup and teardown, NetBIOS session setup, SMB-over-TCP/NBT headers, keepalive tracking, and SMB request allocation/freeing.

## Main Interfaces

- Transport send/receive: `smb_session_send()`, `smb_session_xprt_gethdr()`.
- Session receiver: `smb_session_receiver()` and internal `smb_session_reader()`.
- Session lifecycle: `smb_session_create()`, `smb_session_delete()`, `smb_session_disconnect()`, `smb_session_logoff()`.
- Request lifecycle: `smb_request_alloc()`, `smb_request_free()`, `smb_request_cancel()`, `smb_session_cancel_requests()`.
- Lookup helpers: `smb_session_lookup_uid()`, `smb_session_lookup_ssnid()`, `smb_session_lookup_uid_st()`, `smb_session_lookup_tree()`.
- Cleanup helpers: `smb_session_close_pid()`, `smb_session_disconnect_owned_trees()`, `smb_session_disconnect_share()`.
- Client/oplock helpers: `smb_session_getclient()`, `smb_session_isclient()`, `smb_session_oplocks_enable()`, `smb_session_levelII_oplocks()`.
- Timers: `smb_session_timers()`.

## Behavior And Data Flow

`smB_session_receiver()` optionally handles a NetBIOS session request on port 139, transitions the session to established, starts an authentication timeout, and calls `smb_session_reader()`. When reading ends, it marks the session disconnected unless already terminated, cancels the auth timeout, shuts down the socket, and calls session cancellation.

The reader loops over 4-byte transport headers, handles keepalives, validates message length, allocates an SMB request, receives the full message into an mbuf chain, accounts received bytes, and calls the session's `newrq_func`. Initially `newrq_func` is `smbsr_newrq_initial()`, which accepts only SMB1 or SMB2 negotiate magic and then lets the SMB1/SMB2 negotiate path install the appropriate request posting function.

Transport send prepends a 4-byte NBT/direct-hosted SMB header, encodes the type/length for port 139 or port 445 semantics, sends mbufs, and always consumes/frees the provided mbuf chain. Header receive validates direct-hosted type zero on port 445.

Session creation allocates id pools, lists, transmit state, locks, random challenge/session keys, copies current server config, records socket addresses and ports for real connections, increments server NBT/TCP counters, and sets command/reply maxima. A special socketless server session is created for server-internal activity and uses a modern dialect/config without map/unmap upcalls.

## Cancellation And Teardown

`smB_request_cancel()` transitions request states carefully. Waiting states require a non-null cancel method; the cancel method runs without holding `sr_mutex`, then the canceller broadcasts the state cv. Completed/cancelled/free-state behavior is explicitly separated.

Session cancellation cancels all outstanding requests, disconnects `IPC$` trees to unblock pipe reads, waits for the request list to empty, closes transaction state objects, and logs off all users. `smb_session_logoff()` walks users, logs off logging-on/logged-on users, waits briefly for user objects to disappear, marks the session shutdown if the user list empties, then disconnects remaining trees.

Tree disconnect helpers post destructors to list flush queues so potentially blocking unmap/disconnect operations do not run while holding list locks. Share-specific disconnect also cancels requests using the affected tree.

## Dependencies

This file depends on kernel sockets, SMB network send/receive mbuf helpers, NetBIOS name parsing, SMB1/SMB2 negotiate entry points, request queues, session/user/tree/ofile state machines, task cancellation, durable handle/session logoff behavior, random number generation, and server counters/config.

## Notable Invariants And Risks

- New requests are allowed only while session state is connected/initialized/established/negotiated.
- Every allocated request is inserted into `s_req_list` and removed during `smb_request_free()`.
- Request free releases ofile, tree, user, tree-connect user, request-specific memory, and mbuf chains.
- Authentication timeout protects sessions with no authenticated users.
- Keepalive timer decrement is currently incomplete; comments note idle-session killing is not implemented.
- `smb_reader_delay` exists only to serialize request dispatch for smbtorture workarounds.
- Cancellation correctness depends on each waiting state installing exactly one valid `cancel_method`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_session.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_session_setup_andx.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_session_setup_andx.c

## Purpose

`smb_session_setup_andx.c` implements SMB1 `SessionSetupAndX` request parsing and response encoding. It supports pre-NTLM 0.12, NTLM 0.12 without extended security, and NTLM 0.12 extended-security session setup flows.

## Main Interfaces

- `smb_pre_session_setup_andx()` decodes the request into `smb_arg_sessionsetup_t`.
- `smb_post_session_setup_andx()` ends tracing and zeroes decoded password buffers.
- `smb_com_session_setup_andx()` updates session limits/capabilities, invokes authentication, maps authentication statuses to SMB errors, and encodes the setup response.

## Behavior And Data Flow

Preprocessing allocates `smb_arg_sessionsetup_t` from request storage and enforces a minimum word count of 10. It decodes the common AndX command/offset, max buffer size, and max multiplex count. For dialects before NT LM 0.12, it decodes only an LM password and optional user/domain strings. For NT LM 0.12 word count 13, it decodes LM and NT password lengths, capabilities, clears extended-security capability defensively, then decodes LM password, NT password, user, and domain. For word count 12, it requires `CAP_EXTENDED_SECURITY`, decodes an input security blob, and defers user/domain identity to extended authentication.

The parser then decodes native OS and native LanMan strings. Native OS/LanMan parsing is tolerant; failures default to NT-style values. NT4 padding quirks are handled by using a different decode pattern when native OS is recognized as Windows NT.

The command path updates session message size, max mpx, capabilities, and native OS/LM on first calls. If server configuration requires encryption, SMB1 access is rejected. Authentication is delegated to `smb_authenticate_ext()` for extended security or `smb_authenticate_old()` for legacy forms. Success and continuation responses include guest action flag, optional output security blob, and server native OS/LM/domain strings.

## Dependencies

This file depends on SMB request decode/encode helpers, session fields, server config, legacy and extended SMB authentication helpers, native OS/LanMan classification, request-specific memory, SMB token/idmap headers, and DTrace probes.

## Notable Invariants And Risks

- Password buffers are zeroed in post-processing before request storage is freed.
- Extended-security requests must advertise `CAP_EXTENDED_SECURITY`.
- `NT_STATUS_MORE_PROCESSING_REQUIRED` is encoded as an SMB status but is not treated as fatal.
- Required SMB3 encryption disables SMB1 session setup entirely.
- First-call detection for extended security uses `smb_uid == 0` or `0xFFFF`; follow-up calls preserve existing session properties.
- Native OS/LanMan strings are not security-critical and parsing is intentionally forgiving.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_session_setup_andx.c -->