# Group Research: group_1241_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_msdosfs_msdosfs_fat_c_s_60f552b74861

Scope: `Docs/research_subset_a.md`. All listed source files were read completely; no file was sampled.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_fat.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_fat.c

## Summary
Implements FAT block mapping, FAT cache maintenance, FAT entry reads/writes, FAT mirroring, free-space bitmap construction, cluster allocation/freeing, and file-chain extension for NetBSD msdosfs. It is the core allocator and logical-cluster-to-physical-sector translation layer for FAT12, FAT16, and FAT32.

## Main Responsibilities
- Map file-relative clusters to filesystem-relative sectors through `msdosfs_pcbmap()`, with special handling for fixed-size FAT12/16 root directories.
- Maintain denode FAT cache entries via `msdosfs_fc_lookup()` and `msdosfs_fc_purge()` to avoid repeated FAT-chain scans.
- Read and update FAT entries through `msdosfs_fatentry()`, preserving FAT32 high bits and handling packed FAT12 entries.
- Propagate FAT writes to mirrored FAT copies and update FAT32 FSInfo free-count/next-free hints in `updatefats()`.
- Track allocation state in `pm_inusemap` and `pm_freeclustercount` with `usemap_alloc()`, `usemap_free()`, and `msdosfs_fillinusemap()`.
- Allocate contiguous cluster chains with `chainlength()`, `chainalloc()`, and `msdosfs_clusteralloc()`, using a pseudo-randomized scan start for new files.
- Free clusters through `msdosfs_clusterfree()` and `msdosfs_freeclusterchain()`.
- Extend file chains through `msdosfs_extendfile()`, including optional zeroing for newly allocated directory clusters.

## Key Interfaces
- `msdosfs_pcbmap(struct denode *, u_long, daddr_t *, u_long *, int *)`.
- `msdosfs_fatentry(int, struct msdosfsmount *, u_long, u_long *, u_long)`.
- `msdosfs_clusteralloc(struct msdosfsmount *, u_long, u_long, u_long *, u_long *)`.
- `msdosfs_clusterfree(struct msdosfsmount *, u_long, u_long *)`.
- `msdosfs_freeclusterchain(struct msdosfsmount *, u_long)`.
- `msdosfs_fillinusemap(struct msdosfsmount *)`.
- `msdosfs_extendfile(struct denode *, u_long, struct buf **, u_long *, int)`.

## Risks
The file directly mutates FAT metadata and the allocation bitmap, so partial failures can desynchronize in-memory allocation state from on-disk FAT entries; for example, `chainalloc()` marks clusters allocated before `fatchain()` succeeds and does not roll back on `fatchain()` error. FAT12 packed-entry handling is offset-sensitive, and bounds checks around FAT block offsets are critical. `updatefats()` ignores FSInfo write errors after disabling future FSInfo updates, and FAT mirroring writes other copies before the primary/current FAT. Several recovery comments note crash-consistency limitations typical of non-journaled FAT.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_fat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_lookup.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_lookup.c

## Summary
Implements msdosfs directory lookup, directory-entry creation/removal helpers, directory emptiness checks, short-name collision generation, and Win95 long-name discovery. It bridges VFS pathname operations with FAT directory entry layout, including 8.3 aliases and long filename slot sequences.

## Main Responsibilities
- Perform `VOP_LOOKUP` for msdosfs directories, including access checks, name-cache lookup/insert, root `.`/`..` synthesis, short-name conversion, long-name checksum matching, slot discovery, and create/rename/delete result setup.
- Install new directory entries with `msdosfs_createde()`, extending directories as needed and writing Win95 long-name slots before the DOS entry.
- Roll back partially written long-name entries by marking slots deleted if directory-entry creation fails after modifications begin.
- Test directories for emptiness with `msdosfs_dosdirempty()`, ignoring deleted entries, volume labels, `.` and `..`.
- Read directory entries by parent cluster/offset through `msdosfs_readep()` and by denode through `msdosfs_readde()`.
- Remove directory entries and preceding long-name slots with `msdosfs_removede()`, including denode refcount handling and vcache rekeying for removed objects.
- Generate unique 8.3 aliases with `msdosfs_uniqdosname()`.
- Detect whether a directory appears to contain Win95 long filename entries via `msdosfs_findwin95()`.

## Key Interfaces
- `msdosfs_lookup(void *)`.
- `msdosfs_createde(struct denode *, struct denode *, const struct msdosfs_lookup_results *, struct denode **, struct componentname *)`.
- `msdosfs_dosdirempty(struct denode *)`.
- `msdosfs_readep(struct msdosfsmount *, u_long, u_long, struct buf **, struct direntry **)`.
- `msdosfs_readde(struct denode *, struct buf **, struct direntry **)`.
- `msdosfs_removede(struct denode *, struct denode *, const struct msdosfs_lookup_results *)`.
- `msdosfs_uniqdosname(struct denode *, struct componentname *, u_char *)`.
- `msdosfs_findwin95(struct denode *)`.

## Risks
Lookup result state is stored in the parent denode's `de_crap` and remains valid only while the directory lock discipline is respected. Negative name caching is disabled because case-insensitive and 8.3 alias behavior would make invalidation unsafe. Directory-entry creation and removal span multiple directory slots and sometimes multiple blocks, so failures can leave deleted or orphaned long-name slots. `msdosfs_removede()` intentionally deletes any preceding Win95 entries it sees, not only those proven to belong to the short entry. Directory scanning depends on FAT semantics where `SLOT_EMPTY` terminates the used directory region.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_rename.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_rename.c

## Summary
Implements msdosfs rename using NetBSD's `genfs_sane_rename` framework. It adapts the old VOP rename API to a saner internal flow, provides filesystem-specific permission and genealogy callbacks, creates the destination directory entry, removes the source entry, rekeys denodes, and fixes `..` for reparented directories.

## Main Responsibilities
- Normalize VFS rename arguments in `msdosfs_rename()`, unlocking/releasing nodes according to the caller contract and rejecting invalid target-directory self-renames.
- Delegate high-level ordering, locking, and validation to `genfs_sane_rename()` with msdosfs callback operations.
- Model FAT permissions as UFS-like modes based on mount owner, masks, and the DOS readonly bit.
- Check whether target directories are empty with `msdosfs_dosdirempty()`.
- Perform actual renames in `msdosfs_gro_rename()` by optionally removing the target, generating the destination 8.3 name, creating a new directory entry, incrementing `de_refcnt`, removing the old entry, and rekeying non-directory vcache entries.
- Handle same-object remove cases with `msdosfs_gro_remove()`.
- Re-run lookup and preserve `msdosfs_lookup_results` in `msdosfs_gro_lookup()`.
- Walk parent chains in `msdosfs_gro_genealogy()` using `..` entries to prevent directory cycles.
- Read and replace `..` entries with `msdosfs_read_dotdot()` and `msdosfs_rename_replace_dotdot()`.
- Lock directories safely for rename traversal with `msdosfs_gro_lock_directory()`.

## Key Interfaces
- `msdosfs_rename(void *)`.
- Static `msdosfs_sane_rename(...)`.
- Static `msdosfs_gro_rename(...)`, `msdosfs_gro_remove(...)`, `msdosfs_gro_lookup(...)`, and `msdosfs_gro_genealogy(...)`.
- Static `msdosfs_read_dotdot(...)` and `msdosfs_rename_replace_dotdot(...)`.
- `msdosfs_genfs_rename_ops`, the callback table passed to `genfs_sane_rename()`.

## Risks
The implementation explicitly notes non-journaled crash-consistency gaps: if a crash occurs after target removal or after destination creation but before source removal, POSIX rename guarantees may be violated. Several failure paths contain comments questioning whether rollback or panic is appropriate. Directory rename uses the legacy `DE_RENAME` guard, and parent-chain analysis trusts on-disk `..` entries. The code has to compensate for VFS rename API locking/reference conventions, making lock ordering and reference ownership important.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_rename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_unicode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_unicode.c

## Summary
Provides a static Unicode 5.0 simple/common case-folding table for msdosfs filename handling. The file is data-oriented: it defines source-to-folded 16-bit Unicode codepoint pairs for codepoints in the BMP and exports the number of table entries.

## Main Responsibilities
- Embed Unicode case folding data derived from Unicode 5.0 `CaseFolding.txt`.
- Cover simple/common folding mappings for Latin, Greek, Cyrillic, Armenian, Georgian, Coptic, fullwidth Latin, Roman numerals, and related BMP characters present in the table.
- Expose the table as `msdosfs_unicode_foldmap[]`.
- Expose `msdosfs_unicode_foldmap_entries` as the array element count.

## Key Interfaces
- `const u_int16_t msdosfs_unicode_foldmap[]`.
- `size_t msdosfs_unicode_foldmap_entries`.

## Risks
The table is frozen to Unicode 5.0-era data and only represents simple/common folding, not full case folding expansions. Consumers must interpret the flat array as key/value pairs; the exported entry count is the raw element count, not a count of mapping pairs unless callers divide by two. The table only covers 16-bit codepoints, so supplementary-plane Unicode folding is outside this file's scope.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_vfsops.c

## Summary
Implements NetBSD VFS-level operations for msdosfs: module registration, mount/update/root-mount handling, boot sector and BPB validation, mount control block initialization, FAT geometry setup, in-use map initialization, unmount, root lookup, statvfs, sync, and NFS file-handle conversion.

## Main Responsibilities
- Define the `msdosfs_vfsops` table and module attach/detach entry point.
- Register the msdosfs sysctl node.
- Normalize and apply mount options in `update_mp()`, including legacy argument compatibility, GMT offset handling, GEMDOS behavior, long-name/short-name policy, and name length reporting.
- Mount root from `root_device` with default msdosfs arguments.
- Implement `msdosfs_mount()` for argument retrieval, update mounts, device lookup, block-device permission checks, device open, `msdosfs_mountfs()` invocation, and statvfs metadata setup.
- Parse and validate FAT boot sector/BPB fields in `msdosfs_mountfs()`, including sector size, sectors per cluster, FAT size, FAT type, FAT32 FSInfo, GEMDOS transformations, cluster count, FAT block sizing, and max block size limits.
- Allocate and populate `struct msdosfsmount`, set mount flags/shifts/sizes, build `pm_inusemap` via `msdosfs_fillinusemap()`, and mark the block device mounted.
- Unmount by flushing vnodes, closing the device, destroying file-handle state, and freeing mount/FAT allocation structures.
- Return the root vnode with `msdosfs_root()`.
- Report capacity/free-space metadata through `msdosfs_statvfs()`.
- Sync dirty denodes and the device vnode through `msdosfs_sync()`.
- Convert between file handles and vnodes with `msdosfs_fhtovp()` and `msdosfs_vptofh()`.

## Key Interfaces
- `msdosfs_vfsops`.
- `msdosfs_mountroot(void)`.
- `msdosfs_mount(struct mount *, const char *, void *, size_t *)`.
- `msdosfs_mountfs(struct vnode *, struct mount *, struct lwp *, struct msdosfs_args *)`.
- `msdosfs_unmount(struct mount *, int)`.
- `msdosfs_root(struct mount *, int, struct vnode **)`.
- `msdosfs_statvfs(struct mount *, struct statvfs *)`.
- `msdosfs_sync(struct mount *, int, kauth_cred_t)`.
- `msdosfs_fhtovp(struct mount *, struct fid *, int, struct vnode **)`.
- `msdosfs_vptofh(struct vnode *, struct fid *, size_t *)`.
- `msdosfs_vget(struct mount *, ino_t, int, struct vnode **)`, currently unsupported.

## Risks
Mount validation is security- and stability-sensitive because malformed BPB fields drive shift counts, FAT sizing, cluster counts, and buffer sizes. The boot signature check is disabled for compatibility with real-world media, so later consistency checks carry more responsibility. Read-write upgrades depend on device permission checks and mount flag transitions. FSInfo validation is partial and may disable FSInfo use. `msdosfs_sync()` panics if a read-only mount is marked modified. NFS file handles rely on directory cluster/offset plus generation state maintained outside this file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_vnops.c

## Summary
Implements vnode operations for msdosfs regular files and directories. It handles create, close, access, getattr/setattr, read/write, metadata update, remove, mkdir/rmdir, readdir, bmap, strategy, advisory locks, pathconf, fsync, timestamp conversion, and the vnode operation dispatch table.

## Main Responsibilities
- Create regular files with `msdosfs_create()`, generating unique DOS aliases, initializing denode metadata, creating directory entries, and populating the name cache.
- Update access timestamps on close while files remain referenced.
- Enforce access with read-only filesystem checks and DOS readonly-bit-to-mode translation in `msdosfs_access()`.
- Fill Unix-style attributes in `msdosfs_getattr()`, including file IDs aligned with `readdir`, mount uid/gid, mode masks, FAT timestamps, archive bit projection, size, and block usage.
- Apply supported attributes in `msdosfs_setattr()`: size truncation/extension, atime/mtime, readonly bit from owner-write mode, and archive flag.
- Read regular files through UBC and directories through device-vnode buffer I/O in `msdosfs_read()`.
- Write regular files through UBC in `msdosfs_write()`, pre-extending FAT chains for contiguous allocation, zero-filling holes because FAT has no sparse files, enforcing the 32-bit FAT file size limit, flushing on sync writes, and truncating back on write failure.
- Persist denode metadata into directory entries with `msdosfs_update()`.
- Remove non-directories with `msdosfs_remove()`.
- Create directories with `msdosfs_mkdir()`, allocating one cluster, initializing `.` and `..`, writing it before linking from the parent, then creating the parent directory entry.
- Remove empty directories with `msdosfs_rmdir()`, rejecting `.` and `DE_RENAME` directories, deleting the parent entry, purging cache, and truncating the removed directory.
- Convert FAT directory entries to `struct dirent` records in `msdosfs_readdir()`, including synthetic root `.`/`..`, Win95 long-name assembly, short-name fallback, cookies, file IDs, and EOF reporting.
- Map file clusters to device blocks with `msdosfs_bmap()` and contiguous run discovery.
- Submit buffer I/O to the underlying device vnode in `msdosfs_strategy()`.
- Provide diagnostics, advisory locks, pathconf limits, fsync/cache sync, and timestamp conversion helpers.
- Define `msdosfs_vnodeop_entries` and `msdosfs_vnodeop_opv_desc`.

## Key Interfaces
- VOP handlers: `msdosfs_create`, `msdosfs_close`, `msdosfs_access`, `msdosfs_getattr`, `msdosfs_setattr`, `msdosfs_read`, `msdosfs_write`, `msdosfs_remove`, `msdosfs_mkdir`, `msdosfs_rmdir`, `msdosfs_readdir`, `msdosfs_bmap`, `msdosfs_strategy`, `msdosfs_print`, `msdosfs_advlock`, `msdosfs_pathconf`, and `msdosfs_fsync`.
- Metadata helpers: `msdosfs_update()` and `msdosfs_detimes()`.
- Operation vector exports: `msdosfs_vnodeop_p`, `msdosfs_vnodeop_entries`, and `msdosfs_vnodeop_opv_desc`.

## Risks
Regular-file I/O uses UBC while directory I/O uses the filesystem device vnode to avoid buffer-cache aliasing with directory metadata. Writes pre-extend files and must roll back on failure; any failure after FAT allocation can interact with truncation and metadata update paths. Directory creation writes the new directory cluster before linking it for crash-ordering reasons but the filesystem is still non-journaled. `msdosfs_update()` skips writing directory denodes and removed entries, relying on directory-entry update paths elsewhere. `readdir` long-name reconstruction depends on checksum continuity and falls back to short names when long-name entries are missing or corrupt.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfsmount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfsmount.h

## Summary
Defines msdosfs mount arguments, mount option flags, the in-kernel/makefs mount control block, FAT geometry macros, directory-entry address helpers, and VFS prototypes. It is the central shared header for msdosfs mount state and sector/cluster/block conversions.

## Main Responsibilities
- Define `struct msdosfs_args` for mount arguments, including versioned extensions for directory mask and GMT offset.
- Define user-visible and internal mount flags: short names, long names, ignoring Win95 entries, GEMDOS mode, versioned args, UTF-8 names, read-only, synchronous FAT updates, and FAT mirroring.
- Declare msdosfs malloc types under `_KERNEL`.
- Define `struct msdosfsmount`, holding mount/device identity, uid/gid/masks, timezone offset, BPB copy, FAT/root/cluster geometry, free-space state, FAT type parameters, current FAT, allocation bitmap, and flags.
- Provide FAT byte-offset macro `FATOFS()`.
- Provide mount conversion macro `VFSTOMSDOSFS()`.
- Define allocation bitmap unit size `N_INUSEBITS`.
- Alias BPB fields through `pm_*` macros.
- Convert between directory offsets, cluster numbers, filesystem sectors, kernel block numbers, and file offsets.
- Declare msdosfs VFS lifecycle functions and `VFS_PROTOS(msdosfs)`.

## Key Interfaces
- `struct msdosfs_args`.
- `struct msdosfsmount`.
- Mount flags `MSDOSFSMNT_*` and `MSDOSFS_FATMIRROR`.
- Conversion macros: `FATOFS`, `bptoep`, `de_bn2cn`, `de_cn2bn`, `de_bn2kb`, `de_kb2bn`, `de_cluster`, `de_clcount`, `de_blk`, `de_cn2off`, `de_bn2off`, `cntobn`, `roottobn`, and `detobn`.
- Prototypes: `msdosfs_init`, `msdosfs_reinit`, `msdosfs_done`, and kernel VFS prototypes.

## Risks
Many macros assume power-of-two sector and cluster sizes and valid shift relationships initialized by mount validation. Incorrect `pm_*` geometry can turn simple macros into invalid block numbers or offsets. `detobn()` maps non-root directory offsets only to the directory's starting cluster, so callers must already use FAT-chain mapping when offsets may span later clusters. The mount argument structure preserves compatibility fields, so version handling in callers must stay aligned with this header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfsmount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs.h

## Summary
Defines private kernel-facing NFS client macros, debug controls, NFS I/O daemon state, and prototypes for client metadata, buffer I/O, RPC, commit, cache, node-locking, and initialization routines.

## Main Responsibilities
- Provide default terminal printf delay constants for NFS user-visible wait messages.
- Define mount-version predicates `NFS_ISV3`, `NFS_ISV4`, and `NFS_ISV34`.
- Define conditional NFS debug categories and the `NFS_DPF` debug-print macro.
- Define `enum nfsiod_state` for async I/O daemon availability and creation state.
- Declare core NFS client functions for sizing, direct writes, buffered reads/writes, buffer invalidation, async I/O dispatch, RPC reads/writes/readdir/readdirplus/readlink, commit handling, mount fsinfo, hash/node lifecycle, node locks, attribute cache lookup, and nfsiod creation.

## Key Interfaces
- Macros: `NFS_TPRINTF_INITIAL_DELAY`, `NFS_TPRINTF_DELAY`, `NFS_ISV3`, `NFS_ISV4`, `NFS_ISV34`, and `NFS_DPF`.
- Debug bits under `NFS_DEBUG`: `NFS_DEBUG_ASYNCIO`, `NFS_DEBUG_WG`, and `NFS_DEBUG_RC`.
- `enum nfsiod_state`.
- Prototypes including `ncl_bioread`, `ncl_biowrite`, `ncl_asyncio`, `ncl_doio`, `ncl_readrpc`, `ncl_writerpc`, `ncl_readdirrpc`, `ncl_readdirplusrpc`, `ncl_commit`, `ncl_fsinfo`, `ncl_init`, and `ncl_uninit`.

## Risks
This header is compiled only for `_KERNEL` and assumes surrounding NFS types such as `struct nfsmount` and `struct nfsnode` are available from other headers. Version macros dereference `v_mount` and `VFSTONFS()` without local validation. Debug output is compiled away unless `NFS_DEBUG` is set, so side effects must never be embedded in `NFS_DPF` arguments.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs.h -->