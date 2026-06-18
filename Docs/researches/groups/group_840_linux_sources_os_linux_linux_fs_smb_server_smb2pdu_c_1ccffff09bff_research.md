# Group Research: group_840_linux_sources_os_linux_linux_fs_smb_server_smb2pdu_c_1ccffff09bff

Scope checked against `Docs/research_subset_a.md`: `sources/os/linux/linux` is included in subset A. The listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smb2pdu.c -->
# File Research: sources/os/linux/linux/fs/smb/server/smb2pdu.c

## Role

`smb2pdu.c` is the main SMB2/SMB3 protocol command implementation for the Linux in-kernel SMB server, `ksmbd`. It parses SMB2 PDUs, validates session/tree/file state, maps SMB protocol requests onto Linux VFS operations, builds wire-format responses, and handles SMB3 signing, preauthentication hashing, and encryption transform headers.

## Main Responsibilities

- Initializes SMB2 response headers, error responses, compound response chaining, response buffers, credits, and async interim responses.
- Handles SMB dialect negotiation, SMB 3.1.1 negotiate contexts, preauth integrity, encryption/signing capability negotiation, POSIX extension negotiation, and compression context rejection/defaulting.
- Implements session setup for NTLMSSP and optional Kerberos, including session binding, multichannel channel tracking, signing/encryption key generation, guest handling, and failed-login throttling.
- Implements tree connect/disconnect and session logoff, including share type/capability reporting, share maximal access, tree/session state transitions, and file cleanup.
- Implements file create/open, including name conversion, stream names, POSIX create context, EA/security-descriptor create contexts, maximal-access and on-disk-id contexts, durable and persistent handle contexts, ACL inheritance, DOS attribute xattrs, oplock/lease grants, share-mode checks, truncation, allocation-size handling, and response create contexts.
- Implements directory enumeration, file/filesystem/security query info, close, echo, set info, read/write/flush, cancel, byte-range locks, ioctls, oplock/lease break acknowledgements, and signing/encryption helpers.

## Protocol State and Validation

The file enforces SMB2 state sequencing through helpers such as `smb2_check_user_session()`, `smb2_get_ksmbd_tcon()`, `check_session_id()`, and compound-request FID/session tracking. It treats negotiate, session setup, echo, cancel, logoff, and tree connect/disconnect as special cases where normal session/tree validation may be skipped or relaxed.

Compound requests are tracked with `next_smb2_rcv_hdr_off`, `next_smb2_rsp_hdr_off`, `compound_fid`, `compound_pfid`, and `compound_sid`. Responses are 8-byte aligned, chained with `NextCommand`, and related-operation requests may reuse a FID produced by an earlier create in the compound sequence.

Credit accounting in `smb2_set_rsp_credits()` subtracts the request credit charge, grants bounded credits, rejects overdraw, and accumulates compound grants so the last response carries the final granted credit count.

## Negotiation, Authentication, and Crypto

`smb2_handle_negotiate()` validates dialect lists and SMB 3.1.1 negotiate context offsets before selecting server dialect setup. SMB 3.1.1 requires parsing preauth integrity context; encryption, POSIX, and signing contexts are decoded if present. The server then assembles negotiate response contexts for preauth, encryption, POSIX support, and signing capabilities.

Session setup supports:
- NTLMSSP negotiate and authenticate phases, with optional SPNEGO wrapping.
- Optional Kerberos authentication under `CONFIG_SMB_SERVER_KERBEROS5`.
- SMB3 multichannel binding checks against dialect, signed binding request, client GUID, existing session state, reconnect state, and guest restrictions.
- SMB3 signing/encryption key generation and session encryption flagging.

The end of the file implements SMB2 HMAC-SHA256 signing, SMB3 signing, SMB 3.1.1 preauth response hashing, SMB3 transform-header construction, response encryption, transform-header detection, and request decryption.

## File and Directory Operations

`smb2_open()` is the central filesystem-facing path. It converts UTF-16 names, rejects leading slashes and vetoed names, handles alternate data streams through xattrs, validates create options/dispositions/access masks/attributes, resolves paths without following symlinks, checks DACL and inode permissions, creates files/directories, opens dentries, allocates ksmbd file IDs, handles durable handles, grants oplocks/leases, applies allocation-size/truncate behavior, inherits POSIX and NT ACLs, stores DOS attributes, and constructs SMB2 create responses.

Directory query uses `iterate_dir()` with a reservation pass and a second stat/population pass. It supports multiple SMB directory info classes, POSIX directory info, dot/dotdot handling, wildcard matching, hidden dot-file attributes, veto filtering, and output-buffer exhaustion semantics.

Query-info maps VFS metadata into SMB file, filesystem, EA, stream, POSIX, and security descriptor response classes. Filesystem info uses `vfs_statfs()`, reports NTFS-like attributes/name for compatibility, exposes sector/object/volume/size data, and supports POSIX filesystem info when negotiated.

Set-info mutates file basic info, allocation size, EOF, rename, hard link, disposition/delete-pending, EAs, file position, mode, and security descriptors. It checks write/share permissions and maps Linux/VFS errors back to SMB status codes.

## I/O, Locks, and IOCTLs

`smb2_read()` and `smb2_write()` validate handles, access rights, offsets, sizes, tree writability, and optional SMB Direct RDMA channels. Normal reads pin an auxiliary payload buffer into the response iov; RDMA reads write directly to the client memory region. Writes support write-through and RDMA reads from client memory before VFS write.

`smb2_lock()` translates SMB lock elements into Linux `file_lock`s, caps lock count at 64, checks range overflow and intra-request conflicts, tracks locks in connection and file lists, supports blocking lock deferral through async work and cancel, and rolls back already-applied locks on failure.

`smb2_ioctl()` implements selected FSCTLs: DFS referral stubs, object ID dummy response, pipe transceive, validate negotiate info, network interface info, resume keys, server-side copy chunk, sparse flag updates, zero data, allocated ranges, reparse-point reporting for special files, and duplicate extents/clone fallback.

## Oplocks, Leases, and Async Behavior

The file participates in ksmbd’s oplock/lease system by granting oplocks during create, breaking oplocks before truncation/allocation/write-sensitive operations, acknowledging SMB2.0 oplock breaks, and acknowledging SMB2.1 lease breaks. Lease acknowledgements validate requested downgrade state against expected new state and wake waiters on completion.

Async support is used for pending operations such as deferred locks. `setup_async_work()` allocates an async id, attaches cancel callbacks, records the work on the connection async list, and sends interim `STATUS_PENDING` responses. `smb2_cancel()` searches async or normal request lists and invokes cancel callbacks while guarding against repeated cancellation of already-cancelled deferred locks.

## Important Invariants

- SMB2/SMB3 request parsing is length-checked before dereferencing variable-length dialect, context, EA, name, security, IOCTL, and directory buffers.
- `ksmbd_override_fsids()` and `ksmbd_revert_fsids()` bracket VFS operations that must run under the SMB user identity.
- File references from `ksmbd_lookup_fd_*()` are released with `ksmbd_fd_put()` on all normal and error paths.
- Durable reconnect paths must balance durable lookup references separately from session file-table references.
- Delete-pending state is enforced before new opens and during disposition handling.
- Oplock/lease state changes wake waiters and reset `op_state`.
- Signed and encrypted requests use the negotiated/session/channel keys; SMB 3.1.1 preauth hashes are updated for negotiate and session setup traffic.

## Research Notes

This file is the main bridge between SMB2/SMB3 wire semantics and Linux VFS behavior in ksmbd. For filesystem research, the most relevant areas are `smb2_open()`, query/set-info handling, directory enumeration, read/write paths, lock handling, FSCTL implementations, DOS/EA/stream xattr mapping, ACL/security descriptor conversion, durable handles, and oplock/lease coordination.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smb2pdu.c -->