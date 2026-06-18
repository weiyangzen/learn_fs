# Group Research: group_338_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_tmpfs_tmpfs_vnops_h_8669a0c7b5a7

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_vnops.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_vnops.h

Kernel-only tmpfs vnode operations declaration header.

Key responsibilities:
- Enforces kernel-only inclusion with a preprocessor error for non-`_KERNEL` builds.
- Exports tmpfs VOP operation tables for ordinary vnodes and FIFO vnodes: `tmpfs_vnode_vops` and `tmpfs_fifo_vops`.
- Exports the read-mostly `tmpfs_bufcache_mode` tuning variable.
- Declares core tmpfs vnode operation entry points implemented in `tmpfs_vnops.c`: access checks, full and lightweight getattr, setattr, and reclaim.

Dependencies:
- Depends on DragonFly VFS `struct vop_ops` and `struct vop_*_args` declarations being available from including context.
- Uses `__read_mostly`, so it is tied to DragonFly kernel compiler/storage annotations.

Notable risks:
- This is a small internal interface; signature changes must match both the VOP table definitions and callers in tmpfs code.
- The header intentionally exposes only a narrow subset of tmpfs vnode operations, so additional tmpfs VOPs may be private to implementation files.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_vnops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/Makefile

Kernel module build descriptor for the DragonFly UDF filesystem.

Key responsibilities:
- Declares the kernel module name as `udf`.
- Builds the module from `osta.c`, `udf_vfsops.c`, and `udf_vnops.c`.
- Includes DragonFly's common kernel-module make rules through `bsd.kmod.mk`.

Dependencies:
- Requires the kernel build system's `bsd.kmod.mk`.
- The source list must remain synchronized with the UDF implementation files.

Notable risks:
- Adding UDF support code without updating `SRCS` would silently exclude it from the module build.
- This module is read-only at VFS registration time, so write-support files would also need VFS flag changes elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/ecma167-udf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/ecma167-udf.h

Packed on-disk ECMA-167/UDF descriptor layout header.

Key responsibilities:
- Defines UDF descriptor tag identifiers for primary volume, anchor, volume, implementation volume, partition, logical volume, unallocated space, terminator, integrity, file set, file identifier, and file entry descriptors.
- Defines packed media-format structures used by mount and vnode code: descriptor tags, logical block addresses, extent descriptors, short/long/extended allocation descriptors, character-set specs, timestamps, entity identifiers, ICB tags, anchor pointers, volume descriptors, partition maps, sparing tables, partition descriptors, file set descriptors, file identifier descriptors, and file entries.
- Defines key UDF constants such as `UDF_REGID_ID_SIZE`, `UDF_PMAP_SIZE`, `UDF_FID_SIZE`, `UDF_FENTRY_SIZE`, file-character flags, ICB permission flags, and file-entry permission masks.
- Provides `union dscrptr` for treating a descriptor buffer as one of the known UDF descriptor formats.
- Provides allocation descriptor helper macros `GETICB` and `GETICBLEN`.

Dependencies:
- Requires fixed-width integer types and DragonFly's `__packed` annotation from included kernel headers.
- Consumed by UDF mount parsing and vnode block-mapping code.

Notable risks:
- Structure layout is media ABI; padding, field width, or packing changes would break disk parsing.
- Several structures use flexible one-element tail arrays, so consumers must validate descriptor lengths before copying variable data.
- Comments and implementation only cover a subset of UDF variants; type 2 virtual/sparable maps are described, but runtime support is limited.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/ecma167-udf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/osta.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/osta.c

OSTA UDF helper implementation for CS0 Unicode compression/decompression and checksums.

Key responsibilities:
- Implements `udf_UncompressUnicode`, converting UDF CS0 compressed names with compression IDs 8 or 16 into host-order 16-bit Unicode values.
- Implements `udf_UncompressUnicodeByte`, a byte-preserving variant that emits two bytes per Unicode value.
- Implements `udf_CompressUnicode`, writing a CS0 compressed byte stream from host-order 16-bit Unicode input.
- Defines the CRC-CCITT style lookup table used by UDF checksums.
- Implements `udf_cksum` over bytes and `udf_unicode_cksum` over 16-bit Unicode values using big-endian byte order for Unicode checksum input.
- Contains an optional `MAIN` checksum test harness and an optional `NEEDS_ISPRINT` filename translation implementation, both inactive in the normal kernel-module build.

Dependencies:
- Includes `vfs/udf/osta.h` for `byte`, `unicode_t`, constants, and prototypes.
- Optional inactive translation code expects platform macros such as `UNIX`, `MAXLEN`, and printable-character helpers.

Notable risks:
- The active decompression routines only validate the compression ID; callers must ensure input correctness and output buffer capacity.
- `udf_transname` in `udf_vnops.c` depends on these routines and currently degrades non-8-bit Unicode characters to `.`.
- The optional filename translation block references `isprint`/`UnicodeIsPrint` details and appears not wired into the DragonFly build.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/osta.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/osta.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/osta.h

Prototype and compatibility header for OSTA UDF helper routines.

Key responsibilities:
- Defaults the platform macro to `UNIX` if no platform is selected.
- Defaults `MAXLEN` to 255 for translated filenames.
- Defines the helper types `unicode_t` as unsigned 16-bit and `byte` as unsigned 8-bit.
- Declares CS0 compression/decompression, byte checksum, Unicode checksum, and optional filename translation functions.

Dependencies:
- Expects the compiler's `unsigned short` and `unsigned char` sizes to match the documented UDF helper assumptions.
- Included by both `osta.c` and UDF VFS/vnode code.

Notable risks:
- Type definitions are intentionally simple and predate fixed-width typedefs; portability assumes DragonFly's target ABI.
- `UDFTransName` is declared even though the implementation is conditional in `osta.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/osta.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf.h

Internal UDF filesystem state and helper interface header.

Key responsibilities:
- Defines `struct udf_node`, the per-vnode in-memory object containing vnode/device references, mount pointer, hash id, directory lookup offset, and copied UDF file entry.
- Defines `struct udf_mnt`, the per-mount state containing device and mount references, export state, logical block geometry, partition start/length, root ICB, vnode cache hash table, sparing-table metadata, and hash synchronization token.
- Defines `struct udf_dirstream`, the state machine used by `udf_vnops.c` to iterate file identifier descriptors across directory extents and fragmented FIDs.
- Defines conversion macros `VFSTOUDFFS` and `VTON`.
- Defines block-read helpers: `RDSECTOR`, `udf_readlblks`, and `udf_readalblks`. Logical block reads are rounded to the mount block mask; allocation-block reads include partition offset and one-block read-ahead.
- Defines `udf_getid`, mapping a long allocation descriptor to an inode-like file number by `lb_num`.
- Declares vnode allocation, vnode hash, descriptor tag validation, and `udf_vget` helpers.

Dependencies:
- Requires UDF on-disk structures from `ecma167-udf.h` and DragonFly kernel VFS/buffer/mount/list/token types.
- Uses DragonFly buffer APIs `bread` and `breadn`.

Notable risks:
- `udf_getid` assumes long allocation descriptors and uses only logical block number; multi-partition or descriptor variants could collide or be unsupported.
- Read helpers depend on `udfmp->bshift` and `bmask` being initialized from the logical volume descriptor.
- The mount structure has single-partition assumptions despite UDF descriptors supporting richer layouts.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf_mount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf_mount.h

User/kernel mount-argument structure for the UDF filesystem.

Key responsibilities:
- Defines `struct udf_args`, carrying the user-supplied block special device path, network export options, and mount flags.
- Provides the mount argument ABI consumed by `udf_mount` in `udf_vfsops.c`.

Dependencies:
- Uses `struct export_args` from DragonFly mount/export infrastructure.
- The `fspec` pointer is copied from userland by mount code.

Notable risks:
- This is ABI-facing for mount tooling; field order and type changes affect userland compatibility.
- `fspec` is a user pointer and requires careful `copyin`/`copyinstr` handling by callers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf_vfsops.c

DragonFly UDF VFS operations implementation: mount, unmount, root lookup, statfs, file-handle conversion, and vnode instantiation.

Key responsibilities:
- Registers `udf_vfsops` as a read-only local filesystem through `VFS_SET(..., VFCF_READONLY)` and module version 1.
- Implements `udf_mount`, requiring read-only mounts, rejecting root filesystem mounts, copying `struct udf_args`, supporting export updates, resolving the block device with namecache lookup, checking disk/read access, and delegating actual media parsing to `udf_mountfs`.
- Implements `udf_checktag`, validating descriptor tag id and checksum over descriptor-tag bytes except the checksum byte.
- Implements `udf_mountfs`, opening the device, allocating `struct udf_mnt`, initializing mount IDs/geometry defaults, reading the anchor at sector 256, scanning the main volume descriptor sequence for logical volume and partition descriptors, parsing partition maps, reading the file set descriptor, storing the root ICB, installing vnode ops, validating the root file entry, and initializing the vnode hash table.
- Implements `udf_unmount`, flushing vnodes, closing and releasing the device vnode, freeing sparing table/hash/mount allocations, and clearing mount state.
- Implements `udf_root`, resolving the root ICB into a vnode through `udf_vget` and marking it `VROOT`.
- Implements `udf_statfs`, reporting logical block size, partition length, zero free blocks/files, and mount source name.
- Implements `udf_vget`, using the vnode hash cache first, reading and copying a one-block UDF file entry, allocating a vnode, linking `udf_node` state, inserting it into the hash, and mapping UDF file type values to DragonFly vnode types.
- Implements NFS-style file handle conversion through a local `ifid` carrying inode number.
- Implements `udf_find_partmaps`, supporting ordinary type 1 maps and type 2 sparable partition maps, reading the first sparing table and recording valid sparing-table entries.

Dependencies:
- Uses DragonFly VFS, vnode, namecache, buffer cache, capability, mount-export, and module APIs.
- Uses UDF on-disk descriptors from `ecma167-udf.h`, OSTA helpers, and internal UDF structures from `udf.h`.
- Depends on `udf_vnode_vops` from `udf_vnops.c`.

Notable risks:
- Mount probing is intentionally narrow: it uses 2048-byte sectors, checks only anchor sector 256, and comments note missing checks for sector `n`, `n - 256`, and 512.
- The implementation supports one partition and limited partition-map types; unsupported maps fail mount.
- `udf_vget` allocates `size = UDF_FENTRY_SIZE + l_ea + l_ad` from on-disk fields after only tag validation, so malformed descriptors can stress allocation or bounds assumptions.
- The sparing table tag validation calls `udf_checktag(..., 0)`, which accepts only tag id 0 even though the table has a descriptor tag; this is a compatibility-sensitive area.
- Error paths close/free most state, but media parsing assumes many descriptor fields are trustworthy after tag checks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf_vnops.c

DragonFly UDF vnode operations implementation for the read-only filesystem.

Key responsibilities:
- Defines `udf_vnode_vops` with handlers for access, bmap, old lookup, getattr, ioctl, pathconf, read, readdir, readlink, reclaim, and strategy.
- Implements vnode hash helpers `udf_hashlookup`, `udf_hashins`, and `udf_hashrem` protected by the mount hash token.
- Implements `udf_allocv`, allocating a UDF vnode and downgrading the VX lock state for normal use.
- Converts UDF file-entry permissions and ICB flags to DragonFly `mode_t` in `udf_permtomode`.
- Implements read-only access checks through `vop_helper_access`.
- Converts UDF timestamps to `timespec` with leap-year handling and a 12-bit signed timezone offset.
- Implements `udf_getattr`, filling vnode attributes from UDF file entries, including fallback uid/gid handling for `0xffffffff`, directory-size normalization, block size, file id, link count, and timestamps.
- Implements `udf_read`, using `udf_readatoffset` and `uiomove` to read regular file data.
- Implements CS0 name translation and comparison helpers, using OSTA decompression and replacing non-8-bit Unicode characters with `.`.
- Implements directory stream helpers `udf_opendir`, `udf_getfid`, and `udf_closedir`; `udf_getfid` handles file identifier descriptors that span logical-block boundaries by assembling fragments into a temporary buffer.
- Implements `udf_readdir`, emitting `.` and `..`, skipping deleted entries, translating names, returning directory cookies when requested, and writing entries through `vop_write_dirent`.
- Implements `udf_lookup`, scanning directory FIDs, supporting lookup restart from `node->diroff`, handling `..`, returning `EROFS` for create/rename misses, and resolving matches through `udf_vget`.
- Implements `udf_strategy` and `udf_bmap`, translating vnode logical offsets to device offsets unless file data is embedded in the file entry.
- Implements `udf_readatoffset`, handling normal extent reads and embedded file-entry data.
- Implements `udf_bmap_internal`, supporting allocation strategy type 4, short and long allocation descriptors, embedded-data descriptors, and sparing-table remapping.
- Implements `udf_reclaim`, removing a vnode from the hash and freeing device references, copied file entry, and node memory.

Dependencies:
- Uses DragonFly VOP, buffer, uio, namei, dirent, iconv include surface, vnode locking, BIO strategy, and kernel malloc APIs.
- Uses UDF descriptor structures/macros from `ecma167-udf.h` and internal mount/node state from `udf.h`.
- Relies on OSTA Unicode decompression from `osta.c`.

Notable risks:
- The filesystem is read-only; create/rename through lookup return `EROFS`, and many mutation VOPs are absent.
- Unicode handling is deliberately incomplete and lossy for 16-bit characters, which affects lookup and readdir name fidelity.
- Directory FID parsing trusts length fields after limited checks; fragmented FID assembly has several bounds-sensitive paths.
- `udf_strategy` checks `nbio->bio_offset == NOOFFSET` before calling `udf_bmap_internal` but passes `bio->bio_offset`; this path is subtle because embedded data cannot be represented as a device block.
- `udf_bmap_internal` has limited allocation descriptor support and rejects strategy 4096 and extended descriptors.
- Timestamp conversion is explicitly approximate and ignores daylight savings and nanoseconds.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/dinode.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/dinode.h

UFS on-disk inode layout and mode constant header.

Key responsibilities:
- Defines special inode numbers: root inode `UFS_ROOTINO` as 2 and whiteout placeholder `UFS_WINO` as 1.
- Defines direct and indirect block pointer counts: `UFS_NDADDR` and `UFS_NIADDR`.
- Defines packed-by-field `struct ufs1_dinode`, the UFS1 on-disk inode containing mode, link count, legacy ids/inumber union, size, timestamps, direct/indirect block arrays, flags, block count, generation, uid/gid, and DragonFly 2019 high timestamp extension fields.
- Defines compatibility aliases for old uid/gid, LFS inode number, device number overlay, and short symlink overlay.
- Defines `UFS1_MAXSYMLINKLEN` as the storage available in direct/indirect block pointer space.
- Defines file permission bits and UFS file type bits.

Dependencies:
- Includes `ufs_types.h` for UFS integer and disk-address types.
- Consumed by inode load/update code and UFS/FFS metadata manipulation.

Notable risks:
- This is on-disk ABI; field layout and sizes must not change without filesystem-format migration.
- The direct block array is overloaded for devices and short symlinks, so consumers must respect inode type before interpretation.
- DragonFly's 48-bit timestamp extensions reuse former spare fields, which affects cross-system compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/dir.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/dir.h

UFS directory entry format header.

Key responsibilities:
- Defines `doff_t` as a 32-bit directory offset and caps practical directory size at `MAXDIRSIZE`.
- Defines directory block size `DIRBLKSIZ` as `DEV_BSIZE` and maximum name length `MAXNAMLEN` as 255.
- Defines `struct direct`, the UFS directory record with inode number, record length, file type, name length, and NUL-terminated name buffer.
- Defines directory entry type constants compatible with `dirent`-style `DT_*` values.
- Defines conversion macros between inode mode file type bits and directory type values: `IFTODT` and `DTTOIF`.
- Defines `DIRECTSIZ` and endian-aware `DIRSIZ` for calculating minimal aligned directory record length, including old-directory-format support on little-endian systems.
- Defines directory templates for new and old `.`/`..` entry layouts.

Dependencies:
- Requires system constants/types such as `DEV_BSIZE`, `BYTE_ORDER`, and `__offsetof`.
- Used by UFS directory manipulation and dirhash code.

Notable risks:
- Directory parsing depends on record length and name length integrity; malformed on-disk entries can corrupt traversal unless callers validate.
- Old/new directory format handling is endian-sensitive.
- Directory block layout assumes 4-byte alignment and atomic transfer-sized directory blocks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/dirhash.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/dirhash.h

UFS directory hash structure and API header.

Key responsibilities:
- Documents and defines the hash-table scheme used to map filenames to directory offsets for large directories.
- Defines empty and deleted hash slot sentinels: `DIRHASH_EMPTY` and `DIRHASH_DEL`.
- Defines directory alignment and free-space-statistics sizing constants.
- Defines scoring constants for the dirhash cache eviction policy.
- Defines a two-level hash table layout through `DH_BLKOFFSHIFT`, `DH_NBLKOFF`, `DH_NBLKOFFMASK`, and `DH_ENTRY`.
- Defines `struct dirhash`, holding the hash arrays, free-space summaries, sequential-access optimization state, cache score, global-list membership, and TAILQ linkage.
- Declares dirhash lifecycle, lookup, free-space, add/remove/move, truncation, free, and checkblock functions.

Dependencies:
- Depends on `struct inode`, `struct direct`, `doff_t`, `TAILQ_ENTRY`, and directory constants from UFS headers.
- Implementations are elsewhere in the UFS codebase.

Notable risks:
- The header itself notes poor performance with the current lookup path for large directories.
- Open-addressing with spillover requires low utilization and correct `DIRHASH_DEL` handling to preserve chains.
- Free-space statistics assume `DIRBLKSIZ` is 512 bytes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/dirhash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_alloc.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_alloc.c

FFS block, fragment, cluster, and inode allocation/free implementation for UFS.

Key responsibilities:
- Implements `ffs_alloc`, the top-level data block/fragment allocator. It validates sizes, enforces minfree for non-root users, charges quotas, selects a cylinder group from preference or inode location, calls the hash allocator, updates inode block counts, and reports full filesystems.
- Implements `ffs_realloccg`, growing a fragment in place when possible or relocating it through normal allocation, with `FS_OPTSPACE`/`FS_OPTTIME` switching based on fragmentation pressure.
- Provides sysctls under `vfs.ffs` for asynchronous free behavior and cluster reallocation behavior.
- Implements `ffs_reallocblks`, which tries to relocate a logical cluster of full blocks to a contiguous physical cluster, updates direct or indirect block maps, integrates soft updates dependencies, writes modified metadata, and frees old blocks.
- Implements `ffs_valloc`, selecting and allocating a new inode, then returning the corresponding vnode through `VFS_VGET`.
- Implements `ffs_dirpref`, choosing cylinder groups for new directories using root-level spreading, average free inode/block thresholds, maximum contiguous-directory heuristics, and parent locality.
- Implements `ffs_blkpref`, computing preferred block placement based on direct/indirect section boundaries, average free blocks, previous allocations, max contiguous blocks, and rotational delay.
- Implements `ffs_hashalloc`, the shared preferred-CG, quadratic-rehash, and brute-force fallback allocator loop used for blocks, clusters, and inodes.
- Implements internal allocation helpers: `ffs_fragextend`, `ffs_alloccg`, `ffs_alloccgblk`, `ffs_clusteralloc`, `ffs_nodealloccg`, and `ffs_mapsearch`.
- Implements `ffs_blkfree_cg`, returning blocks/fragments to cylinder-group maps, reassembling fragments into full blocks, updating free summaries and cluster accounting.
- Implements TRIM-aware `ffs_blkfree`, issuing `BUF_CMD_FREEBLKS` when mounted with `MNT_TRIM` and deferring bitmap free until the device callback schedules `ffs_blkfree_trim_task`.
- Implements diagnostic `ffs_checkblk` for allocation-state verification.
- Implements `ffs_vfree` and `ffs_freefile`, freeing inodes directly or via soft updates.
- Implements `ffs_clusteracct`, maintaining cluster free maps, cluster summaries, and `fs_maxcluster`.
- Implements `ffs_fserr`, logging filesystem/user error diagnostics.

Dependencies:
- Uses DragonFly kernel buffer cache, vnode, mount, sysctl, taskqueue, BIO, device, quota, and soft updates APIs.
- Depends on UFS inode structures, `ufsmount`, filesystem layout macros from `fs.h`, and exported prototypes in `ffs_extern.h`.
- Integrates with quotas through `ufs_chkdq` and inode hash avoidance through `ufs_ihashcheck`.

Notable risks:
- This is core metadata mutation code; incorrect bitmap, summary, quota, or soft updates ordering can corrupt filesystems.
- Many paths panic on detected internal inconsistency, as expected for kernel metadata corruption checks.
- TRIM free ordering is intentionally delayed to avoid reusing blocks before trim completes; callback pointer handling and taskqueue scheduling are sensitive.
- Allocation decisions depend on legacy rotational geometry fields that may be approximate on modern storage.
- Inode allocation deliberately avoids inodes still present in the hash, handling races with vnode reclamation.
- Cluster reallocation spans direct and indirect block maps and has complex cleanup semantics when allocation fails.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_balloc.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_balloc.c

FFS logical-to-physical block allocation routine for file writes.

Key responsibilities:
- Implements `ffs_balloc`, the VOP balloc entry point that ensures storage exists for a requested vnode byte range and returns the corresponding buffer.
- Validates logical block number, requested size, and exclusive vnode locking.
- Extends a prior EOF fragment to a full block when a write moves into later blocks.
- Handles direct blocks, including existing full blocks, existing fragments that may need reallocation, and newly allocated fragments/full blocks.
- For indirect blocks, computes the indirection chain with `ufs_getlbns`, pre-acquires the data buffer to avoid VM/filesystem deadlocks, allocates missing indirect blocks synchronously or with soft updates metadata dependencies, and allocates the final data block.
- Honors `B_CLRBUF`, `B_SYNC`, clustering, asynchronous writes, and read-before-write behavior for existing uncached blocks.
- Maintains undo history for newly allocated indirect/data blocks and unwinds allocations on failure with fsync, buffer invalidation, quota rollback, inode block count adjustment, pointer clearing, and block frees.

Dependencies:
- Uses FFS allocation helpers `ffs_alloc`, `ffs_realloccg`, `ffs_blkpref`, and `ffs_blkfree`.
- Uses UFS block mapping helper `ufs_getlbns`, inode/block layout macros, buffer-cache APIs, cluster read, soft updates setup hooks, and quota accounting.

Notable risks:
- Failure cleanup is deliberately complex; missing an allocated block in the undo lists would leak space or leave dangling metadata.
- The code relies on exclusive vnode locking to safely modify inode direct and indirect block pointers.
- Indirect block allocation must not expose garbage pointers; synchronous metadata writes are used when soft updates is not active.
- `B_CLRBUF` behavior must preserve valid dirty data around truncation/extension edge cases.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_extern.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_extern.h

Public internal FFS function and sysctl declaration header.

Key responsibilities:
- Defines FFS sysctl IDs and the `FFS_NAMES` table entries for `doreallocblks` and `doasyncfree`.
- Forward-declares kernel types needed by FFS APIs.
- Declares allocation, block mapping, mount, sync, statfs, truncate, update, vnode allocation/free/get, file-handle, and bitmap helper functions implemented across FFS source files.
- Declares soft updates entry points used by FFS code for inode block updates, mount/flush handling, allocation dependencies, freeblock setup, metadata sync, and freefile handling.

Dependencies:
- Depends on UFS disk address and logical block typedefs being available from included context.
- Shared by FFS allocation, inode, mount, vnode, and soft updates implementation files.

Notable risks:
- Function prototypes are cross-file kernel contracts; signature drift causes build or ABI-like internal breakage.
- Soft updates declarations are tightly coupled to metadata update ordering in allocation and truncate code.
- Sysctl ID values must stay consistent with existing kernel/user expectations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_inode.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_inode.c

FFS inode update and truncate implementation.

Key responsibilities:
- Implements `ffs_update`, refreshing inode timestamps, clearing lazy/modified flags, skipping writes on read-only filesystems or bad vnodes, maintaining legacy uid/gid fields for old inode formats, reading the inode block, invoking soft updates inode handling when enabled, copying the in-memory dinode to disk, and choosing synchronous or delayed write based on `waitfor`, async mode, and memory pressure.
- Implements `ffs_truncate`, handling both file extension and shrink. It validates length, handles short symlink truncation, integrates quotas, coordinates with soft updates, updates VM/buffer object sizes through `nvextendbuf`/`nvtruncbuf`, allocates the last byte when extending, shrinks partial direct blocks to fragments, writes new inode block pointers before freeing old storage, frees indirect and direct blocks, releases trailing fragments, updates `i_blocks`, and applies quota credits.
- Defines indirect block level constants `SINGLE`, `DOUBLE`, and `TRIPLE`.
- Implements recursive `ffs_indirtrunc`, reading an indirect block by explicit device offset, zeroing unneeded pointers, writing metadata before freeing referenced blocks, recursively freeing lower-level indirect trees, and reporting released block counts.

Dependencies:
- Uses DragonFly VM/buffer interfaces, vnode operations, quota helpers, UFS inode state, FFS filesystem layout macros, and FFS block-free/update helpers.
- Integrates with soft updates through `softdep_setup_freeblocks`, `softdep_slowdown`, and `softdep_update_inodeblock`.

Notable risks:
- Truncate ordering is crash-safety critical: inode pointers are cleared and written before blocks are returned to free maps.
- Partial truncate with soft updates forces fsync in some cases to avoid dangling dependencies.
- Triple-indirect truncation is explicitly noted as untested.
- Manual BIO setup in `ffs_indirtrunc` bypasses normal vnode block mapping, so device offset correctness is essential.
- Block count and quota accounting must match exactly with the blocks/fragments actually freed.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_inode.c -->