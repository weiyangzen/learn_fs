# Group Research: group_839_linux_sources_os_linux_linux_fs_smb_server_mgmt_user_session_h_sourc_fec64bd71e01

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/user_session.h -->
# File Research: sources/os/linux/linux/fs/smb/server/mgmt/user_session.h

This header defines ksmbd’s per-user SMB session model and the public session-management API used by the SMB2/SMB3 server path.

Key structures:
- `struct channel` binds a `ksmbd_conn` to an SMB3 signing key for multichannel-capable sessions.
- `struct preauth_session` stores SMB 3.1.1 preauthentication hash state before a full session is established.
- `struct ksmbd_session` is the central authenticated-session object. It tracks session id, dialect, client GUID, user, sequence number, signing/encryption flags, state, preauth hash, session key, channel xarray, tree-connect xarray and ID allocator, RPC handle xarray, SMB3 encryption/decryption/signing keys, file table, activity time, procfs entry, refcount, and locks.

Important exported operations:
- Session lifecycle: `ksmbd_smb2_session_create`, `ksmbd_session_destroy`, `ksmbd_session_register`, `ksmbd_sessions_deregister`.
- Lookup paths: per-connection, global/all-session, slowpath, and raw `__session_lookup`.
- Preauth: `ksmbd_preauth_session_alloc`, `ksmbd_preauth_session_lookup`.
- Tree-connect IDs: `ksmbd_acquire_tree_conn_id`, `ksmbd_release_tree_conn_id`.
- RPC handles: `ksmbd_session_rpc_open`, `ksmbd_session_rpc_close`, `ksmbd_session_rpc_method`.
- Refcounting: `ksmbd_user_session_get`, `ksmbd_user_session_put`.

Concurrency/lifetime notes:
- `chann_lock`, `tree_conns_lock`, and `rpc_lock` protect mutable per-session containers.
- `atomic_t refcnt` makes session lifetime explicit across request dispatch and async paths.
- Procfs session visibility is compiled under `CONFIG_PROC_FS`.

Role in this group:
- `server.c` obtains/releases sessions while handling requests.
- `proc.c` initializes procfs, while session-specific proc entries are declared here and implemented in session management code.
- `ntlmssp.h` provides constants and packet structures needed to authenticate and fill session keys.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/user_session.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/misc.c -->
# File Research: sources/os/linux/linux/fs/smb/server/misc.c

This file contains shared ksmbd utility routines for pattern matching, filename/path conversion, share-name case folding, directory-name conversion, and SMB/Unix time conversion.

Main behavior:
- `match_pattern()` implements case-insensitive wildcard matching with `*` and `?`. It explicitly notes missing DOS wildcard semantics for DOS_DOT, DOS_QM, and DOS_STAR.
- `ksmbd_validate_filename()` rejects ASCII control characters and Windows-invalid wildcard/special characters such as `?`, `"`, `<`, `>`, `|`, and `*`.
- `parse_stream_name()` splits NTFS alternate data stream syntax, validates stream names against `/`, `:`, and `\`, and maps `$DATA` to `DATA_STREAM` and `$INDEX_ALLOCATION` to `DIR_STREAM`.
- `convert_to_nt_pathname()` converts a kernel `struct path` to a share-relative Windows path after verifying it is under the share root.
- `convert_to_unix_name()` joins a share root and client-relative path into a Unix path string.
- `ksmbd_casefold_sharename()` uses Unicode casefolding when available, otherwise ASCII lowercasing.
- `ksmbd_extract_sharename()` extracts the final component of a UNC tree path.
- `ksmbd_convert_dir_info_name()` converts directory names to UTF-16 for SMB directory responses.
- `ksmbd_NTtimeToUnix()`, `ksmbd_UnixTimeToNT()`, and `ksmbd_systime()` convert between NTFS 100ns timestamps since 1601 and Unix `timespec64`.

Notable implementation details:
- Path conversion mutates slash direction with `strreplace`.
- `convert_to_nt_pathname()` returns `ERR_PTR` values on allocation, prefix, or `d_path()` failure.
- The NT time conversion handles negative pre-1970 timestamps without relying on signed 64-bit division on 32-bit architectures.
- `parse_stream_name()` assumes the caller passes a name containing stream syntax; callers should avoid invoking it on names where `strsep()` leaves no stream component.

Role in this group:
- Provides utility declarations in `misc.h`.
- Used by SMB request handlers and VFS-facing code for path, share, directory, and time normalization.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/misc.h -->
# File Research: sources/os/linux/linux/fs/smb/server/misc.h

This header declares shared helper APIs for ksmbd utility code and procfs integration.

Functional areas:
- Filename and path handling: `match_pattern`, `ksmbd_validate_filename`, `parse_stream_name`, `convert_to_nt_pathname`, `convert_to_unix_name`, slash conversion helpers, and trailing-slash stripping.
- Share-name handling: `ksmbd_casefold_sharename` and `ksmbd_extract_sharename`.
- Directory response conversion: `ksmbd_convert_dir_info_name()` and `KSMBD_DIR_INFO_ALIGNMENT`.
- Time conversion: `NTFS_TIME_OFFSET`, `ksmbd_NTtimeToUnix`, `ksmbd_UnixTimeToNT`, and `ksmbd_systime`.

Procfs API:
- Under `CONFIG_PROC_FS`, declares `struct ksmbd_const_name` and proc helpers:
  `ksmbd_proc_init`, `ksmbd_proc_cleanup`, `ksmbd_proc_reset`, `ksmbd_proc_create`,
  `ksmbd_proc_show_flag_names`, and `ksmbd_proc_show_const_name`.
- Without procfs, init/cleanup/reset become no-op inline functions, keeping server lifecycle code simple.

Role in this group:
- `misc.c` implements the non-proc utility APIs.
- `proc.c` implements procfs setup and server counters.
- Session-management code implements some proc formatting helpers declared here, so this header is a shared contract across general server, session, connection, and file-cache instrumentation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/ndr.c -->
# File Research: sources/os/linux/linux/fs/smb/server/ndr.c

This file implements ksmbd’s local NDR-style little-endian encoder/decoder for DOS attributes, POSIX ACL metadata, and NT ACL xattrs.

Internal marshalling helpers:
- `ndr_get_field()` returns the current cursor.
- `try_to_realloc_ndr_blob()` grows the blob by 1024 bytes and zeroes the new region.
- `ndr_write_int16/int32/int64`, `ndr_write_bytes`, and `ndr_write_string` append little-endian values or aligned strings.
- `ndr_read_int16/int32/int64`, `ndr_read_bytes`, and `ndr_read_string` bounds-check reads against `n->length`.

DOS attribute handling:
- `ndr_encode_dos_attr()` allocates a 1024-byte blob and writes versioned DOS xattr data. Version 3 includes hex attr text, EA size, size, allocation size, create time, and change time; version 4 writes internal time and create time.
- `ndr_decode_dos_attr()` validates supported versions 3 and 4, checks duplicate version fields match, and extracts attributes and timestamps.

ACL handling:
- `ndr_encode_posix_acl()` writes optional access/default ACL references, mapped inode uid/gid through the mount idmap, mode, and ACL entries.
- `ndr_encode_v4_ntacl()` writes version, hash metadata, description, current time, POSIX ACL hash, and raw security descriptor.
- `ndr_decode_v4_ntacl()` validates version 4, verifies the description starts with `posix_acl`, allocates `sd_buf`, and copies the remaining security descriptor.

Risk/edge notes:
- Encoder functions allocate `n->data`; ownership is transferred to callers.
- Some error paths after allocation return without freeing `n->data`, so callers must treat partial encode failures carefully or the caller path must clean up.
- Decode functions consistently reject short buffers via offset/length checks.

Role in this group:
- Declared by `ndr.h`.
- Supplies serialization used by ksmbd VFS/xattr ACL paths rather than direct network SMB2 packet processing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/ndr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/ndr.h -->
# File Research: sources/os/linux/linux/fs/smb/server/ndr.h

This compact header declares the NDR blob cursor and encoder/decoder entry points.

Key declarations:
- `struct ndr` carries `data`, current `offset`, and total `length`.
- `NDR_NTSD_OFFSETOF` defines the NT security descriptor offset constant used by related ACL code.
- Public APIs cover DOS attribute encode/decode, POSIX ACL encode, v3/v4 NT ACL encode, and v4 NT ACL decode.

Role in this group:
- `ndr.c` implements all declared functions.
- Callers provide filesystem xattr-side structures such as `xattr_dos_attrib`, `xattr_smb_acl`, and `xattr_ntacl`.
- The header intentionally exposes only high-level serialization calls, keeping primitive read/write helpers private to `ndr.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/ndr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/ntlmssp.h -->
# File Research: sources/os/linux/linux/fs/smb/server/ntlmssp.h

This header defines NTLMSSP constants and packed wire structures used by ksmbd authentication.

Protocol constants:
- Signature: `NTLMSSP_SIGNATURE`.
- Target name: `TGT_Name` as `KSMBD`.
- Key and ciphertext sizes: `CIFS_CRYPTO_KEY_SIZE`, `CIFS_KEY_SIZE`, `CIFS_ENCPWD_SIZE`, and `CIFS_CPHTXT_SIZE`.
- Message type constants for negotiate, challenge, authenticate, and unknown messages.
- Full NTLMSSP negotiate flag set for Unicode/OEM strings, signing, sealing, NTLM, domain/workstation supplied, target info, version, 128-bit, key exchange, and 56-bit negotiation.

Wire structures:
- `struct security_buffer` models NTLMSSP length/max-length/offset triples.
- `struct target_info` models AV-pair records.
- `struct negotiate_message`, `challenge_message`, and `authenticate_message` are packed layouts for the three NTLMSSP exchange messages.
- `struct ntlmv2_resp` models the NTLMv2 response prefix.
- `struct ntlmssp_auth` stores per-session NTLMSSP negotiation state, connection/client flags, ciphertext, and challenge key.

Role in this group:
- Included by `user_session.h` for `CIFS_KEY_SIZE` session-key storage.
- Used by ksmbd authentication code outside this group to parse and produce NTLMSSP security blobs during SMB2 session setup.

Security relevance:
- Structures are `__packed` and endian-annotated for direct wire parsing.
- The header contains layout definitions only; validation and cryptographic operations happen in auth code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/ntlmssp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/oplock.c -->
# File Research: sources/os/linux/linux/fs/smb/server/oplock.c

This file implements ksmbd SMB2/SMB3 oplocks, leases, break notifications, create-context helpers, and durable-handle reconnect validation.

Core data organization:
- Per-inode oplock records live on `ksmbd_inode::m_op_list`, protected by the inode `m_lock`.
- Lease records are additionally indexed in global `lease_table_list`, keyed by SMB2 client GUID and protected by `lease_list_lock`.
- `oplock_info` lifetime is refcounted and freed via RCU. File pointers publish `f_opinfo` with RCU assignment.
- Separate per-inode counters distinguish normal file oplocks and stream oplocks.

Allocation/lifetime:
- `alloc_opinfo()` initializes wait queues, refcounts, connection reference, FID, TID, state, and level.
- `alloc_lease()` creates lease state from parsed create context.
- `close_id_del_oplock()` removes list entries, clears `fp->f_opinfo`, wakes waiters if a break is pending, decrements counts, and releases refs.
- `destroy_lease_table()` removes all lease-table entries for a connection or globally.

State transitions:
- `opinfo_write_to_read`, `opinfo_read_handle_to_read`, `opinfo_write_to_none`, and `opinfo_read_to_none` apply acknowledged break transitions.
- `lease_read_to_write()` and `lease_none_upgrade()` handle same-client lease upgrades.
- `smb2_map_lease_to_oplock()` maps R/H/W lease-state combinations to batch, exclusive, level II, or none.

Break handling:
- `oplock_break_pending()` serializes concurrent break operations using a bit wait.
- `oplock_break()` computes target state, sends interim responses when needed, marks `OPLOCK_ACK_WAIT`, sends oplock or lease break notifications, waits for acknowledgements/timeouts, and wakes waiters.
- `smb2_oplock_break_noti()` and `smb2_lease_break_noti()` build async SMB2 break notifications.
- `smb_break_all_write_oplock`, `smb_break_all_levII_oplock`, and `smb_break_all_oplock` are called by write/truncate and open paths to invalidate client caching.

Grant path:
- `smb_grant_oplock()` handles file-create requested oplock/lease levels, directory lease constraints, same-client lease reuse/upgrade, share-mode conflicts, breaking previous exclusive/batch owners, stacked lease/oplock restrictions, and final publication.
- It preallocates a new lease table before publishing `opinfo` to inode/global lists, avoiding failure after concurrent readers can see the object.

Create-context helpers:
- `parse_lease_state()` extracts v1/v2 lease create contexts.
- `smb2_find_context_vals()` walks create contexts with alignment, length, and bounds validation.
- Response builders create lease, durable handle v1/v2, maximal access, disk ID, and POSIX extension contexts.

Durable reconnect:
- `lookup_lease_in_table()` finds a breakable lease for client GUID and lease key.
- `smb2_check_durable_oplock()` validates durable reconnect owner, client GUID, lease key, handle-caching state, lease version, batch oplock requirements, and path/name validity unless pending delete.

Concurrency notes:
- Uses RCU for `f_opinfo` and lease-list iteration, refcounts before dropping RCU read locks, wait queues for break acknowledgements, and atomic counters for concurrent break state.
- Calls avoid operating on connections in releasing state.
- Timeout paths downgrade caching to none when clients do not acknowledge.

Role in this group:
- Declared by `oplock.h`.
- Called from SMB2 create, write, truncate, close, lease-break acknowledgement, durable reconnect, and VFS mutation paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/oplock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/oplock.h -->
# File Research: sources/os/linux/linux/fs/smb/server/oplock.h

This header defines ksmbd’s oplock/lease data structures, state constants, and public oplock API.

Constants:
- `OPLOCK_WAIT_TIME` is 35 seconds.
- Oplock object states: none, acknowledgement wait, and closing.
- Break transition flags describe write-to-read, read-handle-to-read, write-to-none, and read-to-none.

Key structures:
- `lease_ctx_info` holds parsed SMB2 create lease request data, including lease key, requested state, flags, duration, parent lease key, epoch, version, and directory flag.
- `lease_table` groups leases by client GUID.
- `lease` stores active granted lease state and metadata.
- `oplock_info` binds a lease/oplock to connection, session, work, file, level, state, FID/TID, pending break bit, refcount, break count, wait queues, and list nodes.
- `lease_break_info` and `oplock_break_info` are small work payloads for async break notifications.

Exported behavior:
- Grant and break: `smb_grant_oplock`, `smb_break_all_levII_oplock`, `smb_break_all_oplock`, `close_id_del_oplock`.
- State transitions: `opinfo_write_to_read`, `opinfo_read_handle_to_read`, `opinfo_write_to_none`, `opinfo_read_to_none`, `lease_read_to_write`.
- Lookup/lifetime: `opinfo_get`, `opinfo_put`, `lookup_lease_in_table`, `find_same_lease_key`, `destroy_lease_table`.
- Create-context utilities: lease parsing, lease/oplock mapping, durable response builders, POSIX response builder, and context lookup.
- Durable reconnect validation: `smb2_check_durable_oplock`.

Role in this group:
- `oplock.c` implements the state machine.
- SMB2 create/close/write/ioctl paths include this header to coordinate client-side caching semantics with server-side file operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/oplock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/proc.c -->
# File Research: sources/os/linux/linux/fs/smb/server/proc.c

This file implements ksmbd procfs monitoring support and global per-CPU counters.

Procfs layout:
- Creates `/proc/fs/ksmbd`.
- Creates a `sessions` directory under it.
- Creates a `server` proc entry via `ksmbd_proc_create()`.

Counters:
- Defines global `struct ksmbd_counters ksmbd_counters`.
- Initializes and destroys all `percpu_counter` entries.
- `ksmbd_proc_reset()` sets counters to zero.
- Server stats include sessions, tree connects, read bytes, written bytes, and per-SMB2-command request counts.

Server stats display:
- Prints server string, NetBIOS name, workgroup, min/max protocol strings, server flags, fake filesystem capabilities, and aggregate counters.
- Maps SMB2 command indexes to stable names from negotiate through oplock break.

Lifecycle:
- `ksmbd_proc_init()` creates procfs directories, initializes counters, creates the server stats entry, and resets counters.
- Any init failure calls `ksmbd_proc_cleanup()` for partial cleanup.
- `ksmbd_proc_cleanup()` removes the proc tree and destroys counters.

Role in this group:
- Called from `server.c` module init and cleanup paths.
- Helper declarations live in `misc.h`.
- Session proc entries are declared through `user_session.h` and implemented by session management code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/server.c -->
# File Research: sources/os/linux/linux/fs/smb/server/server.c

This file is the ksmbd module lifecycle, control-plane, and request-dispatch hub.

Global state:
- Defines `ksmbd_debug_types`.
- Defines global `struct ksmbd_server_config server_conf`.
- Provides setters/getters for NetBIOS name, server string, and workgroup.
- Initializes server defaults: starting state, min/max protocol, NTLMSSP auth, optional Kerberos mechanisms, and max inflight request credits.

Request handling:
- `queue_ksmbd_work()` initializes SMB protocol state for a connection, allocates work, transfers `conn->request_buf`, queues the work, increments request count, and updates activity.
- `__handle_ksmbd_work()` decrypts transform requests, allocates response buffers, initializes response headers, checks session/tree connection, dispatches commands, assigns credits, signs responses, updates preauth hash, encrypts responses when needed, releases tcon/session refs, and writes the response.
- `__process_request()` verifies SMB messages, validates command dispatch entries, checks signatures, invokes the command handler, increments command counters, and supports positive return values for chained/AndX-style dispatch.
- Connection termination deregisters sessions and destroys leases for that connection.

Control work:
- Server control work supports init and reset.
- Init resets proc counters and starts connection transport.
- Reset performs IPC soft reset, transport destroy, durable scavenger stop, config free/reinit, and returns to startup state.
- Work items hold a module reference until completion and serialize through `ctrl_lock`.

Sysfs class:
- Registers `ksmbd-control` with `stats`, `kill_server`, and `debug` attributes.
- `stats` exposes a versioned state/port/ipc activity line.
- `kill_server` accepts `hard` and performs synchronous reset.
- `debug` toggles debug categories or all categories.

Module lifecycle:
- Init registers class, initializes procfs and session proc entries, registers TCP callbacks, initializes config, work pools, file cache, IPC, global file table, inode hash, crypto, request workqueue, and connection workqueue.
- Exit sets shutdown state, tears down procfs, sysfs, workqueues, IPC, transports, crypto, file table, leases, file cache, and inode hash, using `rcu_barrier()` before destroying deferred connection workqueue state.

Role in this group:
- Uses `server.h` for global config.
- Uses `oplock.h` for lease cleanup.
- Uses `user_session.h` for session deregistration and ref release.
- Dispatch behavior depends on protocol ops/tables defined in `smb2ops.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/server.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/server.h -->
# File Research: sources/os/linux/linux/fs/smb/server/server.h

This header defines global ksmbd server state and configuration APIs.

Server states:
- Starting up
- Running
- Resetting
- Shutting down

Configuration:
- `struct ksmbd_server_config` stores global flags, state, signing policy, protocol range, TCP port, IPC timeout/activity, deadtime, fake filesystem capabilities, domain SID, auth mechanisms, connection/request limits, config strings, durable-handle task, and interface binding mode.
- Config string indexes cover NetBIOS name, server string, and workgroup.
- `server_conf` is exported globally.

Public helpers:
- Setters/getters for NetBIOS name, server string, and workgroup.
- `ksmbd_server_running()` checks for `SERVER_STATE_RUNNING` with `READ_ONCE`.
- `ksmbd_server_configurable()` permits configuration while state is before resetting.
- Control-work queue functions request server init or reset.

Role in this group:
- `server.c` owns the global object and lifecycle.
- `proc.c` reads this state for procfs stats.
- `smb2ops.c` reads flags/protocol capabilities while initializing per-connection SMB dialect operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/server.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smb2misc.c -->
# File Research: sources/os/linux/linux/fs/smb/server/smb2misc.c

This file validates SMB2 request headers, fixed structure sizes, variable data areas, message lengths, and credit charges.

Validation tables:
- `smb2_req_struct_sizes[]` maps SMB2 command indexes to expected request `StructureSize2`.
- `has_smb2_data_area[]` marks commands with variable data buffers.

Header and data-area validation:
- `check_smb2_hdr()` rejects server-to-client SMB2 packets received as requests.
- `smb2_get_data_area_len()` extracts command-specific buffer offset/length for session setup, tree connect, create, query/set info, read, write, query directory, lock, and ioctl.
- It rejects offsets over 4096 and total offset+length beyond `MAX_STREAM_PROT_LEN`.
- `smb2_calc_size()` computes the expected request length from SMB2 header, fixed body, and variable data area. It handles the SMB2 lock structure-size special case.

Credit validation:
- Request length helpers estimate credit needs for query info, set info, read, write, query directory, and ioctl.
- `smb2_validate_credit_charge()` compares client credit charge with calculated requirement, max credits, total granted credits, and outstanding credit limits under `credits_lock`.

Main entry:
- `ksmbd_smb2_check_message()` validates compound-message `NextCommand`, SMB2 header size, command range, fixed structure size, fixed body length, calculated message size, acceptable padding quirks, negotiate special case, and large-MTU credit charge.
- `smb2_negotiate_request()` forwards negotiation to common SMB negotiation handling.

Compatibility notes:
- Allows one-byte implied bcc difference.
- Allows final compound PDU padding to 8-byte alignment.
- Allows small padding differences up to 8 bytes for observed Linux/SMB 3.0.2 clients.
- SMB2 negotiate receives relaxed size handling and is validated deeper in negotiate handling.

Role in this group:
- Called by `server.c` through protocol ops before dispatch.
- Protects SMB2 command handlers and create-context parsing, including `oplock.c`’s `smb2_find_context_vals()`, from malformed packet lengths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smb2misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smb2ops.c -->
# File Research: sources/os/linux/linux/fs/smb/server/smb2ops.c

This file defines per-dialect SMB2/SMB3 server values, operations, command dispatch tables, and runtime tuners for I/O sizes and credits.

Dialect values:
- SMB 2.1 uses large MTU, SMB2 default I/O sizes, HMAC-SHA256 signing, and lease-size v1 create contexts.
- SMB 3.0 and 3.0.2 use SMB3 I/O sizes, AES-CMAC signing, encryption-capable ops, durable v2 context sizing, and optional directory leasing/encryption/multichannel/persistent handles depending on global flags and client capabilities.
- SMB 3.1.1 uses SMB3 sizes, AES-CMAC signing in this setup, SMB 3.1.1 signing/encryption key generation hooks, preauth session table initialization, and optional leasing/multichannel/persistent handles.

Operation tables:
- SMB2 ops include command extraction, request counters, response header/status setup, response allocation, credits, session/tcon lookup, signing checks, and signing response generation.
- SMB3 ops add SMB3 signing checks, SMB3 signing responses, signing/encryption key generation, transform-header detection, decrypt request, and encrypt response.
- SMB3.1.1 swaps in SMB3.1.1 key derivation functions.

Command dispatch:
- One command table maps SMB2 command indexes to handlers: negotiate, session setup, tree connect/disconnect, logoff, create, query info, query directory, close, echo, set info, read, write, flush, cancel, lock, ioctl, oplock break, and change notify.

Initialization functions:
- `init_smb2_1_server`, `init_smb3_0_server`, `init_smb3_02_server`, and `init_smb3_11_server` assign per-connection values, ops, command table, max command count, signing algorithm, and advertised capabilities.
- Capability advertisement depends on `server_conf.flags` and client capabilities.

Runtime tuners:
- `init_smb2_max_read_size`, `init_smb2_max_write_size`, and `init_smb2_max_trans_size` clamp values between SMB3 min/max I/O sizes and apply them to all dialect tables.
- `init_smb2_max_credits()` updates max credits for all dialect tables.

Role in this group:
- Supplies the protocol ops consumed by `server.c`.
- Uses `server.h` global configuration.
- Selects capabilities that affect `oplock.c` lease behavior, durable handles, multichannel, signing, encryption, and credit processing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smb2ops.c -->