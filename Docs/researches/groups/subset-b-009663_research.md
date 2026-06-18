# subset-b-009663 research

Grouped research for the libsmb2 SMB2 command, metadata, signing, sealing, and socket transport files in `sources/user-network-fs/libsmb2/lib`. Each section preserves its source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-query-directory.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-query-directory.c

## Purpose
Implements SMB2 QUERY_DIRECTORY request/reply construction and parsing, plus a decoder for `FILE_ID_FULL_DIRECTORY_INFORMATION`. It supports both client-side directory enumeration requests and server-style reply/request handling.

## Important APIs, Types, And Functions
The exported entry points are `smb2_cmd_query_directory_async`, `smb2_cmd_query_directory_reply_async`, `smb2_process_query_directory_fixed`, `smb2_process_query_directory_variable`, `smb2_process_query_directory_request_fixed`, and `smb2_process_query_directory_request_variable`. `smb2_decode_fileidfulldirectoryinformation` decodes a single directory entry into `struct smb2_fileidfulldirectoryinformation`. The code depends on `struct smb2_query_directory_request`, `struct smb2_query_directory_reply`, `struct smb2_fileidbothdirectoryinformation`, iovec helpers, and UTF-16/UTF-8 conversion helpers.

## Control Flow
Client request encoding allocates the fixed request buffer, writes information class, flags, file index, file id, name offset/length, and output buffer length, then appends an optional UTF-16 search pattern. `smb2_cmd_query_directory_async` pads the outgoing chain and sets `credit_charge` for large output buffers when multi-credit is supported. Reply encoding can either pass a raw server buffer through or convert an in-memory list of `smb2_fileidbothdirectoryinformation` records into packed `FILE_ID_FULL_DIRECTORY_INFORMATION` or `FILE_ID_BOTH_DIRECTORY_INFORMATION` entries with `next_entry_offset` chaining. Receive-side parsing validates fixed sizes, checks variable buffer bounds and overlap against the SMB2 header, then stores a pointer into the final receive iovec.

## State And Persistence
State is carried in allocated PDU payloads and in iovec-backed variable buffers. Request names decoded from inbound server requests are copied into the SMB2 context allocator with `smb2_alloc_init`, so the pointer survives beyond the temporary input iovec. The function does not persist directory enumeration state itself; file id, flags, and file index come from caller/server state.

## Dependencies And Integration Points
This file integrates with the generic PDU allocator, 64-bit padding, credit accounting, SMB2 fixed/variable payload dispatch, Unicode conversion, and FILEID directory info structures from `libsmb2-private.h`. It is used by raw directory enumeration APIs and by server/pass-through paths that synthesize query-directory replies.

## Risks
The reply encoder has multiple allocation-error paths where already-added iovectors rely on later PDU cleanup. Unsupported directory information classes result in zero-sized entries rather than a specific protocol error. `smb2_decode_fileidfulldirectoryinformation` validates `name_len` with a redundant-looking overflow guard and should be fuzzed with extreme lengths. Server request parsing checks filename bounds, but some conversions assume valid UTF-16 input.

## Test Signals
Exercise empty and non-empty search names, both supported info classes, passthrough replies, multi-entry chaining, zero-length output replies, malformed name offsets, output buffers that overlap fixed headers, and multi-credit output lengths above 64 KiB.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-query-directory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-query-info.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-query-info.c

## Purpose
Implements SMB2 QUERY_INFO request/reply encoding and fixed/variable response parsing for file, filesystem, security, and passthrough information classes.

## Important APIs, Types, And Functions
Core APIs are `smb2_encode_query_info_request`, `smb2_cmd_query_info_async`, `smb2_cmd_query_info_reply_async`, `smb2_process_query_info_fixed`, `smb2_process_query_info_variable`, `smb2_process_query_info_request_fixed`, and `smb2_process_query_info_request_variable`. It dispatches to file-info codecs such as `smb2_decode_file_all_info`, `smb2_encode_file_basic_info`, filesystem codecs such as `smb2_decode_file_fs_size_info`, and `smb2_decode_security_descriptor`.

## Control Flow
Client request encoding rejects non-empty input buffers, emits the fixed 41-byte request, stores `info_type` and `file_info_class` into the PDU for later unmarshalling, and pads the PDU. Reply encoding writes a fixed reply header, then chooses a typed encoder based on request `info_type` and `file_info_class`. Encoded output can be truncated to the caller's requested output length, in which case the PDU status is set to `SMB2_STATUS_BUFFER_OVERFLOW`. Receive parsing validates the fixed reply, detects offset plus length wraparound, rejects output beyond the SPL or into a chained PDU, and then decodes the variable buffer according to the remembered PDU query class.

## State And Persistence
PDU fields `info_type` and `file_info_class` are critical state because response decoding has no independent class marker. Decoded objects are allocated from the SMB2 context allocator, while passthrough output copies raw bytes into context-owned memory. Request parsing exposes input buffer bytes directly through `req->input`.

## Dependencies And Integration Points
This is the main bridge between raw QUERY_INFO commands and the structured file/filesystem/security descriptor codec files. It relies on PDU header state, `smb2->spl`, chained PDU `next_command`, passthrough mode, and status setting for buffer overflow.

## Risks
Most unsupported classes fail only after a reply arrives unless passthrough is enabled. Request encoding still lacks input-buffer support. Some decode paths allocate a type that may be broader than the decoded struct, and the stream info decoder intentionally over-allocates by payload size. Security info parsing is bypassed in passthrough mode.

## Test Signals
Cover every supported file and filesystem class, security descriptors, buffer overflow truncation, passthrough unknown classes, chained PDU boundary checks, wrapped output offsets, zero-length "No Info" replies, and malformed variable payload lengths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-query-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-read.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-read.c

## Purpose
Builds SMB2 READ requests and replies and parses READ replies/requests for client and server modes.

## Important APIs, Types, And Functions
The public command functions are `smb2_cmd_read_async` and `smb2_cmd_read_reply_async`. Receive handlers are `smb2_process_read_fixed`, `smb2_process_read_variable`, `smb2_process_read_request_fixed`, and `smb2_process_read_request_variable`. `free_read_reply` releases copied reply data when the application supplied a receive buffer.

## Control Flow
Request encoding writes flags, length, offset, file id, minimum count, channel, remaining bytes, and optional channel info. Without multi-credit support, reads above 64 KiB are capped and minimum count is cleared. A one-byte dummy buffer is appended when no channel info exists because SMB2 requires a buffer field. `smb2_cmd_read_async` adds caller-provided reply storage to `pdu->in` so the generic socket reader can place data directly. Reply encoding emits a fixed reply header and appends data when present. Reply parsing validates data offset and returns the variable data length for the socket state machine; variable parsing either copies into the application buffer or points `rep->data` at the receive iovec for zero copy.

## State And Persistence
Read length and output buffer ownership are tied to PDU lifetime. If the application provides `req->buf`, the payload is copied and `free_read_reply` frees it later; otherwise the reply data pointer is valid only as long as the PDU/input vector is retained. Request parsing stores file id, length, offset, and channel data pointers in the PDU payload.

## Dependencies And Integration Points
The code depends on credit accounting, max read size enforcement, iovec receive injection, PDU padding, and the generic fixed/variable parser. It integrates with server callbacks that consume parsed `struct smb2_read_request`.

## Risks
In `smb2_process_read_request_fixed`, `req->read_channel_info_length` is tested before it is loaded from the wire, so channel-info offset handling can be wrong. Data offset validation for replies expects exactly `SMB2_HEADER_SIZE + 16`, which is intentionally strict. Channel info is only encoded outside passthrough by returning an unsupported error. Server request parsing enforces max read size but does not deeply validate channel data semantics.

## Test Signals
Test reads with zero and nonzero lengths, caller-supplied and zero-copy buffers, >64 KiB requests with and without multi-credit, malformed data offsets, read requests above `max_read_size`, passthrough channel info, and channel-info length/offset fuzzing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-session-setup.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-session-setup.c

## Purpose
Encodes and decodes SMB2 SESSION_SETUP requests and replies, carrying authentication security buffers and updating the active session id.

## Important APIs, Types, And Functions
Exports `smb2_cmd_session_setup_async`, `smb2_cmd_session_setup_reply_async`, `smb2_process_session_setup_fixed`, `smb2_process_session_setup_variable`, `smb2_process_session_setup_request_fixed`, and `smb2_process_session_setup_request_variable`. It works with `struct smb2_session_setup_request` and `struct smb2_session_setup_reply`.

## Control Flow
Request encoding emits flags, security mode, capabilities, channel, fixed security buffer offset, length, previous session id, and then appends the caller-provided security blob. Reply encoding writes session flags and appends a padded security response buffer. Client reply parsing validates fixed structure, checks security-buffer end against the SPL, updates `smb2->session_id` from the SMB2 header, and returns the variable buffer length. Server request parsing reads request fields and returns the security buffer length for subsequent variable parsing.

## State And Persistence
The most important state transition is storing `smb2->session_id = smb2->hdr.session_id` on a parsed reply. Security buffers point into iovec memory, not independently copied, so their lifetime follows the PDU/input vector. Previous session id is carried for reconnect/session binding semantics.

## Dependencies And Integration Points
This file sits between authentication code and the generic PDU/socket layer. It influences signing behavior because signing starts only after a valid session and session key exist. It also participates in server-mode request parsing for authentication negotiation.

## Risks
The server request parser has the security-buffer offset read commented out and returns only the length, implicitly assuming the variable bytes immediately follow the fixed payload. It also reads `previous_session_id` at offset 18, while encoding writes it at offset 16, which is suspicious and needs protocol test coverage. Security buffer allocation with zero length is not specially handled in request encoding.

## Test Signals
Cover empty and non-empty security buffers, multi-leg auth, previous-session reconnect, malformed offsets and lengths, session id propagation, server-mode request parsing, and signing behavior immediately before and after session setup completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-session-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-set-info.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-set-info.c

## Purpose
Builds SMB2 SET_INFO requests/replies and parses inbound SET_INFO requests, supporting selected file information classes and passthrough raw buffers.

## Important APIs, Types, And Functions
Primary entry points are `smb2_cmd_set_info_async`, `smb2_cmd_set_info_reply_async`, `smb2_process_set_info_fixed`, `smb2_process_set_info_request_fixed`, and `smb2_process_set_info_request_variable`. It uses `smb2_encode_file_basic_info`, `struct smb2_file_end_of_file_info`, `struct smb2_file_disposition_info`, and `struct smb2_file_rename_info`.

## Control Flow
Request encoding writes the fixed SET_INFO header, file id, and buffer offset. In passthrough mode it appends caller-supplied raw data. Structured mode supports `SMB2_FILE_BASIC_INFORMATION`, EOF size changes, rename, and disposition/delete-pending. Rename names are converted from UTF-8 to UTF-16 and forward slashes are converted to backslashes. Reply encoding emits an empty fixed success structure. Request parsing stores fixed fields and returns `buffer_length`; variable parsing currently only exposes raw input in passthrough mode.

## State And Persistence
The request payload owns no persistent server-side decoded structures in non-passthrough mode; server parsing rejects interpretation unless passthrough is set. Rename and metadata values are serialized into PDU iovectors. File id and additional information are carried in `struct smb2_set_info_request`.

## Dependencies And Integration Points
This file depends on file-info encoders, Unicode conversion, PDU padding, and pass-through server logic. Higher-level filesystem APIs call it for chmod/timestamps/truncate/rename/delete style operations.

## Risks
Passthrough mode sets fields on the current iovec after appending the raw buffer, so header field writes can target the appended buffer rather than the fixed header. Request parsing returns `buffer_length` without validating `buffer_offset` or header overlap. Non-passthrough server interpretation is intentionally absent. The typo in an error string is harmless but signals limited coverage of unsupported paths.

## Test Signals
Test basic info, EOF, rename with slash conversion, disposition, passthrough raw buffers, unsupported info classes, malformed buffer offsets, zero-length buffers, and server request parsing in both passthrough and structured modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-set-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-tree-connect.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-tree-connect.c

## Purpose
Implements SMB2 TREE_CONNECT request/reply encoding and parsing, including local tree-id registration and encryption enablement from share flags.

## Important APIs, Types, And Functions
Exports `smb2_cmd_tree_connect_async`, `smb2_cmd_tree_connect_reply_async`, `smb2_process_tree_connect_fixed`, `smb2_process_tree_connect_request_fixed`, and `smb2_process_tree_connect_request_variable`. It consumes `struct smb2_tree_connect_request` and `struct smb2_tree_connect_reply`.

## Control Flow
Request encoding writes flags, path offset, and path length, then appends the caller-provided UTF-16 path bytes. Reply encoding writes share type, share flags, capabilities, and maximal access. Server reply creation can invent a tree id from a static counter when the caller passes zero, connects that tree id in the context, and stamps it into the reply header. Client reply parsing registers the tree id from the SMB2 header, reads share properties, and enables sealing when the share has `SMB2_SHAREFLAG_ENCRYPT_DATA` and sealing was not already set.

## State And Persistence
Tree connection state is persisted in the SMB2 context via `smb2_connect_tree_id`. A static `s_tree_id` is used for server-side synthetic tree ids, so it is process-global rather than context-local. The parsed request path points into the receive iovec.

## Dependencies And Integration Points
This file integrates session-authenticated transport with share-scoped operations. It feeds tree id state used by subsequent create/read/write/query commands and ties share encryption policy into SMB3 sealing.

## Risks
Request parsing returns `path_length` but does not validate `path_offset` for overlap or bounds in this file. The static tree-id counter is not synchronized and can collide across contexts or long-running tests. Path bytes are not converted here; callers must understand UTF-16 path data.

## Test Signals
Cover explicit and auto-generated tree ids, share encryption flag behavior, malformed path offsets/lengths, multiple contexts in server mode, disconnect/reconnect cycles, and paths containing UTF-16 UNC names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-tree-connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-tree-disconnect.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-tree-disconnect.c

## Purpose
Implements the small SMB2 TREE_DISCONNECT request/reply and removes tree-id state when a disconnect reply is processed.

## Important APIs, Types, And Functions
Exports `smb2_cmd_tree_disconnect_async`, `smb2_cmd_tree_disconnect_reply_async`, `smb2_process_tree_disconnect_fixed`, and `smb2_process_tree_disconnect_request_fixed`.

## Control Flow
Request and reply encoding each allocate a four-byte fixed payload and write the structure size. The async wrappers allocate a `SMB2_TREE_DISCONNECT` PDU and pad it. Client reply processing calls `smb2_disconnect_tree_id` with the tree id from the SMB2 header. Server request parsing is a no-op because the command has no variable body.

## State And Persistence
The only state mutation is removal of the current header tree id from the SMB2 context. No payload data is retained.

## Dependencies And Integration Points
This command closes the lifecycle started by TREE_CONNECT and affects all later tree-scoped operations. It uses generic PDU allocation, iovectors, padding, and tree-id registry helpers.

## Risks
The fixed request parser does not check the incoming structure size in this file, so malformed disconnect requests rely on generic sizing elsewhere. Disconnecting based solely on header tree id is correct for SMB2 but needs tests around stale or unknown ids.

## Test Signals
Test normal connect/disconnect, disconnect of missing tree ids, malformed fixed payloads, server-mode disconnect requests, and ensuring later tree-scoped commands fail or select a different tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-tree-disconnect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-write.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-write.c

## Purpose
Builds SMB2 WRITE requests/replies and parses WRITE replies/requests for client and server paths.

## Important APIs, Types, And Functions
Key functions are `smb2_cmd_write_async`, `smb2_cmd_write_reply_async`, `smb2_process_write_fixed`, `smb2_process_write_request_fixed`, and `smb2_process_write_request_variable`. It uses `struct smb2_write_request` and `struct smb2_write_reply`.

## Control Flow
Request encoding emits data offset, length, offset, file id, channel, remaining bytes, optional write channel info, and flags. It caps writes above 64 KiB when multi-credit is unavailable. `smb2_cmd_write_async` pads the header vectors, then appends the caller's data buffer with optional ownership transfer, and sets multi-credit charge for large writes. Reply encoding writes count and remaining bytes. Request parsing extracts fixed fields, validates channel-info overlap when present, and returns enough variable length to include channel info padding plus data. Variable parsing exposes channel info and write data as zero-copy pointers into the receive iovec.

## State And Persistence
Write data can be owned by the PDU when `pass_buf_ownership` is true. Parsed inbound request buffers point into the PDU input vector and should not outlive PDU cleanup. Credit consumption is persisted through the PDU header.

## Dependencies And Integration Points
This file depends on iovec-based zero-copy sends/receives, credit charging, PDU padding, and server callbacks for writes. It pairs with `socket.c` logic that writes compound vectors and reads variable request data.

## Risks
The passthrough channel-info offset assignment uses `SMB2_READ_REQUEST_SIZE` instead of the write request size, which is likely a bug. Request parsing does not validate data offset directly; it derives the data pointer after padded channel info. Unsupported structured channel info returns an error unless passthrough is enabled.

## Test Signals
Exercise small and large writes with and without multi-credit, ownership and non-ownership buffers, malformed data/channel offsets, zero-length writes, passthrough channel info, and server-side zero-copy lifetime.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-data-file-info.c -->
# sources/user-network-fs/libsmb2/lib/smb2-data-file-info.c

## Purpose
Provides structured encoders and decoders for SMB2 file information classes used by QUERY_INFO and SET_INFO.

## Important APIs, Types, And Functions
Functions include `smb2_decode_file_basic_info`, `smb2_encode_file_basic_info`, `smb2_decode_file_standard_info`, `smb2_encode_file_standard_info`, `smb2_decode_file_stream_info`, `smb2_encode_file_stream_info`, `smb2_decode_file_position_info`, `smb2_encode_file_position_info`, `smb2_decode_file_all_info`, `smb2_encode_file_all_info`, `smb2_decode_file_network_open_info`, `smb2_encode_file_network_open_info`, `smb2_decode_file_normalized_name_info`, and `smb2_encode_file_normalized_name_info`.

## Control Flow
The codecs translate between little-endian wire fields in `struct smb2_iovec` and libsmb2 C structs. Timestamp fields are converted between Windows filetime and `smb2_timeval`; `smb2_tv_timeval_to_win` preserves SMB sentinel values for "do not change" and "maximum". Variable names and stream names are converted between UTF-16 and UTF-8 and allocated under a caller-provided memory context. Stream info walks a next-entry chain and emits padded chained records.

## State And Persistence
Decoded strings are allocated with `smb2_alloc_data` under the provided memory context, usually a larger decoded object. Encode paths may mutate length fields such as `stream_name_length` and `file_name_length` to byte counts. No global state is used.

## Dependencies And Integration Points
These helpers are called directly by QUERY_INFO reply processing and SET_INFO request encoding. They rely on endian-safe `smb2_get_*`/`smb2_set_*`, time conversion, padding macros, and UTF helpers.

## Risks
Some encoders copy variable names without independently proving the destination iovec has room beyond the fixed header. `smb2_encode_file_stream_info` multiplies `stream_name_length` in place, which can surprise callers that reuse the struct. There are stray `#include <stdio.h>` lines in the middle of the file. Truncated decode behavior may hide malformed server replies by clipping names.

## Test Signals
Use round-trip tests for all supported classes, sentinel timestamp values, long and truncated names, multiple stream entries, UTF-16 conversion failures, short iovecs, and caller struct reuse after encoding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-data-file-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-data-filesystem-info.c -->
# sources/user-network-fs/libsmb2/lib/smb2-data-filesystem-info.c

## Purpose
Encodes and decodes SMB2 filesystem information classes for volume, size, device, attribute, control, full-size, object-id, and sector-size data.

## Important APIs, Types, And Functions
Exports paired codecs such as `smb2_decode_file_fs_volume_info`/`smb2_encode_file_fs_volume_info`, `smb2_decode_file_fs_size_info`/`smb2_encode_file_fs_size_info`, `smb2_decode_file_fs_device_info`/`smb2_encode_file_fs_device_info`, `smb2_decode_file_fs_attribute_info`/`smb2_encode_file_fs_attribute_info`, `smb2_decode_file_fs_control_info`/`smb2_encode_file_fs_control_info`, `smb2_decode_file_fs_full_size_info`/`smb2_encode_file_fs_full_size_info`, `smb2_decode_file_fs_object_id_info`/`smb2_encode_file_fs_object_id_info`, and `smb2_decode_file_fs_sector_size_info`/`smb2_encode_file_fs_sector_size_info`.

## Control Flow
Each decoder checks a fixed minimum length for fixed-size classes, reads little-endian fields from the iovec, and allocates decoded UTF-8 strings for variable labels or filesystem names. Encoders write fields back into an iovec and convert labels/names to UTF-16. Return values report encoded byte counts for reply construction.

## State And Persistence
Decoded variable strings are attached to the caller's memory context. The code has no global or persistent state. Encoded structs are read-only except for temporary local UTF-16 conversions.

## Dependencies And Integration Points
Used by `smb2-cmd-query-info.c` for filesystem QUERY_INFO replies. Depends on SMB2 iovec endian helpers, Windows time conversion, UTF conversion, GUID sizes, and allocation helpers.

## Risks
Volume and attribute decoders assume UTF conversion succeeds before calling `strlen`; null conversion results could crash. Variable-length decoders do not consistently verify that the declared UTF-16 name length fits inside `vec->len`. Encoders assume non-null filesystem labels/names and enough iovec space for variable data.

## Test Signals
Test every class with minimum and truncated buffers, null/empty labels, long filesystem names, UTF conversion failures, object-id exact 64-byte payloads, and sector-size flags/alignment fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-data-filesystem-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-data-reparse-point.c -->
# sources/user-network-fs/libsmb2/lib/smb2-data-reparse-point.c

## Purpose
Decodes SMB2 reparse data buffers, currently handling symbolic-link reparse payloads.

## Important APIs, Types, And Functions
The file exports `smb2_decode_reparse_data_buffer`, operating on `struct smb2_reparse_data_buffer` and `struct smb2_iovec`.

## Control Flow
The decoder checks for the reparse header, reads `reparse_tag` and `reparse_data_length`, verifies the declared data fits, and switches on the tag. For `SMB2_REPARSE_TAG_SYMLINK`, it reads symlink flags, substitute-name offset/length, and print-name offset/length. Each UTF-16 name is converted to UTF-8 and allocated under the reparse buffer object.

## State And Persistence
Decoded symlink names are stored inside the caller-provided reparse structure using context allocation. No encode path or global state exists.

## Dependencies And Integration Points
This decoder is consumed by higher-level FSCTL or QUERY_INFO paths that retrieve reparse data. It depends on iovec getters, UTF conversion, and context allocation.

## Risks
The function does not check UTF conversion return before `strlen(tmp)`, so malformed UTF-16 can crash. Only symlinks are interpreted; other reparse tags are accepted with just the tag and length populated. Offset arithmetic uses 16-bit fields and should be fuzzed for wrap/edge cases.

## Test Signals
Cover valid symlink substitute and print names, relative/absolute flags, unknown tags, short headers, declared lengths beyond the buffer, malformed UTF-16, and offset-plus-length boundary cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-data-reparse-point.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-data-security-descriptor.c -->
# sources/user-network-fs/libsmb2/lib/smb2-data-security-descriptor.c

## Purpose
Decodes self-relative SMB2/Windows security descriptors into SID, ACL, and ACE structures.

## Important APIs, Types, And Functions
The public API is `smb2_decode_security_descriptor`. Internal helpers are `decode_sid`, `decode_ace`, and `decode_acl`. It uses `struct smb2_security_descriptor`, `struct smb2_sid`, `struct smb2_acl`, and `struct smb2_ace`, with list linkage through `SMB2_LIST_ADD_END`.

## Control Flow
Security descriptor decoding validates the descriptor header and revision, reads owner/group/SACL/DACL offsets, and decodes present owner, group, and DACL components. SID decoding validates revision and subauthority count before allocating a variable-sized SID. ACL decoding validates revision and ACL size, then iterates ACE count and decodes each ACE. ACE decoding handles common allow/deny/audit/mandatory/object/callback ACEs and stores raw data for unknown types.

## State And Persistence
All decoded substructures are allocated under the provided memory context, commonly the security descriptor object. The DACL ACE list is linked into the decoded ACL. The parser advances local iovec copies and does not mutate the source buffer.

## Dependencies And Integration Points
Called from QUERY_INFO security response decoding. Depends on `slist.h`, SMB2 security constants, iovec helpers, context allocation, and error reporting through `smb2_set_error`.

## Risks
SACL offsets are read but not decoded. Some ACE paths call `decode_sid` but do not immediately fail if it returns null, leaving possible partially initialized ACEs. Unknown ACE raw length is the remaining local vector after the header, not necessarily bounded to `ace_size - 4`. Offset checks use minimal SID/ACL header sizes and ignore descriptors where an offset points exactly to the last valid byte.

## Test Signals
Test owner/group/DACL decoding, ACL revisions, zero ACEs, all supported ACE families, unknown ACE raw preservation, malformed SID revisions/counts, ACE size underflow/overflow, SACL-only descriptors, and truncated self-relative offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-data-security-descriptor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-share-enum.c -->
# sources/user-network-fs/libsmb2/lib/smb2-share-enum.c

## Purpose
Implements asynchronous share enumeration through DCERPC SRVSVC `NetrShareEnum` over an existing SMB2 connection.

## Important APIs, Types, And Functions
The exported API is `smb2_share_enum_async`. Internal callbacks are `share_enum_bind_cb`, `srvsvc_ioctl_cb`, and `nse_free`. The private state container `struct smb2nse` stores the user callback and `srvsvc_NetrShareEnum_req`.

## Control Flow
`smb2_share_enum_async` creates a DCERPC context from the SMB2 context, allocates request state, builds a `\\server` name from `smb2->server`, sets the requested info level and maximum length, then starts an async bind to the `srvsvc` pipe/interface. On bind success, `share_enum_bind_cb` issues the `SRVSVC_NETRSHAREENUM` call. `srvsvc_ioctl_cb` forwards either transport status or returned SRVSVC status to the original callback and destroys the DCERPC context.

## State And Persistence
The outstanding operation state is `struct smb2nse`, freed on every callback completion/error path. The server name string is owned by the request state. DCERPC context lifetime is scoped to this one enumeration.

## Dependencies And Integration Points
Depends on libsmb2 DCERPC helpers, generated SRVSVC coders, raw SMB2 context access, and callback conventions that use `smb2_command_cb`.

## Risks
The server string allocation uses `strlen(smb2->server) + 3`, sufficient for two backslashes plus NUL, but assumes `smb2->server` is set. Callback status mixes SMB transport status and SRVSVC application status, so callers must interpret both. There is no pagination loop for `ResumeHandle`; it requests `0xffffffff` bytes and returns the first server response.

## Test Signals
Mock bind failure, DCERPC call failure, SRVSVC non-success status, null/empty server names, multiple info levels, large share lists requiring resume handles, and callback/data lifetime after completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-share-enum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-signing.c -->
# sources/user-network-fs/libsmb2/lib/smb2-signing.c

## Purpose
Calculates and adds SMB2/SMB3 PDU signatures using HMAC-SHA256 for SMB2.1 and AES-CMAC-128 for newer dialects.

## Important APIs, Types, And Functions
Public functions are `smb2_calc_signature`, `smb2_pdu_add_signature`, and stub `smb2_pdu_check_signature`. Internal AES-CMAC helpers are `aes_cmac_shift_left`, `aes_cmac_xor`, `aes_cmac_sub_keys`, and `smb3_aes_cmac_128`.

## Control Flow
`smb2_calc_signature` clears the SMB2 header signature field, then either concatenates all iovecs and runs AES-CMAC for SMB3 dialects or streams iovecs through HMAC-SHA256 for SMB2.1. `smb2_pdu_add_signature` skips most session-setup PDUs until the first successful server-to-client setup response, validates vector layout and session key presence, sets `SMB2_FLAGS_SIGNED`, recalculates the signature, and copies it into both the PDU header and serialized header iovec.

## State And Persistence
Uses `smb2->signing_key`, `session_id`, `session_key_size`, and dialect state. It mutates outgoing PDU flags and signature bytes. It temporarily allocates a contiguous message buffer for AES-CMAC.

## Dependencies And Integration Points
Called by the PDU send path before transmission and by socket receive verification logic through `smb2_calc_signature`. Depends on embedded AES and SHA/HMAC helpers and SMB2 header/iovec layout.

## Risks
`smb2_pdu_check_signature` is a stub; inbound checking is implemented elsewhere in `socket.c`, so direct users of the declared check function get no validation. AES-CMAC concatenates all iovecs into one allocation, which can be expensive for large compounded writes. The source defines `EBC` instead of likely `ECB`, though included AES code may not depend on it.

## Test Signals
Use known AES-CMAC and HMAC-SHA256 vectors, signed session setup boundary cases, unsigned session id zero PDUs, missing session keys, multi-iovec compound messages, large write signing memory behavior, and negative tests for altered signatures on receive.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-signing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-signing.h -->
# sources/user-network-fs/libsmb2/lib/smb2-signing.h

## Purpose
Declares the SMB2 signing API used by the rest of libsmb2.

## Important APIs, Types, And Functions
The header exposes `smb2_pdu_add_signature(struct smb2_context *, struct smb2_pdu *)` and `smb2_pdu_check_signature(struct smb2_context *, struct smb2_pdu *)`.

## Control Flow
There is no executable control flow. The include guard `_SMB2_SIGNING_H_` protects declarations, and C++ linkage wrappers expose a C ABI.

## State And Persistence
No state is stored in the header. The declared functions operate on SMB2 context and PDU state supplied by callers.

## Dependencies And Integration Points
Includes `slist.h`, `smb2.h`, `libsmb2.h`, `libsmb2-raw.h`, and `libsmb2-private.h`, making it an internal signing interface rather than a small standalone public header.

## Risks
The declared check function currently maps to a stub implementation in `smb2-signing.c`; callers expecting verification through this API would be misled. The broad private includes increase compile coupling.

## Test Signals
Compile C and C++ translation units including this header, ensure prototypes stay synchronized with implementation, and add a test that fails if `smb2_pdu_check_signature` remains a no-op in paths that rely on it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-signing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb3-seal.c -->
# sources/user-network-fs/libsmb2/lib/smb3-seal.c

## Purpose
Implements SMB3 message encryption and decryption ("sealing") using AES-128-CCM transform headers.

## Important APIs, Types, And Functions
Exports `smb3_encrypt_pdu` and `smb3_decrypt_pdu`. It uses the SMB3 transform protocol marker `{0xFD,'S','M','B'}`, `aes128ccm_encrypt`, `aes128ccm_decrypt`, and encryption keys from `struct smb2_context`.

## Control Flow
Encryption returns immediately unless context sealing and PDU sealing are both enabled. It computes the total compound payload length, allocates a transform buffer, writes the 52-byte transform header, fills part of the nonce with `random()`, writes original message size, algorithm id, session id, copies all compound PDU outgoing iovecs after the transform header, and encrypts/signs the payload in place with AES-CCM. Decryption verifies AES-CCM over the transform header and payload, stores decrypted bytes in `smb2->enc`, resets the normal receive state to parse a fresh SMB2 header from that buffer, calls `smb2_read_from_buf`, and frees the temporary decrypted buffer.

## State And Persistence
Encryption stores `pdu->crypt`, `pdu->crypt_len`, and may clear `pdu->seal` on allocation failure. Decryption temporarily uses `smb2->enc`, `enc_len`, and `enc_pos`, resets `spl` and `recv_state`, and transfers ownership of the decrypted payload away from the input iovec.

## Dependencies And Integration Points
Integrated directly with `socket.c`: encrypted outgoing PDUs are sent as a single transform payload, and encrypted incoming frames are detected by transform header magic and then re-fed through normal parsing. It depends on negotiated encryption keys and share/session sealing decisions.

## Risks
Nonce generation uses `random()` and only fills bytes 20 through 30, so nonce quality and uniqueness should be reviewed. No explicit transform header validation beyond successful CCM authentication is visible here. Only AES-128-CCM is used. Decryption frees `smb2->enc` after parsing, so callbacks must not retain pointers into decrypted input beyond PDU lifetime.

## Test Signals
Round-trip encrypted single and compound PDUs, wrong key/tag failure, seal disabled/enabled combinations, nonce uniqueness under repeated sends, malformed transform headers, decrypted chained messages, and memory ownership after callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb3-seal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb3-seal.h -->
# sources/user-network-fs/libsmb2/lib/smb3-seal.h

## Purpose
Declares the internal SMB3 sealing encrypt/decrypt functions.

## Important APIs, Types, And Functions
The header exports `smb3_encrypt_pdu(struct smb2_context *, struct smb2_pdu *)` and `smb3_decrypt_pdu(struct smb2_context *)`.

## Control Flow
There is no executable logic. Include guards and C++ extern wrappers provide safe inclusion from C and C++ code.

## State And Persistence
The header stores no state. The declared functions mutate SMB2 context and PDU encryption buffers in their implementation.

## Dependencies And Integration Points
Unlike `smb2-signing.h`, this header forward-uses `struct smb2_context` and `struct smb2_pdu` without including their definitions directly, relying on includers such as `socket.c` or `smb3-seal.c` to include SMB2 headers first.

## Risks
Because it lacks explicit forward declarations, strict compilers may warn if included before definitions in some translation units. Prototype drift would break socket integration.

## Test Signals
Compile include-order tests, C++ linkage tests, and integration tests ensuring socket encryption paths call these prototypes with the expected context/PDU types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb3-seal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/socket.c -->
# sources/user-network-fs/libsmb2/lib/socket.c

## Purpose
Implements libsmb2 nonblocking socket transport, event selection, credit-gated writes, receive-state parsing, SMB3 transform handling, async connect with Happy Eyeballs behavior, server listen/accept helpers, and event callback updates.

## Important APIs, Types, And Functions
Public APIs include `smb2_which_events`, `smb2_get_fd`, `smb2_get_fds`, `smb2_write_to_socket`, `smb2_read_from_buf`, `smb2_service_fd`, `smb2_service`, `smb2_connect_async`, `smb2_bind_and_listen`, `smb2_accept_connection_async`, and `smb2_change_events`. Important internal helpers include `smb2_read_data`, `smb2_read_from_socket`, `smb2_readv_from_socket`, `smb2_readv_from_buf`, `connect_async_ai`, `smb2_connect_async_next_addr`, `interleave_addrinfo`, and fd cleanup helpers.

## Control Flow
Writes are gated by available credits, flatten compound PDU iovecs or encrypted transform buffers behind a 4-byte SPL prefix, handle partial `writev`, then move sent client PDUs to the waitqueue or free server replies. Reads use a state machine: SPL, SMB2 header, fixed payload, variable payload, padding, transform payload, or unknown reply. Header parsing updates credits, validates request/reply direction, matches client replies by message id, creates notification PDUs for oplock breaks, and invokes command-specific fixed/variable parsers. Encrypted transform frames are detected by magic, read as a transform header plus payload, decrypted by `smb3_decrypt_pdu`, and parsed from memory. Connection setup resolves host/port, interleaves address families, opens nonblocking sockets, races connection attempts with a 100 ms timeout, and promotes the first successful fd.

## State And Persistence
Major state lives in `struct smb2_context`: `fd`, connecting fd array, addrinfo cursor, outqueue, waitqueue, credits, receive iovectors, `recv_state`, SPL, current PDU, encrypted buffer cursor, callbacks, and event mask. Sent client PDUs persist in the waitqueue until matched replies arrive. Server-mode requests are queued to correlate later replies.

## Dependencies And Integration Points
This file is the transport core for all command files. It integrates signing verification through `smb2_calc_signature`, sealing through `smb3_decrypt_pdu`, PDU allocation/lookup/free, command payload dispatch, timeout handling, fd-change/event callbacks, POSIX/Windows socket APIs, and address resolution.

## Risks
The receive state machine is complex and sensitive to length arithmetic, chained PDU padding, and encrypted-vs-plain SPL accounting. Unknown replies are skipped only below a max-size guard. Signature checking mutates the received signature field while recalculating and then compares restored bytes, so regression tests are important. Happy Eyeballs fd arrays assume capacity from initial addrinfo count and require cleanup on all paths. Some error strings include stale `smb2_get_error` text rather than `strerror`.

## Test Signals
Use integration tests for partial reads/writes, credit exhaustion/refill, compound request/reply order, pending replies, unknown replies, oplock notifications, signed tamper detection, encrypted transform PDUs, IPv4/IPv6 racing, connect failure fallback, server accept, timeout processing, and event mask transitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/socket.c -->
