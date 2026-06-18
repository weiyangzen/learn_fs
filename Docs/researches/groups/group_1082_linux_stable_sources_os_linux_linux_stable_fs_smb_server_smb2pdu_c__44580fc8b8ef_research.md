# Group Research: group_1082_linux_stable_sources_os_linux_linux_stable_fs_smb_server_smb2pdu_c__44580fc8b8ef

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smb2pdu.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/smb2pdu.c

## Summary
Implements the KSMBD server-side SMB2/SMB3 PDU handlers. This is the main protocol execution layer for negotiation, session setup, tree connect/disconnect, file create/open/close, directory enumeration, query/set info, read/write, flush, cancel, byte-range locking, FSCTL/IOCTL dispatch, oplock and lease break acknowledgments, packet signing, SMB 3.1.1 preauth hashing, and SMB3 encryption/decryption.

## Main Responsibilities
- Manage SMB2 response buffer selection for normal and compound requests through `WORK_BUFFERS()` and chained response offsets.
- Validate session ids, tree ids, compound request relationships, response sizes, credits, and command-specific buffer bounds.
- Negotiate SMB dialect features, including SMB 3.1.1 preauth integrity, encryption ciphers, signing capabilities, compression placeholder handling, and POSIX extension availability.
- Drive NTLMSSP/SPNEGO and optional Kerberos session setup, including previous-session teardown, multichannel binding, signing/encryption key generation, and guest/session flags.
- Connect and disconnect shares, set share capabilities, expose pipe versus disk share behavior, and enable POSIX extensions per tree connection.
- Implement `CREATE` with path conversion, stream parsing, veto names, POSIX create context, EA/security descriptor contexts, durable/persistent handles, leases/oplocks, ACL inheritance, DOS attribute xattrs, allocation size, maximal access, disk id, and AAPL detection.
- Encode directory query responses for multiple information classes, including POSIX directory entries and dot/dotdot handling.
- Serve file, filesystem, and security query-info classes, including EA enumeration, stream enumeration, NT security descriptor construction, POSIX info, and pipe special cases.
- Apply set-info operations for timestamps, DOS attributes, allocation size, EOF, rename, hardlink, delete disposition, EAs, position, mode, and security descriptors.
- Handle file and IPC pipe read/write paths, including RDMA channel descriptors for SMB Direct.
- Implement lock validation, conflict checks across connections, deferred blocking locks, cancellation cleanup, rollback, and oplock breaks after lock changes.
- Dispatch FSCTLs such as validate negotiate info, query interface info, copychunk, set sparse, zero data, query allocated ranges, get reparse point, resume key, duplicate extents, object id, and pipe transceive.
- Verify and generate SMB2 HMAC-SHA256 and SMB3 AES-CMAC signatures and wrap/unwrap encrypted SMB3 transform messages.

## Key Interfaces
- Framing/session helpers: `smb2_allocate_rsp_buf()`, `init_smb2_rsp_hdr()`, `smb2_set_err_rsp()`, `smb2_set_rsp_credits()`, `smb2_check_user_session()`, `smb2_get_ksmbd_tcon()`, `is_chained_smb2_message()`.
- Negotiation/authentication: `init_smb2_neg_rsp()`, `smb2_handle_negotiate()`, `smb2_sess_setup()`, `smb3_encryption_negotiated()`, `smb3_preauth_hash_rsp()`.
- Tree/session commands: `smb2_tree_connect()`, `smb2_tree_disconnect()`, `smb2_session_logoff()`.
- File lifecycle and metadata: `smb2_open()`, `smb2_close()`, `smb2_query_info()`, `smb2_set_info()`, `smb2_query_dir()`.
- I/O and synchronization: `smb2_read()`, `smb2_write()`, `smb2_flush()`, `smb2_cancel()`, `smb2_lock()`, `smb_flock_init()`.
- IOCTL and cache-control: `smb2_ioctl()`, `smb2_oplock_break()`, `smb2_notify()`.
- Signing/encryption: `smb2_is_sign_req()`, `smb2_check_sign_req()`, `smb2_set_sign_rsp()`, `smb3_check_sign_req()`, `smb3_set_sign_rsp()`, `smb3_is_transform_hdr()`, `smb3_decrypt_req()`, `smb3_encrypt_resp()`, `smb3_11_final_sess_setup_resp()`.

## Control Flow And Behavior
Incoming commands use the current SMB2 header offset to choose request and response buffers. Compound requests preserve the create FID/session for later related operations, align each response to 8 bytes, and adjust RFC1001 length/iovec accounting.

Negotiation validates dialect arrays and SMB 3.1.1 negotiate-context offsets before selecting dialect-specific server values. SMB 3.1.1 computes preauth hashes over request and response data and returns contexts for preauth, encryption, POSIX, and signing when applicable.

Session setup creates or looks up sessions, supports multichannel binding only under SMB3 and configured multichannel support, validates signed binding requests and client GUIDs, then runs Kerberos or NTLMSSP authentication. Successful setup marks the connection good, updates session state, installs channel state, and generates signing/encryption keys.

The create path is the densest section. It converts names from UTF-16, rejects leading slashes and vetoed names, handles alternate data streams through xattrs, enforces create options/dispositions/access masks, maps Windows access to Linux open and permission checks, creates missing files/directories, sets EAs and ACLs, opens a `ksmbd_file`, publishes volatile/persistent ids, negotiates share modes and leases/oplocks, truncates when needed, and appends create-context responses.

Directory query first reserves response entries while iterating the directory, then looks up each reserved name to fill attributes. Query/set info paths translate between SMB info classes and Linux VFS/xattr/security descriptor operations, with explicit output-buffer checks before pinning response iovecs.

Read/write enforce maximum negotiated or RDMA transport sizes, validate offsets and channel descriptors, check granted access, call KSMBD VFS helpers, and either pin inline payloads or transfer data through RDMA. Locking maps SMB lock flags to POSIX locks and tracks KSMBD lock records on connection and file lists.

## State And Synchronization
The file coordinates connection/session/tree/file state through connection locks, session locks, tree connection locks, channel xarrays, async request lists, per-connection lock lists, file blocked-work lists, and fsuid override/revert pairs. It also manages buffer ownership through `ksmbd_iov_pin_rsp()` and `ksmbd_iov_pin_rsp_read()`, with special care for auxiliary payload buffers and security descriptors.

## Cross-File Interactions
This file depends heavily on KSMBD management and protocol modules: `connection.c` and transport layers for connection state and writes; `auth.c`, `asn1.c`, and Kerberos/NTLM helpers for authentication; `oplock.c` for oplocks/leases; `vfs.c` and `vfs_cache.c` for file operations; `smbacl.c` for security descriptors; `transport_ipc.c` for named pipes; `transport_rdma.c` for SMB Direct; and share/session/tree management modules for configured access policy and lifetime.

## Risks
Highest-risk areas are untrusted wire-length validation, compound offset accounting, create-context parsing, durable-handle reconnect lifetime, ACL/security descriptor sizing, EA and stream xattr translation, async lock cancellation, cross-connection lock conflict handling, RDMA descriptor validation, signing/encryption key selection during multichannel binding, and status-code mapping. Many behaviors vary by dialect, share flags, POSIX extensions, encryption, durable handle support, oplocks, streams, IPC pipes, and RDMA transport.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smb2pdu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smb2pdu.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/smb2pdu.h

## Summary
Defines KSMBD SMB2/SMB3 PDU constants, wire-adjacent structures, file/filesystem information sizes, create-context payloads, POSIX extension structures, and the public server-side SMB2 handler prototypes implemented by `smb2pdu.c`.

## Main Responsibilities
- Define SMB2 create actions, credit limits, maximum header and I/O sizing defaults.
- Store SMB 3.1.1 preauth integrity state and negotiate-context offsets.
- Define session state bits and timeout constants.
- Define create-context payload wrappers for allocation size, durable responses, POSIX responses, EA buffers, and security descriptor buffers.
- Define IOCTL response structures for socket addresses, file object ids, sparse flag setting, and network interface responses.
- Define file and filesystem information class response-size constants used by query/set info handlers.
- Define packed SMB2 file information payloads for access, alignment, alternate name, streams, standard info, EA info, allocation, disposition, position, mode, compression, attribute tags, EA entries, and POSIX directory/query data.
- Declare the KSMBD SMB2 command handlers and signing/encryption helpers.
- Define POSIX file type constants used in SMB3 POSIX mode encoding.

## Key Types And Constants
- `struct preauth_integrity_info` stores the negotiated preauth hash id and hash value.
- `OFFSET_OF_NEG_CONTEXT` captures the negotiate-context offset difference between Kerberos-enabled and non-Kerberos builds.
- `SMB2_SESSION_EXPIRED`, `SMB2_SESSION_IN_PROGRESS`, and `SMB2_SESSION_VALID` describe session lifecycle state.
- `struct create_alloc_size_req`, `struct create_durable_rsp`, `struct create_posix_rsp`, `struct create_ea_buf_req`, and `struct create_sd_buf_req` mirror create-context payloads consumed by `smb2_open()`.
- `struct smb2_ea_info_req` and `struct smb2_ea_info` define EA query/set payload layout.
- `struct smb2_posix_info` defines SMB3 POSIX directory information with embedded SID and variable name data.
- Handler declarations include `smb2_handle_negotiate()`, `smb2_sess_setup()`, `smb2_tree_connect()`, `smb2_open()`, `smb2_query_info()`, `smb2_query_dir()`, `smb2_set_info()`, `smb2_read()`, `smb2_write()`, `smb2_lock()`, `smb2_ioctl()`, and `smb2_oplock_break()`.

## Important Behavior
The structures are packed wire-format definitions, so callers must validate offsets, buffer lengths, and variable tails before use. The size constants in this header are directly coupled to response encoding in `smb2pdu.c`; changing them affects buffer sizing, info-class validation, and iovec pinning.

## Cross-File Interactions
`smb2pdu.c` is the primary consumer and implementer of the declarations here. Other KSMBD protocol, transport, connection, and dispatch code uses these prototypes to initialize dialect behavior, validate SMB2 messages, route command handlers, and apply signing/encryption processing.

## Risks
The main risk is wire-layout drift. Any change to packed structures, info-class sizes, negotiate offsets, POSIX mode constants, or handler prototypes must be synchronized with request validation and response construction in `smb2pdu.c`; otherwise clients can receive malformed PDUs or server-side bounds checks can become incorrect.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smb2pdu.h -->