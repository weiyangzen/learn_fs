# Group Research: group_1463_parted_sources_block_storage_parted_libparted_fs_r_hfs_reloc_c_sour_efbce3ad5d11

Scope verified against `Docs/research_subset_a.md`: `sources/block-storage/parted` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/reloc.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/reloc.c

Purpose: Implements classic HFS extent relocation for libparted resize/compaction support when `DISCOVER_ONLY` is not set. It moves allocation blocks, updates extent references in the MDB, catalog B-tree, and extents-overflow B-tree, and compacts used extents away from a requested free-space region.

Main interfaces: `hfs_update_mdb()` rewrites primary and alternate master directory blocks. `hfs_pack_free_space_from_block()` is the exported compaction entry point declared in `reloc.h`.

Control flow: `hfs_pack_free_space_from_block()` builds an in-memory extent cache from MDB/catalog/extent trees, sizes the shared copy buffer, loads bad-block metadata, scans allocation blocks from `fblock`, and uses `hfs_move_extent_starting_at()` for occupied non-bad extents. `hfs_effect_move_extent()` finds a non-overlapping destination before/in the gap/after source, copies chunks via `ped_geometry_read/write`, and updates the allocation bitmap. `hfs_do_move()` then rewrites the owning extent descriptor and moves the cache entry.

Dependencies: HFS private structs from `hfs.h`, file access from `file.h`, advanced HFS helpers from `advfs.h`, cache operations from `cache.h`, endian helpers, `PedGeometry`, `PedTimer`, and libparted exceptions.

Important details and risks: Relocation is not atomic: data, extent references, and allocation bitmap writes can be partially committed, though comments rely on the HFS unmounted bit for protection. Extents overflow self-extents can be cached as `CR_BTREE_EXT_EXT`, but `hfs_do_move()` has no explicit handler for that case after the warning path. Progress divisor depends on `to_free`; invalid caller inputs could make progress reporting misleading. Test coverage should include MDB-only extents, catalog file/data/resource extents, overflow extents, bad-block avoidance, two-pass relocation, and simulated write failures.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/reloc.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/reloc.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/reloc.h

Purpose: Public header for classic HFS relocation helpers.

Exports: `hfs_update_mdb(PedFileSystem *fs)` and `hfs_pack_free_space_from_block(PedFileSystem *fs, unsigned int fblock, PedTimer *timer, unsigned int to_free)`.

Dependencies: Includes libparted core, endian/debug headers, and `hfs.h`.

Important details and risks: The header exposes only the MDB update and pack operation; all cache-building and low-level extent movement remain private to `reloc.c`. Callers need a fully initialized HFS `PedFileSystem` with valid private data and allocation map.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/reloc.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/reloc_plus.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/reloc_plus.c

Purpose: Implements HFS+ extent relocation and free-space packing for resize/compaction when `DISCOVER_ONLY` is disabled. It is the HFS+ analog of `reloc.c`, extended for 32-bit allocation blocks, HFS+ volume-header fork records, attributes B-tree, and journal metadata.

Main interfaces: `hfsplus_update_vh()` rewrites primary and alternate HFS+ volume headers. `hfsplus_pack_free_space_from_block()` is the exported compaction entry point declared in `reloc_plus.h`.

Control flow: `hfsplus_pack_free_space_from_block()` caches extents from the volume header, catalog B-tree, extents overflow B-tree, and attributes B-tree. It then scans occupied allocation blocks and calls `hfsplus_move_extent_starting_at()`, which may do a second relocation pass if a temporary post-source destination was used. `hfsplus_do_move()` updates the relevant volume-header fork, B-tree node, opened file cache, and journal info block/location when the moved extent is journal-related.

Dependencies: HFS+ private structures from `hfs.h`, I/O helpers from `file_plus.h`, bad-block helpers from `advfs_plus.h`, relocation cache from `cache.h`, journal helpers from `journal.h`, libparted geometry/timer/exception APIs, and endian helpers.

Important details and risks: Allocation bitmap persistence is tracked with `dirty_alloc_map` and flushed by sector through the allocation file. B-tree node sizes are read dynamically and allocated with `ped_malloc`; malformed record offsets are checked before use. Extents-overflow self-extents can be cached as `CR_BTREE_EXT_EXT` after a warning, but `hfsplus_do_move()` has no explicit case for moving that reference. Relocation is multi-write and not crash atomic. Tests should cover catalog data/resource forks, attributes fork records, startup/allocation/catalog/extents VH forks, journal info blocks, dirty allocation bitmap flushing, two-pass moves, and failure injection in B-tree rewrites.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/reloc_plus.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/reloc_plus.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/reloc_plus.h

Purpose: Public header for HFS+ relocation helpers.

Exports: `hfsplus_update_vh(PedFileSystem *fs)` and `hfsplus_pack_free_space_from_block(PedFileSystem *fs, unsigned int fblock, PedTimer *timer, unsigned int to_free)`.

Dependencies: Includes libparted core, endian/debug headers, and `hfs.h`.

Important details and risks: The API assumes HFS+ private data, `plus_geom`, volume header, open metadata files, and allocation maps are already initialized by the HFS+ resize stack.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/reloc_plus.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/reiserfs/reiserfs.c -->
# File Research: sources/block-storage/parted/libparted/fs/reiserfs/reiserfs.c

Purpose: Detection-only ReiserFS filesystem backend for libparted.

Main interfaces: Registers a `PedFileSystemType` named `reiserfs` with only a `probe` operation. `ped_file_system_reiserfs_init()` registers it; `ped_file_system_reiserfs_done()` unregisters it.

Control flow: `reiserfs_probe()` reads candidate superblock sectors at offsets 128 and 16. If any recognized ReiserFS magic string matches, it computes filesystem length from little-endian block size and block count and returns a new geometry.

Dependencies: `reiserfs.h` for the superblock layout and magic strings, libparted geometry APIs, endian helpers, and UUID/header includes.

Important details and risks: It does not validate checksums or deeper ReiserFS metadata, so detection is signature-and-size based. Geometry sizing assumes superblock block-size fields are sane and divisible by device sector size. Tests should include old/new ReiserFS signatures at both supported offsets and short/truncated geometries.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/reiserfs/reiserfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/reiserfs/reiserfs.h -->
# File Research: sources/block-storage/parted/libparted/fs/reiserfs/reiserfs.h

Purpose: Minimal ReiserFS on-disk definitions used by libparted probing.

Content: Defines ReiserFS magic strings, default block size, `struct reiserfs_super_block`, exception/gauge compatibility typedefs, format constants, journal constants, and hash identifiers.

Dependencies: Relies on fixed-width integer types being available from including translation units.

Important details and risks: Most declarations are compatibility leftovers and are not consumed by current `reiserfs.c`; the active probe depends primarily on `s_block_count`, `s_blocksize`, and `s_magic`. The struct layout must remain aligned with the on-disk superblock fields used by old ReiserFS formats.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/reiserfs/reiserfs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/udf/udf.c -->
# File Research: sources/block-storage/parted/libparted/fs/udf/udf.c

Purpose: Detection-only UDF filesystem backend.

Main interfaces: `udf_probe()` returns a duplicate of the input geometry when UDF is detected. `ped_file_system_udf_init()` and `_done()` register/unregister the `udf` type.

Control flow: `detect_udf()` requires both a Volume Recognition Sequence with `NSR02` or `NSR03` and a valid Anchor Volume Descriptor Pointer. It checks VRS descriptors beginning at byte offset 32768, first using 2048-byte VSD units for block sizes up to 2048, then larger block sizes through 32768. AVDP locations are tried at block 256, block -257, last block, and block 512.

Dependencies: Uses only libparted geometry reads plus stack scratch buffers through `alloca`.

Important details and risks: The probe intentionally returns the whole input geometry rather than deriving a smaller filesystem span. `read_bytes()` handles unaligned byte reads through sector-aligned `ped_geometry_read()`. Tests should include optical-style 2048-byte media, 512-byte block UDF, larger-block UDF, missing VRS, missing anchor, and anchors near small-device boundaries.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/udf/udf.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/ufs/ufs.c -->
# File Research: sources/block-storage/parted/libparted/fs/ufs/ufs.c

Purpose: Detection-only UFS backend for Sun and HP UFS variants.

Main interfaces: Registers two filesystem types, `sun-ufs` and `hp-ufs`, each with a probe operation.

Control flow: Both probes read the UFS superblock area around offset 16 * 512 bytes. `ufs_probe_sun()` accepts the standard UFS magic in either big-endian or little-endian form. `ufs_probe_hp()` accepts HP magic variants `UFS_MAGIC_LFN`, `UFS_MAGIC_FEA`, and `UFS_MAGIC_4GB`, again in either endian form. Successful probes compute returned geometry from `fs_bsize / sector_size * fs_size`.

Dependencies: The file embeds a packed UFS superblock layout adapted from Linux `ufs_fs.h`, uses libparted geometry/endian/debug APIs, and registers file system types with libparted.

Important details and risks: The struct-size assertion guards layout drift. Detection is magic-and-size based and does not verify secondary consistency. Reads assume the superblock spans three 512-byte sectors rounded to the device sector size. Tests should cover endian variants, HP-specific magics, devices shorter than five sectors, and unusual sector sizes.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/ufs/ufs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/xfs/platform_defs.h -->
# File Research: sources/block-storage/parted/libparted/fs/xfs/platform_defs.h

Purpose: Local platform compatibility header imported from older XFS userspace code.

Content: Includes standard C/system headers, defines XFS scalar aliases such as `xfs_off_t`, `xfs_ino_t`, `xfs_dev_t`, `xfs_daddr_t`, and pointer-sized integer aliases `__psint_t`/`__psunsigned_t` based on configured pointer width. It also maps `ASSERT` to `assert` only under `DEBUG`.

Dependencies: Assumes glibc/endian/system type availability and configure-time width macros, here fixed to 32-bit long and 32-bit pointer.

Important details and risks: This is compatibility scaffolding for the imported XFS headers used by the simple probe; it is not a complete modern xfsprogs platform layer. The hard-coded pointer-size macros are notable if reused beyond the current narrow probe build context.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/xfs/platform_defs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/xfs/xfs.c -->
# File Research: sources/block-storage/parted/libparted/fs/xfs/xfs.c

Purpose: Detection-only XFS filesystem backend.

Main interfaces: Registers a `PedFileSystemType` named `xfs` with probe operation `xfs_probe()`.

Control flow: `xfs_probe()` reads the superblock at `XFS_SB_DADDR` and checks `sb_magicnum` against `XFS_SB_MAGIC` in little-endian and big-endian forms. On match, it derives filesystem length from `sb_blocksize / sector_size * sb_dblocks` and returns a new geometry.

Dependencies: Uses libparted geometry/endian APIs, UUID headers, and imported `platform_defs.h`, `xfs_types.h`, and `xfs_sb.h`.

Important details and risks: XFS on disk is normally big-endian, but this code accepts both endian interpretations. It does not validate superblock version, sector size, UUID, AG geometry, or checksums. Tests should include valid big-endian XFS, bogus magic, too-short geometry, and corrupted block-size/count fields.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/xfs/xfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/xfs/xfs_sb.h -->
# File Research: sources/block-storage/parted/libparted/fs/xfs/xfs_sb.h

Purpose: Imported XFS superblock definitions and version/feature macros used by the XFS probe and potentially by older XFS utility code.

Content: Defines `XFS_SB_MAGIC`, version constants, feature-bit masks, `xfs_sb_t` layout, field-number enum, superblock field bit masks, feature test/add/subtract macros, and block/basic-block/byte conversion macros.

Dependencies: Depends on XFS integer types from `xfs_types.h`, `uuid_t`, and optional `XFS_WANT_FUNCS`/`XFS_WANT_SPACE` macro regimes.

Important details and risks: The active libparted probe uses only the superblock struct, magic, blocksize, and dblocks. Many macros are legacy imported logic and are not compiled into functions unless external feature macros request it. The header represents an older XFS format generation and should not be treated as a complete modern XFS feature model.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/xfs/xfs_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/xfs/xfs_types.h -->
# File Research: sources/block-storage/parted/libparted/fs/xfs/xfs_types.h

Purpose: Imported XFS core type definitions used by `xfs_sb.h`.

Content: Defines allocation group, extent, filesystem block, realtime block, file offset, transaction/log, directory/hash, project ID, null sentinel, max extent constants, lookup and btree enums, optional statistics macros, and kernel-only IRIX device helpers.

Dependencies: Requires fixed-width integer types and is shaped by `XFS_BIG_FILES` and `XFS_BIG_FILESYSTEMS`, both enabled here.

Important details and risks: For libparted’s XFS probe, this header mainly ensures the superblock structure has the expected field widths. Much of the statistics and kernel-only material is unused in this tree. Reuse outside the probe should account for the age of these definitions relative to modern XFS.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/xfs/xfs_types.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/Makefile.am -->
# File Research: sources/block-storage/parted/libparted/labels/Makefile.am

Purpose: Automake build definition for libparted disk-label backends.

Content: Builds `liblabels.la` from common label sources, conditionally includes S390/DASD sources when `COMPILE_FOR_S390` is true, wires include paths and libraries, and generates `pt-limit.c` from `pt-limit.gperf`.

Important details: The gperf output is post-processed with Perl to add `static` before `__GNUC_STDC_INLINE__`, then installed as a read-only generated file. `pt-limit.c` is a built source included by `pt-tools.c`, not compiled independently.

Risks/tests: Build correctness depends on gperf availability for maintainer builds and on `S390_SRCS` matching platform configuration. Dist and maintainer-clean rules must keep generated and source gperf files in sync.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/aix.c -->
# File Research: sources/block-storage/parted/libparted/labels/aix.c

Purpose: Minimal AIX disk-label backend with probing support and unsupported operation stubs.

Main interfaces: Registers `PedDiskType` named `aix`. `aix_probe()` checks sector 0 for big-endian magic `0xc9c2d4c1`. Standard disk and partition callbacks are present through `pt-common.h`.

Control flow: Allocation creates an empty `PedDisk`; duplicate creates a fresh empty AIX disk. Read, write, partition creation, duplication, system setting, and flag setting throw `PED_EXCEPTION_NO_FEATURE` and fail. Max supported partitions is reported as 16, while max primary count returns 4.

Dependencies: Uses libparted disk abstractions, endian helpers, `pt-tools.h`, and generated limit functions from `pt-common.h`.

Important details and risks: This backend can recognize AIX labels but cannot safely inspect or modify them. Any user path expecting actual AIX partition enumeration will receive an unsupported error. Tests should verify probe behavior and that mutation/read APIs fail cleanly without partial state.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/aix.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/atari.c -->
# File Research: sources/block-storage/parted/libparted/labels/atari.c

Purpose: Full Atari partition-table backend supporting AHDI, ICD, and XGM-style extended/logical layouts.

Main interfaces: Registers `PedDiskType` named `atari` with extended-partition support. Implements probe, alloc, duplicate, free, read, clobber, write, partition allocation/duplication/destruction, system mapping, boot flag handling, alignment, numbering, metadata allocation, and partition limit reporting.

Control flow: `atari_probe()` validates a magic-less format by reading the root sector, checking disk size and bad-sector-list fields, validating AHDI primary entries, rejecting invalid/multiple/slot-zero XGM layouts, walking XGM auxiliary root sectors, and optionally validating ICD entries. `atari_read()` parses AHDI primaries, XGM logical chains, or ICD entries into `PedPartition`s. `atari_write()` preserves bootability, fixes stored device size when requested, fills AHDI/ICD entries, writes XGM ARS sectors, writes the root sector, and initializes an HDX-compatible bad-sector list if needed.

Data model: `AtariRawTable` is exactly one 512-byte sector containing boot code, ICD entries, disk size, four AHDI entries, BSL fields, and checksum. `AtariDisk` tracks current mode, BSL location, and whether content has been read/written. `AtariPart` tracks 3-character Atari and ICD partition IDs plus boot flags.

Important details and risks: The backend has complex numbering rules: XGM extended partitions use libparted number 0, logical partitions may force renumbering of following primaries, and ICD mode is incompatible with XGM. Bootability is represented by a root-sector checksum, with safeguards against DOS-like forbidden signatures for non-boot sectors. Alignment avoids the bad-sector-list range and reserves ARS metadata sectors before logical partitions. Tests should cover empty signed labels, AHDI-only layouts, ICD overflow primaries, XGM logical chains, BSL conflicts, boot checksum preservation, partition ID mapping, and max-partition limits.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/atari.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/bsd.c -->
# File Research: sources/block-storage/parted/libparted/labels/bsd.c

Purpose: BSD disklabel backend for reading and writing classic 8-slot BSD labels.

Main interfaces: Registers `PedDiskType` named `bsd`. Implements probe, alloc, duplicate, free, read, write, partition allocation/duplication/destruction, system mapping, boot/RAID/LVM flags, alignment, enumeration, and metadata reservation.

Control flow: `bsd_probe()` reads sector 0 and checks the label at offset 64 for little-endian `BSD_DISKMAGIC`. `bsd_alloc()` initializes a default SCSI-style label from BIOS geometry. `bsd_read()` copies sector-zero label data and creates active partitions from nonzero size/type entries. `bsd_write()` optionally preserves existing boot code, clears and refills raw partition entries, updates `d_npartitions`, computes the XOR checksum, computes Alpha bootblock checksum, writes sector data, and syncs.

Data model: `BSDDiskData` contains 64 bytes of boot code, a packed `BSDRawLabel`, and trailing unused bytes. Per-partition private data stores raw BSD type plus libparted boot/RAID/LVM booleans.

Important details and risks: `d_npartitions` is written as `max_part + 1`, which reflects historical label semantics but deserves regression coverage. Flag state is libparted-private and does not appear to affect raw BSD partition type beyond `bsd_partition_set_system()`. Alignment reserves sector 0 metadata and allows partitions from sector 1 onward. Tests should cover checksum round trips, boot-code preservation, slot enumeration, Linux swap system mapping, and invalid/corrupt labels.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/bsd.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/dasd.c -->
# File Research: sources/block-storage/parted/libparted/labels/dasd.c

Purpose: IBM S/390 DASD disk-label backend using fdasd/VTOC helpers, with support for CDL labels and read-only handling of LDL/CMS-style layouts.

Main interfaces: Registers `PedDiskType` named `dasd`. Implements probe, alloc, duplicate, free, read, write, partition allocation/duplication/destruction, flag mapping, alignment, enumeration, system mapping, metadata allocation, and partition limit reporting.

Control flow: `dasd_probe()` initializes an fdasd anchor, reads DASD geometry, and rejects missing labels on CDL devices. `dasd_read()` distinguishes unlabeled/FBA implicit partitions, LDL/CMS labels, and CDL/VTOC partitions. CDL partitions are created from `partition_info_t` track ranges, with free-space pseudo-partitions where fdasd reports gaps. `dasd_write()` refuses LDL/CMS mutation, recreates the VTOC for CDL, adds partitions by track range, updates DS1DSNAM type strings, prepares/writes labels, and cleans fdasd state.

Data model: Disk private data stores format type, label block, and volume label. Partition private data stores a raw type and Linux system ID. Supported flags map to Linux LVM, RAID, and swap type IDs.

Important details and risks: DASD alignment is track-based using Linux real sector size and hardware sectors per track. LDL/CMS format reports only one real partition and disables flags. `dasd_write()` has a local `part_info` array that is populated only for encountered partitions before `dasd_update_type()` consumes corresponding entries; sparse partition numbering should be tested carefully. Metadata allocation marks leading VTOC/label space and, for LDL/CMS, possible trailing metadata after the implicit partition. Tests require S390/fdasd fixtures or mocks for CDL, LDL, CMS, FBA, sparse partitions, and flag-to-type updates.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/dasd.c -->