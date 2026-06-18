# Group Research: group_454_freebsd_src_sources_os_bsd_freebsd_src_sys_ufs_ffs_fs_h_sources_os_b_8255e6c55cd4

Scope: `Docs/research_subset_a.md`  
Repository root: `/home/sansha/Github/learn_fs`  
Files read completely: 16

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/fs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/fs.h

## Purpose
Defines the core on-disk and in-memory layout contract for FreeBSD FFS/UFS: superblock locations, filesystem geometry, cylinder group metadata, allocation/addressing macros, feature flags, metadata checksum flags, snapshot sentinel blocks, soft-update journal record formats, and UFS suspension ioctls.

## Key Contents
- Superblock constants:
  - `SBLOCK_FLOPPY`, `SBLOCK_UFS1`, `SBLOCK_UFS2`, `SBLOCK_PIGGY`
  - `SBLOCKSEARCH`
  - `SBLOCKSIZE`
  - `UFS_STDSB`
- Superblock read/validation flags:
  - `UFS_NOHASHFAIL`, `UFS_NOWARNFAIL`, `UFS_NOMSG`, `UFS_NOCSUM`, `UFS_FSRONLY`, `UFS_ALTSBLK`
- Filesystem sizing/layout constants:
  - `MAXFRAG`, `MINBSIZE`, `MAXMNTLEN`, `MAXVOLLEN`, `FS_MAXCONTIG`, `MINFREE`, `FSMAXSNAP`
- Snapshot special block values:
  - `BLK_NOCOPY`
  - `BLK_SNAP`
- fsck command protocol:
  - `FFS_ADJ_REFCNT` through `FFS_ADJ_DEPTH`
  - `struct fsck_cmd`
  - `struct fsrecovery`
- Summary structures:
  - `struct csum`
  - `struct csum_total`
  - `struct fs_summary_info`
- Main FFS superblock:
  - `struct fs`
  - Preserves historical UFS1 fields, modern UFS2 fields, mount metadata, summary pointers, snapshot inode list, checksum state, flags, and geometry constants.
  - Compile-time assertion expects `sizeof(struct fs) == 1376`.
- Filesystem magic and format constants:
  - `FS_UFS1_MAGIC`, `FS_UFS2_MAGIC`, `FS_BAD_MAGIC`
  - `FS_42INODEFMT`, `FS_44INODEFMT`
- Filesystem feature flags:
  - `FS_UNCLEAN`, `FS_DOSOFTDEP`, `FS_NEEDSFSCK`, `FS_SUJ`, `FS_ACLS`, `FS_MULTILABEL`, `FS_GJOURNAL`, `FS_NFS4ACLS`, `FS_METACKHASH`, `FS_TRIM`
  - Future/unsupported feature bits are defined and cleared at mount via `FS_SUPPORTED`.
- Metadata checksum flags:
  - `CK_SUPERBLOCK`, `CK_CYLGRP`, `CK_INODE`, `CK_INDIR`, `CK_DIR`
- Buffer extended flags for metadata identity:
  - `BX_SUPERBLOCK`, `BX_CYLGRP`, `BX_INODE`, `BX_INDIR`, `BX_DIR`
- Cylinder group layout:
  - `CGSIZE(fs)`
  - `struct cg`
  - Access macros: `cg_inosused`, `cg_blksfree`, `cg_clustersfree`, `cg_clustersum`
- Address translation macros:
  - `fsbtodb`, `dbtofsb`
  - `cgbase`, `cgdata`, `cgmeta`, `cgdmin`, `cgimin`, `cgsblock`, `cgtod`, `cgstart`
  - `ino_to_cg`, `ino_to_fsba`, `ino_to_fsbo`
  - `dtog`, `dtogd`
- Block/fragments arithmetic:
  - `blkoff`, `fragoff`, `lblktosize`, `lfragtosize`, `lblkno`, `numfrags`, `blkroundup`, `fragroundup`, `fragstoblks`, `blkstofrags`, `fragnum`, `blknum`
- File block size helpers:
  - `blksize(fs, ip, lbn)`
  - `sblksize(fs, size, lbn)`
- Indirect block helpers:
  - `NINDIR(fs)`
  - `lbn_level()`
  - `lbn_offset()`
- Inode block helpers:
  - `INOPB(fs)`
  - `INOPF(fs)`
- Soft-update journal record definitions:
  - Journal op types: `JOP_ADDREF`, `JOP_REMREF`, `JOP_NEWBLK`, `JOP_FREEBLK`, `JOP_MVREF`, `JOP_TRUNC`, `JOP_SYNC`
  - `struct jsegrec`, `jrefrec`, `jmvrec`, `jblkrec`, `jtrncrec`
  - `union jrec`
  - Compile-time assertions keep each journal record at `JREC_SIZE == 32`.
- UFS write suspension ioctls:
  - `UFSSUSPEND`
  - `UFSRESUME`

## Interactions
- Included by UFS/FFS implementation files that need filesystem geometry, metadata layout, journal record formats, and feature flags.
- Depends on `ufs/ufs/dinode.h` for address/time/inode constants.
- `ufs_bmap.c` relies on block pointer semantics and indirect addressing.
- `ufs_gjournal.c` uses cylinder group and superblock counters.
- Soft-update journaling code uses the `jrec` formats declared here.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/softdep.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/softdep.h

## Purpose
Defines the private soft updates and soft-update journaling dependency model used by FFS. This header is a structural map of metadata dependency objects, state flags, work queues, journaling dependencies, hash tables, and per-mount softdep state.

## Key Contents
- Dependency state flags:
  - `ATTACHED`, `UNDONE`, `COMPLETE`, `DEPCOMPLETE`
  - Directory-specific flags: `MKDIR_PARENT`, `MKDIR_BODY`, `RMDIR`, `DIRCHG`
  - Lifecycle/write flags: `GOINGAWAY`, `IOSTARTED`, `DELAYEDFREE`, `NEWBLOCK`, `INPROGRESS`, `ONWORKLIST`, `IOWAITING`, `ONDEPLIST`, `WRITESUCCEEDED`
  - UFS/journal flags: `UFS1FMT`, `EXTDATA`
  - Unlinked-inode tracking: `UNLINKED`, `UNLINKNEXT`, `UNLINKPREV`, `UNLINKONLIST`, `UNLINKLINKS`
  - Completion mask: `ALLCOMPLETE`
- Dependency type identifiers:
  - `D_PAGEDEP`, `D_INODEDEP`, `D_BMSAFEMAP`, `D_NEWBLK`, `D_ALLOCDIRECT`, `D_INDIRDEP`, `D_ALLOCINDIR`
  - Freeing/removal types: `D_FREEFRAG`, `D_FREEBLKS`, `D_FREEFILE`, `D_FREEWORK`, `D_FREEDEP`
  - Directory types: `D_DIRADD`, `D_MKDIR`, `D_DIRREM`, `D_NEWDIRBLK`
  - Journal types: `D_JADDREF`, `D_JREMREF`, `D_JMVREF`, `D_JNEWBLK`, `D_JFREEBLK`, `D_JFREEFRAG`, `D_JSEG`, `D_JSEGDEP`, `D_JTRUNC`, `D_JFSYNC`
  - `D_SBDEP`, `D_SENTINEL`
- Common work item:
  - `struct worklist`
  - Must be first field in dependency structures that participate in work queues.
  - Carries mount pointer, type, state, global list linkage, and invariant debug provenance.
- Type conversion macros:
  - `WK_PAGEDEP`, `WK_INODEDEP`, `WK_BMSAFEMAP`, `WK_NEWBLK`, etc.
- Dependency list heads:
  - Defines many `LIST_HEAD`/`TAILQ_HEAD` collections for directory, inode, block, journal, and free-work dependencies.
- Core dependency structures:
  - `struct pagedep`: tracks directory page dependencies, pending adds/removes, move-reference journal records, and new directory blocks.
  - `struct inodedep`: tracks dependencies tied to an inode write, including delayed operations, allocation updates, link changes, unlinked list state, and rollback snapshots.
  - `struct bmsafemap`: tracks dependencies waiting on a cylinder group bitmap write.
  - `struct newblk`: generic newly allocated block dependency.
  - `struct allocdirect`: direct inode block pointer allocation dependency.
  - `struct indirdep`: indirect block dependency manager with safe copy/live copy handling.
  - `struct allocindir`: indirect pointer allocation dependency.
  - `union allblk`: allocation sizing union for `newblk`, `allocdirect`, and `allocindir`.
  - `struct freefrag`: delayed fragment free after fragment replacement.
  - `struct freeblks`: root object for truncation/freeing file block trees.
  - `struct freework`: child work items for freeing direct/indirect block trees.
  - `struct freedep`: bitmap-write completion dependency for frees.
  - `struct freefile`: delayed inode free after zero-link inode is safely written.
  - `struct diradd`, `struct mkdir`, `struct dirrem`, `struct newdirblk`: directory mutation dependency records.
- Journal dependency structures:
  - `struct inoref`: common reference operation payload.
  - `struct jaddref`: journals new references.
  - `struct jremref`: journals removed references.
  - `struct jmvref`: journals directory entry offset movement.
  - `struct jnewblk`: journals newly allocated blocks/fragments.
  - `struct jblkdep`, `struct jfreeblk`, `struct jfreefrag`: journal block-free dependencies.
  - `struct jtrunc`: journals truncation intent.
  - `struct jfsync`: journals fsync completion.
  - `struct jsegdep`: reference to a written journal segment.
  - `struct jseg`: journal segment write state.
  - `struct jblocks` and `struct jextent`: journal extent allocator and sequence tracking.
- Superblock dependency:
  - `struct sbdep`: tracks superblock writes for the soft-update journal unlinked inode list head.
- Hash and per-mount structures:
  - Hash heads for `pagedep`, `inodedep`, `newblk`, `bmsafemap`, and indirect freework.
  - `struct mount_softdeps`: all per-filesystem softdep state, including locks, pending work queues, journal queues, dirty cylinder groups, unlinked inode list, hash tables, counters, flush thread state, and per-type dependency lists.
- Flush thread flags:
  - `FLUSH_EXIT`, `FLUSH_CLEANUP`, `FLUSH_STARTING`, `FLUSH_RC_ACTIVE`, `FLUSH_DI_ACTIVE`
- Compatibility macros:
  - Maps old `ufsmount` field names to `um_softdep->sd_*` fields.

## Interactions
- Consumed by the FFS soft updates implementation.
- Coupled to UFS directory, inode, cylinder group, block allocation, truncation, and journaling code.
- Structures mirror journal record formats declared in `ffs/fs.h`.
- `ufs_extern.h` exposes selected softdep setup/revert functions used by UFS directory and vnode operations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/softdep.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/acl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/acl.h

## Purpose
Declares UFS-specific ACL entry points for kernel builds, including POSIX.1e ACL vnode operations and internal NFSv4 ACL helpers.

## Key Contents
- Forward declaration:
  - `struct inode`
- Internal NFSv4 ACL helpers:
  - `ufs_getacl_nfs4_internal(struct vnode *, struct acl *, struct thread *)`
  - `ufs_setacl_nfs4_internal(struct vnode *, struct acl *, struct thread *)`
- POSIX.1e synchronization helpers:
  - `ufs_sync_acl_from_inode(struct inode *, struct acl *)`
  - `ufs_sync_inode_from_acl(struct acl *, struct inode *)`
- VOP ACL entry points:
  - `ufs_getacl`
  - `ufs_setacl`
  - `ufs_aclcheck`

## Interactions
- Implemented in `ufs_acl.c`.
- Depends on UFS extended attributes for ACL storage.
- Bridges ACL state with inode mode bits.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/dinode.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/dinode.h

## Purpose
Defines the UFS on-disk inode formats and associated constants for UFS1 and UFS2.

## Key Contents
- Special inode numbers:
  - `UFS_ROOTINO` is inode 2.
  - `UFS_WINO` is inode 1, used as the whiteout placeholder.
- Core on-disk types:
  - `ufs1_daddr_t`
  - `ufs2_daddr_t`
  - `ufs_lbn_t`
  - `ufs_time_t`
- Mode and permission bits:
  - `IEXEC`, `IWRITE`, `IREAD`, `ISVTX`, `ISGID`, `ISUID`
- File type bits:
  - `IFMT`, `IFIFO`, `IFCHR`, `IFDIR`, `IFBLK`, `IFREG`, `IFLNK`, `IFSOCK`, `IFWHT`
- Block pointer constants:
  - `UFS_NXADDR`
  - `UFS_NDADDR`
  - `UFS_NIADDR`
- `struct ufs2_dinode`:
  - 64-bit size/block/time fields.
  - UID/GID, mode, link count, flags, generation, block size.
  - Birth time and nanosecond timestamps.
  - External attribute blocks via `di_extb`.
  - Direct/indirect block arrays or embedded short symlink union.
  - `di_modrev`, SUJ freelink or directory depth, inode checksum.
- `struct ufs1_dinode`:
  - Legacy UFS1 layout with 32-bit disk block addresses and timestamp seconds.
  - Direct/indirect block arrays or embedded short symlink union.
  - UID/GID, flags, generation, block count, `di_modrev`.
- Overlay:
  - `di_rdev` maps device number onto first direct block.
- Limits/unions:
  - `UFS_LINK_MAX`
  - `union dinode`
  - `union dinodep`

## Interactions
- Included by `inode.h` for in-core inode access.
- Included by `ffs/fs.h` for filesystem geometry and block/inode macros.
- The `DIP`/`DIP_SET` macros in `inode.h` abstract over UFS1 vs UFS2 fields.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/dir.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/dir.h

## Purpose
Defines UFS directory entry format, directory block sizing, record sizing macros, file type conversions, and templates for `.` / `..` initialization.

## Key Contents
- Directory offset type:
  - `doff_t` as `int32_t`
  - `MAXDIRSIZE`
- Directory block and name limits:
  - `DIRBLKSIZ` equals `DEV_BSIZE`
  - `UFS_MAXNAMLEN` is 255
- `struct direct`:
  - `d_ino`, `d_reclen`, `d_type`, `d_namlen`, `d_name`
- Directory file type values:
  - `DT_UNKNOWN`, `DT_FIFO`, `DT_CHR`, `DT_DIR`, `DT_BLK`, `DT_REG`, `DT_LNK`, `DT_SOCK`, `DT_WHT`
- Conversion macros:
  - `IFTODT(mode)`
  - `DTTOIF(dirtype)`
- Directory record sizing:
  - `DIR_ROUNDUP`
  - `DIRECTSIZ(namlen)`
  - `DIRSIZ(oldfmt, dp)`, with little-endian compatibility for old directory format.
  - `OLDDIRFMT`, `NEWDIRFMT`
- Directory templates:
  - `struct dirtemplate`
  - `struct odirtemplate`

## Interactions
- Used by directory lookup, insertion, deletion, and dirhash code.
- `ufs_dirhash.c` uses `DIRSIZ`, `DIRBLKSIZ`, and `struct direct` heavily.
- ACL/extattr code includes it because those paths interact with UFS vnode/inode directory support.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/dirhash.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/dirhash.h

## Purpose
Declares the optional UFS directory hash cache used to speed up operations on large directories and maintain free-space hints.

## Key Contents
- Hash slot sentinels:
  - `DIRHASH_EMPTY`
  - `DIRHASH_DEL`
- Alignment/stat constants:
  - `DIRALIGN`
  - `DH_NFSTATS`
- Recycling score policy:
  - `DH_SCOREINIT`
  - `DH_SCOREMAX`
- Two-level hash table geometry:
  - `DH_BLKOFFSHIFT`
  - `DH_NBLKOFF`
  - `DH_BLKOFFMASK`
  - `DH_ENTRY(dh, slot)`
- `struct dirhash`:
  - `sx` lock and refcount.
  - Two-level hash array of directory offsets.
  - Hash size/usage/memory counters.
  - Per-directory-block free-space summaries.
  - `dh_firstfree[]` index by free-space bucket.
  - Sequential lookup hint `dh_seqoff`.
  - LRU/LFU hybrid score and global list linkage.
- Function declarations:
  - Lifecycle: `ufsdirhash_init`, `ufsdirhash_uninit`, `ufsdirhash_free`
  - Build/lookup: `ufsdirhash_build`, `ufsdirhash_lookup`
  - Free-space helpers: `ufsdirhash_findfree`, `ufsdirhash_enduseful`
  - Mutation hooks: `ufsdirhash_newblk`, `ufsdirhash_add`, `ufsdirhash_remove`, `ufsdirhash_move`, `ufsdirhash_dirtrunc`
  - Debug checking: `ufsdirhash_checkblock`

## Interactions
- Implemented in `ufs_dirhash.c`.
- Referenced by `struct inode` as `i_dirhash`.
- Used by directory lookup and mutation paths to avoid linear scans on large directories.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/dirhash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/extattr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/extattr.h

## Purpose
Defines UFS extended attribute constants, file/header formats, in-memory per-mount attribute registration, and kernel entry points for extended attribute control and vnode operations.

## Key Contents
- File-format constants:
  - `UFS_EXTATTR_MAGIC`
  - `UFS_EXTATTR_VERSION`
  - `UFS_EXTATTR_MAXEXTATTRNAME`
- Autostart directory names:
  - `.attribute`
  - `system`
  - `user`
- Attribute flags and permissions:
  - `UFS_EXTATTR_ATTR_FLAG_INUSE`
  - `UFS_EXTATTR_PERM_KERNEL`, `ROOT`, `OWNER`, `ANYONE`
- Per-mount flags:
  - `UFS_EXTATTR_UEPM_INITIALIZED`
  - `UFS_EXTATTR_UEPM_STARTED`
- Control commands:
  - `UFS_EXTATTR_CMD_START`
  - `UFS_EXTATTR_CMD_STOP`
  - `UFS_EXTATTR_CMD_ENABLE`
  - `UFS_EXTATTR_CMD_DISABLE`
- Backing-file metadata:
  - `struct ufs_extattr_fileheader`
  - `struct ufs_extattr_header`
- Native extended attribute record layout:
  - `struct extattr`
  - `EXTATTR_NEXT`
  - `EXTATTR_CONTENT`
  - `EXTATTR_CONTENT_SIZE`
  - `EXTATTR_BASE_LENGTH`
- Registered backing attribute entry:
  - `struct ufs_extattr_list_entry`
- Per-mount extended attribute state:
  - `struct ufs_extattr_per_mount`
  - Contains `sx` lock, list of enabled attributes, credential, and flags.
- Kernel declarations:
  - `ufs_extattr_uepm_init`, `ufs_extattr_uepm_destroy`
  - `ufs_extattr_start`, `ufs_extattr_autostart`, `ufs_extattr_stop`
  - `ufs_extattrctl`
  - `ufs_getextattr`, `ufs_deleteextattr`, `ufs_setextattr`
  - `ufs_extattr_vnode_inactive`

## Interactions
- Implemented in `ufs_extattr.c`.
- ACL implementation stores POSIX.1e and NFSv4 ACLs through extended attributes.
- UFS1 uses backing files; UFS2 has native extended attribute support noted in implementation comments.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/extattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/gjournal.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/gjournal.h

## Purpose
Declares the UFS hooks used by GEOM journaling support.

## Key Contents
- `ufs_gjournal_orphan(struct vnode *fvp)`
- `ufs_gjournal_close(struct vnode *vp)`

## Interactions
- Implemented in `ufs_gjournal.c`.
- Updates UFS unreferenced inode counters when gjournal tracks orphaned/deleted vnodes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/gjournal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/inode.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/inode.h

## Purpose
Defines the UFS in-core inode structure and helper macros for vnode conversion, dinode field access, inode flags, lazy timestamp/update behavior, and UFS1/UFS2 abstraction.

## Key Contents
- `struct iown_tracker` under `DIAGNOSTIC`:
  - Tracks ownership and stack traces for inode directory lookup side-effect fields.
- `struct inode`:
  - Vnode/mount identity: `i_vnode`, `i_ump`.
  - Quotas: `i_dquot[MAXQUOTAS]`.
  - Union for `i_dirhash` or snapshot block list.
  - On-disk dinode pointer union `i_dp`.
  - Inode number, flags, effective link count.
  - Directory lookup side-effect fields: `i_count`, `i_endoff`, `i_diroff`, `i_offset`.
  - Cluster write tracking.
  - Extended attribute transaction fields: `i_ea_area`, `i_ea_len`, `i_ea_error`, `i_ea_refs`.
  - Cached dinode fields: `i_size`, `i_gen`, `i_flags`, `i_uid`, `i_gid`, `i_nlink`, `i_mode`.
- Inode flags:
  - Timestamp/update: `IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, `IN_MODIFIED`
  - Sync/lazy flags: `IN_NEEDSYNC`, `IN_LAZYMOD`, `IN_LAZYACCESS`
  - Extended attributes: `IN_EA_LOCKED`, `IN_EA_LOCKWAIT`
  - Journaling/truncation: `IN_TRUNCATED`
  - Format/state: `IN_UFS2`, `IN_IBLKDATA`, `IN_SIZEMOD`, `IN_ENDOFF`
- Flag helpers:
  - `UFS_INODE_SET_MODE`
  - `UFS_INODE_SET_FLAG`
  - `UFS_INODE_SET_FLAG_SHARED`
- Field aliases:
  - `i_dirhash`, `i_snapblklist`, `i_din1`, `i_din2`
- Mount/device/filesystem conversion macros:
  - `ITOUMP`, `ITODEV`, `ITODEVVP`, `ITOFS`, `ITOVFS`
- Format helpers:
  - `I_IS_UFS1`
  - `I_IS_UFS2`
- Dinode field access:
  - `DIP(ip, field)`
  - `DIP_SET(ip, field, val)`
  - `DIP_SET_NLINK`
- Snapshot and vnode helpers:
  - `IS_SNAPSHOT`
  - `IS_UFS`
  - `VTOI`, `VTOI_SMR`, `ITOV`
- Logical block path:
  - `struct indir`
- Softdep mount predicates:
  - `MOUNTEDSOFTDEP`, `DOINGSOFTDEP`
  - `MOUNTEDSUJ`, `DOINGSUJ`
- File handle overlay:
  - `struct ufid`
- Diagnostic wrappers for directory lookup side-effect fields:
  - `I_OFFSET`, `SET_I_OFFSET`
  - `I_COUNT`, `SET_I_COUNT`
  - `I_ENDOFF`, `SET_I_ENDOFF`

## Interactions
- Central in-core object used by UFS vnode operations, block mapping, ACLs, extattrs, quotas, dirhash, snapshots, and journaling.
- Includes `dinode.h`, `buf.h`, `seqc.h`, and queue/lock headers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/quota.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/quota.h

## Purpose
Defines UFS quota constants, on-disk quota formats, quotactl commands, kernel `dquot` structure, quota locking helpers, and quota function declarations.

## Key Contents
- Grace period defaults:
  - `MAX_IQ_TIME`
  - `MAX_DQ_TIME`
- Quota types:
  - `MAXQUOTAS`
  - `USRQUOTA`
  - `GRPQUOTA`
- Default quota file names:
  - `INITQFNAMES`
  - `QUOTAFILENAME`
  - `QUOTAGROUP`
- `quotactl` command composition:
  - `SUBCMDMASK`, `SUBCMDSHIFT`, `QCMD`
  - `Q_QUOTAON`, `Q_QUOTAOFF`
  - 32-bit commands: `Q_GETQUOTA32`, `Q_SETQUOTA32`, `Q_SETUSE32`
  - 64-bit commands: `Q_GETQUOTA`, `Q_SETQUOTA`, `Q_SETUSE`
  - `Q_SYNC`, `Q_GETQUOTASIZE`
- On-disk quota records:
  - `struct dqblk32`
  - `struct dqblk64`
  - `dqblk` alias to `dqblk64`
- 64-bit quota file header:
  - `Q_DQHDR64_MAGIC`
  - `Q_DQHDR64_VERSION`
  - `struct dqhdr64`
- Kernel `struct dquot`:
  - Hash/free-list linkage.
  - Mutex, flags, type, refcount, id, owning `ufsmount`.
  - Embedded `struct dqblk64`.
- Dquot flags:
  - `DQ_LOCK`, `DQ_WANT`, `DQ_MOD`, `DQ_FAKE`, `DQ_BLKS`, `DQ_INODS`
- Field aliases:
  - `dq_bhardlimit`, `dq_bsoftlimit`, `dq_curblocks`, etc.
- Helpers:
  - `NODQUOT`
  - `FORCE`, `CHOWN`
  - `DQREF`
  - `DQI_LOCK`, `DQI_UNLOCK`, `DQI_WAIT`, `DQI_WAKEUP`
- Kernel declarations:
  - Accounting: `chkdq`, `chkiq`, `getinoquota`
  - Lifecycle: `dqinit`, `dquninit`, `dqrele`
  - Sync/control: `qsync`, `qsyncvp`, `quotaon`, `quotaoff`, `ufs_quotactl`
  - Quota get/set variants.
  - Soft updates quota hooks under `SOFTUPDATES`.
- Userland declaration:
  - `quotactl(const char *, int, int, void *)`

## Interactions
- Included by `inode.h` and UFS implementation files because `struct inode` contains dquot pointers.
- Used by allocation, truncation, write, and ownership-change paths to enforce quota limits.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_acl.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_acl.c

## Purpose
Implements UFS ACL vnode operations and internal helpers for POSIX.1e and NFSv4 ACLs. The implementation stores nontrivial ACL state in UFS extended attributes and synchronizes relevant permission bits with the inode mode.

## Key Contents
Compiled under `#ifdef UFS_ACL`.

- Feature registration:
  - `FEATURE(ufs_acl, "ACL support for UFS")`
- POSIX.1e synchronization:
  - `ufs_sync_acl_from_inode`
    - Updates ACL entries from inode mode.
    - Updates `ACL_USER_OBJ`, `ACL_OTHER`, and either `ACL_MASK` or `ACL_GROUP_OBJ`.
  - `ufs_sync_inode_from_acl`
    - Computes mode bits from ACL and writes both in-core inode mode and dinode mode.
- NFSv4 ACL get path:
  - `ufs_getacl_nfs4_internal`
    - Reads NFSv4 ACL from extended attribute.
    - If absent, synthesizes trivial ACL from inode mode and owner.
    - Validates exact ACL size and calls `acl_nfs4_check`.
  - `ufs_getacl_nfs4`
    - Requires `MNT_NFS4ACLS`.
    - Requires `VREAD_ACL`.
- POSIX.1e ACL get path:
  - `ufs_get_oldacl`
    - Reads access/default ACL from extended attributes.
    - Validates stored `oldacl` size.
  - `ufs_getacl_posix1e`
    - Requires `MNT_ACLS`.
    - For absent access ACL, synthesizes minimal user/group/other ACL.
    - For absent default ACL, returns an empty ACL.
    - Converts old ACL storage format into `struct acl`.
    - Synchronizes access ACL from inode mode.
  - `ufs_getacl`
    - Dispatches to NFSv4 or POSIX.1e based on ACL type and mount flags.
- NFSv4 ACL set path:
  - `ufs_setacl_nfs4_internal`
    - Removes trivial ACL extended attribute or writes nontrivial ACL.
    - Maps `ENOATTR` to `EOPNOTSUPP`.
    - Updates mode from ACL, marks inode changed, posts vnode note, calls `UFS_UPDATE`.
  - `ufs_setacl_nfs4`
    - Requires `MNT_NFS4ACLS`, writable mount, non-null ACL.
    - Validates with `VOP_ACLCHECK`.
    - Rejects immutable/append-only inodes.
    - Requires `VWRITE_ACL`.
    - Reserves ACL entry headroom for chmod canonicalization.
- POSIX.1e ACL set/delete path:
  - `ufs_setacl_posix1e`
    - Requires `MNT_ACLS`.
    - Validates set ACLs with `VOP_ACLCHECK`.
    - Allows deletion only for default ACLs on directories.
    - Requires writable mount, non-immutable/non-append inode, and `VADMIN`.
    - Stores access/default ACLs via extended attributes.
    - Removes default ACL if requested.
    - Updates inode mode only after access ACL storage succeeds.
  - `ufs_setacl`
    - Dispatches to NFSv4 or POSIX.1e.
- ACL validation:
  - `ufs_aclcheck_nfs4`
    - Requires `MNT_NFS4ACLS`.
    - Enforces chmod headroom.
    - Calls `acl_nfs4_check`.
  - `ufs_aclcheck_posix1e`
    - Requires `MNT_ACLS`.
    - Allows access ACLs for all objects, default ACLs only for directories.
    - Enforces `OLDACL_MAX_ENTRIES`.
    - Calls `acl_posix1e_check`.
  - `ufs_aclcheck`
    - Handles mount validation and dispatch.

## Interactions
- Relies on `vn_extattr_get`, `vn_extattr_set`, and `vn_extattr_rm`.
- Uses inode mode helpers from `inode.h`.
- Depends on mount flags `MNT_ACLS` and `MNT_NFS4ACLS`.
- Extended attribute absence is sometimes interpreted as “ACL not present” and sometimes mapped to “operation not supported,” depending on path.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_bmap.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_bmap.c

## Purpose
Implements logical-to-physical block mapping for UFS, including direct and indirect block traversal, run-length clustering hints, sparse block handling, snapshot special cases, indirect logical block path construction, and `SEEK_DATA` support.

## Key Contents
- Sysctl:
  - `vfs.ufs.bmap_use_unmapped`
  - Controls whether UFS bmap may use unmapped buffers for indirect reads.
- Public bmap entry:
  - `ufs_bmap`
    - Supplies backing device bufobj if requested.
    - Uses `ufs_bmaparray` to translate logical block number to disk block number.
- Indirect block read helper:
  - `readindir`
    - Gets/caches indirect block buffers.
    - Can use `GB_UNMAPPED` for UFS2 when enabled.
    - Issues BIO read manually when buffer is not cached.
    - Updates RACCT and thread block I/O statistics.
- Unmapped buffer helpers:
  - `ufs_bm_sf_get`
  - `ufs_bm_sf_put`
    - Temporarily map buffer pages via `sf_buf` while CPU-pinned.
- Main mapping routine:
  - `ufs_bmaparray`
    - Calls `ufs_getlbns` to compute indirect path.
    - Handles direct blocks, UFS2 external attribute blocks, and indirect blocks.
    - Returns `-1` for holes unless snapshot semantics map them differently.
    - Treats snapshot sentinel blocks in range `1..um_seqinc` as zero-fill.
    - Validates indirect addresses via `UFS_CHECK_BLKNO`.
    - Calculates forward/backward contiguous run lengths for clustering.
    - Handles both UFS1 32-bit and UFS2 64-bit block pointer arrays.
- Logical block count helper:
  - `lbn_count`
    - Computes number of data blocks addressed by an indirect level.
- `SEEK_DATA` support:
  - `ufs_bmap_seekdata`
    - Rejects non-regular files and snapshots.
    - Validates requested offset against file size.
    - Calls `vnode_pager_clean_sync` so delayed dirty pages are reflected in block allocation.
    - Scans direct and indirect pointers for the next allocated data block.
    - Returns `ENXIO` if no data exists at or after the requested offset.
- Indirect path construction:
  - `ufs_getlbns`
    - Converts data or metadata logical block number into an array of `struct indir` entries.
    - Handles direct blocks, single/double/triple indirection, and negative metadata logical block numbers.
    - Returns `EFBIG` for out-of-range logical blocks.

## Interactions
- Uses `struct inode`, `DIP`, `I_IS_UFS1`, `I_IS_UFS2`, `IS_SNAPSHOT`.
- Depends on mount/ufsmount block-size helpers such as `MNINDIR`, `blkptrtodb`, `is_sequential`.
- Exposed through `ufs_extern.h`.
- Used by vnode paging, clustering, read/write, and seek-data paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_dirhash.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_dirhash.c

## Purpose
Implements optional hash-based lookup and free-space indexing for large UFS directories. It caches name-to-directory-offset mappings, maintains per-directory-block free-space summaries, and recycles hashes under memory pressure.

## Key Contents
Compiled under `#ifdef UFS_DIRHASH`.

- Sysctls:
  - `vfs.ufs.dirhash_minsize`
  - `vfs.ufs.dirhash_maxmem`
  - `vfs.ufs.dirhash_mem`
  - `vfs.ufs.dirhash_docheck`
  - `vfs.ufs.dirhash_lowmemcount`
  - `vfs.ufs.dirhash_reclaimpercent`
- Allocation and global state:
  - `M_DIRHASH`
  - UMA zone `ufsdirhash_zone`
  - Global list `ufsdirhash_list`
  - Global mutex `ufsdirhash_mtx`
- Locking/refcount model:
  - Directory hash pointer belongs to inode and is protected by vnode exclusive lock or vnode interlock with shared vnode lock.
  - Hash contents protected by `dh_lock`.
  - Global list and memory counters protected by `ufsdirhash_mtx`.
  - `ufsdirhash_hold`, `ufsdirhash_drop`, `ufsdirhash_release`.
- Create/acquire/free:
  - `ufsdirhash_create`
    - Creates new hash or locks existing hash.
    - Handles races with recycling.
  - `ufsdirhash_acquire`
    - Gets exclusive lock for mutation paths.
    - Frees recycled hash when encountered.
  - `ufsdirhash_free`
  - `ufsdirhash_free_locked`
- Build:
  - `ufsdirhash_build`
    - Skips small directories, old format directories, and zero-link inodes.
    - Allocates hash slots at 150% of maximum possible entries for current directory size.
    - Allocates block free-space summary storage.
    - Reads directory blocks and inserts live entries.
    - Fails back to linear lookup on allocation or corruption failures.
    - Inserts successfully built hash on global LRU/LFU list.
- Lookup:
  - `ufsdirhash_lookup`
    - Searches linear-probing hash chain.
    - Reads target directory buffers as needed.
    - Verifies entries by name and length.
    - Maintains sequential lookup hint `dh_seqoff`.
    - Updates cache score and last-used time.
    - Returns `ENOENT` for miss or `EJUSTRETURN` to request linear fallback.
- Free-space search:
  - `ufsdirhash_findfree`
    - Uses `dh_firstfree[]` to find a directory block with enough free space.
    - Reads the block to identify the exact compaction range.
  - `ufsdirhash_enduseful`
    - Finds trailing fully-free directory blocks suitable for truncation.
- Mutation hooks:
  - `ufsdirhash_add`
    - Inserts new entry and updates free-space stats.
    - Frees hash if utilization exceeds 75%.
  - `ufsdirhash_remove`
    - Removes entry and updates free-space stats.
  - `ufsdirhash_move`
    - Changes cached offset after directory compaction.
  - `ufsdirhash_newblk`
    - Accounts for one newly appended directory block.
    - Frees hash if preallocated summary space is exhausted.
  - `ufsdirhash_dirtrunc`
    - Handles directory shrink.
    - Frees hash if directory becomes much smaller.
- Debug checker:
  - `ufsdirhash_checkblock`
    - Optional runtime consistency check against actual directory block contents.
- Internal helpers:
  - `ufsdirhash_hash`
    - FNV hash over name plus hash object address salt.
  - `ufsdirhash_adjfree`
    - Updates per-block free-space bucket state.
  - `ufsdirhash_findslot`
    - Finds exact name/offset slot or panics.
  - `ufsdirhash_delslot`
    - Handles linear-probing deletion and trailing `DIRHASH_DEL` cleanup.
  - `ufsdirhash_getprev`
    - Finds previous directory entry within a block.
  - `ufsdirhash_destroy`
    - Detaches and frees hash backing memory.
  - `ufsdirhash_recycle`
    - Frees low-score hashes until memory target is met.
  - `ufsdirhash_lowmem`
    - VM low-memory callback.
  - `ufsdirhash_set_reclaimpercent`
    - Validates reclaim percentage.
- Lifecycle:
  - `ufsdirhash_init`
    - Sizes max memory from `hibufspace`, creates UMA zone, initializes mutex/list, registers low-memory event.
  - `ufsdirhash_uninit`
    - Requires global list empty, destroys UMA zone and mutex.

## Interactions
- `struct inode` stores `i_dirhash`.
- Directory lookup and mutation paths call build/lookup/add/remove/move/truncate hooks.
- Depends on `dir.h` directory record invariants and `ufs_extern.h` block access.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_dirhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_extattr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_extattr.c

## Purpose
Implements UFS extended attribute support for the backing-file based UFS1 extended attribute system. It manages per-mount EA lifecycle, optional autostart, enabling/disabling named attributes, and vnode operations for get/set/delete.

## Key Contents
Compiled under `#ifdef UFS_EXTATTR`.

- Feature registration:
  - `FEATURE(ufs_extattr, "ufs extended attribute support")`
- Sysctl:
  - `debug.ufs_extattr_sync`
  - Forces synchronous writes for attribute metadata/content when enabled.
- Per-mount lock helpers:
  - `ufs_extattr_uepm_lock`
  - `ufs_extattr_uepm_unlock`
- Attribute validation/search:
  - `ufs_extattr_valid_attrname`
    - Rejects null and empty names.
  - `ufs_extattr_find_attr`
    - Finds enabled backing attribute by namespace/name under mount EA lock.
- Per-mount lifecycle:
  - `ufs_extattr_uepm_init`
    - Initializes list, lock, and `INITIALIZED` flag.
  - `ufs_extattr_uepm_destroy`
    - Requires initialized but not started state.
  - `ufs_extattr_start`
  - `ufs_extattr_start_locked`
    - Sets `STARTED` and stores held credential.
  - `ufs_extattr_stop`
    - Disables all enabled attributes, clears `STARTED`, releases credential.
- Optional autostart under `UFS_EXTATTR_AUTOSTART`:
  - `ufs_extattr_lookup`
    - Performs UFS lookup for a name under a directory.
  - `ufs_extattr_iterate_directory`
    - Iterates attribute backing files in a namespace directory and enables regular files.
  - `ufs_extattr_autostart`
  - `ufs_extattr_autostart_locked`
    - Applies only to UFS1.
    - Looks for `.attribute/system` and `.attribute/user` below filesystem root.
    - Starts EA support and enables found backing files.
- Enable/disable:
  - `ufs_extattr_enable_with_open`
    - Opens backing vnode read/write, increments writecount, references vnode, unlocks it, then enables.
  - `ufs_extattr_enable`
    - Validates backing vnode type and started state.
    - Ensures no duplicate attribute.
    - Reads and validates `ufs_extattr_fileheader` magic/version.
    - Adds enabled attribute entry to per-mount list.
  - `ufs_extattr_disable`
    - Removes enabled attribute entry and closes backing vnode.
- Control API:
  - `ufs_extattrctl`
    - Requires `PRIV_UFS_EXTATTRCTL`.
    - Rejects jailed privileged callers via `priv_check`.
    - Supports only UFS1 because UFS2 uses native extended attributes.
    - Handles start, stop, enable, disable commands.
- Vnode operations:
  - `ufs_getextattr`
    - Locks per-mount EA state and calls `ufs_extattr_get`.
  - `ufs_setextattr`
    - Rejects null `uio` delete legacy behavior.
    - Calls `ufs_extattr_set`.
  - `ufs_deleteextattr`
    - Calls `ufs_extattr_rm`.
- Attribute record get:
  - `ufs_extattr_get`
    - Requires started state and non-empty name.
    - Checks extattr read credentials.
    - Finds backing attribute.
    - Allows only offset 0.
    - Computes backing-file offset as file header plus inode-indexed fixed-size record.
    - Reads per-inode `ufs_extattr_header`.
    - Requires `INUSE` and matching inode generation.
    - Returns size and optionally copies content.
- Attribute record set:
  - `ufs_extattr_set`
    - Rejects readonly mounts, stopped EA state, invalid names, invalid credentials.
    - Rejects nonzero offset and content larger than configured backing slot.
    - Writes per-inode header with `INUSE`, content length, and inode generation.
    - Writes user data after header.
    - Uses `IO_SYNC` if configured.
- Attribute record delete:
  - `ufs_extattr_rm`
    - Rejects readonly mounts, stopped state, invalid names, invalid credentials.
    - Validates current header is in-use and generation matches.
    - Clears `INUSE` and length in backing header.
- Inactive cleanup:
  - `ufs_extattr_vnode_inactive`
    - When EA support is started, removes all enabled attributes for an inactive vnode.

## Interactions
- ACL code uses this layer for POSIX.1e and NFSv4 ACL storage.
- UFS2 is explicitly excluded from backing-file `extattrctl` because UFS2 uses native extended attributes.
- Uses vnode read/write/open/close operations against backing files.
- Per-inode records rely on inode number and generation to detect stale attribute data reuse.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_extattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_extern.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_extern.h

## Purpose
Declares UFS external function interfaces shared across UFS implementation files, including vnode operations, directory operations, block mapping, softdep hooks, initialization, and low-level allocation flags.

## Key Contents
- Forward declarations for UFS/VFS structures.
- VOP vectors:
  - `ufs_fifoops`
  - `ufs_vnodeops`
- Block mapping:
  - `ufs_bmap`
  - `ufs_bmaparray`
  - `ufs_bmap_seekdata`
  - `ufs_getlbns`
- Directory operations:
  - `ufs_checkpath`
  - `ufs_dirbad`
  - `ufs_dirbadentry`
  - `ufs_dirempty`
  - `ufs_makedirentry`
  - `ufs_direnter`
  - `ufs_dirremove`
  - `ufs_dirrewrite`
  - `ufs_lookup_ino`
  - `ufs_lookup`
  - `ufs_readdir`
- Extended data operations:
  - `ufs_extread`
  - `ufs_extwrite`
- Vnode lifecycle:
  - `ufs_inactive`
  - `ufs_need_inactive`
  - `ufs_reclaim`
  - `ufs_vinit`
  - `ufs_root`
- Filesystem lifecycle:
  - `ufs_init`
  - `ufs_uninit`
- Timestamp/snapshot helpers:
  - `ufs_itimes`
  - `ffs_snapgone`
- Sysctl declaration:
  - `SYSCTL_DECL(_vfs_ufs)`
- Soft updates hooks:
  - Directory add/change/remove setup.
  - Link count changes.
  - Create/link/mkdir/rmdir/unlink setup and revert.
  - `softdep_slowdown`
- Low-level allocation flags:
  - `BA_CLRBUF`
  - `BA_METAONLY`
  - `BA_UNMAPPED`
  - Sequential heuristic encoding: `BA_SEQMASK`, `BA_SEQSHIFT`, `BA_SEQMAX`

## Interactions
- Central declaration point for UFS C files.
- `ufs_bmap.c` implements several block mapping declarations here.
- Directory and vnode operation implementations elsewhere use the softdep and allocation flag contracts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_gjournal.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_gjournal.c

## Purpose
Implements UFS hooks for GEOM journaling orphan tracking by maintaining unreferenced inode counters in cylinder groups and the superblock.

## Key Contents
- Internal counter updater:
  - `ufs_gjournal_modref(struct vnode *vp, int count)`
    - Determines inode cylinder group via `ino_to_cg`.
    - Resolves the real device from normal disk device or snapshot device vnode.
    - Validates inode range against filesystem inode capacity.
    - Reads cylinder group with `ffs_getcg`.
    - Updates `cg_unrefs` and `fs_unrefs` by `count`.
    - Marks superblock modified via `fs_fmod`.
    - Clears active cylinder group bit with `ACTIVECLEAR`.
    - Writes cylinder group buffer with `bdwrite`.
- Orphan hook:
  - `ufs_gjournal_orphan`
    - Returns if no gjournal provider.
    - Skips vnodes without enough references or already marked deleted.
    - Skips directories with more than `.`/`..` links and non-directories with more than one link.
    - Marks vnode `VV_DELETED`.
    - Increments unreferenced inode count.
- Close hook:
  - `ufs_gjournal_close`
    - Returns if no gjournal provider or vnode is not marked deleted.
    - If inode link count is now zero, decrements unreferenced inode count.

## Interactions
- Declared in `gjournal.h`.
- Uses `ffs_getcg`, `struct cg`, and `struct fs` from FFS.
- Updates state used for journal recovery/orphan cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_gjournal.c -->