# Group Research: group_1070_linux_stable_sources_os_linux_linux_stable_fs_smb_client_cifsacl_c__30e33182541e

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsacl.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsacl.c

Read status: complete.

## Purpose

Implements CIFS/SMB security descriptor, SID, ACE, ACL, UID/GID, mode-bit, and POSIX ACL translation logic. This file is the bridge between Windows/CIFS NT security descriptors and Linux VFS ownership/permission attributes.

## Main Responsibilities

- Registers and tears down the `cifs.idmap` key type used for SID-to-id and id-to-SID request-key upcalls.
- Maps SIDs to Linux `kuid_t`/`kgid_t` values, including fast paths for well-known Unix SID forms.
- Maps Linux UID/GID values back to SIDs for chown/chgrp operations.
- Parses NT security descriptors and DACLs into `struct cifs_fattr` ownership and mode fields.
- Builds modified security descriptors for chmod/chown/chgrp and sends them back to the server.
- Converts between POSIX mode bits and CIFS ACE access masks.
- Supports special SIDs used by NFS/Apple-style SMB servers for Unix uid/gid/mode persistence.
- Provides legacy CIFS ACL get/set helpers when insecure legacy and POSIX ACL support are compiled in.

## Key Data and Constants

- Well-known SIDs:
  - `sid_everyone`
  - `sid_authusers`
  - `sid_unix_users`
  - `sid_unix_groups`
  - `sid_unix_NFS_users`
  - `sid_unix_NFS_groups`
  - `sid_unix_NFS_mode`
- `root_cred` stores a kernel credential with a private `.cifs_idmap` thread keyring for idmap upcall caching.
- SID types use `SIDOWNER` and `SIDGROUP` to distinguish owner and group mappings.

## Important Functions

- `cifs_idmap_key_instantiate()` / `cifs_idmap_key_destroy()`
  - Key payload lifetime handlers for `cifs.idmap`.
  - Small payloads are stored inline in the key payload union; larger payloads are copied with `kmemdup()`.

- `init_cifs_idmap()` / `exit_cifs_idmap()`
  - Register/unregister the `cifs.idmap` key type.
  - Allocate/revoke the private keyring used by root override credentials.

- `sid_to_key_str()`
  - Converts an SMB SID into request-key text such as owner/group SID keys.
  - Handles 48-bit SID authority formatting, including hex formatting for large authorities.

- `compare_sids()`
  - Lexicographically compares SID revision, authority bytes, and subauthorities.

- `is_well_known_sid()`
  - Recognizes `S-1-22-*` and `S-1-5-88-*` Unix SID forms.
  - Extracts Unix uid/gid directly when possible.

- `id_to_sid()`
  - Requests a SID from userspace for a Linux uid/gid using `oi:<id>` or `gi:<id>` key descriptions.
  - Validates returned SID payload length before copying.

- `sid_to_id()`
  - Maps a SID into `fattr->cf_uid` or `fattr->cf_gid`.
  - Uses direct Unix SID extraction for `idsfromsid` or SMB POSIX extensions before falling back to idmap upcall.
  - Falls back to mount uid/gid on failed mapping and returns success unless malformed SID/key data is detected.

- `validate_dacl()`
  - Bounds-checks DACL and ACE layout.
  - Rejects undersized ACLs, invalid ACE sizes, zero subauthority SIDs in ACEs, and excessive subauthority counts.

- `parse_dacl()`
  - Converts matching owner/group/everyone/authenticated-users ACEs into mode bits.
  - Supports special `S-1-5-88-3` mode SID when `mode_from_special_sid` is enabled.

- `access_flags_to_mode()` / `mode_to_access_flags()`
  - Convert between CIFS access masks and POSIX rwx bits.
  - Preserves deny/allow ordering semantics and uses `FILE_DELETE_CHILD` to approximate sticky-bit behavior.

- `populate_new_aces()`
  - Creates replacement ACEs for chmod.
  - Handles `modefromsid`, SMB POSIX mode SID behavior, deny ACEs for restrictive owner/group modes, and sticky-bit delete-child handling.

- `set_chmod_dacl()`
  - Retains unrelated ACEs, replaces owner/group/everyone/authenticated-users/mode ACEs, and preserves inherited ACE ordering.

- `build_sec_desc()`
  - Builds a new security descriptor for chmod/chown/chgrp.
  - Can synthesize owner/group SIDs from special `S-1-5-88-{1,2}` form when `idsfromsid` is active, otherwise uses idmap upcalls.

- `parse_sec_desc()`
  - Extracts owner SID, group SID, and DACL from a security descriptor and updates `struct cifs_fattr`.

- `cifs_acl_to_fattr()`
  - Public conversion path used by inode attribute code to populate mode/uid/gid from server ACLs.

- `id_mode_to_cifs_acl()`
  - Public conversion path used by chmod/chown/chgrp to retrieve an existing descriptor, build a modified one, and call dialect-specific `set_acl`.

- `cifs_get_acl()` / `cifs_set_acl()`
  - POSIX ACL xattr-style accessors for legacy CIFS POSIX support; return unsupported when not compiled in.

## Dependencies

- Uses structures from `cifsacl.h`, common SMB ACL definitions, `cifsglob.h`, `cifsproto.h`, and mount context state from `fs_context.h`.
- Calls dialect-specific operations through `server->ops->get_acl`, `get_acl_by_fid`, and `set_acl`.
- Uses request-key infrastructure, kernel credentials, POSIX ACL helpers, and Linux idmapping primitives.

## Notable Behaviors

- Malformed SID/DACL inputs are routed through `smb_EIO*()` helpers for traceable `-EIO`, or `-EINVAL` for illegal layout.
- The DACL parser does not require canonical ACE order; it tracks allow/deny effects as ACEs are encountered.
- Chmod can deliberately reduce the mode it reports back through `*pnmode` when the exact requested mode cannot be represented cleanly as NT ACEs.
- ACL read paths prefer an already open readable handle when available, avoiding path opens where possible.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsacl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsacl.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsacl.h

Read status: complete.

## Purpose

Defines CIFS/SMB ACL constants and wire-format structures used by ACL parsing and construction code.

## Main Contents

- Permission bit constants:
  - `READ_BIT`
  - `WRITE_BIT`
  - `EXEC_BIT`
  - owner/group/everyone ACL masks
  - user/group bit shifts

- `DEFAULT_SEC_DESC_LEN`
  - Conservative default allocation size for a security descriptor with a DACL and several ACEs.

- `struct smb3_sd`
  - SMB3 self-relative security descriptor layout matching MS-DTYP/MS-SMB2 naming.
  - Contains revision, control flags, and owner/group/SACL/DACL offsets.

- ACL control flag definitions:
  - Self-relative, protected, inherited, present/defaulted, and resource-manager flags.

- `struct smb3_acl`
  - SMB3 ACL header layout with revision, size, and ACE count.

- `struct owner_sid`
  - Packed representation for special `S-1-5-88-*` Unix uid/gid/mode SIDs.

- `struct owner_group_sids`
  - Pair of owner and group special SIDs.

- Minimum length constants:
  - `MIN_SID_LEN`
  - `MIN_SEC_DESC_LEN`

## Dependencies

- Includes `../common/smbacl.h` for shared SID/ACL/security-descriptor definitions.

## Role in the Subsystem

This header supplies the ACL code with stable wire-format layouts and bounds constants. It is tightly coupled to `cifsacl.c` and to SMB2/SMB3 security descriptor handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsacl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsencrypt.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsencrypt.c

Read status: complete.

## Purpose

Implements CIFS/SMB cryptographic helper routines for request signing and NTLM/NTLMv2 authentication response generation.

## Main Responsibilities

- Feed SMB request vectors and iterators into MD5, HMAC-SHA256, or AES-CMAC signing contexts.
- Build and parse NTLMSSP AV-pair target-info blobs.
- Construct NTLMv2 authentication responses, including timestamp, client challenge, SPN AV pair, and session key derivation.
- Generate the NTLM session key ciphertext using RC4 for legacy NTLMSSP paths.
- Release SMB3 encryption/decryption AEAD transform handles.

## Important Functions

- `cifs_sig_step()`, `cifs_sig_iter()`, `cifs_sig_final()`
  - Generic signing data path over `iov_iter`.
  - Chooses MD5, HMAC-SHA256, or AES-CMAC based on `struct cifs_calc_sig_ctx`.

- `__cifs_calc_signature()`
  - Calculates a signature over an SMB request’s kvecs and data iterator.
  - Rejects undersized request data and returns traceable `-EIO` on short iterator processing.

- `build_avpair_blob()`
  - Builds a minimal NTLM target-info blob for non-extended negotiate paths.
  - Defaults missing domain to `WORKGROUP`.

- `find_next_av()`, `find_av_name()`, `find_timestamp()`
  - Safe AV-pair iteration helpers.
  - Extract domain names and server timestamp from the NTLMSSP challenge; falls back to local time when no timestamp exists.

- `calc_ntlmv2_hash()`
  - Computes NTLMv2 hash from password NT hash, uppercase Unicode username, and Unicode domain or server IP.

- `set_auth_key_response()`
  - Replaces the session auth response buffer with a full NTLMv2 response layout.
  - Copies existing target info and appends `NTLMSSP_AV_TARGET_NAME` as `cifs/<hostname>` plus EOL.

- `setup_ntlmv2_rsp()`
  - High-level NTLMv2 response builder.
  - Handles domain auto-discovery, DNS domain extraction, timestamp selection, random client challenge, response HMAC, and session key derivation.
  - Disables NTLMv2 under FIPS mode because it relies on legacy MD4/MD5 primitives.

- `calc_seckey()`
  - Generates a random secondary key, encrypts it with RC4 using the NTLM response key, and stores the clear secondary key as the session key.
  - Disabled under FIPS mode.

- `cifs_crypto_secmech_release()`
  - Frees SMB3 AEAD encryption/decryption transforms on the server object.

## Dependencies

- Uses kernel crypto helpers for MD5, SHA/HMAC, AES-CMAC, AEAD, and ARC4.
- Uses session state from `struct cifs_ses` and server state from `struct TCP_Server_Info`.
- Relies on Unicode conversion helpers from `cifs_unicode.h`.

## Notable Behaviors

- Sensitive buffers are freed with `kfree_sensitive()` or wiped with `memzero_explicit()` where appropriate.
- AV-pair parsing validates alignment and bounds before conversion.
- `setup_ntlmv2_rsp()` serializes updates under `cifs_server_lock()` because it rewrites session authentication material tied to the server.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsencrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsfs.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsfs.c

Read status: complete.

## Purpose

Provides the CIFS/SMB client’s Linux VFS and module integration: filesystem registration, superblock setup, mount flow, inode/file operation tables, module parameters, cache/mempool/workqueue initialization, and module teardown.

## Main Responsibilities

- Defines global module knobs for dialect security, buffer sizing, directory cache timeout, oplocks, signing, encryption strength, and request concurrency.
- Registers the `cifs` and `smb3` filesystem types.
- Builds and tears down CIFS superblocks.
- Implements VFS super operations, inode operation tables, and file operation tables.
- Initializes inode caches, SMB request buffers, MID pools, netfs I/O pools, workqueues, DFS/SPNEGO/SWN/idmap subsystems, and procfs integration.
- Implements server-side copy/remap helpers and file lease behavior.

## Important Areas

### Module and Global State

- Exposes module parameters:
  - `CIFSMaxBufSize`
  - `cifs_min_rcv`
  - `cifs_min_small`
  - `cifs_max_pending`
  - `dir_cache_timeout`
  - `enable_oplocks`
  - `enable_gcm_256`
  - `require_gcm_256`
  - `enable_negotiate_signing`
  - `disable_legacy_dialects`
- Defines global counters and locks:
  - XID counters under `GlobalMid_Lock`
  - allocation/reconnect counters
  - TCP session list and lock
  - request and MID allocation counters

### Superblock Lifecycle

- `cifs_sb_active()` / `cifs_sb_deactive()`
  - Maintain active references from CIFS superblock state to VFS superblock lifetime.

- `cifs_read_super()`
  - Configures POSIX ACL flag, read-only snapshot state, max file size, time granularity/range, xattr handlers, readahead, block size, root inode, dentry ops, and optional export ops.

- `cifs_kill_sb()`
  - Closes cached directories and deferred files, flushes oplock/deferred-close workqueues, drops root dentry, kills the anonymous superblock, and unmounts CIFS state.

- `cifs_umount_begin()` / `cifs_freeze()`
  - Wake blocked request waiters on forced unmount paths and close deferred files during freeze.

### Mount Flow

- `cifs_smb3_do_mount()`
  - Duplicates mount context, sets up `cifs_sb_info`, performs CIFS mount, reuses or creates a superblock via `sget()`, reads the superblock, and resolves root/prefix dentry.
  - Sets `SB_NODIRATIME | SB_NOATIME`.

- `cifs_get_root()`
  - Walks the prefix path from the share root when the mount uses a subpath.

### VFS Operations

- `cifs_super_ops`
  - Supplies `statfs`, inode allocation/free/drop/evict, writeback, mount option display, unmount-begin, and freeze hooks.

- Inode operation tables:
  - `cifs_dir_inode_ops`
  - `cifs_file_inode_ops`
  - `cifs_symlink_inode_ops`

- File operation tables:
  - `cifs_file_ops`
  - `cifs_file_strict_ops`
  - `cifs_file_direct_ops`
  - no-byte-range-lock variants
  - `cifs_dir_ops`

- `cifs_permission()`
  - Supports `noperm` behavior while still rejecting execute when execute bits are not present.

- `cifs_llseek()`
  - Revalidates file size for non-trivial seeks and delegates dialect-specific seek when available.

- `cifs_setlease()`
  - Allows local leases only when compatible with oplock/cache state or `local_lease`.

### Copy and Remap

- `cifs_remap_file_range()`
  - Implements clone/remap through server `duplicate_extents` when available.
  - Flushes source, adjusts source EOF if needed, flushes/invalidate destination pages, updates netfs/fscache size state, and maps some unsupported overlap cases to `-EINVAL`.

- `cifs_file_copychunk_range()` and `cifs_copy_file_range()`
  - Use server-side copychunk when possible, falling back to splice copy for unsupported or cross-device cases.
  - Maintains pagecache, fscache, inode size, and zero-point state.

### Initialization and Teardown

- `init_cifs()`
  - Initializes error maps, procfs, global counters, workqueues, inode/netfs/MID/request pools, DFS, SPNEGO, SWN, idmap, and filesystem registrations.
  - Uses structured unwind labels for partial initialization failure.

- `exit_cifs()`
  - Unregisters filesystems and tears down automount, idmap, optional upcall subsystems, pools, caches, workqueues, and procfs.

## Dependencies

- Includes CIFS global state, protocol prototypes, SMB2 prototypes, mount context, DFS/SWN/fscache/cached-dir support.
- Connects lower SMB dialect operations into Linux VFS objects.

## Notable Behaviors

- Snapshot mounts are forced read-only.
- Old SMB1-style servers get one-second timestamp granularity; modern SMB uses 100ns granularity.
- `/proc/mounts` option display is extensive and includes negotiated/cache/security/reparse/symlink/channel details.
- Workqueue and pool initialization order is mirrored carefully in failure unwind and module exit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsfs.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsfs.h

Read status: complete.

## Purpose

Declares CIFS VFS-facing operations, helpers, filesystem types, file operation tables, and module version constants shared by the client implementation.

## Main Contents

- `ROOT_I`
  - Root inode number constant.

- `cifs_uniqueid_to_ino_t()`
  - Converts a 64-bit server file id to `ino_t`.
  - Hashes down to a nonzero 31-bit value on 32-bit `ino_t` platforms.

- Dentry time helpers:
  - `cifs_set_time()`
  - `cifs_get_time()`

- Extern declarations for:
  - `cifs_fs_type`
  - `smb3_fs_type`
  - address-space operations
  - inode operations
  - file operations
  - dentry operations
  - export operations when enabled

- VFS operation prototypes:
  - create/open/tmpfile/lookup/unlink/link/mkdir/rmdir/rename/mknod
  - revalidation
  - getattr/setattr/fiemap
  - file read/write/fsync/flush/lock/mmap/readdir
  - symlink handling
  - xattr listing
  - copychunk, ioctl, setsize, mount

- Temporary and silly rename name prefixes:
  - `CIFS_TMPNAME_PREFIX`
  - `CIFS_SILLYNAME_PREFIX`

- Version constants:
  - `SMB3_PRODUCT_BUILD`
  - `CIFS_VERSION`

## Role in the Subsystem

This is the public local header for CIFS VFS integration. It binds together declarations implemented across `cifsfs.c`, inode/file/dir/xattr modules, and mount code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsglob.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsglob.h

Read status: complete.

## Purpose

Central shared header for the CIFS/SMB client. It defines global constants, core state structures, dialect operation callbacks, mount/session/tcon/inode/file/request data structures, lock ordering documentation, global externs, and inline helpers.

## Main Responsibilities

- Define protocol and client-wide constants for paths, ports, buffers, credits, timeouts, channels, and cache sizing.
- Define connection/session/tree/open/inode/MID/I/O state structures.
- Declare the dialect abstraction table `struct smb_version_operations`.
- Provide helpers for credits, MID generation, path delimiters, DFS metadata, refcounting, cache-state checks, reconnect scheduling, and scatterlist setup.
- Document lock ordering for the CIFS client.

## Major Type Groups

### Protocol and Mount Constants

- Ports:
  - `CIFS_PORT`
  - `RFC1001_PORT`
- Request/concurrency constants:
  - `CIFS_MAX_REQ`
  - `SMB2_MAX_CREDITS_AVAILABLE`
  - `MAX_COMPOUND`
- Timeouts:
  - `CIFS_DEF_ACTIMEO`
  - `CIFS_MAX_ACTIMEO`
  - `SMB3_MAX_HANDLE_TIMEOUT`
  - echo interval bounds
- Size limits:
  - `CIFS_MAX_WSIZE`
  - `CIFS_MAX_RSIZE`
  - RFC1002-size variants
  - non-POSIX default read/write sizes

### Enums

- Connection state:
  - `enum statusEnum`
- Session state:
  - `enum ses_status_enum`
- Tree state:
  - `enum tid_status_enum`
- Security mechanism:
  - `enum securityEnum`
- Upcall target:
  - `enum upcall_target_enum`
- Reparse and symlink policy:
  - `enum cifs_reparse_type`
  - `enum cifs_symlink_type`

### Core Structures

- `struct session_key`
  - Authentication/session-key byte buffer.

- `struct cifs_secmech`
  - SMB3 AEAD encrypt/decrypt transforms.

- `struct ntlmssp_auth`
  - NTLMSSP flags, challenge/ciphertext, and session-key behavior.

- `struct cifs_open_info_data`
  - File metadata query result container, including reparse buffers, WSL EAs, POSIX info, symlink targets, and owner/group SIDs.

- `struct smb_rqst`
  - Complete SMB request representation: kvecs, data iterator, and encryption buffer.

- `struct smb_version_operations`
  - Large dialect callback table for SMB1/2/3 differences.
  - Covers send/receive, signing, credits, negotiate/session/tree connect, path/file queries, open/close/read/write, directory enumeration, oplocks, locks, copy offload, ACLs, xattrs, transform headers, reparse handling, fiemap, llseek, and POSIX node creation.

- `struct TCP_Server_Info`
  - Per-server/socket state.
  - Tracks transport status, socket addresses, credits, pending MIDs, signing/encryption negotiation, cryptographic keys, RDMA, compression, reconnect state, multichannel primary/channel state, DFS state, and work items.

- `struct cifs_ses`
  - Per-authenticated SMB session state.
  - Tracks user/domain/passwords, security type, signing/encryption keys, capabilities, interface list, multichannel channel array, DFS root session, and NLS table.

- `struct cifs_tcon`
  - Per-tree/share connection state.
  - Tracks share capabilities, flags, statistics, open files, pending opens, cached directory handles, DFS integration, fscache state, durable/persistent handle policy, POSIX extensions, witness, and snapshot metadata.

- `struct tcon_link`
  - Refcounted tree-connection holder keyed by uid for multiuser mounts.

- `struct cifs_open_parms`
  - Open request parameter bundle used by dialect open routines.

- `struct cifs_fid`
  - SMB1 netfid or SMB2 persistent/volatile file id plus lease key and open state.

- `struct cifsFileInfo`
  - Per-open-file state, including inode/tcon links, locks, fid, reconnect/deferred-close/oplock work, search info, and symlink target.

- `struct cifsInodeInfo`
  - CIFS inode extension embedded around `struct netfs_inode`.
  - Tracks oplock/cache state, open files, lock lists, DOS attrs, lease key, timestamps, deferred closes, symlink target, and reparse tag.

- `struct mid_q_entry`
  - Pending request/response tracking object.
  - Holds MID id, credits, response buffer, callbacks, state flags, timing/stat fields, and synchronization.

- `struct cifs_io_request` / `struct cifs_io_subrequest`
  - Netfs-integrated read/write request and subrequest state.

## Important Macros and Helpers

- `CIFS_SB()`
  - `_Generic` helper to retrieve `struct cifs_sb_info *` from inode, dentry, superblock, file, or CIFS inode.

- `cifs_sb_flags()`
  - Atomic read of mount flags.

- `CIFS_DIR_SEP()` and `convert_delimiter()`
  - Path delimiter policy helpers.

- Credit helpers:
  - `add_credits()`
  - `add_credits_and_wake_if()`
  - `set_credits()`
  - `adjust_credits()`
  - `has_credits()`

- MID helpers:
  - `get_next_mid64()`
  - `get_next_mid()`
  - `revert_current_mid()`
  - `mid_execute_callback()`
  - `smb_get_mid()`
  - `release_mid()`

- Cache helpers:
  - `CIFS_CACHE_READ()`
  - `CIFS_CACHE_HANDLE()`
  - `CIFS_CACHE_WRITE()`
  - `cifs_reset_oplock()`

- Reconnect helpers:
  - `cifs_queue_server_reconn()`
  - `cifs_requeue_server_reconn()`

- DFS helpers:
  - `free_dfs_info_param()`
  - `free_dfs_info_array()`
  - `dfs_src_pathname_equal()`
  - `is_tcon_dfs()`
  - `cifs_is_referral_server()`

- Error classification:
  - `is_interrupt_error()`
  - `is_retryable_error()`
  - `is_replayable_error()`

- Security flag constants:
  - `CIFSSEC_MAY_*`
  - `CIFSSEC_MUST_*`
  - `CIFSSEC_DEF`
  - `CIFSSEC_MAX`
  - `CIFSSEC_AUTH_MASK`

- Request/MID state constants:
  - `MID_*`
  - `CIFS_*_BUFFER`
  - send/receive request flags and operation types

## Global Declarations

When `DECLARE_GLOBALS_HERE` is defined, the header can switch declarations through `GLOBAL_EXTERN`, but this file primarily declares globals initialized in `cifsfs.c`, including:

- TCP session list and lock
- XID counters and lock
- allocation/reconnect/debug counters
- module option globals
- workqueues
- request/MID/netfs mempools
- dialect operation/value tables

## Locking Documentation

The header contains a detailed lock ordering table. It covers mount, volume context, superblock tlink trees, server reconnect/session locks, TCP session lock, tcon locks, inode locks, cached directory locks, file-info locks, RDMA locks, and MID locks. This is important because CIFS has nested server/session/tcon/inode/file state and many reconnect/oplock paths.

## Role in the Subsystem

`cifsglob.h` is the main structural contract for the CIFS client. Most implementation files include it either directly or indirectly, and the dialect-specific SMB1/SMB2/SMB3 implementations are bound to the common VFS/client layer through the operation table declared here.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsglob.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifspdu.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifspdu.h

Read status: complete.

## Purpose

Currently an empty compatibility/placeholder header for CIFS PDU declarations.

## Contents

- SPDX and copyright header.
- Include guard:
  - `_CIFSPDU_H`
- No structure, macro, or function declarations are present in this version.

## Role in the Subsystem

This file likely remains for include compatibility with older CIFS code organization where CIFS PDU definitions lived in a dedicated header. Current PDU definitions are provided elsewhere, such as common SMB headers and SMB1/SMB2-specific headers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifspdu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsproto.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsproto.h

Read status: complete.

## Purpose

Central prototype and inline-helper header for CIFS client implementation files. It declares buffer, transport, mount, session, inode, ACL, crypto, DFS, multichannel, reparse, lock, and utility functions implemented across the SMB client.

## Main Responsibilities

- Expose cross-file function prototypes.
- Provide XID tracing macros.
- Provide small inline wrappers for optional dialect operations and common helpers.
- Define helper functions for path allocation, session refcounting, MID refcounting, EIO tracing, scatterlist setup, and readable/writable open-file lookup.

## Major Prototype Groups

### Buffer and Transport

- CIFS large/small buffer allocation and release:
  - `cifs_buf_get()`
  - `cifs_buf_release()`
  - `cifs_small_buf_get()`
  - `cifs_small_buf_release()`
  - `free_rsp_buf()`

- Socket and send/receive paths:
  - `smb_send_kvec()`
  - `__smb_send_rqst()`
  - `cifs_call_async()`
  - `cifs_send_recv()`
  - `compound_send_recv()`
  - `wait_for_response()`
  - `wait_for_free_request()`
  - `cifs_wait_mtu_credits()`

- Receive helpers:
  - `cifs_read_from_socket()`
  - `cifs_discard_from_socket()`
  - `cifs_read_iter_from_socket()`
  - `cifs_readv_receive()`

### XID Tracing

- `get_xid()`
  - Wraps `_get_xid()`, logs current function and fsuid, and emits trace entry.

- `free_xid(curr_xid)`
  - Wraps `_free_xid()`, logs function exit and emits success/error trace based on local `rc`.

### Mount, Path, Session, and Reconnect

- Path construction and parsing:
  - `build_path_from_dentry()`
  - `cifs_build_path_to_root()`
  - `cifs_build_devname()`
  - `smb3_parse_devname()`
  - `smb3_fs_context_fullpath()`
  - `extract_unc_hostname()`
  - `extract_hostname()`
  - `extract_sharename()`

- Mount lifecycle:
  - `cifs_setup_cifs_sb()`
  - `cifs_mount()`
  - `cifs_umount()`
  - `cifs_match_super()`
  - mount session/tcon helper routines

- Session and reconnect:
  - `cifs_get_tcp_session()`
  - `cifs_put_tcp_session()`
  - `cifs_negotiate_protocol()`
  - `cifs_setup_session()`
  - `cifs_reconnect()`
  - reconnect marking helpers

### Inode and File Metadata

- Attribute conversion and inode population:
  - `cifs_fill_uniqueid()`
  - `cifs_unix_basic_to_fattr()`
  - `cifs_dir_info_to_fattr()`
  - `cifs_fattr_to_inode()`
  - `cifs_iget()`
  - `cifs_get_inode_info()`
  - `smb311_posix_get_inode_info()`
  - `cifs_get_inode_info_unix()`

- File state:
  - writable/readable open-file lookup
  - `cifs_new_fileinfo()`
  - `cifs_file_flush()`
  - `cifs_file_set_size()`
  - deferred close management

### ACL and Security Descriptor Operations

- ID/SID and ACL translation:
  - `sid_to_id()`
  - `cifs_acl_to_fattr()`
  - `id_mode_to_cifs_acl()`
  - `get_cifs_acl()`
  - `get_cifs_acl_by_fid()`
  - `set_cifs_acl()`
  - `cifs_get_acl()`
  - `cifs_set_acl()`

- ACE construction:
  - `setup_authusers_ACE()`
  - `setup_special_mode_ACE()`
  - `setup_special_user_owner_ACE()`

### Crypto and Authentication

- `setup_ntlmv2_rsp()`
- `calc_seckey()`
- `cifs_crypto_secmech_release()`
- `generate_smb30signingkey()`
- `generate_smb311signingkey()`
- `E_md4hash()`
- `__cifs_calc_signature()`
- `cifs_select_sectype()`

### Locks, Oplocks, and Deferred State

- Oplock and writer state:
  - `cifs_set_oplock_level()`
  - `cifs_get_writer()`
  - `cifs_put_writer()`
  - `cifs_done_oplock_break()`
  - `cifs_queue_oplock_break()`

- Byte-range locks:
  - `cifs_unlock_range()`
  - `cifs_push_mandatory_locks()`
  - `cifs_find_lock_conflict()`
  - lock list helpers

- Deferred and pending opens:
  - `cifs_add_pending_open()`
  - `cifs_del_pending_open()`
  - `cifs_is_deferred_close()`
  - deferred-close add/delete/close helpers

### DFS, Multichannel, Reparse, and Special Files

- DFS:
  - `parse_dfs_referrals()`
  - `get_dfs_path()` inline when DFS upcall is enabled
  - DFS super/prepath helpers

- Multichannel:
  - `cifs_try_adding_channels()`
  - `smb3_update_ses_channels()`
  - channel reconnect/interface helpers
  - `SMB3_request_interfaces()`

- Reparse and symlink/special files:
  - `parse_reparse_point()`
  - SFU node creation helpers
  - `wire_mode_to_posix()`
  - MF symlink helpers

### Inline Helpers

- `send_cancel()`
  - Calls dialect-specific cancel operation when present.

- `alloc_dentry_path()` / `free_dentry_path()`
  - Name-buffer allocation wrappers.

- `cifs_create_options()`
  - Adds backup intent when backup credentials are active.

- `cifs_put_smb_ses()` and `cifs_smb_ses_inc_refcount()`
  - Session refcount helpers.

- `dfs_src_pathname_equal()`
  - Case-insensitive path comparison treating `/` and `\` as equivalent.

- `smb_EIO()`, `smb_EIO1()`, `smb_EIO2()`
  - Traceable `-EIO` helpers.

- `cifs_get_num_sgs()` and `cifs_sg_set_buf()`
  - Scatterlist sizing/population helpers for encrypted SMB transform data.

- `cifs_get_writable_file()` / `find_readable_file()`
  - Inline wrappers normalizing open-file lookup flags.

## Role in the Subsystem

`cifsproto.h` is the shared declaration surface for the CIFS client. It prevents implementation files from needing to include many private module headers for every cross-file symbol and centralizes frequently used inline behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsproto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsroot.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsroot.c

Read status: complete.

## Purpose

Implements early-boot CIFS root filesystem support through the `cifsroot=` kernel command-line option.

## Main Responsibilities

- Parse `cifsroot=//<server-ip>/<share>[,options]`.
- Store the root CIFS UNC path and mount options in initdata buffers.
- Extract an IPv4 server address for `root_server_addr`.
- Provide root device and mount option data to the kernel root-mount path.

## Key Data

- `DEFAULT_MNT_OPTS`
  - Default root mount options:
    - `vers=1.0`
    - `cifsacl`
    - `mfsymlinks`
    - `rsize=1048576`
    - `wsize=65536`
    - `uid=0`
    - `gid=0`
    - `hard`
    - `rootfs`

- `root_dev`
  - Stores the parsed UNC device string.

- `root_opts`
  - Stores default options plus user-supplied options appended after the comma.

## Important Functions

- `parse_srvaddr()`
  - Extracts digits and dots from the server portion and converts them with `in_aton()`.
  - IPv6 is explicitly left as TODO.

- `cifs_root_setup()`
  - Registered with `__setup("cifsroot=", ...)`.
  - Marks `ROOT_DEV = Root_CIFS`.
  - Validates and copies the UNC prefix.
  - Parses server address and optional mount options.
  - Bounds-checks both root device and options buffers.

- `cifs_root_data()`
  - Returns the parsed device and options to the root filesystem mount path.
  - Fails when no root device was parsed or the server address is invalid.

## Dependencies

- Uses early boot/root infrastructure from `root_dev.h` and IP autoconfig state from `net/ipconfig.h`.

## Notable Behaviors

- Only IPv4 server address parsing is implemented.
- The function returns `1` from setup parsing even on malformed input, matching `__setup` convention for consuming the option.
- Defaults to SMB1/CIFS root options in this file.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifsroot.c -->