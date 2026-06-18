# Group Research: group_332_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_isofs_cd9660_cd9660_f97f54bfff17

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_node.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_node.c

Implements CD9660 in-core node hashing, vnode inactive/reclaim handling, default ISO attributes, timestamp conversion, and pseudo-inode derivation.

Key behavior:
- `cd9660_init()` allocates the global ISO node hash table, capped at `CD9660_HASH_SIZE_LIMIT`; `cd9660_uninit()` frees it.
- `cd9660_ihashget()` looks up nodes by device and inode, locks with `vget()`, then revalidates after blocking.
- `cd9660_ihashins()` and `cd9660_ihashrem()` maintain the hash under `cd9660_ihash_token`.
- `cd9660_inactive()` clears node flags and recycles unusable nodes.
- `cd9660_reclaim()` removes a node from the hash, releases the device vnode, and frees the node.
- `cd9660_defattr()` synthesizes file type, mode, UID, GID, and link count from directory records and optional extended attributes.
- `cd9660_deftstamp()`, `cd9660_tstamp_conv7()`, and `cd9660_tstamp_conv17()` convert ISO timestamps to `timespec`.
- `isodirino()` derives the pseudo-inode from extent plus extended-attribute length shifted by mount block size.

Risks and invariants:
- Hash lookup must revalidate because reclaim can remove entries while `vget()` blocks.
- Extended attributes are optional; absent or invalid attributes fall back to root ownership and read/execute bits.
- ISO 17-byte timestamp parsing assumes decimal fields.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_node.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_node.h

Defines the in-memory CD9660 inode model and vnode/node helper interfaces.

Key contents:
- Defines `doff_t` as `long` for directory offsets.
- `ISO_RRIP_INODE` stores synthesized POSIX metadata: times, mode, UID, GID, link count, and special-device number.
- `struct iso_node` stores hash linkage, vnode/device references, device identity, pseudo-inode number, mount pointer, lock state, directory lookup cache offsets, ISO extent/start/size fields, and embedded metadata.
- `VTOI()` and `ITOV()` convert between vnode and ISO node.
- Declares malloc types `M_ISOFSMNT` and `M_ISOFSNODE`.
- Declares CD9660 lookup, inactive, reclaim, bmap, block-offset reads, attribute/timestamp extraction, inode hash, and timestamp conversion functions.

Risks and invariants:
- `i_number` is a filesystem pseudo-inode, not a native on-disk Unix inode.
- Directory offset type is chosen for practical CD sizes, not theoretical maximum ISO directory size.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_rrip.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_rrip.c

Implements Rock Ridge and SUSP parsing for CD9660 metadata, alternate names, relocated directories, symlinks, timestamps, and continuation areas.

Key behavior:
- Uses table-driven scanners over SUSP records.
- `cd9660_rrip_analyze()` reads `PX`, `TF`, `PN`, `RR`, `CE`, and `ST` fields into an `iso_node`.
- `cd9660_rrip_getname()` extracts `NM` names and handles `CL`, `PL`, and `RE` relocated-directory records.
- `cd9660_rrip_getsymname()` reconstructs symlink targets from `SL` component records.
- `cd9660_rrip_offset()` validates root `SP` and `ER` records, including CD-ROM XA skip handling, and returns the SUSP skip count.
- `cd9660_rrip_loop()` locates system-use data after the ISO filename, applies mount skip offsets, dispatches records, follows `CE` continuation blocks, and applies fallback handlers for missing expected fields.

Risks and invariants:
- Continuation blocks are bounded by `volume_space_size` and `logical_block_size`.
- Name assembly is constrained by `NAME_MAX`; symlink assembly is constrained by `MAXPATHLEN`.
- Missing `PX`, `TF`, or `NM` records fall back to ISO defaults; malformed long names are treated as absent.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_rrip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_rrip.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_rrip.h

Defines packed SUSP and Rock Ridge record layouts consumed by the RRIP parser.

Key contents:
- `ISO_SUSP_HEADER` is the common type/length/version header.
- Defines records for POSIX attributes (`PX`), devices (`PN`), symlinks (`SL`), alternate names (`NM`), child/parent links (`CL`/`PL`), relocated directories (`RE`), timestamps (`TF`), identifier flags (`RR`), extension references (`ER`), SUSP offset/skip (`SP`), and continuation (`CE`).
- Defines component flags for current, parent, root, volume root, host, and continuation.
- Defines timestamp form and field bits.

Risks and invariants:
- Structures describe on-disk byte layouts and require ISO numeric conversion helpers.
- Variable-length fields require parser-side length validation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_rrip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_util.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_util.c

Provides ISO/Joliet filename character extraction, comparison, translation, and local-rune extraction.

Key behavior:
- `isochar()` decodes plain ISO one-byte names or Joliet two-byte names, optionally using kernel iconv.
- `isofncmp()` compares local names against ISO names, with case folding and optional omission of `;version`.
- `isofntrans()` translates ISO directory-entry names for readdir, handling lowercase conversion, generation stripping, and associated-file `=` prefixing.
- `sgetrune()` extracts a local character with optional iconv.

Risks and invariants:
- Joliet decoding consumes two-byte units except special one-byte cases.
- Without iconv, unsupported Joliet high-byte characters degrade to `?`.
- Version stripping and case folding affect both lookup and directory presentation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_vfsops.c

Implements the CD9660 VFS layer: mount, root mount, unmount, statfs, vnode construction, and NFS filehandle/export support.

Key behavior:
- Registers `cd9660_vfsops` as read-only.
- `iso_get_ssector()` scans CD TOC data to pick the last data track for multisession media.
- `cd9660_mount()` enforces read-only mounts, handles updates/exports, resolves the block device, checks access, and calls `iso_mountfs()`.
- `iso_mountfs()` opens the device, scans volume descriptors, detects High Sierra, primary, supplementary/Joliet descriptors, validates block size, initializes `iso_mnt`, probes Rock Ridge, opens iconv handles, chooses ISO/RRIP/Joliet mode, and installs vnode ops.
- `cd9660_unmount()` flushes vnodes, closes iconv handles, clears device mount state, closes/releases the device vnode, and frees mount state.
- `cd9660_root()`, `cd9660_vget()`, and `cd9660_vget_internal()` build/find ISO vnodes from directory records.
- `cd9660_fhtovp()`, `cd9660_vptofh()`, and `cd9660_checkexp()` support NFS exports.

Risks and invariants:
- Mounts are always read-only.
- Volume descriptor scanning assumes 2048-byte descriptor sectors.
- Vnode construction validates pseudo-inode block range and record boundaries before trusting directory records.
- Rock Ridge root handling may require reading the relocated `.` entry.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_vnops.c

Implements CD9660 vnode operations for read-only access, attributes, reads, directory iteration, symlinks, strategy I/O, pathconf, and advisory locks.

Key behavior:
- `cd9660_setattr()` rejects mutable metadata/size changes for regular files and directories.
- `cd9660_access()` applies mount UID/GID overrides and masks before `vop_helper_access()`.
- `cd9660_getattr()` fills vnode attributes and probes RRIP symlink length when recorded size is zero.
- `cd9660_ioctl()` supports `FIOGETLBA`.
- `cd9660_read()` reads block-sized data with clustering or read-ahead.
- `cd9660_readdir()` validates ISO directory records, translates ISO/Joliet/RRIP names, emits cookies, and coalesces associated/default entries in default mode.
- `cd9660_readlink()` extracts RRIP `SL` targets from the parent directory-record block.
- `cd9660_strategy()` maps logical offsets through `VOP_BMAP()` and forwards I/O to the backing device vnode.
- Defines normal, special-device, and FIFO VOP tables.

Risks and invariants:
- Directory parsing rejects short records and block-crossing records.
- Symlinks require RRIP.
- Write-like operations preserve read-only semantics.
- Strategy must complete the original bio if mapping fails or maps to `NOOFFSET`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/iso.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/iso.h

Defines ISO9660, High Sierra, Joliet, directory-record, extended-attribute, mount-state, block mapping, and numeric conversion primitives.

Key contents:
- `ISODCL()` declares fixed byte spans.
- Defines generic, primary, supplementary/Joliet, and High Sierra volume descriptor layouts.
- Defines descriptor type constants, standard IDs, and default 2048-byte block size.
- Defines `struct iso_directory_record` and `struct iso_extended_attributes`.
- Kernel section defines `enum ISO_FTYPE`, `struct iso_mnt`, `VFSTOISOFS()`, logical-block macros, CD9660 init/vget declarations, filename utilities, `isodirino()`, and `sgetrune()`.
- Inline `isonum_711` through `isonum_733` decode ISO 7.x numeric fields.
- Defines `ASSOCCHAR` for associated-file names.

Risks and invariants:
- Multi-byte ISO numeric fields must be accessed through conversion helpers.
- `iso_mnt` stores active mount mode, RRIP skip values, Joliet level, and iconv handles that drive lookup/readdir behavior.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/iso.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/iso_rrip.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/iso_rrip.h

Defines RRIP/SUSP analyzer flags, parser state, and exported RRIP parser interfaces.

Key contents:
- Defines bit flags for attributes, devices, symlinks, alternate names, child/parent links, relocated directories, timestamps, ID flags, extension references, continuation, offset, stop, and unknown records.
- `ISO_RRIP_ANALYZE` carries parser context: target node, requested fields, continuation block/offset/length, mount pointer, output buffers, inode pointer, and continuation state.
- Declares `cd9660_rrip_analyze()`, `cd9660_rrip_getname()`, `cd9660_rrip_getsymname()`, and `cd9660_rrip_offset()`.

Risks and invariants:
- Analyzer fields double as requested-work and completion tracking.
- Buffer length fields must be honored by RRIP parser implementations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/iso_rrip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/mfs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/mfs/Makefile

Builds the DragonFlyBSD MFS kernel module.

Key contents:
- Sets `KMOD=mfs`.
- Builds `mfs_vfsops.c`.
- Includes `<bsd.kmod.mk>`.

Risks and invariants:
- Module build scope is intentionally only the MFS VFS/device implementation file.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/mfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/mfs/mfs_extern.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/mfs/mfs_extern.h

Declares external MFS interfaces.

Key contents:
- Forward-declares `buf`, `mfsnode`, `mount`, `thread`, and `vnode`.
- Declares `mfs_getimage()`, `mfs_mountfs()`, and `mfs_mountroot()`.

Risks and invariants:
- Header exposes legacy MFS entry points used by surrounding kernel/VFS code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/mfs/mfs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/mfs/mfs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/mfs/mfs_vfsops.c

Implements the memory filesystem as a UFS-backed in-memory block device plus VFS mount/start/statfs operations.

Key behavior:
- Registers `mfs_vfsops`, reusing UFS/FFS operations for root, unmount, sync, vget, filehandles, quotas, and exports.
- Defines `mfs_ops` device operations: open, close, read/write via phys I/O, and strategy.
- `mfs_mount()` creates a per-mount `/dev/mfs<pid>` device, initializes `mfsnode`, resolves the devfs vnode, sets vnode pager size, and mounts FFS over it.
- `mfs_start()` holds the mounting process, services queued bios, handles signals by attempting unmount, and cleans up the device/node on exit.
- `mfsstrategy()` bounds-checks I/O, clips EOF reads, queues bios to the service thread, or handles directly when already on that thread.
- `mfs_doio()` handles `BUF_CMD_READ` with `copyin`, `BUF_CMD_WRITE` with `copyout`, and `BUF_CMD_FREEBLKS` with page-aligned `MADV_FREE`.

Risks and invariants:
- MFS cannot be mounted as root in this implementation.
- The service thread/process must not be swapped out while it backs filesystem I/O.
- Device strategy must handle EOF clipping and invalid offsets carefully.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/mfs/mfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/mfs/mfsnode.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/mfs/mfsnode.h

Defines the MFS per-device control structure.

Key contents:
- `struct mfsnode` stores the memory base, total size, supporting thread, bio queue, backing character device, active flag, and spare field.
- Declares `M_MFSNODE` malloc type when available.

Risks and invariants:
- `mfs_baseoff` is user memory backing the filesystem image.
- `bio_queue` is serviced by the thread retained in `mfs_start()`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/mfs/mfsnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/Makefile

Builds the MSDOSFS kernel module and iconv submodule.

Key contents:
- Sets `KMOD=msdos`.
- Builds conversion, denode, FAT, lookup, VFS, vnode ops, and `opt_msdosfs.h`.
- Exports `msdos_iconv`.
- Descends into `msdosfs_iconv`.

Risks and invariants:
- Core MSDOSFS and iconv support are separate modules, with iconv symbols exported for optional conversion support.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/bootsect.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/bootsect.h

Defines on-disk DOS/FAT boot-sector layouts.

Key contents:
- `bootsector33`, `bootsector50`, and `bootsector710` model DOS 3.3, DOS 5.0, and FAT32-era boot sectors.
- `extboot` models extended boot metadata: drive number, boot signature, volume ID, label, and filesystem type.
- Defines boot-sector signatures `0x55` and `0xaa`, and extended boot signatures `0x29`/`0x28`.
- `union bootsector` provides shared access to all variants.

Risks and invariants:
- Structures are byte-layout views of sector data and include fixed padding to 512 bytes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/bootsect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/bpb.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/bpb.h

Defines BIOS Parameter Block and FAT32 FSInfo structures.

Key contents:
- Native BPB structs for DOS 3.3, DOS 5.0, and FAT32/DOS 7.10.
- Byte-oriented BPB structs for unaligned on-disk access.
- Defines little-endian helpers `getushort`, `getulong`, `putushort`, and `putulong`.
- FAT32 BPB fields include big FAT size, mirroring flags, version, root cluster, FSInfo sector, and backup boot sector.
- `struct fsinfo` defines FAT32 free-cluster and next-free metadata signatures/fields.

Risks and invariants:
- On-disk BPB fields are unaligned byte arrays; callers must use endian helpers.
- FAT32 version and mirroring flags influence mount and FAT update behavior.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/bpb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/denode.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/denode.h

Defines the in-memory MSDOSFS vnode-private denode and related conversion/cache interfaces.

Key contents:
- Documents FAT/DOS root-directory and cluster-number quirks.
- Defines `MSDOSFSROOT_OFS` as the pseudo-offset for the root directory entry.
- Defines FAT cache slots `FC_LASTMAP`, `FC_LASTFC`, and `FC_NEXTTOLASTFC`.
- `struct denode` stores hash linkage, vnode/device references, directory-entry location, lookup cache offsets, reference count, mount pointer, DOS name/attributes/times/start cluster/file size, FAT cache, and revision.
- Defines denode flags for time updates, creation/access updates, modification, and rename.
- Defines `DE_INTERNALIZE` and `DE_EXTERNALIZE` for direntry conversion.
- Defines `DETIMES()` for deferred FAT timestamp updates.
- Declares denode, lookup, directory-entry, truncation, creation, removal, path-checking, and FAT-map helpers.

Risks and invariants:
- Denodes are keyed by directory-entry location, but deleted open files can coexist with reused slots.
- Root directory has no real on-disk entry and must be synthesized.
- FAT32 root handling differs from fixed FAT12/16 root directory handling.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/denode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/direntry.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/direntry.h

Defines DOS short directory entries, Win95 long-name entries, time/date bit layouts, and filename conversion APIs.

Key contents:
- `struct direntry` models 8.3 names, attributes, NT lowercase flags, timestamps, high/low start cluster fields, and file size.
- Defines slot markers for empty, deleted, and `0xe5` escape.
- Defines FAT attributes: read-only, hidden, system, volume, directory, archive.
- `struct winentry` models VFAT long-name slots and checksum fields.
- Defines `WIN_CHARS` and `WIN_MAXLEN`.
- Defines DOS time/date masks and shifts.
- Kernel section declares `mbnambuf` and DOS/VFAT conversion functions.

Risks and invariants:
- VFAT long-name entries are tied to short-name checksums.
- Long-name reassembly must preserve slot order and length limits.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/direntry.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/fat.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/fat.h

Defines FAT cluster constants, FAT-width helpers, EOF detection, and FAT manipulation APIs.

Key contents:
- Defines reserved/root/free/bad/EOF cluster constants.
- Defines FAT12, FAT16, and FAT32 masks and predicates.
- `MSDOSFSEOF()` normalizes EOF detection across FAT widths.
- Defines `FAT_GET`, `FAT_SET`, `FAT_GET_AND_SET`, and `DE_CLEAR`.
- Declares `pcbmap()`, `clusterfree()`, `clusteralloc()`, `fatentry()`, `freeclusterchain()`, `extendfile()`, `fc_purge()`, and volume-dirty marking.

Risks and invariants:
- FAT12/16/32 share logical APIs but require different bit packing in implementation.
- FAT32 high bits are masked/preserved by implementation code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/fat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_conv.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_conv.c

Implements FAT filename, VFAT long-name, checksum, multibyte buffer, and character-set conversion logic.

Key behavior:
- Provides static CP850/ISO-8859-1 conversion and case tables for non-iconv operation.
- `dos2unixfn()` converts 8.3 DOS names to Unix names, including `SLOT_E5` handling and lowercase flags.
- `unix2dosfn()` converts Unix names to DOS 8.3 names, classifies whether VFAT long-name entries are needed, and inserts generation suffixes.
- `unix2winfn()` emits VFAT long-name slots.
- `win2unixfn()` decodes VFAT slots into a multibyte name buffer and validates illegal slash characters.
- `winChkName()` compares case-insensitively against assembled long names.
- `winChksum()`, `winSlotCnt()`, and `winLenFixup()` support VFAT slot accounting.
- `dos2unixchr()`, `unix2doschr()`, `win2unixchr()`, and `unix2winchr()` use kernel iconv when mounted with conversion handles.
- `mbnambuf_*()` reassembles long-name substrings in descending slot order.

Risks and invariants:
- DOS short names reject disallowed characters and names made only of blanks/dots.
- VFAT names are limited to `WIN_MAXLEN`, and this implementation also rejects assembled names over 127 bytes.
- Iconv failures degrade to `?`, zero, or generation-required markers depending on direction.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_conv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_denode.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_denode.c

Implements MSDOSFS denode cache lifecycle, vnode creation, directory-entry updates, truncation/extension, inactive, and reclaim.

Key behavior:
- `msdosfs_init()` allocates the denode hash table and initializes `dehash_token`; `msdosfs_uninit()` frees it.
- `msdosfs_hashget()` looks up active denodes by device, directory cluster, and directory offset; it revalidates after `vget()`.
- `msdosfs_hashins()`, `msdosfs_hashrem()`, and `msdosfs_reinsert()` maintain the hash.
- `deget()` creates or finds locked denodes, synthesizes root denodes, reads real directory entries, initializes vnode type, file size, device vnode, and VM object.
- `deupdat()` applies deferred timestamp updates and writes changed directory entries.
- `detrunc()` shrinks files, zeros partial cluster tails, updates VM buffers and directory entries, breaks FAT chains, and frees removed clusters.
- `deextend()` allocates clusters to grow regular files and updates directory metadata.
- `msdosfs_inactive()` truncates and marks deleted unlinked files on writable mounts, then recycles stale/deleted nodes.
- `msdosfs_reclaim()` removes denodes from hash and frees resources.

Risks and invariants:
- Deleted but still-open files remain in cache with `de_refcnt <= 0` and must not be returned by lookups.
- Fixed FAT12/16 root directories cannot be extended or truncated.
- Directory size for subdirectories is derived by walking the FAT chain because on-disk directory entries store zero size.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_denode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_fat.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_fat.c

Implements FAT block addressing, file-cluster mapping, FAT cache maintenance, FAT entry updates, cluster allocation/freeing, file extension, and clean/dirty volume marking.

Key behavior:
- `fatblock()` maps a FAT byte offset to backing device block, size, and in-block offset.
- `pcbmap()` maps file-relative clusters to filesystem-relative blocks/clusters, using denode FAT cache entries.
- `fc_lookup()` and `fc_purge()` manage per-denode cluster mapping cache.
- `updatefats()` writes modified FAT blocks to mirrored FAT copies, writing the first/current FAT last.
- `fatentry()` gets/sets FAT12/16/32 entries, preserving FAT32 high bits and handling FAT12 nibble packing.
- `fatchain()` writes contiguous cluster chains efficiently.
- `clusteralloc()` and helpers allocate contiguous free clusters using `pm_inusemap`, `pm_nxtfree`, and fallback best run.
- `freeclusterchain()` walks and frees a cluster chain while updating FAT blocks and the in-use bitmap.
- `fillinusemap()` scans the FAT at mount time to build the free/used bitmap and validate the media descriptor.
- `extendfile()` appends allocated chains to files and optionally clears newly allocated clusters.
- `markvoldirty_upgrade()` sets/clears FAT16/FAT32 clean bits in cluster 1, with a read-only exception for rw upgrade.

Risks and invariants:
- Mount lock protects the in-use bitmap and free-cluster count.
- FAT12 updates are especially sensitive to odd/even cluster packing.
- Reserved and EOF markers are normalized across FAT widths.
- `fatentry()` does not update `pm_inusemap`; callers must keep FAT and bitmap consistent.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_fat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_iconv/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_iconv/Makefile

Builds the MSDOSFS iconv helper module.

Key contents:
- Sets `KMOD=msdos_iconv`.
- Builds `msdosfs_iconv.c`.
- Includes `<bsd.kmod.mk>`.

Risks and invariants:
- This module is only the iconv registration shim; core conversion logic lives in `msdosfs_conv.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_iconv/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_iconv/msdosfs_iconv.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_iconv/msdosfs_iconv.c

Registers MSDOSFS with the kernel iconv/VFS iconv framework.

Key contents:
- Includes kernel, module, mount, and iconv headers.
- Uses `VFS_DECLARE_ICONV(msdos)` to declare the MSDOSFS iconv integration symbol/module hook.

Risks and invariants:
- Provides registration only; all actual charset conversion behavior depends on the shared iconv framework and handles opened by MSDOSFS mount code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_iconv/msdosfs_iconv.c -->