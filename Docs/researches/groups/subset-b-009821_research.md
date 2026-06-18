# Research: subset-b-009821

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clifsinfo.c -->
# sources/user-network-fs/samba/source3/libsmb/clifsinfo.c

## Purpose

This file implements SMB client filesystem-information helpers for Unix extensions, filesystem attributes, volume and size information, POSIX filesystem statistics, and POSIX identity discovery. The SMB1 path is built on Trans2 `QFSINFO`/`SETFSINFO`; selected calls dispatch to SMB2 helpers when `smbXcli_conn_protocol(cli->conn) >= PROTOCOL_SMB2_02`.

## Important APIs, Types, and Functions

Important exported APIs are `cli_unix_extensions_version[_send/_recv]`, `cli_set_unix_extensions_capabilities[_send/_recv]`, `cli_get_fs_attr_info[_send/_recv]`, `cli_get_fs_volume_info`, `cli_get_fs_full_size_info`, `cli_get_posix_fs_info[_send/_recv]`, and `cli_posix_whoami[_send/_recv]`. Per-call state structs keep Trans2 setup/parameter buffers and parsed response fields. `cli_unix_extensions_version_recv()` updates `cli->server_posix_capabilities`; the set-capabilities completion updates `cli->requested_posix_capabilities` only after a successful server reply.

## Control Flow

Async send functions allocate a `tevent_req`, fill SMB1 setup/parameter/data buffers with `SSVAL`/`SIVAL`, call `cli_trans_send()`, and parse replies in callbacks. Synchronous wrappers reject use while other async calls are active, create a temporary event context, poll the request, then call the recv side. SMB2-specific filesystem attribute, volume, full-size, and POSIX filesystem info calls route to `cli_smb2_*` helpers instead of SMB1 Trans2. `cli_posix_whoami_done()` parses guest status, uid/gid, supplementary gids, and NDR-encoded SIDs from a bounded Trans2 response.

## State and Persistence Behavior

The file has no durable storage of its own. Persistent effects are limited to server state changed by `SMB_SET_CIFS_UNIX_INFO` and in-memory capability fields on `cli_state`. Returned arrays for POSIX gids/SIDs are talloc-owned and moved to the caller in recv functions. Response buffers are transient and freed after parsing.

## Dependencies and Integration Points

The file depends on `cli_trans`, SMB2 fnum helpers, tevent NTSTATUS helpers, Trans2 constants, gensec/credentials headers, and NDR security SID parsing. It feeds higher-level client logic that needs dialect capabilities, Unix extension negotiation, statfs-like data, quota-sized volume information, and POSIX identity mapping.

## Risks and Test Signals

Parsing risk is concentrated in server-controlled lengths: volume-name byte counts, 64-bit POSIX fields, whoami gid/SID counts, and residual bytes after SID decoding. Tests should cover SMB1 and SMB2 dialects, malformed short responses, oversized whoami counts, unknown SID encodings, capability field updates only on success, and sync wrapper rejection when async calls are outstanding.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clifsinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clilist.c -->
# sources/user-network-fs/samba/source3/libsmb/clilist.c

## Purpose

This file implements directory enumeration for SMB clients across old SMB search, SMB1 Trans2 find, and SMB2 find paths. It normalizes returned directory entries into `struct file_info`, validates server-returned names, and offers both async one-entry-at-a-time iteration and a synchronous callback wrapper.

## Important APIs, Types, and Functions

Key APIs are `is_bad_finfo_name()`, `cli_list_send()`, `cli_list_recv()`, `cli_list()`, and legacy `cli_list_old()`. Internal parsers include `interpret_short_filename()`, `interpret_long_filename()`, and `calc_next_entry_offset()`. State structs `cli_list_old_state`, `cli_list_trans_state`, and `cli_list_state` track search masks, Trans2 handles, resume keys, raw last names, accumulated `file_info` arrays, and per-entry delivery progress.

## Control Flow

`cli_list_send()` chooses SMB2 listing, SMB1 Trans2 find, or old `SMBsearch` based on dialect. The Trans2 path sends `FINDFIRST`, parses returned records according to the requested info level, stores entries, then sends `FINDNEXT` using resume key and last filename bytes until end-of-search. The old path loops `SMBsearch` and finally closes with `SMBfclose`. `cli_list_recv()` can be called repeatedly; it moves one `file_info` to the caller and defers the request callback so async consumers receive entry notifications.

## State and Persistence Behavior

No persistent filesystem state is modified. Client-side state includes accumulated directory entries, raw resume names, old-search status bytes, and protocol search handles. The code disconnects the SMB connection if a server returns names containing `/` or, for Windows pathnames, `\`, treating such names as hostile network responses.

## Dependencies and Integration Points

The file integrates with `cli_smb2_list_*`, `cli_trans`, `cli_smb_send`, DFS path rewriting through `smb1_dfs_share_path()`, time conversion helpers, Trans2 info-level constants, and `dir_check_ftype()` for SMB2-side attribute filtering. Higher-level file, tree, and client tools consume `cli_list()` for wildcard scans.

## Risks and Test Signals

Important risks are malformed record offsets, name-length overrun, Unicode conversion failures, looping `FINDNEXT` responses, and mismatched SMB2 attribute filtering semantics. Tests should inject truncated old-search records, invalid next offsets, bad short-name lengths, unsafe separators, repeated resume names, empty matches, SMB2 no-more-files behavior, and callback errors stopping iteration.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clilist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/climessage.c -->
# sources/user-network-fs/samba/source3/libsmb/climessage.c

## Purpose

This file implements the legacy SMB "send message" client sequence. It starts a message to a destination host/user, sends the text in SMB-sized chunks, and terminates the message group.

## Important APIs, Types, and Functions

The public APIs are `cli_message_send()`, `cli_message_recv()`, and synchronous `cli_message()`. Internal helpers are `cli_message_start_send/recv`, `cli_message_text_send/recv`, and `cli_message_end_send/recv`. Their state structs carry the message group id, text word parameter, event context, CLI pointer, sent byte count, and original message pointer.

## Control Flow

`cli_message_send()` chains three SMB commands: `SMBsendstrt`, one or more `SMBsendtxt`, then `SMBsendend`. Start converts user and host from Unix to DOS charset and returns a group id if the server supplies one. Text chunks are limited to 127 bytes from the original message string; each chunk is converted to DOS charset if possible, otherwise sent in the Unix charset with a debug message. The sync wrapper creates a private event loop and rejects calls when other async calls exist.

## State and Persistence Behavior

The file keeps only request-local state. The durable side effect is remote server delivery of a legacy SMB message. The sent counter advances by source-string chunk length, not converted byte count, so state is tied to the input string boundaries.

## Dependencies and Integration Points

It depends on `cli_smb_send/recv`, tevent request helpers, charset conversion, and `smbXcli_conn_has_async_calls()`. It is a legacy SMB1 facility and does not branch to SMB2.

## Risks and Test Signals

Risks include charset conversion failures, repeated `strlen()` on mutable caller memory, chunking multi-byte input by source bytes, and ambiguous behavior when `SMBsendstrt` returns no group word. Tests should cover empty messages, >127-byte messages, conversion failures, missing group id, server errors at each phase, and sync rejection during active async traffic.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/climessage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clioplock.c -->
# sources/user-network-fs/samba/source3/libsmb/clioplock.c

## Purpose

This file implements SMB1 oplock-break waiting and acknowledgement. It lets a client register a pending request for the special oplock break MID and send the `LOCKING_ANDX_OPLOCK_RELEASE` acknowledgement when a break is received.

## Important APIs, Types, and Functions

Public APIs are `cli_smb_oplock_break_waiter_send()`, `cli_smb_oplock_break_waiter_recv()`, `cli_oplock_ack_send()`, and `cli_oplock_ack_recv()`. `cli_smb_oplock_break_waiter_state` stores the fnum and new level parsed from the unsolicited break packet; `cli_oplock_ack_state` is only a placeholder for tevent allocation.

## Control Flow

The waiter creates a fake SMB1 request with `smb1cli_req_create()`, sets its MID to `0xffff`, marks it pending with `smbXcli_req_set_pending()`, and waits for the connection layer to complete it with an oplock break packet. The callback validates at least eight words, extracts fnum from word 2 and level from word 3 high byte, and completes. Acknowledgement delegates to `cli_lockingx_send()` with `LOCKING_ANDX_OPLOCK_RELEASE`.

## State and Persistence Behavior

The waiter mutates connection pending-request state by installing the synthetic MID. The ack changes server-side oplock state for an open file. No durable local storage is used.

## Dependencies and Integration Points

The file sits between `smb1cli_req_*`, `smbXcli_req_set_pending()`, and the existing lockingx client code. Callers must be SMB1-aware; SMB2 leases/oplocks are handled elsewhere.

## Risks and Test Signals

Risks include stale fake pending requests, malformed unsolicited packets, incorrect level extraction, and ack failures after a break. Tests should simulate MID `0xffff` completion, short word counts, connection teardown while waiting, valid fnum/level extraction, and server responses to oplock acknowledgements.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clioplock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/cliprint.c -->
# sources/user-network-fs/samba/source3/libsmb/cliprint.c

## Purpose

This file implements legacy RAP/LANMAN print queue operations over `\\PIPE\\LANMAN`: enumerating print jobs and deleting a print job.

## Important APIs, Types, and Functions

The exported APIs are `cli_print_queue()` and `cli_printjob_del()`. `fix_char_ptr()` converts server pointer/converter pairs into safe offsets inside the returned RAP data buffer and substitutes `""` or `"<ERROR>"` for null or invalid pointers. Parsed queue entries are returned through `struct print_job_info` to a caller callback.

## Control Flow

`cli_print_queue()` builds a RAP parameter block for `DosPrintJobEnum` function 76, calls `cli_trans()` against `\\PIPE\\LANMAN`, checks the result code, then walks fixed-size PRJINFO_2 records. For each job it extracts id, priority, user, submitted time, size, and name, resolving string pointers through `fix_char_ptr()`. `cli_printjob_del()` sends function 81, reads the result code, and maps `ERRnosuchprintjob` to `NT_STATUS_INVALID_PARAMETER`.

## State and Persistence Behavior

Enumeration is read-only. Deletion mutates the remote print queue by cancelling a job. The file uses only transient parameter and response buffers.

## Dependencies and Integration Points

It depends on `cli_trans`, RAP format strings, `smb1cli_conn_server_time_zone()` for submitted-time conversion, fixed fstring copies, and `libsmb/clirap.h`. It is part of the old SMB1 print management surface.

## Risks and Test Signals

Risks include malformed converter offsets, truncated job records, unterminated strings, unexpected RAP result codes, and fixed 1000-byte response sizing. Tests should cover valid queues, empty queues, invalid string pointers, result-code mapping, truncated `rparam`/`rdata`, and deletion of missing jobs.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/cliprint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/cliquota.c -->
# sources/user-network-fs/samba/source3/libsmb/cliquota.c

## Purpose

This file implements SMB client quota support for user quotas and filesystem default quota data. It can open the quota pseudo-file, parse and build NT quota records, list user quotas, and get/set per-user or filesystem quota state over SMB1 NT transact/Trans2 or SMB2 helper paths.

## Important APIs, Types, and Functions

Key APIs are `cli_get_quota_handle()`, `parse_user_quota_record()`, `parse_user_quota_list()`, `build_user_quota_buffer()`, `build_fs_quota_buffer()`, `cli_get_user_quota()`, `cli_set_user_quota()`, `cli_list_user_quota()`, `cli_get_fs_quota_info()`, `cli_set_fs_quota_info()`, and `fill_quota_buffer()`. `SMB_NTQUOTA_STRUCT` and `SMB_NTQUOTA_LIST` carry parsed quotas and list ownership.

## Control Flow

SMB1 user quota queries build NDR `nttrans_query_quota_params` and optional `file_get_quota_info`, call `SMBnttrans` with `NT_TRANSACT_GET_USER_QUOTA`, then parse `file_quota_information`. Listing repeatedly calls `cli_list_user_quota_step()` with restart on the first request until non-OK; `NT_STATUS_NO_MORE_ENTRIES` is normalized to success. Set operations serialize quota records with `fill_quota_buffer()` and send `NT_TRANSACT_SET_USER_QUOTA`. Filesystem quota get/set uses Trans2 `SMB_FS_QUOTA_INFORMATION`.

## State and Persistence Behavior

Set operations persist quota thresholds, hard limits, usage records, and quota flags on the remote filesystem. Locally, quota lists are talloc-owned via `mem_ctx`; `free_ntquota_list()` releases the root context stored on list entries.

## Dependencies and Integration Points

The file integrates with fake file name `FAKE_FILE_NAME_QUOTA_WIN32`, SMB2 quota helpers, NDR quota/security generated code, overflow helpers, and `cli_trans`. It is used by administrative client paths that inspect or modify NT quota state.

## Risks and Test Signals

Risks include malformed NDR records, `next_entry_offset` loops or overruns, max-data truncation in `fill_quota_buffer()`, SMB1/SMB2 behavioral differences, and inconsistent ownership of list memory. Tests should cover single and multi-record quotas, offset zero termination, offset beyond buffer, max-data cutoffs, empty list behavior, SMB2 delegation, and fs quota buffers shorter than 48 bytes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/cliquota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clirap.c -->
# sources/user-network-fs/samba/source3/libsmb/clirap.c

## Purpose

This file combines legacy RAP client calls with higher-level path and file information helpers. It enumerates shares and servers, changes OEM passwords, sets basic file times/attributes, queries path/file metadata, parses stream information, and handles SMB1/SMB2 differences for common metadata queries.

## Important APIs, Types, and Functions

Major APIs include `cli_RNetShareEnum()`, `cli_NetServerEnum()`, `cli_oem_change_password()`, `cli_setpathinfo_ext()`, `cli_setfileinfo_ext[_send/_recv]`, `cli_qpathinfo2[_send/_recv]`, `cli_qpathinfo3()`, `cli_qpathinfo_streams[_send/_recv]`, `parse_streams_blob()`, `cli_qfileinfo_basic[_send/_recv]`, `cli_qpathinfo_basic[_send/_recv]`, and `cli_qpathinfo_alt_name()`. Helper `prep_basic_information_buf()` constructs the 40-byte `FILE_BASIC_INFORMATION` payload.

## Control Flow

RAP calls build old LANMAN parameter descriptors and use `cli_trans()` to `\\PIPE\\LANMAN`. `cli_NetServerEnum()` loops `RAP_NetServerEnum2` then `RAP_NetServerEnum3`, using the last returned server name as continuation and skipping repeated first entries. Metadata setters choose SMB2 set-info or SMB1 `cli_setfileinfo`/`cli_setpathinfo`. `cli_qpathinfo2_send()` requests all information; if the file is a reparse point it chains `cli_get_reparse_data_send()` and maps symlink/NFS reparse tags to POSIX modes.

## State and Persistence Behavior

RAP enumeration is read-only; OEM password change mutates account credentials remotely using LanMan hash and ARCFOUR-derived password buffers. Set-path/file-info calls persist timestamp and attribute changes. Query helpers hold transient parsed timestamps, sizes, inode/file ids, stream arrays, and mode classifications.

## Dependencies and Integration Points

The file depends on RAP generated constants, GnuTLS crypto, libcli auth hash helpers, reparse parsing, SMB2 fnum helpers, Trans2 constants, and lower-level qpath/qfile/fsctl helpers declared in `clirap.h` and implemented elsewhere. It is a central compatibility layer for callers that want one API across SMB1 and SMB2.

## Risks and Test Signals

Risks include RAP converter offset mistakes, fixed stack parameter buffers, legacy password crypto failures, parsing stream record lengths, reparse fetch failures after metadata queries, and SMB1 fallback paths for Win95/LANMAN dialects. Tests should cover large share/server enumerations with `ERRmoredata`, malformed comments, too-long usernames, SMB1 and SMB2 qpathinfo on normal files and symlinks, unknown reparse tags, alternate-name conversion, and stream blobs with bad next offsets.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clirap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clirap.h -->
# sources/user-network-fs/samba/source3/libsmb/clirap.h

## Purpose

This header declares the public client RAP and metadata-query APIs implemented primarily by `clirap.c` and related lower-level files. It gives other libsmb components one include for share/server enumeration, password change, path/file info, streams, flush, shadow-copy data, and FSCTL operations.

## Important APIs, Types, and Functions

The declarations cover synchronous RAP calls (`cli_RNetShareEnum`, `cli_NetServerEnum`, `cli_oem_change_password`), extended setters (`cli_setpathinfo_ext`, `cli_setfileinfo_ext_*`), metadata queries (`cli_qpathinfo2`, `cli_qpathinfo3`, `cli_qfileinfo_basic`, `cli_qpathinfo_basic`, `cli_qpathinfo_alt_name`), stream parsing (`parse_streams_blob`), lower-level `cli_qpathinfo`/`cli_qfileinfo`, `cli_flush`, `cli_shadow_copy_data`, and `cli_fsctl`.

## Control Flow

There is no runtime control flow in the header. Its design mirrors Samba's async convention: `_send()` creates a `tevent_req`, `_recv()` extracts results, and a synchronous wrapper exists for many operations.

## State and Persistence Behavior

The header stores no state. It defines ownership expectations through `TALLOC_CTX *mem_ctx` result parameters and through `DATA_BLOB` output for FSCTL.

## Dependencies and Integration Points

It forward-declares `struct cli_state` and expects included Samba headers to provide `NTSTATUS`, `TALLOC_CTX`, `struct tevent_context`, `struct tevent_req`, `SMB_STRUCT_STAT`, `SMB_INO_T`, `fstring`, `DATA_BLOB`, and `struct stream_struct`. `clisymlink.c`, `cliprint.c`, Python bindings, and other libsmb files use these declarations.

## Risks and Test Signals

The main risk is declaration/implementation drift because several declarations are implemented outside `clirap.c` in `clifile.c`. Build tests should compile consumers after signature changes, and ABI/API tests should verify async recv ownership and nullable output parameters.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clirap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clireadwrite.c -->
# sources/user-network-fs/samba/source3/libsmb/clireadwrite.c

## Purpose

This file implements SMB client file read, write, full-write, pull, push, and splice helpers. It handles SMB1 read/write-andx framing, SMB2 helper dispatch, max transfer sizing, credit/request availability, ordered parallel chunk pipelines, and fallback copy loops.

## Important APIs, Types, and Functions

Important APIs are `cli_read_andx_create/send/recv`, `cli_pull_send/recv`, `cli_pull()`, `cli_read_send/recv`, `cli_read()`, `cli_write_andx_create/send/recv`, `cli_write_send/recv`, `cli_writeall_send/recv`, `cli_writeall()`, `cli_push_send/recv`, `cli_push()`, and `cli_splice()`. Internal sizing helpers are `cli_read_max_bufsize()` and `cli_write_max_bufsize()`. Chunk state structs keep offsets, buffers, partial sizes, outstanding subrequests, and ordered linked lists.

## Control Flow

SMB1 read/write create functions construct `SMBreadX`/`SMBwriteX` word vectors, submit chains, and validate returned byte counts and offsets. Single-read/write APIs choose SMB2 or SMB1 based on dialect and respect available credits or SMB1 request slots. `cli_pull_send()` and `cli_push_send()` compute chunk sizes and a window of up to 256 chunks, issue chunks only when request slots are available, and preserve ordered sink delivery for reads. `cli_writeall()` loops partial SMB1 writes until the requested size is written. `cli_splice()` prefers SMB2 server-side copy when source and destination are the same SMB2 connection, falling back to 1 MiB read/write blocks.

## State and Persistence Behavior

Reads are remote-state neutral. Writes, writeall, push, and splice persist data changes on remote files. Local state is request-scoped: buffers may be held under subrequest talloc ownership for full chunks, copied into chunk buffers for partial reads, and freed as chunks complete.

## Dependencies and Integration Points

The file depends on SMB1 low-level request building, SMB2 read/write/splice helpers, connection capability flags, signing/encryption status, `cli_state_available_size()`, tevent, and DLIST macros. It is the core data path used by client file copy, get/put, and higher-level libsmb operations.

## Risks and Test Signals

Risks include trusting server byte counts, large-offset handling without `CAP_LARGE_FILES`, short reads/writes, zero-byte writes, credit starvation, preserving read order under parallel completion, overflow in offset advancement, and fallback cancellation. Tests should cover SMB1/SMB2 reads and writes across max chunk boundaries, signing/encryption reduced sizes, EOF as zero bytes, server over-read/over-write responses, partial writes, push source EOF, splice fallback after unsupported SMB2 copychunk, and active-async rejection in sync wrappers.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clireadwrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clisecdesc.c -->
# sources/user-network-fs/samba/source3/libsmb/clisecdesc.c

## Purpose

This file implements querying and setting security descriptors on open files through SMB1 NT transact security descriptor operations or SMB2 query/set-info security operations.

## Important APIs, Types, and Functions

Public APIs are `cli_query_security_descriptor_send/recv`, `cli_query_security_descriptor()`, `cli_query_secdesc()`, `cli_query_mxac()`, `cli_set_security_descriptor_send/recv`, `cli_set_security_descriptor()`, and `cli_set_secdesc()`. Query and set state structs store SMB1 parameter buffers and marshalled/unmarshalled descriptor blobs.

## Control Flow

Query send selects SMB2 `cli_smb2_query_info_fnum_send()` with `SMB2_0_INFO_SECURITY` or SMB1 `NT_TRANSACT_QUERY_SECURITY_DESC` with fnum and `sec_info` in an 8-byte parameter block. Query recv unmarshals the returned descriptor when the caller asks for it. Set send first marshals the descriptor, then dispatches to SMB2 set-info security or SMB1 `NT_TRANSACT_SET_SECURITY_DESC`. `cli_set_secdesc()` derives `SECINFO_*` bits from descriptor content and present flags.

## State and Persistence Behavior

Queries are read-only. Set operations persist remote owner, group, DACL, or SACL state depending on `sec_info`. Local state is request-scoped and talloc-owned; recv calls mark requests received where appropriate.

## Dependencies and Integration Points

The file integrates with `marshall_sec_desc()`, `unmarshall_sec_desc()`, SMB2 fnum helpers, `cli_trans`, and security descriptor constants. `cli_query_mxac()` is SMB2-only and delegates to `cli_smb2_query_mxac()`.

## Risks and Test Signals

Risks include incorrect `sec_info` selection, large descriptors near the 0x10000 SMB1 output size, malformed descriptor unmarshalling, SACL privilege failures, and dialect differences. Tests should cover owner/group/DACL/SACL combinations, null output descriptor queries, malformed returned blobs, SMB1 and SMB2 set/query round trips, MXAC unsupported on SMB1, and sync wrapper rejection with active async calls.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clisecdesc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clisymlink.c -->
# sources/user-network-fs/samba/source3/libsmb/clisymlink.c

## Purpose

This file implements client symlink and reparse-point handling. It can create Windows symlink reparse points, fetch raw reparse data, and read links either through SMB1 POSIX extensions or through `FSCTL_GET_REPARSE_POINT`.

## Important APIs, Types, and Functions

Important APIs are `cli_create_reparse_point_send/recv`, `cli_symlink_send/recv`, `cli_symlink()`, `cli_get_reparse_data_send/recv`, `cli_get_reparse_data()`, `cli_readlink_send/recv`, and `cli_readlink()`. State structs track fnums, pending FSCTL status, reparse blobs, returned raw data, POSIX targets, and event/CLI pointers.

## Control Flow

Creating a reparse point opens the new file with `FILE_OPEN_REPARSE_POINT`, `FILE_CREATE`, and Windows-like symlink creation access masks, sends `FSCTL_SET_REPARSE_POINT`, then closes. If setting the reparse point fails, it marks the file delete-on-close before closing. `cli_symlink_send()` marshals an `IO_REPARSE_TAG_SYMLINK` buffer and delegates to create-reparse. Fetching reparse data opens the path with read attributes/EA and `FILE_OPEN_REPARSE_POINT`, calls `cli_fsctl_send(FSCTL_GET_REPARSE_POINT)`, then closes before completing. `cli_readlink_send()` prefers negotiated SMB1 POSIX readlink when available; otherwise it fetches and parses symlink reparse data.

## State and Persistence Behavior

Symlink creation persists a new remote file with reparse metadata. Failed create attempts try to clean up with delete-on-close. Raw reparse data and parsed names are talloc-moved to callers. No local durable state exists.

## Dependencies and Integration Points

The file depends on create/close/delete-on-close helpers, `cli_fsctl`, POSIX readlink helpers, reparse marshalling/parsing, security access constants, and SMB2 impersonation values. `clirap.c` uses `cli_get_reparse_data_send()` to classify reparse-point modes.

## Risks and Test Signals

Risks include cleanup failure after partial symlink creation, parsing non-symlink reparse tags as readlink, server-specific access/share requirements, and close-status masking of FSCTL errors. Tests should cover successful symlink creation, FSCTL failure cleanup, readlink via SMB1 POSIX and reparse paths, non-symlink reparse data, malformed reparse buffers, relative/absolute symlink flags, and close failure precedence.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clisymlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clitrans.c -->
# sources/user-network-fs/samba/source3/libsmb/clitrans.c

## Purpose

This file is the common SMB1 transaction wrapper for libsmb client code. It provides async and sync entry points around `smb1cli_trans_send/recv`, including cancellation, output ownership transfer, minimum response validation, and optional DOS error mapping.

## Important APIs, Types, and Functions

The exported APIs are `cli_trans_send()`, `cli_trans_recv()`, and synchronous `cli_trans()`. `cli_trans_state` stores the `cli_state`, lower-level subrequest, receive flags, setup words, parameter bytes, data bytes, and their counts.

## Control Flow

`cli_trans_send()` creates a tevent request and calls `smb1cli_trans_send()` with the connection, timeout, pid, tree connect, session, pipe name/fid/function/flags, and caller-supplied setup/parameter/data buffers. Completion calls `smb1cli_trans_recv()` and stores returned buffers. `cli_trans_recv()` checks minimum setup/param/data sizes, talloc-moves requested buffers to the caller, and maps DOS statuses to NTSTATUS when `cli->map_dos_errors` is enabled. The sync wrapper rejects concurrent async calls and polls a private tevent context.

## State and Persistence Behavior

This wrapper does not define protocol semantics itself; side effects depend on the specific transaction command supplied by callers. It owns returned buffers until recv moves them. Cancellation forwards to the lower subrequest.

## Dependencies and Integration Points

It is used by many SMB1 helpers in this subset: FS info, listing, RAP, quota, print, and security descriptor code. It depends on `smb1cli_trans_*`, tevent NTSTATUS helpers, and `smbXcli_conn_has_async_calls()`.

## Risks and Test Signals

Risks include callers specifying wrong minimum lengths, DOS-to-NT mapping changing expected statuses, missing recv calls leaking buffers until request free, and sync misuse during active async work. Tests should cover minimum-length failures, buffer ownership moves, cancellation propagation, DOS error mapping on/off, transaction errors, and sync wrapper invalid-parameter behavior.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clitrans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/conncache.c -->
# sources/user-network-fs/samba/source3/libsmb/conncache.c

## Purpose

This file implements a negative connection cache on top of Samba `gencache`. It records domain/server pairs that recently failed connection attempts so other processes avoid repeated expensive retries.

## Important APIs, Types, and Functions

Public APIs are `has_negative_conn_cache_entry()`, `add_failed_connection_entry()`, and `flush_negative_conn_cache_for_domain()`. Internal helpers `negative_conn_cache_keystr()`, `negative_conn_cache_valuestr()`, `negative_conn_cache_valuedecode()`, and `delete_matches()` encode keys, statuses, and flush callbacks.

## Control Flow

Keys are formatted as `NEG_CONN_CACHE/<domain>,<server>`, with null server mapped to an empty string. Failed non-OK statuses are encoded as hexadecimal `NT_STATUS_V()` values and stored until `time(NULL) + FAILED_CONNECTION_CACHE_TIMEOUT`. Lookup reads the key, decodes status, and reports an entry only when the decoded status is not OK. Flush builds a wildcard key for a domain and passes `delete_matches()` to `gencache_iterate()`.

## State and Persistence Behavior

State persists in the shared gencache backend, not process-local memory. This gives the negative cache cross-process behavior. Entries expire by timeout or explicit domain flush.

## Dependencies and Integration Points

The file depends on `lib/gencache.h`, NTSTATUS encoding helpers, Samba debug logging, and the global `FAILED_CONNECTION_CACHE_TIMEOUT`. Winbind and connection-management paths can use it before attempting server connections.

## Risks and Test Signals

Risks include domain names with delimiter characters producing ambiguous keys, value parse failures becoming internal-error cache hits, stale negative entries suppressing recovered servers until expiry, and wildcard flush matching more than intended. Tests should cover null domain/server inputs, OK statuses not being cached, decode failures, expiry behavior, exact server and domain-wide flush, and cross-process visibility through gencache.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/conncache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/dsgetdcname.c -->
# sources/user-network-fs/samba/source3/libsmb/dsgetdcname.c

## Purpose

This file implements Samba's `DsGetDcName`-style domain-controller discovery. It resolves DC candidates by DNS SRV and/or NetBIOS, probes them with CLDAP/netlogon pings or NetBIOS datagrams, maps replies to `netr_DsRGetDCNameInfo`, caches successful discoveries, and supports targeted discovery of one named DC.

## Important APIs, Types, and Functions

Public APIs are `dsgetdcname()` and `dsgetonedcname()`. Important internals include `check_allowed_required_flags()`, `discover_dc_dns()`, `discover_dc_netbios()`, `process_dc_dns()`, `process_dc_netbios()`, `make_dc_info_from_cldap_reply()`, `make_domain_controller_info()`, `map_dc_and_domain_names()`, `map_ds_flags_to_nt_version()`, `dsgetdcname_rediscover()`, and `is_closest_site()`. `struct ip_service_name` pairs a Samba socket address with a hostname.

## Control Flow

`dsgetdcname()` validates flag combinations, derives a site from the site cache when none is provided, builds a gencache key from domain/guid/site/flags, and returns a cached NDR-decoded info struct unless forced rediscovery is requested. If discovery is needed, `dsgetdcname_rediscover()` chooses DNS for DNS names, NetBIOS for flat names, or DNS with NetBIOS fallback for unspecified names. DNS discovery builds SRV queries for PDC/GC/KDC/DC/guid cases, keeps up to one IPv4 and one IPv6 address per SRV target, then probes with `netlogon_pings()`. NetBIOS discovery resolves logon or PDC names and uses `nbt_getdc()` with AD-style response flags, falling back to `name_status_find()` for older responses. Successful non-closest-site results can trigger a second discovery against the client site from the first reply.

## State and Persistence Behavior

Successful results are cached in `gencache` for 15 minutes as NDR `netr_DsRGetDCNameInfo` blobs under `DSGETDCNAME/...` keys. The client site is stored through `sitename_store()`. Name cache entries are updated for NetBIOS results. No permanent local files are written by this file directly.

## Dependencies and Integration Points

The file integrates with DNS SRV query builders, async DNS timeout settings, CLDAP/netlogon ping code, NetBIOS name resolution and datagrams, sitename cache, gencache, tsocket address conversion, loadparm options such as `lp_disable_netbios()` and `lp_ldap_timeout()`, and generated NDR netlogon structures.

## Risks and Test Signals

Risks include invalid flag combinations, stale cache entries, DNS records without addresses, IPv6/IPv4 address conversion failures, site fallback loops, NetBIOS disabled behavior, pause responses from netlogon, and mapping flat versus DNS names incorrectly. Tests should cover cache hit/miss/invalid-NDR eviction, `DS_FORCE_REDISCOVERY`, `DS_BACKGROUND_ONLY`, flat-only and DNS-only discovery, PDC/GC/KDC flags, site-specific retry, closest-site replacement, single-DC discovery, and DNS/NetBIOS failure fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/dsgetdcname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/dsgetdcname.h -->
# sources/user-network-fs/samba/source3/libsmb/dsgetdcname.h

## Purpose

This header declares the public domain-controller discovery APIs implemented by `dsgetdcname.c`.

## Important APIs, Types, and Functions

It forward-declares `struct netr_DsRGetDCNameInfo` and `struct messaging_context`, includes talloc and GUID definitions, and declares `dsgetdcname()` plus `dsgetonedcname()`. Both return `NTSTATUS` and allocate the resulting `netr_DsRGetDCNameInfo` under a caller-provided `TALLOC_CTX`.

## Control Flow

The header has no runtime control flow. Callers pass discovery inputs, flags, and a messaging context; the implementation handles cache lookup, DNS/NetBIOS discovery, probing, and result allocation.

## State and Persistence Behavior

The header stores no state. Its API exposes ownership of returned discovery info through talloc and lets the implementation manage gencache/sitename/name-cache state.

## Dependencies and Integration Points

It depends on `replace.h`, `<talloc.h>`, and `librpc/gen_ndr/misc.h` for `struct GUID`. It is included by discovery callers and by `dsgetdcname.c` itself to keep signatures consistent.

## Risks and Test Signals

Risk is mostly API contract drift: callers need a valid messaging context for NetBIOS discovery paths and must provide stable domain/DC strings. Build tests should catch signature drift; runtime tests should verify allocation ownership, null or missing optional GUID/site inputs, and proper status returns for unresolved domains.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/dsgetdcname.h -->
