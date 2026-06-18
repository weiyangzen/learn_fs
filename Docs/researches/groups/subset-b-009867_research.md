# Research: subset-b-009867

Grouped research for Samba smbd POSIX ACL, quota, scavenger, sealing, Python binding, and prototype surface files. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/posix_acls.c -->
# sources/user-network-fs/samba/source3/smbd/posix_acls.c

## Purpose
This file is smbd's POSIX ACL to Windows security descriptor bridge. It reads POSIX access/default ACLs and file ownership through the VFS layer, exposes them as NT security descriptors, accepts NT ACL writes, converts those into POSIX ACLs or chmod mode bits, and preserves selected Windows inheritance metadata in the `user.SAMBA_PAI` extended attribute when `map acl inherit` is enabled. It is also the implementation behind several UNIX extensions that set raw POSIX ACL wire formats.

## Important APIs, Types, And Functions
The central internal type is `canon_ace`, a doubly linked canonical ACE carrying a POSIX ACL tag, UNIX uid/gid/world identity, mapped SID, ALLOW/DENY attribute, `S_IRUSR/S_IWUSR/S_IXUSR`-normalized permissions, and Windows ACE flags. `pai_entry` and `pai_val` model the on-disk Samba POSIX ACL inheritance EA, with v1 compatibility and v2 storage of security descriptor type and ACE flags.

Exported functions declared in `proto.h` include `unix_perms_to_acl_perms`, `map_acl_perms_to_permset`, `map_canon_ace_perms`, `current_user_in_group`, `free_empty_sys_acl`, `posix_fget_nt_acl`, `chown_if_needed`, `set_nt_acl`, `get_acl_group_bits`, `inherit_access_posix_acl`, `set_unix_posix_default_acl`, `set_unix_posix_acl`, `posix_sys_acl_blob_get_fd`, `get_default_acl_style_list`, and `make_default_filesystem_acl`. The key read path is `posix_fget_nt_acl` -> `posix_get_nt_acl_common` -> `canonicalise_acl` -> `map_canon_ace_perms`. The key write path is `set_nt_acl` -> `chown_if_needed` -> `unpack_canon_ace` -> `create_canon_ace_lists` -> `merge_aces`/`process_deny_list` -> `set_canon_ace_list`, with chmod fallback through `convert_canon_ace_to_posix_perms`.

## Control Flow
On ACL read, smbd `fstat`s the file, fetches access ACLs and directory default ACLs with `SMB_VFS_SYS_ACL_GET_FD`, reads inheritance metadata with `fload_inherited_info`, canonicalizes POSIX entries into `canon_ace` lists, applies POSIX mask entries, arranges owner first and other last, maps entries to NT ACEs, merges access/default pairs for Windows inheritance display, builds a security descriptor, and marks the DACL protected unless PAI data says otherwise.

On ACL write, the incoming descriptor is copied because helper code normalizes it in place. Ownership/group SIDs are mapped first and `try_chown` applies root, privilege, take-ownership, or `dos filemode` rules. DACLs are then transformed into file and directory canonical ACE lists. Unsupported ACE types fail; non-mappable system SIDs can be ignored, while unknown user/group SIDs fail unless `force unknown acl user` is enabled. The deny handling is deliberately conservative: DENY ACEs are folded into ALLOW-only POSIX semantics by masking later ALLOW entries, converting user and group denies into explicit reduced allow entries, and failing closed when permissions cannot be represented. The result is written as POSIX ACLs if supported, including generated mask entries, or as chmod mode bits if the filesystem reports no ACL support.

## State And Persistence
Persistent state is primarily filesystem metadata: POSIX ACLs, chmod mode bits, owner/group ids, and optionally `SAMBA_POSIX_INHERITANCE_EA_NAME` (`user.SAMBA_PAI`) xattrs. PAI v2 records descriptor type plus ACE flags for access and default ACL lists; v1 is still decoded to preserve inherited/protected state on older files. Runtime state is talloc-scoped canonical ACE lists and PAI structures. Privilege state is temporarily changed with `become_root`/`unbecome_root` for privileged chown, ACL override, and xattr operations.

## Dependencies And Integration Points
The file depends on Samba security descriptor/SID helpers, idmap (`sids_to_unixids`, `uid_to_sid`, `gid_to_sid`), VFS ACL operations, loadparm policy flags (`acl map full control`, `dos filemode`, `acl group control`, `map acl inherit`, `inherit owner`, `force unknown acl user`), and smbd security context helpers. It is consumed by SMB1/SMB2 security descriptor query/set paths, DOS mode code via `get_acl_group_bits`, UNIX extensions ACL setters, create/inheritance paths through `inherit_access_posix_acl`, VFS snapshot/blob export through `posix_sys_acl_blob_get_fd`, and default ACL synthesis for filesystems without native descriptors.

## Risks And Test Signals
High-risk areas are DENY-to-POSIX semantic reduction, idmap `ID_TYPE_BOTH` expansion into both user and group entries, preserving owner/group access after chown, ACL mask handling, PAI xattr corruption/size checks, default ACL inheritance round trips, and chmod fallback when ACL syscalls partially work. Tests should cover NT security descriptor get/set round trips on files and directories, inherited ACE flags with `map acl inherit`, owner/group changes under root and non-root privilege cases, `dos filemode` and `acl group control` overrides, non-mappable and unknown SIDs, POSIX ACL removal via UNIX extensions, default ACL deletion, filesystems with no ACL support, and directory trees where access/default ACEs must merge back into Windows-style inheritable ACEs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/posix_acls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/proto.h -->
# sources/user-network-fs/samba/source3/smbd/proto.h

## Purpose
This header is the broad internal prototype map for source3 smbd. It gathers declarations from many smbd compilation units so legacy and cross-module C code can call server routines for signing, async I/O, byte-range locking, connection management, DOS mode handling, path resolution, file table operations, notifications, quotas, ACLs, SMB packet processing, encryption, security context switching, service/session management, VFS helpers, and SMB2 create support.

## Important APIs, Types, And Functions
The header forward-declares major server types such as `smbXsrv_client`, `smbXsrv_connection`, `dcesrv_context`, and several operation-specific structs. It exposes grouped declarations by implementation file. For this work item, the important groups are `posix_acls.c` (`posix_fget_nt_acl`, `set_nt_acl`, `set_unix_posix_acl`, default ACL helpers), `quotas.c` (`disk_quotas`), and `seal.c` (`is_encrypted_packet`, `srv_decrypt_buffer`, `srv_encrypt_buffer`, `srv_request_encryption_setup`, `srv_encryption_start`, `server_encryption_shutdown`). It also declares the adjacent dependencies those files use, including pathref open/close helpers, security context helpers, VFS operations, and SMB request processing entry points.

## Control Flow
`proto.h` has no runtime control flow. Its compile-time organization mirrors smbd subsystems, with comments identifying the source file for each declaration block. Include guards prevent repeated declarations, and conditional blocks expose quota query helpers only when `HAVE_SYS_QUOTAS` or SMB1-server build choices make them valid.

## State And Persistence
The header stores no runtime state and persists no data. Its practical state is C ABI coupling: signatures here must match definitions exactly, and any mismatch can become compiler warnings, link errors, or undefined behavior depending on build flags.

## Dependencies And Integration Points
Because this is a central smbd header, it integrates almost every file-server subsystem. It relies on types from `smbd.h`, Samba security/ACL headers, tevent, messaging, VFS, locking, notify, and SMB request structures being available through normal include chains. Changes to declarations here affect call sites throughout source3 and, for non-static functions, the internal module boundary.

## Risks And Test Signals
Risks are stale prototypes after implementation changes, accidental exposure of functions that should stay file-local, conditional declaration drift across build configurations, and ABI mismatches for structs or enum types declared elsewhere. Test signals are full matrix compilation with SMB1 enabled/disabled, quota support enabled/disabled, POSIX ACL support enabled/disabled, and warning-clean builds that include call sites for ACL, quota, seal, VFS, and SMB2 create paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/pysmbd.c -->
# sources/user-network-fs/samba/source3/smbd/pysmbd.c

## Purpose
This file implements the Python extension module `smbd`, exposing selected smbd VFS, NT ACL, POSIX ACL, ownership, unlink, mkdir, and create-file operations to Samba Python tooling. It lets Python code perform filesystem changes through smbd's connection, VFS, ACL, SID, and security-context machinery instead of using raw POSIX calls.

## Important APIs, Types, And Functions
The module exports `have_posix_acls`, `set_simple_acl`, `set_nt_acl`, `get_nt_acl`, `get_sys_acl`, `set_sys_acl`, `chown`, `unlink`, `mkdir`, and `create_file`. Internal helpers include `get_conn_tos`, which builds a temporary `connection_struct` for a service and `auth_session_info`; `canonicalize_path`; `init_files_struct`, which opens a path and initializes enough `files_struct` fields for VFS/ACL operations; `set_nt_acl_conn`/`get_nt_acl_conn`; `set_sys_acl_conn`; and `make_simple_acl`. `fchdir_state` restores the caller's working directory when the temporary connection wrapper is freed.

## Control Flow
Each Python wrapper validates argument types, especially `samba.dcerpc.auth.session_info` and NDR-backed security/ACL objects, creates a temporary talloc frame, obtains a smbd connection with `get_conn_tos`, converts paths into `smb_filename` or `files_struct` objects, performs the relevant VFS or ACL operation, maps NTSTATUS/errno failures into Python exceptions, and frees the frame. File and ACL operations generally open a pathref or real fd, call `SMB_VFS_*` functions, and close the `files_struct` with `fd_close`. Directory creation and unlink use parent path references plus `SMB_VFS_MKDIRAT`/`SMB_VFS_UNLINKAT`.

## State And Persistence
Runtime state is temporary and talloc-scoped, but operations persist filesystem changes: ACL updates, owner/group changes, file creation, directory creation, and unlinking. `get_conn_tos` mutates process working directory indirectly through connection setup, then relies on a talloc destructor to `fchdir` back to the saved descriptor. It also initializes POSIX locking and resets the mangle cache. Created files and directories force `umask(0)` temporarily to keep smbd in control of permissions.

## Dependencies And Integration Points
The file depends on Python C APIs, Samba `pytalloc`, NDR Python converters, auth/session structures, passdb/secrets initialization context, smbd VFS helpers, pathref helpers, POSIX ACL wrappers, NT ACL routines from the VFS, and loadparm service lookup. It is used by Samba Python administration and test code that needs smbd-equivalent ACL behavior, especially when service-specific VFS modules or security tokens matter.

## Risks And Test Signals
Risks include incomplete `files_struct` initialization relative to full smbd open paths, cwd restoration assertions in destructor paths, Python exception paths that may leak fds if close ordering changes, errno/NTSTATUS mapping inconsistencies, service lookup failures, and operations bypassing normal share read-only restrictions by explicitly setting `conn->read_only = false` and full share access. Tests should import the module, exercise each method with valid and invalid session_info, run against paths inside and outside named services, verify cwd restoration after failures, round-trip NT and POSIX ACLs, test directory vs file open fallback, confirm FileNotFoundError mapping, and validate VFS module behavior under Python-driven creates/unlinks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/pysmbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/quotas.c -->
# sources/user-network-fs/samba/source3/smbd/quotas.c

## Purpose
This file provides smbd's `disk_quotas` implementation: a best-effort way to report share free/total space according to user or group quota limits instead of raw filesystem capacity. It contains legacy Solaris/NFS quota code for builds without the newer sysquotas interface and a VFS-backed implementation when `HAVE_SYS_QUOTAS` is available.

## Important APIs, Types, And Functions
The exported API is `disk_quotas(connection_struct *conn, struct files_struct *fsp, uint64_t *bsize, uint64_t *dfree, uint64_t *dsize)`. In Solaris legacy builds, `nfs_quotas`, `my_xdr_getquota_args`, and `my_xdr_getquota_rslt` query remote rquota over RPC and parse `/etc/mnttab`/quota files. In the modern path, `disk_quotas` uses `SMB_VFS_GET_QUOTA` with `SMB_USER_FS_QUOTA_TYPE`, `SMB_USER_QUOTA_TYPE`, `SMB_GROUP_FS_QUOTA_TYPE`, and `SMB_GROUP_QUOTA_TYPE`.

## Control Flow
With sysquotas, the function first checks whether user quotas are enforced. If they are, it queries the current effective uid or, when owner inheritance means new files are owned by the directory owner, the directory/file uid under root. If the user quota is not usable, it tries group quota enforcement and then either the directory gid for setgid directories or the current effective gid. Soft limits define reported size/free space unless limits are exceeded, in which case free space is zero and total size is current usage. If quotas are disabled, unsupported, or unlimited, it returns false so callers can fall back to normal disk-free calculation.

## State And Persistence
The file does not modify quota state. It reads quota records through VFS or platform RPC/ioctl calls and writes only output values. It temporarily escalates with `become_root`/`unbecome_root` for quota lookups that must inspect inherited owner/group quota records.

## Dependencies And Integration Points
`disk_quotas` is declared in `proto.h` and feeds `get_dfree_info`/disk space reporting. It depends on `files_struct->fsp_name` stat data, loadparm `inherit owner`, current effective uid/gid, VFS quota operations, and platform quota headers. The Solaris path integrates with mount-table parsing, UFS/VxFS quota files, and NFS rquota RPC.

## Risks And Test Signals
Risks include quota enforcement detection differing by filesystem, soft-vs-hard-limit interpretation, inherited owner/group quota selection, setgid directory group handling, stale stat data, root escalation around VFS calls, and legacy Solaris/NFS RPC assumptions. Tests should cover user quota enforced, user quota disabled with group fallback, unlimited quotas, exceeded block and inode limits, inherited owner directories, setgid directories, ENOSYS from VFS modules, and normal dfree fallback when `disk_quotas` returns false.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/quotas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/scavenger.c -->
# sources/user-network-fs/samba/source3/smbd/scavenger.c

## Purpose
This file implements the smbd scavenger helper process that cleans up disconnected durable opens after their timeout expires. Parent smbd processes schedule cleanup work by messaging a parent-owned scavenger controller, which starts or reuses a forked `smbd-scavenger` child and forwards cleanup messages to it.

## Important APIs, Types, And Functions
The exported functions are `smbd_scavenger_init` and `scavenger_schedule_disconnected`. Internal state lives in `smbd_scavenger_state` with tevent/messaging contexts, parent server id, optional scavenger server id, and an `am_scavenger` flag. `scavenger_message` contains `file_id`, `open_persistent_id`, and an absolute `NTTIME until`. Cleanup-specific helpers include `scavenger_add_timer`, `scavenger_timer`, `share_mode_cleanup_disconnected`, and `cleanup_disconnected_share_mode_entry_fn`.

## Control Flow
Initialization registers `MSG_SMB_SCAVENGER`. A disconnected durable open calls `scavenger_schedule_disconnected`, computes the timeout from disconnect time plus durable timeout, asserts the open is marked disconnected, and sends a `scavenger_message` to the original parent smbd. The parent-side message handler starts the scavenger if needed using `socketpair` and `fork`, waits for the child to send its `server_id`, then forwards the message. The child reinitializes smbd state after fork, sets process title and logging, watches the parent pipe for death, handles SIGTERM, receives only parent-origin messages, and schedules tevent timers. Timer expiry first calls `smbXsrv_open_cleanup`, then removes byte-range locks and share-mode entries for the disconnected persistent open, and removes stale leases if needed.

## State And Persistence
Persistent effects are cleanup of global open records, byte-range locks, share-mode entries, and lease records. Runtime state includes one global `smbd_scavenger_state`, a forked helper process, socketpair fd monitors used for parent/child liveness, messaging registrations, and tevent timers holding copied cleanup messages. The child exits cleanly if the parent pipe becomes readable/dead.

## Dependencies And Integration Points
The file depends on smbd globals, messaging, serverid, tevent, fork reinitialization, share mode locking, byte-range lock cleanup, leases DB cleanup, open-global cleanup, and process/logging utilities. It integrates with durable handle disconnect paths and the locking subsystem; its correctness depends on disconnected server ids and persistent open ids matching share-mode records.

## Risks And Test Signals
Risks include failing to start the child under fork/socketpair pressure, message loss if the parent dies, cleanup timers scheduled with corrupt or stale messages, races with durable reconnect before timeout, panics if a supposedly disconnected share-mode entry is owned by a live server, and partial cleanup when open-global cleanup succeeds but share-mode/BRL cleanup fails. Tests should cover init idempotency, child restart after death, parent death handling, schedule timing, durable reconnect-before-timeout behavior, cleanup of share modes, byte-range locks and leases, spurious sender messages ignored by the child, and fork/reinit failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/scavenger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/scavenger.h -->
# sources/user-network-fs/samba/source3/smbd/scavenger.h

## Purpose
This header declares the public smbd scavenger interface for initializing the durable-open cleanup helper and scheduling disconnected opens for later cleanup.

## Important APIs, Types, And Functions
It exposes `bool smbd_scavenger_init(TALLOC_CTX *mem_ctx, struct messaging_context *msg, struct tevent_context *ev)` and `void scavenger_schedule_disconnected(struct files_struct *fsp)`. It intentionally hides `smbd_scavenger_state`, message formats, timer contexts, and cleanup helpers inside `scavenger.c`.

## Control Flow
The header has no runtime control flow. Callers include it to initialize the message handler during smbd setup and to schedule cleanup when a durable open transitions to disconnected.

## State And Persistence
No state lives in the header. The declared functions mutate runtime scavenger state and eventually persistent locking/open databases as described in `scavenger.c`.

## Dependencies And Integration Points
The declarations require visible Samba types for talloc, messaging, tevent, and `files_struct` from the including compilation unit's normal smbd headers. The header is the narrow integration boundary between durable-open code and the scavenger implementation.

## Risks And Test Signals
Risks are minimal but include missing prototypes when callers do not include the right type definitions first and accidental broadening of the interface if internals are moved here. Test signals are compile coverage for smbd setup and durable disconnect call sites, plus runtime tests covered by `scavenger.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/scavenger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/seal.c -->
# sources/user-network-fs/samba/source3/smbd/seal.c

## Purpose
This file implements server-side SMB1 transport encryption, historically called sealing. It negotiates a gensec SPNEGO security context with seal support, identifies encrypted packets, decrypts incoming buffers, encrypts outgoing buffers, and tears down partial or active encryption contexts.

## Important APIs, Types, And Functions
The exported API is `is_encrypted_packet`, `srv_free_enc_buffer`, `srv_decrypt_buffer`, `srv_encrypt_buffer`, `srv_request_encryption_setup`, `srv_encryption_start`, and `server_encryption_shutdown`. Internal helpers include `srv_enc_ctx`, `make_auth_gensec`, `make_srv_encryption_context`, and `check_enc_good`. Runtime context is held in global `partial_srv_trans_enc_ctx` during negotiation and `srv_trans_enc_ctx` after successful start; both are `smb_trans_enc_state` objects with gensec state and encryption context numbers.

## Control Flow
Packet detection ignores non-session messages, checks for the `0xFF 'E'` encrypted marker, extracts the encryption context number, and compares it to the active server context. Negotiation starts lazily in `srv_request_encryption_setup`, creating an auth gensec context with `GENSEC_FEATURE_SEAL`, starting SPNEGO as root, then feeding client blobs to `gensec_update`. While more processing is required it returns only a response blob; on success it also returns the two-byte context id in the transaction parameters. `srv_encryption_start` verifies the negotiated context has signing and sealing, frees any old active context, moves the partial context to active, and marks encryption on. Buffer encryption/decryption call common SMB sealing helpers only for session messages and only when an active context exists.

## State And Persistence
State is process-local and talloc-managed: one partial negotiation context and one active transport encryption context. No on-disk state is written. Temporary root privilege is used because gensec may need secrets or keytab access during mechanism start/update. Encrypted outgoing buffers may be newly allocated and must be released through `srv_free_enc_buffer`.

## Dependencies And Integration Points
The file depends on SMB sealing helpers in `libcli/smb/smb_seal.h`, gensec/auth setup, tsocket local/remote addresses, smbd globals, and SMB packet framing helpers. It integrates with SMB1 packet receive/send paths through `proto.h`: receive code can ask whether a packet is encrypted, decrypt buffers before processing, encrypt replies, and shut down contexts when the connection ends.

## Risks And Test Signals
Risks include reliance on global single-context state, accepting only packets whose context number matches the active context, cleanup of partial contexts on negotiation failure, privilege transitions around gensec calls, memory ownership of encrypted buffers, and ensuring signing plus sealing are both negotiated before activation. Tests should cover multi-step SPNEGO setup, failed mechanism start/update, encrypted marker parsing with short or malformed packets, context-number mismatch, encrypt/decrypt round trips, non-session message pass-through, shutdown during partial negotiation, and connection replacement of an existing active context.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/seal.c -->
