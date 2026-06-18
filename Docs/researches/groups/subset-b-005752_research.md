# Research Report: subset-b-005752

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsacl.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifsacl.c

Purpose: implements CIFS/SMB NT security descriptor handling for the Linux client. It maps Windows SIDs and DACL ACEs to Linux uid/gid/mode attributes, builds modified security descriptors for chmod/chown/chgrp, registers the `cifs.idmap` key type used by userspace SID mapping upcalls, and exposes optional legacy POSIX ACL xattr accessors.

Important APIs and functions: exported entry points include `init_cifs_idmap`, `exit_cifs_idmap`, `sid_to_id`, `cifs_acl_to_fattr`, `id_mode_to_cifs_acl`, `get_cifs_acl`, `get_cifs_acl_by_fid`, `set_cifs_acl`, `cifs_get_acl`, `cifs_set_acl`, `setup_authusers_ACE`, `setup_special_mode_ACE`, and `setup_special_user_owner_ACE`. Core helpers include `sid_to_key_str`, `id_to_sid`, `is_well_known_sid`, `compare_sids`, `validate_dacl`, `parse_dacl`, `parse_sec_desc`, `build_sec_desc`, `populate_new_aces`, `set_chmod_dacl`, and `replace_sids_and_copy_aces`.

Control flow: module init calls `init_cifs_idmap`, which creates a root-owned thread keyring and registers the `cifs.idmap` key type. File metadata refresh calls `cifs_acl_to_fattr`; this obtains a security descriptor through dialect operations, validates owner/group/DACL offsets, maps SIDs to ids through direct well-known SID decoding or request-key upcalls, and folds matching ACEs into mode bits. Attribute changes call `id_mode_to_cifs_acl`; it fetches the current descriptor, sizes a new descriptor, rebuilds the DACL for chmod or replaces owner/group SIDs for chown/chgrp, then submits it through `ops->set_acl`. Legacy CIFS/SMB1 builds can open a path or reuse a fid and issue CIFS ACL get/set calls. POSIX ACL get/set paths are compiled only with legacy and POSIX support and use the CIFS POSIX ACL wire helpers.

State and persistence behavior: persistent state is the server-side NT security descriptor, including owner SID, group SID, DACL, optional special S-1-5-88 mode/uid/gid SIDs, and inherited ACEs retained during chmod reconstruction. In-memory state includes the module-private idmap root credential/keyring, request-key payloads, temporary `smb_ntsd` buffers, and fallback ids from mount context. The code intentionally falls back to mount uid/gid when SID-to-id mapping fails, but malformed key payloads or malformed ACL layout return errors.

Dependencies and integration points: depends on `../common/smbacl.h` wire structures, keyrings/request-key userspace idmapping, NLS UTF-16 helpers, CIFS mount flags such as `CIFS_MOUNT_UID_FROM_ACL` and `CIFS_MOUNT_MODE_FROM_SID`, VFS inode and dentry paths, SMB version operation hooks for `get_acl`, `get_acl_by_fid`, and `set_acl`, and legacy CIFS SMB1 ACL functions under `CONFIG_CIFS_ALLOW_INSECURE_LEGACY`.

Risks: security descriptor parsing is offset and length sensitive; invalid `dacloffset`, ACE size, or SID subauthority counts must be rejected before pointer arithmetic crosses the returned buffer. Mode approximation from arbitrary Windows ACE order is lossy and can diverge from server-side access checks. `setup_special_user_owner_ACE` stores `current_fsgid()` in a user-owner SID helper, which is worth reviewing when touching special SID behavior. Chmod DACL reconstruction has complex deny/allow ordering and inherited ACE placement rules. Idmapping upcall failures silently retain mount fallback ids, so permission displays can be misleading without trace/debug signals.

Test signals: mount with `cifsacl`, `modefromsid`, `idsfromsid`, POSIX extensions, and fallback uid/gid modes; parse descriptors with empty, missing, inherited, deny-first, allow-first, owner/group/everyone/authenticated-users, and S-1-5-88 mode ACEs; malformed ACL fuzz cases for offsets, sizes, zero subauths, and too many subauths; chown/chgrp through upcall SIDs and special SID generation; chmod with sticky bit and owner/group SID equality; fid-based and path-based ACL retrieval; legacy POSIX ACL get/set; and FIPS/user namespace cases around id conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsacl.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifsacl.h

Purpose: defines CIFS ACL constants and packed SMB3 security descriptor structures used by ACL parsing and synthesis. It bridges common SMB ACL wire definitions with client-local mode masks and special SID helper layouts.

Important APIs and types: defines permission masks `READ_BIT`, `WRITE_BIT`, `EXEC_BIT`, `ACL_OWNER_MASK`, `ACL_GROUP_MASK`, `ACL_EVERYONE_MASK`, `UBITSHIFT`, `GBITSHIFT`, `DEFAULT_SEC_DESC_LEN`, `MIN_SID_LEN`, and `MIN_SEC_DESC_LEN`. It declares packed wire-compatible `struct smb3_sd`, `struct smb3_acl`, `struct owner_sid`, and `struct owner_group_sids`, plus ACL control flags such as `ACL_CONTROL_SR`, `ACL_CONTROL_DP`, and ACL revision constants.

Control flow: this header has no executable flow. It is included by `cifsacl.c` and globally through `cifsglob.h`, so its constants guide DACL building, chmod mode mapping, SMB3 security descriptor parsing, and special S-1-5-88 owner/group persistence.

State and persistence behavior: the packed structs describe persistent on-the-wire or server-stored data, especially self-relative SMB3 security descriptors and special NFS-style owner/group SIDs. The macros set local buffer sizing assumptions for constructing security descriptors in memory before sending them to the server.

Dependencies and integration points: includes `../common/smbacl.h` for shared `smb_ntsd`, `smb_acl`, `smb_ace`, and `smb_sid` definitions. It is consumed by ACL code, SMB2/SMB3 create/query/set-info paths, and the broader CIFS global declarations that need ACL type names.

Risks: these packed structures must stay aligned with MS-DTYP/MS-SMB2 field order and endianness. `DEFAULT_SEC_DESC_LEN` is only a conservative construction size for common owner/group/world descriptors; callers that add inherited or special ACEs must size larger. Changing mask constants would alter chmod/chown semantic translation across the client.

Test signals: compile-time packed layout checks if added, ACL round trips against Windows/Samba security descriptors, chmod/chown buffer sizing with four or more ACEs, special owner/group SID persistence, and static analysis for endian annotations on the SMB3 descriptor fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsencrypt.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifsencrypt.c

Purpose: implements NTLM/NTLMv2 authentication hashing, SMB request signature feeding, NTLMv2 target-info response construction, legacy session-key encryption, and cleanup of SMB3 encryption transforms.

Important APIs and functions: exported functions are `__cifs_calc_signature`, `setup_ntlmv2_rsp`, `calc_seckey`, and `cifs_crypto_secmech_release`. Internal helpers include `cifs_sig_step`, `cifs_sig_iter`, `cifs_sig_final`, `build_avpair_blob`, `find_next_av`, `find_av_name`, `find_timestamp`, `calc_ntlmv2_hash`, `CalcNTLMv2_response`, and `set_auth_key_response`.

Control flow: signing callers initialize a `cifs_calc_sig_ctx` with MD5, HMAC-SHA256, or AES-CMAC state, then `__cifs_calc_signature` streams request kvecs and the payload iterator into the selected primitive and finalizes the signature. NTLMv2 setup parses server AV pairs from the challenge or constructs a minimal domain AV blob, discovers domain and DNS domain names, reuses the server timestamp or current time, generates a client challenge, appends a `cifs/<hostname>` SPN target-name AV pair, computes the NTLMv2 hash from password/user/domain, computes the NTLMv2 proof string, and derives the session key. `calc_seckey` encrypts a random secondary key with ARC4 for legacy NTLMSSP. Crypto release frees AEAD handles cached on the server object.

State and persistence behavior: state is per-session and per-server, not filesystem persistent. The code mutates `ses->auth_key.response` and `ses->auth_key.len`, may allocate `ses->domainName` and `ses->dns_dom`, reads `ses->ntlmssp` challenge state, and uses `TCP_Server_Info::secmech` AEAD pointers. Sensitive temporary buffers and old target-info blobs are released with sensitive/free paths where applicable.

Dependencies and integration points: depends on kernel crypto helpers for MD5, HMAC-MD5, HMAC-SHA256, AES-CMAC, ARC4, random bytes, FIPS state, iov iterators, NLS/UTF-16 conversion, NTLMSSP AV-pair structures, and CIFS server/session locking. It is called by SMB1/SMB2/SMB3 authentication, signing-key derivation, and transport signing/encryption paths.

Risks: NTLMv2 and ARC4 paths are disabled or rejected under FIPS, so mount/auth error handling must propagate those failures clearly. AV-pair parsing must reject odd UTF-16 lengths and truncated blobs. `set_auth_key_response` replaces `ses->auth_key.response`; callers must preserve and free the old target-info blob correctly. Signature calculation assumes non-user-backed iterators are already prepared and returns EIO when iterators advance short. Authentication changes can easily break interop with domain defaults, SPN target names, or timestamp tolerance.

Test signals: NTLMv2 auth with explicit domain, auto-discovered domain, empty domain, DNS domain AV pairs, missing timestamp, and malformed AV blobs; FIPS-mode failures for NTLMv2/ARC4; signature calculation over kvec-only and iterator payload requests for MD5/HMAC/CMAC contexts; SPN target-name inclusion; memory leak checks around repeated session setup retries; and interoperability with Samba, Windows, and legacy NTLMSSP servers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsencrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsfs.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifsfs.c

Purpose: provides the main CIFS/SMB filesystem module entry point and VFS registration layer. It defines global tunables and counters, superblock operations, inode/file/directory operation tables, mount orchestration, server-side copy/remap helpers, inode/slab/mempool/workqueue lifecycle, and module init/exit.

Important APIs and functions: visible objects include `cifs_fs_type`, `smb3_fs_type`, `cifs_dir_inode_ops`, `cifs_file_inode_ops`, `cifs_symlink_inode_ops`, `cifs_file_ops`, `cifs_file_strict_ops`, `cifs_file_direct_ops`, `cifs_file_nobrl_ops`, `cifs_file_strict_nobrl_ops`, `cifs_file_direct_nobrl_ops`, `cifs_dir_ops`, `cifs_sb_active`, `cifs_sb_deactive`, `cifs_smb3_do_mount`, and `cifs_file_copychunk_range`. Major internal functions include `cifs_read_super`, `cifs_kill_sb`, `cifs_statfs`, `cifs_permission`, `cifs_alloc_inode`, `cifs_evict_inode`, `cifs_show_options`, `cifs_umount_begin`, `cifs_get_root`, `cifs_llseek`, `cifs_setlease`, `cifs_remap_file_range`, request/inode/netfs/mid cache initialization, `init_cifs`, and `exit_cifs`.

Control flow: module load initializes error mapping, proc state, counters, random lock secret, workqueues, inode/netfs/mid/request caches, DFS/SPNEGO/SWN/idmap subsystems, then registers both `cifs` and `smb3` filesystems. Mount duplicates the parsed fs context, sets up the CIFS superblock, negotiates/mounts connections, reuses or creates an anonymous superblock via `sget`, reads root inode metadata, selects case-sensitive or case-insensitive dentry ops, and resolves a prefix root dentry if needed. VFS operations dispatch to dialect-specific server ops for queryfs, fallocate, llseek, copychunk, duplicate extents, and regular create/read/write/lock/readdir helpers from other files. Unmount closes cached directories and deferred handles, flushes oplock work, kills the superblock, and tears down connections. Module exit unregisters filesystems and releases subsystems in reverse order.

State and persistence behavior: global module state includes tunables such as `CIFSMaxBufSize`, `cifs_min_rcv`, `cifs_min_small`, `cifs_max_pending`, `dir_cache_timeout`, security/encryption toggles, global XID counters, allocation counters, connection lists, workqueues, mempools, and slab caches. Per-superblock state is `cifs_sb_info`, root dentry, mount context, BDI readahead settings, VFS flags, and tcon/session references. Persistent server state is modified indirectly through open/close, setattr, copychunk/remap, fallocate, ACL, xattr, and directory operations. Pagecache/netfs/fscache state is explicitly flushed or invalidated around remap and copy operations.

Dependencies and integration points: integrates with VFS superblock/inode/file/dentry APIs, netfs writeback, fscache, workqueues, mempools, slab caches, mount fs_context parsing, SMB dialect operation tables, DFS/SPNEGO/SWN/idmap optional subsystems, cached directory handles, deferred close handling, oplock/lease work, pagecache invalidation, and server-side copy offload.

Risks: init and exit have many ordered resources; missing one error unwind can leak global state or leave a registered filesystem with incomplete support. Mount reuse must compare the correct flags and release unused connection objects. Copy/remap must flush source data, preserve dirty destination folios outside the target range, update EOF/zero-point/fscache state, and translate unsupported overlap cases correctly. Lease decisions must match oplock state or local-lease semantics. `cifs_show_options` can expose stale or incomplete option state if fields are not maintained consistently.

Test signals: module load/unload with every optional config combination; mount and remount of `cifs` and `smb3`, including superblock reuse, prefix paths, case-insensitive shares, snapshots, POSIX ACLs, and read-only snapshots; forced unmount with pending requests and deferred closes; statfs/queryfs failures; loose/strict/direct/nobrl file operation selection; copy_file_range and remap_file_range across same file, cross-file, cross-session, EOF-extension, overlap, and fallback paths; cache/fscache invalidation checks; and fault injection through each init error label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsfs.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifsfs.h

Purpose: declares the CIFS VFS-facing interface exported across the SMB client. It names the filesystem types, inode/file/address-space/dentry operation tables, mount entry point, inode and dentry helpers, and user-visible version constants.

Important APIs and types: defines `ROOT_I`, `SMB3_PRODUCT_BUILD`, `CIFS_VERSION`, temporary/silly rename name prefixes, `cifs_uniqueid_to_ino_t`, `cifs_set_time`, and `cifs_get_time`. It declares `cifs_fs_type`, `smb3_fs_type`, inode operations, file operations, dentry operations, address-space operations, root inode lookup, create/open/lookup/unlink/link/mkdir/rmdir/rename/revalidation/getattr/setattr/fiemap helpers, file read/write/lock/fsync/flush/mmap/readdir helpers, `cifs_file_copychunk_range`, `cifs_ioctl`, `cifs_setsize`, and `cifs_smb3_do_mount`.

Control flow: the header has no runtime flow, but it defines the cross-file call graph between `cifsfs.c`, inode/namei/file/dir/xattr/export modules, and VFS registration. Inline inode conversion hashes 64-bit server file ids down for 32-bit `ino_t` while avoiding inode number zero. Dentry time helpers store attribute-cache timestamps in `d_fsdata`.

State and persistence behavior: persistent state is not stored here. The declared APIs manipulate VFS inode/dentry/pagecache state, server file ids, temporary delete-on-close names, mount roots, and remote file state through implementations elsewhere. The version constants identify the client module version exposed at module metadata level.

Dependencies and integration points: includes Linux hash and dcache APIs and is included by files implementing CIFS VFS operations. It also exposes optional xattr and NFSD export hooks behind config guards.

Risks: `cifs_uniqueid_to_ino_t` intentionally hashes server ids on 32-bit architectures, so inode collisions remain possible and must be handled by inode lookup code. Storing timestamps in `d_fsdata` assumes no other dentry subsystem consumer overwrites it. Prototype drift here can break operation table wiring or optional config builds.

Test signals: 32-bit inode-number behavior with large server ids, attribute-cache timeout behavior through dentry timestamp helpers, builds with and without xattr/NFSD export support, VFS operation table linkage, and module version consistency when changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsglob.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifsglob.h

Purpose: defines the central shared object model, constants, operation vectors, state machines, locking order, global variables, and inline helpers for the Linux CIFS/SMB client. Most implementation files depend on this header for connection, session, tree, inode, file, request, credit, DFS, multichannel, caching, security, and reconnect state.

Important APIs and types: key enums include `statusEnum`, `ses_status_enum`, `tid_status_enum`, `securityEnum`, `upcall_target_enum`, `cifs_reparse_type`, `cifs_symlink_type`, `cifs_find_flags`, and inode flags. Major structs include `session_key`, `cifs_secmech`, `ntlmssp_auth`, `cifs_open_info_data`, `smb_rqst`, `smb_version_operations`, `cifs_mnt_data`, `TCP_Server_Info`, `cifs_credits`, `cifs_server_iface`, `cifs_chan`, `cifs_ses`, `cifs_fattr`, `cifs_tcon`, `tcon_link`, `cifs_pending_open`, `cifs_deferred_close`, `cifsLockInfo`, `cifs_search_info`, `cifs_open_parms`, `cifs_fid`, `cifsFileInfo`, `cifs_io_parms`, `cifs_io_request`, `cifs_io_subrequest`, `cifsInodeInfo`, `mid_q_entry`, `dfs_info3_param`, and `cifs_mount_ctx`. Important helpers cover server locking, credit accounting, MID generation, DFS path cleanup, retry classification, tcon link refcounts, fileinfo refcounts, CIFS_SB extraction, delimiter conversion, stats accounting, callback execution, reconnect scheduling, cache-state checks, forced shutdown, create option construction, and block count calculation.

Control flow: dialect implementations fill `smb_version_operations`; higher layers call through this table for negotiate/session setup/tree connect, open/query/set/close, read/write, directory enumeration, signing/encryption transforms, ACLs, leases/oplocks, copy offload, reparse parsing, DFS referrals, and ioctl support. Transport code allocates `mid_q_entry` objects, queues requests on `TCP_Server_Info::pending_mid_q`, tracks credits and in-flight counts under locks, and executes receive/handle/callback hooks. Mount code builds `TCP_Server_Info -> cifs_ses -> cifs_tcon -> tcon_link` graphs, while open paths add `cifsFileInfo` and `cifs_fid` objects to tcon and inode lists. Reconnect helpers mark servers, sessions, tcons, channels, and MIDs with status bits and reschedule delayed reconnect work.

State and persistence behavior: this header defines in-memory state rather than on-disk state. `TCP_Server_Info` persists connection-level socket, dialect, signing, encryption, RDMA, compression, credit, MID, reconnect, echo, multichannel, and DFS target state for a server connection. `cifs_ses` persists authentication, keys, channels, DFS root sessions, interfaces, and user identity. `cifs_tcon` persists share state, capabilities, statistics, cached directory handles, fscache volume, pending opens, and reconnect flags. `cifsInodeInfo` persists client-side inode cache, lease/oplock, uniqueid, creation time, deferred closes, and reparse metadata while the inode lives. Request and MID state persists only while operations are outstanding.

Dependencies and integration points: includes Linux networking, crypto-adjacent, netfs, mempool, workqueue, lock, and mount headers plus CIFS superblock, ACL, common SMB, SMB1, SMB2, and FSCC wire definitions. It is the integration point between transport, connect, SMB1/SMB2/SMB3 dialect code, inode/file/dir operations, ACLs, DFS cache, SMB Direct, fscache, witness, multichannel, and trace/debug code.

Risks: this file encodes lock ordering for the whole module; violating it can deadlock reconnect, open-file, MID, or inode-lock paths. The `smb_version_operations` table is large and partially optional, so callers must guard unsupported dialect hooks. Credit accounting, channel reconnect bitmaps, MID states, and callback single-execution semantics are concurrency-sensitive. Many globals are shared across mounts and network namespaces. Struct layout changes have wide blast radius, especially for cached handles, fids, netfs integration, and security/session key fields.

Test signals: lockdep under reconnect, multichannel, oplock breaks, deferred close, and forced unmount; request credit exhaustion and wakeups; MID cancellation, malformed response, transform response, retry, and callback paths; dialect fallback with missing operation hooks; DFS failover and referral path equality; channel scaling and reconnect bitmaps; cache-state macros under lease break and mount-cache flags; 32-bit/64-bit builds; and optional configs for stats, DFS, SWN, SMB Direct, fscache, legacy SMB1, and upcalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsglob.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifspdu.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifspdu.h

Purpose: currently acts as an empty compatibility include guard for the CIFS PDU header name in this source tree.

Important APIs and functions: it defines only `_CIFSPDU_H` include guards and no structures, constants, prototypes, or inline helpers.

Control flow: no executable code or macro control flow exists beyond the guard.

State and persistence behavior: no state is declared and no persistent wire-format structures are defined here. CIFS/SMB PDU definitions used by this client live in headers such as `smb1pdu.h`, `smb2pdu.h`, and common SMB headers.

Dependencies and integration points: any include of this file succeeds without pulling in additional definitions. Its main integration role is source compatibility for code that still references `cifspdu.h`.

Risks: adding real PDU definitions here could create duplicate or divergent wire structures compared with the maintained SMB1/SMB2/common headers. Removing it could break stale include paths.

Test signals: allmodconfig/allyesconfig build coverage and include-cleanup checks to confirm no translation unit expects declarations from this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifspdu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsproto.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifsproto.h

Purpose: declares the main internal CIFS client function prototypes and lightweight inline helpers shared across transport, mount, connection, inode, file, directory, ACL, DFS, multichannel, reparse, and crypto code.

Important APIs and functions: declares buffer allocation/release, XID tracing macros, path builders, MID lifecycle, async/sync send/receive, reconnect, channel selection, writable/readable file lookup, time conversion, oplock and lock helpers, inode/fattr conversion, ACL/idmap APIs, socket receive helpers, mount/session/tcon lifecycle, deferred close and pending open helpers, tree/session setup, DFS parsing, session/tcon allocation, NTLMv2 and signing-key helpers, symlink/reparse helpers, multichannel helpers, DFS super helpers, SFU special file helpers, and wire mode conversion. Inline helpers include `send_cancel`, `alloc_dentry_path`, `free_dentry_path`, `cifs_create_options`, `cifs_put_smb_ses`, `cifs_smb_ses_inc_refcount`, `dfs_src_pathname_equal`, `smb_get_mid`, `release_mid`, `cifs_free_open_info`, `smb_EIO*`, `cifs_get_num_sgs`, `cifs_sg_set_buf`, `cifs_get_writable_file`, and `find_readable_file`.

Control flow: implementation files include this header to route operations across subsystem boundaries. `get_xid` and `free_xid` wrap request tracing around call sites. Send/receive prototypes describe the core flow of allocating/queuing MIDs, waiting for credits and responses, and dispatching callbacks. Mount prototypes drive TCP session acquisition, SMB session setup, tree connection, superblock matching, and unmount. File and inode prototypes expose lookup, revalidation, open-file reuse, deferred close, and byte-range lock flows. Inline scatterlist helpers count and populate SG entries for transform encryption/decryption.

State and persistence behavior: this header does not own state but exposes functions that mutate nearly every major CIFS state object: global XID counters, TCP server connection state, session keys, tcon references, inode attributes, pagecache/netfs state, open file lists, pending MID queues, DFS referrals, cached reparse data, and server-side file metadata. Inline cleanup helpers free reparse and symlink buffers embedded in `cifs_open_info_data`.

Dependencies and integration points: includes NLS/ctype, `cifsglob.h`, tracepoints, optional DFS cache, and SMB1 prototypes. It is the primary compile-time contract between `cifsfs.c`, `connect.c`, `transport.c`, `inode.c`, `file.c`, `dir.c`, `misc.c`, ACL code, SMB2/SMB3 code, DFS code, and crypto code.

Risks: because this is a broad internal ABI, prototype drift or wrong config guards can break many files. The `free_xid` macro assumes an `rc` variable is in scope, which is easy to misuse. SG helpers must not accept user-backed or pinning iterators and must correctly handle vmalloc/stack buffers. Reference helpers for sessions and MIDs must be paired correctly to avoid leaks or use-after-free. Inline error helpers trace and return `-EIO`, so callers must not lose more specific parse-failure context where it matters.

Test signals: build coverage across optional configs; tracepoint validation for `get_xid`/`free_xid`; send/receive cancellation and reconnect tests; transform encryption SG construction for kvec, vmalloc, stack signature, and bvec iterators; static analysis for `free_xid` macro scope; refcount tests for MIDs and DFS root sessions; and integration tests for ACL, DFS, reparse, multichannel, and mount lifecycle prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsproto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsroot.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifsroot.c

Purpose: implements early-boot CIFS root filesystem parameter handling for `cifsroot=`, allowing the kernel to mount an SMB share as the root filesystem.

Important APIs and functions: defines default root mount options in `DEFAULT_MNT_OPTS`, stores early root device/options in `root_dev` and `root_opts`, parses IPv4 server addresses with `parse_srvaddr`, handles the boot parameter in `cifs_root_setup`, registers it via `__setup("cifsroot=", ...)`, and exposes `cifs_root_data` to return the parsed device and options to root-mount code.

Control flow: `cifs_root_setup` runs during early parameter parsing. If the argument looks like `//server/share[,options]`, it sets `ROOT_DEV = Root_CIFS`, copies the UNC path up to the comma into `root_dev`, extracts an IPv4 address from the server portion into `root_server_addr`, and appends user-supplied options to the default mount option string. Later, `cifs_root_data` verifies that a device and server address were recorded and returns pointers to the static buffers.

State and persistence behavior: state is early-init static data marked `__initdata`; it persists only during boot setup. The effective root mount options default to SMB1-era settings including `vers=1.0`, `cifsacl`, `mfsymlinks`, large `rsize`, fixed `wsize`, uid/gid 0, hard mount, and `rootfs`, with user options appended.

Dependencies and integration points: depends on Linux init parameter parsing, root device selection, `root_server_addr` from IP autoconfiguration/root infrastructure, IPv4 `in_aton`, and CIFS mount option parsing later in the normal SMB client mount stack. It is invoked before the full filesystem module mount flow.

Risks: IPv6 is explicitly unsupported. Address parsing accepts only digits and dots from the server substring, so DNS names or bracketed IPv6 cannot populate `root_server_addr`. The default `vers=1.0` is insecure and may conflict with modern servers or with configurations that disable legacy dialects. Option string length is bounded and truncation returns an early error. `cifs_root_setup` returns `1` even on ignored or failed parse paths, following `__setup` convention but requiring log messages for diagnosis.

Test signals: boot parameter tests for valid `//IPv4/share`, option append, too-long UNC, too-long options, missing share, DNS name, invalid address, absent `cifsroot`, and root mount handoff; modern SMB server tests requiring `vers=3.x` override; and explicit coverage that IPv6 remains rejected or is implemented intentionally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifsroot.c -->
