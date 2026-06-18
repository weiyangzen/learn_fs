# Group Research: group_394_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_msdosfs_msdosfs_vfsops_548900f60f74

Scope: `Docs/research_subset_a.md`. This grouped report covers FreeBSD source files under `sources/os/bsd/freebsd-src`, spanning the msdosfs mount/vnode implementation and the common NFS header, ACL, RPC, and FreeBSD port layers.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_vfsops.c

## Purpose

`msdosfs_vfsops.c` implements the FreeBSD VFS operations for FAT/MS-DOS filesystems: mount argument translation, mount/update/remount handling, boot-sector and BPB parsing, FAT geometry initialization, root vnode lookup, statfs, sync, NFS file-handle conversion, unmount cleanup, and emergency read-only remount after detected metadata corruption.

## Main Entry Points

- `msdosfs_cmount()` converts legacy `struct msdosfs_args` from userland into named mount arguments such as `from`, `uid`, `gid`, masks, charset names, long/short-name options, and iconv options before calling `kernel_mount()`.
- `msdosfs_mount()` validates mount options, handles MNT_UPDATE read-only/read-write transitions, resolves and checks the device vnode, calls `mountmsdosfs()` for new mounts, and applies per-mount user-visible options through `update_mp()`.
- `mountmsdosfs()` opens the GEOM provider, reads the boot sector, validates BPB fields, computes FAT12/16/32 geometry, initializes the in-use cluster bitmap, marks writable volumes dirty, counts fixed-root free directory entries, and installs mount data.
- `msdosfs_unmount()` suspends writes for writable mounts, flushes vnodes, marks the volume clean, closes iconv handles, closes the GEOM provider, releases device references, destroys the FAT lock, and frees mount state.
- `msdosfs_root()`, `msdosfs_statfs()`, `msdosfs_sync()`, and `msdosfs_fhtovp()` provide the VFS root/stat/sync/export hooks used by the kernel.
- `msdosfs_integrity_error()` and `msdosfs_remount_ro()` implement asynchronous forced read-only remount after corruption-sensitive failures.

## Data And State

The file allocates `M_MSDOSFSMNT` for `struct msdosfsmount` and `M_MSDOSFSFAT` for the FAT allocation bitmap. `mountmsdosfs()` fills all key `msdosfsmount` fields: device vnode/provider references, BPB values, FAT size and block layout, root directory block/size, first data cluster, max cluster, sector/cluster shift values, FAT masks/multipliers, FSInfo location, next-free cluster hint, free-cluster bitmap, root directory free-entry count, flags, and the FAT lock/taskqueue context.

The VFS operation vector registered by `VFS_SET(msdosfs_vfsops, msdosfs, 0)` exposes `.vfs_fhtovp`, `.vfs_mount`, `.vfs_cmount`, `.vfs_root`, `.vfs_statfs`, `.vfs_sync`, and `.vfs_unmount`.

## Mount And Remount Behavior

The update path distinguishes read-write to read-only and read-only to read-write transitions. Downgrading to read-only suspends writes, flushes writable vnodes, marks the volume clean while the provider is still writable, drops the GEOM write reference, clears `pm_fmod`, sets `MSDOSFSMNT_RONLY`, and sets `MNT_RDONLY`. Upgrading verifies write access or mount privilege on the original device vnode, gains a GEOM write reference, marks the volume dirty via `markvoldirty_upgrade()`, then clears the read-only flags.

For a new mount, the code accepts device mounts only, checks VREAD/VWRITE permissions or `PRIV_VFS_MOUNT_PERM`, protects against multiple mounts by atomically setting `dev->si_mountpt`, opens the provider through GEOM, and sets `BO_NOBUFS` on the original device vnode buffer object while the mounted filesystem owns device buffering.

`update_mp()` applies charset/iconv options and ownership/mask/name-mode flags. If `nowin95` is set, it forces short-name mode; otherwise it defaults to long-name mode. Charset conversion handles are opened only when `kiconv` is requested and `msdosfs_iconv` is available.

## FAT Geometry And Validation

`mountmsdosfs()` reads the boot sector, optionally checks boot signatures, initializes DOS 5 style BPB fields, and then fixes FAT32-specific fields from the FAT32 BPB extension. Validation checks include nonzero bytes-per-sector and sectors-per-cluster, power-of-two sector and cluster sizing, minimum sector size, nonzero total and FAT sectors, maximum cluster size within `MAXBSIZE`, volume size not exceeding provider media size, total sectors past first cluster, and FAT capacity not exceeded by the computed maximum cluster.

FAT type is selected from BPB layout and cluster count. FAT32 uses a root-directory cluster and FSInfo block; FAT12/FAT16 use a fixed root directory between the FAT area and first data cluster. FAT12 uses a 3/2 FAT byte addressing ratio and a smaller FAT block size chosen to avoid split entries. FAT16 and FAT32 use page-sized FAT blocks rounded to the device sector size.

The FSInfo block is trusted only if its signatures match. The next-free hint is clamped to a valid cluster range, and the free-count field is ignored because the implementation scans the FAT into `pm_inusemap`.

## Sync, Stat, And Export Semantics

`msdosfs_statfs()` reports clusters as blocks and uses `pm_freeclustercount` for both free and available blocks. File counts are meaningful mainly for the fixed FAT12/FAT16 root directory; FAT32 sets root-directory free entries to zero.

`msdosfs_sync()` scans every vnode on the mount, skips clean or lazy-only vnodes, nonblocking-locks dirty vnodes, calls `VOP_FSYNC()`, then fsyncs the device vnode for non-lazy sync and flushes FAT32 FSInfo through `msdosfs_fsiflush()`. On `MNT_SUSPEND`, it sets `MNTK_SUSPEND2 | MNTK_SUSPENDED` after successful flushing.

`msdosfs_fhtovp()` maps exported file handles containing directory cluster and directory offset back to denodes via `deget()`, then creates a vnode VM object sized to `de_FileSize`.

## Dependencies

This file depends on FreeBSD VFS, vnode, mount, namei, privilege, buffer cache, taskqueue, and GEOM APIs. msdosfs-specific dependencies include BPB/boot-sector structures, denodes, FAT helpers, `fillinusemap()`, `markvoldirty()`, `markvoldirty_upgrade()`, `deget()`, FAT type macros, cluster constants, and FSInfo encoding helpers.

## Invariants And Risks

- Writable mounts must mark the FAT volume dirty and must mark it clean before dropping write access during unmount or read-only remount.
- `dev->si_mountpt`, GEOM open references, `BO_NOBUFS`, device references, mount data, and the FAT lock have tightly paired setup and cleanup paths.
- BPB parsing is deliberately defensive; overflow and media-size checks prevent bogus media from creating invalid cluster arithmetic.
- The fixed FAT12/FAT16 root directory cannot grow, so root free-entry accounting is mount-time state later maintained by allocation/free macros.
- Emergency read-only remount is asynchronous and relies on busying the mount before queueing the task; pending counts are unwound in `msdosfs_remount_ro()`.

<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_vnops.c

## Purpose

`msdosfs_vnops.c` implements the FreeBSD vnode operation vector for FAT/MS-DOS files and directories. It translates VFS operations into denode, FAT-chain, directory-entry, buffer-cache, and VM pager operations while preserving FAT-specific limitations: no hard links, no symlinks, only regular files/directories, 32-bit file sizes, case-insensitive names, synthetic root dot entries, and non-sparse file data.

## Main Entry Points

- Namespace operations: `msdosfs_create()`, `msdosfs_remove()`, `msdosfs_rename()`, `msdosfs_mkdir()`, `msdosfs_rmdir()`, `msdosfs_link()`, `msdosfs_symlink()`, and `msdosfs_mknod()`.
- File state and attributes: `msdosfs_open()`, `msdosfs_close()`, `msdosfs_access()`, `msdosfs_getattr()`, `msdosfs_setattr()`, `msdosfs_fsync()`, `msdosfs_pathconf()`, and `msdosfs_print()`.
- Data and directory I/O: `msdosfs_read()`, `msdosfs_write()`, `msdosfs_readdir()`, `msdosfs_bmap()`, `msdosfs_getpages()`, and `msdosfs_strategy()`.
- Export support: `msdosfs_vptofh()` creates `struct defid` file handles from denode directory cluster/offset.
- Registration: `msdosfs_vnodeops` maps the VOP vector to these routines and inherited/common routines such as `msdosfs_lookup`, `msdosfs_inactive`, and `msdosfs_reclaim`.

## File Creation And Attribute Semantics

`msdosfs_create()` refuses to extend a full fixed root directory, creates an 8.3 on-disk name with `uniqdosname()`, initializes a zero-length archive denode with access/create/update timestamps, calls `createde()`, and populates the name cache when requested.

`msdosfs_getattr()` derives synthetic POSIX attributes from FAT metadata. The file ID computation must match `msdosfs_readdir()` so tools such as `pwd` work. Directories use their starting cluster converted to a filesystem block and directory-entry index; regular files use the containing directory cluster plus directory offset. DOS attributes map to FreeBSD user flags (`UF_ARCHIVE`, `UF_HIDDEN`, `UF_READONLY`, `UF_SYSTEM`). All objects report the mount owner/group, one link, and mode bits masked by the mount file or directory mask.

`msdosfs_setattr()` rejects unsupported vnode attributes and rejects root-directory mutation. Ownership changes are only accepted if they resolve back to the mount-wide uid/gid. Size changes are allowed only for regular files and route through `detrunc()`. Time changes use FAT timestamp conversion, skip access time when Win95 metadata is disabled, and set the archive bit for non-directories. Mode writes only affect the FAT read-only bit through the owner write bit.

## Read And Write Behavior

`msdosfs_read()` reads cluster-sized pieces until EOF or residual exhaustion. Directory data is read through the filesystem device vnode because FAT directory entry metadata lives in directory blocks and the buffer cache key must use the device vnode. Regular file reads use clustered reads unless disabled by mount flags, and set `DE_ACCESS` on successful non-read-only, non-noatime reads.

`msdosfs_write()` supports only regular files. `IO_APPEND` moves the offset to EOF. Since FAT has no sparse files, writes beyond EOF first call `deextend()` to fill the hole. Writes beyond current EOF preallocate clusters via `extendfile()` to improve contiguity. Full-cluster writes avoid disk reads by using `getblk()` and clearing the buffer first so mmap cannot observe uninitialized data if `uiomove` faults. Partial writes read existing cluster data. Buffer writeback is selected among synchronous writes, async writes under memory pressure, clustered writes on cluster boundaries, and delayed writes otherwise.

Failure handling is sensitive to `IO_UNIT`: unit writes roll file size and `uio` state back to the original state, while partial non-unit writes may return success if some data was written. `vn_rlimit_fsizex()` enforces `MSDOSFS_FILESIZE_MAX` and its result is finalized after write completion.

## Rename And Directory Operations

`msdosfs_rename()` is the most complex operation in this file. It rejects cross-device renames and unsupported flags except `AT_RENAME_NOREPLACE`, relocks source and destination parents in a deadlock-avoidance loop, revalidates source and target by on-disk directory location, rejects `.`/`..`/self-directory aliases, checks write access and hierarchy constraints for moving directories to a new parent, removes an existing compatible empty target, generates the destination DOS name, creates the destination entry, removes the old entry, updates denode hash location, and repairs a moved directory's `..` entry when its parent changes. If removing the old entry or updating `..` fails after the new entry has been written, it reports an integrity error and schedules remount read-only.

`msdosfs_mkdir()` allocates one cluster, initializes `.` and `..` entries from `dosdirtemplate`, handles FAT32 high cluster words, writes the initialized cluster before linking it from the parent, then creates the parent directory entry. On failure it frees the allocated cluster. `msdosfs_rmdir()` verifies the target directory is empty with `dosdirempty()`, removes the directory entry, purges parent and target cache entries, and truncates the directory to free its cluster chain.

Hard links, symlinks, and device nodes are unsupported (`EOPNOTSUPP` or `EINVAL`) because FAT does not represent them.

## Directory Reading

`msdosfs_readdir()` converts raw FAT directory slots into `struct dirent`. It rejects non-directories and misaligned offsets. For root directories it synthesizes `.` and `..` because FAT root directories do not store those entries in the same way as ordinary directories. It tracks long-name slots with `mbnambuf`, `win2unixfn()`, and checksum matching; if the long-name checksum fails or short-name mode is forced, it falls back to `dos2unixfn()`. Deleted, empty, long-name-only, and volume-label entries are skipped as appropriate.

The routine computes `d_fileno` consistently with `msdosfs_getattr()`, emits cookies as next FAT directory-entry offsets, sets EOF on empty slots or file-size exhaustion, and updates `uio_offset` to the last delivered FAT-entry boundary.

## Block Mapping, Pager, And Strategy

`msdosfs_bmap()` maps logical cluster numbers to device block numbers with `pcbmap()`, returns the device buffer object, and computes contiguous run lengths before and after the requested cluster for clustered I/O. It saves and restores the denode FAT-chain cache around run probing so read-ahead does not push the useful cache position too far ahead of actual I/O.

`msdosfs_getpages()` can use the buffer pager through `vfs_bio_getpages()` with FAT-specific logical block and block-size callbacks, controlled by `vfs.msdosfs.use_buf_pager`. Otherwise it falls back to `vnode_pager_generic_getpages()`.

`msdosfs_strategy()` maps unmapped buffers through `pcbmap()`, clears buffers for impossible FAT holes, sets `b_iooffset`, and dispatches to the mounted device buffer object through `BO_STRATEGY()`.

## Dependencies

The file depends on FreeBSD VFS, vnode, buffer cache, VM pager, namecache, credentials, privilege checks, resource limits, and pathconf APIs. msdosfs dependencies include denode flags and timestamps, FAT cluster allocation/free/truncation/mapping helpers, directory creation/removal helpers, DOS/Win95 name conversion, case-insensitive lookup support, and integrity-error remount support from `msdosfs_vfsops.c`.

## Invariants And Risks

- File IDs in `getattr` and `readdir` must remain identical for the same object.
- FAT directory metadata is buffer-cache keyed by the device vnode, not the directory vnode.
- FAT files cannot be sparse; extension before writes is required for holes.
- Rename has crash-consistency and corruption risk because FAT directory-entry updates are not transactional; the code remounts read-only after certain post-link failures.
- Long-name reconstruction depends on correct checksum/order handling and must gracefully fall back to 8.3 names.
- The root directory is special for FAT12/16 and partly special for FAT32, affecting dot entries, free-entry limits, and `..` encoding.

<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfsmount.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfsmount.h

## Purpose

`msdosfsmount.h` defines the in-kernel mount control block, mount arguments, flags, locking macros, and block/cluster conversion helpers for FreeBSD msdosfs. It is the shared structural contract between msdosfs VFS operations, vnode operations, FAT code, denode code, and user-facing mount argument translation.

## Key Structures

`struct msdosfsmount` stores all per-mount state:

- VFS and device integration: `pm_mountp`, GEOM consumer `pm_cp`, device buffer object `pm_bo`, mounted device vnode `pm_devvp`, original device vnode `pm_odevvp`, and character device `pm_dev`.
- Ownership and permission synthesis: `pm_uid`, `pm_gid`, `pm_mask`, and `pm_dirmask`.
- BPB and filesystem geometry: `pm_bpb`, sector/block ratios, FAT sector counts, FAT start block, root directory block or FAT32 cluster, fixed root directory size, first data cluster, max cluster, cluster/block shift values, bytes per cluster, FAT block size, FAT size, FAT mask, FAT32 FSInfo block, current FAT, and root directory free-slot count.
- Allocation state: `pm_freeclustercount`, `pm_nxtfree`, `pm_fatmult`, `pm_fatdiv`, and `pm_inusemap`.
- Runtime flags and services: `pm_flags`, iconv handles for local/Unicode/DOS conversions, `pm_fatlock`, and `pm_rw2ro_task` for emergency read-only remount.

`struct msdosfs_fileno` maps a 64-bit file number to a 32-bit number in a red-black tree node. This header declares the structure but the behavior lives elsewhere.

`struct msdosfs_args` is the legacy kernel mount argument layout consumed by `msdosfs_cmount()`: device path, export args, uid/gid, file mask, flags, old unused Unicode table storage, charset names, and directory mask.

## Macros And Helpers

The header aliases BPB fields (`pm_BytesPerSec`, `pm_ResSectors`, `pm_FATs`, and others) into the embedded BPB. It defines `VFSTOMSDOSFS()` for retrieving mount data, `FATOFS()` for byte offsets into the FAT, `N_INUSEBITS` for allocation bitmap sizing, and multiple conversions among file offsets, logical cluster numbers, device block numbers, and FAT root directory locations.

Important conversion helpers include:

- `de_cluster()`, `de_clcount()`, `de_blk()`, `de_cn2off()`, and `de_bn2off()` for translating file offsets and cluster/block units.
- `cntobn()` for mapping a data cluster number to a filesystem-relative device block.
- `roottobn()` and `detobn()` for fixed root directory and ordinary directory entry block mapping.
- `bptoep()` for locating a `struct direntry` inside a buffer by directory offset.

The root directory accounting macros `rootde_alloced()` and `rootde_freed()` update `pm_rootdirfree` only for fixed FAT12/FAT16 root directories. The lock macros wrap `pm_fatlock` through `lockmgr()`.

## Flags

Mount option flags include `MSDOSFSMNT_SHORTNAME`, `MSDOSFSMNT_LONGNAME`, `MSDOSFSMNT_NOWIN95`, and `MSDOSFSMNT_KICONV`. Runtime/internal flags include `MSDOSFSMNT_RONLY`, `MSDOSFSMNT_WAITONFAT`, `MSDOSFS_FATMIRROR`, `MSDOSFS_FSIMOD`, and `MSDOSFS_ERR_RO`.

## Dependencies

The header depends on kernel lock, task, tree, mount/vnode/device types, FAT BPB definitions, and directory entry/cluster constants from the rest of msdosfs. It exposes `msdosfs_integrity_error()` to kernel code.

## Invariants And Risks

- Shift and mask conversion macros assume power-of-two sector and cluster sizes validated at mount time.
- `pm_rootdirblk` means a block number for FAT12/16 but a root cluster for FAT32; callers must use FAT type checks correctly.
- `pm_fatlock` protects FAT allocation state and must be held for allocation bitmap/FAT mutations.
- Mount option flags and internal runtime flags share `pm_flags`, so option-mask use must avoid clobbering runtime bits.

<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfsmount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs.h

## Purpose

`nfs.h` is a central FreeBSD NFS header defining timing constants, sizing limits, `nfssvc(2)` argument structures, NFSv4 client/server state flags, attribute and operation bitset helpers, socket/request descriptors, file-handle structures, NFS request descriptor layout, session slots, ACL support constants, and assorted NFS utility macros.

## Constants And Tunables

The header defines client/server timing defaults such as `NFS_TICKINTVL`, `NFS_TIMEO`, minimum/maximum timeout values, TCP timeout, callback timeout/retry counts, upcall timeout/retry counts, soft-mount retry defaults, delegation return wait, and NFSv4 lease-related constants. It also defines I/O sizing defaults (`NFS_WSIZE`, `NFS_RSIZE`, `NFS_READDIRSIZE`), read-ahead/async daemon limits, hash-table sizes, state/cache high-water marks, pNFS device limits, and maximum NFSv4 owner/group string length.

NFSv4 root constants reserve a synthetic FSID/inode/generation for the v4 pseudo-root. Server/client cache and state watermarks are used by other NFS server and client code to bound memory/state growth.

## nfssvc And Userland ABI Structures

The header declares several structures passed through the `nfssvc(2)` interface or related NFS userland daemons:

- `nfsd_addsock_args`, `nfsd_nfsd_args`, and old `nfsd_nfsd_oargs` for nfsd startup and socket/service configuration, including pNFS DS metadata in the newer structure.
- `nfsd_pnfsd_args` and `PNFSDOP_*` operations for pNFS data-server management.
- `nfsd_nfscbd_args`, `nfscbd_args`, and `nfsuserd_args` for callback daemon and nfsuserd configuration.
- `nfsd_oidargs`, `nfsuserd_args`, `nfsd_clid`, dump-list/client/lock structures, and `nfsreferral` for id mapping, stats/dump operations, lock/client reporting, and referrals.

## NFSv4 State Flags

`LCL_*` flags describe NFSv4 server client state such as confirmation, callback transport, callback liveness, GSS modes, admin revoke, reclaim completion, NFSv4.1/v4.2 support, TLS callback state, and machine-credential state.

`NFSLCK_*` flags describe open/share/lock/delegation state. The access and deny bits are intentionally ordered because later code shifts between read/write access, deny, and lock bits. Flags cover open, close, lock, unlock, blocking, reclaim, delegation, downgrade, release, setattrs, and wanted delegation types.

## Attribute And Operation Bitsets

`nfsattrbit_t` is a fixed three-word bitset with macros for zero/copy/test/set/clear operations and common attribute masks. Macros build masks for supported attributes, fillable attributes, settable attributes, GETATTR, weak cache consistency, write GETATTR, callback GETATTR, pathconf, statfs, rootfs, readdirplus, and referral attributes. Several macros conditionally remove NFSv4.1 or NFSv4.2 attributes based on descriptor flags.

`nfsopbit_t` is a fixed three-word operation bitset with analogous zero/copy/test/set/clear helpers for NFSv4 operation support.

The header comments explicitly warn that these macros must be updated if the bitset word count changes.

## Runtime Structures

`struct nfscred` stores the uid and groups used when stateids are acquired. `struct nfssockreq` records socket address, socket type/protocol/flags, credential, lock bits, mutex, RPC program/version, RPC client, cached AUTH handle, and server principal name storage. `struct nfsrv_descript` is the central request/reply descriptor for NFS client, server, and callback code; it tracks mbuf chains, current XDR positions, flags, procedure number, reply status, credentials, GSS principal, TCP/socket refs, NFSv4 session IDs and slot sequencing, current stateids, max request/response sizes, external-page build state, and allowed operations for machine credentials.

Other structures include client/server file handles (`nfsfh`, `nfsrvfh`), NFSv4 sleep lock state (`nfsv4lock`), NFSv4.1 sequence slots (`nfsslot`), GSS mechanism descriptors, network-address unions, and request-queue heads.

## Descriptor Flags

`ND_*` flags encode protocol version, security mode, reply-cache behavior, public lookup, GSS principal use, same TCP connection, implied client ID, no-more-data state, callback/client direction, NFSv4.1/v4.2/session/slot state, pNFS data-server state, current-stateid handling, external-page mbufs, TLS modes, relockup state, and machine credentials. These flags are consumed heavily by XDR builders/parsers and `newnfs_request()`.

## Dependencies

This header bridges kernel-only types from RPC, sockets, mbufs, credentials, vnodes, mount state, NFS XDR constants, ACL constants, and pNFS/session state defined in other NFS headers. It is intentionally shared across NFS client, server, callback, and common-port code.

## Invariants And Risks

- Fixed-size bitset macros must stay synchronized with protocol maximum attribute/op numbers.
- Many state flags are protocol-coupled; changing flag values can break shift-based lock/open/share tests.
- `struct nfsrv_descript` is shared across many layers, so flag interpretation and mbuf cursor ownership must be consistent.
- `nfssvc` structures are ABI-facing and must preserve layout compatibility for old and new userland callers.

<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonacl.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonacl.c

## Purpose

`nfs_commonacl.c` converts between FreeBSD ACL entries and NFS wire encodings. It handles NFSv4 ACL ACE XDR parsing/building, POSIX draft ACL ACE XDR parsing/building, permission-mask translation, user/group string conversion, and ACL equality comparison.

## Main Entry Points

- `nfsrv_dissectace()` parses one NFSv4 ACE from an NFS descriptor into `struct acl_entry`.
- `nfsrv_dissectposixace()` parses one POSIX draft ACL ACE.
- `nfs_aceperm()` converts FreeBSD regular-file ACL permission bits to NFSv4 `acemask4`.
- `nfsrv_buildacl()` serializes a FreeBSD NFSv4 ACL as an NFSv4 ACL list.
- `nfsrv_buildposixacl()` serializes a POSIX draft ACL list.
- `nfsrv_compareacl()` compares two ACLs for same count, same tags, same ids for user/group entries, and same permissions for POSIX-style comparable entries.

Internal helpers include `nfsrv_acemasktoperm()`, `nfsrv_buildace()`, and `nfsrv_buildposixace()`.

## NFSv4 ACE Parsing

`nfsrv_dissectace()` reads ACE type, flags, mask, and who-string length from XDR. It bounds the who string to `NFSV4_OPAQUELIMIT`, treats zero-length who strings from NetApp filers as a deny ACE for `ACL_EVERYONE` with undefined id to avoid panics, and allocates temporary name storage only when the name exceeds `NFSV4_SMALLSTR`.

Special principals `OWNER@`, `GROUP@`, and `EVERYONE@` map to `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, and `ACL_EVERYONE`. Other names map through `nfsv4_strtouid()` or `nfsv4_strtogid()` depending on `NFSV4ACE_IDENTIFIERGROUP`. Supported inheritance/audit flags are translated to FreeBSD ACL entry flags; unknown remaining flag bits produce `NFSERR_ATTRNOTSUPP`. Servers accept only allow/deny ACE types, while non-server parsing also accepts audit/alarm types. Permission masks are translated by `nfsrv_acemasktoperm()`.

## POSIX Draft ACE Parsing

`nfsrv_dissectposixace()` reads a numeric POSIX ACL tag, permission bits, and optional name. It validates the tag range, maps protocol tags through `nfsv4_to_posixacltag`, resolves ids only for `ACL_USER` and `ACL_GROUP`, and returns the ACE wire size when requested. Name lengths are bounded by `NFSV4_OPAQUELIMIT`.

## ACL Building

`nfsrv_buildacl()` emits an ACE count placeholder, iterates ACL entries, maps owner/group/everyone tags to special names, converts user/group ids to NFSv4 names with `nfsv4_uidtostr()` and `nfsv4_gidtostr()`, skips unsupported tags, serializes each ACE with `nfsrv_buildace()`, and finally writes the count. `nfsrv_buildace()` translates FreeBSD flags and type to NFSv4 ACE fields. Directory ACEs map directory-specific permissions such as list/add/search/delete-child explicitly, while non-directory ACEs use `nfs_aceperm()`.

`nfsrv_buildposixacl()` similarly emits POSIX draft ACL ACEs, using empty names for object/mask/other entries and id-to-string conversion only for named users and groups. A NULL ACL produces a zero entry count.

## Dependencies

This file depends on NFS XDR descriptor macros (`NFSM_DISSECT`, `NFSM_BUILD`, `nfsm_advance` through included infrastructure), mbuf string helpers (`nfsrv_mtostr()`), user/group mapping functions, ACL type/flag/permission constants, NFSv4 ACE constants, and NFS memory type `M_NFSSTRING`.

## Invariants And Risks

- Wire string lengths must be bounded before allocation or mbuf extraction.
- Unknown ACE flags, types, or mask bits must surface as `NFSERR_ATTRNOTSUPP` rather than being silently accepted.
- Directory and file ACE masks differ: directory search/list/add semantics are not identical to regular file read/write/execute semantics.
- Special principals must not be passed through id mapping.
- Build routines skip unsupported local ACL tags, so callers must understand that serialized ACE counts may be lower than local `acl_cnt`.

<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonacl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonkrpc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonkrpc.c

## Purpose

`nfs_commonkrpc.c` implements the common kernel RPC transport layer used by the FreeBSD NFS client, NFS callbacks, upcalls, pNFS data-server calls, and NFSv4.1 session-aware request handling. It creates and tears down krpc clients, selects authentication, sends mbuf-based RPC calls, parses common reply framing, manages NFSv4 sequence slots, handles retry/backoff/recovery cases, tracks server down/up notifications, and provides signal-interrupt helpers for interruptible mounts.

## Global State And Sysctls

The file defines DTrace probe hooks for NFSv2/3/4 client RPC start/done events when KDTrace is enabled. It declares shared NFS locks, statistics, request queues, callback pools, and client-state globals. Tunables include:

- `vfs.nfs.bufpackets` for socket buffer reservation scaling.
- `vfs.nfs.reconnects` for reconnect count.
- `vfs.nfs.nfs3_jukebox_delay`.
- `vfs.nfs.skip_wcc_data_onerr`.
- `vfs.nfs.dsretries` for pNFS data-server RPC retry limits.

`nfscl_use_gss[]` marks which NFSv4 operations should use RPCSEC_GSS under security modes such as `syskrb5`.

## Connection Management

`newnfs_connect()` creates an RPC client for a mount, callback, upcall, or pNFS DS connection. It temporarily installs the mount/socket credential as the current thread credential because low-level socket setup may use `td_ucred`. It chooses `udp`, `tcp`, `udp6`, or `tcp6` netconfig entries from the target address and socket type, probes socket buffer reservations with `soreserve()`, clamps `bufpackets` between 2 and 64, and emits guidance when `kern.ipc.maxsockbuf` is too small for large TCP NFS I/O.

For client mounts it configures interruptibility, reserved ports, TLS/certificate options, hard/soft retry counts, UDP retry timeout, and NFSv4/pNFS timeout behavior. For NFSv4.1 client connections it may attach a callback backchannel when callback daemons are running. For DS connections (`cred == NULL`) it sets shorter timeouts and `dsretries` so failed data servers are detected. For callbacks/upcalls (`nmp == NULL`) it selects callback or upcall retry behavior and optional TLS. The created `CLIENT` is installed under `nr_mtx`; if another thread connected first, the local client is released.

`newnfs_disconnect()` atomically detaches the primary client and any `nconnect` auxiliary clients, purges GSS security state in the credential's vnet, closes, and releases all RPC clients.

## Authentication

`nfs_getauth()` returns an RPC AUTH handle for AUTH_SYS or RPCSEC_GSS Kerberos flavors. For Kerberos it maps security flavor to GSS service (`none`, `integrity`, or `privacy`), obtains the Kerberos mechanism OID when needed, and either finds an existing security context for a server principal or creates one using an explicit client principal. AUTH_SYS falls back to `authunix_create()`.

`newnfs_request()` chooses credentials and authentication based on callback/client direction, mount security flags, `ND_USEGSSNAME`, system uid configuration, root credential fallback, server principal storage in `nfssockreq`, and operation-specific `nfscl_use_gss[]` policy.

## Request Path

`newnfs_request()` is the central RPC engine. It rejects new requests during forced unmount, holds the authentication credential, masks interruptible-mount signals around the RPC if needed, ensures the primary connection exists, optionally selects an `nconnect` auxiliary TCP connection for large read/write/readdir RPCs, sets feedback callbacks, maps NFSv4 procedures to `COMPOUND`, maps NFSv3 logical proc numbers to NFSv2 proc numbers when needed, and allocates a lightweight outstanding request record for NFSv4 compound operations requiring recovery suppression.

It then sends the request via:

- `clnt_bck_call()` for backchannel callback calls tied to a session transport,
- `CLNT_CALL_MBUF()` on an auxiliary `nconnect` client for large data calls,
- or `CLNT_CALL_MBUF()` on the primary `nfssockreq` client.

The current thread credential is temporarily changed to the auth credential during `CLNT_CALL_MBUF()` because RPC auth refresh may require the correct vnet.

RPC status is translated to kernel errors. Timeouts increment stats and become `ETIMEDOUT`; version mismatch becomes protocol errors; send/receive/system errors may free or poison NFSv4.1 session slots; auth errors become `EACCES`. Successful replies are realigned for strict-alignment architectures, then the descriptor mbuf cursors are initialized.

## NFSv4 And Session Handling

For NFSv4 replies, `newnfs_request()` strips the compound tag, reads operation count and first op/status, and handles `SEQUENCE` or `CBSEQUENCE` results. It verifies session IDs, slot IDs, returned sequence numbers, and target/highest slot values. It adjusts the session's fore-channel slot count, resets unused slot sequence values when the server lowers slot availability, records bad slots on mismatches or `NFSERR_SEQMISORDERED`, and frees slots after use.

`NFSERR_BADSESSION` on a client MDS RPC marks the MDS session defunct, initiates recovery when appropriate, sleeps briefly for a new session, optionally rewrites the request's SEQUENCE fields when `ND_LOOPBADSESS` is set, and retries. Delay/grace/resource/retryable uncached reply errors use exponential sleep capped by `NFS_TRYLATERDEL`; if a sequence slot was consumed, its sequence number is incremented and patched into the request before retry.

The code marks `ND_INCRSEQID` for open/confirm/downgrade/close/lock/locku operations when their reply status requires advancing the open/lock owner sequence. It also sets `ND_NOMOREDATA` for most failed NFSv4 operations and maps stale recovery errors to `NFSERR_STALEDONTRECOVER` when the outstanding request was marked `R_DONTRECOVER`.

## Cancellation, Signals, And Notifications

`newnfs_nmcancelreqs()` closes the primary mount client, auxiliary `nconnect` clients, and DS clients on all non-MDS sessions so forced unmounts or teardown can terminate outstanding RPCs.

`newnfs_set_sigmask()`, `newnfs_restore_sigmask()`, `newnfs_msleep()`, and `newnfs_sigintr()` implement the signal behavior for `NFSMNT_INT` mounts. Only a narrow signal set (`SIGINT`, `SIGTERM`, `SIGHUP`, `SIGKILL`, `SIGQUIT`) is allowed to interrupt NFS operations, while already-masked or ignored signals remain masked.

`nfs_feedback()`, `nfs_down()`, and `nfs_up()` produce rate-limited terminal messages and VFS event notifications (`VQ_NOTRESP`, `VQ_NOTRESPLOCK`) when servers stop responding or recover.

`nfs_resetslots()` clears sequence numbers for nonbusy slots above the current fore-channel slot limit.

## Dependencies

This file depends on FreeBSD krpc (`CLNT_CALL_MBUF`, `clnt_reconnect_create`, `CLNT_CONTROL`), RPCSEC_GSS, sockets, credentials/vnets, NFS mount/session/client state, NFS descriptor/XDR macros, DTrace hooks, vfs event signaling, task/callback infrastructure, and NFS recovery/session helpers such as `nfsv4_freeslot()`, `nfsv4_sequencelookup()`, and `nfsmnt_mdssession()`.

## Invariants And Risks

- `nd_mreq` is always consumed/freed by `newnfs_request()`, including error paths.
- Current thread credentials are deliberately swapped during connect/auth/RPC refresh and must always be restored.
- NFSv4.1 session slot sequence numbers are fragile; failed sends, bad slots, wrong slots, and retries must not allow stale cached replies to be accepted.
- Retry behavior differs by operation because non-idempotent NFSv4 operations cannot always be replayed safely.
- `nconnect` sends only selected large-message operations over auxiliary connections to avoid head-of-line blocking for small metadata RPCs.
- GSS auth handles cached in `nfssockreq` must not be destroyed by request cleanup, while per-request auth handles must be destroyed.

<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonkrpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonport.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonport.c

## Purpose

`nfs_commonport.c` is the FreeBSD-specific common port layer for the shared NFS implementation. It owns global storage, malloc types, mutex initialization, mbuf realignment for strict-alignment architectures, pathname lookup wrappers, credential helpers, sleep/pathconf/filesystem-info wrappers, `nfssvc` dispatch for shared common functions, compatibility stats conversion, per-vnet initialization/cleanup, ACL support probes, pNFS taskqueue dispatch, and the `nfscommon` module lifecycle.

## Global State

The file defines common NFS globals such as `newnfs_numnfsd`, `nfsstatsv1`, `nfs_numnfscbd`, `nfscl_debuglevel`, `nfsrv_lughashsize`, `nfsrv_dslock_mtx`, `nfsrv_devidhead`, `nfsrv_devidcnt`, `ncl_call_invalcaches`, `nfs_advlock_p`, `nfs_reclaim_p`, and `nfs_srvmaxio`. It defines per-vnet `nfsstatsv1_p` and references per-vnet nfsuserd socket/state.

It registers the `_vfs.nfs` sysctl node with realignment counters, debug level, user hash size, and pNFS I/O thread count. It also defines all FreeBSD `MALLOC_DEFINE()` storage classes for common NFS server/client state, file handles, lock/open/delegation state, strings, request headers, pNFS layouts/devices/sessions, and server sessions.

## Portability Wrappers

`newnfs_realign()` is a no-op on architectures that tolerate unaligned access. On strict-alignment architectures it scans an mbuf chain and, when any mbuf length or data pointer is not 4-byte aligned, copies the remaining chain into a newly allocated aligned mbuf chain and frees the original chain tail. Counters expose how often the test and realignment occur.

`nfsrv_lookupfilename()` wraps `namei()` for user-space paths. `newnfs_copycred()` copies stored NFS uid/group credentials into a FreeBSD `ucred`. `nfsmsleep()` maps a `timespec` timeout to ticks and calls `msleep()`. `newnfs_setroot()` and `newnfs_getcred()` create root-like credentials used for renew/recovery. `nfs_catnap()` implements short sleeps, using five seconds during NFS grace and one tick otherwise.

`nfsvno_getfs()` provides NFSv3 FSINFO-style server defaults, using datagram max data for UDP and `nfs_srvmaxio` otherwise. `nfsvno_pathconf()` wraps `VOP_PATHCONF()` and fakes common pathconf values instead of failing for unsupported flags. `nfsrv_atroot()` and `nfsv4root_getreferral()` are stubs in this FreeBSD port layer.

## nfssvc Dispatch And Stats Compatibility

`nfssvc_nfscommon()` switches to the caller's vnet and delegates to `nfssvc_call()`. `nfssvc_call()` handles common `nfssvc` flags:

- `NFSSVC_IDNAME` copies old or new id/name arguments and calls `nfssvc_idname()`.
- `NFSSVC_GETSTATS` copies current per-vnet `nfsstatsv1` into either old `ext_nfsstats`, older `nfsstatsov1`, or current `nfsstatsv1` user buffers, translating operation-count arrays where old layouts differ from NFSv4.2 layouts.
- `NFSSVC_ZEROCLTSTATS` and `NFSSVC_ZEROSRVSTATS` zero selected client/server statistics after a successful get-stats.
- `NFSSVC_NFSUSERDPORT` copies old or new nfsuserd port arguments and calls `nfsrv_nfsuserdport()`.
- `NFSSVC_NFSUSERDDELPORT` removes the nfsuserd port.

The stats conversion code is intentionally verbose because it maintains ABI compatibility across historical stats layouts.

## ACL And pNFS Helpers

`nfs_supportsnfsv4acls()` and `nfs_supportsposixacls()` require a locked vnode, honor the global `nfsrv_useacl` switch, call `VOP_PATHCONF()` with `_PC_ACL_NFS4` or `_PC_ACL_EXTENDED`, and return boolean support.

`nfs_pnfsio()` lazily creates a `pnfsioq` taskqueue and starts pNFS mirror I/O worker threads. If `vfs.nfs.pnfsiothreads` is negative, it defaults to `mp_ncpus * 4`; zero disables pNFS I/O dispatch. The function initializes the embedded task in the caller-provided pNFS I/O context and enqueues it, updating `inprog` according to enqueue success.

## Initialization And Module Lifecycle

`newnfs_portinit()` initializes common SMP locks once. `nfs_vnetinit()` points default-vnet stats at the global `nfsstatsv1`, allocates stats for non-default vnets, and initializes the per-vnet nfsuserd socket mutex. `nfs_cleanup()` destroys the per-vnet mutex, frees non-default stats, and cleans the name/id cache.

`nfscommon_modevent()` handles module load/unload. Load initializes mutexes, the pNFS DS lock and device list, common NFS code via `newnfs_init()`, and installs `nfssvc_nfscommon` into `nfsd_call_nfscommon`. Unload refuses while nfsd, nfsuserd, or callback daemons are active, clears the function pointer, and destroys mutexes. The module declares dependencies on `nfssvc` and `krpc`.

## Dependencies

This file depends on FreeBSD sysctl, vnet, mutex, mbuf, vnode, namei, taskqueue, VM/UMA, RPC common code, NFS id-mapping support, NFS stats structures, pNFS structures, and common NFS initialization/cleanup helpers declared elsewhere.

## Invariants And Risks

- Per-vnet stats storage differs for the default vnet and non-default vnets; cleanup must not free the global default stats.
- Old stats layouts must be kept compatible with current `nfsstatsv1`, including fake/pure NFSv4.2 operation index translations.
- `newnfs_realign()` cannot realign in place because mbuf buffers may contain adjacent RPC data; it must allocate/copy/free.
- The pNFS taskqueue is lazily initialized without an explicit teardown in this file, so repeated calls rely on the static queue pointer and module lifetime.
- Module unload must be blocked while common NFS users are active to avoid dangling function pointers or destroyed locks.

<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonport.c -->