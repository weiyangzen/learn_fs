# Group Research: group_1078_linux_stable_sources_os_linux_linux_stable_fs_smb_client_smb2pdu_c__98a094d93814

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2pdu.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2pdu.c

## Summary
Implements the SMB2/SMB3 protocol worker layer for the Linux CIFS client. It constructs and sends most SMB2 PDUs, handles reconnect/replay gating, negotiates dialects and negotiate contexts, performs session setup and tree connect/disconnect, opens and closes file handles, sends query/set/IOCTL/lock/read/write/flush/directory/lease/oplock requests, parses create and POSIX contexts, and bridges SMB3 features such as encryption, multichannel, persistent handles, compression, leases, POSIX extensions, and SMB Direct read/write offload.

## Main Responsibilities
- Assemble SMB2 headers, fixed command bodies, variable buffers, and create/query contexts with the protocol-required alignment and length fields.
- Decide when SMB3 encryption is required from session flags, share flags, mount `seal`, global security flags, and server capabilities.
- Coordinate reconnects before sending handle-independent commands, including session setup, tree reconnect, multichannel rescaling, interface queries, and persistent-handle reopen scheduling.
- Negotiate SMB2/SMB3 dialects, SMB 3.1.1 preauth/encryption/signing/compression/POSIX contexts, server capabilities, max I/O sizes, security mode, and AEAD crypto setup.
- Run session setup using Kerberos upcall or raw NTLMSSP challenge/authenticate flows, including channel binding behavior.
- Connect and disconnect trees, validate negotiate info for SMB3 dialects before 3.1.1, and initialize share attributes such as capabilities, encryption, copychunk defaults, and isolated transport.
- Build `CREATE` requests with path conversion, DFS prefixing, leases, durable/persistent handle contexts, POSIX mode contexts, snapshot timewarp, security descriptor mode/owner contexts, query-id contexts, and EA contexts.
- Parse `CREATE` response contexts for leases, query-on-disk IDs, and SMB3 POSIX response data.
- Provide synchronous and asynchronous read/write paths, including netfs completion callbacks, credit accounting, replay decisions, signature verification, stats, EOF handling, compression flags, and optional SMB Direct memory registration.
- Implement `IOCTL`, `QUERY_INFO`, `SET_INFO`, `QUERY_DIRECTORY`, `CHANGE_NOTIFY`, `LOCK`, `FLUSH`, `CLOSE`, `ECHO`, `OPLOCK_BREAK`, `LEASE_BREAK`, and filesystem-info helpers.

## Key Interfaces
- Core negotiation/session/tree APIs: `SMB2_negotiate()`, `smb3_validate_negotiate()`, `smb2_select_sectype()`, `SMB2_sess_setup()`, `SMB2_logoff()`, `SMB2_tcon()`, and `SMB2_tdis()`.
- Reconnect and channel handling: `smb3_update_ses_channels()`, `smb2_reconnect_server()`, and the internal `smb2_reconnect()` path.
- Open/create APIs: `SMB2_open_init()`, `SMB2_open()`, `SMB2_open_free()`, `smb311_posix_mkdir()`, `smb2_parse_contexts()`, `posix_info_sid_size()`, and `posix_info_parse()`.
- Request families: `SMB2_ioctl[_init/_free]()`, `SMB2_close[_init/_free]()`, `SMB2_flush[_init/_free]()`, `SMB2_query_info[_init/_free]()`, `SMB2_query_acl()`, `SMB2_get_srv_num()`, `SMB2_query_directory[_init/_free]()`, `SMB2_set_info_init()`, `SMB2_set_eof()`, `SMB2_set_acl()`, `SMB2_set_ea()`, `SMB2_QFS_attr()`, and `SMB311_posix_qfs_info()`.
- I/O APIs: `smb2_async_readv()`, `SMB2_read()`, `smb2_async_writev()`, and `SMB2_write()`.
- Lock and cache-control APIs: `SMB2_lock()`, `smb2_lockv()`, `SMB2_oplock_break()`, `SMB2_lease_break()`, `SMB2_change_notify()`, `SMB2_echo()`, and `SMB2_set_compression()`.
- Validation helpers: `smb2_validate_iov()`, `smb2_validate_and_copy_iov()`, `smb2_copy_fs_info_to_kstatfs()`, and SMB3 encryption predicate `smb3_encryption_required()`.

## Control Flow And Behavior
Requests are normally built through `smb2_plain_req_init()`, which first runs reconnect gating, allocates either a small or large CIFS buffer based on command type, fills the SMB2 header, initializes structure size, and increments per-tcon SMB2 command stats. IOCTL initialization can skip reconnect for validate-negotiate and reconnect-time interface queries to avoid recursion.

Reconnect handling rejects sends while tcons or sessions are exiting, waits for transport reconnect, serializes session reconnect under `session_mutex`, renegotiates dialect/session state, handles servers that lose multichannel support, tree-connects again when needed, marks open files invalid, schedules persistent-handle reopen, queries interfaces, adjusts channels, and returns `-EAGAIN` for handle-based commands that the caller must retry with a known-good handle.

Negotiation builds dialect lists for `vers=default`, `vers=3`, and explicit dialects. SMB 3.1.1 adds negotiate contexts for preauth integrity, encryption, netname, POSIX extension availability, optional compression, and optional signing capabilities. The response is checked against the requested dialect set, security mode and capability state are recorded, signing is enabled if required, GSS/NTLMSSP blobs are decoded, 3.1.1 contexts are parsed, and AEAD crypto transforms are allocated when encryption is negotiated.

Session setup is state-machine based. Raw NTLMSSP allocates an NTLMSSP context, sends negotiate, decodes challenge, sends authenticate, stores the session id and flags unless this is channel binding, and generates signing/encryption keys. Kerberos uses `cifs_get_spnego_key()`, validates the upcall format, pads short GSS session keys to the SMB2 minimum, sends the security blob, and establishes session keys. Sensitive buffers are explicitly zeroed or freed through sensitive cleanup paths.

Create/open request construction is the densest part of the file. Paths are UTF-16 converted, optionally prefixed with tree name for DFS operations, padded to 8-byte alignment, and followed by zero or more create contexts. Lease contexts request file or directory leases; durable contexts support both legacy durable handles and SMB3 persistent handle v2 reconnect/create GUIDs; POSIX contexts carry mode; security descriptor contexts encode mode/owner through special SIDs; query-id contexts request stable inode identifiers; EA contexts are spliced from caller-provided vectors. Create response parsing validates context bounds before extracting lease state, disk id, or POSIX owner/group/mode data.

Asynchronous reads and writes integrate with netfs subrequests. They choose channels, build request PDUs, request or adjust credits based on I/O size, optionally set SMB Direct channel descriptors and memory registrations, and call `cifs_call_async()`. Completion callbacks release credits, deregister RDMA memory, verify signatures for signed unencrypted reads, update stats and task I/O counters, set netfs retry/progress/EOF flags, and terminate subrequests. Synchronous read/write variants share the same PDU fields but use `cifs_send_recv()`.

Directory querying validates output offsets and lengths, parses entry chains defensively through `num_entries()`, accounts for SMB POSIX directory entries with variable owner/group SID and name tails, transfers ownership of response buffers into `cifs_search_info`, and handles `STATUS_NO_MORE_FILES` as end-of-search.

## State And Synchronization
The file coordinates with session and server locks in reconnect paths (`session_mutex`, `ses_lock`, `chan_lock`, `srv_lock`, `cifs_tcp_ses_lock`, and reconnect mutexes), with per-tcon counters and flags for remote opens, reconnect, and persistent handle reopen, and with netfs subrequest flags for I/O progress and retry. Request buffers have strict ownership rules: init helpers allocate, free helpers release, and error paths must avoid double-freeing response buffers that are handed to callers.

## Cross-File Interactions
This file is the concrete SMB2/SMB3 implementation behind function pointers installed by dialect tables in `smb2ops.c` and related global value tables. It depends on `smb2transport.c` for MID setup, signing, verification, key derivation, and AEAD allocation; on `connect.c` for session/tree/reconnect primitives and channel selection; on `file.c` for async read/write callers and handle lifetime; on `dir.c`/`inode.c`/`readdir.c` for path, metadata, and directory operations; on `smbdirect.c` for RDMA transport and memory registration; and on `compress.c` for write compression eligibility.

## Risks
The highest-risk areas are replay/reconnect behavior around handle-based requests, multichannel channel-key and reconnect ordering, create-context length/alignment handling, persistent-handle reconnect semantics, async read/write credit accounting, RDMA memory-registration lifetime, encryption/signing interaction, and parsing server-controlled variable-length contexts or directory entries. Many paths differ by dialect, server capabilities, mount flags, POSIX extensions, DFS, SMB Direct, encryption, compression, and fscache/netfs behavior, so regressions can be highly configuration-specific.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2pdu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2pdu.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2pdu.h

## Summary
Defines SMB2/SMB3 PDU-adjacent structures, constants, vector-count limits, create-context payloads, IOCTL payloads, POSIX extension directory payloads, and WSL EA constants used by the SMB2 worker implementation.

## Main Responsibilities
- Define SMB2 transform and RDMA transform header sizes and structures.
- Describe SMB2 symlink and SMB 3.1.1 error-context response payloads, including share-redirect address records.
- Set request/response sizing constants for create and read/write PDUs.
- Define lease-state bits and fixed create-context payload structures for timewarp, query-on-disk-id, and security descriptor create contexts.
- Define FSCTL request/response structures for retrieval pointers, DFS referral request payloads, network resiliency, and compression.
- Define maximum iovec counts for `CREATE`, `IOCTL`, and query-directory request construction.
- Define packed SMB2 file information structures for EA, reparse point, file-id, and file-id extended directory responses.
- Define SMB3 POSIX create response and query-directory entry structures, plus a parsed helper structure for variable-length POSIX entry data.
- Define WSL EA names and expected EA response-size bounds.

## Key Types And Constants
- `SMB2_TRANSFORM_HEADER_SIZE`, `MAX_SMB2_HDR_SIZE`, and `SMB2_READWRITE_PDU_HEADER_SIZE` establish transport/protocol header sizing assumptions.
- `struct smb2_rdma_transform` and `struct smb2_rdma_crypto_transform` describe RDMA transform metadata.
- `struct smb2_symlink_err_rsp`, `struct smb2_error_context_rsp`, and `struct share_redirect_error_context_rsp` model special error response payloads.
- `SMB2_CREATE_IOV_SIZE`, `MAX_SMB2_CREATE_RESPONSE_SIZE`, `SMB2_IOCTL_IOV_SIZE`, and `SMB2_QUERY_DIRECTORY_IOV_SIZE` bound stack iovec arrays used in `smb2pdu.c`.
- `struct crt_twarp_ctxt`, `struct crt_query_id_ctxt`, and `struct crt_sd_ctxt` are create-context wrappers.
- `struct smb2_posix_info` and `struct smb2_posix_info_parsed` support SMB3 POSIX directory parsing.

## Important Behavior
All wire structures are packed and intentionally mirror MS-SMB2/MS-FSCC/SMB3 POSIX extension layouts. Several structures contain flexible array members or comments describing trailing data, so callers must validate offsets and lengths before dereferencing. The create iovec limit is tied directly to the optional context set assembled in `SMB2_open_init()`.

## Cross-File Interactions
`smb2pdu.c` consumes nearly every definition in this header for request construction and response parsing. Directory code and reparse/symlink handling use the file-id, POSIX, and symlink response structures through public helpers declared in `smb2proto.h`.

## Risks
Wire layout drift is the primary risk. Changing packed structures, vector-count limits, alignment assumptions, or WSL/SMB3 POSIX size constants requires coordinated updates to builders and validators in `smb2pdu.c`; otherwise malformed requests, buffer overruns, or rejected server responses can result.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2pdu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2proto.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2proto.h

## Summary
Declares the internal SMB2/SMB3 client API used across the CIFS client. It exposes error mapping, message validation, signing/receive helpers, request setup, oplock and lease handling, path/reparse helpers, SMB2 worker functions, replay helpers, and protocol-specific metadata operations.

## Main Responsibilities
- Provide prototypes for SMB2 status-to-Linux-error mapping and optional KUnit-test access to the error map.
- Declare message size/data-area validation and UTF-16 path conversion helpers.
- Declare signing, receive checking, MID setup, async setup, tcon lookup, lease-state parsing, and oplock-break validation helpers.
- Expose path-info, reparse-point, symlink, mkdir/rmdir/unlink/rename/hardlink, and pending-delete helpers implemented outside `smb2pdu.c`.
- Declare all core SMB2 worker functions for negotiate, session setup, logoff, tcon/tdis, open, close, IOCTL, query, set, read/write, directory, locks, lease/oplock breaks, filesystem info, and validate-negotiate.
- Declare replay, compounding, preauth hash, encryption predicate, and response-buffer validation helpers.
- Expose SMB3 POSIX parsing helpers for directory and create-response consumers.

## Key Interfaces
Important public surfaces include `SMB2_negotiate()`, `SMB2_sess_setup()`, `SMB2_tcon()`, `SMB2_open()`, `SMB2_ioctl()`, `SMB2_query_info()`, `smb2_async_readv()`, `smb2_async_writev()`, `SMB2_query_directory()`, `SMB2_set_eof()`, `SMB2_lock()`, `SMB2_lease_break()`, `smb3_validate_negotiate()`, `smb2_verify_signature()`, `smb2_check_receive()`, `smb2_setup_request()`, `smb2_setup_async_request()`, and `smb2_reconnect_server()`.

## Important Behavior
This header is the cross-module contract for SMB2 dialect implementations. Many declarations have paired init/free forms so callers can build compound requests or reuse the same PDU construction helpers without sending immediately. It also separates protocol-neutral VFS operations from SMB2-specific implementation details, allowing dialect operation tables to point at these functions.

## Cross-File Interactions
Implemented functions are distributed across `smb2pdu.c`, `smb2transport.c`, `smb2misc.c`, `smb2ops.c`, `smb2maperror.c`, `smb2inode.c`, and adjacent CIFS client modules. Callers include connection setup, VFS file and directory operations, inode metadata paths, readdir, DFS/reparse handling, and netfs I/O.

## Risks
Prototype changes have broad blast radius because this is the primary SMB2 internal API. Init/free pair contracts and buffer ownership expectations are especially important; mismatches can leak CIFS buffers, free caller-owned response vectors, or break compound request construction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2transport.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2transport.c

## Summary
Implements SMB2/SMB3 transport-layer signing, signature verification, key derivation, MID allocation/setup, session/tcon lookup by SMB identifiers, receive checking, and AEAD crypto allocation. It is the cryptographic and request-tracking support layer under the SMB2 PDU workers.

## Main Responsibilities
- Find session signing keys for SMB2 and per-channel SMB3 signing keys for multichannel connections.
- Look up non-exiting sessions and tree connections by SessionId and TreeId from incoming SMB2 headers.
- Compute SMB2 HMAC-SHA256 signatures and SMB3 AES-CMAC signatures over request vectors.
- Generate SMB3 signing, encryption, and decryption keys using dialect-specific labels and contexts.
- Support SMB3.0 key derivation and SMB3.1.1 preauth-hash-based key derivation, including AES-256 full-session-key handling.
- Sign outgoing requests when `SMB2_FLAGS_SIGNED` is set and session state permits signing.
- Verify incoming signed responses unless the command or connection state exempts verification.
- Allocate and initialize MID queue entries, assign message ids, charge multi-credit requests, and insert synchronous requests into pending MID queues.
- Set up synchronous and asynchronous requests with message ids and signatures.
- Check received responses by verifying signatures and mapping SMB status codes to Linux errors.
- Allocate kernel AEAD transforms for SMB3 encryption/decryption based on negotiated cipher type.

## Key Interfaces
- Lookup helpers: `smb2_find_smb_tcon()` and internal session/tcon lookup routines.
- Signing and verification: `smb2_verify_signature()`, internal `smb2_calc_signature()`, `smb3_calc_signature()`, and `smb2_sign_rqst()`.
- Key derivation: `generate_smb30signingkey()` and `generate_smb311signingkey()`.
- Request setup: `smb2_setup_request()` and `smb2_setup_async_request()`.
- Receive/error handling: `smb2_check_receive()`.
- Crypto allocation: `smb3_crypto_aead_allocate()`.

## Control Flow And Behavior
Signing key lookup differs by dialect. SMB2 uses the session `auth_key.response`; SMB3 uses the session or channel signing key, and binding a new channel uses the master session key until that channel key is established. Key derivation writes a primary session signing key, per-channel signing key, and encryption/decryption keys for established sessions; channel binding only updates the new channel signing key.

Outgoing setup assigns a message id, creates a MID, queues it when synchronous, and signs the request. If MID allocation or signing fails, the message id is reverted and the MID is deleted or released. Signature calculation strips an RFC1002 length vector when present by hashing it first and then signing the remaining SMB request data in the form expected by shared CIFS signing helpers.

Incoming verification saves the server signature, zeroes the header signature, recomputes it using the negotiated key and dialect algorithm, and compares with `crypto_memneq()`. Negotiate, session setup, oplock break, ignored-signature connections, and pre-session-established responses are skipped.

## State And Synchronization
Session and channel lookup is protected with `cifs_tcp_ses_lock`, `ses_lock`, and `chan_lock`; MID insertion uses `mid_queue_lock`; key derivation touches session/channel key slots under the session/channel locks where required. Request setup assumes the caller holds the appropriate server mutex according to CIFS send-path conventions.

## Cross-File Interactions
`smb2pdu.c` calls this file for signing-key generation after session setup, response signature verification in async I/O, AEAD allocation after negotiation, and MID setup indirectly through the send path. `connect.c` and demultiplex code use `smb2_find_smb_tcon()` to route unsolicited and response-related events such as oplock/lease breaks.

## Risks
Multichannel key selection and binding state are subtle: using the wrong key breaks signing or weakens channel isolation. Message-id rollback must stay aligned with credit charge. Signature calculation must include exactly the same byte stream that the server signs, including RFC1002 handling and encrypted/decrypted response state. AEAD allocation failure handling must avoid leaving one transform allocated without the other.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2transport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smbdirect.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smbdirect.c

## Summary
Implements the CIFS SMB Direct transport adapter for RDMA-enabled SMB connections. In this version it delegates most low-level RDMA connection, send/receive, memory registration, and debug display mechanics to the kernel `smbdirect` socket API while preserving CIFS module parameters, logging classes, connection lifecycle, and upper-layer send/receive wrappers.

## Main Responsibilities
- Define SMB Direct default tunables for credits, send/receive sizes, fragmented receive size, keepalive interval, FRMR depth, and RDMA read/write threshold.
- Expose module parameters for SMB Direct logging class and level.
- Bridge CIFS logging requests to `smbdirect_socket` logging callbacks.
- Create SMB Direct connections on port 5445 first and then fall back to port 445 with port-family constraints for iWARP versus InfiniBand/RoCE behavior.
- Configure initial `smbdirect_socket_parameters`, kernel polling settings, connect timeouts, keepalive timeouts, and RDMA resource counts.
- Destroy and reconnect SMB Direct sessions for `TCP_Server_Info`.
- Send CIFS SMB request arrays as SMB Direct payloads, including metadata iovecs and optional data iterators.
- Receive data from the SMB Direct reassembly queue into caller-provided message iterators.
- Register, describe, and deregister memory regions for SMB Direct RDMA read/write offload.
- Emit SMB Direct debug information into CIFS proc/debug output.

## Key Interfaces
- Connection lifecycle: `smbd_get_connection()`, `smbd_reconnect()`, `smbd_destroy()`, and internal `_smbd_get_connection()`.
- Transport I/O: `smbd_send()` and `smbd_recv()`.
- RDMA memory registration: `smbd_register_mr()`, `smbd_mr_fill_buffer_descriptor()`, and `smbd_deregister_mr()`.
- Parameter/debug helpers: `smbd_get_parameters()` and `smbd_debug_proc_show()`.

## Control Flow And Behavior
Connection creation builds an initial parameter block, creates a kernel SMB Direct socket in the CIFS network namespace, installs logging hooks, configures transport parameters and kernel settings, writes the requested port into the destination address, and attempts a synchronous RDMA connect. `smbd_get_connection()` first tries the dedicated SMB Direct port and then ordinary SMB port; after success it clamps the server RDMA read/write threshold to the negotiated maximum fragmented send size.

`smbd_send()` computes the total SMB request length across all request fragments, validates it against the negotiated fragmented send maximum, initializes a send batch, posts each request's metadata kvecs and then its data iterator in chunks that respect the negotiated send size, flushes the batch, waits for pending sends to drain, and returns retryable errors when completion waiting fails.

Memory registration wrappers verify connection state and then call the SMB Direct socket API. These are used by `smb2pdu.c` read/write paths to expose client memory to the server through SMB2 RDMA channel descriptors.

## State And Synchronization
The CIFS-visible state is mainly `server->smbd_conn`, `server->rdma`, and `server->rdma_readwrite_threshold`; deeper queue pair, credit, receive reassembly, and memory registration state is owned by the `smbdirect_socket` layer. Destruction releases the socket before freeing the CIFS wrapper.

## Cross-File Interactions
`connect.c` creates or reconnects SMB Direct sessions when RDMA transport is requested. `smb2pdu.c` uses memory-registration helpers for RDMA offloaded reads and writes. `smbdirect.h` provides stubs when `CONFIG_CIFS_SMB_DIRECT` is disabled.

## Risks
The main risks are negotiated size mismatches, send iterator consumption across multi-fragment requests, connection-state races around reconnect/destroy, and memory-registration lifetime. Because much of the implementation delegates to `linux/smbdirect.h`, CIFS must keep its wrapper assumptions synchronized with the lower-level socket API behavior and negotiated parameter semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smbdirect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smbdirect.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smbdirect.h

## Summary
Declares the CIFS SMB Direct transport interface and compile-time stubs. When `CONFIG_CIFS_SMB_DIRECT` is enabled it exposes the RDMA connection wrapper, tunable globals, send/receive APIs, memory-registration APIs, and debug hook; otherwise it compiles callers against inert fallbacks.

## Main Responsibilities
- Define `cifs_rdma_enabled(server)` as either `server->rdma` or constant false depending on configuration.
- Include CIFS global structures and the kernel SMB Direct socket API for enabled builds.
- Declare SMB Direct module tunables shared with `smbdirect.c`.
- Define `struct smbd_connection` as a wrapper around `struct smbdirect_socket`.
- Declare connection lifecycle, transport I/O, RDMA memory registration, descriptor fill, deregistration, and debug functions.
- Provide disabled-build stubs for connection, reconnect, destroy, receive, and send operations.

## Key Interfaces
Enabled builds expose `smbd_get_connection()`, `smbd_get_parameters()`, `smbd_reconnect()`, `smbd_destroy()`, `smbd_recv()`, `smbd_send()`, `smbd_register_mr()`, `smbd_mr_fill_buffer_descriptor()`, `smbd_deregister_mr()`, and `smbd_debug_proc_show()`.

## Important Behavior
The disabled branch preserves a small subset of the call surface so generic CIFS code can compile without SMB Direct support. Some memory-registration declarations only exist in enabled builds, matching call sites that are themselves guarded by `CONFIG_CIFS_SMB_DIRECT`.

## Risks
Interface drift between the enabled declarations and disabled stubs can break non-RDMA builds. Callers must respect configuration guards around memory-registration helpers because the disabled branch does not define all RDMA types and functions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smbdirect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smbencrypt.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smbencrypt.c

## Summary
Provides the legacy SMB password-hash helper for producing an MD4 hash of a password encoded as NT Unicode. It is a small cryptographic support file used by older CIFS/NTLM authentication paths.

## Main Responsibilities
- Wrap the CIFS MD4 implementation through `mdfour()`.
- Convert an input password to UTF-16 using the supplied NLS codepage with a maximum of 128 characters.
- Hash the UTF-16 password bytes into the 16-byte NT hash buffer.
- Explicitly zero the temporary UTF-16 password buffer before returning.

## Key Interfaces
- `E_md4hash(const unsigned char *passwd, unsigned char *p16, const struct nls_table *codepage)` is the exported helper.
- Internal `mdfour()` initializes, updates, and finalizes `struct md4_ctx`.

## Important Behavior
A null password is treated as an empty UTF-16 string. The temporary password buffer is stack-allocated and then cleared with `memzero_explicit()` to avoid leaving plaintext-derived material in memory. MD4 failures are logged and returned to the caller.

## Cross-File Interactions
This helper belongs to legacy SMB/CIFS authentication support and uses `../common/md4.h` plus CIFS Unicode conversion from `cifs_unicode.h`. SMB2 raw NTLMSSP setup in `smb2pdu.c` ultimately depends on NTLM credential material prepared by surrounding CIFS authentication helpers.

## Risks
The algorithm is legacy and cryptographically obsolete, but required for NT hash compatibility. The main implementation risks are password length truncation, codepage conversion behavior, and preserving sensitive-buffer clearing on all paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smbencrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smberr.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smberr.h

## Summary
Defines classic SMB/CIFS error classes and error-code constants, with comments documenting their intended POSIX errno mappings. It is the legacy SMB error vocabulary used by SMB1-era mapping code and still retained in the client source tree.

## Main Responsibilities
- Define `struct smb_to_posix_error` entries pairing SMB error numbers with POSIX error codes.
- Define SMB error classes: `SUCCESS`, `ERRDOS`, `ERRSRV`, `ERRHRD`, and `ERRCMD`.
- Enumerate DOS-class errors such as invalid function, file not found, bad path, access denied, bad FID, sharing violation, lock conflict, disk full, invalid name, directory not empty, EA unsupported, quota exceeded, and symlink/internal passthrough cases.
- Enumerate server-class errors such as bad password, DFS referral, invalid TID/network name/device, print queue errors, invalid command, internal server error, bad permissions, paused server, timeout, no resources, too many UIDs, bad UID, notification enum, and account/password expiry cases.
- Preserve comments that are consumed or mirrored by mapping-table generation/maintenance expectations.

## Key Interfaces
This header is mostly constants rather than functions. The visible type is `struct smb_to_posix_error`, and the constants are named `ERR*`, `Err*`, and class names matching CIFS/SMB protocol terminology.

## Important Behavior
The comments after many defines document the Linux errno mapping intended by the client. Some values are not direct wire values but internal passthrough markers from NT status handling to POSIX errors. The header does not include guards in the displayed content, so it is intended for controlled inclusion in legacy error-mapping code rather than as a broad standalone API.

## Cross-File Interactions
Legacy CIFS error mapping code uses these definitions to translate SMB error-class/code pairs into Linux errnos. SMB2-specific error handling uses NT status mapping in separate code, but both ultimately feed the client’s POSIX-facing error returns.

## Risks
Changing values or mappings can alter user-visible errno behavior for legacy SMB/CIFS operations. Because the mappings are encoded in comments and constants, automated or manual table generation must keep comments, constants, and mapping tables synchronized.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smberr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/trace.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/trace.c

## Summary
Instantiates CIFS/SMB tracepoints by defining `CREATE_TRACE_POINTS` and including `trace.h`.

## Main Responsibilities
- Include CIFS global and SPNEGO types needed by tracepoint definitions.
- Define `CREATE_TRACE_POINTS` exactly once for the CIFS client tracepoint provider.
- Include `trace.h` so tracepoint storage and registration code is generated.

## Key Interfaces
This file does not define callable functions. Its interface is the set of tracepoints declared in `trace.h`, which become concrete tracepoint definitions through this compilation unit.

## Cross-File Interactions
All CIFS/SMB client files that call `trace_smb3_*` and related trace helpers depend on this file being compiled once. The files in this group use tracepoints heavily for negotiate, tree connect/disconnect, open, read/write, lock, close, flush, query, SMB Direct connect, and session-key events.

## Risks
The file is intentionally minimal. The main risk is accidental duplicate `CREATE_TRACE_POINTS` definition elsewhere or missing type includes needed by `trace.h`, either of which would break tracepoint compilation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/trace.c -->