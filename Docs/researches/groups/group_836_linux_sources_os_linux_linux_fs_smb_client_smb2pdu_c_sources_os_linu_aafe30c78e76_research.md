# Group Research: group_836_linux_sources_os_linux_linux_fs_smb_client_smb2pdu_c_sources_os_linu_aafe30c78e76

Scope: `Docs/research_subset_a.md`; all listed files under `sources/os/linux/linux/fs/smb/client/` were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2pdu.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb2pdu.c

## Purpose

`smb2pdu.c` is the main SMB2/SMB3 PDU construction and command execution implementation for the Linux CIFS/SMB client. It builds wire requests, sends them through CIFS transport helpers, parses responses, manages replay/reconnect semantics, and handles SMB2/3 operations including negotiation, session setup, tree connect, create/open, I/O, query/set info, directory enumeration, locking, oplock/lease acknowledgements, filesystem info, and SMB3 multichannel reconnect handling.

## Main Responsibilities

- Assemble SMB2 headers and fixed command bodies with correct `StructureSize`, `TreeId`, `SessionId`, credit requests, signing flags, encryption flags, DFS flags, and replay markers.
- Negotiate dialects and SMB3.1.1 negotiate contexts for preauth integrity, encryption, compression, POSIX extensions, signing capabilities, and netname.
- Establish sessions using Kerberos or raw NTLMSSP, generate/consume security blobs, and initialize signing/encryption keys through server ops.
- Connect/disconnect trees and validate negotiated SMB3 settings.
- Build `CREATE` requests with path handling, DFS path prefixes, lease/durable/persistent-handle/POSIX/security-descriptor/timewarp/query-id/EA contexts.
- Implement synchronous and asynchronous read/write paths, including SMB Direct RDMA offload descriptors when configured.
- Parse server responses with boundary checks for create contexts, ioctl output, query info, directory entries, POSIX info, and filesystem info.
- Drive reconnect and multichannel recovery, including session/channel rebind, tcon reconnect, persistent handle reopen, channel scaling, and server interface re-query.
- Report tracing/statistics for command starts, completions, failures, credits, reconnect references, and I/O progress.

## Key Control Flow

- `smb2_hdr_assemble()` creates the common SMB2 header and selects credit requests/signing flags.
- `smb2_plain_req_init()` runs reconnect handling, allocates a small or large CIFS buffer, fills the header, and updates per-command stats.
- `SMB2_negotiate()` builds dialect lists and SMB3.1.1 negotiate contexts, sends the negotiate request, validates the selected dialect, records server capabilities and sizes, decodes security blobs, decodes negotiate contexts, and allocates AEAD crypto state if encryption is available.
- `SMB2_sess_setup()` selects Kerberos or NTLMSSP and runs a small state machine through `sess_data->func`.
- `SMB2_tcon()` converts the UNC tree path to UTF-16, sends tree connect, records share type/flags/caps/TID, initializes copy-chunk limits, and optionally validates negotiation.
- `SMB2_open_init()` builds a create request and all optional create contexts; `SMB2_open()` sends it, stores file IDs, copies open metadata, and parses create contexts.
- `SMB2_ioctl()`, `query_info()`, `SMB2_query_directory()`, `send_set_info()`, `SMB2_flush()`, `__SMB2_close()`, `smb2_lockv()`, `SMB2_oplock_break()`, and `SMB2_lease_break()` follow the common pattern: initialize request, set transform/sign/replay flags, send via `cifs_send_recv()`, validate/copy response data, update stats/traces, free buffers, and replay retry if eligible.
- `smb2_async_readv()` and `smb2_async_writev()` create requests, adjust credits, optionally register SMB Direct memory regions, send via `cifs_call_async()`, and complete in callbacks that verify signatures, update byte counters, release credits, and notify netfs.
- `smb2_reconnect_server()` selects affected sessions/tcons/channels, serializes reconnects with the primary server reconnect mutex, reconnects sessions/tcons, renegotiates I/O size, reopens persistent handles, and reschedules when needed.

## Dependencies and Integration

- Depends heavily on CIFS core objects from `cifsglob.h`: `TCP_Server_Info`, `cifs_ses`, `cifs_tcon`, `cifs_fid`, `cifs_io_subrequest`, and `cifs_search_info`.
- Uses transport functions such as `cifs_send_recv()`, `cifs_call_async()`, reconnect helpers, credit helpers, and MID handling from the CIFS client.
- Uses `smb2proto.h` prototypes and SMB2/3 wire structures from SMB common headers.
- Uses `smbdirect.h` only when `CONFIG_CIFS_SMB_DIRECT` is enabled for RDMA memory registration and buffer descriptors.
- Integrates with Linux netfs through `netfs_read_subreq_terminated()`, `cifs_write_subrequest_terminated()`, and netfs trace flags.
- Integrates with tracing through `trace.h` tracepoints and with CIFS stats counters.

## Important Data Handling

- Uses little-endian conversions for all wire fields.
- Pads paths and create contexts to SMB2-required alignment.
- Uses `check_add_overflow()` / `check_sub_overflow()` and explicit response-boundary validation in several parsers.
- Keeps request buffers and sensitive auth buffers freed or zeroed through CIFS buffer release helpers and `kfree_sensitive()`.
- Treats file IDs as opaque wire values where appropriate.
- Carries SMB3 replay via `smb2_set_replay()` and bounded replay retry helpers.

## Risk Notes

- This file is security sensitive: it constructs and parses untrusted network PDUs, manages authentication material, signing/encryption policy, and reconnect state.
- Response parsing correctness depends on offset/length validation. The file contains many guards, but any new parser should follow `smb2_validate_iov()` or the create-context overflow pattern.
- Resource ownership is split across iovec elements, CIFS small/large buffers, response buffers, and caller-owned error iovs. New code must preserve the existing free conventions.
- Reconnect and multichannel code is concurrency sensitive, using multiple locks (`srv_lock`, `ses_lock`, `chan_lock`, `session_mutex`, reconnect mutex, global session lock). Lock ordering must be preserved.
- SMB Direct offload explicitly disables signed/encrypted offload; changing that requires coordinated signing/encryption transport work.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2pdu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2pdu.h -->
# File Research: sources/os/linux/linux/fs/smb/client/smb2pdu.h

## Purpose

`smb2pdu.h` defines SMB2/SMB3 PDU-adjacent constants and wire structures used by the CIFS SMB2 client implementation. It supplements the broader SMB2 structure definitions with create-context, RDMA transform, ioctl/fsctl, POSIX extension, WSL xattr, symlink error, and share redirect layouts.

## Main Contents

- Header and transform size constants: `SMB2_TRANSFORM_HEADER_SIZE`, `MAX_SMB2_HDR_SIZE`, and `SMB2_READWRITE_PDU_HEADER_SIZE`.
- SMB Direct/RDMA transform structures and transform type constants.
- Symlink and SMB3.1.1 error context response layouts.
- Share redirect error context structures including target IP address records.
- Create request iovec sizing and max create response sizing.
- Lease caching flags.
- Create context structures for timewarp, query-on-disk-id, and security descriptor contexts.
- FSCTL request/response structs for retrieval pointers, DFS referral, network resiliency, and compression.
- SMB2 query info structures for EA, reparse-point, file-id, and file-id extended directory information.
- POSIX create response and SMB3 POSIX directory info structures, plus parsed helper representation.
- WSL EA/xattr names and size constants.

## Integration

- Included by `smb2pdu.c` and other SMB2 client files that need these wire layouts.
- Depends on `cifsacl.h` for SID/security-descriptor-related types.
- Exposes `smb2_padding[7]`, used by request free paths to avoid freeing static padding as dynamic iovec memory.
- The `SMB2_CREATE_IOV_SIZE`, `SMB2_IOCTL_IOV_SIZE`, and `SMB2_QUERY_DIRECTORY_IOV_SIZE` constants directly constrain the request-building code in `smb2pdu.c`.

## Risk Notes

- All wire structs are packed and endian-sensitive. Field additions or reordering would break protocol layout.
- Flexible arrays and variable-length trailing fields require callers to validate lengths before access.
- The create iovec size must remain in sync with every optional context that `SMB2_open_init()` can append.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2pdu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2proto.h -->
# File Research: sources/os/linux/linux/fs/smb/client/smb2proto.h

## Purpose

`smb2proto.h` is the primary exported prototype header for the CIFS SMB2/SMB3 client implementation. It declares error mapping, PDU validation, signing, request setup, reconnect, path operations, core SMB2 command workers, and helper parsers used across the SMB client.

## Main API Areas

- Error and message handling: `map_smb2_to_linux_error()`, `smb2_check_message()`, `smb2_calc_size()`, `smb2_get_data_area_len()`.
- Path conversion and path-level operations: UTF-16 conversion, query path info, mkdir/rmdir/unlink/rename/hardlink/symlink helpers, file size setting, reparse point handling.
- Signing and transport setup: `smb2_verify_signature()`, `smb2_check_receive()`, `smb2_setup_request()`, `smb2_setup_async_request()`.
- Session/tcon lookup and reconnect: `smb2_find_smb_tcon()`, `smb2_reconnect_server()`, replay helpers.
- Core SMB2 command workers: negotiate, session setup, logoff, tree connect/disconnect, open, ioctl, notify, close, flush, query info, read/write, echo, query directory, set info, set EOF/ACL/EA/compression, oplock and lease break, filesystem info, lock.
- Request init/free helpers for open, ioctl, close, flush, query info, query directory, and set info.
- Validation and parsing helpers: create-context parsing, iov validation/copy, filesystem stat copy, POSIX info parsing, SID sizing.
- SMB3 crypto: `smb3_crypto_aead_allocate()` and preauth update.

## Integration

- Includes `cached_dir.h` because several higher-level path operations interact with cached directory state.
- Used by SMB2 PDU construction (`smb2pdu.c`), transport signing (`smb2transport.c`), reconnect paths, inode/path helpers, and operation tables.
- Provides the public surface that dialect operation tables can bind to.

## Risk Notes

- This header exposes a broad internal API; signature changes can have a large blast radius across the CIFS client.
- Several APIs transfer buffer ownership through `struct kvec`, `char **`, and `int *buftype`; callers must follow the documented/freeing conventions in the implementation.
- The header mixes high-level VFS path helpers and low-level PDU helpers, so include dependencies should be changed cautiously.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2transport.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb2transport.c

## Purpose

`smb2transport.c` implements SMB2/SMB3 transport-adjacent security and request setup logic: signing key lookup, SMB2 HMAC-SHA256 signing, SMB3 AES-CMAC signing, SMB3 key derivation, signature verification, MID allocation, request sequencing, and AEAD crypto transform allocation.

## Main Responsibilities

- Locate session and channel signing keys for SMB2 and SMB3 multichannel.
- Derive SMB3 signing, encryption, and decryption keys for SMB3.0 and SMB3.1.1.
- Sign outgoing SMB2/SMB3 requests when required.
- Verify incoming SMB2/SMB3 response signatures.
- Allocate and initialize MID queue entries, assign message IDs according to credit charge, and add requests to pending MID queues.
- Set up synchronous and asynchronous SMB2 requests before send.
- Allocate AEAD crypto transforms for SMB3 encryption/decryption.

## Key Control Flow

- `smb3_get_sign_key()` finds a session by ID on the primary server, handles channel binding, and selects either the master signing key or per-channel signing key.
- `smb2_get_sign_key()` locates the SMB2 session key from `ses->auth_key.response`.
- `smb2_calc_signature()` signs SMB2 requests using HMAC-SHA256 over the request data.
- `generate_key()` implements the SMB3 KDF-style HMAC derivation using labels, contexts, and 128/256-bit output length selectors.
- `generate_smb30signingkey()` uses SMB3.0 labels/contexts; `generate_smb311signingkey()` uses SMB3.1.1 preauth hash contexts.
- `smb3_calc_signature()` uses AES-CMAC for SMB3 dialects and falls back to SMB2 HMAC for SMB2.1 and earlier.
- `smb2_sign_rqst()` enforces signing only when the request is marked signed, skips signing during negotiate, and uses the dummy early-session signature where required.
- `smb2_verify_signature()` skips commands that are not verified, recalculates the expected signature, and compares with `crypto_memneq()`.
- `smb2_setup_request()` assigns a message ID, allocates and queues a MID, signs the request, and rolls back on failure.
- `smb2_setup_async_request()` performs a similar setup for async requests without session-status filtering.
- `smb3_crypto_aead_allocate()` allocates `gcm(aes)` or `ccm(aes)` transforms depending on negotiated cipher type.

## Dependencies and Integration

- Uses Linux crypto helpers for AEAD, AES-CMAC, SHA-256 HMAC, and constant-time comparison.
- Works with CIFS global session/server lists protected by `cifs_tcp_ses_lock` plus per-session and per-channel locks.
- Integrates with `mid_q_entry`, `pending_mid_q`, credit charge, sequence numbers, and CIFS request send paths.
- Called by send/receive paths declared in `smb2proto.h` and by dialect ops for SMB3 key generation.

## Risk Notes

- Key selection is multichannel-sensitive. Binding a new channel must not overwrite master session keys incorrectly.
- Signing intentionally includes the RFC1002 length prefix only when present as a separate iovec; request layout changes must preserve this behavior.
- Message ID assignment and rollback must stay paired with MID allocation failures to avoid sequence corruption.
- Debug key dumping is gated by `CONFIG_CIFS_DEBUG_DUMP_KEYS` and should remain restricted.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb2transport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smbdirect.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smbdirect.c

## Purpose

`smbdirect.c` implements the CIFS client’s SMB Direct transport adapter when `CONFIG_CIFS_SMB_DIRECT` is enabled. It wraps the kernel `linux/smbdirect.h` socket API to create, reconnect, destroy, send, receive, and register memory for RDMA-backed SMB transport.

## Main Responsibilities

- Define default SMB Direct and RDMA tuning parameters exposed as module parameters or globals.
- Configure SMB Direct logging classes and bridge SMB Direct logging into CIFS debug output.
- Create SMB Direct connections using port 5445 first, then port 445 as fallback.
- Set initial socket parameters including credit limits, send/receive sizes, fragmented receive size, FRMR depth, keepalive intervals, and RDMA connection timeouts.
- Reconnect and destroy SMB Direct connections associated with `TCP_Server_Info`.
- Send one or more SMB requests over SMB Direct, fragmenting metadata and payload iterators according to negotiated send size.
- Receive data through the SMB Direct socket into upper-layer message iterators.
- Register/deregister memory regions for RDMA read/write offload and fill SMB2 RDMA buffer descriptors.
- Emit debug/proc output for RDMA transport state.

## Key Control Flow

- `_smbd_get_connection()` allocates `struct smbd_connection`, creates a kernel SMB Direct socket, sets initial parameters and kernel settings, patches the destination port, connects synchronously, and returns the connection.
- `smbd_get_connection()` first tries SMB Direct port 5445, then port 445, then records the negotiated RDMA read/write threshold.
- `smbd_reconnect()` destroys any existing transport and creates a new connection for the server destination address.
- `smbd_send()` computes total payload length across request arrays, rejects payloads exceeding `max_fragmented_send_size`, sends all metadata iovecs and data iterators in a single batch, flushes the batch, and waits for pending sends to drain.
- `smbd_register_mr()` and `smbd_deregister_mr()` wrap lower SMB Direct memory-region APIs used by `smb2pdu.c` read/write offload paths.

## Dependencies and Integration

- Includes `smbdirect.h`, `cifsproto.h`, and `smb2proto.h`.
- Uses the exported SMB Direct namespace via `MODULE_IMPORT_NS("SMBDIRECT")`.
- Depends on `smb_rqst_len()` to compute upper-layer request lengths.
- Integrates with `TCP_Server_Info->smbd_conn`, `server->rdma`, and `server->rdma_readwrite_threshold`.
- Used by SMB2 read/write request construction for RDMA buffer descriptors and by the transport layer for send/receive.

## Risk Notes

- `smbd_send()` mutates request iterators while sending; callers must not assume iterators are reusable afterward without reset.
- Payload size checks depend on negotiated SMB Direct parameters.
- Destination port is written directly into the supplied socket address before connect.
- Connection teardown assumes no upper-layer user remains; lifetime must be coordinated by CIFS server/session management.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smbdirect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smbdirect.h -->
# File Research: sources/os/linux/linux/fs/smb/client/smbdirect.h

## Purpose

`smbdirect.h` declares the CIFS SMB Direct transport interface and provides no-op fallback stubs when SMB Direct support is not compiled.

## Main Contents

- `cifs_rdma_enabled(server)` macro, either `server->rdma` or constant `0`.
- Extern declarations for SMB Direct tunables such as credit limits, send/receive sizes, keepalive interval, FRMR depth, and RDMA threshold.
- `struct smbd_connection`, which currently wraps a `struct smbdirect_socket *`.
- Declarations for connection lifecycle: `smbd_get_connection()`, `smbd_reconnect()`, `smbd_destroy()`.
- Declarations for send/receive: `smbd_recv()` and `smbd_send()`.
- Declarations for RDMA memory registration and buffer descriptor filling.
- Debug output declaration: `smbd_debug_proc_show()`.
- Fallback stubs returning `NULL` or `-1` when `CONFIG_CIFS_SMB_DIRECT` is disabled.

## Integration

- Included by `smb2pdu.c` and transport/session code that can optionally use RDMA.
- Pulls in `linux/smbdirect.h` only when SMB Direct is enabled.
- Allows most call sites to compile without conditional declarations, while implementation code still uses `#ifdef CONFIG_CIFS_SMB_DIRECT` for offload-only logic.

## Risk Notes

- Fallback stubs return generic `-1` rather than a specific errno, so callers should normally gate behavior through `cifs_rdma_enabled()` or config checks.
- The public structure is intentionally small; expanding it changes the abstraction boundary between CIFS and the SMB Direct socket layer.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smbdirect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smbencrypt.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smbencrypt.c

## Purpose

`smbencrypt.c` provides the legacy NT password hash helper used by CIFS authentication code. Its active exported function, `E_md4hash()`, converts a password to NT Unicode and computes the MD4 hash.

## Main Behavior

- Defines small byte-order helper macros copied locally to avoid include conflicts.
- `mdfour()` wraps the CIFS MD4 implementation: initialize, update with input bytes, finalize into a 16-byte digest, and log failures.
- `E_md4hash()` converts a password to UTF-16 with `cifs_strtoUTF16()`, limits input to 128 characters, hashes the UTF-16 bytes with MD4, then wipes the stack password buffer with `memzero_explicit()`.

## Dependencies and Integration

- Includes CIFS Unicode, global, debug, and protocol headers.
- Uses `../common/md4.h` rather than the generic crypto API directly.
- Used by authentication paths that need the NT hash form of a password.

## Risk Notes

- MD4/NT hash handling is legacy and cryptographically weak, but required for compatibility with older SMB authentication mechanisms.
- The password conversion buffer is stack allocated and explicitly cleared; future changes should preserve sensitive-data wiping.
- The hash input length is based on UTF-16 character conversion count, not original byte length.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smbencrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smberr.h -->
# File Research: sources/os/linux/linux/fs/smb/client/smberr.h

## Purpose

`smberr.h` defines legacy SMB/CIFS error classes and error-code constants, with comments indicating intended POSIX errno mappings. It supports mapping server SMB-class errors to Linux errors.

## Main Contents

- `struct smb_to_posix_error`, pairing an SMB error code with a POSIX code.
- SMB error classes: `SUCCESS`, `ERRDOS`, `ERRSRV`, `ERRHRD`, and `ERRCMD`.
- `ERRDOS` constants for filesystem and DOS-style failures such as invalid function, file not found, bad path, too many open files, access denied, bad file ID, no memory, invalid drive, cross-device rename, no more files, write protected, share conflict, lock conflict, unsupported operation, no such share, file exists, disk full, invalid name, directory not empty, quota, not-a-link, symlink, and too many links.
- `ERRSRV` constants for server/session/tree/authentication failures such as general server error, bad password, DFS referral needed, invalid TID, invalid network name, invalid device, print queue errors, bad command, paused server, timeout, too many UIDs, bad UID, notify enum dir, account expired, bad client, bad logon time, and password expired.

## Integration

- Consumed by SMB/CIFS error mapping code to translate protocol-specific status to Linux errno.
- Comments are structured so mapping tables can be generated or verified from the errno annotations.
- Complements SMB2/NTSTATUS mappings used elsewhere; this header is primarily for classic SMB error classes.

## Risk Notes

- These constants are protocol ABI and should not be renumbered.
- The POSIX mapping comments are semantically important for generated tables; editing comments can affect tooling if parsers rely on them.
- Some constants are internal passthrough values, not wire values, and should not be emitted as server SMB errors.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smberr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/trace.c -->
# File Research: sources/os/linux/linux/fs/smb/client/trace.c

## Purpose

`trace.c` is the compilation unit that instantiates CIFS/SMB client tracepoints.

## Main Behavior

- Includes `cifsglob.h` and `cifs_spnego.h` so tracepoint definitions have required type context.
- Defines `CREATE_TRACE_POINTS` before including `trace.h`, causing tracepoint storage and definitions to be emitted exactly once.

## Integration

- Supports tracepoints used throughout the SMB client, including many calls from `smb2pdu.c` and `smb2transport.c`.
- Must remain a single-definition translation unit for the tracepoint system.

## Risk Notes

- Moving `CREATE_TRACE_POINTS` into multiple files would cause duplicate tracepoint definitions.
- Removing required includes can break tracepoint macro expansion if trace payload types become incomplete.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/trace.c -->