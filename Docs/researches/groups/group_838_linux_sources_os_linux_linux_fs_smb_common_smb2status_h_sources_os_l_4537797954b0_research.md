# Group Research: group_838_linux_sources_os_linux_linux_fs_smb_common_smb2status_h_sources_os_l_4537797954b0

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`, so all files in this group are in scope.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/common/smb2status.h -->
# File Research: sources/os/linux/linux/fs/smb/common/smb2status.h

This header defines SMB2/NTSTATUS wire-status constants from MS-ERREF for the Linux SMB stack. It is data-oriented: after the include guard and `struct ntstatus`, the file is almost entirely `STATUS_*`, `DBG_*`, `RPC_NT_*`, and related constant definitions encoded with `cpu_to_le32()`.

The comments beside each status name carry the intended POSIX errno mapping, and the header explicitly notes that those comments feed generation of `smb2_error_map_table`. This makes the file both a protocol constant source and an error-translation source.

Important details:
- Defines severity constants and the packed `struct ntstatus` layout.
- Covers success, informational, warning, and error NTSTATUS ranges.
- Includes filesystem-relevant mappings such as `STATUS_OBJECT_NAME_NOT_FOUND`, `STATUS_ACCESS_DENIED`, `STATUS_SHARING_VIOLATION`, `STATUS_DISK_FULL`, `STATUS_NOT_A_DIRECTORY`, and `STATUS_STOPPED_ON_SYMLINK`.
- Ends with SMB-specific `STATUS_SMB_NO_PREAUTH_INTEGRITY_HASH_OVERLAP`.
- Has no executable logic, allocation, locking, or external calls.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/common/smb2status.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/common/smbacl.h -->
# File Research: sources/os/linux/linux/fs/smb/common/smbacl.h

This common SMB header defines Windows security descriptor, SID, ACL, and ACE wire layouts used by SMB client/server code. The structures are packed and little-endian where required.

Key contents:
- ACE type constants from MS-DTYP, including allow, deny, audit, callback, object, mandatory label, resource attribute, and scoped policy ACEs.
- ACE inheritance/audit flags such as `OBJECT_INHERIT_ACE`, `CONTAINER_INHERIT_ACE`, and `INHERITED_ACE`.
- SID string sizing helpers and SID subauthority limits.
- SID role enum values for owner, group, UNIX/NFS user/group, and mode.
- Packed `struct smb_ntsd`, `struct smb_sid`, `struct smb_acl`, and `struct smb_ace`.

The file has no behavior; it is a shared ABI/layout definition for security metadata parsing and generation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/common/smbacl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/common/smbfsctl.h -->
# File Research: sources/os/linux/linux/fs/smb/common/smbfsctl.h

This header defines SMB/CIFS/SMB2 FSCTL and reparse-tag constants. It documents the 32-bit FSCTL bit layout as device, access, function, and method fields.

Key contents:
- Device, access, function, and method masks for FSCTL decoding.
- Common FSCTL operation codes for DFS referrals, oplocks, sparse/zero data, reparse points, copychunk, offload read/write, snapshots, validate negotiate info, named pipes, and network interface queries.
- Reparse tags for mount points, DFS, symlinks, NFS, Azure File Sync, AF_UNIX, and WSL Linux file types.
- `IS_REPARSE_TAG_NAME_SURROGATE(tag)` helper macro.
- `SMB2_0_IOCTL_IS_FSCTL` request flag.

The file is a protocol constant catalog with no runtime logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/common/smbfsctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/common/smbglob.h -->
# File Research: sources/os/linux/linux/fs/smb/common/smbglob.h

This common SMB header defines shared protocol-version values and RFC1001/1002 length helpers.

Key contents:
- `struct smb_version_values`, which describes negotiated protocol behavior: dialect string/id, lock commands, capabilities, maximum read/write/transaction sizes, credit limits, lock types, header sizes, response sizes, capability booleans, signing policy, and create-context sizes.
- `get_rfc1002_len()` reads the 24-bit length from a big-endian RFC1002 header.
- `inc_rfc1001_len()` increments the RFC1001 length field.
- String constants for SMB dialect names from SMB1 through SMB 3.1.1.
- Common I/O size constants, including `CIFS_DEFAULT_IOSIZE` and `MAX_CIFS_SMALL_BUFFER_SIZE`.

This is used by connection and response code to interpret stream framing and dialect-specific limits.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/common/smbglob.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/Kconfig -->
# File Research: sources/os/linux/linux/fs/smb/server/Kconfig

This Kconfig file declares kernel configuration options for the KSMBD SMB3 server.

Key options:
- `SMB_SERVER`: tristate SMB3 server support. Depends on networking, multiuser, and file locking; selects NLS, UTF-8/UCS2 helpers, crypto primitives, AEAD CCM/GCM, ASN.1, OID registry, and CRC32.
- `SMB_SERVER_SMBDIRECT`: optional SMB Direct/RDMA support, dependent on InfiniBand support and module/static compatibility.
- `SMB_SERVER_CHECK_CAP_NET_ADMIN`: defaults on; prevents unprivileged processes from starting the server.
- `SMB_SERVER_KERBEROS5`: optional Kerberos 5 support, defaults on when SMB server is enabled.

The help text positions KSMBD as an SMB3 kernel server backed by `ksmbd-tools` userspace configuration and IPC.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/Makefile -->
# File Research: sources/os/linux/linux/fs/smb/server/Makefile

This Makefile builds the `ksmbd` module/object when `CONFIG_SMB_SERVER` is enabled.

Key contents:
- `obj-$(CONFIG_SMB_SERVER) += ksmbd.o`.
- Core object list includes Unicode, auth, VFS, oplock, connection, work, crypto context, management modules, IPC/TCP transports, ACL, SMB2 PDU/ops/misc, and ASN.1-generated SPNEGO decoders.
- Adds explicit dependencies so `asn1.o` waits for generated ASN.1 headers.
- Conditionally includes `transport_rdma.o` for SMB Direct and `proc.o` for procfs support.

This file shows the group’s modules are early/core KSMBD infrastructure rather than standalone utilities.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/asn1.c -->
# File Research: sources/os/linux/linux/fs/smb/server/asn1.c

This file wraps Linux ASN.1 BER decoding for SPNEGO negotiation and builds SPNEGO NTLMSSP response blobs.

Main behavior:
- `ksmbd_decode_negTokenInit()` and `ksmbd_decode_negTokenTarg()` call generated ASN.1 decoders with `struct ksmbd_conn` as context.
- `encode_asn_tag()` and `compute_asn_hdr_len_bytes()` encode short/long BER lengths for generated response blobs.
- `build_spnego_ntlmssp_neg_blob()` builds a negTokenTarg response containing negotiation result, NTLMSSP OID, and an NTLM blob.
- `build_spnego_ntlmssp_auth_blob()` builds a final auth response with success/failure negotiation result.
- ASN.1 callbacks validate SPNEGO OIDs, record supported auth mechanisms on the connection, select the first preferred mechanism, and copy mech tokens with `kmemdup_nul()`.

It depends on generated headers `ksmbd_spnego_negtokeninit.asn1.h` and `ksmbd_spnego_negtokentarg.asn1.h`, Linux OID lookup, and auth-mechanism constants from `auth.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/asn1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/asn1.h -->
# File Research: sources/os/linux/linux/fs/smb/server/asn1.h

This header declares the SPNEGO ASN.1 entry points used by KSMBD session setup.

Exports:
- `ksmbd_decode_negTokenInit()`
- `ksmbd_decode_negTokenTarg()`
- `build_spnego_ntlmssp_neg_blob()`
- `build_spnego_ntlmssp_auth_blob()`

The decode APIs take a security blob and `struct ksmbd_conn`; the build APIs allocate output blobs and return their lengths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/asn1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/auth.c -->
# File Research: sources/os/linux/linux/fs/smb/server/auth.c

This file implements KSMBD authentication, signing, key derivation, preauth hashing, and SMB3 encryption/decryption.

Main areas:
- SPNEGO negotiate header: `ksmbd_copy_gss_neg_header()` copies a fixed GSS/SPNEGO header, with Kerberos OIDs included when `CONFIG_SMB_SERVER_KERBEROS5` is enabled.
- NTLMv2: computes the NTLMv2 hash from passkey, uppercase UTF-16 username, and domain; verifies the client response; derives the session key; handles optional key exchange via ARC4.
- NTLMSSP parsing/building: validates negotiate/authenticate blobs, stores client flags, generates challenge blobs with target info and random challenge.
- Kerberos: when enabled, delegates SPNEGO authentication to userspace IPC and builds/validates the session user plus session key; otherwise returns `-EOPNOTSUPP`.
- Signing: SMB2 uses HMAC-SHA256; SMB3 uses AES-CMAC.
- SMB3 keys: derives SMB 3.0 and SMB 3.1.1 signing/encryption/decryption keys using dialect-specific labels and contexts, including preauth hash context for 3.1.1.
- Encryption: `ksmbd_crypt_message()` uses AES-GCM or AES-CCM AEAD with scatterlists spanning response/request iovecs and transform-header associated data.

Security-sensitive dependencies include Linux crypto, FIPS gating for NTLMv2, session/user state, preauth session lookup, and the pooled AEAD context manager in `crypto_ctx.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/auth.h -->
# File Research: sources/os/linux/linux/fs/smb/server/auth.h

This header declares authentication and cryptographic APIs for KSMBD.

Key definitions:
- GSS header length/padding differ depending on Kerberos support.
- NTLM/SMB hash and signature sizes.
- Auth mechanism bit flags for NTLMSSP, Kerberos, MS Kerberos, and Kerberos user-to-user.

Exported APIs cover:
- SMB3 message encryption/decryption.
- GSS negotiate header copy.
- NTLMv2 authentication and NTLMSSP blob parsing/challenge generation.
- Kerberos authentication.
- SMB2/SMB3 signing.
- SMB 3.0/3.1.1 signing and encryption key derivation.
- SMB 3.1.1 preauth integrity hash generation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/auth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/connection.c -->
# File Research: sources/os/linux/linux/fs/smb/server/connection.c

This file manages KSMBD connection lifecycle, global connection tracking, receive loops, request accounting, writes, and transport startup/shutdown.

Main behavior:
- Maintains global `conn_list` hash under `conn_list_lock`.
- Optionally exposes procfs client information with address, dialect, credits, open files, running requests, and last active time.
- Uses a dedicated `ksmbd-conn-release` workqueue so final connection teardown can sleep safely even if the last put happens from non-sleepable context.
- `ksmbd_conn_alloc()` initializes NLS/Unicode state, sessions xarray, request lists, waitqueues, locks, credit state, async IDA, and refcounts.
- Request queue helpers account `req_running`, list synchronous requests, and release async work when dequeued.
- `ksmbd_conn_handler_loop()` is the per-connection receive loop: reads RFC1002 header, validates PDU size, allocates request buffer, reads the full PDU, validates SMB framing, and calls registered server callbacks.
- `ksmbd_conn_write()` serializes transport writes with `srv_mutex` and uses RFC1002 length from the first iovec.
- Transport init/destroy starts TCP and RDMA, creates proc entries, shuts down active sessions, and drains the global list.

The file abstracts transport operations but relies on TCP/RDMA implementations and server callbacks elsewhere.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/connection.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/connection.h -->
# File Research: sources/os/linux/linux/fs/smb/server/connection.h

This header defines the central `struct ksmbd_conn` and transport interfaces.

Key contents:
- Connection status enum for new, good, exiting, reconnect, negotiate/setup, and releasing states.
- `struct ksmbd_conn_stats` with open file and served request counters.
- `struct ksmbd_conn`, containing dialect ops/values, locks, network address, transport, NLS/Unicode state, session xarray, request lists, credits, NTLMSSP state, preauth state, auth mechanism selection, signing/encryption negotiation, async IDA, and release work.
- `struct ksmbd_conn_ops` server callbacks for processing and termination.
- `struct ksmbd_transport_ops` for disconnect/shutdown/read/writev/RDMA read/write/free.
- Public connection lifecycle, lookup, write, RDMA, queue, callback, lock, refcount, and transport APIs.
- Inline status testers/setters using `READ_ONCE()`/`WRITE_ONCE()`.

This is the main contract between KSMBD protocol handling and the underlying transport/session machinery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/connection.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/crypto_ctx.c -->
# File Research: sources/os/linux/linux/fs/smb/server/crypto_ctx.c

This file implements a small pool of reusable AEAD crypto contexts for SMB3 encryption.

Main behavior:
- Maintains `ctx_list` with spinlock, available-count, idle list, and waitqueue.
- Lazily allocates `struct ksmbd_crypto_ctx` and individual AEAD transforms for `gcm(aes)` and `ccm(aes)`.
- Caps retained contexts around `num_online_cpus()`; excess contexts are freed on release.
- `ksmbd_crypto_ctx_find_gcm()` and `ksmbd_crypto_ctx_find_ccm()` return a context with the requested transform allocated.
- `ksmbd_release_crypto_ctx()` returns a context to the idle list or frees it.
- `ksmbd_crypto_create()` initializes the pool with one idle context; `ksmbd_crypto_destroy()` frees idle contexts.

It is used by `auth.c` encryption/decryption paths to avoid repeatedly allocating AEAD transforms.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/crypto_ctx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/crypto_ctx.h -->
# File Research: sources/os/linux/linux/fs/smb/server/crypto_ctx.h

This header declares KSMBD AEAD crypto context pooling.

Key contents:
- Enum values for AES-GCM and AES-CCM slots.
- `struct ksmbd_crypto_ctx`, containing a list node and AEAD transform array.
- Convenience macros `CRYPTO_GCM(c)` and `CRYPTO_CCM(c)`.
- APIs to find/release contexts and create/destroy the pool.

The enum starts at value 16, so the transform array has unused lower slots; callers use the named enum values only.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/crypto_ctx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/glob.h -->
# File Research: sources/os/linux/linux/fs/smb/server/glob.h

This server-global header defines common KSMBD debug and allocation helpers.

Key contents:
- Includes Unicode and VFS cache headers.
- Declares global `ksmbd_debug_types`.
- Defines debug category bits for SMB, auth, VFS, oplock, IPC, connection, and RDMA.
- Sets `pr_fmt` to prefix messages with `ksmbd` and optional `SUBMOD_NAME`.
- `ksmbd_debug(type, ...)` emits `pr_info()` when the selected category bit is enabled.
- Defines `UNICODE_LEN(x)` and `KSMBD_DEFAULT_GFP`.

Many files in this group use `KSMBD_DEFAULT_GFP` and category debug logging from here.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/glob.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/ksmbd_netlink.h -->
# File Research: sources/os/linux/linux/fs/smb/server/ksmbd_netlink.h

This header is the userspace ABI between the kernel KSMBD server and the IPC daemon over generic netlink.

Main contents:
- Netlink family name/version and maximum field sizes.
- Request/response structures for heartbeat, startup, shutdown, login, extended login groups, share config, tree connect/disconnect, logout, RPC, and SPNEGO/Kerberos authentication.
- Flexible payload layouts for startup interface lists, share veto/path data, RPC payloads, and SPNEGO session-key/AP-REP payloads.
- `ksmbd_event` enum where response event IDs are paired with request IDs.
- Tree connect status enum.
- User, global, share, tree connect, RPC method, RPC status, and config-option flag namespaces.
- `ksmbd_share_config_path()` helper to locate the path after optional veto-list payload data.

This file is ABI-sensitive: structure packing, field widths, payload order, and flag values must match `ksmbd-tools`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/ksmbd_netlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/ksmbd_work.c -->
# File Research: sources/os/linux/linux/fs/smb/server/ksmbd_work.c

This file manages per-request `struct ksmbd_work` allocation, freeing, queueing, and response iovec construction.

Main behavior:
- Creates a `ksmbd_work_cache` slab for work objects.
- Creates the `ksmbd-io` percpu workqueue.
- `ksmbd_alloc_work_struct()` initializes compound FIDs, request/async/file list nodes, aux read list, and an initial 4-entry iovec array.
- `ksmbd_free_work_struct()` releases response/request buffers, transform buffer, iovec storage, auxiliary read buffers, async ID, and the slab object.
- `ksmbd_queue_work()` queues work to the KSMBD I/O workqueue.
- `ksmbd_iov_pin_rsp()` and `ksmbd_iov_pin_rsp_read()` append response buffers to the work iovec array and maintain the RFC1001/1002 length in iov[0].
- `allocate_interim_rsp_buf()` allocates a small response buffer for interim replies.

The code owns response vector bookkeeping used later by signing/encryption and transport write paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/ksmbd_work.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/ksmbd_work.h -->
# File Research: sources/os/linux/linux/fs/smb/server/ksmbd_work.h

This header defines per-request KSMBD work state.

Key contents:
- Work state enum: active, cancelled, closed.
- `struct aux_read` for auxiliary read buffers attached to a response.
- `struct ksmbd_work`, linking a request to connection/session/tree connect, request and response buffers, response iovecs, compound request offsets/FIDs, saved credentials, credits, transform buffer, state flags, RDMA invalidation data, async cancellation data, workqueue item, and request/async/file list nodes.
- Inline helpers to locate next/current response SMB2 buffer and next request SMB2 buffer, accounting for the RFC1002 header.
- Allocation/free, pool/workqueue, queue, iovec pinning, and interim response APIs.

This is the primary request context passed through SMB2 command handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/ksmbd_work.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/ksmbd_ida.c -->
# File Research: sources/os/linux/linux/fs/smb/server/mgmt/ksmbd_ida.c

This file wraps Linux IDA allocation for KSMBD protocol IDs.

Functions:
- `ksmbd_acquire_smb2_tid()` allocates SMB2 tree IDs in range `1..0xFFFFFFFE`.
- `ksmbd_acquire_smb2_uid()` allocates SMB2 session/user IDs from 1 and skips reserved `0xFFFE`.
- `ksmbd_acquire_async_msg_id()` allocates async message IDs from 1.
- `ksmbd_acquire_id()` allocates a generic ID.
- `ksmbd_release_id()` frees an ID.

The wrapper keeps protocol-reserved ID rules centralized.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/ksmbd_ida.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/ksmbd_ida.h -->
# File Research: sources/os/linux/linux/fs/smb/server/mgmt/ksmbd_ida.h

This header declares KSMBD IDA helpers and documents SMB protocol ID restrictions.

Important notes:
- TID `0xFFFF` must not be used as a valid SMB1-style TID.
- UID `0xFFFE` is reserved by LAN Manager history and should not be used.
- Exposes helpers for SMB2 TID, SMB2 UID, async message ID, generic ID, and release.

It is used by session, tree connection, and async work management.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/ksmbd_ida.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/share_config.c -->
# File Research: sources/os/linux/linux/fs/smb/server/mgmt/share_config.c

This file manages cached share configuration fetched from the userspace IPC daemon.

Main behavior:
- Maintains `shares_table`, a hash table keyed by casefolded share name under `shares_table_lock`.
- `share_config_request()` asks userspace for share configuration, validates the returned name against the requested name, allocates `struct ksmbd_share_config`, copies flags/masks/forced IDs, parses veto-list payloads, normalizes the path, and resolves it with `kern_path()` under overridden filesystem IDs.
- Pipe shares skip filesystem path setup.
- Existing cache entries win if another thread inserted the share while IPC was in progress.
- Reference counting is atomic; final put removes from the hash and frees veto patterns, path, name, and vfs path.
- `ksmbd_share_veto_filename()` matches filenames against configured veto wildcard patterns.

This module bridges userspace share configuration into kernel path and permission metadata used by tree connects and VFS operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/share_config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/share_config.h -->
# File Research: sources/os/linux/linux/fs/smb/server/mgmt/share_config.h

This header defines `struct ksmbd_share_config` and share configuration helpers.

Key fields:
- Share name/path and path length.
- Share flags and veto-list.
- Resolved `struct path`.
- Atomic refcount and hash node.
- Create/directory masks and forced create/directory modes.
- Forced uid/gid fields, with invalid sentinels.

Inline helpers compute final create/directory modes by applying masks and forced bits, and test share flags. Public APIs fetch, put, delete, and veto-match shares.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/share_config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/tree_connect.c -->
# File Research: sources/os/linux/linux/fs/smb/server/mgmt/tree_connect.c

This file manages SMB tree connections between a session and a share.

Main behavior:
- `ksmbd_tree_conn_connect()` gets share config, allocates a tree connect, acquires a tree ID, asks userspace IPC to authorize the connection, handles stale-share update requests, links the user/share to the tree, and stores it in the session xarray.
- Tree connection creation increments KSMBD tree connection counters.
- `ksmbd_tree_conn_lookup()` returns only connected tree connections and takes a refcount.
- `ksmbd_tree_conn_disconnect()` removes the tree from the session xarray, sends userspace disconnect IPC, releases the tree ID, decrements counters, and drops references.
- `ksmbd_tree_conn_session_logoff()` disconnects all trees for a session and destroys the xarray.

The file coordinates share config lifetime, userspace authorization, and per-session tree ID ownership.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/tree_connect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/tree_connect.h -->
# File Research: sources/os/linux/linux/fs/smb/server/mgmt/tree_connect.h

This header defines tree connection state and APIs.

Key contents:
- Tree states: new, connected, disconnected.
- `struct ksmbd_tree_connect` with ID, flags, share config, user, list node, maximal access, POSIX extension flag, refcount, and state.
- `struct ksmbd_tree_conn_status` combining status code and tree pointer.
- `test_tree_conn_flag()` helper.
- APIs for connect, put, disconnect, lookup, and session logoff cleanup.

It includes `ksmbd_netlink.h` for tree connection flag/status values shared with userspace IPC.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/tree_connect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/user_config.c -->
# File Research: sources/os/linux/linux/fs/smb/server/mgmt/user_config.c

This file manages KSMBD user objects returned by userspace IPC.

Main behavior:
- `ksmbd_login_user()` sends a login request to userspace, checks `KSMBD_USER_FLAG_OK`, optionally fetches extended group data, and allocates a user.
- `ksmbd_alloc_user()` copies account name, flags, uid/gid, NT hash/passkey, and optional supplementary groups.
- `ksmbd_free_user()` sends logout IPC and frees groups, name, passkey, and object.
- `ksmbd_anonymous_user()` detects empty-name users.
- `ksmbd_compare_user()` compares name and passkey for session reuse checks.

The file keeps user credentials as kernel-owned copies while relying on userspace for account database lookup.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/user_config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/user_config.h -->
# File Research: sources/os/linux/linux/fs/smb/server/mgmt/user_config.h

This header defines `struct ksmbd_user` and accessors for user state.

Fields include:
- User flags.
- uid/gid.
- Account name.
- Passkey/hash and size.
- Supplementary group count and gid array.

Inline helpers test/set flags, detect guest flag, and return name/passkey/uid/gid. Public APIs cover login, allocation, free, anonymous check, and user comparison.

`set_user_guest()` is currently an empty inline, so guest status is represented by flags populated elsewhere rather than by this helper.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/user_config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/user_session.c -->
# File Research: sources/os/linux/linux/fs/smb/server/mgmt/user_session.c

This file manages SMB2 session lifetime, lookup, multichannel bindings, preauth sessions, RPC handles, and procfs session reporting.

Main behavior:
- Maintains global session IDs with `session_ida`, a `sessions_table` hash, and per-connection session xarrays.
- Optional procfs output reports sessions, clients, users, state, capabilities, signing/encryption algorithm, channel count, and tree connects.
- Session creation initializes file tables, xarrays, locks, sequence number, refcount, SMB2 flag, session ID, hash insertion, proc entry, and counters.
- Session destruction logs off tree connects, destroys file table, frees user, launches durable-handle scavenger, clears RPC handles, frees channels/preauth hash, releases IDs, and frees the session.
- Lookup APIs support per-connection lookup, global slowpath lookup, and multichannel binding validation.
- `destroy_previous_session()` handles reconnect semantics: validates same user/passkey, marks related connections for reconnect, waits idle, destroys previous file table, expires the session, and restores setup state.
- Preauth session helpers store and look up per-session preauth hash values for SMB 3.1.1 binding.
- RPC helpers map named pipes such as `srvsvc`, `wkssvc`, `samr`, `lsarpc`, and `LANMAN` to IPC RPC methods and track per-session RPC handles.

This is the main session ownership layer tying together users, channels, tree connects, file tables, durable cleanup, and IPC-backed RPC.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/mgmt/user_session.c -->