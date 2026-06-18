# subset-b-009876 Research

Grouped research for the listed Samba SMB server files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_trans2.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_trans2.c

## Purpose
This file implements most of Samba smbd's SMB1 trans2/NT transact file information behavior that is also reused by SMB2 query/set info paths. It is a translation layer between SMB wire information levels and Samba's internal file, directory, filesystem, EA, quota, stream, POSIX, rename, hardlink, allocation, timestamp, and delete-on-close operations.

The code is broad but organized around three jobs: marshal query replies, parse set-info requests, and enforce Windows/SMB semantics over Unix/VFS primitives. It handles legacy SMB1 levels, pass-through SMB2 levels, CIFS UNIX extensions, and SMB3 POSIX extension data.

## Important APIs, Types, And Functions
Key helper APIs include `refuse_symlink_fsp()`, `check_any_access_fsp()`, and `smb_roundup()`. `refuse_symlink_fsp()` blocks EA access on symlinks and pathrefs without a pathref fd. `check_any_access_fsp()` validates that at least one requested access bit was granted, with special snapshot/TWRP handling that maps non-read access to `NT_STATUS_MEDIA_WRITE_PROTECTED`. `smb_roundup()` applies the configured allocation roundup size only for Windows-like clients, not Samba or Linux CIFS clients.

The EA subsystem is centered on `get_ea_value_fsp()`, `get_ea_names_from_fsp()`, `get_ea_list_from_fsp()`, `fill_ea_buffer()`, `fill_ea_chained_buffer()`, `estimate_ea_size()`, `set_ea()`, and `read_ea_list()`. It maps Windows EA names into POSIX `user.*` xattrs, filters Samba-private xattrs such as DOS attributes, NT ACLs, reparse attributes, AppleDouble metadata, and DOS stream xattrs, and rejects invalid Windows EA names unless POSIX path semantics are in use.

Directory enumeration uses `smbd_dirptr_lanman2_entry()` and the internal `smbd_marshall_dir_entry()`. These support many info levels: old LanMan formats, SMB find directory/full/both/name/id formats, CIFS UNIX formats, and `FSCC_FILE_POSIX_INFORMATION`. The marshaller computes file size, allocation size, timestamps, mode bits, file ids, EA sizes or reparse tags, 8.3 short names, AAPL readdir attributes, padding, next-entry offsets, and resume-key slots.

Filesystem information is handled by `smbd_do_qfsinfo()` and `smbd_do_setfsinfo()`. Query levels include allocation, volume, attributes, label, size, full size, device, quota, object id, sector size, CIFS UNIX capability, POSIX filesystem info, and POSIX whoami. Setfsinfo only supports quota updates through `smb_set_fsquota()`.

File/path query information is handled by `smbd_do_qfilepathinfo()`. It emits standard/basic/EA/name/all/internal/access/position/mode/alignment/stream/compression/network-open/attribute-tag/POSIX information. Helper functions include `store_file_unix_basic()`, `store_file_unix_basic_info2()`, `map_info2_flags_from_sbuf()`, `map_info2_flags_to_sbuf()`, and `marshall_stream_info()`.

File/path mutation is handled by `smbd_do_setfilepathinfo()`. Important callees are `smb_set_info_standard()`, `smb_set_file_basic_info()`, `smb_set_file_time()`, `smb_set_file_dosmode()`, `smb_set_file_size()`, `smb_set_file_allocation_info()`, `smb_set_file_end_of_file_info()`, `smb_info_set_ea()`, `smb_set_file_full_ea_info()`, `smb_check_file_disposition_info()`, `smb_set_file_disposition_info()`, `smb_file_position_information()`, `smb_file_mode_information()`, `smb2_parse_file_rename_information()`, `smb_file_rename_information()`, `smb2_file_rename_information()`, `smb_file_link_information()`, and `hardlink_internals()`.

## Control Flow
Query control flow is mostly dispatch-by-information-level. Callers allocate or pass a response buffer; `smbd_do_qfsinfo()` and `smbd_do_qfilepathinfo()` grow the buffer with an additional safety margin, zero it, choose a case by info level, write little-endian fields with Samba macros, return `fixed_portion` for SMB2 framing where needed, and report the final data length.

Directory enumeration flows through a directory pointer. `smbd_dirptr_lanman2_entry()` derives the wildcard mask, applies long-name/8.3 matching in `smbd_dirptr_lanman2_match_fn()`, gets one matching entry through `smbd_dirptr_get_entry()`, marshals it, and pushes it back to the overflow queue if the entry does not fit. The marshaller calculates alignment before the record and record padding after the variable name payload, then writes the previous record's next offset through `last_entry_off`.

EA query flow lists xattrs with `SMB_VFS_FLISTXATTR()`, filters names, reads values with `SMB_VFS_FGETXATTR()`, drops zero-length or oversized values, converts names to DOS/ASCII form, and serializes either old SMB EA buffers or chained `FILE_FULL_EA_INFORMATION` buffers. EA set flow parses incoming EA records, validates access and names before applying any change, canonicalizes case against existing EAs, and uses `SMB_VFS_FSETXATTR()` or `SMB_VFS_FREMOVEXATTR()`.

Set-info control flow is similarly case-based. It validates minimal payload sizes, checks access rights close to each mutating operation, and then delegates to Samba VFS or common smbd helpers. Rename and link flows parse SMB1 or SMB2 wire name formats, convert paths relative to cwd or parent pathrefs, reject unsupported stream cases, then call `rename_internals_fsp()`, `rename_internals()`, or `SMB_VFS_LINKAT()`.

## State And Persistence Behavior
Most state is stored in existing smbd structures rather than in this file. It reads and updates `files_struct`, `smb_filename`, `connection_struct`, `smb_request`, file handle position, share-mode/delete-on-close state, DOS attributes, xattrs, timestamps, allocation size, file length, quotas, and notify state.

Persistent filesystem state changes include xattrs, quota settings, DOS mode storage, file timestamps, allocation and EOF length, hardlinks, renames, delete-on-close flags that apply across opens on the same dev/inode, and VFS-backed stream information. The file also emits change notifications through `notify_fname()` and triggers lease/dirlease break behavior for timestamp and hardlink changes.

Time handling is stateful. `smb_set_file_time()` rounds timestamps to the connection timestamp resolution, omits fields marked "no change", sets sticky write time on open files when requested, and calls `file_ntimes()`. File size and allocation updates call `prepare_file_modified()`, `mark_file_modified()`, `trigger_write_time_update_immediate()`, or `vfs_allocate_file_space()` to preserve Windows-visible update semantics.

## Dependencies And Integration Points
The file integrates heavily with Samba's VFS layer: xattrs, directory attributes, statvfs, file ids, allocation size, stream info, quota, linkat, create/open, chmod-like DOS mode, truncate, and timestamp operations all cross the VFS boundary. It also depends on Samba path conversion and name mangling code, SMB string conversion helpers, NDR encoders for SMB3 POSIX information, security tokens, access-check helpers, share-mode/delete-on-close logic, notify/lease code, reparse point helpers, and loadparm configuration.

SMB1 and SMB2 integration is intentional. Several public functions are called from both SMB1 trans2/NT transact handlers and SMB2 query/set info handlers, with protocol-specific branches such as `conn_using_smb2()`, `fsp->fsp_flags.posix_open`, SMB2 normalized names, SMB2 full EA chained buffers, and SMB2 rename wire parsing.

## Risks And Edge Cases
The largest risk is wire-format compatibility. Many cases have fixed offsets, padding, null-termination quirks, and client-specific comments. Small layout mistakes can break old clients, SMB2 `fixed_portion` calculation, directory enumeration continuation, or EA parsing.

Security-sensitive areas include symlink refusal for EA operations, protection of Samba-private xattrs, access checks for write attributes/data/EA, snapshot write protection, quota root checks, delete-on-close authorization, and hardlink/rename path conversion. Bugs here can expose metadata, permit mutation without rights, or allow unsafe path handling.

State correctness risks include sticky write times after writes, delete-on-close across multiple handles, allocation-size rounding that differs by client type, fallback opens for path-based size/allocation changes, and correct cleanup after temporary open failures. The hardlink path rejects directories, streams, existing targets without overwrite, and timewarp source paths, all of which should remain covered.

## Test Signals
Relevant tests are Samba smbtorture RAW-SFILEINFO, RAW-QFILEINFO, SMB2-QUERY-INFO, SMB2-SETINFO, SMB2-CREATE replay/rename variants, stream tests, EA tests, UNIX/POSIX extension tests, quota tests when enabled, and durable handle regression tests around delete-on-close and lease breaks. Manual probes should cover Windows clients, Linux CIFS clients, SMB1 UNIX extensions, SMB3 POSIX opens, AAPL directory attributes, reparse points, named streams, symlinks, snapshots, pathrefs, max-sized EA buffers, and insufficient response-buffer cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_trans2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_write.c -->
# sources/user-network-fs/samba/source3/smbd/smb2_write.c

## Purpose
This file implements the SMB2 WRITE request path in smbd. It parses SMB2 write packets, validates offsets, data lengths, credit charge, file ids, and server max-write limits, then performs writes to normal files or named pipes using asynchronous paths where possible and synchronous fallback where needed.

## Important APIs, Types, And Functions
The top-level entry point is `smbd_smb2_request_process_write()`. It verifies the request body size, extracts the data offset, data length, offset, persistent and volatile file ids, and write flags, resolves the `files_struct` through `file_fsp_smb2()`, and starts `smbd_smb2_write_send()`.

`smbd_smb2_request_write_done()` receives the tevent completion, builds the SMB2 write response body, writes the byte count, and completes or errors the original SMB2 request.

`struct smbd_smb2_write_state` tracks the request, fake SMB1 request wrapper, target fsp, write-through flag, input length and offset, and output byte count. `smb2_write_complete()` and `smb2_write_complete_nosync()` route into `smb2_write_complete_internal()`, which maps write errors, handles disk-full zero-write behavior, optionally calls `sync_file()`, and stores `out_count`.

`smbd_smb2_write_send()` is the core worker. It handles write-through flag interpretation, fake SMB request creation, named-pipe writes through `np_write_send()`, access checks, POSIX append offset rules, asynchronous file writes through `schedule_aio_smb2_write()`, cancellation through `cancel_smb2_aio()`, strict-lock checks, synchronous `write_file()` fallback, and completion posting.

## Control Flow
The request path first validates the SMB2 wire shape. The data offset must equal the header plus body length, the announced data length must fit in the dynamic input buffer or deferred SMB1 unread bytes for recvfile-style handling, and the length must not exceed `xconn->smb2.server.max_write`. Credit charge is verified against the write length before the file id lookup.

For IPC/named pipes, `smbd_smb2_write_send()` requires a pipe fsp, sends the buffer to `np_write_send()`, marks async activity on the fsp with `aio_add_req_to_fsp()`, and completes in `smbd_smb2_write_pipe_done()`. Pipe errors are mapped through `nt_status_np_pipe()`, and zero writes for nonzero input are treated as access denied.

For normal files, the function checks `FILE_WRITE_DATA|FILE_APPEND_DATA`, validates the special append offset against `fsp->fsp_flags.posix_append`, and tries `schedule_aio_smb2_write()`. `NT_STATUS_OK` means the AIO layer owns completion and cancellation is enabled. Any status other than `NT_STATUS_RETRY` is a setup failure. `NT_STATUS_RETRY` falls back to synchronous I/O after `SMB_VFS_STRICT_LOCK_CHECK()`.

## State And Persistence Behavior
Persistent state changes are the bytes written to the target file or pipe. The path also updates normal smbd file-modified state indirectly through `write_file()` or AIO completion code, and it may force data to stable storage with `sync_file()` when write-through or SMB 3.0.2 unbuffered flags request it.

The tevent request state is transient and owns the fake `smb_request`. Cancellation is available only for scheduled SMB2 AIO writes. IPC writes attach async state to the fsp to protect shutdown/close handling while a pipe write is outstanding.

## Dependencies And Integration Points
This file integrates with SMB2 request framing, credit accounting, `file_fsp_smb2()` open lookup, smbd fake SMB1 request creation, access checks from `smb2_trans2.c`, named-pipe helpers, AIO scheduling/cancellation, strict byte-range locking, `write_file()`, sync/write-through handling, and server connection termination on transport errors.

It also depends on `smbd_smb2_request_pending_queue()` for asynchronous response lifetime and uses the generic tevent request model used throughout smbd.

## Risks And Edge Cases
Important correctness risks include accepting malformed data offsets, overrun of the dynamic buffer, exceeding negotiated max write, mishandling recvfile-style NULL input data, incorrect credit charge verification, or returning success for zero bytes written when the client sent data.

Concurrency risks involve strict-lock enforcement on the synchronous fallback and cancellation semantics for AIO. Append mode is intentionally strict: POSIX-append handles must use `VFS_PWRITE_APPEND_OFFSET`, and non-append handles must not. Write-through behavior must remain aligned with protocol flags because it affects durability guarantees and performance.

## Test Signals
Useful tests include SMB2 write torture cases for max-write negotiation, credit charge boundaries, invalid data offsets, invalid file ids, byte-range lock conflicts, append-only behavior, write-through/unbuffered writes, AIO cancellation, disk-full behavior, alternate-stream `EOVERFLOW` mapping to `NT_STATUS_FILE_SYSTEM_LIMITATION`, named-pipe writes, and recvfile/large-write paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb2_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_client.c -->
# sources/user-network-fs/samba/source3/smbd/smbXsrv_client.c

## Purpose
This file manages the global SMBX client identity record for an smbd client and implements SMB3 multichannel negotiate ownership transfer. It persists one client record keyed by client GUID, coordinates which smbd process owns that GUID, passes accepted sockets to the owner process when possible, or asks the current owner to disconnect so another process can take over.

## Important APIs, Types, And Functions
`struct smbXsrv_client_table` holds local client counts and the global watched DB context. `smbXsrv_client_global_init()` opens `smbXsrv_client_global.tdb` under the lock path with watched-db support; the comments note that this database contains secret information such as client keys.

`smbXsrv_client_global_id_to_key()` converts a client GUID to the fixed 16-byte TDB key. `smbXsrv_client_global_fetch_locked()` locks a specific client record. `smbXsrv_client_global_verify_record()` parses the NDR `smbXsrv_client_globalB` value, validates version 0, deletes records for explicitly dead or nonexistent server ids, returns free/existing state, and can return the parsed global record plus sequence number.

`smbXsrv_client_create()` builds the per-process client object, initializes the table, sets multi-channel state, stores initial connect time and server id, installs destructors, and starts two long-lived filtered messaging reads for `MSG_SMBXSRV_CONNECTION_PASS` and `MSG_SMBXSRV_CONNECTION_DROP`.

`smb2srv_client_mc_negprot_send()`, `smb2srv_client_mc_negprot_next()`, `smb2srv_client_mc_negprot_done()`, and `smb2srv_client_mc_negprot_watched()` implement the multichannel negotiate state machine for a new connection with an already-known client GUID. `smb2srv_client_connection_pass()` serializes the original negotiate request and sends the TCP socket fd to the owning process if local. `smb2srv_client_connection_drop()` sends a takeover/drop message when the owner is not local.

`smbXsrv_client_connection_pass_loop()` receives passed sockets, validates the pass blob, acknowledges with `MSG_SMBXSRV_CONNECTION_PASSED`, adds the connection with `smbd_add_connection()`, marks the client GUID verified, and replays the captured negotiate request into `smbd_smb2_process_negprot()`. `smbXsrv_client_connection_drop_loop()` validates drop messages and calls `smbd_server_disconnect_client()`.

`smbXsrv_client_remove()` locks and deletes the global client record during teardown after cancelling message loops.

## Control Flow
On initial client creation, no global record is necessarily stored until the SMB2 client GUID is known and verified. In multichannel negotiation, `smb2srv_client_mc_negprot_next()` locks the GUID record and verifies it. If the record is free, it stores the current client global record, marks the GUID verified, and completes.

If another live process owns the GUID, the code avoids duplicate socket delivery by tracking `sent_server_id`. For a local owner process, it opens a filtered read waiting for `MSG_SMBXSRV_CONNECTION_PASSED`, sends a pass message with one fd and the original negotiate request, and then watches the DB record. For a remote/nonlocal owner, it sends a drop message so that the owner disconnects and removes the record, waking watchers.

Watched DB sequencing is used for fairness. If the sequence number changed, this waiter removes and re-adds its watch instance so other waiters can progress. When the watched record changes, the state machine re-locks and re-verifies the record.

The receiving owner process continuously listens for pass and drop messages. The pass loop validates GUIDs and connect times, acknowledges the origin, consumes the fd into a new `smbXsrv_connection`, extracts the original SMB2 message id from the captured negotiate request, and processes negotiation. The drop loop validates identity and disconnects all client connections so another process can acquire the GUID record.

## State And Persistence Behavior
Persistent state is the watched TDB record in `smbXsrv_client_global.tdb`, keyed by client GUID and containing NDR-encoded `smbXsrv_client_global0` plus a sequence number. The stored record tracks client GUID, server id, connect times, addresses, names, and other client-global authentication/session material from generated NDR structures.

Local state includes the `smbXsrv_client` object, current message loops, `server_multi_channel_enabled`, `next_channel_id`, raw event and messaging contexts, and the stored flag on the global record. Records are removed when the client is torn down, and stale records are deleted if their server id no longer exists.

The pass/drop messaging protocol transfers live socket file descriptors and captured negotiate bytes between smbd processes. Correct fd ownership is enforced by setting `rec->num_fds = 0` after successful consumption and closing any unconsumed fds on the `next:` path.

## Dependencies And Integration Points
The file depends on dbwrap, watched dbwrap, Samba messaging with fd passing, tevent, generated NDR for SMBXSRV structures, server-id liveness checks, global messaging context, tsocket transport descriptors, SMB2 negotiate processing, smbd connection add/disconnect functions, authentication/session structures, and multi-channel server policy helpers.

It integrates directly with SMB2 negotiation: this is the code that decides whether a new transport connection for a client GUID is accepted locally, passed to an existing owner, or causes a disconnect/takeover sequence.

## Risks And Edge Cases
This file is race-sensitive. Duplicate pass messages for the same fd can create multiple `smbXsrv_connection` objects for one TCP connection, so `sent_server_id` and watcher ordering are critical. Stale server-id cleanup must be correct or client GUIDs can remain permanently owned by dead processes.

Security and correctness risks include malformed NDR records, invalid message versions, GUID/connect-time mismatches, failing to close passed fds on error paths, storing secret client state in a database with incorrect permissions, and accepting a negotiated connection into the wrong client object.

Cluster or nonlocal behavior is delicate. Local owners receive sockets through fd passing; nonlocal owners receive drop messages and must remove state to let the new process proceed. Any missed watch wakeup, sequence handling bug, or failed global-record removal can stall multichannel negotiation.

## Test Signals
Test signals include SMB3 multichannel negotiate/reconnect torture tests, repeated simultaneous connections with the same client GUID, owner process death during negotiation, pass-message fd leak checks, drop/takeover behavior, watched-db wakeups under contention, malformed/corrupt `smbXsrv_client_global.tdb` records, and verification that session keys and message-id validation remain correct after socket pass.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_open.c -->
# sources/user-network-fs/samba/source3/smbd/smbXsrv_open.c

## Purpose
This file manages SMBX open-handle identity for SMB1 and SMB2. It allocates local volatile ids, stores global/persistent open records in `smbXsrv_open_global.tdb`, supports durable/disconnected opens, implements SMB2 create replay cache handling, recreates durable handles, traverses global open state, and cleans expired or stale open/replay records.

## Important APIs, Types, And Functions
`struct smbXsrv_open_table` contains the local id allocator and global DB context. The local side uses an `idr_context` bounded by protocol-specific id ranges; the global side uses a TDB database shared across smbd processes.

`smbXsrv_open_global_init()` opens `smbXsrv_open_global.tdb`. `smbXsrv_open_global_id_to_key()` converts 32-bit global ids to big-endian TDB keys so in-memory dbwrap ordering matches integer order. `smbXsrv_open_global_parse_record()`, `smbXsrv_open_global_verify_record()`, `smbXsrv_open_global_lookup()`, and `smbXsrv_open_global_store()` handle NDR serialization, version validation, stale-server detection, sequence numbers, and locked updates.

`smbXsrv_open_create()` allocates a local open object and local id, initializes `smbXsrv_open_global0`, records owner SID, session/tcon global ids, client GUID for SMB2.1+, random-allocates a global id, and stores the global record. `smbXsrv_open_update()` rewrites the global record and populates the replay cache if requested. `smbXsrv_open_close()` marks an open closed, stores a disconnected durable record or deletes a nondurable one, clears replay cache for nondurable opens, removes the local id, and frees the compat `files_struct`.

SMB1 and SMB2 table/lookup entry points are `smb1srv_open_table_init()`, `smb1srv_open_lookup()`, `smb2srv_open_table_init()`, and `smb2srv_open_lookup()`. SMB2 lookups validate high 32 bits, match volatile and persistent ids, refresh idle time, and clear the replay cache once the client proves it received the create response.

Replay-cache functions are `smbXsrv_open_replay_cache_key()`, `smbXsrv_open_set_replay_cache()`, `smbXsrv_open_purge_replay_cache()`, `smbXsrv_open_clear_replay_cache()`, and `smb2srv_open_lookup_replay_cache()`. Durable reconnect is implemented by `smb2srv_open_recreate()` and `smb2srv_open_recreate_fn()`. Cleanup and traversal use `smbXsrv_open_global_traverse()`, `smbXsrv_open_cleanup()`, and `smbXsrv_replay_cleanup()`.

## Control Flow
Open table initialization selects an id range and maximum open count, creates the local IDR allocator, initializes the global DB, and attaches the table to the client. SMB1 uses 1..65534. SMB2 allows a wider `int`-bounded local id space, but max opens is still capped by `real_max_open_files` and currently truncated to the SMB1-like limit.

Create flow allocates local first, initializes global metadata, then repeatedly tries random 32-bit global ids. Each candidate is locked and verified. Empty slots are stored. Live records cause retry. Records for dead smbd processes can be deleted and then retried, with a small delay before immediate id reuse.

Lookup flow is intentionally two-tiered. The local volatile id finds an in-process `smbXsrv_open`; the global/persistent id confirms it is the intended open. SMB1 treats the global check as a no-op by passing zero.

Replay-cache lookup has three major states. No record creates a reservation and returns `NT_STATUS_FWP_RESERVED`. A record with global id zero means the original create is still pending and returns `NT_STATUS_FILE_NOT_AVAILABLE`. A record with a valid global id looks up the original global open; if a matching local open exists and session matches, it returns that open, otherwise it returns `NT_STATUS_HANDLE_NO_LONGER_VALID` with the persistent id to trigger reconnect.

Durable recreate validates the persistent id width, allocates a fresh local open id, locks the global record, requires a disconnected durable record, optionally validates client GUID and create GUID, checks the current user's token contains the original owner SID, updates volatile id/server/session/tcon fields, stores the record, and returns the recreated local open.

Cleanup locks the global id, deletes corrupt, expired disconnected, or dead-server records, and then deletes the associated replay-cache key if a create GUID was present. Traversal distinguishes normal open records from fixed-size replay-cache records and reports either the parsed global open or the replay-cache global-key value to the callback.

## State And Persistence Behavior
The local `idr_context` maps volatile ids to in-process `smbXsrv_open` objects and tracks `num_opens`. The global TDB maps persistent/global ids to NDR-encoded `smbXsrv_open_global0` records. For SMB2 durable handles, close does not delete the global record; it sets a disconnected server id, disconnect time, clears session/tcon ids, and stores the durable state for later reconnect until timeout cleanup.

Replay cache records live in the same global DB but use a key composed from client GUID and create GUID, with a value containing the global open id key. A zero global id value is a pending reservation. Replay cache entries are removed when normal file-id lookup proves the client received the original response, when create failure purges a reservation, or during cleanup.

Open global records hold persistent id, volatile id, server id, open time, disconnect time, owner SID, session/tcon global ids, client GUID, create GUID, durable flags and timeout, and lock sequence array state. Store operations preserve and increment a record sequence number embedded in the NDR wrapper.

## Dependencies And Integration Points
The file integrates with generated `ndr_smbXsrv` structures, Samba dbwrap, random id generation, server-id liveness, messaging server ids, session/tcon/auth state, GUID/lease structures, durable-handle reconnect logic in create handling, file close/free logic, and replay cleanup callers.

It is the authoritative handle id layer used by SMB1 fnum lookup and SMB2 persistent/volatile file id lookup. Other smbd paths depend on it for resolving request file ids, durable handle reconnect, create replay idempotence, and global open cleanup after crashes or timeouts.

## Risks And Edge Cases
Persistent id allocation must avoid collisions and premature id reuse. Corrupt records, dead smbd records, and disconnected durable records all have different meanings. A bad status mapping can leak handles, break durable reconnect, or make clients retry indefinitely.

Replay-cache semantics are subtle. Returning the wrong status for pending, successful same-process replay, successful other-process replay, or stale record cases changes SMB2 create idempotence and durable reconnect behavior. Clearing replay cache too early can make a replay fail; clearing too late can accept duplicate creates.

Security risks include reconnecting a durable handle for a user whose token does not contain the original owner SID, accepting mismatched client/create GUIDs, or ignoring high 32 bits in SMB2 ids incorrectly. Cleanup risks include deleting live durable records or failing to remove expired replay records.

## Test Signals
Relevant signals are SMB2 create replay tests, durable-handle v1/v2 reconnect tests, persistent/volatile id validation, session mismatch replay returning duplicate-object behavior, crash/stale-record cleanup, durable timeout cleanup, multi-process reconnect, SMB1 fnum lookup, maximum-open exhaustion, replay reservation purge on failed create, and traversal consumers such as status/debug tooling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_open.h -->
# sources/user-network-fs/samba/source3/smbd/smbXsrv_open.h

## Purpose
This header declares the smbd SMBX open-handle management interface implemented by `smbXsrv_open.c`. It exposes global initialization, create/update/close, SMB1 and SMB2 lookup tables, SMB2 create replay cache lookup/purge, durable open recreation, global traversal, and cleanup APIs.

## Important APIs, Types, And Functions
The header forward-declares `smbXsrv_connection`, `auth_session_info`, `smbXsrv_open`, `smbXsrv_open_global0`, `smbXsrv_client`, `smbXsrv_session`, `smbXsrv_tcon`, `smb2_lease_key`, and `db_record`, keeping consumers decoupled from the concrete structures.

Public lifecycle calls are `smbXsrv_open_global_init()`, `smbXsrv_open_create()`, `smbXsrv_open_update()`, and `smbXsrv_open_close()`. Protocol-specific table APIs are `smb1srv_open_table_init()`, `smb1srv_open_lookup()`, `smb2srv_open_table_init()`, and `smb2srv_open_lookup()`.

Replay and durable APIs are `smbXsrv_open_purge_replay_cache()`, `smb2srv_open_lookup_replay_cache()`, `smb2srv_open_recreate()`, `smbXsrv_open_cleanup()`, and `smbXsrv_replay_cleanup()`. `smbXsrv_open_global_traverse()` exposes a callback-based iterator that can return either a parsed global open record or a replay-cache value key.

## Control Flow
Callers initialize global/table state during connection setup, create an open after successful file create, update it when durable/replay/create metadata changes, look it up for request file ids, and close it during file teardown. SMB2 create handling also calls the replay-cache lookup before normal create processing and calls recreate when durable reconnect is required.

The traverse API inverts control: callers pass a callback taking a locked `db_record`, optional `smbXsrv_open_global0`, optional replay-cache key value, and private data. Cleanup APIs are called by housekeeping or reconnect failure paths to delete stale persistent/replay state.

## State And Persistence Behavior
The header itself has no state, but its functions govern the persistent `smbXsrv_open_global.tdb` records and in-memory per-client open tables. The exposed parameters make the identity model explicit: SMB2 file ids are `persistent_id` plus `volatile_id`; replay identity is client GUID plus create GUID; durable recreation may also validate create GUID and lease key.

## Dependencies And Integration Points
Includes are minimal: `replace.h`, NTSTATUS, NTTIME, `DATA_BLOB`, and generated misc GUID definitions. This lets SMB2 create/read/write/setinfo/close code, cleanup code, and debugging/traversal code share the open-management contract without including the implementation's dbwrap, idtree, or NDR details.

## Risks And Edge Cases
Because this is a cross-module contract, signature changes can affect many SMB1/SMB2 handlers. The callback shape for traversal is especially easy to misuse because either `global` or `rc_open_global_key` may be present depending on record type. Callers must also preserve the distinction between SMB2 persistent and volatile ids and must not treat replay-cache statuses as generic lookup errors.

## Test Signals
Header-level test signal comes from successful compilation of all smbd consumers plus runtime coverage of create/update/close, SMB1 lookup, SMB2 file-id lookup, replay-cache lookup/purge, durable reconnect, traversal, and cleanup paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smbXsrv_open.h -->
