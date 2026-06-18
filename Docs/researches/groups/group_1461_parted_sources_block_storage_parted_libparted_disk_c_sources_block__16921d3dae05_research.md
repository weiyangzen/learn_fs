# Group Research: group_1461_parted_sources_block_storage_parted_libparted_disk_c_sources_block__16921d3dae05

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/disk.c -->
# File Research: sources/block-storage/parted/libparted/disk.c

Core libparted disk-label and partition-list implementation. It owns the global `PedDiskType` registry, disk probing/opening/duplication/destruction, partition table commit paths, generic disk sanity checks, and the public partition mutation API.

The main design is a two-level abstraction: generic code manages `PedDisk`, `PedPartition`, ordering, constraints, free-space placeholders, metadata placeholders, and feature gating, while label-specific behavior is delegated through `PedDiskOps`. `ped_disk_probe()` iterates registered disk labels with exceptions fetched/cleared. `ped_disk_new()` probes, allocates a fresh disk object, calls the label reader, then pushes/pops update mode to rebuild metadata and free-space virtual partitions. `ped_disk_commit_to_dev()` optionally clobbers old signatures before invoking the label writer; `ped_disk_commit()` keeps the device open across device and OS commits to avoid unwanted udev events.

Update mode is the key invariant. `_disk_push_update_mode()` removes virtual free-space partitions and metadata; `_disk_pop_update_mode()` reallocates label metadata before leaving update mode and then regenerates free-space placeholders. Add/remove/resize operations use this state so raw partition list changes occur against active partitions only. `_disk_raw_add()` keeps primary and logical lists ordered by start sector, with logical partitions stored under the extended partition.

Partition mutation is constraint-driven. `ped_disk_add_partition()` checks basic type/count rules, intersects caller constraints with overlap-derived free-space constraints, enumerates, aligns via the disk label, validates label-specific rules, and inserts. `ped_disk_set_partition_geom()` preserves the old geometry on failure. Maximize/minimize helpers use neighboring partitions and extended-partition bounds to grow or shrink safely.

The file also exposes disk/partition flags, names, type IDs, type UUIDs, and UUIDs with feature checks before calling label-specific ops. Flag/name lookup supports translated and English strings. Risk areas are nested update-mode reentrancy, cleanup on partial add/delete failures, and label-specific callbacks that assume metadata/free-space placeholders are present or absent at the wrong time.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/exception.c -->
# File Research: sources/block-storage/parted/libparted/exception.c

Implements libparted’s process-global exception mechanism. It maintains a current exception object, a global pending flag `ped_exception`, a handler pointer, and a fetch-depth counter used by callers that want exceptions returned instead of immediately handled.

`ped_exception_throw()` formats a printf-style message into a dynamically grown buffer, stores type/options, and calls `do_throw()`. If `ped_exception_fetch_all()` is active, throws return `PED_EXCEPTION_UNHANDLED`; otherwise the configured handler is invoked and the exception is caught/freed afterward. `ped_exception_rethrow()` repeats handling of the current exception. `ped_exception_catch()` clears the pending flag and frees the current exception.

The default handler prints bug-specific guidance for `PED_EXCEPTION_BUG`, otherwise prints the type and message. It auto-returns only simple single-option cases (`OK`, `CANCEL`, `IGNORE`); other option sets are left unhandled so callers can choose safe defaults. Option-to-string lookup assumes option values are powers of two and uses a local `ped_log2()` helper.

The mechanism is simple and not thread-local. Concurrent use would race on global state; nested throws replace any existing exception by catching it first.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/exception.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/filesys.c -->
# File Research: sources/block-storage/parted/libparted/filesys.c

Implements the global `PedFileSystemType` and alias registries plus generic filesystem probing. Filesystem modules register `PedFileSystemType` objects containing probe callbacks; aliases map alternate or deprecated names onto those types.

`ped_file_system_type_get()` first checks canonical names case-insensitively, then aliases. Deprecated aliases emit a debug message. `ped_file_system_probe_specific()` opens the geometry’s device, calls a single filesystem probe op, closes the device, and returns the detected geometry.

`ped_file_system_probe()` is the ambiguous-detection resolver. It fetches all exceptions while probing every registered filesystem, records up to 32 successful detections and their geometric error from the requested geometry, then chooses the best match only if it is significantly better than all other matches. The significance threshold is `max(4096 sectors, 1% of input length)`. This avoids stale signatures winning when multiple filesystems are partly present.

Risk points are the fixed 32-entry detection arrays and process-global registry mutation. The probe scoring compares only start/end deltas, not semantic confidence.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/filesys.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/Makefile.am -->
# File Research: sources/block-storage/parted/libparted/fs/Makefile.am

Automake definition for libparted filesystem support. It builds an internal `libfs.la` with probe modules for Amiga filesystems, btrfs, ext2/3/4, FAT, f2fs, HFS/HFS+/HFSX, JFS, linux swap, NILFS2, NTFS, reiserfs, UDF, UFS, and XFS.

It also builds public `libparted-fs-resize.la`, versioned with libtool `0:5:0`, using `fsresize.sym` as the linker version script. The resize library source list is separate under `r/`, including FAT resize implementation and HFS/HFS+ resize/relocation/cache/journal support. `libfs.la` links UUID, intl, and OS libraries; the resize library links UUID.

The file encodes an architectural split: normal libparted filesystem support is mostly probe and registration code, while the `r/` subtree contains resizing-capable implementations exported through the fs-resize shared library.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/a-interface.c -->
# File Research: sources/block-storage/parted/libparted/fs/amiga/a-interface.c

Registration glue for Amiga filesystem probes. `ped_file_system_amiga_init()` registers all Amiga-related `PedFileSystemType` instances, and `ped_file_system_amiga_done()` unregisters them in the same family list.

Registered types include AFFS variants `affs0` through `affs7`, muFS variants `amufs`, `amufs0` through `amufs5`, `asfs`, and PFS/APFS-style `apfs1` and `apfs2`. The file has no probe logic; it imports the type globals from the individual implementation files.

The order matters because libparted’s filesystem registry is a stack-like linked list. Registration prepends each type, so effective probe order is reverse registration order unless later modules alter the registry.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/a-interface.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/affs.c -->
# File Research: sources/block-storage/parted/libparted/fs/amiga/affs.c

AFFS and muFS filesystem probe implementation. `_generic_affs_probe()` accepts a boot-block DOS type (`DOS\0` through `DOS\7`, `muFS`, and `muF\0` through `muF\5`) and returns a duplicate of the input geometry if the boot block and root block validate.

The probe is restricted to 512-byte device sectors. It optionally locates the matching Amiga RDB partition block via `amiga_find_part()` to derive reserved block count and block size. Without RDB data it defaults to reserved `2` and block size `1` sector. It reads the boot block at the partition start and checks the big-endian kind value. It then computes the AFFS root block near the middle of the filesystem, reads it, and validates root block type, tail marker, and checksum.

The file defines one `PedFileSystemOps` and `PedFileSystemType` per AFFS/muFS variant. It does not inspect directory trees or allocation maps; detection is signature/checksum based. Errors during reads/allocation throw libparted exceptions and return no match.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/affs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/affs.h -->
# File Research: sources/block-storage/parted/libparted/fs/amiga/affs.h

Header placeholder for AFFS support. It contains only the standard GNU Parted license/comment block and no declarations, macros, or include guard.

The implementation in `affs.c` does not rely on this header for exported symbols. It is included for source organization and build-list symmetry with other Amiga filesystem modules.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/affs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/amiga.c -->
# File Research: sources/block-storage/parted/libparted/fs/amiga/amiga.c

Shared Amiga RDB helper code used by the Amiga filesystem probes. It defines Rigid Disk Block constants, block identifiers, checksum helpers, and partition-list traversal for finding the RDB partition block matching a `PedGeometry`.

`_amiga_add_id()`, `_amiga_free_ids()`, and `_amiga_id_in_list()` maintain a small linked list of acceptable Amiga block IDs. `_amiga_read_block()` reads a 512-byte block, verifies an allowed ID when supplied, checks the Amiga checksum, and offers to fix bad checksums by recalculating and writing the block. `_amiga_find_rdb()` scans the first 16 blocks for an `RDSK` block.

`amiga_find_part()` reads the RDB, follows the partition block linked list up to 128 entries, detects loops, derives each partition’s start/end from cylinders, surfaces, and blocks-per-track, and returns the partition block whose geometry exactly matches the caller’s geometry. This lets filesystem probes determine Amiga block size and reserved blocks.

Important risks: most code uses big-endian conversions, but the `part->pb_ID != IDNAME_PARTITION` comparison is raw and may depend on host/layout assumptions. The checksum-fix path can write during probing if the exception handler selects fix.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/amiga.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/amiga.h -->
# File Research: sources/block-storage/parted/libparted/fs/amiga/amiga.h

Defines the Amiga `PartitionBlock` layout and shared helper declarations. `PartitionBlock` mirrors Amiga RDB partition metadata: block ID, checksum fields, linked-list pointer, flags, BSTR drive name, environment vector fields, geometry fields, DOS type, boot priority, and reserved words.

Macros include `PART(pos)` for casting, bootable/nomount flag bit definitions, and declarations for `amiga_find_part()` plus the `AmigaIds` linked-list helpers used to filter expected RDB block kinds. Fields are stored in Amiga big-endian order and are converted by callers with `PED_BE*_TO_CPU`.

This header is consumed by AFFS, ASFS, APFS/PFS, and the RDB helper implementation. It does not include an include guard, so it relies on conventional single inclusion in these small C files.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/amiga.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/apfs.c -->
# File Research: sources/block-storage/parted/libparted/fs/amiga/apfs.c

Probe implementation for Amiga `apfs1` and `apfs2` types, corresponding to PFS-style signatures `0x50463101` and `0x50463102`. `_generic_apfs_probe()` reads the boot block, checks the signature, then reads a root block at `geom->start + reserved * blocksize` and validates that it has the same kind value.

Like the AFFS probe, it only works on 512-byte sector devices and optionally uses `amiga_find_part()` to derive reserved blocks and filesystem block size from the matching RDB partition block. It returns a duplicate of the input geometry on success and `NULL` on mismatch or read/allocation failure.

The probe is intentionally shallow: root validation is just a kind comparison. It does not checksum APFS/PFS metadata or calculate a more precise filesystem length.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/apfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/apfs.h -->
# File Research: sources/block-storage/parted/libparted/fs/amiga/apfs.h

Header placeholder for Amiga APFS/PFS probe support. It contains only the license/comment block and no declarations, constants, or include guard.

`apfs.c` includes it for consistency with the filesystem module layout, but all required symbols are local to `apfs.c` or provided by `amiga.h` and libparted headers.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/apfs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/asfs.c -->
# File Research: sources/block-storage/parted/libparted/fs/amiga/asfs.c

ASFS filesystem probe implementation. `_asfs_probe()` requires 512-byte sectors, optionally reads the Amiga RDB partition block to get filesystem block size, then validates ASFS root blocks.

The ASFS root signature is `0x53465300`. `_asfs_probe_root()` checks the signature, verifies a big-endian checksum with initial sum `1`, checks that the root block number encoded in the block maps to the root sector being tested, and verifies 64-bit start/end byte ranges match the input geometry. The probe checks the first root at partition start and a second root near the end, accepting the filesystem if either validates.

The implementation returns a duplicate of the input geometry on detection. It does not attempt repair or detailed metadata parsing, but its start/end checks make it stricter than the APFS/PFS probe.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/asfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/asfs.h -->
# File Research: sources/block-storage/parted/libparted/fs/amiga/asfs.h

Header placeholder for ASFS support. It contains only the standard license/comment block and no definitions.

The ASFS implementation keeps all probe logic and constants in `asfs.c`; this header exists for source tree consistency.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/amiga/asfs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/btrfs/btrfs.c -->
# File Research: sources/block-storage/parted/libparted/fs/btrfs/btrfs.c

Minimal btrfs probe module. It reads the first btrfs superblock located 64 KiB inside the partition and checks the little-endian magic value `_BHRfS_M`.

The local buffer union models only enough of `struct btrfs_super_block` to reach the magic: checksum, FSID, bytenr, flags, and magic. If the partition is too short to contain the 64 KiB offset plus one sector, or the read fails, probing returns `NULL`. On a magic match it returns a `PedGeometry` spanning the entire input geometry.

The module registers one `PedFileSystemType` named `btrfs`. It does not validate checksum, generation, device size, or backup superblocks, so it is a signature detector rather than a consistency checker.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/btrfs/btrfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/ext2/ext2.h -->
# File Research: sources/block-storage/parted/libparted/fs/ext2/ext2.h

Private ext2 support header. It includes libparted headers, `sys/types.h`, integer types, and either the system ext2 header if configured or the local `ext2_fs.h`.

It defines `blk_t` and `struct ext2_fs`, a richer state object inherited from older resize code. The structure carries a device handle, superblock, group descriptor table, buffer cache, metadata dirty state, feature booleans, block/group sizing, relocation pool, debug/safe/verbose options, and journal pointer.

In the current listed implementation, ext2 probing uses only the local superblock definitions through this header. The larger `struct ext2_fs` is mostly relevant to historical or external resize components not present in this file group.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/ext2/ext2.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/ext2/ext2_fs.h -->
# File Research: sources/block-storage/parted/libparted/fs/ext2/ext2_fs.h

Local ext2/ext3/ext4 on-disk structure header. It defines magic values, block constants, special inode numbers, directory file type values, error policy constants, and feature flags used to distinguish ext3 and ext4.

Structures include `ext2_dir_entry_2`, `ext2_group_desc`, `ext2_inode`, and the packed `ext2_super_block`. The superblock layout covers classic ext2 fields plus dynamic revision fields, feature masks, UUID, volume name, last mounted path, compression bitmap, and journal metadata. Accessor macros convert little-endian fields for directory entries, group descriptors, inodes, and superblock fields.

The probe code relies especially on `EXT2_SUPER_MAGIC`, block count, log block size, blocks per group, group number, first data block, revision level, and feature masks. This header is disk-layout sensitive; packed structure and endian macros are essential to portability.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/ext2/ext2_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/ext2/interface.c -->
# File Research: sources/block-storage/parted/libparted/fs/ext2/interface.c

Filesystem registration and probing for ext2, ext3, and ext4. `_ext2_generic_probe()` reads enough sectors from the start of the geometry to access the superblock at byte offset 1024, verifies the ext magic, computes block size and total length, then classifies the filesystem by feature flags.

Ext4 is detected from modern incompatible/readonly-compatible features such as extents, 64-bit, flex_bg, huge file, GDT checksum, or dir_nlink. Ext3 is detected by the journal compatible feature when ext4 features are absent. The caller’s expected version determines whether the match is accepted.

The probe handles backup/group superblocks: if a dynamic revision superblock reports a nonzero block group number, it computes the original filesystem start, initializes a temporary geometry, and recursively probes from that base. Otherwise it returns a geometry sized by block count and block size. The file registers three types: `ext2`, `ext3`, and `ext4`.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/ext2/interface.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/f2fs/f2fs.c -->
# File Research: sources/block-storage/parted/libparted/fs/f2fs/f2fs.c

Minimal f2fs probe module. `f2fs_probe()` allocates one device sector on the stack, reads sector offset `F2FS_SB_OFFSET` from the geometry, and checks the little-endian `F2FS_MAGIC`.

On success it returns a new geometry covering the entire input geometry. The module registers one filesystem type named `f2fs` and unregisters it in the matching done function.

The probe does not validate checksum, block size fields, segment layout, or backup superblock. It is a simple signature detector using the packed superblock prefix defined in `f2fs.h`.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/f2fs/f2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/f2fs/f2fs.h -->
# File Research: sources/block-storage/parted/libparted/fs/f2fs/f2fs.h

Defines the f2fs superblock prefix needed for probing. Constants include `F2FS_MAGIC`, maximum volume-name length, and superblock sector offset `0x02`.

`struct f2fs_super_block` is packed and includes the magic, version, sector/block geometry logs, segment/section/zone counts, checkpoint/SIT/NAT/SSA/main block addresses, root/node/meta inode numbers, UUID, and UTF-16 volume name. The probe currently only reads `magic`, but the structure documents the adjacent on-disk fields and keeps alignment stable for future checks.

The header has a conventional include guard and no function declarations.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/f2fs/f2fs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/fat/bootsector.c -->
# File Research: sources/block-storage/parted/libparted/fs/fat/bootsector.c

FAT boot-sector reader and analyzer for libparted’s non-resize FAT probe path. `fat_boot_sector_read()` reads sector zero of a geometry into a `FatBootSector`, then performs minimum sanity checks needed to avoid invalid arithmetic: boot signature `0xAA55`, nonzero sector size aligned to 512, nonzero cluster size, nonzero reserved sectors, and FAT count between 1 and 4.

`fat_boot_sector_probe_type()` deliberately ignores the textual FAT label. It treats zero root-directory entries as FAT32; otherwise it computes first data cluster location and cluster count to distinguish FAT12 from FAT16. `fat_boot_sector_analyse()` fills `FatSpecific` fields: logical sector size, CHS values, total sectors, FAT count and offsets, cluster sizing, FAT type, FAT size, serial, root directory placement, FAT32 info/backup sector offsets, and cluster count. FAT12 is explicitly rejected as unsupported.

This copy is read/probe oriented. Unlike the resize-library copy under `fs/r/`, it does not fix CHS fields or generate/write boot/info sectors.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/fat/bootsector.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/fat/bootsector.h -->
# File Research: sources/block-storage/parted/libparted/fs/fat/bootsector.h

Defines packed FAT boot-sector and FAT32 info-sector layouts for the non-resize FAT support. It includes boot message/jump/code constants, FAT32 FSInfo magic values, and declarations for read, type-probe, and analysis functions.

`FatBootSector` models the BIOS parameter block and FAT16/FAT32 union fields, ending with `boot_sign` at byte `0x1fe`. `FatInfoSector` models FAT32 free-cluster and next-cluster metadata. This version also defines `FAT_BOOT_CODE_LENGTH 128`, used as a compile-time size constant by related code.

The header is layout-critical: `fat.c` checks `sizeof(FatBootSector) == 512` before registering FAT probes.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/fat/bootsector.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/fat/count.h -->
# File Research: sources/block-storage/parted/libparted/fs/fat/count.h

FAT cluster-usage interface header. It defines `FatClusterFlag` values for free, file, directory, and bad clusters, plus a packed `FatClusterInfo` bitfield storing 6 bits of usage units and a 2-bit flag.

It declares functions to collect cluster info for a filesystem, query cluster flags and usage, map fragment flags, and test whether a fragment is active. These functions are implemented outside the listed files but are referenced by FAT resize/analysis code through `fat.h`.

The bitfield makes per-cluster metadata compact, with one usage unit representing `cluster_size / 64`.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/fat/count.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/fat/fat.c -->
# File Research: sources/block-storage/parted/libparted/fs/fat/fat.c

FAT filesystem allocation, probing, registration, and cleanup. `fat_alloc()` allocates a `PedFileSystem`, its `FatSpecific` payload, initializes boot/info sector pointers, duplicates the geometry, and marks the filesystem unchecked. `fat_free()` frees boot sector, geometry, type-specific storage, and the filesystem object.

`fat_probe()` allocates a temporary filesystem, reads and analyzes the boot sector, returns the detected FAT type through an output parameter, and creates a geometry sized to the FAT sector count from the boot sector. `fat_probe_fat16()` and `fat_probe_fat32()` wrap it and accept only matching analyzed types, freeing mismatched probe geometries.

`ped_file_system_fat_init()` registers `fat16` and `fat32` only if the packed boot sector is exactly 512 bytes; otherwise it throws a bug exception and disables FAT support. This protects against compiler packing/layout problems.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/fat/fat.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/fat/fat.h -->
# File Research: sources/block-storage/parted/libparted/fs/fat/fat.h

Main FAT support header for libparted’s probe-oriented FAT code. It defines `FatCluster`, `FatFragment`, `FatType`, FAT table state, packed directory-entry layout, and the `FatSpecific` per-filesystem state structure.

`FatSpecific` stores boot/info sectors, logical and physical sizing, CHS fields, total sectors, cluster counts and offsets, FAT type/count/size, serial number, root directory details, FAT32 info/backup sector offsets, FAT table and cluster-info pointers, buffer sizing, and fragment mapping. Macros define directory attributes, cluster-count thresholds for FAT12/FAT16/FAT32, and root directory defaults.

The header also declares public helper functions for allocation, free, buffer allocation, and resize. Some declarations are implemented outside this file group, so this header is shared with broader FAT support.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/fat/fat.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/hfs/hfs.c -->
# File Research: sources/block-storage/parted/libparted/fs/hfs/hfs.c

HFS filesystem type registration module. It defines global block-cache pointers/counters used by HFS/HFS+ internals and registers three filesystem types: `hfs`, `hfs+`, and `hfsx`.

Each type’s `PedFileSystemOps` contains only a probe callback, implemented in `probe.c`: `hfs_probe`, `hfsplus_probe`, or `hfsx_probe`. Init and done functions register/unregister the three types.

The module itself contains no validation logic. It acts as the registry bridge between libparted’s filesystem framework and the HFS probe implementation.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/hfs/hfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/hfs/hfs.h -->
# File Research: sources/block-storage/parted/libparted/fs/hfs/hfs.h

Comprehensive HFS/HFS+/HFSX on-disk and private-state header. It defines allocation-bitmap macros, buffer limits, Apple creator codes, HFS/HFS+/HFSX signatures and versions, volume attribute bits, B-tree node kinds, catalog record kinds, well-known file IDs, journal constants, and HFSX compare modes.

The HFS section defines packed structures for extents, master directory block, B-tree node/header records, catalog and extent keys, directory/file records, and thread records. The HFS+ section defines permissions, extent descriptors, fork data, Unicode names, volume header, B-tree records, catalog records, extents keys, attributes, and journal info/header/block list structures.

The private section defines in-memory file handles, extent lists, filesystem data for HFS and HFS+, generic B-tree keys, and B-tree leaf record references. External globals `hfs_block`, `hfsp_block`, and counters support shared block buffers. This header is used beyond probing by resize/relocation code, so it is much broader than `probe.c` requires.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/hfs/hfs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/hfs/probe.c -->
# File Research: sources/block-storage/parted/libparted/fs/hfs/probe.c

HFS/HFS+/HFSX probe implementation. `hfsc_can_use_geom()` rejects devices whose sector size is not 512 bytes, because the code assumes classic HFS sector layout.

`hfs_and_wrapper_probe()` detects an HFS master directory block at byte offset 1024 and scans expected alternate MDB positions near the computed end of the volume. It returns a geometry sized to the detected HFS wrapper/base volume. `hfsplus_probe()` first checks for HFS+ embedded in an HFS wrapper by looking at the embedded signature in the wrapper MDB; if absent, it detects standalone HFS+ by reading the volume header at sector 2 and scanning alternate volume headers near the legal/legacy end ranges. `hfs_probe()` accepts plain HFS only when `hfs_and_wrapper_probe()` succeeds and `hfsplus_probe()` does not identify an embedded HFS+ volume. `hfsx_probe()` similarly validates HFSX signature and legal alternate volume header positions.

The probes return geometries sized by discovered alternate header positions, not merely input geometry. They validate signatures but do not parse B-trees or journal state.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/hfs/probe.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/hfs/probe.h -->
# File Research: sources/block-storage/parted/libparted/fs/hfs/probe.h

Declaration header for HFS probe helpers. It includes libparted, endian/debug, and `hfs.h`, then declares sector-size validation and probe entry points: `hfsc_can_use_geom()`, `hfs_and_wrapper_probe()`, `hfsplus_probe()`, `hfs_probe()`, and `hfsx_probe()`.

The functions are consumed by `hfs.c` for filesystem type registration and may be reused by HFS resize code that needs wrapper detection.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/hfs/probe.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/jfs/jfs.c -->
# File Research: sources/block-storage/parted/libparted/fs/jfs/jfs.c

Minimal JFS probe module. It reads the JFS aggregate superblock at byte offset 32768, verifies magic `"JFS1"`, and returns a geometry sized from the superblock’s physical block size and aggregate size.

The probe first checks that the candidate geometry is large enough to reach the superblock offset. It reads one device sector at `JFS_SUPER_OFFSET / sector_size` into the JFS superblock structure. On a match, it converts `s_pbsize` and `s_size` from little endian and computes length as `block_size * block_count / device_sector_size`.

The file registers a single filesystem type named `jfs`. It does not validate the superblock version, state, log fields, or secondary metadata.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/jfs/jfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/jfs/jfs_superblock.h -->
# File Research: sources/block-storage/parted/libparted/fs/jfs/jfs_superblock.h

JFS aggregate superblock layout header imported from IBM JFS utilities. It defines `JFS_MAGIC`, `JFS_VERSION`, volume-name size, and `struct superblock` when `_JFS_UTILITY` is defined.

The structure includes magic/version, aggregate size and block-size fields, physical block-size fields, allocation group size, flags/state/compression, primary/secondary inode table/map extents, log/fsck extents, update time, fsck log metadata, volume name, extendfs parameters, VFS/reserved fields, and free-space accounting.

The probe uses only `s_magic`, `s_pbsize`, and `s_size`, but the full layout preserves offsets for those fields and supports possible utility reuse.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/jfs/jfs_superblock.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/jfs/jfs_types.h -->
# File Research: sources/block-storage/parted/libparted/fs/jfs/jfs_types.h

JFS utility type and list-macro header. In `_JFS_UTILITY` mode it defines fixed-width signed/unsigned aliases, Unicode character type, OS/2 holdover aliases, a JFS timespec-like structure, boolean constants, min/max/roundup helpers, and JFS extent descriptor types.

It defines logical, physical, and data extent descriptors (`lxd_t`, `pxd_t`, `dxd_t`) with construction/extraction macros, including 24-bit length fields and little-endian address conversions. It also defines component-name and DASD quota structures.

The second half provides generic circular doubly-linked list and singly headed doubly-linked list macros: header/entry declarations, init, insert, remove, move-to-head/tail, and self-orphan helpers. For this file group, these definitions mainly support `jfs_superblock.h`; they are not actively used by `jfs.c` beyond providing type names.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/jfs/jfs_types.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/linux_swap/linux_swap.c -->
# File Research: sources/block-storage/parted/libparted/fs/linux_swap/linux_swap.c

Linux swap and swsusp probe module. It treats swap as a `PedFileSystem` for libparted registration purposes and supports old swap signature `SWAP-SPACE`, new signature `SWAPSPACE2`, and suspend signature `S1SUSPEND`.

`swap_alloc()` creates a temporary filesystem object with `SwapSpecific` state, page-sized header buffer, large working buffer, duplicate geometry, and default v1 type. `swap_init()` derives page-sector size from `getpagesize()` and device sector size, computes page count, and reads the first page. `_swap_v0_open()`, `_swap_v1_open()`, and `_swap_swsusp_open()` validate signatures at the end of the first memory page. v0 page count is bounded by the old bitmap capacity; v1 uses `last_page`; swsusp is identified separately.

`_generic_swap_probe()` opens the requested kind and returns a geometry sized by swap page count for v1 or by input length for v0. Init registers three types and aliases: deprecated `linux-swap(old)`, deprecated `linux-swap(new)`, and canonical `linux-swap` pointing to v1. Risks include dependence on host page size matching swap metadata expectations.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/linux_swap/linux_swap.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/nilfs2/nilfs2.c -->
# File Research: sources/block-storage/parted/libparted/fs/nilfs2/nilfs2.c

NILFS2 filesystem probe module with CRC validation. It defines the packed NILFS2 superblock layout, primary superblock offset, and macro for computing the secondary superblock offset from device size in 512-byte units.

`is_valid_nilfs_sb()` checks little-endian magic `0x3434`, validates the superblock byte count, and recomputes the EFI CRC32 over the superblock with the checksum field treated as zero. `nilfs2_probe()` converts the candidate geometry length to 512-byte units, computes the secondary superblock offset, reads the primary superblock from byte offset 1024, validates it, reads the secondary superblock near the end, validates it, then returns a geometry ending after the reserved 4 KiB secondary-superblock area.

The module registers one filesystem type named `nilfs2`. It is stricter than many other probes because both primary and secondary superblocks must pass checksum validation.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/nilfs2/nilfs2.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/ntfs/ntfs.c -->
# File Research: sources/block-storage/parted/libparted/fs/ntfs/ntfs.c

Minimal NTFS probe module. `ntfs_probe()` reads the first sector of the candidate geometry, checks for the `"NTFS"` signature at byte offset 3, then copies the 64-bit total-sector count from offset `0x28` and returns a geometry of that length from the input start.

The code does not endian-convert the copied length explicitly, relying on little-endian host behavior or compatible representation. It also does not validate bytes-per-sector, sectors-per-cluster, MFT fields, or boot-sector checksum. The module registers a single filesystem type named `ntfs`.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/ntfs/ntfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/bootsector.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/fat/bootsector.c

FAT boot-sector implementation for the resize library under `fs/r/`. It shares read/type/analyze logic with the probe-only FAT copy, but adds write/generation support when `DISCOVER_ONLY` is not defined.

`fat_boot_sector_read()` validates signature and core BPB fields. `fat_boot_sector_probe_type()` classifies FAT32 by zero root-entry count and FAT12/FAT16 by computed cluster count. `fat_boot_sector_analyse()` fills `FatSpecific` and rejects FAT12. Unlike the non-resize copy, invalid CHS geometry offers `FIX`, `IGNORE`, or `CANCEL`; choosing fix updates sector/heads fields in the boot sector and writes it back through `fat_boot_sector_write()`.

Resize-specific helpers generate boot code, synthesize FAT16/FAT32 boot sectors from `FatSpecific`, write the primary boot sector and FAT32 backup boot sector, read/generate/write the FAT32 info sector, and populate free-cluster/last-allocation values from FAT table statistics. This file is therefore both a parser and mutator for FAT resize operations.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/bootsector.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/bootsector.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/fat/bootsector.h

Resize-library FAT boot-sector header. It defines the same packed `FatBootSector` and `FatInfoSector` layouts as the probe copy, plus boot message/jump/code constants and FAT32 info-sector magic values.

In addition to read/type/analyze declarations, this resize version declares mutating helpers: `fat_boot_sector_set_boot_code()`, `fat_boot_sector_generate()`, `fat_boot_sector_write()`, `fat_info_sector_read()`, `fat_info_sector_generate()`, and `fat_info_sector_write()`. These are used by FAT resizing code to rewrite BPB fields, backup boot sectors, and FSInfo metadata.

Compared with `fs/fat/bootsector.h`, this header omits `FAT_BOOT_CODE_LENGTH` but exposes the generation/write API needed by `libparted-fs-resize`.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/bootsector.h -->