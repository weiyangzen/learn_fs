# Group Research: group_393_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_fuse_fuse_vnops_c_sour_30c17b2f2085

Scope checked against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_vnops.c

Implements FreeBSD vnode operations for the kernel FUSE filesystem bridge. It maps VFS operations onto FUSE protocol requests, manages vnode/filehandle state, handles cache coherency, and integrates FUSE with FreeBSD permissions, buffer cache, VM pager, NFS export support, xattrs, locking, and sparse-file interfaces.

Main responsibilities:
- Registers `fuse_vnops` for normal FUSE vnodes and `fuse_fifoops` for FIFO special handling.
- Implements VOPs for access, lookup, create, mknod, mkdir, symlink, link, rename, remove, rmdir, open, close, inactive, reclaim, read, write, readdir, readlink, fsync/fdatasync, getattr/setattr, bmap, strategy, getpages, pathconf, advlock, ioctl, xattrs, allocate/deallocate, delayed setsize, print, and NFS filehandle export.
- Uses FUSE feature probing and fallback: `FUSE_CREATE` fallback to `MKNOD+OPEN`, optional `FUSE_BMAP`, `FUSE_LSEEK`, `FUSE_FALLOCATE`, `FUSE_COPY_FILE_RANGE`, and xattr opcodes.
- Maintains attribute and entry cache validity, with explicit cache purges after namespace mutations and local size/timestamp changes.

Key implementation details:
- Dead-session checks generally return `ENXIO` with extended error context, while root getattr has a minimal fallback so path-based unmount can still work.
- `fuse_vnop_lookup()` uses FreeBSD namecache timeouts, handles `"."` and `".."`, validates server node ids, creates vnodes via `fuse_vnode_get()`, and enforces sticky/write checks when default permissions are active.
- `fuse_vnop_create()` can receive both entry and open-handle data from `FUSE_CREATE`; if vnode creation fails it sends `FUSE_RELEASE` for the opened handle.
- Read/write choose direct or buffered backends based on `IO_DIRECT`, `FN_DIRECTIO`, and mount data-cache options.
- Buffer invalidation around allocate/deallocate/copy/write preserves dirty partial blocks by flushing edge buffers before invalidating whole buffer ranges.
- `fuse_vnop_close()` sends `FUSE_FLUSH`, opportunistically persists atime, and saves delayed size changes.
- `fuse_vnop_inactive()` flushes or invalidates dirty regular-file buffers before closing all filehandles, then recycles revoked vnodes.
- `fuse_vnop_reclaim()` sends `FUSE_FORGET` for non-root nodes with positive lookup counts, purges cache/hash entries, and destroys vnode-private data.
- xattr VOPs translate FreeBSD `user`/`system` namespaces to Linux/FUSE `user.name` and `system.name` strings; list conversion rewrites NUL-delimited Linux names into FreeBSD length-prefixed names.
- NFS export support requires `FSESS_EXPORT_SUPPORT` and rejects kernel NFS export when the daemon implements `FUSE_OPENDIR`.

Important dependencies:
- FUSE helpers from `fuse.h`, `fuse_file.h`, `fuse_internal.h`, `fuse_ipc.h`, `fuse_node.h`, and `fuse_io.h`.
- FreeBSD VFS/vnode, namecache, buffer cache, VM pager, credential/privilege, extattr, and SDT tracing APIs.
- `fuse_internal_*` routines perform most request construction, permission, setattr, entry validation, fsync, readdir, remove/rename, and vnode cache updates.

Notable risks and edge cases:
- Several operations depend on daemon protocol capability and intentionally degrade to `ENOSYS`, `EOPNOTSUPP`, `ENOTTY`, or local VFS fallbacks.
- Cached attributes can be stale by design; the code carefully chooses when stale cached size is acceptable for advisory clustering.
- FUSE protocol limitations require guessed bmap runs, synthesized `_PC_MIN_HOLE_SIZE`, xattr format conversion, and local validation of server-returned node ids.
- Direct I/O flag reads are explicitly done without a lock, with a referenced FreeBSD bug comment.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/mntfs/mntfs_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/mntfs/mntfs_vnops.c

Implements private `mntfs` character-device vnodes used by mounted filesystems to safely hold backing disk devices without depending directly on the application-visible devfs vnode.

Main responsibilities:
- Defines `mntfs_vnodeops`, using default vnode ops, standard fsync, panic strategy, and custom reclaim.
- `mntfs_allocvp()` allocates a private `VCHR` vnode associated with a mount and an existing device vnode’s `v_rdev`.
- `mntfs_freevp()` tears down the private vnode with `vgone()` and `vput()`.

Key implementation details:
- The design avoids devfs vnode invalidation problems when a device disappears. Filesystems can keep their own private vnode and clean dirty buffers in a controlled manner.
- `mntfs_allocvp()` requires the original vnode to be exclusively locked, takes a device reference with `dev_ref()`, unlocks the original vnode, locks the new vnode, and marks it constructed.
- `mntfs_reclaim()` releases the held device reference with `dev_rel()`.

Important dependencies:
- FreeBSD vnode lifecycle and device reference APIs: `getnewvnode`, `vn_lock`, `vn_set_state`, `vgone`, `vput`, `dev_ref`, `dev_rel`.
- Used by filesystems that need stable private access to their backing device vnode.

Notable risks and edge cases:
- `vop_strategy` is `VOP_PANIC`; the vnode is not intended for normal strategy I/O dispatch through this vector.
- Correct paired use of `mntfs_allocvp()` and `mntfs_freevp()` is required to balance device references.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/mntfs/mntfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/bootsect.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/bootsect.h

Defines on-disk boot-sector layouts for FAT/MS-DOS filesystems.

Main responsibilities:
- Describes DOS 3.3, DOS 5.0, and DOS 7.10/FAT32 boot sectors as fixed 512-byte structures.
- Defines the extended boot record fields used by FAT12/FAT16 volume metadata.
- Provides boot-sector signature constants `BOOTSIG0` and `BOOTSIG1`, and extended signature `EXBOOTSIG`.

Key structures:
- `struct bootsector33`: 3-byte jump, OEM name, 19-byte BPB, drive number, boot code pad, signature.
- `struct extboot`: drive number, reserved byte, extended signature, volume ID, label, filesystem type.
- `struct bootsector50`: DOS 5.0 boot sector with 25-byte BPB and 26-byte extension.
- `struct bootsector710`: FAT32 boot sector with 53-byte BPB and 26-byte extension.
- `union bootsector`: overlays all supported boot-sector forms.

Important dependencies:
- Paired with `bpb.h`, which defines the BIOS Parameter Block layouts embedded in these boot-sector byte arrays.

Notable risks and edge cases:
- These are disk-format structures; fields are byte arrays where alignment/endian handling is expected elsewhere.
- A disabled `#if 0` shorthand block documents older BPB field aliases but is not active.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/bootsect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/bpb.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/bpb.h

Defines BIOS Parameter Block and FAT32 FSInfo layouts for msdosfs.

Main responsibilities:
- Provides native BPB structs for DOS 3.3, DOS 5.0, and DOS 7.10/FAT32.
- Provides byte-packed on-disk BPB structs that avoid compiler alignment assumptions.
- Defines little-endian load/store macros for BPB fields.
- Defines FAT32 flags/version/root/info/backup boot-sector fields and FSInfo block layout.

Key structures and constants:
- `struct bpb33`, `bpb50`, `bpb710`: typed in-memory BPB layouts.
- `struct byte_bpb33`, `byte_bpb50`, `byte_bpb710`: byte-array disk layouts.
- `FATNUM`, `FATMIRROR`, and `FSVERS` describe FAT32 extended flags/version behavior.
- `struct fsinfo` contains FAT32 FSInfo signatures, free-cluster count, and next-free hint.
- `getushort`, `getulong`, `putushort`, `putulong` wrap little-endian decoding/encoding.

Important dependencies:
- Uses `<sys/endian.h>` little-endian helpers.
- Consumed by mount, FAT, directory, and conversion code that parses or writes FAT metadata.

Notable risks and edge cases:
- Disk fields are little-endian and often unaligned; callers must use the byte-layout structures and endian macros for on-disk data.
- FAT32 support depends on correctly interpreting `bpbBigFATsecs`, root cluster, FSInfo sector, and mirroring flags.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/bpb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/denode.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/denode.h

Defines msdosfs vnode-private state, FAT cache state, denode flags, directory-entry conversion macros, file ID format, and internal function prototypes.

Main responsibilities:
- Documents FAT/MS-DOS directory and root-directory quirks that drive the in-memory denode model.
- Defines `struct denode`, the filesystem-specific vnode payload.
- Defines a small FAT lookup cache for cluster-chain traversal.
- Provides conversion macros between on-disk `struct direntry` and in-memory `struct denode`.
- Declares core denode, FAT, directory, creation, truncation, and lookup helper routines.

Key structures and macros:
- `MSDOSFSROOT_OFS` is a synthetic root-directory entry offset.
- `struct fatcache` and slots `FC_LASTMAP`, `FC_LASTFC`, `FC_NEXTTOLASTFC` cache file-relative to filesystem-relative cluster mappings.
- `struct denode` stores vnode pointer, cluster write state, flags, directory-entry location, search state, refcount, mount pointer, DOS name/attributes/timestamps/start cluster/size, FAT cache, file revision, and synthetic inode number.
- Flags include `DE_UPDATE`, `DE_CREATE`, `DE_ACCESS`, and `DE_MODIFIED`.
- `MSDOSFS_FILESIZE_MAX` caps FAT files at 4 GiB minus 1.
- `DE_INTERNALIZE` and `DE_EXTERNALIZE` move fields between disk directory entries and denodes, including FAT32 high cluster bits.
- `DETIMES` updates FAT date/time fields from timespecs and honors `MSDOSFSMNT_NOWIN95`.
- `DETOI()` constructs stable synthetic inode numbers from directory location.

Important dependencies:
- Depends on FAT type predicates from `fat.h` and directory entry layout from `direntry.h`.
- Exposes internal APIs used by msdosfs vnode ops, lookup, FAT allocation, and mount code.

Notable risks and edge cases:
- FAT has no real inode numbers or link counts, so denode identity is synthesized from directory-entry location and special root handling.
- Multiple directory entries can refer to a directory via `"."`, `".."`, and parent entries; root lacks real dot entries.
- Directory sizes on disk are unreliable in normal directory entries, so runtime code often derives directory length from the FAT chain.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/denode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/direntry.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/direntry.h

Defines on-disk FAT directory entries, Win95 long-filename entries, attribute bits, timestamp bitfields, and name conversion prototypes.

Main responsibilities:
- Models the 32-byte DOS short directory entry.
- Models Win95/VFAT long-name subentries.
- Defines directory slot marker values and file attribute bits.
- Defines FAT time/date bit masks and shifts.
- Provides kernel-only interfaces for short-name and long-name conversion.

Key structures and constants:
- `struct direntry`: 8.3 name, attributes, lowercase flags, create/access/modify timestamps, high/low start cluster, and file size.
- Slot markers: `SLOT_EMPTY`, `SLOT_E5`, `SLOT_DELETED`.
- Attributes: readonly, hidden, system, volume, directory, archive, and normal.
- Lowercase flags: `LCASE_BASE`, `LCASE_EXT`.
- `struct winentry`: VFAT LFN sequence count, UTF-16 name parts, `ATTR_WIN95`, checksum, and reserved fields.
- `WIN_CHARS`, `WIN_MAXSUBENTRIES`, and `WIN_MAXLEN` define LFN capacity.

Important dependencies:
- `struct mbnambuf` buffers reconstructed long names in kernel builds.
- Declares conversion helpers implemented in `msdosfs_conv.c`.

Notable risks and edge cases:
- LFN entries are checksum-linked to the following 8.3 entry and must be processed in reverse slot order.
- FAT timestamp fields are packed manually rather than represented with bitfields for portability.
- `WIN_MAXLEN` must fit within `struct dirent.d_name`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/direntry.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/fat.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/fat.h

Defines FAT cluster constants, FAT type predicates, EOF detection, FAT operation flags, and internal FAT allocation/mapping prototypes.

Main responsibilities:
- Normalizes cluster marker values across FAT12, FAT16, and FAT32.
- Defines FAT masks and predicates for filesystem type checks.
- Declares cluster-chain mapping, allocation, freeing, extension, cache purge, and volume dirty-bit routines.

Key constants and macros:
- `MSDOSFSROOT` and `CLUST_FREE` are both zero in different contexts.
- `CLUST_FIRST` is the first allocatable cluster.
- `CLUST_RSRVD`, `CLUST_BAD`, `CLUST_EOFS`, and `CLUST_EOFE` represent reserved, bad, and EOF ranges.
- `FAT12_MASK`, `FAT16_MASK`, `FAT32_MASK` select valid cluster bits.
- `FAT12(pmp)`, `FAT16(pmp)`, `FAT32(pmp)` inspect `pm_fatmask`.
- `MSDOSFSEOF(pmp, cn)` detects EOF markers after mask normalization.
- `FAT_GET`, `FAT_SET`, and `FAT_GET_AND_SET` drive `fatentry()`.
- `DE_CLEAR` requests zeroing newly allocated clusters during extension.

Important dependencies:
- Prototypes depend on `struct denode` and `struct msdosfsmount`.
- Implemented mainly by `msdosfs_fat.c`.

Notable risks and edge cases:
- FAT12 packed 12-bit entries require special handling in implementation.
- Cluster zero has special meanings for root directory, empty file, and free FAT entry depending on context.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/fat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_conv.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_conv.c

Implements filename and character conversion for msdosfs, including DOS 8.3 names, Win95/VFAT long filenames, local charset conversion, and UTF-16 handling.

Main responsibilities:
- Converts DOS short names to Unix names with optional lowercase handling.
- Converts Unix names to DOS 8.3 names, including generation suffixes like `~1`.
- Creates and validates VFAT long-name directory entries.
- Reassembles VFAT long-name entries into `dirent` names.
- Computes VFAT short-name checksums and LFN slot counts.
- Provides helper buffer management for multi-byte LFN assembly.

Key implementation details:
- Static translation tables map ISO-8859-1/local bytes to CP850-style DOS bytes and back, plus upper/lowercase tables.
- If `MSDOSFSMNT_KICONV` is active and `msdosfs_iconv` is available, conversions use kernel iconv handles from the mount.
- `unix2dosfn()` rejects names consisting only of spaces/dots and disallowed characters, handles `"."`/`".."`, splits extension rules, inserts generation numbers, and remaps leading `0xe5` to `SLOT_E5`.
- `unix2winfn()` writes one VFAT LFN slot at a time, trims trailing spaces/dots, handles UTF-16 surrogate pairs, and marks the last slot with `WIN_LAST`.
- `win2unixfn()` validates slot sequence and checksum, rejects embedded slash, handles surrogate pairs crossing slot boundaries, and appends slot text to `mbnambuf`.
- `winChkName()` compares requested names case-insensitively through UTF-16 conversion.
- `mbnambuf_write()` expects descending slot ids and shifts variable-width substrings to reconstruct full names.

Important dependencies:
- Uses `direntry.h` LFN/short-entry structures and `msdosfsmount.h` charset flags/handles.
- Exposes conversion routines declared in `direntry.h`.

Notable risks and edge cases:
- VFAT long names are case-insensitive for lookup even when preserving case.
- Trailing spaces and dots are dropped for Win95 long-name slot calculations.
- Invalid or unconvertible characters become `?`, `_`, or cause conversion failure depending on path.
- Surrogate-pair handling spans adjacent LFN slots, which is easy to break if slot ordering changes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_conv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_denode.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_denode.c

Implements denode lifecycle and file-size mutation for msdosfs: vnode lookup/allocation, directory-entry synchronization, truncation, extension, hash reinsertion, inactive processing, and reclaim.

Main responsibilities:
- `deget()` obtains or creates a denode/vnode for a directory-entry location.
- `deupdat()` writes modified denode metadata back to its on-disk directory entry.
- `detrunc()` truncates files and frees trailing cluster chains.
- `deextend()` allocates clusters and extends regular files.
- `reinsert()` updates the vnode hash key after a file moves to a new directory entry.
- `msdosfs_inactive()` handles final cleanup of deleted files.
- `msdosfs_reclaim()` removes denodes from the vnode hash and frees memory.

Key implementation details:
- Denodes are hashed by synthetic inode from `DETOI()`, with `de_vncmpf()` rejecting unlinked/open entries with nonpositive refcount.
- Root denodes are manufactured because FAT root directories may lack real directory entries. Non-FAT32 root has fixed size; FAT32 root behaves more like a normal cluster chain.
- Directory denode size is derived by walking the FAT chain with `pcbmap()` because directory entries store zero size for directories.
- `deupdat()` applies pending FAT timestamp changes via `DETIMES()`, externalizes the denode to a `direntry`, and writes or delays the directory block.
- `detrunc()` protects fixed FAT12/16 root directories, zero-fills partial final clusters, updates file size and directory entry, truncates vnode buffers, breaks the FAT chain, and frees removed clusters.
- `deextend()` refuses directories and fixed root extension, allocates required clusters with `extendfile()`, clears partial buffers at old EOF for large cluster/page interactions, updates vnode pager size, and writes metadata.
- `msdosfs_inactive()` truncates deleted read/write files to zero, marks the directory entry deleted, and recycles deleted/empty denodes.

Important dependencies:
- FAT mapping/allocation routines from `fat.h`.
- Directory entry conversion macros from `denode.h`.
- Buffer cache, vnode hash, VM page pressure, and vnode pager APIs.

Notable risks and edge cases:
- Root handling differs between FAT32 and older FAT variants.
- Deleted but still open files must not be reused from the denode hash even if their directory slot is reused.
- Extension has a rollback path through `detrunc()` if allocation or buffer clearing fails.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_denode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_fat.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_fat.c

Implements FAT block access, cluster-chain traversal, FAT cache lookup, cluster allocation/freeing, in-use bitmap construction, file extension, FAT mirroring, and FAT16/FAT32 dirty-bit updates.

Main responsibilities:
- `pcbmap()` maps file-relative clusters to filesystem-relative clusters and disk blocks.
- `fatentry()` reads and/or writes individual FAT entries.
- `clusteralloc()` finds and allocates contiguous free cluster runs.
- `freeclusterchain()` frees an entire cluster chain.
- `fillinusemap()` scans the FAT to build the in-memory allocation bitmap and free-cluster count.
- `extendfile()` appends allocated clusters to a denode’s chain and optionally clears them.
- `markvoldirty_upgrade()` manipulates FAT16/FAT32 clean/dirty volume bits.

Key implementation details:
- `fatblock()` maps FAT byte offsets to backing device blocks, with special FAT12 block-size adjustment for packed entries.
- `pcbmap()` handles fixed root-directory blocks separately from normal cluster chains and uses the denode FAT cache to avoid repeated full-chain scans.
- FAT12 reads/writes use packed 12-bit nibble logic; FAT16 uses 16-bit entries; FAT32 preserves high-order reserved bits.
- `updatefats()` mirrors modified FAT blocks to all FAT copies when mirroring is enabled, writing the primary/current FAT last.
- Allocation uses `pm_inusemap`, `pm_freeclustercount`, and `pm_nxtfree`; it prefers requested starts, then scans from next-free and wraps.
- `chainalloc()` marks bitmap bits first, writes the FAT chain, and rolls bitmap changes back on FAT write failure.
- `freeclusterchain()` updates both FAT entries and the in-use map under the msdosfs mount lock.
- `fillinusemap()` initially marks all clusters used, then frees entries whose FAT content is zero, validating cluster 0’s FAT media descriptor.
- `markvoldirty_upgrade()` skips FAT12, supports read-only-to-read-write upgrade, sets `B_INVALONERR`, and writes synchronously to avoid zombie dirty buffers on device write failure.

Important dependencies:
- Mount fields in `struct msdosfsmount`: FAT geometry, masks, bitmap, free counts, active FAT, mirroring flags, root-directory layout, and device vnode.
- Buffer cache and endian helpers from `bpb.h`.
- Denode cache helpers from `denode.h`.

Notable risks and edge cases:
- FAT12 packed entries are the most delicate path and require block sizing that safely spans adjacent bytes.
- Cluster 0 and 1 are special; generic `fatentry()` only accepts allocatable clusters, so dirty-bit code has a custom cluster-1 implementation.
- Freeing an already-free cluster reports an integrity error.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_fat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_iconv.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_iconv.c

Small module glue file declaring msdosfs kernel iconv support.

Main responsibilities:
- Includes kernel, module, mount, and iconv headers.
- Uses `VFS_DECLARE_ICONV(msdosfs)` to declare iconv integration state/functions for the msdosfs filesystem.

Important dependencies:
- The `msdosfs_conv.c` conversion code references `extern struct iconv_functions *msdosfs_iconv`.
- Active only when kernel iconv infrastructure is available and mounts request charset conversion.

Notable risks and edge cases:
- Contains no conversion logic itself; it is registration/declaration glue for the conversion paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_iconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_lookup.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_lookup.c

Implements msdosfs directory lookup, creation-entry insertion, directory emptiness checks, rename path safety, directory-entry reads, removal, and unique short-name generation.

Main responsibilities:
- `msdosfs_lookup()` delegates cached lookup to `msdosfs_lookup_ino()`.
- `msdosfs_lookup_ino()` scans directory entries, matches DOS 8.3 and VFAT long names, handles create/rename/delete lookup semantics, and returns target denodes.
- `createde()` writes a new short directory entry plus optional preceding VFAT long-name entries.
- `dosdirempty()` checks whether a directory contains only `"."` and `".."`.
- `doscheckpath()` prevents moving a directory into its own subtree.
- `readep()` and `readde()` read directory-entry blocks.
- `removede()` marks short and preceding long-name entries deleted.
- `uniqdosname()` finds a collision-free generated 8.3 name.

Key implementation details:
- Root `"."` and `".."` are faked because FAT root directories do not contain real dot entries.
- Lookup first converts the requested component with `unix2dosfn()` and computes required VFAT slot count with `winSlotCnt()` unless short-name mode forces 8.3-only behavior.
- Directory scanning uses `pcbmap()` cluster by cluster, reads backing device blocks, and tracks reusable empty/deleted slots for create/rename.
- VFAT entries are accumulated with `mbnambuf`; a valid long-name checksum match wins, otherwise a short 8.3 match is used when allowed.
- Volume label and VFAT entries are ignored as normal file targets.
- For create/rename miss at last component, the parent directory write permission is checked and `de_fndoffset`/`de_fndcnt` record where new entries should be written.
- For delete and rename hit cases, root deletion is rejected and parent write access is required.
- Dot-dot lookup uses `vn_vget_ino_gen()` and then revalidates that `".."` still maps to the same synthetic inode after parent locking was dropped.
- `createde()` extends the directory when the chosen slot is beyond current size, writes the short entry, then writes LFN entries backward across block boundaries as needed.
- `removede()` decrements the denode refcount and aggressively deletes preceding Win95 entries that appear associated or invalid.
- `uniqdosname()` iterates generation numbers and scans the directory for exact short-name collisions.

Important dependencies:
- Name conversion from `msdosfs_conv.c`.
- Cluster mapping/allocation from `msdosfs_fat.c`.
- Denode creation from `msdosfs_denode.c`.
- VFS namei flags and vnode locking semantics.

Notable risks and edge cases:
- Negative namecache insertion is disabled because the cache does not understand FAT case-insensitivity and 8.3 aliasing.
- Corrupted filesystems can violate directory hardlink assumptions; `msdosfs_lookup_checker()` detects target vnode equal to parent and reports integrity errors.
- `doscheckpath()` may return a wait cluster when it cannot immediately lock an ancestor denode.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_lookup.c -->