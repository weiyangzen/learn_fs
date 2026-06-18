# Group Research: group_1023_linux_stable_sources_os_linux_linux_stable_fs_nfs_internal_h_source_3a1ce60e7098

Scope verified against `Docs/research_subset_a.md`: `sources/os/linux/linux-stable` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/internal.h

## Purpose
Central private header for the Linux NFS client implementation. It ties together mount parsing, client/server lifecycle, page I/O, namespace/submount handling, localio, NFSv2/v3/v4 procedure tables, inode/file operations, commit/writeback helpers, and small inline utilities shared across `fs/nfs`.

## Main Interfaces
- Defines `struct nfs_client_initdata`, the construction input for `nfs_client` objects: address, hostname, protocol, NFS module, network namespace, timeouts, credentials, transport security, and connect/reconnect timeouts.
- Defines `struct nfs_fs_context`, the in-kernel mount context used by NFS fs_context code. It stores parsed mount options, server/mount-server addresses, auth flavor selection, transport security, clone/submount data, and resulting `nfs_server`.
- Defines `struct nfs_mount_request` for the v2/v3 MOUNT protocol client in `mount_clnt.c`.
- Declares the broad internal NFS API: client allocation/probing, server creation/cloning, procfs hooks, page cache slab setup, pgio setup, file operations, inode lifecycle, namespace automount/submount helpers, read/write/commit paths, NFSv4 client/state helpers, and direct I/O request state.
- Declares `struct nfs_direct_req`, the direct I/O completion and commit tracker with refcounting, I/O counters, completion, error/count fields, and direct-write/read flags.

## Important Inline Helpers
- Attribute and mountpoint helpers:
  - `nfs_attr_check_mountpoint()` marks fattrs as mountpoints when fsids differ.
  - `nfs_attr_use_mounted_on_fileid()` decides whether `mounted_on_fileid` should be used for mountpoint/referral cases.
  - `nfs_lookup_is_soft_revalidate()` detects positive dentries eligible for soft revalidation.
- Mount/logging helpers:
  - `nfs_fc2context()` extracts `nfs_fs_context`.
  - `nfs_errorf`, `nfs_invalf`, `nfs_warnf` variants route messages through fs_context logging when available.
- I/O and sizing helpers:
  - `flags_to_mode()` maps open flags to `FMODE_READ`, `FMODE_WRITE`, `FMODE_EXEC`.
  - `nfs_file_block_o_direct()` clears `NFS_INO_ODIRECT` and waits for DIO.
  - `nfs_block_bits()`, `nfs_block_size()`, and `nfs_io_size()` clamp and align block/read/write sizes.
  - `nfs_super_set_maxbytes()` clamps server max file size to Linux limits.
  - `nfs_folio_length()` computes valid data length for a folio relative to inode size.
  - `nfs_page_array_len()` computes page-vector length for base+len.
- Write/commit helpers:
  - `nfs_folio_mark_unstable()` accounts unstable writeback and dirties inode state.
  - `nfs_write_verifier_cmp()` / `nfs_write_match_verf()` compare commit verifiers.
  - `nfs_clear_pnfs_ds_commit_verifiers()` clears pNFS commit verifier state when v4 is enabled.
- Error helpers:
  - `nfs_error_is_fatal()` and `nfs_error_is_fatal_on_server()` classify errors for retry/recovery behavior.
  - `nfs_current_task_exiting()` wraps `PF_EXITING`.
- Misc:
  - `nfs_should_remove_suid()` implements NFS-specific suid/sgid stripping.
  - `nfs_timespec_to_change_attr()` converts timestamps to a synthetic change attribute.
  - `nfs_stateid_hash()` hashes NFSv4 stateids.
  - `nfs_set_port()` applies default/user port selection to socket addresses.
  - `nfs_igrab_and_active()` / `nfs_iput_and_deactive()` pair inode refs with superblock active refs.

## Configuration-Dependent Behavior
- `CONFIG_NFS_V4` gates v4 XDR/proc declarations and pNFS commit verifier handling.
- `CONFIG_NFS_V4_SECURITY_LABEL` gates NFSv4 label allocation/copy/cache invalidation.
- `CONFIG_NFS_LOCALIO` exposes local I/O probe/open/read-write/commit hooks; otherwise stubs return disabled behavior.
- `CONFIG_PROC_FS`, `CONFIG_NFS_FSCACHE`, and `CONFIG_MIGRATION` provide no-op or feature-specific hooks.

## Dependencies and Coupling
This header is intentionally high-coupling: it is the contract between NFS mount setup, RPC procedure modules, inode/file/page I/O code, pNFS, localio, and NFSv4 state management. Changes here affect many translation units and should be treated as ABI-like within `fs/nfs`.

## Research Notes
- The file is not an implementation module but is behaviorally important because many static inline helpers encode policy, especially I/O sizing, fatal error classification, suid stripping, localio stubs, and mountpoint detection.
- The localio declarations correspond directly to `localio.c`.
- The `io.c` declarations and `nfs_file_block_o_direct()` form the buffered-vs-direct serialization contract.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/io.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/io.c

## Purpose
Implements NFS client I/O mode serialization between buffered I/O and direct I/O using `inode->i_rwsem` plus the `NFS_INO_ODIRECT` inode flag.

## Key Functions
- `nfs_start_io_read(struct inode *inode)`
  - Starts buffered read.
  - Takes `i_rwsem` for read when no direct I/O mode is active.
  - If direct mode is active, upgrades through a write lock, calls `nfs_file_block_o_direct()`, then downgrades to read lock.
- `nfs_end_io_read(struct inode *inode)`
  - Releases read side of `i_rwsem`.
- `nfs_start_io_write(struct inode *inode)`
  - Starts buffered write.
  - Takes `i_rwsem` for write and blocks direct I/O via `nfs_file_block_o_direct()`.
  - Exported GPL.
- `nfs_end_io_write(struct inode *inode)`
  - Releases write side of `i_rwsem`.
  - Exported GPL.
- `nfs_start_io_direct(struct inode *inode)`
  - Starts direct I/O.
  - Takes shared lock if `NFS_INO_ODIRECT` already set.
  - Otherwise takes write lock, sets `NFS_INO_ODIRECT`, syncs mapping via `nfs_sync_mapping()`, and downgrades to shared lock.
- `nfs_end_io_direct(struct inode *inode)`
  - Releases read side of `i_rwsem`.

## Synchronization Model
- Buffered reads and direct I/O can each run concurrently with same-mode operations under shared `i_rwsem`.
- Mode transitions require exclusive `i_rwsem`.
- Buffered writes and truncates are serialized with both buffered reads and direct I/O by taking the write side.
- `NFS_INO_ODIRECT` marks direct-I/O mode; clearing it waits for in-flight direct I/O through `inode_dio_wait()` in the header helper.

## Research Notes
This file is small but critical to page-cache coherency. The main invariant is that switching between buffered and direct paths flushes/waits at the transition point while preventing concurrent mode flips.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/iostat.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/iostat.h

## Purpose
Defines per-mount NFS client I/O statistics storage and lightweight per-CPU accounting helpers.

## Main Types and Helpers
- `struct nfs_iostats`
  - Per-CPU structure with byte counters indexed by `__NFSIOS_BYTESMAX`.
  - Event counters indexed by `__NFSIOS_COUNTSMAX`.
  - Cacheline aligned to reduce contention.
- `nfs_inc_server_stats()` / `nfs_inc_stats()`
  - Increment per-server or inode-derived event counters using `this_cpu_inc()`.
- `nfs_add_server_stats()` / `nfs_add_stats()`
  - Add byte counts using `this_cpu_add()`.
- `nfs_alloc_iostats()`
  - Macro wrapping `alloc_percpu(struct nfs_iostats)` so allocation tagging remains distinct.
- `nfs_free_iostats()`
  - Frees non-NULL per-CPU stats.

## Dependencies
Uses public NFS iostat enum definitions from `<linux/nfs_iostat.h>` and relies on `NFS_SERVER(inode)->io_stats`.

## Research Notes
The file is intentionally header-only for hot-path accounting. It has no locking because it uses per-CPU counters.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/iostat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/localio.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/localio.c

## Purpose
Implements NFS client LOCALIO support: when the NFS server is local to the same kernel, the client can bypass the network RPC data path and perform reads, writes, and commits directly against an `nfsd_file`.

## Main Concepts
- LOCALIO detection uses a small auxiliary RPC program, `nfslocalio`, with `UUID_IS_LOCAL`.
- A client is considered local when its UUID maps to local server state and `localio_enabled` is true.
- Data I/O is still shaped like NFS pgio/commit completion: local operations fill NFS result structures and invoke the same RPC completion callbacks expected by the upper NFS client layers.

## Key Data Structures
- `struct nfs_local_kiocb`
  - Wraps a `kiocb`, bio_vec array, target `nfs_pgio_header`, work item, completion callback work hook, local `nfsd_file`, and up to three `iov_iter`s for DIO splitting.
- `struct nfs_local_fsync_ctx`
  - Tracks local commit/fsync work, the target `nfsd_file`, `nfs_commit_data`, work item, and optional synchronous completion.
- `struct nfs_local_dio` is declared in `internal.h` and filled here to describe misaligned start, aligned middle, and misaligned end extents.

## LOCALIO Probe Path
- `localio_xdr_enc_uuidargs()` / `localio_xdr_dec_uuidres()` encode/decode the UUID probe.
- `nfslocalio_program` declares the auxiliary RPC program.
- `nfs_init_localioclient()` binds the auxiliary RPC program to an existing NFS RPC client.
- `nfs_server_uuid_is_local()` sends `UUID_IS_LOCAL`, then checks that required local UUID fields were initialized.
- `nfs_local_probe()` enables or disables localio based on module parameter, AUTH_SYS requirement, UUID state, and probe result.
- `nfs_local_probe_async_work()` and `nfs_local_probe_async()` queue probing on `nfsiod_workqueue`.

## Opening Local File Handles
- `nfs_local_open_fh()` checks local status and allowed mode, selects cached read-only or read-write local file slot, and calls `__nfs_local_open_fh()`.
- `__nfs_local_open_fh()` uses `nfs_open_local_fh()` and retriggers probing on selected failures such as `-ENOMEM`, `-ENXIO`, and `-ENOENT`.
- Local file references are released through `nfs_local_file_put()`.

## Read/Write Data Path
- `nfs_local_iocb_alloc()` builds a local `kiocb`, allocates bvecs, sets `GFP_NOFS` on the backing mapping, and initializes position/flags.
- `nfs_local_iters_init()` converts the NFS page array and pgbase/count into bvec-backed iterators.
- Direct I/O support:
  - `nfs_is_local_dio_possible()` queries server-side DIO alignment and splits the request.
  - `nfs_local_iters_setup_dio()` creates up to three iterators: misaligned start, aligned middle, misaligned end.
  - The aligned middle can run with `IOCB_DIRECT`; misaligned portions fall back to buffered I/O.
- `nfs_local_do_read()` queues `nfs_local_call_read()` on `nfslocaliod_workqueue`.
- `nfs_local_call_read()` runs `read_iter()` under the file credentials and handles immediate, queued, short, and error completions.
- `nfs_local_do_write()` sets sync flags according to NFS stable-write mode, sets a local write verifier, and queues `nfs_local_call_write()`.
- `nfs_local_call_write()` runs `write_iter()` with `PF_LOCAL_THROTTLE | PF_MEMALLOC_NOIO`, handles short writes by marking the open context for synchronous writes, and ends file write accounting.
- AIO completion callbacks queue final callback processing to `nfsiod_workqueue` because completion can occur in bottom-half context.

## Completion and Result Handling
- `nfs_local_pgio_done()` accumulates byte counts, maps negative errors to NFSv4-style status values, and tracks multi-iterator completion.
- `nfs_local_read_done()` clears `res.replen` to avoid corrupt behavior if falling back to normal RPC, and sets EOF based on file size.
- `nfs_local_write_done()` resets boot verifier on errors.
- `nfs_local_vfs_getattr()` refreshes selected fattr fields from VFS after writes, including v4 change attribute handling.
- `nfs_local_pgio_release()` invokes normal RPC call-done/release callbacks and supports restart if the callback installs a new task action.

## Commit Path
- `nfs_local_commit()` allocates an fsync context, initializes task ops, and queues `nfs_local_fsync_work()`.
- `nfs_local_run_commit()` calls `vfs_fsync_range()` for the requested range.
- `nfs_local_commit_done()` sets verifier/op status on success or maps errors on failure.
- Synchronous commits use stack completion and wait for work completion.

## Configuration and Controls
- `localio_enabled` module parameter globally enables/disables localio.
- LOCALIO requires AUTH_SYS in `nfs_local_probe()`.
- Direct I/O alignment is delegated to nfsd through `nfs_to->nfsd_file_dio_alignment()`.

## Research Notes
This file is a bridge between client-side NFS page I/O semantics and local VFS file operations. The subtle parts are completion ordering, DIO splitting, verifier generation/reset, memory reclaim flags, and preserving normal RPC callback semantics even when no network RPC was used.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/localio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/mount_clnt.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/mount_clnt.c

## Purpose
Implements the in-kernel NFS MOUNT protocol client used by NFSv2/v3 mounts to obtain a root file handle and optional auth flavor list from the server's mount daemon.

## Main Entry Point
- `nfs_mount(struct nfs_mount_request *info, int timeo, int retrans)`
  - Validates `dirpath` against `MNTPATHLEN`.
  - Builds a temporary RPC client for the MOUNT program.
  - Selects v1 or v3 MOUNT procedure based on `info->version`.
  - Sends `MOUNTPROC_MNT` with soft timeout behavior.
  - Copies returned file handle into caller-provided `nfs_fh`.
  - Populates auth flavors for v3; if no flavors are returned or protocol is not v3, fakes a permissive single `RPC_AUTH_NULL` flavor.

## XDR Encoding
- `encode_mntdirpath()` encodes the export path as an opaque string.
- `mnt_xdr_enc_dirpath()` is the RPC encoder wrapper.

## XDR Decoding
- v1/v2 style:
  - `decode_status()` maps OpenGroup XNFS MOUNT status values to Linux errno.
  - `decode_fhandle()` decodes fixed-size `NFS2_FHSIZE` file handles.
  - `mnt_xdr_dec_mountres()` combines status and file handle decode.
- v3:
  - `decode_fhs_status()` maps RFC 1813 MOUNT v3 status values.
  - `decode_fhandle3()` decodes variable-size v3 file handles and rejects zero or too-large handles.
  - `decode_auth_flavors()` decodes up to `NFS_MAX_SECFLAVORS`, capped by caller capacity.
  - `mnt_xdr_dec_mountres3()` combines v3 status, file handle, and auth flavor decoding.

## RPC Program Tables
- Defines v1 procedures for `MOUNT` and `UMOUNT`.
- Defines v3 procedures for `MOUNT` and `UMOUNT`.
- Registers local static `mnt_program` with program number `NFS_MNT_PROGRAM`.

## Research Notes
The error mapping is intentionally protocol-specific and avoids trusting server-local errno values. The auth flavor list is capped because RFC 1813 does not impose a practical maximum.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/mount_clnt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/namespace.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/namespace.c

## Purpose
Implements NFS namespace behavior: path reconstruction, server-side mountpoint crossing, referrals/submounts, automount expiry, and the module parameter controlling automount timeout.

## Path Reconstruction
- `nfs_path(char **p, struct dentry *dentry, char *buffer, ssize_t buflen, unsigned flags)`
  - Reconstructs an NFS server path from a dentry chain and the root dentry's `d_fsdata`.
  - Uses `rename_lock` sequence checking plus RCU and dentry locks to retry safely during renames.
  - Supports `NFS_PATH_CANONICAL` to ensure a single slash between export root and relative path.
  - Returns `ERR_PTR(-ENAMETOOLONG)` if the buffer is too small.
- `nfs_devname()` in `internal.h` wraps this for canonical device/source naming.

## Automount and Submount
- `nfs_d_automount(struct path *path)`
  - Creates a submount fs_context from the parent mount.
  - Copies credentials and network namespace from the parent server/client.
  - Inherits selected superblock flags covered by `NFS_SB_MASK`.
  - Sets server address/version/minorversion/module from the parent client.
  - Optionally inherits block size.
  - Calls protocol-specific `submount()` operation, then creates a vfsmount.
  - Adds the mount to the NFS automount expiry list if timeout is positive.
- `nfs_submount(struct fs_context *fc, struct nfs_server *server)`
  - Re-lookups the mountpoint to obtain attributes and file handle.
  - Sets selected auth flavor from the parent server client.
  - Calls `nfs_do_submount()`.
- `nfs_do_submount(struct fs_context *fc)`
  - Clones the server using protocol-specific `clone_server()`.
  - Builds the source string with `nfs_devname()`.
  - Parses it into fs_context and calls `vfs_get_tree()`.

## Mountpoint and Referral Inode Ops
- `nfs_mountpoint_inode_operations`
  - Uses normal `nfs_getattr` and `nfs_setattr`.
- `nfs_referral_inode_operations`
  - Uses wrappers that fall back to generic attributes and reject setattr with `-EACCES` when the referral object has no file handle.

## Automount Expiry
- Global `nfs_automount_list` and delayed work `nfs_automount_task`.
- `nfs_expire_automounts()` calls `mark_mounts_for_expiry()` and reschedules while the list is non-empty.
- `nfs_release_automount_timer()` cancels delayed work when no automounts remain.
- `nfs_mountpoint_expiry_timeout` defaults to `500 * HZ`.

## Module Parameter
- `param_set_nfs_timeout()` parses seconds, converts to jiffies, reschedules expiry work, or disables expiry for non-positive values.
- `param_get_nfs_timeout()` reports seconds or `-1` when disabled.
- Exposed as `nfs_mountpoint_expiry_timeout`.

## Research Notes
This file is central to correct NFS behavior when a server export contains mountpoints or v4 referrals. It preserves identity and statistics by creating client-side mountpoints at server-side filesystem boundaries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/namespace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/netns.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/netns.h

## Purpose
Defines NFS private per-network-namespace state accessed through `net_generic()`.

## Main Types
- `struct bl_dev_msg`
  - Stores block-layout device reply status and major/minor numbers.
- `struct nfs_net`
  - DNS resolver cache pointer.
  - Block layout device pipe/reply/waitqueue/mutex.
  - Per-net NFS client and volume lists.
  - NFSv4 callback ID allocator and callback port state when v4 is enabled.
  - NFSv4 data server cache and lock when v4 is enabled.
  - Per-net `nfs_netns_client`.
  - Global NFS client lock for the namespace.
  - Namespace boot time and RPC stats.
  - Optional procfs root entry.

## Exports
- Declares `extern unsigned int nfs_net_id`, the netns generic ID used by NFS code.

## Research Notes
This header is shared by client creation, NFSv4 callback/trunking code, procfs/sysfs integration, and pNFS block/data-server paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/netns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs.h

## Purpose
Internal interface exported by the base NFS module for version-specific NFS modules.

## Main Type
- `struct nfs_subversion`
  - Holds module owner, filesystem type, RPC version table, protocol operation table, superblock operations, and xattr handlers for one NFS protocol version.

## Declared API
- `find_nfs_version(unsigned int)`
- `get_nfs_version(struct nfs_subversion *)`
- `put_nfs_version(struct nfs_subversion *)`
- `register_nfs_version(struct nfs_subversion *)`
- `unregister_nfs_version(struct nfs_subversion *)`

## Research Notes
This is the version registration contract used by `nfs2super.c`, `nfs3super.c`, and NFSv4 module code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs2super.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs2super.c

## Purpose
Registers NFSv2 support as an NFS subversion module.

## Main Behavior
- Defines static `nfs_v2`:
  - owner: `THIS_MODULE`
  - filesystem type: `nfs_fs_type`
  - RPC version: `nfs_version2`
  - RPC ops: `nfs_v2_clientops`
  - superblock ops: `nfs_sops`
- `init_nfs_v2()` registers the subversion.
- `exit_nfs_v2()` unregisters it.
- Declares module description and GPL license.

## Research Notes
No protocol logic lives here; it is a module registration shim binding the v2 XDR/proc implementation to the common NFS client.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs2super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs2xdr.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs2xdr.c

## Purpose
Implements NFSv2 XDR encoding/decoding and exports the NFSv2 RPC procedure table.

## Basic Type Handling
- Uses RFC 1094 layout sizes for handles, attributes, paths, filenames, data, and result unions.
- Translates RPC credentials to user namespace via `rpc_rqst_userns()`.
- `decode_nfsdata()` reads page-backed opaque read data and clamps cheating servers that report more data than received.
- `decode_stat()` reads NFS status and maps nonzero values later through `nfs_stat_to_errno()`.
- `xdr_decode_ftype()` maps v2 file type values and sanitizes invalid types.
- `encode_fhandle()` / `decode_fhandle()` handle fixed `NFS2_FHSIZE` file handles.
- Time helpers encode/decode v2 timeval, including the Sun convention for "set to current server time" using usec `1000000`.

## Attribute Handling
- `decode_fattr()` fills `nfs_fattr` from v2 `fattr`, including mode, nlink, uid/gid translation, size, blocksize, rdev, blocks, fsid, fileid, timestamps, and synthetic change attribute.
- Handles the v2 FIFO convention where `NFCHR` plus `NFS2_FIFO_DEV` becomes `S_IFIFO`.
- `encode_sattr()` writes `sattr`, using `NFS2_SATTR_NOT_SET` for unchanged fields.

## Argument Encoders
- File handle: `nfs2_xdr_enc_fhandle()`.
- Setattr: `nfs2_xdr_enc_sattrargs()`.
- Lookup/remove/rmdir style directory args: `nfs2_xdr_enc_diropargs()` and `nfs2_xdr_enc_removeargs()`.
- Readlink/read: prepare reply pages and mark read buffers.
- Write: encodes offset/count and writes pages to XDR buffer.
- Create/mkdir: dir args plus attributes.
- Rename, link, symlink, readdir: protocol-specific encoders.

## Result Decoders
- `nfs2_xdr_dec_stat()`, `nfs2_xdr_dec_attrstat()`, `nfs2_xdr_dec_diropres()`.
- `nfs2_xdr_dec_readlinkres()` decodes path into page-backed buffer and terminates string.
- `nfs2_xdr_dec_readres()` decodes status, fattr, and read data.
- `nfs2_xdr_dec_writeres()` treats all v2 writes as `NFS_FILE_SYNC`.
- `nfs2_xdr_dec_readdirres()` stores raw directory bytes into page cache.
- `nfs2_xdr_dec_statfsres()` decodes transfer size, block size, blocks, free, and available blocks.

## Directory Entry Decoding
- `nfs2_decode_dirent()` decodes cached readdir entries on later `getdents()` processing.
- Handles EOF markers, fileid, inline filename, 32-bit cookie, and sets `DT_UNKNOWN`.

## RPC Table
- `nfs_procedures[]` covers GETATTR, SETATTR, LOOKUP, READLINK, READ, WRITE, CREATE, REMOVE, RENAME, LINK, SYMLINK, MKDIR, RMDIR, READDIR, and STATFS.
- `nfs_version2` exports version number 2, procedure table, and per-procedure counters.

## Research Notes
The file is strictly v2 protocol translation. Notable compatibility behavior includes UID/GID namespace translation, FIFO special-case handling, v2 synchronous write semantics, and defensive handling of oversized or inconsistent server replies.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs2xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs3_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs3_fs.h

## Purpose
NFSv3-specific internal declarations.

## Contents
- ACL declarations under `CONFIG_NFS_V3_ACL`:
  - `nfs3_get_acl()`
  - `nfs3_set_acl()`
  - `nfs3_proc_setacls()`
  - `nfs3_listxattr()`
- Stub behavior when ACL support is disabled:
  - `nfs3_proc_setacls()` returns success.
  - `nfs3_listxattr` is `NULL`.
- Client/server declarations:
  - `nfs3_create_server()`
  - `nfs3_clone_server()`
- Extern declaration for `nfs_v3`.

## Research Notes
This header connects NFSv3 ACL support, v3 client creation, and v3 module registration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs3_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs3acl.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs3acl.c

## Purpose
Implements NFSv3 POSIX ACL get/set/list xattr support using the separate Sun NFSACL v3 RPC program.

## ACL Cache Race Handling
- `nfs3_prepare_get_acl()`, `nfs3_complete_get_acl()`, and `nfs3_abort_get_acl()` use POSIX ACL sentinel logic to coordinate with VFS ACL caching.
- This mirrors `fs/posix_acl.c:get_acl()` behavior to avoid races where multiple readers fill the same ACL cache.

## Getting ACLs
- `nfs3_get_acl(struct inode *inode, int type, bool rcu)`
  - Rejects RCU mode with `-ECHILD`.
  - Requires `NFS_CAP_ACLS`.
  - Revalidates inode change state first.
  - Requests access ACL only when explicitly asked; requests default ACL for directories.
  - Allocates fattr, prepares cache sentinels, sends `ACLPROC3_GETACL`, frees any XDR-allocated pages, and refreshes inode attributes.
  - Disables ACL capability on protocol unsupported errors.
  - Normalizes trivial/empty access ACLs to `NULL`.
  - Updates or forgets access/default ACL caches based on response mask.

## Setting ACLs
- `__nfs3_proc_setacls()`
  - Validates capability and maximum ACL entry counts.
  - Computes XDR ACL size and allocates pages if larger than inline buffer.
  - Sends `ACLPROC3_SETACL`.
  - Zaps access and ACL caches.
  - Refreshes inode attributes on success.
  - Disables ACL capability on unsupported errors.
- `nfs3_proc_setacls()`
  - Treats `-EOPNOTSUPP` as success for callers that can proceed without server ACL support.
- `nfs3_set_acl()`
  - Handles VFS `set_acl` for access/default ACLs.
  - For directories, fetches the complementary ACL so both access and default ACL state can be sent together.
  - If access ACL is removed, synthesizes ACL from inode mode before sending.

## Listing xattrs
- `nfs3_list_one_acl()` checks whether a given ACL exists and appends its xattr name.
- `nfs3_listxattr()` lists POSIX ACL access and default names when present, respecting buffer size and returning `-ERANGE` as needed.

## Research Notes
This file handles policy above XDR: cache coherency, capability disabling after unsupported responses, VFS ACL semantics, and the requirement to send access/default ACLs together for directories.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs3acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs3client.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs3client.c

## Purpose
Provides NFSv3-specific server/client creation helpers, NFSACL client setup, and pNFS data server client setup for NFSv3.

## ACL Client Setup
- Under `CONFIG_NFS_V3_ACL`, defines `nfsacl_program` using `nfsacl_version3`.
- `nfs_init_server_aclclient()`
  - Skips setup if `NFS_MOUNT_NOACL`.
  - Binds the NFSACL program to the main server RPC client.
  - Links the ACL RPC client into sysfs.
  - Sets `NFS_CAP_ACLS` on success, clears it on failure.
- Without ACL support, clears ACL capability and normalizes flags.

## Server Creation
- `nfs3_create_server(struct fs_context *fc)`
  - Calls common `nfs_create_server()`.
  - Initializes ACL client when server creation succeeds.
- `nfs3_clone_server(...)`
  - Calls common `nfs_clone_server()`.
  - Initializes ACL client for cloned server if source has a usable ACL client.

## pNFS Data Server Client
- `nfs3_set_ds_client(...)`
  - Builds `nfs_client_initdata` for an NFSv3 data server.
  - Uses MDS identity, net namespace, credentials, and timeout policy.
  - Computes connect/reconnect timeout from DS timeo/retrans.
  - Fakes hostname from DS address for lockd.
  - Handles TCP-TLS fallback to TCP unless MDS transport security is configured.
  - Carries `nconnect` for TCP/RDMA families when MDS has multiple connections.
  - Propagates no-reserved-port and net-unreachable-fatal flags.
  - Marks the client as a data server with `NFS_CS_DS`.
  - Calls `nfs_get_client()`.

## Research Notes
The ACL setup here pairs with `nfs3acl.c` and `nfs3xdr.c`. The pNFS data-server path is carefully conservative: soft-ish low timeout behavior is chosen so failures can fall back through the metadata server.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs3client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs3proc.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs3proc.c

## Purpose
Implements client-side NFSv3 procedure stubs and exports the `nfs_v3_clientops` operation table used by the generic NFS client.

## RPC Wrapper and Retry
- `nfs3_rpc_wrapper()` wraps synchronous RPC calls to handle `-EJUKEBOX` by sleeping for `NFS_JUKEBOX_RETRY_TIME` unless interrupted or exiting.
- The file locally redefines `rpc_call_sync` to the wrapper.
- `nfs3_async_handle_jukebox()` restarts async tasks after delay and increments `NFSIOS_DELAY`.

## Core Metadata Procedures
- `nfs3_proc_get_root()` uses FSINFO and falls back to GETATTR if needed.
- `nfs3_proc_getattr()` optionally uses timeout behavior for soft revalidation.
- `nfs3_proc_setattr()` uses file credentials when available, updates inode state, and zaps ACL cache if ACL state was invalidated.
- Lookup:
  - `__nfs3_proc_lookup()` sends LOOKUP, refreshes parent directory attrs, and falls back to GETATTR if returned object attrs are absent.
  - `nfs3_proc_lookup()` adds soft-revalidation timeout behavior.
  - `nfs3_proc_lookupp()` looks up `".."`.

## Access and Readlink
- `nfs3_proc_access()` sends ACCESS, refreshes attrs, and maps returned access mask into `nfs_access_entry`.
- `nfs3_proc_readlink()` sends READLINK into a page buffer and refreshes symlink attrs.

## Create and Directory Mutations
- `struct nfs3_createdata` packages create-family args, result file handle, object attrs, and directory attrs.
- `nfs3_proc_create()`
  - Handles POSIX ACL creation.
  - Supports exclusive create with verifier, and falls back from exclusive to guarded to unchecked on `-ENOTSUPP`.
  - Performs post-create setattr after exclusive create.
  - Applies ACLs after creation.
- `nfs3_proc_remove()`, unlink setup/prepare/done, rename setup/prepare/done update post-op directory attrs.
- `nfs3_proc_link()` updates both file and target directory attrs.
- `nfs3_proc_symlink()`, `nfs3_proc_mkdir()`, `nfs3_proc_rmdir()`, and `nfs3_proc_mknod()` implement their VFS operations with appropriate create data and ACL handling.

## Readdir and Filesystem Info
- `nfs3_proc_readdir()` supports plain READDIR and READDIRPLUS, copies cookie verifier when cookie is nonzero, invalidates directory atime, and refreshes directory attrs.
- `nfs3_proc_statfs()`, `nfs3_proc_fsinfo()`, and `nfs3_proc_pathconf()` wrap FSSTAT, FSINFO, and PATHCONF.

## Read/Write/Commit pgio Hooks
- `nfs3_read_done()`
  - Handles optional pgio callback, Jukebox retry, records `read_hdrsize`, triggers localio re-probe on successful I/O, invalidates atime, and refreshes inode attrs.
- `nfs3_proc_read_setup()` selects READ proc and cached read header size.
- `nfs3_write_done()` handles callback/Jukebox, updates inode writeback state, and triggers localio re-probe.
- `nfs3_proc_write_setup()` selects WRITE proc.
- `nfs3_commit_done()` handles callback/Jukebox and refreshes inode attrs.
- `nfs3_proc_commit_setup()` selects COMMIT proc.

## LOCALIO Re-Probing
- Under `CONFIG_NFS_LOCALIO`, module parameter `nfs3_localio_probe_throttle` controls periodic LOCALIO probe attempts after normal successful I/O.
- Intended for cases where LOCALIO was disabled after server restart and may later become possible again.

## Locking
- Integrates with lockd through `nlmclnt_operations`.
- For close unlocks, takes and releases NFS lock/open contexts and waits for async I/O counters before unlock where needed.
- `nfs3_proc_lock()` dispatches to `nlmclnt_proc()`.

## Operation Tables
- Defines NFSv3 directory and file inode operations, including ACL hooks when configured.
- `nfs_v3_clientops` wires all v3 implementations into the generic NFS client:
  - metadata ops, lookup/access/readlink/create/remove/rename/link/symlink/mkdir/rmdir/readdir/mknod
  - statfs/fsinfo/pathconf
  - pgio read/write/commit hooks
  - lock, ACL cache clearing, delegation stubs, client/server creation and cloning.

## Research Notes
This file is the main NFSv3 behavior layer above XDR. It coordinates RPC calls, inode cache updates, ACL semantics, retry behavior, writeback completion, lockd, and localio probing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs3proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs3super.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs3super.c

## Purpose
Registers NFSv3 support as an NFS subversion module.

## Main Behavior
- Defines exported `nfs_v3`:
  - owner: `THIS_MODULE`
  - filesystem type: `nfs_fs_type`
  - RPC version: `nfs_version3`
  - RPC ops: `nfs_v3_clientops`
  - superblock ops: `nfs_sops`
- `init_nfs_v3()` registers the subversion.
- `exit_nfs_v3()` unregisters it.
- Declares module description and GPL license.

## Research Notes
No protocol mechanics live here. It binds NFSv3 XDR/proc/client code into the common NFS version registry.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs3super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs3xdr.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs3xdr.c

## Purpose
Implements NFSv3 XDR encoding/decoding, NFSv3 directory-entry decoding from cached readdir pages, optional NFSACL v3 XDR, and exports the NFSv3 RPC version/procedure tables.

## Sizing and Primitive Types
- Defines request/reply XDR word-size constants for NFSv3 operations and ACL operations.
- Maps NFSv3 file types to Linux `S_IFMT` bits using `nfs_type2fmt`.
- Provides user namespace helpers for UID/GID translation.
- Encodes/decodes primitives:
  - uint32/uint64
  - fileid3, filename3, nfspath3
  - cookie3 and cookie verifier
  - create/write verifiers
  - size3
  - nfsstat3
  - ftype3
  - specdata3
  - variable-length `nfs_fh3`
  - nfstime3

## Attribute and WCC Handling
- `encode_sattr3()` encodes optional mode/uid/gid/size/atime/mtime fields using NFSv3 discriminated unions.
- `decode_fattr3()` fills `nfs_fattr`, including mode/type, link count, namespace-translated uid/gid, size, used blocks, rdev, fsid, fileid, timestamps, change attribute, and valid flags.
- `decode_post_op_attr()` handles optional post-op attrs.
- `decode_wcc_attr()`, `decode_pre_op_attr()`, and `decode_wcc_data()` decode weak cache consistency data.
- `decode_post_op_fh3()` handles optional returned file handles and zeroes the handle when absent.

## Argument Encoders
- GETATTR, SETATTR with optional ctime guard, LOOKUP, ACCESS.
- READLINK and READ prepare page-backed reply buffers.
- WRITE writes page data and marks XDR buffer as write data.
- CREATE encodes unchecked, guarded, or exclusive create forms.
- MKDIR, SYMLINK, MKNOD, REMOVE, RENAME, LINK.
- READDIR and READDIRPLUS encode cookies/verifiers and prepare page-backed directory replies.
- COMMIT encodes file handle, offset, and count.
- Optional ACL encoders:
  - GETACL prepares sparse reply pages when ACL data is requested.
  - SETACL writes ACL payload inline or through pages and uses `nfsacl_encode()`.

## Result Decoders
- GETATTR, SETATTR, LOOKUP, ACCESS, READLINK.
- READ:
  - `decode_read3resok()` validates count against opaque length, reads pages, handles cheating server counts, and sets EOF/count.
  - `nfs3_xdr_dec_read3res()` records op status and reply header length.
- WRITE:
  - Decodes WCC data, count, stable commit level, and write verifier.
  - Rejects invalid `stable_how`.
- CREATE:
  - Decodes optional returned file handle and attrs.
  - If server omits file handle, invalidates fattr to force a later LOOKUP.
- REMOVE, RENAME, LINK decode relevant WCC/post-op attrs.
- READDIR:
  - Stores raw directory bytes in page cache for later decoding.
  - Decodes directory attrs and cookie verifier.
- FSSTAT, FSINFO, PATHCONF, COMMIT:
  - Fill stat, server I/O limits, name/link limits, max file size, time delta, and commit verifier information.
- Optional ACL decoders:
  - GETACL decodes fattr, mask, access ACL, and default ACL.
  - SETACL decodes post-op attrs on success.

## Cached Directory Entry Decoding
- `nfs3_decode_dirent()`
  - Decodes raw cached READDIR/READDIRPLUS entries during `getdents()` processing.
  - Handles EOF marker via `-EBADCOOKIE`.
  - Decodes fileid, filename, cookie.
  - For READDIRPLUS, decodes post-op attrs and optional file handle.
  - Sets `d_type` from decoded mode when attrs are available.
  - Handles mounted-on-fileid when fattr fileid differs from entry fileid.

## RPC Tables
- `nfs3_procedures[]` covers GETATTR, SETATTR, LOOKUP, ACCESS, READLINK, READ, WRITE, CREATE, MKDIR, SYMLINK, MKNOD, REMOVE, RMDIR, RENAME, LINK, READDIR, READDIRPLUS, FSSTAT, FSINFO, PATHCONF, and COMMIT.
- `nfs_version3` exports NFS protocol version 3 and counters.
- Under `CONFIG_NFS_V3_ACL`, `nfs3_acl_procedures[]` and `nfsacl_version3` export GETACL/SETACL.

## Research Notes
This file is the authoritative NFSv3 wire-format implementation. Key correctness points are variable file-handle bounds, UID/GID namespace validation, weak cache consistency preservation, page-backed read/readdir data handling, verifier validation, and ACL page/inline encoding.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs3xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs40.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs40.h

## Purpose
Small NFSv4.0-specific internal declaration header.

## Contents
- Client lifecycle and callback recovery:
  - `nfs40_shutdown_client()`
  - `nfs40_init_client()`
  - `nfs40_handle_cb_pathdown()`
- Minor-version ops:
  - `extern const struct nfs4_minor_version_ops nfs_v4_0_minor_ops`
- Server trunking discovery:
  - `nfs40_discover_server_trunking()`

## Research Notes
The implementations are in `nfs40client.c` and `nfs40proc.c`. This header separates v4.0-specific hooks from generic v4 code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs40.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs40client.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs40client.c

## Purpose
Implements NFSv4.0 client initialization, shutdown, callback-path recovery, and v4.0 server trunking discovery.

## Client Slot Table
- `nfs40_init_client(struct nfs_client *clp)`
  - Allocates a v4.0 slot table.
  - Initializes it with `NFS4_MAX_SLOT_TABLE`.
  - Stores it in `clp->cl_slot_tbl`.
- `nfs40_shutdown_client(struct nfs_client *clp)`
  - Shuts down and frees the slot table if present.

## Callback Path Recovery
- `nfs40_handle_cb_pathdown(struct nfs_client *clp)`
  - Sets `NFS4CLNT_LEASE_EXPIRED`.
  - Expires all delegations to force callback path recovery.
- `nfs4_schedule_path_down_recovery(struct nfs_client *clp)`
  - Invokes v4.0 callback pathdown handling and schedules the state manager.

## Callback Ident Swapping
- `nfs4_swap_callback_idents(struct nfs_client *keep, struct nfs_client *drop)`
  - Used when trunking discovery proves two clients are the same server after SETCLIENTID changed callback identity.
  - Swaps IDR entries and `cl_cb_ident` values under the namespace NFS client lock.

## Server Trunking Discovery
- `nfs4_same_verifier()` compares v4 verifiers.
- `nfs40_walk_client_list()`
  - Walks the per-net client list looking for an existing client matching the new one.
  - Uses `nfs4_match_client()` and `SETCLIENTID_CONFIRM` to prove sameness.
  - Handles stale clientid, restart/timeout callback path recovery, and callback ident swap.
  - Returns a referenced matching client through `result` on success.
- `nfs40_discover_server_trunking()`
  - Sends `SETCLIENTID` with callback port for IPv4 or IPv6.
  - Stores returned clientid/confirm verifier.
  - Calls `nfs40_walk_client_list()`.
  - On success, schedules state renewal for the matched client and state manager if needed.

## Research Notes
This is v4.0-specific because NFSv4.0 trunking and callback setup use SETCLIENTID/SETCLIENTID_CONFIRM rather than the v4.1+ session model.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs40client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs40proc.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs40proc.c

## Purpose
Defines NFSv4.0 minor-version procedure behavior: sequence slot handling, renewals, migration recovery, lock-owner release, state recovery operations, and the exported `nfs_v4_0_minor_ops`.

## Sequence Handling
- `nfs40_call_sync_prepare()` sets up v4 sequence state before sync calls.
- `nfs40_call_sync_done()` completes sequence processing.
- `nfs40_sequence_free_slot()` returns or reassigns a slot in the v4.0 slot table.
- `nfs40_sequence_done()` frees sequence slot when present.

## State and Delegation Recovery
- `nfs40_clear_delegation_stateid()` clears delegation stateid when a delegation exists.
- `nfs40_open_expired()` clears delegation/open state flags and calls generic expired-open recovery. NFSv4.0 does not allow delegation recovery on open expiration.
- `nfs40_test_and_free_expired_stateid()` returns `-NFS4ERR_BAD_STATEID`, reflecting lack of v4.1-style TEST_STATEID/FREE_STATEID support.

## Lease Renewal
- `struct nfs4_renewdata` tracks client and timestamp.
- `nfs4_proc_async_renew()`
  - Queues asynchronous RENEW when renewal flags are nonzero.
  - Takes a client ref and records timestamp.
- `nfs4_renew_done()`
  - Handles success, `LEASE_MOVED`, callback path down, and general lease recovery scheduling.
  - Calls `do_renew_lease()` on successful/handled renew.
- `nfs4_proc_renew()`
  - Synchronous RENEW and lease timestamp update.

## Migration and Lease-Moved Recovery
- `_nfs40_proc_get_locations()`
  - Sends FS_LOCATIONS with appended RENEW to signal migration recovery.
  - Fills `nfs4_fs_locations`.
  - Renews server lease on success.
- `_nfs40_proc_fsid_present()`
  - Sends FSID_PRESENT with appended RENEW to signal lease-moved recovery.
  - Allocates temporary file handle result storage.
  - Updates lease on success.

## Lock Owner Release
- `struct nfs_release_lockowner_data` stores lock state, server, args/res, and timestamp.
- `nfs4_release_lockowner_prepare()` sets up sequence and lock owner clientid.
- `nfs4_release_lockowner_done()` renews lease on success or schedules recovery/retry for stale clientid, expired lease, lease moved, or delay.
- `nfs4_release_lockowner_release()` frees lock state and calldata.
- `nfs4_release_lockowner()` queues asynchronous RELEASE_LOCKOWNER for minor version 0 only.

## Exported Minor Version Ops
- `nfs_v4_0_minor_ops`
  - minor version: 0
  - initial capabilities: READDIRPLUS, ATOMIC_OPEN, POSIX_LOCK
  - client init/shutdown: `nfs40_init_client()`, `nfs40_shutdown_client()`
  - stateid match/root sec/lock state/free expired hooks
  - seqid allocator and sync/sequence slot ops
  - reboot and no-grace recovery ops
  - lease renewal ops
  - migration recovery ops

## Research Notes
This file adapts generic NFSv4 state machinery to v4.0 constraints: no sessions, v4.0 slot table behavior, RENEW-based lease maintenance, SETCLIENTID-era recovery, and RELEASE_LOCKOWNER support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs40proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs42.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs42.h

## Purpose
NFSv4.2-specific internal declarations and small helpers.

## Constants
- `PNFS_LAYOUTSTATS_MAXDEV` is set to 4, limiting layoutstats devices per compound.
- `READ_PLUS_SCRATCH_SIZE` is set to 16.

## Declared NFSv4.2 Procedures
Under `CONFIG_NFS_V4_2`:
- Space management:
  - `nfs42_proc_allocate()`
  - `nfs42_proc_deallocate()`
  - `nfs42_proc_zero_range()`
- Copy/clone/seek:
  - `nfs42_proc_copy()`
  - `nfs42_proc_clone()`
  - `nfs42_proc_llseek()`
  - `nfs42_proc_copy_notify()`
- pNFS reporting:
  - `nfs42_proc_layoutstats_generic()`
  - `nfs42_proc_layouterror()`
- Extended attributes:
  - `nfs42_proc_getxattr()`
  - `nfs42_proc_setxattr()`
  - `nfs42_proc_listxattrs()`
  - `nfs42_proc_removexattr()`

## Inline Helpers
- `nfs42_files_from_same_server(struct file *in, struct file *out)`
  - Compares major server owner IDs of input/output NFS clients.
  - Used to decide whether server-side operations can treat two files as same-server.
- `nfs42_listxattr_xdrsize(u32 buflen)`
  - Computes an upper-bound XDR buffer size for listxattr output.
  - Assumes worst case of many small `user.x` names and rounds to 4-byte alignment.

## Research Notes
This header exposes v4.2 feature entry points but does not implement them. The listxattr sizing helper encodes an important wire-buffer bound used by v4.2 xattr code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs42.h -->