# subset-b-005760 research

Grouped code research for SMB2/SMB3 client PDU, transport, SMBDirect, encryption, error, and trace files. Each section preserves the source path and is intended to be split into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2pdu.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb2pdu.c

## Purpose
`smb2pdu.c` is the central SMB2/SMB3 client protocol implementation for constructing, sending, replaying, and decoding command PDUs. It owns the command workers for negotiate, session setup, tree connect/disconnect, create/open, ioctl, close, query/set info, change notify, echo, flush, read/write, directory enumeration, lock, oplock/lease acknowledgement, and filesystem information queries. It also contains SMB3.1.1 negotiate context construction/parsing, POSIX extension handling, DFS path prefixing, durable/persistent handle create contexts, multichannel reconnect coordination, and RDMA offload integration points.

## Important APIs, Types, And Functions
The command entry points exported through `smb2proto.h` include `SMB2_negotiate`, `SMB2_sess_setup`, `SMB2_logoff`, `SMB2_tcon`, `SMB2_tdis`, `SMB2_open`/`SMB2_open_init`/`SMB2_open_free`, `SMB2_ioctl`/`SMB2_ioctl_init`, `SMB2_close`, `SMB2_flush`, `SMB2_query_info`, `SMB2_query_acl`, `SMB2_get_srv_num`, `SMB2_read`, `SMB2_write`, async `smb2_async_readv`/`smb2_async_writev`, `SMB2_query_directory`, `SMB2_set_eof`, `SMB2_set_acl`, `SMB2_set_ea`, `SMB2_oplock_break`, `SMB2_lease_break`, `SMB311_posix_qfs_info`, `SMB2_QFS_attr`, and `smb2_lockv`/`SMB2_lock`.

Core helpers are `smb2_hdr_assemble`, `smb2_reconnect`, `smb2_plain_req_init`, `smb2_ioctl_req_init`, `smb2_parse_contexts`, `smb2_validate_iov`, `smb2_validate_and_copy_iov`, `posix_info_sid_size`, and `posix_info_parse`. `smb3_encryption_required` centralizes whether a request should be transformed based on session flags, share flags, mount `seal`, and global mandatory seal policy. `smb3_update_ses_channels` coordinates multichannel expansion or disablement after reconnect or capability changes.

The important wire and state types used here are `struct smb_rqst`, `struct kvec`, `struct cifs_ses`, `struct cifs_tcon`, `struct TCP_Server_Info`, `struct cifs_open_parms`, `struct cifs_fid`, `struct cifs_io_parms`, `struct cifs_io_subrequest`, `struct cifs_search_info`, SMB2 request/response structs from common headers, create context structs from `smb2pdu.h`, and SMBDirect descriptors from `smbdirect.h`.

## Control Flow
Most workers follow the same pattern: select a channel with `cifs_pick_channel`, determine transform/sign/replay flags, allocate a request with `smb2_plain_req_init` or a command-specific init function, fill fixed and variable PDU fields, optionally add create or IO context vectors, send through `cifs_send_recv` or `cifs_call_async`, validate server offsets/lengths, copy or retain response payloads, release request/response buffers, and retry through `smb2_should_replay` for replayable failures.

Negotiation builds dialect arrays for explicit, default, and SMB3-any modes, sends SMB3.1.1 negotiate contexts for preauth integrity, encryption, netname, POSIX extensions, optional compression, and optional signing capability, then validates the returned dialect and decodes the security blob and negotiate contexts. The response updates `server->dialect`, `server->ops`, `server->vals`, sizes, capabilities, security mode, preauth hash, cipher, compression, POSIX support, and AEAD allocation.

Session setup is implemented as a small state machine in `struct SMB2_sess_data`. It selects Kerberos or RawNTLMSSP, allocates a session setup PDU, runs challenge/authenticate phases, updates session IDs/flags for non-binding sessions, stores auth/session keys, and calls `SMB2_sess_establish_session` to derive signing/encryption keys and mark the server session established.

Create/open flow is context-heavy. `SMB2_open_init` builds the create request, handles DFS-prefixed paths, leases, durable/persistent handle contexts, POSIX mode contexts, timewarp snapshot contexts, security descriptor contexts for mode/owner SID mapping, query-id contexts, and EA contexts. `SMB2_open` sends the request, stores returned persistent/volatile FIDs and lease metadata, copies basic file attributes, and parses returned create contexts.

Read/write paths have synchronous and async variants. Async reads install `cifs_readv_receive`, `smb2_readv_callback`, and `smb3_handle_read_data`; callbacks verify signatures, update credits, stats, netfs state, EOF/progress flags, retry flags, and RDMA MR lifetime. Async writes build an SMB2 write request around `rq_iter`, optionally use SMBDirect RDMA read descriptors, request/adjust credits, optionally set compression, and terminate netfs write subrequests from the callback.

## State And Persistence Behavior
The file mutates durable mount/session state rather than persistent local files. Negotiation persists dialect, capabilities, cipher, signing algorithm, compression algorithm, buffer sizes, preauth hashes, and AEAD handles in `TCP_Server_Info`. Session setup persists session IDs, flags, NTLM/Kerberos auth key material, SMB3 signing/encryption/decryption keys, and `session_estab`. Tree connect persists TID, share type, share flags, capabilities, maximal access, tree name, copy chunk defaults, isolated transport behavior, and reconnect flags in `cifs_tcon`.

Open and IO operations persist remote handle IDs, access mask, create GUID, lease keys/epoch, remote open counters, cached directory invalidation, search buffers, fs attribute/device/sector/volume info, and stats counters. Reconnect logic marks open files invalid, sets `need_reopen_files` for persistent handles, queues server reconnect work, renegotiates IO size, and reopens persistent handles after successful reconnect.

## Dependencies And Integration Points
This file integrates with the CIFS/SMB client core (`cifsglob.h`, `cifsproto.h`, `cifs_debug.h`), SMB2 transport signing and mid setup (`smb2transport.c`), SMBDirect (`smbdirect.h`), compression (`compress.h`), DFS upcall/cache, SPNEGO/key upcall, NTLMSSP blob builders, ACL/SID helpers, netfs subrequest completion, tracepoints from `trace.h`, Linux crypto setup through transport helpers, and common SMB2 status/fsctl definitions. All actual wire transmission is delegated to `cifs_send_recv` or `cifs_call_async`.

## Risks
The highest-risk areas are packed wire-buffer construction, variable-length context lists, and server-controlled offsets/lengths. The code contains many overflow and bounds checks, but changes near `CreateContextsOffset`, `OutputBufferOffset`, `OutputBufferLength`, `NextEntryOffset`, POSIX SID/name parsing, or DFS path rewriting can still introduce memory corruption or malformed PDU acceptance. Replay and reconnect behavior is subtle because handle-based commands must often return `-EAGAIN` so callers reopen handles rather than reuse stale FIDs. Signing/encryption decisions must stay aligned with SMB dialect rules, especially SMB3.1.1 tree connect signing and encrypted session/share requirements. RDMA offload must deregister MRs promptly on all completion paths to avoid resource exhaustion and IO deadlock.

## Test Signals
Useful tests include dialect negotiation across SMB2.1, SMB3.0, SMB3.0.2, SMB3.1.1; SMB3.1.1 negotiate context fuzzing; guest/null/Kerberos/NTLMSSP session setup; mandatory signing and sealing mounts; DFS and non-DFS create paths; durable and persistent handle reconnect; POSIX mkdir/open/query-dir parsing; malformed response offset/length injection; async read/write retry and credit accounting; SMBDirect threshold/offload paths; compression-enabled writes; change notify and query directory EOF; and tracepoint coverage for success/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2pdu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2pdu.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb2pdu.h

## Purpose
`smb2pdu.h` defines SMB2/SMB3 wire-format constants and packed structures used by the client PDU implementation. It focuses on transform headers, create contexts, IOCTL payloads, query information payloads, POSIX extension records, and WSL-style extended attribute metadata.

## Important APIs, Types, And Functions
This header exports constants such as `SMB2_TRANSFORM_HEADER_SIZE`, `MAX_SMB2_HDR_SIZE`, `SMB2_READWRITE_PDU_HEADER_SIZE`, `COMPOUND_FID`, `SMB2_CREATE_IOV_SIZE`, `MAX_SMB2_CREATE_RESPONSE_SIZE`, `SMB2_IOCTL_IOV_SIZE`, and WSL xattr names/sizes. It declares `extern char smb2_padding[7]` for iovec padding shared by request builders.

Important structs include `smb2_rdma_transform`, `smb2_rdma_crypto_transform`, symlink and error-context response structs, share redirect error context structures, create contexts for timewarp/query-id/security descriptor/EA, FSCTL retrieval pointer structures, DFS referral request, network resiliency request, compression ioctl payload, EA/reparse/file-id query structures, `create_posix_rsp`, `smb2_posix_info`, `smb2_posix_info_parsed`, and `smb2_create_ea_ctx`.

## Control Flow
The header has no executable control flow. Its fields are consumed by `smb2pdu.c` when building create contexts and parsing returned file/directory metadata, and by RDMA/encryption paths when describing transform metadata.

## State And Persistence Behavior
All types are packed wire views or parsed helpers. They do not own lifetime or persistence. State becomes persistent only when callers copy decoded fields into `TCP_Server_Info`, `cifs_tcon`, inode/open metadata, or search buffers.

## Dependencies And Integration Points
The header depends on socket types and CIFS ACL/SID definitions. It is included by SMB2 PDU builders and prototypes and indirectly ties protocol layout to ACL helpers, POSIX extension parsing, DFS, FSCTL, SMBDirect transform handling, and WSL xattr compatibility code.

## Risks
Because these structs model wire layout, alignment, endianness, packing, and flexible-array lengths are critical. Changing field order or sizes can silently break interoperability. Variable-length POSIX SID/name fields and WSL EA size macros require careful bounds checks in consumers. Constants such as maximum create response size and iov counts must remain synchronized with the contexts that `SMB2_open_init` may append.

## Test Signals
Compile-time layout checks, sparse/endian warnings, POSIX directory parsing, create-context interop, symlink/error-context parsing, WSL xattr query tests, and SMBDirect transform negotiation are the most relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2pdu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2proto.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb2proto.h

## Purpose
`smb2proto.h` is the internal declaration surface for the SMB2/SMB3 Linux CIFS client. It connects higher-level CIFS operations, transport code, PDU builders, crypto helpers, parsing helpers, and reconnect/oplock handlers without exposing implementation details in each C file.

## Important APIs, Types, And Functions
The prototypes cover error mapping (`map_smb2_to_linux_error`, `smb2_init_maperror`), message validation and sizing (`smb2_check_message`, `smb2_calc_size`, `smb2_get_data_area_len`), path conversion, signature verification, request setup, tcon lookup, oplock/lease handling, reparse/symlink handling, open/path metadata helpers, directory and filesystem operations, create/open/query/set/close/flush/ioctl/read/write command workers, async IO, echo, reconnect, SMB3 key/AEAD allocation, compounding helpers, replay helpers, security selection, negotiate validation, response validation, preauth hashing, POSIX info parsing, and pending-delete rename handling.

The header also exposes KUnit-only error mapping hooks under `CONFIG_SMB_KUNIT_TESTS`, allowing tests to inspect SMB2 status-to-POSIX mappings.

## Control Flow
There is no runtime logic here, but the grouping documents the layering: upper CIFS VFS code calls these prototypes, `smb2pdu.c` builds command PDUs, `smb2transport.c` signs/verifies and creates MIDs, and lower transport code sends requests. Init/free pairs such as `SMB2_open_init`/`SMB2_open_free`, `SMB2_ioctl_init`/`SMB2_ioctl_free`, and query/set/close/flush/directory init/free functions support compounding and async send paths.

## State And Persistence Behavior
The functions declared here mutate SMB client state through `TCP_Server_Info`, `cifs_ses`, `cifs_tcon`, inode, dentry, file, search, and IO-subrequest structures. The header itself persists no state, but it defines the contracts for who owns request buffers, response buffers, FIDs, replay counters, lease state, preauth hashes, and parsed POSIX metadata.

## Dependencies And Integration Points
The header includes NLS/key support and cached directory declarations, and refers to many CIFS/SMB core types. It is the integration point between authentication, transport signing, PDU construction, DFS/reparse behavior, POSIX extensions, SMBDirect-enabled IO, netfs IO completion, and filesystem stat/query code.

## Risks
Prototype drift is a practical risk: buffer ownership and response lifetime are encoded in signatures but not type-enforced. Several calls take raw pointers plus lengths, so callers must preserve the validation and free conventions from the implementation. Changes to replay, compounding, or init/free signatures can ripple through many VFS and transport users.

## Test Signals
Build coverage across all CIFS feature flags, KUnit status mapping tests, compounding tests, mount/auth variants, async IO, POSIX extension mounts, and reconnect tests signal whether this declaration layer remains consistent with implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2transport.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb2transport.c

## Purpose
`smb2transport.c` implements SMB2/SMB3 request signing, signature verification support, session/channel signing key lookup, SMB3 key derivation, mid-queue allocation/setup, receive checking, and AEAD crypto transform allocation. It is the bridge between already-built SMB2 PDUs and the CIFS transport machinery that assigns message IDs, tracks pending requests, signs outgoing messages, and validates incoming responses.

## Important APIs, Types, And Functions
Exported functions include `generate_smb30signingkey`, `generate_smb311signingkey`, `smb2_verify_signature`, `smb2_check_receive`, `smb2_setup_request`, `smb2_setup_async_request`, `smb2_find_smb_tcon`, and `smb3_crypto_aead_allocate`. Internal helpers include `smb3_get_sign_key`, `smb2_find_smb_ses_unlocked`, `smb2_get_sign_key`, `smb2_find_smb_sess_tcon_unlocked`, `smb2_calc_signature`, `generate_key`, `generate_smb3signingkey`, `smb3_calc_signature`, `smb2_sign_rqst`, `smb2_seq_num_into_buf`, `smb2_mid_entry_alloc`, and `smb2_get_mid_entry`.

The important state types are `TCP_Server_Info`, `cifs_ses`, `cifs_chan`, `cifs_tcon`, `mid_q_entry`, `smb_rqst`, `smb2_hdr`, HMAC-SHA256 and AES-CMAC contexts, and Linux crypto `crypto_aead` handles.

## Control Flow
Outgoing synchronous requests call `smb2_setup_request`: assign a message ID with credit-charge aware sequencing, validate server/session status, allocate and queue a MID, and sign the request if required. Async requests use `smb2_setup_async_request`, which performs a lighter server negotiation-status check, allocates a MID, and signs before submission. If signing fails, message IDs are reverted and MIDs are deleted or released.

SMB2 signing uses HMAC-SHA256 over the request, using the NTLMv2 session key from `ses->auth_key.response`. SMB3 signing uses AES-CMAC and channel-specific signing keys. Both paths zero the signature field before calculation and include an RFC1002 length vector if present before passing the data-only vectors into the shared signature calculator.

Key derivation uses SMB3 KDF labels and contexts. SMB3.0 derives signing, encryption, and decryption keys from fixed strings. SMB3.1.1 derives them using the preauth hash. Binding a new multichannel connection derives only the channel signing key and avoids overwriting session encryption/decryption keys. AES-256 ciphers on SMB3.1.1 use the full session key for encryption/decryption KDF input when available.

Incoming receive checking wraps the response in a single-vector request, dumps a short trace, verifies signatures when signing is enabled and the response was not decrypted, and maps SMB2 status to Linux errno.

## State And Persistence Behavior
The file mutates server sequence numbers, pending MID queues, MID refcounts/states, session and channel signing keys, session encryption/decryption keys, server AEAD encrypt/decrypt handles, and credit-related MID fields. It takes `cifs_tcp_ses_lock`, `ses_lock`, `chan_lock`, `srv_lock`, and `mid_queue_lock` around shared state. It increments session/tcon references when looking up objects by IDs and returns referenced tcons to callers.

## Dependencies And Integration Points
It depends on CIFS global structures and debug helpers, SMB2 prototype/status definitions, Linux crypto HMAC/AES-CMAC/AEAD APIs, the mid mempool, tracepoints, and error helpers. `smb2pdu.c` relies on this file through request setup and AEAD allocation; lower send paths rely on the MIDs and signatures prepared here.

## Risks
Key lookup across multichannel is concurrency-sensitive: binding channels, exiting sessions, and primary-vs-secondary server selection must remain correct. Signing must preserve the RFC1002/vector handling rules or signatures will fail only under certain send paths. Message ID rollback on failures is subtle and must match MID queue state. AEAD allocation failure paths must avoid leaking half-created transforms. Debug key dumping is gated but inherently sensitive.

## Test Signals
Important tests include signed and unsigned mounts, SMB2.1 HMAC signing, SMB3 AES-CMAC signing, multichannel binding/reconnect, SMB3.1.1 preauth hash key derivation, AES-256 cipher negotiation, signature-failure injection, MID allocation failure injection, and crypto allocation failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb2transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smbdirect.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smbdirect.c

## Purpose
`smbdirect.c` adapts the Linux SMBDirect socket API to the CIFS client. It creates, reconnects, destroys, sends, receives, registers memory, deregisters memory, and reports debug state for SMB over RDMA transports.

## Important APIs, Types, And Functions
Global tunables define initial SMBD credits, max send/receive sizes, fragmented receive size, keepalive interval, maximum FRMR depth, and the RDMA read/write threshold. Module parameters `smbd_logging_class` and `smbd_logging_level` control class-based logging.

Exported functions are `smbd_get_connection`, `smbd_get_parameters`, `smbd_reconnect`, `smbd_destroy`, `smbd_recv`, `smbd_send`, `smbd_register_mr`, `smbd_mr_fill_buffer_descriptor`, `smbd_deregister_mr`, and `smbd_debug_proc_show`. Internal helpers include `_smbd_get_connection`, `smbd_post_send_full_iter`, `smbd_logging_needed`, and `smbd_logging_vaprintf`.

## Control Flow
Connection setup builds `smbdirect_socket_parameters` from tunables, chooses port-specific transport restrictions, creates a kernel SMBDirect socket, installs logging callbacks, applies initial parameters and polling settings, rewrites the destination port, and connects synchronously. `smbd_get_connection` first tries port 5445 for iWARP-style SMBD and falls back to port 445 for InfiniBand/RoCE-style use, then clamps `server->rdma_readwrite_threshold` to the negotiated maximum fragmented send size.

Send flow calculates the combined SMB payload length across one or more `smb_rqst` objects, rejects payloads above the negotiated fragmented send size, builds a send batch, sends metadata kvecs and payload iterators in chunks that respect negotiated max-send size, flushes the batch, and waits for pending sends to drain. Receive flow delegates to `smbdirect_connection_recvmsg` after checking connection state.

RDMA memory registration delegates an `iov_iter` to `smbdirect_connection_register_mr_io`; descriptor filling and deregistration are thin wrappers used by SMB2 read/write offload paths in `smb2pdu.c`.

## State And Persistence Behavior
The only local connection state is `struct smbd_connection`, which owns a `struct smbdirect_socket *`. `server->smbd_conn` is installed, destroyed, or replaced during reconnect. Negotiated socket parameters are read dynamically from the socket. RDMA threshold state is persisted in `TCP_Server_Info`. Memory registration state is owned by `struct smbdirect_mr_io` objects and must be deregistered by IO completion paths.

## Dependencies And Integration Points
This file depends on `linux/smbdirect.h`, CIFS debug/proto helpers, `smb2proto.h`, and the `SMBDIRECT` namespace. It is called by CIFS connection setup/reconnect, low-level receive/send paths, `/proc` debug reporting, and SMB2 read/write RDMA offload in `smb2pdu.c`.

## Risks
The send path assumes upper layers never exceed negotiated fragmented send size and returns `-EINVAL` if they do. Connection setup mutates the destination sockaddr port in place, so callers must tolerate port rewriting and fallback. Batch flush and wait-zero-pending semantics are critical for correctness under error paths. MR exhaustion is a risk if callers fail to deregister promptly. Logging knobs can become noisy under class masks.

## Test Signals
Exercise connection fallback from 5445 to 445, disconnected send/recv returning retryable errors, large fragmented sends near negotiated limits, RDMA threshold clamping, read/write offload MR registration/deregistration, reconnect replacement of `server->smbd_conn`, and `/proc` debug output for RDMA and non-RDMA mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smbdirect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smbdirect.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/smbdirect.h

## Purpose
`smbdirect.h` declares the CIFS client wrapper interface for SMBDirect/RDMA support and provides no-op stubs when `CONFIG_CIFS_SMB_DIRECT` is disabled.

## Important APIs, Types, And Functions
When enabled, it defines `cifs_rdma_enabled(server)`, exposes RDMA tunables, declares `struct smbd_connection { struct smbdirect_socket *socket; }`, and prototypes connection, send/recv, MR registration, buffer descriptor fill, MR deregistration, and debug display functions. When disabled, it defines `cifs_rdma_enabled(server)` as `0`, an empty `struct smbd_connection`, and inline stubs returning `NULL` or `-1`.

## Control Flow
There is no runtime control flow in the header. Compile-time configuration selects real SMBDirect declarations or stubs, allowing the rest of the SMB client to compile with minimal feature-condition checks.

## State And Persistence Behavior
The enabled struct stores the SMBDirect socket pointer. No additional state is maintained here. Disabled stubs intentionally prevent RDMA state from existing.

## Dependencies And Integration Points
The enabled branch includes CIFS globals and `linux/smbdirect.h`. `smb2pdu.c`, transport setup, debug proc code, and connection management use this header to conditionally integrate RDMA behavior.

## Risks
The disabled stubs return generic `-1` rather than a specific errno, so callers should generally be protected by `cifs_rdma_enabled` or compile-time guards. Any new enabled API must receive a matching stub or non-RDMA builds will fail.

## Test Signals
Build both `CONFIG_CIFS_SMB_DIRECT=y/m` and disabled configurations. Runtime tests should verify non-RDMA mounts never enter stub send/recv paths and RDMA builds expose the expected wrapper functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smbdirect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smbencrypt.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smbencrypt.c

## Purpose
`smbencrypt.c` contains legacy SMB/CIFS password hashing support. In this listed slice it implements NT MD4 password hashing used to produce the 16-byte NT hash from a password converted to NT Unicode.

## Important APIs, Types, And Functions
The exported function is `E_md4hash(const unsigned char *passwd, unsigned char *p16, const struct nls_table *codepage)`. It converts at most 128 password characters to UTF-16 with `cifs_strtoUTF16`, hashes the UTF-16 byte stream through the internal `mdfour` helper, writes the digest to `p16`, and explicitly zeros the temporary UTF-16 password buffer.

The internal `mdfour` helper wraps `cifs_md4_init`, `cifs_md4_update`, and `cifs_md4_final` from the common MD4 implementation and logs failures.

## Control Flow
If `passwd` is non-null, `E_md4hash` converts it to UTF-16; if null, it hashes an empty null-terminated buffer. It then calls `mdfour`, clears `wpwd` with `memzero_explicit`, and returns the crypto helper status. `mdfour` performs init/update/final in order and exits early on init/update failures.

## State And Persistence Behavior
No persistent state is stored. The sensitive temporary Unicode password is stack-allocated and explicitly cleared. The resulting hash is written to the caller-provided output buffer.

## Dependencies And Integration Points
The file depends on CIFS Unicode conversion, debug helpers, common MD4, NLS tables, and kernel crypto/FIPS-related headers. It integrates with legacy authentication code that needs NT password hashes.

## Risks
MD4/NT hashes are legacy and security-sensitive. Callers must avoid using this in contexts where stronger authentication is required. The 128-character conversion limit is intentional but can truncate longer inputs. Output buffer sizing is caller-owned, so callers must provide at least 16 bytes. Any edits must preserve `memzero_explicit` of password material.

## Test Signals
Known NT hash test vectors, null/empty password behavior, non-ASCII password conversion under different NLS tables, crypto helper failure injection, and static analysis for sensitive buffer clearing are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smbencrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smberr.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/smberr.h

## Purpose
`smberr.h` defines legacy SMB error classes and SMB error-code constants with comments indicating intended POSIX errno mappings. It supports code that maps SMB/CIFS protocol errors to Linux errors and documents server-originated DOS/SRV/HRD/CMD status classes.

## Important APIs, Types, And Functions
The header defines `struct smb_to_posix_error { __u16 smb_err; int posix_code; }` and constants for error classes `SUCCESS`, `ERRDOS`, `ERRSRV`, `ERRHRD`, and `ERRCMD`. It then lists many DOS-class errors such as `ERRbadfunc`, `ERRbadfile`, `ERRbadpath`, `ERRnoaccess`, `ERRbadfid`, `ERRbadshare`, `ERRfilexists`, `ERRdiskfull`, `ERRdirnotempty`, pipe errors, quota/link errors, and internal passthrough values. It also lists SRV-class errors such as `ERRerror`, `ERRbadpw`, `ERRbadtype`, `ERRaccess`, `ERRinvtid`, `ERRinvnetname`, timeout/resource/user-account errors, and `ERRnosupport`.

## Control Flow
There is no executable logic. Mapping code can include this header to build error translation tables using the constants and the errno guidance embedded in comments.

## State And Persistence Behavior
The header stores no runtime state. It defines stable numeric protocol constants that must match legacy SMB wire values.

## Dependencies And Integration Points
It integrates with SMB/CIFS status-to-POSIX mapping code and with any path that still handles older SMB error-class/error-code responses rather than NTSTATUS-only SMB2 statuses. It complements SMB2 status mapping headers in `../common/smb2status.h`.

## Risks
The constants are protocol ABI. Renumbering or deduplicating them would break error mapping. Some values are obsolete or internal passthrough values; consumers must distinguish wire-originated values from internal-only translation aids. Comments are used to generate or reason about mapping tables, so stale comments can become test or behavior drift.

## Test Signals
Error mapping unit tests, KUnit SMB status tests, legacy server interop, DFS referral error mapping, pipe error handling, quota/link errors, and static checks that table entries use valid class/code pairs are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smberr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/trace.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/trace.c

## Purpose
`trace.c` is the tracepoint definition unit for the CIFS/SMB client. Defining `CREATE_TRACE_POINTS` before including `trace.h` causes the trace event storage and descriptors declared in `trace.h` to be emitted exactly once.

## Important APIs, Types, And Functions
The file does not define ordinary functions. It includes `cifsglob.h` and `cifs_spnego.h` so trace event definitions have the needed types, then includes `trace.h` with `CREATE_TRACE_POINTS`.

## Control Flow
There is no runtime control flow in this file. Runtime trace calls throughout the SMB client bind to the tracepoints instantiated here.

## State And Persistence Behavior
Tracepoint metadata is compiled into the module/kernel. No per-mount state is stored here. Runtime trace buffering is handled by the Linux tracing subsystem.

## Dependencies And Integration Points
All `trace_smb3_*`, key-expiration, reconnect, tcon reference, IO, and related CIFS trace events used by `smb2pdu.c`, `smb2transport.c`, and other client files depend on this compilation unit being linked once.

## Risks
Removing or duplicating `CREATE_TRACE_POINTS` causes missing symbols or duplicate definitions. Include ordering matters because trace event prototypes may reference CIFS/SPNEGO types.

## Test Signals
Build/link tests are the primary signal. Runtime validation can enable CIFS trace events while mounting, negotiating, reconnecting, and performing IO to verify event registration and payload decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/trace.c -->
