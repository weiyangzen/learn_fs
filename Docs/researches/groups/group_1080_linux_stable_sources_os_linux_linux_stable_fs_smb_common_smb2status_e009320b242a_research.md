# Group Research: group_1080_linux_stable_sources_os_linux_linux_stable_fs_smb_common_smb2status_e009320b242a

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/smb2status.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/common/smb2status.h

Read status: complete.

## Purpose
Defines little-endian SMB2/NTSTATUS status constants from MS-ERREF for use across SMB client/server error handling.

## Main Contents
- NTSTATUS severity constants and `struct ntstatus`.
- A large catalog of `STATUS_*`, `RPC_NT_*`, `DBG_*`, and subsystem-specific status codes.
- End-of-line comments documenting the intended Linux/POSIX errno mapping used to generate `smb2_error_map_table`.

## Dependencies And Role
This is a shared protocol header under `fs/smb/common`, consumed by SMB2/SMB3 code that emits, parses, or maps wire status values. Constants are stored with `cpu_to_le32()`/`__constant_cpu_to_le32()` so callers can compare or place wire-format status values directly.

## Risks
The main risk is status-to-errno drift: the comments are not passive documentation, they feed generated mapping tables. Any new code or renamed constants must preserve little-endian representation and keep mappings aligned with SMB2 client/server behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/smb2status.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/smbacl.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/common/smbacl.h

Read status: complete.

## Purpose
Provides shared SMB/CIFS ACL, ACE, SID, and security descriptor wire-format definitions.

## Main Contents
- SID authority/subauthority sizing constants.
- MS-DTYP ACE type and ACE inheritance/audit flag constants.
- SID string sizing helpers and SID type enums for owner/group/Unix/NFS forms.
- Packed wire structs: `smb_ntsd`, `smb_sid`, `smb_acl`, and `smb_ace`.

## Dependencies And Role
Used by SMB client and server ACL code as the common layout contract for security descriptors and access control entries.

## Risks
Packed structure layout and SID size bounds are protocol-sensitive. Changing field order, array sizes, or constants would break ACL parsing/building and can create bounds-checking bugs in callers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/smbacl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/smbfsctl.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/common/smbfsctl.h

Read status: complete.

## Purpose
Defines SMB/CIFS/SMB2 FSCTL and IOCTL control codes plus reparse tag constants shared by SMB protocol code.

## Main Contents
- FSCTL bit-layout masks for device, access, function, and method fields.
- DFS, oplock, compression, reparse point, sparse, copy offload, validate negotiate, snapshot, pipe, and network interface FSCTL codes.
- Common reparse tags including DFS, symlink, NFS, Azure File Sync, AF_UNIX, and WSL tags.
- `IS_REPARSE_TAG_NAME_SURROGATE()` and `SMB2_0_IOCTL_IS_FSCTL`.

## Dependencies And Role
Consumed by SMB IOCTL builders/parsers and reparse handling paths on both client and server sides.

## Risks
These constants are wire ABI. Incorrect values route requests to the wrong server operation or misclassify reparse points, especially around symlink/DFS/WSL behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/smbfsctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/smbglob.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/common/smbglob.h

Read status: complete.

## Purpose
Defines shared SMB version capability values and RFC1001/1002 length helpers.

## Main Contents
- `struct smb_version_values` for dialect-specific limits, capability bits, signing flags, header sizes, and create context sizes.
- `get_rfc1002_len()` and `inc_rfc1001_len()` helpers.
- SMB dialect version strings and default I/O/small-buffer size constants.

## Dependencies And Role
Used by SMB dialect tables and request/response construction code to abstract protocol-version differences.

## Risks
Version value fields are central to negotiated buffer sizing and dialect behavior. Incorrect values can under-allocate messages, advertise unsupported capabilities, or corrupt RFC1002 length framing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/smbglob.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/Kconfig

Read status: complete.

## Purpose
Declares kernel configuration options for the ksmbd SMB3 server.

## Main Contents
- `SMB_SERVER` tristate with dependencies on networking, multiuser, and file locking.
- Crypto, ASN.1, NLS, OID registry, and CRC32 selections required by SMB3 auth/signing/encryption.
- `SMB_SERVER_SMBDIRECT` for optional RDMA/SMB Direct support.
- `SMB_SERVER_CHECK_CAP_NET_ADMIN` and `SMB_SERVER_KERBEROS5` toggles.

## Dependencies And Role
Controls whether ksmbd is built and which transport/authentication features are compiled.

## Risks
Config selections must match code assumptions. Missing crypto/ASN.1 selections would break negotiated SMB3 security features; SMB Direct has strict InfiniBand dependency constraints.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/Makefile

Read status: complete.

## Purpose
Builds the `ksmbd` module/object list for the in-kernel SMB3 server.

## Main Contents
- Adds `ksmbd.o` under `CONFIG_SMB_SERVER`.
- Lists core server, auth, VFS, oplock, connection, work, management, transport, ACL, SMB2 PDU, and generated ASN.1 objects.
- Declares dependencies for generated SPNEGO ASN.1 headers/sources.
- Conditionally includes RDMA transport and proc support.

## Dependencies And Role
Defines compilation composition for the server subtree and generated ASN.1 integration.

## Risks
Object ordering and generated-header dependencies matter for clean parallel builds. Missing objects silently remove feature implementations from the final module.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/asn1.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/asn1.c

Read status: complete.

## Purpose
Implements SPNEGO ASN.1/BER decode callbacks and NTLMSSP SPNEGO response blob builders for ksmbd authentication.

## Main Responsibilities
- Decode `negTokenInit` and `negTokenTarg` blobs with generated ASN.1 decoders.
- Build SPNEGO-wrapped NTLMSSP challenge and final auth response blobs.
- Validate GSS mechanism OIDs and record supported/preferred auth mechanisms on the connection.
- Copy mechanism tokens from decoded SPNEGO messages into `conn->mechToken`.

## Key Interfaces
`ksmbd_decode_negTokenInit()`, `ksmbd_decode_negTokenTarg()`, `build_spnego_ntlmssp_neg_blob()`, `build_spnego_ntlmssp_auth_blob()`, and generated-decoder callbacks such as `ksmbd_neg_token_init_mech_type()`.

## Risks
ASN.1 length encoding and token copying are security-sensitive. Incorrect bounds, OID handling, or allocated token lifetime can break session setup or expose malformed-client parsing bugs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/asn1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/asn1.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/asn1.h

Read status: complete.

## Purpose
Declares ksmbd SPNEGO ASN.1 decode and blob-building helpers.

## Main Contents
- Prototypes for `ksmbd_decode_negTokenInit()` and `ksmbd_decode_negTokenTarg()`.
- Prototypes for NTLMSSP SPNEGO negotiation/auth response blob construction.

## Dependencies And Role
Used by SMB2 session setup/authentication code to bridge wire security blobs to `asn1.c`.

## Risks
Prototype changes affect authentication call sites and buffer ownership expectations for allocated SPNEGO blobs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/asn1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/auth.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/auth.c

Read status: complete.

## Purpose
Implements ksmbd authentication crypto: NTLMv2 verification, Kerberos handoff, SMB2/3 signing, key derivation, preauth hashing, and SMB3 transform encryption/decryption.

## Main Responsibilities
- Provide static GSS negotiation headers depending on Kerberos support.
- Decode NTLMSSP negotiate/authenticate blobs and verify NTLMv2 challenge responses.
- Build NTLMSSP challenge blobs with target info and server challenge.
- Delegate Kerberos/SPNEGO authentication to userspace IPC when enabled.
- Sign SMB2 with HMAC-SHA256 and SMB3 with AES-CMAC.
- Derive SMB3 signing and encryption/decryption keys for SMB 3.0 and 3.1.1, including channel binding/preauth contexts.
- Compute SMB 3.1.1 preauthentication integrity hashes.
- Encrypt/decrypt SMB3 transform messages using AES-CCM or AES-GCM over scatterlists.

## Dependencies And Role
Depends on user/session state, `crypto_ctx`, transport IPC, NTLMSSP structures, SMB common constants, and Linux crypto primitives. It is called from SMB2 negotiation/session setup and encrypted send/receive paths.

## Risks
High-risk areas include FIPS behavior for NTLMv2, NTLMSSP offset/length validation, session-key exchange decryption, multichannel signing-key selection, AES-256 key length selection, scatterlist construction for vmalloc buffers, and transform-header associated-data handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/auth.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/auth.h

Read status: complete.

## Purpose
Declares ksmbd authentication, signing, encryption, and key-derivation interfaces.

## Main Contents
- GSS header length/padding constants conditional on Kerberos support.
- NTLM/CIFS hash and session-key sizes.
- Auth mechanism bit flags for NTLMSSP and Kerberos variants.
- Prototypes for NTLMSSP parsing, challenge building, Kerberos auth, signing, key derivation, preauth hashing, and message encryption/decryption.

## Dependencies And Role
Included by authentication/session setup and SMB2 crypto paths.

## Risks
Function signatures encode buffer ownership and key-size assumptions. Any mismatch with `auth.c` or SMB2 session setup can break signing/encryption interoperability.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/auth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/connection.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/connection.c

Read status: complete.

## Purpose
Manages ksmbd connection objects, per-connection handler loops, request admission, transport writes, RDMA hooks, connection shutdown, and proc client reporting.

## Main Responsibilities
- Allocate/free `ksmbd_conn`, including NLS/Unicode state, xarrays, IDAs, request lists, locks, and refcounts.
- Maintain the global connection hash and optional `/proc` clients view.
- Defer final transport/socket cleanup to a workqueue so last-put cleanup can sleep safely.
- Enqueue/dequeue running requests and async work, updating idle wait queues.
- Read RFC1002-framed SMB PDUs, validate sizes, allocate request buffers, and dispatch through registered process callbacks.
- Serialize transport writes and expose RDMA read/write transport operations.
- Stop all sessions/transports during server teardown.

## Dependencies And Role
Sits between TCP/RDMA transports and SMB request processing. It coordinates with sessions, work items, server config, stats, and transport ops.

## Risks
Critical risks are connection refcount lifetime, request counters during disconnect, RFC1002 PDU size validation, teardown ordering, and avoiding sleepable socket cleanup from non-sleeping contexts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/connection.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/connection.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/connection.h

Read status: complete.

## Purpose
Defines ksmbd connection state, transport operation contracts, and connection lifecycle APIs.

## Main Contents
- Session/connection status enum values.
- `struct ksmbd_conn_stats`, `struct ksmbd_conn`, `struct ksmbd_conn_ops`, `struct ksmbd_transport_ops`, and `struct ksmbd_transport`.
- TCP timeout/backlog constants and global connection hash declarations.
- APIs for allocation, refcounting, request queueing, transport init/destroy, writes, RDMA I/O, handler loop, and status transitions.
- Inline status predicates/setters using `READ_ONCE()`/`WRITE_ONCE()`.

## Dependencies And Role
This is the central contract between transport code, work processing, SMB dialect logic, and session management.

## Risks
The connection struct contains many cross-module lifetimes. Status changes and xarray/session locking must remain consistent to avoid use-after-free, hung shutdown, or incorrect reconnect/session setup behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/connection.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/crypto_ctx.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/crypto_ctx.c

Read status: complete.

## Purpose
Provides a small reusable pool of ksmbd AEAD crypto contexts for SMB3 encryption/decryption.

## Main Responsibilities
- Allocate AES-GCM and AES-CCM `crypto_aead` transforms on demand.
- Maintain an idle context list protected by a spinlock and wait queue.
- Limit retained contexts relative to online CPU count.
- Release contexts back to the pool or free excess contexts.
- Initialize and destroy the global crypto context pool.

## Dependencies And Role
Used by `auth.c` transform encryption/decryption to avoid repeated AEAD allocation overhead.

## Risks
Pool accounting and wait behavior must remain correct under memory pressure and concurrent encrypted I/O. The enum values are sparse, so array bounds checks in lookup are important.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/crypto_ctx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/crypto_ctx.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/crypto_ctx.h

Read status: complete.

## Purpose
Declares ksmbd pooled AEAD crypto context structures and APIs.

## Main Contents
- AEAD IDs for AES-GCM and AES-CCM.
- `struct ksmbd_crypto_ctx` with transform array and list node.
- `CRYPTO_GCM()` and `CRYPTO_CCM()` access macros.
- APIs to find/release contexts and create/destroy the pool.

## Dependencies And Role
Included by SMB3 transform crypto code.

## Risks
The transform array indexing depends on enum values and `CRYPTO_AEAD_MAX`; changes must preserve bounds and macro correctness.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/crypto_ctx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/glob.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/glob.h

Read status: complete.

## Purpose
Defines ksmbd-wide debug flags, logging format, Unicode helper macro, and default GFP flags.

## Main Contents
- `ksmbd_debug_types` extern and debug class bits for SMB/auth/VFS/oplock/IPC/connection/RDMA.
- `pr_fmt` override to prefix logs with `ksmbd` and optional submodule name.
- `ksmbd_debug()` conditional logging macro.
- `UNICODE_LEN()` and `KSMBD_DEFAULT_GFP`.

## Dependencies And Role
Included broadly by ksmbd source files for common logging and allocation policy.

## Risks
Debug flag names are token-pasted by `ksmbd_debug(type, ...)`; callers must use valid class names. Allocation policy changes affect many paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/glob.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/ksmbd_netlink.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/ksmbd_netlink.h

Read status: complete.

## Purpose
Defines the packed generic-netlink ABI between the kernel ksmbd server and its userspace IPC daemon.

## Main Contents
- Generic netlink name/version and maximum account/hash/share-name sizes.
- Startup, shutdown, heartbeat, login, login-extension, share-config, tree-connect, tree-disconnect, logout, RPC, and SPNEGO auth request/response structs.
- Payload helper macros/functions for variable-length interface, veto-list, share-path, RPC, and SPNEGO data.
- Event enum with request/response pairing assumptions.
- User, share, tree-connect, RPC, and config option flags/status constants.

## Dependencies And Role
This is a userspace ABI consumed by transport IPC and ksmbd-tools. It supplies account database, share configuration, tree authorization, RPC offload, and Kerberos/SPNEGO data to kernel code.

## Risks
ABI layout is packed and externally visible. Field size, enum value, flag, or payload-layout changes require userspace coordination and backward-compatibility care.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/ksmbd_netlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/ksmbd_work.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/ksmbd_work.c

Read status: complete.

## Purpose
Allocates, frees, queues, and prepares per-request `ksmbd_work` objects and response iovec arrays.

## Main Responsibilities
- Create/destroy the slab cache for `ksmbd_work`.
- Create/destroy the per-CPU ksmbd I/O workqueue.
- Allocate work objects with default compound FIDs, list heads, aux-read list, and initial kvec array.
- Free response/request buffers, transform buffers, aux read buffers, async IDs, and kvec storage.
- Queue work to `ksmbd-io`.
- Pin response buffers and optional read auxiliary buffers into kvecs while updating RFC1001 length.
- Allocate interim response buffers.

## Dependencies And Role
Used by SMB request dispatch and response construction. Integrates with connection async IDAs and RFC1002 framing helpers.

## Risks
Response iovec growth and RFC1001 length accounting are central to correct replies. Aux-read ownership and async ID release must stay aligned with all error paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/ksmbd_work.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/ksmbd_work.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/ksmbd_work.h

Read status: complete.

## Purpose
Defines the per-request ksmbd work object and workqueue/iovec helper APIs.

## Main Contents
- Work state enum values.
- `struct aux_read`.
- `struct ksmbd_work` containing connection/session/tree pointers, request/response buffers, compound offsets/FIDs, credentials, credits, transform state, async cancel data, response iovecs, and list nodes.
- Inline helpers for current/next compound request and response buffers.
- Allocation, free, pool, workqueue, response pinning, and interim response APIs.

## Dependencies And Role
This is the request execution context shared by SMB command handlers, transport code, auth, and management paths.

## Risks
Many subsystems store transient state in `ksmbd_work`; buffer offset helpers assume SMB response/request buffers include the 4-byte RFC1002 prefix.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/ksmbd_work.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/ksmbd_ida.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/ksmbd_ida.c

Read status: complete.

## Purpose
Wraps Linux IDA allocation for ksmbd protocol IDs.

## Main Responsibilities
- Allocate SMB2 tree IDs in the valid 1..0xFFFFFFFE range.
- Allocate SMB2 user/session IDs while avoiding reserved `0xFFFE`.
- Allocate async message IDs and generic IDs.
- Release IDs back to an IDA.

## Dependencies And Role
Used by session, tree-connect, async work, and IPC/RPC management code.

## Risks
Protocol-reserved values must not be handed out. ID leaks or double releases affect long-running server stability.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/ksmbd_ida.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/ksmbd_ida.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/ksmbd_ida.h

Read status: complete.

## Purpose
Declares ksmbd IDA allocation helpers and documents SMB reserved TID/UID values.

## Main Contents
- Comments for SMB TID and UID generation constraints.
- Prototypes for SMB2 TID, SMB2 UID, async message ID, generic ID acquisition, and ID release.

## Dependencies And Role
Provides the ID allocation contract for management code.

## Risks
Documentation and implementation must stay aligned with SMB protocol reserved values.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/ksmbd_ida.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/share_config.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/share_config.c

Read status: complete.

## Purpose
Caches and manages share configuration fetched from the ksmbd userspace IPC daemon.

## Main Responsibilities
- Hash share configs by casefolded share name and refcount cached entries.
- Request share metadata from userspace and validate returned share name.
- Parse share flags, masks, forced UID/GID, path, and veto patterns.
- Trim trailing slashes from share paths and resolve them with temporary fsuid/fsgid override.
- Support IPC pipe shares without backing path resolution.
- Handle stale share updates requested by userspace.
- Match filenames against per-share veto wildcard patterns.

## Dependencies And Role
Used by tree connect and VFS paths to map SMB share names to local paths and policy flags.

## Risks
Share path resolution runs under overridden credentials and must be reverted reliably. Payload sizing for veto list plus path is ABI-driven; malformed userspace data can otherwise corrupt share config state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/share_config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/share_config.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/share_config.h

Read status: complete.

## Purpose
Defines cached share configuration state and helper APIs.

## Main Contents
- `struct ksmbd_share_config` with name, path, flags, veto list, resolved `struct path`, refcount, hash node, create/directory masks, and forced UID/GID fields.
- Invalid UID/GID sentinels.
- Inline helpers for create and directory mode calculation.
- Flag testing and share config get/put/delete APIs.
- Veto filename match API.

## Dependencies And Role
Consumed by tree connections and VFS create/path handling.

## Risks
Refcounted share configs own resolved paths and veto lists. Mode helper behavior depends on Samba-like mask/force semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/share_config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/tree_connect.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/tree_connect.c

Read status: complete.

## Purpose
Creates, looks up, and disconnects per-session tree connections to shares.

## Main Responsibilities
- Fetch share configuration and allocate a `ksmbd_tree_connect`.
- Allocate tree IDs from the session IDA.
- Ask userspace IPC to authorize tree connection using session, share, tree, and peer address data.
- Handle share config update requests by refreshing stale cached shares.
- Store connected trees in the session xarray.
- Refcount tree connections and release associated share configs.
- Notify userspace on tree disconnect and session logoff.
- Destroy all tree connections during session logoff.

## Dependencies And Role
Bridges SMB2 TREE_CONNECT/TREE_DISCONNECT behavior with share config cache, sessions, IPC, and counters.

## Risks
Tree ID release, xarray erase, IPC disconnect notification, and refcount release must happen exactly once. Update handling must avoid using stale share config after userspace requests refresh.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/tree_connect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/tree_connect.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/tree_connect.h

Read status: complete.

## Purpose
Defines ksmbd tree-connect state and APIs.

## Main Contents
- Tree states: new, connected, disconnected.
- `struct ksmbd_tree_connect` with tree ID, flags, share config, user, access state, POSIX-extension flag, refcount, and state.
- `struct ksmbd_tree_conn_status` return wrapper.
- Flag test helper and APIs for connect, put, disconnect, lookup, and session logoff.

## Dependencies And Role
Used by SMB command handlers to bind session requests to shares.

## Risks
Lookup only returns `TREE_CONNECTED` refs; callers must put returned tree connections to avoid leaked share refs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/tree_connect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_config.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_config.c

Read status: complete.

## Purpose
Fetches, allocates, compares, and frees ksmbd user account configuration.

## Main Responsibilities
- Request login data from userspace IPC and optional supplementary group extension data.
- Allocate `ksmbd_user` with account name, flags, uid/gid, password hash, and supplementary groups.
- Notify userspace on logout during user free.
- Detect anonymous users by empty account name.
- Compare users by name and passkey.

## Dependencies And Role
Used by authentication/session setup and session destruction.

## Risks
Passkey allocation/copy depends on userspace-provided hash size. `ksmbd_compare_user()` assumes comparable passkey sizes are checked by callers where needed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_config.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_config.h

Read status: complete.

## Purpose
Defines ksmbd user account state and accessors.

## Main Contents
- `struct ksmbd_user` with flags, uid, gid, name, passkey, and supplementary groups.
- Helpers for guest flag, arbitrary user flags, passkey/name/uid/gid access.
- APIs for login, allocation from IPC responses, free, anonymous check, and comparison.

## Dependencies And Role
Shared by auth, session, and tree-connect code.

## Risks
The empty `set_user_guest()` helper is intentionally inert in this version; callers should rely on flags from userspace rather than expecting it to mutate state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_session.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_session.c

Read status: complete.

## Purpose
Manages ksmbd SMB2 sessions, channel binding, per-session tree connections, RPC handles, proc reporting, preauth sessions, and session teardown.

## Main Responsibilities
- Allocate/register SMB2 sessions with global hash table and per-connection xarray entries.
- Maintain session refcounts, expiration, lookup, deregistration, and destruction.
- Track channels for SMB3 multichannel/binding via session channel xarray.
- Display sessions and per-session details through proc when enabled.
- Manage per-session RPC pipe handles and map pipe names to userspace RPC methods.
- Log off tree connections, destroy open-file tables, free users, close RPC handles, free channels, release IDs, and launch durable scavenger on session destroy.
- Allocate and look up preauth session snapshots for SMB 3.1.1 channel binding.
- Destroy previous sessions when the same user reconnects with a previous session ID.

## Dependencies And Role
Central session lifecycle layer used by SMB2 session setup, tree connect, file table, RPC over IPC, multichannel, and connection teardown.

## Risks
High-risk areas are nested locking across global sessions, per-connection sessions, channels, and tree connections; session refcount ownership; previous-session reconnect waiting; and binding lookups that cross connection boundaries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_session.c -->