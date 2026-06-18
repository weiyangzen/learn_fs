# Group Research: group_781_linux_sources_os_linux_linux_fs_nfs_internal_h_sources_os_linux_linu_3d721f9b120b

Scope verified against `Docs/research_subset_a.md`: `sources/os/linux/linux` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/internal.h -->
# File Research: sources/os/linux/linux/fs/nfs/internal.h

## Purpose
Central private header for the Linux NFS client. It connects mount parsing, client/server setup, page I/O, namespace/submount handling, LOCALIO, NFSv2/v3/v4 procedure plumbing, inode/file operations, writeback/commit helpers, and direct I/O state.

## Main Interfaces
- Defines `struct nfs_client_initdata`, the input used to construct `nfs_client` objects: server address, hostname, protocol, NFS subversion module, net namespace, credentials, transport security, connection counts, and timeout values.
- Defines `struct nfs_fs_context`, the in-kernel mount context for parsed mount options, server and mount-server addresses, auth flavor selection, transport security, clone/submount state, and resulting `nfs_server`.
- Defines `struct nfs_mount_request`, consumed by `mount_clnt.c` for v2/v3 MOUNT protocol lookups.
- Declares internal NFS APIs for client allocation/probing, server creation/cloning, procfs setup, page cache slab setup, pgio operations, directory/file/inode operations, namespace automounts, read/write/commit paths, NFSv4 state/client helpers, and direct I/O.
- Declares `struct nfs_direct_req`, the direct I/O refcounted completion and commit tracker.
- Adds `struct file_kattr` forward declaration and `nfs_fileattr_get()` for file attribute support in inode operation tables.

## Important Inline Policy
- Mountpoint and referral handling: `nfs_attr_check_mountpoint()`, `nfs_attr_use_mounted_on_fileid()`, `nfs_lookup_is_soft_revalidate()`.
- Mount diagnostics: `nfs_errorf`, `nfs_invalf`, `nfs_warnf`, and fs_context-aware variants.
- I/O sizing and serialization: `flags_to_mode()`, `nfs_file_block_o_direct()`, `nfs_block_bits()`, `nfs_block_size()`, `nfs_io_size()`, `nfs_super_set_maxbytes()`, `nfs_folio_length()`, `nfs_page_array_len()`.
- Writeback and commit helpers: `nfs_folio_mark_unstable()`, write verifier comparison, pNFS DS commit verifier clearing.
- Error classification: `nfs_error_is_fatal()` and `nfs_error_is_fatal_on_server()`.
- Miscellaneous helpers: NFS-specific suid/sgid stripping, timestamp-to-change-attribute conversion, NFSv4 stateid hashing, default port selection, and inode/superblock active-reference pairing.

## Configuration-Dependent Behavior
- `CONFIG_NFS_V4` gates v4 XDR/procedure declarations and pNFS verifier helpers.
- `CONFIG_NFS_V4_SECURITY_LABEL` gates security label allocation/copy/cache invalidation helpers.
- `CONFIG_NFS_LOCALIO` exposes local file open, local pgio, local commit, and local server probe hooks; otherwise stubs return disabled behavior.
- `CONFIG_PROC_FS`, `CONFIG_NFS_FSCACHE`, and `CONFIG_MIGRATION` provide feature-specific or no-op paths.

## Dependencies and Coupling
This header is deliberately high-coupling. It is the contract among NFS mount setup, RPC procedure modules, VFS inode/file operations, page I/O, pNFS, LOCALIO, and NFSv4 state management. Changes here can affect many `fs/nfs` translation units.

## Research Notes
The header contains real behavioral policy despite being mostly declarations. The subtle areas are I/O size alignment, buffered-vs-direct serialization, fatal error classification, suid/sgid stripping, mountpoint detection, and LOCALIO stubbing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/io.c -->
# File Research: sources/os/linux/linux/fs/nfs/io.c

## Purpose
Implements NFS client serialization between buffered I/O and direct I/O using `inode->i_rwsem` plus the `NFS_INO_ODIRECT` inode flag.

## Key Functions
- `nfs_start_io_read()` starts buffered reads. It takes `i_rwsem` shared when already in buffered mode, or upgrades through exclusive locking to clear direct-I/O mode.
- `nfs_end_io_read()` releases the shared lock.
- `nfs_start_io_write()` starts buffered writes. It takes `i_rwsem` exclusive and blocks direct I/O by clearing `NFS_INO_ODIRECT` and waiting for in-flight DIO.
- `nfs_end_io_write()` releases the exclusive lock.
- `nfs_start_io_direct()` starts direct I/O. It takes shared locking if direct mode is already active, otherwise takes exclusive locking, sets `NFS_INO_ODIRECT`, syncs the mapping, then downgrades.
- `nfs_end_io_direct()` releases the shared lock.

## Synchronization Model
Buffered reads can run concurrently with other buffered reads. Direct I/O can run concurrently with other direct I/O. Mode transitions require exclusive `i_rwsem`. Buffered writes and truncates serialize against both read and direct paths through the write side of `i_rwsem`.

## Research Notes
This file is small but important for page-cache coherency. Its central invariant is that switching between buffered and direct paths flushes or waits at the transition while preventing concurrent mode flips.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/iostat.h -->
# File Research: sources/os/linux/linux/fs/nfs/iostat.h

## Purpose
Defines per-mount NFS client I/O statistics storage and lightweight per-CPU accounting helpers.

## Main Types and Helpers
- `struct nfs_iostats` stores byte counters and event counters indexed by public NFS iostat enums, cacheline-aligned.
- `nfs_inc_server_stats()` / `nfs_inc_stats()` increment event counters using `this_cpu_inc()`.
- `nfs_add_server_stats()` / `nfs_add_stats()` add byte counts using `this_cpu_add()`.
- `nfs_alloc_iostats()` wraps `alloc_percpu(struct nfs_iostats)` as a macro for allocation tagging.
- `nfs_free_iostats()` frees non-NULL per-CPU stats.

## Dependencies
Uses `<linux/nfs_iostat.h>` for counter indexes and expects `NFS_SERVER(inode)->io_stats` to point at allocated per-CPU storage.

## Research Notes
Header-only hot-path accounting. Locking is avoided because all updates are per-CPU.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/iostat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/localio.c -->
# File Research: sources/os/linux/linux/fs/nfs/localio.c

## Purpose
Implements NFS client LOCALIO support. When the NFS server is local to the same kernel, reads, writes, and commits can bypass network RPC and operate directly on an `nfsd_file`, while preserving normal NFS pgio and commit completion semantics.

## Main Concepts
- LOCALIO detection uses the auxiliary `nfslocalio` RPC program and `UUID_IS_LOCAL`.
- A client is local only when UUID state maps to local server state and `localio_enabled` is true.
- Data I/O still completes through NFS RPC-style callbacks so upper NFS layers see normal `nfs_pgio_header` and `nfs_commit_data` completion.

## Key Data Structures
- `struct nfs_local_kiocb` wraps a `kiocb`, bvec array, target pgio header, work item, local `nfsd_file`, and up to three iterators for direct-I/O splitting.
- `struct nfs_local_fsync_ctx` tracks local commit/fsync work and optional synchronous completion.
- `struct nfs_local_dio` is declared in `internal.h` and describes misaligned start, aligned middle, and misaligned end extents.

## Probe and Open Path
- XDR helpers encode/decode the UUID probe.
- `nfs_init_localioclient()` binds the auxiliary localio program to an existing NFS RPC client.
- `nfs_server_uuid_is_local()` sends `UUID_IS_LOCAL` and verifies local UUID state.
- `nfs_local_probe()` disables LOCALIO if globally disabled or auth is not `AUTH_SYS`; otherwise it probes and enables local state.
- `nfs_local_probe_async()` queues probing on `nfsiod_workqueue`.
- `nfs_local_open_fh()` opens read-only or read-write cached local file handles via `nfs_open_local_fh()` and reprobes on selected failures.

## Read/Write Path
- `nfs_local_iocb_alloc()` allocates local I/O state, bvecs, and sets GFP_NOFS context on the backing mapping.
- `nfs_local_iters_init()` converts the NFS page array into bvec-backed iterators.
- Direct I/O support queries nfsd alignment, splits requests into up to three iterators, and uses `IOCB_DIRECT` only for aligned extents.
- `nfs_local_call_read()` and `nfs_local_call_write()` invoke `read_iter()` / `write_iter()` under file credentials on `nfslocaliod_workqueue`.
- Writes set sync flags from NFS stable-write mode and use a local boot verifier.
- Short writes mark the open context for synchronous writes.

## Completion and Commit
- `nfs_local_pgio_done()` accumulates counts and maps negative errno values to NFS status values.
- AIO completions are bounced to `nfsiod_workqueue` because they may occur in bottom-half context.
- `nfs_local_read_done()` clears `res.replen` to avoid corruption if falling back to normal RPC and sets EOF from local file size.
- `nfs_local_vfs_getattr()` refreshes fattr fields after local writes, including NFSv4 change attribute behavior.
- `nfs_local_commit()` runs `vfs_fsync_range()` asynchronously or synchronously, fills commit verifier/status, and releases through normal commit callbacks.

## Research Notes
The sensitive areas are DIO alignment splitting, preserving callback ordering, resetting the boot verifier on errors, avoiding reclaim recursion with GFP flags, and keeping LOCALIO fallback compatible with normal RPC completion paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/localio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/mount_clnt.c -->
# File Research: sources/os/linux/linux/fs/nfs/mount_clnt.c

## Purpose
Implements the in-kernel NFS MOUNT protocol client used by NFSv2/v3 mounts to obtain a root file handle and optional auth flavor list from mountd.

## Main Entry Point
- `nfs_mount()` validates the export path length, creates a temporary MOUNT RPC client, selects v1 or v3 MOUNT procedure, sends `MOUNTPROC_MNT` with soft timeout behavior, copies the returned file handle, and fills auth flavors.
- If the server does not provide auth flavors or the protocol is not MOUNT v3, it fakes a permissive one-entry `RPC_AUTH_NULL` flavor list.

## XDR Encoding and Decoding
- `encode_mntdirpath()` encodes the export path.
- v1/v2 decode path maps OpenGroup XNFS MOUNT statuses and decodes fixed-size `NFS2_FHSIZE` file handles.
- v3 decode path maps RFC 1813 statuses, decodes variable-size file handles, rejects zero or oversized handles, and decodes up to `NFS_MAX_SECFLAVORS`.

## RPC Tables
Defines procedure tables for MOUNT v1 and MOUNT v3, exposes only MOUNT and UMOUNT procedures in this client, and registers them under the `mount` RPC program.

## Research Notes
This file is mount-bootstrap infrastructure, not regular file I/O. Its important edge handling is path length validation, file handle validation, status-to-errno mapping, and auth-flavor fallback.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/mount_clnt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/namespace.c -->
# File Research: sources/os/linux/linux/fs/nfs/namespace.c

## Purpose
Implements NFS namespace handling: reconstructing server-side paths, automounting server-side mountpoints/referrals, expiring automounts, and creating submounts when crossing filesystem boundaries.

## Key Functions
- `nfs_path()` reconstructs a server pathname from an arbitrary dentry, using `rename_lock` sequence retry plus dentry locking, and optionally canonicalizes slash handling after the export name.
- `nfs_d_automount()` creates a submount fs_context, inherits credentials/net namespace/superblock flags from the parent, prepares clone data, invokes the protocol-specific submount operation, creates a vfsmount, and schedules expiry.
- `nfs_namespace_getattr()` / `nfs_namespace_setattr()` handle referral-like dentries with empty file handles specially.
- `nfs_expire_automounts()` marks automounts for expiry and reschedules while the list is non-empty.
- `nfs_do_submount()` clones the server, computes a source string with `nfs_devname()`, parses it into the fs_context, and gets the tree.
- `nfs_submount()` redoes lookup to refresh mountpoint attributes, selects the auth flavor, and calls `nfs_do_submount()`.

## Inode Operations
- `nfs_mountpoint_inode_operations` uses normal NFS getattr/setattr and wires `fileattr_get = nfs_fileattr_get`.
- `nfs_referral_inode_operations` uses namespace-specific getattr/setattr and also wires `fileattr_get = nfs_fileattr_get`.

## Module Parameter
`nfs_mountpoint_expiry_timeout` controls automount expiry in seconds. Values `<= 0` disable expiration; setter converts to jiffies and updates/cancels delayed work.

## Research Notes
The subtle parts are path reconstruction under concurrent rename, fs_context inheritance for submounts, active automount expiry management, and special referral dentries that may not carry a real file handle.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/namespace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/netns.h -->
# File Research: sources/os/linux/linux/fs/nfs/netns.h

## Purpose
Defines NFS-private per-network-namespace state accessed through `net_generic()`.

## Main Data
- DNS resolver cache and block-layout device pipe/reply state.
- Per-net NFS client and volume lists.
- NFSv4-only callback identifier IDR, callback ports, callback user counts, and v4 data server cache/list lock.
- Shared NFS client pointer, client-list spinlock, boot time, RPC stats, and optional procfs directory.

## Research Notes
This is a state container header. It is central to isolating NFS client lists, callback state, and proc/stat state per network namespace.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/netns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs.h -->
# File Research: sources/os/linux/linux/fs/nfs/nfs.h

## Purpose
Defines `struct nfs_subversion`, the registration object used by NFS version-specific modules, and declares version lookup/reference management APIs.

## Main Interfaces
- `struct nfs_subversion` contains module owner, filesystem type, RPC version table, client operation table, super operations, and xattr handlers.
- `find_nfs_version()`, `get_nfs_version()`, `put_nfs_version()`, `register_nfs_version()`, and `unregister_nfs_version()` manage available NFS protocol versions.

## Research Notes
This header is the narrow contract between the core NFS module and version modules such as NFSv2 and NFSv3.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs2super.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs2super.c

## Purpose
Registers and unregisters NFSv2 client support as a module-level NFS subversion.

## Main Behavior
- Defines static `nfs_v2` with owner, core `nfs_fs_type`, `nfs_version2`, `nfs_v2_clientops`, and `nfs_sops`.
- `init_nfs_v2()` registers the subversion.
- `exit_nfs_v2()` unregisters it.

## Research Notes
This is module glue. The behavioral implementation for NFSv2 lives primarily in shared client code and `nfs2xdr.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs2super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs2xdr.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs2xdr.c

## Purpose
Implements XDR encoding/decoding and the RPC procedure table for NFSv2.

## Encoding
Encodes v2 file handles, sattr, diropargs, readlink, read, write, create, remove, rename, link, symlink, and readdir arguments. It uses fixed-size v2 file handles and v2-specific 32-bit offset/count fields.

## Decoding
- Decodes status values through `decode_stat()` and maps protocol statuses to Linux errno.
- Decodes fattrs with user namespace uid/gid conversion, NFSv2 FIFO special handling, filesystem IDs, timestamps, and synthetic change attributes.
- Decodes read data into reply pages; NFSv2 has no explicit EOF flag, so EOF is set false in the read result.
- Decodes directory entries lazily from page cache in `nfs2_decode_dirent()`.
- Decodes statfs information into `struct nfs2_fsstat`.

## Edge Handling
- Rejects invalid uid/gid values.
- Checks path and filename lengths and terminates readlink path buffers.
- Detects short/cheating server read/path replies where reported length exceeds received data.
- Treats all NFSv2 writes as `NFS_FILE_SYNC`.

## RPC Table
Defines `nfs_procedures[]` for GETATTR, SETATTR, LOOKUP, READLINK, READ, WRITE, CREATE, REMOVE, RENAME, LINK, SYMLINK, MKDIR, RMDIR, READDIR, and STATFS, then exposes `nfs_version2`.

## Research Notes
This file is the NFSv2 wire-format boundary. The most important maintenance risk is preserving v2 quirks: fixed file handles, 32-bit sizes, no EOF-on-read flag, FIFO device encoding, and server-time timestamp convention.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs2xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs3_fs.h -->
# File Research: sources/os/linux/linux/fs/nfs/nfs3_fs.h

## Purpose
Declares NFSv3-specific filesystem interfaces for ACL support, server creation/cloning, and the NFSv3 subversion object.

## Main Interfaces
- Under `CONFIG_NFS_V3_ACL`, declares ACL get/set, SETACL RPC helper, and xattr listing.
- Without ACL support, `nfs3_proc_setacls()` is a no-op and `nfs3_listxattr` is `NULL`.
- Declares `nfs3_create_server()`, `nfs3_clone_server()`, and external `nfs_v3`.

## Research Notes
This header is the NFSv3-specific bridge between `nfs3proc.c`, `nfs3acl.c`, `nfs3client.c`, and module registration.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs3_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs3acl.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs3acl.c

## Purpose
Implements NFSv3 POSIX ACL operations using the Sun NFSACL side protocol.

## Key Functions
- `nfs3_get_acl()` fetches access/default ACLs, handles RCU refusal, revalidates inode change state, prepares race-safe ACL cache sentinels, calls GETACL, updates inode attributes, and caches or releases returned ACLs.
- `__nfs3_proc_setacls()` validates ACL support and entry counts, allocates pages when needed, sends SETACL, zaps access/ACL caches, and refreshes inode attributes.
- `nfs3_proc_setacls()` treats `-EOPNOTSUPP` as non-fatal for create/mkdir/mknod post-processing.
- `nfs3_set_acl()` coordinates access/default ACL pairs for directories and synthesizes an access ACL from mode when clearing.
- `nfs3_listxattr()` lists POSIX ACL xattr names only when corresponding ACLs exist.

## Edge Handling
- Disables server ACL capability on protocol-not-supported failures.
- Caps ACL entries at `NFS_ACL_MAX_ENTRIES`.
- Frees XDR-allocated pages from GETACL and SETACL page allocations.
- Uses POSIX ACL cache sentinel helpers to avoid racing with generic ACL cache population.

## Research Notes
This file is optional behind `CONFIG_NFS_V3_ACL`. Its behavior is tightly coupled to `nfs3xdr.c` ACL XDR procedures and `nfs3client.c` ACL RPC client setup.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs3acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs3client.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs3client.c

## Purpose
Provides NFSv3-specific server/client setup, including the optional NFSACL RPC client and pNFS data server client creation.

## Key Functions
- `nfs_init_server_aclclient()` binds the NFSACL program to the server RPC client unless `NFS_MOUNT_NOACL` is set; on success, marks `NFS_CAP_ACLS`.
- `nfs3_create_server()` wraps generic server creation and initializes the ACL client.
- `nfs3_clone_server()` clones a server and initializes ACL support on the clone when the source has it.
- `nfs3_set_ds_client()` builds a pNFS data server `nfs_client` for NFSv3, using MDS identity/net/credentials, soft timeout settings, DS flags, optional TLS inheritance, `nconnect`, noresvport, and network-unreachable fatal behavior.

## Research Notes
The pNFS DS path is the nuanced part: it deliberately uses short soft timeouts so data server failures can be retried through the metadata server.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs3client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs3proc.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs3proc.c

## Purpose
Implements client-side NFSv3 procedure stubs and exports the `nfs_v3_clientops` operation table used by the generic NFS client.

## Core RPC Behavior
- Wraps synchronous RPC calls to retry `-EJUKEBOX` with killable/freezable sleep.
- Provides async jukebox handling for unlink, rename, read, write, and commit completion.
- Implements GETROOT/FSINFO fallback from per-server client to base client when needed.
- Implements NFSv3 procedures: getattr, setattr, lookup/lookupp, access, readlink, create, remove/unlink, rename, link, symlink, mkdir, rmdir, readdir/readdirplus, mknod, statfs, fsinfo, pathconf, read/write setup/done, commit setup/done, and lock handling.

## Creation and Metadata
- Shared `nfs3_createdata` supports create, mkdir, symlink, and mknod.
- Exclusive create falls back from EXCLUSIVE to GUARDED to UNCHECKED on `-ENOTSUPP`.
- POSIX ACLs are created and applied after create/mkdir/mknod when enabled.
- Attribute refreshes use post-op or weak-cache-consistency fattrs.

## I/O and LOCALIO
- Read completion records server read header size, refreshes inode attrs, invalidates atime, and can trigger throttled NFSv3 LOCALIO reprobes.
- Write completion updates inode writeback state and can trigger LOCALIO reprobes.
- `nfs3_localio_probe_throttle` controls periodic LOCALIO reprobe frequency for successful normal RPC I/O.

## Locking
Uses lockd via `nlmclnt_proc()`. Close-unlock paths hold NFS open/lock contexts and can wait for asynchronous I/O counters before unlock.

## Operation Tables
- Directory and file inode operations include permission/getattr/setattr and `fileattr_get = nfs_fileattr_get`.
- ACL hooks are included when `CONFIG_NFS_V3_ACL` is enabled.
- `nfs_v3_clientops` binds all NFSv3 client operations, inode/file ops, lock ops, pgio callbacks, commit callbacks, server creation/cloning, delegation stubs, and close-context behavior.

## Research Notes
This is the main NFSv3 behavioral dispatch file. The important risks are error retry semantics, post-op attribute consistency, create fallback behavior, ACL post-processing, localio reprobe throttling, and preserving callback contracts for async RPC paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs3proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs3super.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs3super.c

## Purpose
Registers and unregisters NFSv3 client support as a module-level NFS subversion.

## Main Behavior
- Defines exported `nfs_v3` with owner, core `nfs_fs_type`, `nfs_version3`, `nfs_v3_clientops`, and `nfs_sops`.
- `init_nfs_v3()` registers the subversion.
- `exit_nfs_v3()` unregisters it.

## Research Notes
This is module glue. NFSv3 behavior lives in `nfs3proc.c`, `nfs3xdr.c`, `nfs3client.c`, and optional `nfs3acl.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs3super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs3xdr.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs3xdr.c

## Purpose
Implements XDR encoding/decoding and RPC procedure tables for NFSv3 and optional NFSv3 ACL side protocol.

## Encoding
Encodes NFSv3 primitive types, file handles, sattrs, diropargs, getattr/setattr, lookup, access, readlink, read, write, create, mkdir, symlink, mknod, remove, rename, link, readdir, readdirplus, commit, and optional ACL GETACL/SETACL arguments.

## Decoding
- Decodes protocol statuses and maps them to errno.
- Decodes fattrs with user namespace uid/gid conversion, device numbers, fsid/fileid, timestamps, and synthetic change attributes.
- Decodes post-op attrs and weak-cache-consistency data.
- Decodes read/write results, including opaque length matching, EOF, stable write verifier, op status, and server-cheating checks.
- Decodes create, remove, rename, link, readdir/readdirplus, fsstat, fsinfo, pathconf, and commit results.
- `nfs3_decode_dirent()` lazily decodes cached directory entries and handles READDIRPLUS fattrs/file handles, `mounted_on_fileid`, and `d_type`.
- ACL decoders validate returned ACL masks and decode access/default ACL payloads.

## Notable Behavior
- Rejects zero or oversized v3 file handles.
- `decode_pathconf3resok()` stores `max_link`, `max_namelen`, `case_insensitive`, and `case_preserving`.
- READDIR replies are read into page cache with actual entry decoding deferred to getdents-time.
- FSINFO clears v4-only lease/change/xattr fields.
- COMMIT sets verifier committed mode to `NFS_FILE_SYNC` on success.

## RPC Tables
Defines `nfs3_procedures[]` for all core NFSv3 procedures and exposes `nfs_version3`. Under `CONFIG_NFS_V3_ACL`, defines `nfs3_acl_procedures[]` and `nfsacl_version3`.

## Research Notes
This is the NFSv3 wire-format boundary. The most sensitive areas are XDR length accounting, uid/gid namespace conversion, WCC/post-op attr preservation, READ/READDIR page handling, pathconf case flags, and ACL page-buffer encoding/decoding.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs3xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs40.h -->
# File Research: sources/os/linux/linux/fs/nfs/nfs40.h

## Purpose
Declares NFSv4.0-specific client, procedure, and state/trunking interfaces.

## Main Interfaces
- Client lifecycle: `nfs40_shutdown_client()`, `nfs40_init_client()`, `nfs40_handle_cb_pathdown()`.
- Minor-version operation table: `nfs_v4_0_minor_ops`.
- Trunking discovery: `nfs40_discover_server_trunking()`.

## Research Notes
This header is the v4.0-specific bridge among client setup, v4.0 procedure/state code, and generic v4 minor-version dispatch.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs40.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs40client.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs40client.c

## Purpose
Implements NFSv4.0 client initialization, callback path recovery, and server trunking discovery.

## Key Functions
- `nfs40_init_client()` allocates and initializes the NFSv4.0 slot table.
- `nfs40_shutdown_client()` tears down and frees the slot table.
- `nfs40_handle_cb_pathdown()` marks the lease expired and returns delegations after callback path failure.
- `nfs4_schedule_path_down_recovery()` schedules the state manager after callback path recovery setup.
- `nfs40_discover_server_trunking()` sends SETCLIENTID, stores returned clientid/verifier, then walks existing clients to detect same-server trunking.
- `nfs40_walk_client_list()` tests candidate clients with SETCLIENTID_CONFIRM and swaps callback identifiers when an existing client is confirmed as the same server.

## Research Notes
The delicate logic is callback identifier swapping under per-net client lock and using SETCLIENTID_CONFIRM outcomes to distinguish true trunking from coincidental verifier matches.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs40client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs40proc.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs40proc.c

## Purpose
Defines NFSv4.0 minor-version procedure behavior, including sequence slot handling, lease renewal, migration recovery, lockowner release, and state recovery operation tables.

## Key Behavior
- `nfs40_call_sync_prepare()` / `nfs40_call_sync_done()` wrap synchronous calls with v4 sequence setup and completion.
- `nfs40_sequence_done()` frees v4.0 sequence slots.
- `nfs40_open_expired()` clears delegation state and recovers open state without v4.1-style delegation recovery.
- Async and sync RENEW paths maintain leases and schedule recovery on lease moved, lease recovery, or callback path down errors.
- `_nfs40_proc_get_locations()` and `_nfs40_proc_fsid_present()` support migration and lease-moved recovery with appended RENEW.
- `nfs4_release_lockowner()` sends RELEASE_LOCKOWNER asynchronously for v4.0 lock state cleanup.

## Operation Tables
Defines v4.0 sequence slot ops, reboot recovery ops, no-grace recovery ops, state renewal ops, migration recovery ops, and the exported `nfs_v4_0_minor_ops`.

## Research Notes
This file is v4.0 state-machine glue. The main maintenance risks are slot release ordering, lease renewal timestamps, recovery scheduling on specific NFS4 errors, and v4.0-only lockowner release behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs40proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs42.h -->
# File Research: sources/os/linux/linux/fs/nfs/nfs42.h

## Purpose
Declares NFSv4.2 client procedure interfaces and helper constants.

## Main Interfaces
Under `CONFIG_NFS_V4_2`, declares procedure helpers for allocate, copy, deallocate, zero range, llseek, layoutstats, clone, layouterror, copy notify, getxattr, setxattr, listxattr, and removexattr.

## Helpers
- `PNFS_LAYOUTSTATS_MAXDEV` caps layoutstats devices per compound.
- `READ_PLUS_SCRATCH_SIZE` defines scratch sizing.
- `nfs42_files_from_same_server()` compares server owner major IDs for copy/clone decisions.
- `nfs42_listxattr_xdrsize()` estimates listxattr XDR buffer size for a requested output size and rounds to 4-byte alignment.

## Research Notes
This header is declarative but important for v4.2 feature gating. The listxattr sizing helper encodes assumptions about worst-case user xattr name packing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs42.h -->