# Group Research: group_474_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_7867937ab22f

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/namefs/namevno.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/namefs/namevno.c

Implements NAMEFS vnode operations for mounted file descriptors. NAMEFS is mostly a forwarding layer from the mounted namenode vnode to the underlying file descriptor vnode, with special handling for open-time vnode switching and for attributes/permissions stored on the namenode itself.

Key elements:
- `nm_open()` holds the underlying `nm_filevp`, calls `VOP_OPEN()`, and handles filesystems that switch the opened vnode. If the underlying vnode changes, it finds or creates a new `namenode` keyed by `(outfilevp, mountpt)`, initializes a NAMEFS vnode for it, inserts it in the namenode hash, and returns that vnode.
- `nm_close()` clears process locks/shares on the NAMEFS vnode, forwards `VOP_CLOSE()` to `nm_filevp`, fsyncs on the last close, removes transient `NMNMNT` entries from the namefs hash, and releases the underlying file vnode hold.
- Simple pass-through operations: `nm_read()`, `nm_write()`, `nm_ioctl()`, `nm_fsync()`, `nm_fid()`, `nm_rwlock()`, `nm_rwunlock()`, `nm_seek()`, `nm_realvp()`, and `nm_poll()`.
- `nm_getattr()` returns stored namenode attributes, but refreshes `AT_SIZE` from the underlying vnode.
- `nm_setattr()` updates only mutable stored namenode attributes, rejects `AT_NOSET` and `AT_SIZE`, uses `secpolicy_vnode_setattr()`, strips sticky bit on mode set, updates uid/gid/time fields, and serializes via the underlying vnode write lock plus `nm_lock`.
- `nm_access()` first checks permissions against NAMEFS-stored mode/uid/gid through `nm_access_unlocked()`, then checks the underlying vnode with `VOP_ACCESS()`.
- `nm_create()` supports the empty-name open/create case on a mounted file descriptor mount point; non-exclusive create returns the mount vnode if access passes, exclusive create returns `EEXIST`.
- `nm_link()` rejects links to mounted file descriptors with `EXDEV`.
- `nm_inactive()` releases the vnode reference, closes the stored file pointer for non-`NMNMNT` nodes, invalidates/frees the vnode, drops non-namefs VFS references, frees allocated node ids, and frees the namenode.
- `nm_vnodeops_template` registers NAMEFS VOPs and explicitly errors unsupported dispose.

Dependencies:
- NAMEFS internals from `sys/fs/namenode.h`: `VTONM`, `NMTOV`, `namefind`, `nameinsert`, `nameremove`, `namenodeno_alloc/free`, `ntable_lock`, `namevfs`.
- illumos vnode/VFS APIs: `VOP_OPEN`, `VOP_CLOSE`, `VOP_GETATTR`, `VOP_SETATTR`, `VOP_ACCESS`, `VOP_FSYNC`, `VOP_REALVP`, vnode holds/releases, `vn_alloc`, `vn_setops`, `vn_exists`, `vn_invalid`, `vn_free`.
- File/lock/security helpers: `cleanlocks`, `cleanshares`, `closef`, `secpolicy_vnode_access2`, `secpolicy_vnode_setattr`, `groupmember`.

Research notes:
- The main correctness path is `nm_open()` vnode substitution. It preserves NAMEFS identity by replacing the caller’s vnode with an existing or newly-created namenode for the switched underlying vnode.
- Attributes intentionally split between NAMEFS metadata and underlying vnode size; mode/owner/time changes affect the mounted descriptor node, not the target file object itself.
- `nm_inactive()` depends on `NMNMNT` to distinguish nodes that hold only a vnode reference from nodes whose `nm_filep` must be closed.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/namefs/namevno.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nbmlock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nbmlock.c

Provides common top-level helpers for non-blocking mandatory locking, NBMAND share/lock conflict checks, and System V mandatory lock detection.

Key elements:
- `nbl_start_crit()` and `nbl_end_crit()` enter/leave `vp->v_nbllock`, coordinating I/O paths with lock/share state changes.
- `nbl_in_crit()` reports whether the vnode NBMAND lock is held; comments restrict it to assertion-style use.
- `nbl_need_check()` currently checks whether the vnode’s VFS has `VFS_NBMAND` enabled.
- `nbl_conflict()` is the top-level conflict checker. It requires callers to already be in the NBMAND critical region, checks share reservation conflicts first via `nbl_share_conflict()`, skips byte-range lock checks for remove/rename, and otherwise calls `nbl_lock_conflict()`.
- `nbl_svmand()` detects System V mandatory locking mode bits by fetching `AT_MODE`; when the filesystem supports ACE mask-on-access, it passes `ATTR_NOACLCHECK` to avoid redundant ACL/kidmap work in read/write paths.

Dependencies:
- Vnode state: `vnode_t::v_nbllock`, `v_vfsp`, `vfs_flag`.
- NBMAND lower-level helpers declared in `sys/nbmlock.h`: `nbl_share_conflict()` and `nbl_lock_conflict()`.
- VFS and vnode APIs: `VFS_NBMAND`, `vfs_has_feature()`, `VFSFT_ACEMASKONACCESS`, `VOP_GETATTR()`, `MANDLOCK()`.

Research notes:
- The file is intentionally small and policy-oriented: it centralizes when to ask lower-level lock/share logic rather than implementing byte-range conflict scanning itself.
- `svmand` in `nbl_conflict()` broadens record-lock checking for System V mandatory locking so I/O can fail instead of blocking behind a lock-release path and risking deadlock.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nbmlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/bootparam_xdr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/bootparam_xdr.c

Implements XDR routines for the bootparam RPC protocol structures used by NFS/network boot paths.

Key elements:
- `xdr_bp_machine_name_t()`, `xdr_bp_path_t()`, and `xdr_bp_fileid_t()` encode/decode bounded bootparam strings using `xdr_string()` with protocol maximums.
- `xdr_ip_addr_t()` encodes/decodes the four byte-style IPv4 address fields: `net`, `host`, `lh`, and `impno`.
- `choices[]` maps `IP_ADDR_TYPE` to `xdr_ip_addr_t()` for the bootparam address union.
- `xdr_bp_address()` encodes/decodes the discriminated `bp_address` union.
- `xdr_bp_whoami_arg()` handles a client address request.
- `xdr_bp_whoami_res()` handles returned client name, domain name, and router address.
- `xdr_bp_getfile_arg()` handles a client name plus file id request.
- `xdr_bp_getfile_res()` handles returned server name, server address, and server path.

Dependencies:
- RPC/XDR APIs from `rpc/rpc.h`: `XDR`, `xdr_string`, `xdr_char`, `xdr_union`, `xdr_discrim`.
- Bootparam protocol types and constants from `rpc/bootparam.h`.

Research notes:
- The routines are direct generated-style XDR serializers with simple short-circuit failure handling.
- `xdr_bp_address()` has only one concrete discriminant, `IP_ADDR_TYPE`; unknown/default union arms use a NULL default handler.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/bootparam_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_srv.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_srv.c

Implements the illumos in-kernel NFSv3 server procedure handlers, reply cleanup hooks, filehandle extraction hooks, NFSv3 attribute conversion helpers, RDMA read setup, and per-zone server verifier lifecycle.

Key elements:
- Server state: per-zone `nfs3_srv_t` stores the NFSv3 write verifier returned by WRITE/COMMIT. `rfs3_srv_zone_init()` derives it from hostid plus current time, falling back to high-resolution time when hostid is zero.
- Common operation pattern: convert NFSv3 filehandles with `nfs3_fhtovp()`, run DTrace start/done probes, apply export read-only checks with `rdonly()`, apply Trusted Extensions label checks when enabled, use VOP/VFS operations, map errors with `puterrno3()`, convert `T_WOULDBLOCK`/delegation conflicts to `NFS3ERR_JUKEBOX`, and fill post-op or WCC attributes.
- Metadata procedures:
  - `rfs3_getattr()` gets delegated-aware attributes via `rfs4_delegated_getattr()` and reports NFS referral reparse points as symlinks.
  - `rfs3_setattr()` converts `sattr3` to `vattr`, validates guarded ctime, handles size changes with NBMAND conflict checks and `VOP_SPACE()` for owner truncation, applies `VOP_SETATTR()`, fsyncs metadata, and returns WCC data.
  - `rfs3_access()` maps NFSv3 access bits to VOP access checks, accounts for read-only exports, mandatory locks, and label dominance/equality.
- Lookup/readlink:
  - `rfs3_lookup()` supports normal lookup, public filehandle multi-component WebNFS lookup, `..` handling at export roots, nohide climbing, mounted-on traversal, inbound name conversion, security flavor hints, and weak-auth WebNFS status.
  - `rfs3_readlink()` reads symlinks or synthesizes legacy symlink targets for NFS referral reparse points via `build_symlink()`, then performs outbound name conversion.
- I/O:
  - `rfs3_read()` supports RDMA write chunks, STREAMS mblk replies, and TCP loaned zero-copy buffers. It clamps count to transport size, handles EOF and zero-length fast paths, checks NBMAND/read access/mandatory lock state, and prepares RDMA read reply metadata.
  - `rfs3_write()` accepts data from mblks, RDMA read chunks, or inline buffers, enforces count/data length consistency, read-only/type/access/mandatory-lock checks, clamps by file-size limit, chooses stable write flags, temporarily switches `curthread->t_cred` for quota faults, writes through `VOP_WRITE()`, returns WCC and write verifier.
  - `rfs3_commit()` validates regular writable file access and calls `VOP_FSYNC(FSYNC)`, returning WCC plus the write verifier.
- Namespace creation:
  - `rfs3_create()` implements UNCHECKED, GUARDED, and EXCLUSIVE creates. It handles exclusive verifier-as-mtime, required mode validation, nosuid masking, duplicate exclusive create detection, v4 delegation recall conflicts, NBMAND truncation conflicts, fallback size repair, filehandle creation, and fsync of object and parent.
  - `rfs3_mkdir()`, `rfs3_symlink()`, and `rfs3_mknod()` convert attributes/names, enforce labels/read-only/mode requirements, call the relevant VOP, create optional filehandles, collect attributes, and fsync changed metadata.
  - `rfs3_mknod()` maps NFSv3 device/socket/FIFO types to illumos vnode types and requires `secpolicy_sys_devices()` for block/char device creation.
- Namespace mutation:
  - `rfs3_remove()` looks up the target, checks v4 delegation and NBMAND share conflicts, calls `VOP_REMOVE()`, fsyncs the directory, and returns WCC.
  - `rfs3_rmdir()` calls `VOP_RMDIR()` with zone root context and maps `EEXIST` to `ENOTEMPTY` for NFS wire semantics.
  - `rfs3_rename()` verifies source and target exports match, converts names, checks label/read-only constraints, recalls delegations on source/target, checks NBMAND conflicts, calls `VOP_RENAME()`, updates vnode path cache with `vn_renamepath()`, fsyncs both directories, and returns dual WCC.
  - `rfs3_link()` verifies same export, checks label/read-only/name constraints, calls `VOP_LINK()`, fsyncs file and directory, and returns file attrs plus link-directory WCC.
- Directory procedures:
  - `rfs3_readdir()` reads raw `dirent64` entries, enforces response minimum sizing, converts directory entry names via `nfscmd_convdirent()`, and returns an allocated entry buffer freed by `rfs3_readdir_free()`.
  - `rfs3_readdirplus()` reads directory entries, estimates XDR response size including per-entry attrs/filehandles, looks up each returned child, fills post-op attrs and filehandles unless mounted-on, treats referral reparse points as symlinks, converts names via `nfscmd_convdirplus()`, and frees buffers through `rfs3_readdirplus_free()`.
- Filesystem info:
  - `rfs3_fsstat()` maps `VFS_STATVFS()` data to NFSv3 byte/file counters and preserves unknown `-1` block counts.
  - `rfs3_fsinfo()` reports transport transfer sizes, default multiples, directory preference, max file size from `_PC_FILESIZEBITS`, timestamp granularity, and supported properties.
  - `rfs3_pathconf()` reports link/name/chown/truncation pathconf fields and fixed case-sensitive/case-preserving behavior.
- Conversion helpers:
  - `sattr3_to_vattr()` converts optional mode/uid/gid/size/atime/mtime fields, including server-time handling and time overflow checks.
  - `vattr_to_fattr3()`, `vattr_to_wcc_attr()`, `vattr_to_pre_op_attr()`, `vattr_to_post_op_attr()`, and `vattr_to_wcc_data()` convert vnode attributes into NFSv3 fattr/post-op/WCC forms with overflow suppression.
  - `rdma_setup_read_data3()` sizes RDMA read chunks and attaches write chunk metadata to READ replies.
- Per-procedure `*_getfh()` helpers return the request filehandle pointer for dispatch/cache logic. READLINK, READDIR, and READDIRPLUS have explicit result free hooks for allocated response buffers.

Dependencies:
- illumos vnode/VFS APIs: `VOP_GETATTR`, `VOP_SETATTR`, `VOP_SPACE`, `VOP_LOOKUP`, `VOP_CREATE`, `VOP_MKDIR`, `VOP_SYMLINK`, `VOP_REMOVE`, `VOP_RMDIR`, `VOP_RENAME`, `VOP_LINK`, `VOP_READ`, `VOP_WRITE`, `VOP_READDIR`, `VOP_READLINK`, `VOP_FSYNC`, `VOP_ACCESS`, `VOP_RWLOCK`, `VOP_RWUNLOCK`, `VOP_PATHCONF`, `VFS_STATVFS`.
- NFS export/security helpers: `nfs3_fhtovp`, `makefh3`, `makefh3_ol`, `checkexport`, `chk_clnt_sec`, `rdonly`, `rfs_cross_mnt`, `rfs_climb_crossmnt`, `rfs_publicfh_mclookup`, `nfscmd_convname`, `nfscmd_convdirent`, `nfscmd_convdirplus`.
- NFSv4 cross-version support: `rfs4_delegated_getattr()`, `rfs4_check_delegated()`, `vn_is_nfs_reparse()`, `build_symlink()`, and delegation policy checks.
- NBMAND support: `nbl_need_check()`, `nbl_start_crit()`, `nbl_conflict()`, `nbl_end_crit()`.
- RPC/RDMA/STREAMS support: `svc_getrpccaller()`, `rfs3_tsize()`, `rdma_get_wchunk()`, `rdma_setup_read_chunks()`, `rfs_read_alloc()`, `mblk_to_iov()`, `uio_to_mblk()`, `rfs_setup_xuio()`, `VOP_REQZCBUF()`.
- Trusted Extensions label APIs: request labels, `do_rfs_label_check()`, admin-low handling, trusted host lookup for public WebNFS.
- Kernel memory and diagnostics: `kmem_alloc/free`, DTrace probes, kstats referral counter, zone globals.

Research notes:
- NFSv3 server behavior is intentionally coupled to NFSv4 delegation state: v3 writes, truncates, removes, renames, and creates can return JUKEBOX while v4 delegations are recalled.
- Weak cache consistency is pervasive; operations collect before/after attributes where possible, but many paths deliberately return absent attributes if conversion or post-op getattr fails.
- Read and readdir reply ownership is split between XDR response structures and free callbacks; modifying these paths requires preserving exact allocation/free sizes.
- `rfs3_readdirplus()` sets `nvap->va_type = VLNK` for referral entries after `rfs4_delegated_getattr()`; this assumes `nvap` is non-NULL when referral detection succeeds.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_vfsops.c

Implements NFSv3 client-side VFS operations: filesystem registration, mount argument import, mount setup, root vnode creation, unmount, statvfs, sync, vget, root mounting, and mount-info teardown.

Key elements:
- Static call metadata:
  - `rfsnames_v3[]` names NFSv3 procedures for stats.
  - `call_type_v3[]`, `timer_type_v3[]`, and `ss_call_type_v3[]` classify procedure timeout/retry behavior.
- `nfs3init()` registers NFSv3 VFS ops and vnode ops, stores `nfs3fstyp`, and reports template registration failures.
- `nfs3fini()` is empty; VFS-level init/fini is handled separately by `nfs3_vfsinit()` and `nfs3_vfsfini()`.
- `nfs3_free_args()` releases copied-in mount arguments: filehandle, `knetconfig`, hostname, server address, sync address, netname, and security data.
- `nfs3_copyin()` imports user `nfs_args` in native or 32-bit data models, copies transport strings, netbufs, root filehandle, hostname, legacy secure mount data, new `sec_data`, and failover linked-list pointer for `NFS_ARGS_EXTB`.
- `nfs3_mount()`:
  - Enforces mount privilege and directory mount point.
  - Supports remount validation, rejecting locking-mode changes.
  - Checks mountpoint busy state unless overlay is requested.
  - Builds a `servinfo` list, including failover servers.
  - Validates `NFSMNT_KNCONF`, transport strings, server address, and NFSv3 filehandle length.
  - Handles RDMA mount selection through `rdma_reachable()`, including `NFSMNT_TRYRDMA` fallback and `NFSMNT_DORDMA` server rejection.
  - Loads new or legacy security data, defaulting to AUTH_UNIX, and temporarily enables `AUTH_F_TRYNONE` for secure mount probing.
  - Restricts failover to read-only hard mounts, determines the target zone, applies labeled-system mount policy, rejects mounts into shutting-down zones, calls `nfs3rootvp()`, and applies mount options with `nfs_setopts()`.
  - Cleans up root vnode, server list, async/kstats, and mount info on errors.
- Tunables: `nfs3_dynamic`, `nfs3_max_threads`, `nfs3_bsize`, `nfs3_async_clusters`, and `nfs3_cots_timeo`.
- `nfs3rootvp()`:
  - Allocates and initializes `mntinfo_t`, default flags, timers, stats pointers, ACL procedure metadata, failover CV, server list, attribute cache timings, rnode list, async state, and zone reference.
  - Assigns a unique NFS device id and VFS fsid.
  - Normalizes `nfs3_bsize` to a page multiple.
  - Creates the root rnode with `makenfs3node()`.
  - Calls `FSINFO` on every server to validate root type and choose the minimum supported transfer/read/write sizes and max file size across failover replicas.
  - Starts the async manager thread, initializes mount kstats, fills root type if needed, and returns the root vnode.
- `nfs3_unmount()`:
  - Requires unmount privilege.
  - Forced unmount marks `VFS_UNMOUNTED`, disables async scheduling, stops the async manager, destroys rnodes, deletes kstats, and returns.
  - Normal unmount stops async workers with signal handling, flushes rnodes, checks for active rnodes, restores async limit on busy failure, then stops manager, destroys rnodes, and deletes kstats.
- `nfs3_root()` returns a fresh root vnode for the current server, rejects cross-zone access, handles stale-root signaling through `SV_ROOT_STALE`, and restores known root vnode type.
- `nfs3_statvfs()` obtains root vnode, sends `FSSTAT`, updates root attrs, maps NFSv3 byte/file stats into `statvfs64`, handles unknown `-1` block fields, and purges stale handles on failures.
- `nfs3_sync()` flushes dirty NFS files through `rflush()` unless called for attribute-only sync, serialized by `nfs3_syncbusy`.
- `nfs3_vget()` reconstructs a vnode from an NFSv3 filehandle fid, rejects oversized fids and wrong zones, fetches attributes for unknown type, and maps stale rnodes to `ENOENT`.
- `nfs3_mountroot()` handles NFSv3 root filesystem boot mounting. It calls `mount_root()`, builds `servinfo`, forces AUTH_UNIX, calls `nfs3rootvp()`, applies options, adds the VFS, and updates `rootfs.bo_name`.
- `nfs3_vfsinit()` initializes the sync mutex; `nfs3_vfsfini()` destroys it.
- `nfs3_freevfs()` releases server info and `mntinfo_t` after unmount, asserting kstats were already deleted.

Dependencies:
- illumos VFS/vnode registration and lifecycle: `vfs_setfsops`, `vn_make_ops`, `vfs_make_fsid`, `vfs_add`, `vfs_lock_wait`, `VFS_HOLD`, `VFS_RELE`, `vfs_devismounted`.
- NFS client internals: `mntinfo_t`, `servinfo_t`, `makenfs3node`, `rfs3call`, `nfs3_tsize`, `nfs3getattr`, `nfs_setopts`, `nfs_async_*`, `rflush`, `check_rtable`, `destroy_rtable`, `nfs_free_mi`, `nfs_mnt_kstat_init`.
- Security and zones: `secpolicy_fs_mount`, `secpolicy_fs_unmount`, `sec_clnt_loadinfo`, `sec_clnt_freeinfo`, `nfs_mount_label_policy`, `zone_find_by_path`, `zone_hold/rele`, `zone_hold_ref`, `nfs_mi_zonelist_add`.
- RDMA and transport support: `rdma_reachable`, `knetconfig`, `netbuf`, transport semantics/timeouts.
- Boot/root support: `mount_root`, `getfsname`, `rootfs`, `clkset`.

Research notes:
- Failover mounts use a server list and select conservative transfer sizes by taking minimum server-advertised limits.
- Mount setup is sensitive to ownership transfer from `nfs_args` into `servinfo`; `nfs3_free_args()` intentionally nulls fields after transfer.
- There is a suspicious legacy AUTH_DES setup line copying `knc_proto` into `pf` instead of `p`; this report records the observed code and does not change it.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_vfsops.c -->