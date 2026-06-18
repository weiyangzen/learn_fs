# Group Research: SMB client CIFS/ACL/VFS core files

This group covers Linux SMB/CIFS client ACL translation, NTLMv2 crypto helpers, VFS registration and operation tables, shared client state/prototype headers, and CIFS rootfs boot support under `sources/os/linux/linux/fs/smb/client/`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsacl.c -->
# File Research: sources/os/linux/linux/fs/smb/client/cifsacl.c

## Purpose
`cifsacl.c` implements CIFS/SMB ACL handling: mapping Windows SIDs to Linux ids, translating NT security descriptors/DACLs into POSIX mode bits, building updated security descriptors for chmod/chown/chgrp, retrieving and setting ACLs through SMB protocol operations, and exposing legacy POSIX ACL get/set wrappers when configured.

## Main Responsibilities
- Registers the `cifs.idmap` key type used for SID/id upcalls.
- Converts SID strings and binary SIDs to/from Linux `kuid_t`/`kgid_t`.
- Recognizes special Unix/NFS SID formats:
  - `S-1-22-1` Unix users.
  - `S-1-22-2` Unix groups.
  - `S-1-5-88-1/2/3` NFS-style uid/gid/mode SIDs.
- Parses security descriptors and DACL ACEs into `struct cifs_fattr`.
- Builds new self-relative security descriptors for permission or ownership updates.
- Provides SMB1 legacy ACL fetch/set helpers under `CONFIG_CIFS_ALLOW_INSECURE_LEGACY`.
- Provides POSIX ACL hooks under `CONFIG_CIFS_ALLOW_INSECURE_LEGACY && CONFIG_CIFS_POSIX`.

## Key Data and Constants
- Static well-known SIDs:
  - `sid_everyone`
  - `sid_authusers`
  - `sid_unix_users`
  - `sid_unix_groups`
  - `sid_unix_NFS_users`
  - `sid_unix_NFS_groups`
  - `sid_unix_NFS_mode`
- `root_cred`: kernel credentials with a private `.cifs_idmap` thread keyring for idmap request caching.
- `cifs_idmap_key_type`: custom key type named `cifs.idmap`.

## Important Functions
- `init_cifs_idmap()` / `exit_cifs_idmap()`: register/unregister idmap key type and manage the private keyring credential.
- `sid_to_key_str()`: formats a SID as `os:S-...` or `gs:S-...` key descriptions for userspace idmap upcalls.
- `compare_sids()`: compares two SMB SIDs.
- `is_well_known_sid()`: extracts uid/gid directly from special Unix/NFS SID forms.
- `id_to_sid()`: maps a Linux uid/gid to an SMB SID via keyring upcall.
- `sid_to_id()`: maps an SMB SID to Linux uid/gid, using direct special-SID decoding first when configured, then keyring upcall.
- `validate_dacl()`: validates DACL and ACE bounds before parsing.
- `parse_dacl()`: walks ACEs and updates POSIX mode bits based on owner/group/everyone/authenticated-users ACEs or special mode SID.
- `parse_sec_desc()`: parses owner SID, group SID, and optional DACL from a server security descriptor.
- `build_sec_desc()`: builds a modified security descriptor for chmod/chown/chgrp.
- `cifs_acl_to_fattr()`: retrieves a server ACL and converts it into Linux inode attributes.
- `id_mode_to_cifs_acl()`: converts Linux mode/id changes into a new CIFS ACL and sends it to the server.
- `cifs_get_acl()` / `cifs_set_acl()`: legacy POSIX ACL xattr style hooks.

## Permission Translation
- `access_flags_to_mode()` maps Windows access masks such as `GENERIC_READ`, `GENERIC_WRITE`, `GENERIC_EXECUTE`, `FILE_*_RIGHTS`, and `FILE_DELETE_CHILD` into POSIX mode bits.
- `mode_to_access_flags()` maps POSIX read/write/execute bits back to CIFS file rights.
- `populate_new_aces()` creates canonical owner/group/everyone ACEs and optional deny ACEs to preserve POSIX semantics when Windows ACL inheritance or ordering could otherwise broaden access.
- For `modefromsid` or SMB3 POSIX mode handling, `setup_special_mode_ACE()` embeds the exact mode in `S-1-5-88-3`.

## Validation and Safety Notes
- DACL parsing has explicit length checks for ACL header, ACE header, SID subauthority count, ACE size, and DACL boundary.
- SID subauthority count is capped with `SID_MAX_SUB_AUTHORITIES`.
- Malformed idmap key payloads are invalidated.
- `sid_to_id()` deliberately falls back to mount uid/gid defaults if mapping fails.
- `id_mode_to_cifs_acl()` sizes new security descriptors pessimistically for chmod/chown cases before building them.
- Sensitive key material is not handled here except idmap payloads; crypto lives in `cifsencrypt.c`.

## Dependencies
- Depends on `cifsglob.h`, `cifsacl.h`, `cifsproto.h`, `fs_context.h`, `cifs_fs_sb.h`, and common SMB ACL definitions.
- Protocol-specific ACL operations are dispatched through `server->ops->get_acl`, `get_acl_by_fid`, and `set_acl`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsacl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsacl.h -->
# File Research: sources/os/linux/linux/fs/smb/client/cifsacl.h

## Purpose
`cifsacl.h` defines CIFS/SMB security descriptor and ACL constants used by ACL translation code.

## Main Contents
- Includes shared SMB ACL wire structures from `../common/smbacl.h`.
- Defines POSIX permission masks and bit shifts:
  - `READ_BIT`, `WRITE_BIT`, `EXEC_BIT`
  - `ACL_OWNER_MASK`, `ACL_GROUP_MASK`, `ACL_EVERYONE_MASK`
  - `UBITSHIFT`, `GBITSHIFT`
- Defines `DEFAULT_SEC_DESC_LEN`, the minimum allocation target for a security descriptor containing owner, group, and several ACEs.
- Defines SMB3 security descriptor structure `struct smb3_sd`.
- Defines SMB3 ACL header `struct smb3_acl`.
- Defines special owner/group SID structures used for NFS-style persisted uid/gid:
  - `struct owner_sid`
  - `struct owner_group_sids`
- Defines minimum SID/security descriptor lengths:
  - `MIN_SID_LEN`
  - `MIN_SEC_DESC_LEN`

## Security Descriptor Flags
The file enumerates `ACL_CONTROL_*` flags matching MS-DTYP self-relative security descriptor control bits, including DACL/SACL present/defaulted/protected/inherited flags and resource-manager/self-relative flags.

## Role in the Group
This header is the local schema companion for `cifsacl.c`. It does not implement logic; it supplies wire-format structures and constants needed to parse and synthesize ACL/security-descriptor blobs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsacl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsencrypt.c -->
# File Research: sources/os/linux/linux/fs/smb/client/cifsencrypt.c

## Purpose
`cifsencrypt.c` implements NTLM/NTLMv2 authentication hashing, signing digest helpers, NTLMv2 response generation, NTLM session-key encryption, and release of SMB3 encryption crypto transforms.

## Main Responsibilities
- Feeds SMB request vectors and iterators into a selected signature/hash context.
- Builds and parses NTLMSSP AV-pair target-info blobs.
- Computes NTLMv2 hash from password hash, uppercased username, and domain/server name.
- Builds the NTLMv2 client response and session key.
- Generates the NTLM encrypted secondary session key using ARC4.
- Releases AEAD crypto transforms stored on `TCP_Server_Info`.

## Important Functions
- `cifs_sig_step()`: updates MD5, HMAC-SHA256, or AES-CMAC context for one iterator segment.
- `cifs_sig_final()`: finalizes whichever signing algorithm context is active.
- `cifs_sig_iter()`: safely walks an `iov_iter` into the signing context.
- `__cifs_calc_signature()`: signs SMB request kvecs plus request data iterator.
- `build_avpair_blob()`: constructs a minimal NTLM target-info AV blob when extended security did not provide one.
- `find_next_av()`: bounded iterator over NTLMSSP AV pairs.
- `find_av_name()`: extracts Unicode AV names such as NetBIOS/DNS domain into session strings.
- `find_timestamp()`: returns server-provided NTLM timestamp or current NT time.
- `calc_ntlmv2_hash()`: computes `HMAC-MD5(NT hash, UppercaseUser + DomainOrServer)`.
- `CalcNTLMv2_response()`: computes NTLMv2 proof response over server challenge and response blob.
- `set_auth_key_response()`: creates final NTLMv2 response buffer, appending SPN AV pair `cifs/<hostname>` and EOL.
- `setup_ntlmv2_rsp()`: top-level NTLMv2 response/session-key setup.
- `calc_seckey()`: creates random secondary key and encrypts it with ARC4 using the session key.
- `cifs_crypto_secmech_release()`: frees SMB3 AEAD encryption/decryption transforms.

## Authentication Flow
1. Determine or build target-info AV pairs.
2. Resolve domain fields from challenge AV pairs when domain autodetection is enabled.
3. Select timestamp from server AV pair or local time.
4. Generate client challenge randomness.
5. Build response blob with target-info and SPN.
6. Reject NTLMv2 in FIPS mode.
7. Calculate NTLMv2 hash.
8. Calculate NTLMv2 proof response.
9. Derive session key from proof response.

## Validation and Safety Notes
- AV-pair parsing checks bounds and aligned UTF-16 lengths.
- `setup_ntlmv2_rsp()` uses `cifs_server_lock()` around response-buffer mutation.
- Old target-info buffer is freed with `kfree_sensitive()`.
- NTLMv2 and ARC4 key paths are disabled/rejected under FIPS where applicable.
- Temporary session-key material is wiped with `memzero_explicit()` and freed using sensitive-free helpers.

## Dependencies
- Uses kernel crypto helpers for MD5, HMAC-MD5, HMAC-SHA256, AES-CMAC, ARC4, random bytes, and FIPS state.
- Depends on session/server structures from `cifsglob.h` and NTLMSSP wire structures from `ntlmssp.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsencrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsfs.c -->
# File Research: sources/os/linux/linux/fs/smb/client/cifsfs.c

## Purpose
`cifsfs.c` is the main Linux VFS integration and module lifecycle file for the CIFS/SMB3 client. It defines module parameters/globals, filesystem types, superblock operations, inode/file/dir operation tables, mount setup, copy/clone operations, memory pools, workqueues, and module init/exit.

## Main Responsibilities
- Defines module-wide knobs:
  - buffer sizes and pool minimums,
  - pending request limits,
  - directory cache timeout,
  - oplock/signing/encryption dialect behavior toggles,
  - legacy dialect restrictions.
- Owns global counters and locks for XIDs, sessions, tcons, TCP sessions, buffers, and mids.
- Implements superblock setup and teardown.
- Registers `cifs` and `smb3` filesystem types.
- Exposes inode/file/directory operation tables to VFS.
- Integrates with netfs/fscache, pagecache invalidation, and server-side copy offload.
- Initializes and destroys request buffers, inode cache, mid pool, IO request pools, workqueues, DFS/SPNEGO/SWN/idmap support, and proc state.

## Important Functions
- `cifs_sb_active()` / `cifs_sb_deactive()`: manage CIFS superblock active references.
- `cifs_read_super()`: initializes a superblock, root inode, dentry ops, bdi/readahead settings, time granularity, xattrs, export ops, and max file size.
- `cifs_kill_sb()`: closes cached dirs/deferred files, flushes workqueues, releases root, kills anon super, and unmounts CIFS state.
- `cifs_statfs()`: builds path and dispatches `server->ops->queryfs`.
- `cifs_fallocate()`: serializes with inode lock, waits for netfs IO, marks file modified, dispatches protocol fallocate op.
- `cifs_permission()`: honors `noperm` mount behavior or falls back to generic permission checks.
- `cifs_alloc_inode()` / `cifs_free_inode()` / `cifs_evict_inode()`: manage CIFS inode lifecycle and netfs/fscache teardown.
- `cifs_show_options()`: renders mount options for `/proc/mounts`.
- `cifs_get_root()`: resolves prefix-path mounts to the actual root dentry.
- `cifs_smb3_do_mount()`: duplicates fs context, mounts server/share, gets or creates superblock, reads superblock, and returns mounted root.
- `cifs_llseek()`: revalidates remote size for `SEEK_END`, `SEEK_DATA`, and `SEEK_HOLE`.
- `cifs_setlease()`: gates VFS leases on CIFS oplock/cache state.
- `cifs_fileattr_get()`: reports compression and casefold/case-preserving attributes.
- `cifs_remap_file_range()`: implements clone/duplicate-extents path with source flush, EOF adjustment, destination folio flush/invalidate, fscache invalidation, and size updates.
- `cifs_file_copychunk_range()` / `cifs_copy_file_range()`: implement server-side copychunk with splice fallback.
- `init_cifs()` / `exit_cifs()`: module load/unload lifecycle.

## VFS Operation Tables
- Filesystem types:
  - `cifs_fs_type`
  - `smb3_fs_type`
- Super operations:
  - `cifs_super_ops`
- Inode operations:
  - `cifs_dir_inode_ops`
  - `cifs_file_inode_ops`
  - `cifs_symlink_inode_ops`
- File operations:
  - `cifs_file_ops`
  - `cifs_file_strict_ops`
  - `cifs_file_direct_ops`
  - `cifs_file_nobrl_ops`
  - `cifs_file_strict_nobrl_ops`
  - `cifs_file_direct_nobrl_ops`
  - `cifs_dir_ops`

## Initialization Order
`init_cifs()` initializes, in order:
1. SMB1/SMB2 error maps.
2. proc entries and global counters.
3. workqueues.
4. inode cache.
5. netfs IO pools.
6. MID pool.
7. request buffer pools.
8. DFS cache, SPNEGO, SWN genl when configured.
9. CIFS idmap.
10. `cifs` and `smb3` filesystem registration.

The error path unwinds each initialized component in reverse order.

## Caching and IO Notes
- Superblock readahead is derived from negotiated or requested `rsize`.
- Inodes embed `struct netfs_inode`.
- Copy/clone operations flush source ranges and invalidate destination cache/fscache before server-side mutation.
- Oplock/cache state affects leases and seek revalidation behavior.
- `cifs_evict_inode()` waits for outstanding netfs IO and releases fscache cookies.

## Safety and Concurrency Notes
- Workqueues are flushed during forced superblock teardown to finish oplock/deferred close work.
- `cifs_umount_begin()` wakes request/response wait queues for forced unmount progress.
- `cifs_remap_file_range()` locks both non-directory inodes and handles overlapping/unsupported clone cases.
- Module parameter values are range-clamped during initialization.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsfs.h -->
# File Research: sources/os/linux/linux/fs/smb/client/cifsfs.h

## Purpose
`cifsfs.h` declares the CIFS/SMB VFS-facing functions, operation tables, filesystem types, helper macros, and version constants exported across the SMB client implementation.

## Main Contents
- `ROOT_I`: root inode number constant.
- `cifs_sillycounter`, `cifs_tmpcounter`: counters for temporary/silly-renamed names.
- `cifs_uniqueid_to_ino_t()`: squashes 64-bit server file ids into `ino_t` safely on 32-bit architectures.
- `cifs_set_time()` / `cifs_get_time()`: dentry timestamp storage through `d_fsdata`.
- Extern declarations for:
  - filesystem types,
  - address-space operations,
  - inode operations,
  - file operations,
  - dentry operations,
  - export operations,
  - netfs request ops.
- VFS operation prototypes for create, lookup, mkdir, rename, getattr/setattr, fiemap, open/close, read/write, locks, fsync/flush, mmap, readdir, symlink, xattrs, ioctl, copychunk, and mount.

## Naming Constants
- `CIFS_TMPNAME_PREFIX` / `CIFS_TMPNAME_LEN`
- `CIFS_SILLYNAME_PREFIX` / `CIFS_SILLYNAME_LEN`

These support temporary files and silly rename behavior.

## Versioning
- `SMB3_PRODUCT_BUILD 60`
- `CIFS_VERSION "2.60"`

The comment notes these should be changed together.

## Role in the Group
This is the public local header for `cifsfs.c` and related VFS implementation files. It does not define complex state; that lives in `cifsglob.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsglob.h -->
# File Research: sources/os/linux/linux/fs/smb/client/cifsglob.h

## Purpose
`cifsglob.h` is the central shared state and contract header for the CIFS/SMB client. It defines global constants, mount/security flags, status enums, core server/session/tree/file/inode structures, the SMB dialect operation vtable, request/mid structures, lock-ordering documentation, global externs, and inline helpers.

## Major Constants and Enums
- Ports and path sizes:
  - `CIFS_PORT`, `RFC1001_PORT`, `SMB_PATH_MAX`, `MAX_TREE_SIZE`
- Request and credit limits:
  - `CIFS_MAX_REQ`
  - `SMB2_MAX_CREDITS_AVAILABLE`
  - `MAX_COMPOUND`
- Cache/time values:
  - `CIFS_DEF_ACTIMEO`
  - `CIFS_MAX_ACTIMEO`
  - echo interval bounds
- Status enums:
  - `enum statusEnum` for TCP connection state.
  - `enum ses_status_enum` for SMB session state.
  - `enum tid_status_enum` for tree connection state.
- Security/auth enums:
  - `enum securityEnum`
  - `enum upcall_target_enum`
- Reparse and symlink behavior enums:
  - `enum cifs_reparse_type`
  - `enum cifs_symlink_type`

## Core Structures
- `struct session_key`: response/session-key blob.
- `struct cifs_secmech`: SMB3 AEAD encryption/decryption transforms.
- `struct ntlmssp_auth`: NTLMSSP flags, challenge, and ciphertext.
- `struct cifs_open_info_data`: unified query/open metadata, reparse data, WSL EAs, symlink target, POSIX owner/group SIDs, and file info union.
- `struct smb_rqst`: SMB request kvecs plus data iterator/buffer.
- `struct smb_version_operations`: very large dialect vtable for SMB1/2/3 operations.
- `struct TCP_Server_Info`: per TCP/RDMA server connection state.
- `struct cifs_ses`: per SMB session/authentication state, including multichannel data.
- `struct cifs_tcon`: per tree/share connection state.
- `struct tcon_link`: refcounted per-user tcon link container.
- `struct cifs_fid`: protocol file id/lease key state.
- `struct cifsFileInfo`: per-open file state, locks, deferred close, oplock work, search info.
- `struct cifs_io_request` / `struct cifs_io_subrequest`: netfs IO request wrappers.
- `struct cifsInodeInfo`: CIFS inode extension embedding `struct netfs_inode`.
- `struct mid_q_entry`: pending multiplexed SMB request/response tracking entry.
- DFS, mount, channel, interface, lock, and compound-request helper structs.

## SMB Version Operation Vtable
`struct smb_version_operations` abstracts dialect-specific behavior. It includes hooks for:
- request setup/signing/cancel/receive/error mapping,
- credit accounting,
- negotiate/session/tree connect/disconnect,
- DFS referrals and server interface queries,
- path/file info query and mutation,
- open/close/flush/read/write/readdir,
- oplock/lease handling,
- server-side copy/clone,
- extended attributes and ACLs,
- encryption/compression transforms,
- reparse point handling,
- POSIX/special file creation,
- fiemap/llseek and status checks.

This vtable is the main indirection point that allows common VFS code to dispatch to SMB1, SMB2.1, SMB3.0, SMB3.02, or SMB3.1.1 behavior.

## Locking and Concurrency
The file contains a detailed lock-ordering table covering:
- mount/session/tcon/server locks,
- global MID/XID locks,
- server request/mid locks,
- session interface/channel locks,
- inode and file locks,
- cached directory locks,
- RDMA and MID callback locks.

This is important because CIFS combines VFS locks, network reconnect paths, oplock callbacks, deferred close work, and pending request completion.

## Inline Helpers
- Server locking with `memalloc_nofs_save()`:
  - `cifs_server_lock()`
  - `cifs_server_unlock()`
- Credit helpers:
  - `in_flight()`
  - `has_credits()`
  - `add_credits()`
  - `add_credits_and_wake_if()`
  - `set_credits()`
  - `adjust_credits()`
- MID helpers:
  - `get_next_mid64()`
  - `get_next_mid()`
  - `revert_current_mid()`
  - `mid_execute_callback()`
- Namespace/network helpers:
  - `cifs_net_ns()`
  - `cifs_set_net_ns()`
- Path and mount helpers:
  - `CIFS_SB()`
  - `cifs_sb_flags()`
  - `CIFS_DIR_SEP()`
  - `convert_delimiter()`
- DFS and error classification:
  - `is_tcon_dfs()`
  - `cifs_is_referral_server()`
  - `is_interrupt_error()`
  - `is_retryable_error()`
  - `is_replayable_error()`
- Cache/oplock helpers:
  - `CIFS_CACHE_READ()`
  - `CIFS_CACHE_HANDLE()`
  - `CIFS_CACHE_WRITE()`
  - `cifs_reset_oplock()`
- Reconnect scheduling:
  - `cifs_queue_server_reconn()`
  - `cifs_requeue_server_reconn()`
- File open options:
  - `cifs_open_create_options()`

## Global Externs
The header declares globals defined primarily by `cifsfs.c`, including:
- `cifs_tcp_ses_list`, `cifs_tcp_ses_lock`
- XID counters and `GlobalMid_Lock`
- allocation/reconnect/stat counters
- module parameters such as `enable_oplocks`, `global_secflags`, `CIFSMaxBufSize`, `cifs_max_pending`
- workqueues
- request/mid/netfs mempools
- dialect operation/value structs

## Role in the Group
This is the architectural backbone of the SMB client. `cifsfs.c`, `cifsacl.c`, and `cifsencrypt.c` all depend on its state definitions and helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsglob.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifspdu.h -->
# File Research: sources/os/linux/linux/fs/smb/client/cifspdu.h

## Purpose
`cifspdu.h` is currently an empty guarded header.

## Contents
- SPDX/license and author comment.
- Include guard `_CIFSPDU_H`.
- No structures, constants, prototypes, or inline logic.

## Role in the Group
This appears to be a historical compatibility or placeholder header. CIFS/SMB PDU definitions now live in other headers such as common SMB headers, `smb1pdu.h`, and `smb2pdu.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifspdu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsproto.h -->
# File Research: sources/os/linux/linux/fs/smb/client/cifsproto.h

## Purpose
`cifsproto.h` declares the CIFS/SMB client function surface shared across implementation files. It also defines common small inline wrappers for XID tracing, dentry path allocation, cancel dispatch, DFS stubs, session refcounting, scatterlist setup, and EIO tracing.

## Major Prototype Areas
- Buffer management:
  - `cifs_buf_get()`, `cifs_buf_release()`
  - `cifs_small_buf_get()`, `cifs_small_buf_release()`
  - `free_rsp_buf()`
- XID accounting:
  - `_get_xid()`, `_free_xid()`
  - `get_xid()` and `free_xid()` trace/debug macros
- Path construction:
  - `build_path_from_dentry()`
  - `cifs_build_path_to_root()`
  - `cifs_build_devname()`
  - `smb3_fs_context_fullpath()`
  - UNC hostname/share extraction helpers
- Transport and MID handling:
  - `smb_send_kvec()`
  - `cifs_call_async()`
  - `cifs_send_recv()`
  - `compound_send_recv()`
  - `wait_for_response()`
  - `delete_mid()`, `dequeue_mid()`, `release_mid()`
- Reconnect/session/tcon:
  - `cifs_get_tcp_session()`
  - `cifs_put_tcp_session()`
  - `cifs_get_smb_ses()`
  - `cifs_tree_connect()`
  - `cifs_mount()`, `cifs_umount()`
  - multichannel functions
- Inode/file operations:
  - writable/readable file lookup,
  - inode info conversion,
  - file size and attr mutation,
  - locks and mandatory locks,
  - deferred close helpers,
  - deleted-file handle marking.
- ACL and idmap:
  - `sid_to_id()`
  - `cifs_acl_to_fattr()`
  - `id_mode_to_cifs_acl()`
  - `get_cifs_acl()`
  - `cifs_get_acl()`, `cifs_set_acl()`
  - special ACE setup helpers.
- Crypto/auth:
  - `setup_ntlmv2_rsp()`
  - `calc_seckey()`
  - `__cifs_calc_signature()`
  - SMB3 signing-key generation.
- DFS/reparse/symlink/special files:
  - DFS referral parsing and lookup stubs,
  - reparse point parsing,
  - SFU node creation,
  - MF symlink helpers.
- SMB3 transform helpers:
  - scatterlist sizing and buffer setup for encryption/decryption.

## Important Inline Helpers
- `alloc_dentry_path()` / `free_dentry_path()`: allocate/free path buffer using name cache.
- `send_cancel()`: optional dialect hook wrapper.
- `cifs_create_options()`: adds backup intent when backup credentials are in use.
- `cifs_put_smb_ses()` / `cifs_smb_ses_inc_refcount()`: SMB session refcount helpers.
- `dfs_src_pathname_equal()`: case-insensitive path comparison treating `/` and `\` as equivalent.
- `cifs_free_open_info()`: releases symlink/reparse resources and zeros open info.
- `smb_EIO()`, `smb_EIO1()`, `smb_EIO2()`: trace an SMB EIO cause and return `-EIO`.
- `cifs_get_num_sgs()`: computes scatterlist entry count for transformed requests.
- `cifs_sg_set_buf()`: scatterlist setup supporting vmalloc/module/stack-backed buffers.
- `cifs_get_writable_file()` and `find_readable_file()`: wrappers that normalize find flags.

## Role in the Group
This is the declaration hub connecting the implementation in `cifsfs.c`, ACL handling in `cifsacl.c`, crypto in `cifsencrypt.c`, transport/session code elsewhere, and dialect-specific SMB2/SMB3 modules.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsproto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsroot.c -->
# File Research: sources/os/linux/linux/fs/smb/client/cifsroot.c

## Purpose
`cifsroot.c` implements early boot support for using a CIFS/SMB share as the root filesystem via the `cifsroot=` kernel command-line option.

## Main Data
- `DEFAULT_MNT_OPTS`: default mount options:
  - `vers=1.0`
  - `cifsacl`
  - `mfsymlinks`
  - `rsize=1048576`
  - `wsize=65536`
  - `uid=0,gid=0`
  - `hard`
  - `rootfs`
- `root_dev[2048]`: parsed UNC path.
- `root_opts[1024]`: default options plus user-provided options.

## Important Functions
- `parse_srvaddr()`: extracts IPv4 digits/dots from the server portion and converts with `in_aton()`. IPv6 is explicitly marked TODO.
- `cifs_root_setup()`: parses `cifsroot=//<server-ip>/<share>[,options]`, sets `ROOT_DEV = Root_CIFS`, stores UNC path, parses server address, and appends optional mount options.
- `cifs_root_data()`: returns parsed root device and options to rootfs mounting code, or errors if missing/invalid server address.

## Command-Line Behavior
Registered with:
- `__setup("cifsroot=", cifs_root_setup)`

The parser accepts a UNC-like `//server/share` form and optional comma-separated mount options after the share path.

## Validation and Limits
- Rejects missing share path.
- Rejects UNC path longer than `root_dev`.
- Rejects mount option string longer than `root_opts`.
- Requires parsed server address not equal to `INADDR_NONE`.
- Only IPv4 address extraction is supported.

## Role in the Group
This file is separate from normal runtime VFS registration. It supplies boot-time root filesystem data so the CIFS filesystem registered elsewhere can mount the specified SMB share as `/`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifsroot.c -->