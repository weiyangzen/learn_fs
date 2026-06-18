# Group Research: group_1239_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_cd9660_cd9660_rrip_c_so_2ec3aa20b755

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. All 31 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_rrip.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_rrip.c

Read completely: 709 lines.

Implements Rock Ridge Interchange Protocol support for NetBSD cd9660. The file is table-driven around `RRIP_TABLE` entries that map SUSP/RRIP field signatures (`PX`, `TF`, `PN`, `NM`, `SL`, `CL`, `PL`, `RE`, `RR`, `CE`, `ST`, `ER`) to parser callbacks and optional defaults.

`cd9660_rrip_loop()` is the core scanner. It computes the System Use area after the ISO directory name, applies root/non-root skip offsets, walks SUSP records, follows continuation areas through `CE`, bounds-checks continuation block/offset/length against volume size and logical block size, and calls default handlers for missing required attributes or timestamps.

The public entry points separate RRIP tasks: `cd9660_rrip_analyze()` fills inode mode, uid, gid, link count, device number, and timestamps; `cd9660_rrip_getname()` builds alternate names and handles relocated directories/child-parent links; `cd9660_rrip_getsymname()` assembles symbolic link components with current, parent, root, volume-root, host, and continuation semantics; `cd9660_rrip_offset()` validates `SP` and `ER` records before enabling Rock Ridge.

Important edge handling includes fallback to ISO names/timestamps when RRIP fields are absent, overflow protection for alternate names and symlink buffers, rejection of too-short `NM` entries, SUSP stop handling, and CD-ROM XA skip handling for `SP`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_rrip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_rrip.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_rrip.h

Read completely: 143 lines.

Defines the packed-ish C layouts used to interpret Rock Ridge and SUSP records embedded in ISO9660 directory records. `ISO_SUSP_HEADER` provides the common two-byte type, one-byte length, and one-byte version fields used by all parsers in `cd9660_rrip.c`.

The header covers RRIP structures for POSIX attributes (`PX`), device numbers (`PN`), symbolic links (`SL` plus `ISO_RRIP_SLINK_COMPONENT`), alternate names (`NM`), child/parent links (`CL`/`PL`), relocated directories (`RE`), timestamps (`TF`), RR flags (`RR`), extension references (`ER`), `SP` skip offsets, and continuation areas (`CE`).

It also defines component and timestamp flag constants used when constructing symlink paths and deciding whether timestamps are 7-byte ISO or 17-byte ASCII form. The structures intentionally use byte arrays and `ISODCL` ranges because ISO9660 fields are unaligned and often stored in ISO numeric encodings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_rrip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_util.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_util.c

Read completely: 260 lines.

Provides filename character handling for ISO9660 and Joliet. The global `cd9660_utf8_joliet` controls whether Joliet UCS-2 names are exposed as UTF-8 or reduced to an ISO-8859-1-like byte subset with nonrepresentable high-byte characters replaced by `?`.

`isochar()` decodes one on-disc ISO/Joliet filename character. `isofncmp()` compares a caller-supplied name against an ISO directory name, allowing omitted `;version` suffixes and doing ASCII case folding for ordinary ISO names. `isofntrans()` translates on-disc names to exported names, optionally preserving original `;version`, lowercasing, adding the associated-file `=` prefix, and stopping at version separators.

The internal `wget()` and `wput()` bridge caller names to/from UTF-8 for Joliet via `<fs/unicode.h>`. The file is usable in kernel and selected tool builds, with userland includes guarded for `macppc_installboot`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_vfsops.c

Read completely: 931 lines.

Implements cd9660 VFS operations and module registration. `cd9660_vfsops` wires mount, unmount, root, statvfs, vnode-cache loading, file-handle conversion, init/done, and mountroot operations, and the module attaches/detaches the filesystem with `vfs_attach()`/`vfs_detach()`.

Mounting is strictly read-only. `cd9660_mount()` validates mount arguments, supports legacy mount data size, handles `MNT_GETARGS`, rejects writable mounts, resolves and authorizes the block device, opens it for reading, and delegates initial filesystem parsing to `iso_mountfs()`. Updates are limited to verifying the same device and unchanged uid/gid/mask policy.

`iso_mountfs()` invalidates old buffers, reads ISO volume descriptors from sector 16 onward, accepts a primary descriptor and optional supplementary descriptor, builds `struct iso_mnt`, records block size/shift/root metadata, detects Rock Ridge through `cd9660_rrip_offset()`, and only falls back to Joliet when Rock Ridge is disabled or unavailable. It also handles session offsets from disklabel or CD-ROM multisession ioctl.

`cd9660_loadvnode()` allocates an `iso_node`, finds the directory record by inode-number-as-directory-record-offset, validates block boundaries, reads ISO/RRIP attributes and timestamps, assigns vnode type and operation vector, initializes spec/fifo nodes when needed, and marks the root vnode. NFS file handles carry inode offsets without generation validation beyond checking mode presence.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_vnops.c

Read completely: 924 lines.

Implements cd9660 vnode operations for access checks, attributes, reads, directory iteration, symlink reads, block strategy, pathconf, and limited setattr behavior. Operation tables are provided for regular cd9660 vnodes plus special-device and FIFO vnodes.

Access is read-only for directories, regular files, and symlinks; write is only allowed to pass through resident socket/fifo/device style nodes where the generic vnode layer supports it. Permission checks apply mount-supplied uid/gid overrides and file/directory masks before delegating to kauth/genfs.

Regular file reads use UBC with read advice, while non-regular paths use buffer reads and readahead. `cd9660_readdir()` walks ISO directory records block by block, validates record sizes and block boundaries, translates names through RRIP or ISO/Joliet helpers, synthesizes `.`/`..`, handles associated file ordering in default ISO mode, and returns cookies when requested.

`cd9660_readlink()` rereads the directory record containing the symlink inode and extracts RRIP `SL` content. `cd9660_strategy()` maps logical blocks through `VOP_BMAP` before forwarding to the device vnode. `cd9660_setattr()` rejects all attribute changes except size changes for device/fifo vnode cases.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/iso.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/iso.h

Read completely: 247 lines.

Defines ISO9660 on-disc structures and numeric accessors. The main layouts are `iso_volume_descriptor`, `iso_primary_descriptor`, `iso_supplementary_descriptor`, `iso_directory_record`, and `iso_extended_attributes`, all represented with byte arrays sized by the `ISODCL(from,to)` macro.

The file declares volume descriptor types, standard IDs (`CD001`, `CDW01`), default block size, maximum name length, root directory record layout, and the associated-file prefix `ASSOCCHAR`.

Inline `isonum_*` helpers decode ISO 711/712 one-byte values, 721/722/723 16-bit little/big/both-endian values, and 731/732/733 32-bit little/big/both-endian values. For both-endian fields, the helper chooses the native-endian half at compile time.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/iso.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/iso_rrip.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/iso_rrip.h

Read completely: 85 lines.

Defines RRIP/SUSP analysis bit flags used by `cd9660_rrip.c`. Flags identify parsed or requested fields such as attributes, device numbers, symlinks, alternate names, child/parent links, relocated directories, timestamps, RR flags, extension references, continuations, offsets, stop records, and unknown fields.

Defines `ISO_RRIP_ANALYZE`, the shared state object passed through RRIP parser callbacks. It carries the target inode, wanted fields mask, continuation location, mount pointer, output inode number pointer, output buffer and length tracking, max length, and continuation state for multi-record symlink/name assembly.

The header exports the four RRIP entry points used by the rest of cd9660: analyze inode metadata, get alternate name, get symlink target, and detect RRIP offset.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/iso_rrip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/Makefile

Read completely: 8 lines.

Installs the public EFS kernel headers under `/usr/include/fs/efs`.

The installed headers are `efs.h`, `efs_sb.h`, and `efs_mount.h`, and the file delegates installation mechanics to `bsd.kinc.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs.h

Read completely: 153 lines.

Top-level SGI EFS format header. It documents the Extent File System layout: 512-byte basic blocks, boot/reserved block 0, superblock at block 1, bitmap placement, cylinder groups, inode areas, data extents, direct versus indirect extent descriptors, and big-endian on-disc assumptions.

Defines basic block constants and conversions (`EFS_BB_SHFT`, `EFS_BB_SIZE`, `EFS_BB2BY`, `EFS_BY2BB`), fixed layout offsets, and the 8 GB filesystem limit derived from the 24-bit extent block number.

For kernel builds it defines `VFSTOEFS()` and debug-print plumbing. The header is mostly explanatory but establishes the invariants used by the EFS mount, inode, and extent code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_dinode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_dinode.h

Read completely: 133 lines.

Defines the 128-byte EFS on-disc inode format. `struct efs_dinode` stores mode, link count, 16-bit uid/gid, byte size, access/modify/change times, generation, extent count, version, and a union for direct/indirect extents, inline symlink content, or special-device numbers.

The inode supports twelve direct extent descriptors in `di_extents`. When `di_numextents` exceeds `EFS_DIRECTEXTENTS`, these descriptors identify indirect extent blocks, with the first descriptor’s offset carrying the indirect extent count. Zero-extent symlinks can store the target inline in the union.

The header defines root inode number, inode size/count per basic block, old/new device-number extraction macros, and EFS file type/permission constants corresponding to IRIX on-disc mode bits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_dir.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_dir.h

Read completely: 185 lines.

Defines the EFS directory block and directory entry layout. A directory block is 512 bytes with magic `0xbeef`, a first-used offset, a slot count, and a shared `db_space` area containing compacted entry offsets, free space, and variable-length entries.

Directory entry offsets are stored right-shifted by one because entries are even-aligned. `EFS_DIRENT_OFF_EXPND`, `EFS_DIRENT_OFF_COMPT`, and `EFS_DIRENT_OFF_VALID` handle this encoding. Slot zero means free.

`struct efs_dirent` stores a big-endian inode number plus an unterminated variable-length name. `EFS_DIRENT_SIZE()` computes the padded entry size needed for 16-bit alignment. The extensive comments explain insertion/removal/free-space behavior and IRIX compatibility assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_extent.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_extent.h

Read completely: 64 lines.

Defines EFS extent descriptors. `struct efs_dextent` represents the packed on-disc 8-byte bitfield-like format with an 8-bit magic value, 24-bit filesystem block number, 8-bit length, and 24-bit logical file offset.

Because portable C bitfield layout is unreliable, the implementation accesses `ex_bytes` and `ex_words` and converts to `struct efs_extent`, an in-core unsquished representation with normal integer fields.

Constants define the expected extent magic value, masks for 24-bit fields, and the number of extent descriptors per 512-byte basic block.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_extent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_genfs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_genfs.c

Read completely: 54 lines.

Defines the EFS `genfs_ops` table used when vnodes are initialized. It uses `genfs_size`, `genfs_gop_write`, and `genfs_gop_putrange`, while wiring allocation to `efs_gop_alloc()`.

`efs_gop_alloc()` currently returns success without allocating backing storage. This is acceptable for the read-oriented implementation but means callers should not interpret it as a real block allocation routine for writable EFS.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_genfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_genfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_genfs.h

Read completely: 26 lines.

Declares the EFS genfs integration points: external `efs_genfsops` and `efs_gop_alloc()`.

This small header lets the VFS/vnode loading path initialize EFS vnodes with the filesystem’s genfs operations table.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_genfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_inode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_inode.h

Read completely: 73 lines.

Defines the in-core EFS inode. `struct efs_inode` embeds a genfs node, advisory lock pointer, inode identity/device/vnode pointers, cached host-order metadata fields, and a verbatim copy of the on-disc `efs_dinode`.

The cached fields mirror the disk inode with NetBSD-native types and byte order: mode, nlink, uid, gid, size, times, generation, extent count, and version. Conversion is performed by helpers in `efs_subr.c`.

Also defines `EFS_VTOI()`/`EFS_ITOV()` and the NFS file-handle payload `struct efs_fid`, which carries inode number and generation after the standard `fid` prefix.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_mount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_mount.h

Read completely: 40 lines.

Defines user mount arguments and the in-kernel EFS mount structure. `struct efs_args` carries the block-device path and a version field, with `EFS_MNT_VERSION` currently zero.

In kernel builds, `struct efs_mount` stores the in-core superblock copy, mounted device number, mount pointer, and block-device vnode pointer. This is the object reached through `VFSTOEFS(mp)`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_sb.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_sb.h

Read completely: 70 lines.

Defines the 92-byte EFS superblock. Fields include filesystem size, first cylinder group, cylinder group size, inode blocks per group, geometry, cylinder group count, dirty flag, timestamp, magic, volume names, bitmap size/free counts, bitmap block for grown filesystems, replicated superblock block, last inode, spare bytes, and checksum.

Defines original and grown-filesystem magic values (`EFS_SB_MAGIC`, `EFS_SB_NEWMAGIC`), checksum size excluding the checksum field, and the clean dirty-flag value.

The comments capture IRIX-version nuances, including grown filesystems, replicated superblocks, and historical checksum variants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_subr.c

Read completely: 623 lines.

Provides EFS support routines for superblock validation, inode reads, byte-order conversion, directory lookup, extent conversion, and extent iteration. It owns the global `efs_inode_pool`.

`efs_sb_checksum()` implements SGI’s old/new checksum variants over the superblock. `efs_sb_validate()` checks magic, checksum, maximum size, first cylinder group, and basic nonzero geometry/bitmap fields. `efs_locate_inode()` maps an inode number to a cylinder-group inode block and index, and `efs_read_inode()` reads the containing block and copies the target dinode.

`efs_sync_dinode_to_inode()` converts big-endian disk inode fields to host-order cached fields. The inverse `efs_sync_inode_to_dinode()` panics because this implementation is effectively read-only. Under diagnostics, `efs_is_inode_synced()` checks cache consistency.

Directory lookup walks EFS directory blocks through extents: `efs_dirblk_lookup()` scans slots, compares component names, and returns a big-endian decoded inode; `efs_extent_lookup()` reads each directory block in an extent; `efs_inode_lookup()` iterates all directory extents. Extent conversion helpers decode/encode the 24-bit packed extent fields, and the iterator supports direct extents, indirect extent vectors, optional start hints, and binary search into indirect extents.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_subr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_subr.h

Read completely: 48 lines.

Declares the EFS inode pool, extent iterator state, and helper routines implemented in `efs_subr.c`.

The iterator tracks the inode, next logical extent, next direct extent, and next indirect extent index. Prototypes cover superblock checksum/validation, inode location/read, extent conversion, directory lookup, block reads, inode sync conversion, and extent iterator initialization/advance.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_subr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_vfsops.c

Read completely: 595 lines.

Implements EFS VFS operations and module registration. The module registers `efs_vfsops`, malloc types, vnode operation vectors, and the inode pool lifecycle.

`efs_mount()` rejects updates, resolves and locks the block device, authorizes read access, opens it read-only, and calls `efs_mount_common()`. Common mount code reads the superblock, validates checksum and geometry, warns on dirty filesystems, verifies replicated superblocks when present, checks the last filesystem block is accessible, fills mount flags/stat data, and records the device vnode.

`efs_loadvnode()` allocates an in-core inode, reads the disk inode, converts it to host order, validates that the root inode is a directory, selects vnode type and operation vector for fifo/device/dir/reg/symlink/socket, initializes genfs state, and sets the vnode size. Device vnodes use decoded device metadata later in getattr, though the load path initializes spec nodes with `ei_dev`.

File handles include inode and generation; `efs_fhtovp()` rejects stale handles when mode is zero or generation mismatches. `efs_statvfs()` reports block counts and inode capacity from the superblock, and unmount flushes vnodes, closes the device, and frees the mount.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_vnops.c

Read completely: 896 lines.

Implements EFS vnode operations. Lookup checks execute permission, consults the name cache, handles `.`, searches directory extents with `efs_inode_lookup()`, returns `EJUSTRETURN` only for impossible write/create style paths after access checks, and caches positive or negative results.

Access uses kauth/genfs with inode uid/gid/mode and rejects writes on read-only mounts. Getattr exposes inode metadata, block size, times, generation, and decodes old or new EFS special-device numbers for `va_rdev`.

Regular file reads walk extents and use UBC to transfer ranges that overlap the current extent. Readdir walks directory extents and directory-block slots, validates magic and slot offsets, creates `dirent` records, and reads each target inode to determine `d_type`. Readlink supports inline symlinks stored in the inode union and symlink data stored in extents, returning a NUL-terminated buffer through `uiomove()`.

`efs_bmap()` maps logical EFS basic blocks through the extent iterator and reports run length. `efs_strategy()` resolves logical blocks then forwards I/O to the mounted device. The vnode op tables are read-only for namespace and file modification, while special and FIFO tables pass through appropriate genfs/spec/fifo operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/efs/efs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/Makefile

Read completely: 7 lines.

Installs FileCoreFS public kernel headers under `/usr/include/filecorefs`.

Only `filecore_mount.h` is installed, through `bsd.kinc.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore.h

Read completely: 152 lines.

Defines Acorn FileCore on-disc structures and constants for kernel use. It describes boot block offsets, directory size and entry size, maximum directory entries, root inode sentinel, and the synthetic inode encoding where high bits contain a directory entry index and low bits contain a FileCore address.

`struct filecore_disc_record` models the boot/map disc record, including sector geometry, fragment id width, map layout, root directory address, disc size, name, type, and large-disc fields. Directory records are represented by `filecore_direntry`, `filecore_dirhead`, and `filecore_dirtail`.

The file also defines FileCore attribute bits for read/write/directory/owner access and macros to locate directory header, entries, and tail within the fixed 2048-byte directory block.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_bmap.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_bmap.c

Read completely: 270 lines.

Implements FileCore logical-to-physical block mapping and related read helpers. `filecore_bmap()` supplies the underlying device vnode, computes a conservative readahead run length, and maps a file logical block through `filecore_map()` using the file’s directory-entry address.

`filecore_map()` decodes FileCore fragment and sector addressing, identifies the map zone, reads map sectors, scans variable-length allocation runs encoded in bit fields, and translates a logical block within a fragment to a physical device block. It wraps through zones and returns `E2BIG` if no matching allocation run is found.

`filecore_bread()` maps a FileCore address to its first physical block and reads a requested size from the device. `filecore_dbread()` caches the mapped first block for a directory node and reads the fixed 2048-byte directory body.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_extern.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_extern.h

Read completely: 113 lines.

Declares kernel-private FileCoreFS mount state and shared prototypes. `struct filecore_mnt` stores the mount/device, block size and shift, map location, ids per zone, id mask, block count, mount uid/gid/policy flags, and cached disc record.

Defines `VFSTOFILECORE()` and block offset/number/size macros used by vnode read and bmap code. It also declares the node pool, VFS prototypes, vnode op vector, boot-block checksum, mapped read, and map translation helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_lookup.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_lookup.c

Read completely: 286 lines.

Implements FileCore pathname lookup. It follows a UFS-like lookup outline but is read-only: it checks directory execute permission, rejects delete/rename on read-only final components, consults the name cache, then linearly scans the fixed-size FileCore directory entries.

The scan can begin at `i_diroff` from a previous successful lookup and wrap once for a second pass. Names are compared with `filecore_fncmp()`, which handles FileCore’s name encoding and case behavior. `.` returns the directory vnode itself, and `..` resolves through `filecore_getparent()`.

For normal entries, the child inode number is synthesized from the parent directory’s FileCore address plus the directory entry index shifted into the high inode bits. Missing names are cached negatively and return `EROFS` for create/rename attempts or `ENOENT` otherwise.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_mount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_mount.h

Read completely: 92 lines.

Defines user mount arguments for Acorn FileCore filesystems. `struct filecore_args` carries the block-device path, a compatibility export-args padding field, uid/gid ownership to expose, and FileCore mount flags.

The mount flags control access interpretation and presentation: owner-only access, all-access, forced owner read, using the mounting user’s uid/gid, and optionally including file type in names. `FILECOREMNT_BITS` provides a printable bit description.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_node.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_node.c

Read completely: 258 lines.

Manages FileCore in-core nodes and vnode loading. It owns `filecore_node_pool` and initializes vnodes with a minimal genfs ops table using `genfs_size`.

`filecore_loadvnode()` allocates a node from the pool, records the synthetic inode number, device, mount, and cached device vnode, and either fabricates the root directory entry from the disc record root address or reads the parent directory block and copies the indexed directory entry. It sets vnode tag, operation vector, type (`VDIR` for directory attribute, otherwise `VREG`), root flag, genfs state, and vnode size.

`filecore_inactive()` marks stale nodes for recycling when the directory entry name is zero. `filecore_reclaim()` drops the held device vnode reference, destroys genfs state, returns the node to the pool, and clears `v_data`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_node.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_node.h

Read completely: 133 lines.

Defines the in-core FileCore node. `struct filecore_node` embeds genfs state, vnode/device identity, synthetic inode number, cached physical block, cached parent inode, mount pointer, advisory lock pointer, directory lookup offset, and the copied FileCore directory entry.

The node exposes `i_size` as the directory entry length and defines stale-node detection as an empty directory-entry name. It also declares vnode operation prototypes and utility helpers for mode conversion, timestamp conversion, parent lookup, filename conversion/comparison, and directory block reads.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_utils.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_utils.c

Read completely: 356 lines.

Provides FileCore utility functions. `filecore_bbchecksum()` validates the 512-byte boot block checksum while rejecting degenerate blocks containing all identical bytes, because such blocks would otherwise checksum trivially.

`filecore_mode()` maps FileCore read/owner-read/directory attributes plus mount policy flags into NetBSD mode bits, including directory execute bits and regular-vs-directory file type. `filecore_time()` converts FileCore load/exec timestamp fields into a `timespec` using the RISC OS centisecond epoch adjustment.

`filecore_getparent()` resolves and caches a directory’s parent by reading the directory tail and, when needed, scanning the grandparent directory for the entry pointing back to the current directory. Root’s parent is itself. `filecore_fn2unix()` converts FileCore names to Unix names by replacing `/` with `.`, and `filecore_fncmp()` performs case-insensitive comparison with Unix `.` mapped back to FileCore `/`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_vfsops.c

Read completely: 594 lines.

Implements FileCoreFS VFS operations and module registration. `filecore_vfsops` registers mount, unmount, root, statvfs, sync, vget/loadvnode, file-handle conversion, init/reinit/done, and vnode operation descriptors. A sysctl node is created for the filesystem.

`filecore_mount()` is read-only, supports `MNT_GETARGS`, resolves and authorizes the block device, and delegates new mounts to `filecore_mountfs()`. Updates only verify the same device. `filecore_mountfs()` invalidates old buffers, opens the device, reads and validates the FileCore boot block checksum, extracts the disc record, computes the map location, rereads the map’s boot block/disc record, builds `struct filecore_mnt`, computes block size, id geometry, mask, total block count, uid/gid policy, and mount stat fields.

Unmount flushes vnodes, clears mountedfs on the device vnode, closes the device, frees the mount, and clears `MNT_LOCAL`. Root lookup returns the synthetic `FILECORE_ROOTINO` vnode. `filecore_statvfs()` reports block geometry and total blocks but not free/file counts.

File handles carry only the synthetic inode number. `filecore_fhtovp()` rejects stale nodes whose copied directory entry name is empty; `filecore_vptofh()` serializes the inode into the handle.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_vfsops.c -->