# Group Research: group_1037_linux_stable_sources_os_linux_linux_stable_fs_nilfs2_sysfs_c_source_3d7e067bbf3c

Scope checked against `Docs/research_subset_a.md`: all listed files are under `sources/os/linux/linux-stable`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/sysfs.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/sysfs.c

## Purpose
Implements NILFS2 sysfs support under `/sys/fs/nilfs2`. It exposes global driver features, per-device filesystem metadata, mounted snapshot counters, checkpoint statistics, segment statistics, segment-constructor state, and superblock update state.

## Main Interfaces
- `nilfs_sysfs_init()` creates the NILFS2 root kset under `fs_kobj` and adds the global `features` group.
- `nilfs_sysfs_exit()` removes the feature group and unregisters the kset.
- `nilfs_sysfs_create_device_group(struct super_block *sb)` allocates per-device subgroup storage, creates `/sys/fs/nilfs2/<device>`, then creates child groups.
- `nilfs_sysfs_delete_device_group(struct the_nilfs *nilfs)` tears down child kobjects, drops the device kobject, and frees subgroup storage.
- `nilfs_sysfs_create_snapshot_group(struct nilfs_root *root)` creates either `current_checkpoint` or `mounted_snapshots/<cno>`.
- `nilfs_sysfs_delete_snapshot_group(struct nilfs_root *root)` drops the snapshot kobject.

## Sysfs Layout
- `/sys/fs/nilfs2/features`: `revision`, `README`.
- `/sys/fs/nilfs2/<device>`: `revision`, `blocksize`, `device_size`, `free_blocks`, `uuid`, `volume_name`, `README`.
- `/sys/fs/nilfs2/<device>/mounted_snapshots`: `README`.
- `/sys/fs/nilfs2/<device>/mounted_snapshots/<cno>` and `/sys/fs/nilfs2/<device>/current_checkpoint`: `inodes_count`, `blocks_count`, `README`.
- `/sys/fs/nilfs2/<device>/checkpoints`: `checkpoints_number`, `snapshots_number`, `last_seg_checkpoint`, `next_checkpoint`, `README`.
- `/sys/fs/nilfs2/<device>/segments`: `segments_number`, `blocks_per_segment`, `clean_segments`, `dirty_segments`, `README`.
- `/sys/fs/nilfs2/<device>/segctor`: last/current segment cursor attributes, write times, next checkpoint, dirty data block count, `README`.
- `/sys/fs/nilfs2/<device>/superblock`: `sb_write_time`, `sb_write_time_secs`, `sb_write_count`, `sb_update_frequency`, `README`.

## Implementation Notes
The file uses macros to generate repeated sysfs `show`, `store`, `kobj_type`, release, create, and delete code for device child groups. Typed attribute wrappers from `sysfs.h` route callbacks either to `struct the_nilfs *` for device-level groups or `struct nilfs_root *` for snapshot groups.

Most attributes are read-only. The writable attribute is `superblock/sb_update_frequency`; it parses an unsigned integer with `kstrtouint(skip_spaces(buf), 0, &val)`, clamps values below `NILFS_SB_FREQ` to the 10-second minimum, and updates `nilfs->ns_sb_update_freq` under `ns_sem`.

## Locking and State Access
- `ns_segctor_sem` protects live segment-constructor fields and metadata file stats.
- `ns_last_segment_lock` protects last stable segment cursor fields.
- `ns_sem` protects superblock-backed fields such as revision, device size, UUID, volume name, superblock write time/count, and update frequency.
- Snapshot inode/block counters are read from `atomic64_t` fields in `struct nilfs_root`.
- Dirty data blocks are read from `ns_ndirtyblks`.

## Dependencies
Includes `nilfs.h`, `mdt.h`, `sufile.h`, `cpfile.h`, and `sysfs.h`. Uses NILFS metadata helpers including `nilfs_cpfile_get_stat()`, `nilfs_sufile_get_stat()`, `nilfs_sufile_get_ncleansegs()`, and `nilfs_count_free_blocks()`.

## Error Handling
Device group creation unwinds in reverse order on partial failure. Failed kobject initialization calls `kobject_put()`. Feature-group creation failure unregisters the global kset. Attribute callbacks return metadata/stat errors directly and log NILFS errors for stat retrieval and parsing failures.

## Research Notes
This is an observability and limited-control surface, not core allocation logic. Its key correctness constraint is lifetime alignment between sysfs kobjects and `the_nilfs` / `nilfs_root` objects, plus matching the locks used by writers of each exposed field.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/sysfs.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/sysfs.h

## Purpose
Declares NILFS2 sysfs support types and attribute-generation macros used by `sysfs.c`.

## Main Contents
- `NILFS_ROOT_GROUP_NAME` is `"nilfs2"`.
- `struct nilfs_sysfs_dev_subgroups` embeds kobjects and completion objects for per-device child groups:
  - `superblock`
  - `segctor`
  - `mounted_snapshots`
  - `checkpoints`
  - `segments`
- Attribute wrapper struct macros:
  - `NILFS_KOBJ_ATTR_STRUCT(name)` for plain kobject attributes.
  - `NILFS_DEV_ATTR_STRUCT(name)` for callbacks receiving `struct the_nilfs *`.
  - `NILFS_CP_ATTR_STRUCT(name)` for callbacks receiving `struct nilfs_root *`.

## Macro API
The header provides `NILFS_INFO_ATTR`, `NILFS_RO_ATTR`, and `NILFS_RW_ATTR`, then group-specific aliases for feature, device, segments, mounted snapshots, checkpoints, snapshot, superblock, and segctor attributes. It also provides `_ATTR_LIST` helpers for building `struct attribute *` arrays.

## Dependencies
Includes `<linux/sysfs.h>`. Callback signatures refer to NILFS types supplied by the including implementation context.

## Research Notes
The header centralizes repetitive sysfs boilerplate. Its main design choice is keeping separate typed callback wrappers per sysfs group so `sysfs.c` can recover the correct owning NILFS object with `container_of()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/the_nilfs.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/the_nilfs.c

## Purpose
Implements allocation, initialization, loading, recovery, superblock validation, disk layout setup, segment discard/free-space accounting, and checkpoint-root lookup/lifetime for the shared `struct the_nilfs` object.

## Main Lifecycle
- `alloc_nilfs(struct super_block *sb)` allocates and initializes `struct the_nilfs`, locks, rb-tree roots, lists, counters, mount state defaults, and device pointers.
- `destroy_nilfs(struct the_nilfs *nilfs)` releases loaded superblock buffers if initialized and frees the object.
- `init_nilfs(struct the_nilfs *nilfs, struct super_block *sb)` reads superblocks, validates compatibility, determines filesystem block size, stores disk layout, initializes the log cursor, and marks the object initialized.
- `load_nilfs(struct the_nilfs *nilfs, struct super_block *sb)` searches for a super root, loads metadata files, creates sysfs device state, and performs roll-forward recovery when needed.

## Superblock Handling
- `nilfs_valid_sb()` validates magic, superblock byte size, and CRC.
- `nilfs_load_super_block()` reads primary and secondary superblocks, chooses the newer valid one, rejects invalid secondary-superblock offsets, and records protected sequence state from the older valid superblock.
- `nilfs_fall_back_super_block()` promotes the secondary superblock to primary.
- `nilfs_swap_super_block()` swaps primary and secondary buffer/data pointers.
- `nilfs_release_super_block()` drops both superblock buffers.

## Disk Layout and Limits
- `nilfs_get_blocksize()` derives block size from `s_log_block_size` and rejects oversized blocks.
- `nilfs_store_disk_layout()` validates revision, superblock size, inode size, first user inode, blocks per segment, reserved-segment percentage, segment count, and device-size coverage.
- `nilfs_max_size()` combines page-cache and bmap key limits for `sb->s_maxbytes`.
- `nilfs_nrsvsegs()` computes reserved segments with a `NILFS_MIN_NRSVSEGS` lower bound.
- `nilfs_set_nsegments()` stores total and reserved segment counts.

## Load and Recovery Flow
`load_nilfs()` checks whether the filesystem is clean, searches the latest super root, optionally rolls back to the spare superblock after scan failure, loads DAT/checkpoint/segment-usage metadata files, creates sysfs device state, and then either skips or performs recovery. Recovery may temporarily clear `SB_RDONLY` if the mount is read-only but the block device is writable and recovery is allowed. On success it marks the filesystem clean and updates the superblock. On failure after sysfs creation it deletes the sysfs group and drops metadata inodes.

## Segment and Space Operations
- `nilfs_set_last_segment()` updates latest partial segment state and marks the superblock dirty when the sequence advances.
- `nilfs_discard_segments()` batches contiguous segment ranges and calls `blkdev_issue_discard()`.
- `nilfs_count_free_blocks()` multiplies clean segment count by blocks per segment.
- `nilfs_near_disk_full()` compares clean segments with reserved segments plus in-progress dirty block demand.

## Checkpoint Root Tree
- `nilfs_lookup_root()` searches the checkpoint rb-tree by checkpoint number and increments the root refcount.
- `nilfs_find_or_create_root()` allocates a new `nilfs_root`, initializes counters, inserts it in the rb-tree, and creates its sysfs snapshot group.
- `nilfs_put_root()` decrements the refcount, removes the rb-tree node on final put, deletes sysfs snapshot state, drops `ifile`, and frees the root.

## Locking
- `ns_last_segment_lock` protects latest stable segment cursor fields.
- `ns_sem` protects shared superblock and mount state fields.
- `ns_segctor_sem` protects log writer state outside initialization.
- `ns_cptree_lock` protects checkpoint root tree lookup, insertion, and final removal.

## Research Notes
This file is the central shared-device state manager for NILFS2. It coordinates on-disk superblock selection, metadata inode loading, recovery policy, sysfs attachment, and mounted checkpoint root lifetime.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/the_nilfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/the_nilfs.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/the_nilfs.h

## Purpose
Defines `struct the_nilfs`, `struct nilfs_root`, state flags, inline helpers, and function prototypes for NILFS2 shared filesystem/device state.

## Main Types
`struct the_nilfs` supervises a NILFS block device and multiple mount/checkpoint roots. It contains:
- State flags and flushed-device flag.
- Superblock and block-device back-pointers.
- Locks/semaphores: `ns_sem`, `ns_snapshot_mount_mutex`, `ns_last_segment_lock`, `ns_segctor_sem`, `ns_cptree_lock`, and `ns_inode_lock`.
- Primary/secondary superblock buffers and raw pointers.
- Superblock write time, write count, size, mount state, and update frequency.
- Live segment constructor cursor fields: sequence, segment numbers, partial-segment offset, next checkpoint, and write times.
- Latest stable segment fields protected by `ns_last_segment_lock`.
- Metadata file inodes: DAT, checkpoint file, and segment usage file.
- Checkpoint rb-tree, dirty file list, GC inode list, mount options, reserved IDs, checkpoint interval, dirty-buffer watermark, and static disk layout fields.
- Sysfs device kobject and per-device subgroup pointer.

`struct nilfs_root` represents a mounted checkpoint/current root and contains checkpoint number, rb-tree node, refcount, owning `the_nilfs`, `ifile`, inode/block counters, and a sysfs snapshot kobject.

## Flags and Helpers
The `THE_NILFS_FNS()` macro generates setters, clearers, and testers for initialization, discontinued-chain, GC-running, superblock-dirty, and purging flags. Mount option helpers manipulate `ns_mount_opt`.

## Important Inline Helpers
- `nilfs_sb_need_update()` checks whether periodic superblock update time has elapsed.
- `nilfs_sb_will_flip()` predicts active superblock flipping from write count.
- `nilfs_valid_fs()` reads the clean-state bit under `ns_sem`.
- Segment helpers calculate segment ranges, segment starts, segment numbers, segment termination, next-segment shifts, active segment checks, and latest checkpoint number.
- `nilfs_flush_device()` issues a block-device flush once when barriers are enabled.

## Exported Prototypes
Declares allocation/destruction, init/load, reserved segment calculation, discard/free-space helpers, checkpoint root lookup/create/put, disk-full check, and superblock fallback/swap routines.

## Research Notes
This header defines the shared state contract that NILFS2 mount, recovery, segment construction, checkpoint, and sysfs code all depend on. The comments are especially useful for mapping each sysfs attribute in `sysfs.c` back to the protected field in `struct the_nilfs`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/the_nilfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/nls/Kconfig

## Purpose
Defines Kconfig options for Linux Native Language Support modules used by filesystems that need filename character-set translation.

## Main Structure
- `menuconfig NLS` enables the base NLS subsystem as built-in or module `nls_base`.
- `NLS_DEFAULT` selects the default mount-time NLS name, defaulting to `iso8859-1`.
- Individual `tristate` options select DOS, Windows, ISO-8859, KOI8, Mac, UTF-8, and helper charset modules.
- `NLS_UCS2_UTILS` is a hidden tristate helper option.

## Covered Charset Families
- DOS/OEM codepages: CP437, CP737, CP775, CP850, CP852, CP855, CP857, CP860, CP861, CP862, CP863, CP864, CP865, CP866, CP869, CP874, CP932, CP936, CP949, CP950.
- Windows codepages: CP1250, CP1251, CP1255 via `NLS_ISO8859_8`.
- ISO-8859 sets: 1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14, 15.
- KOI8: KOI8-R and KOI8-U/RU.
- Mac codepages: Roman, Celtic, Central European, Croatian, Cyrillic, Gaelic, Greek, Icelandic, Inuit, Romanian, Turkish.
- UTF-8.

## Filesystem Context
Help text repeatedly explains that these translations affect filenames for filesystems such as FAT, Joliet, NT/NTFS-like, BeOS, NCP, SMB, and HFS/HFS-style Mac partitions, not file contents.

## Research Notes
This file is configuration metadata only. Its direct implementation counterpart is `fs/nls/Makefile`, which maps these symbols to individual NLS object files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/nls/Makefile

## Purpose
Builds Native Language Support modules selected by `fs/nls/Kconfig`.

## Main Mappings
- `CONFIG_NLS` builds `nls_base.o`.
- DOS/OEM codepages build `nls_cp*.o`; CP932 also builds `nls_euc-jp.o`.
- ISO-8859 options build `nls_iso8859-*.o`, except `NLS_ISO8859_8` builds `nls_cp1255.o`.
- KOI8-U builds both `nls_koi8-u.o` and `nls_koi8-ru.o`.
- Mac options build `mac-celtic.o`, `mac-centeuro.o`, `mac-croatian.o`, `mac-cyrillic.o`, `mac-gaelic.o`, `mac-greek.o`, `mac-iceland.o`, `mac-inuit.o`, `mac-romanian.o`, `mac-roman.o`, and `mac-turkish.o`.
- `CONFIG_NLS_UCS2_UTILS` builds `nls_ucs2_utils.o`.

## Research Notes
This is a direct Kbuild dispatch table. The files in this group are the Mac charset modules selected by the matching `CONFIG_NLS_MAC_*` symbols.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-celtic.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/mac-celtic.c

## Purpose
Provides the `macceltic` NLS codepage module. It translates between Mac Celtic single-byte charset values and Unicode for filesystem filename handling.

## Main Data
- `charset2uni[256]` maps byte values to Unicode code points. ASCII/control bytes map directly except byte `0x00`, which maps to `0x0000` and is treated as invalid by `char2uni()`.
- Sparse reverse maps convert Unicode high-byte pages back to charset bytes:
  - `page00`
  - `page01`
  - `page03`
  - `page1e`
  - `page20`
  - `page21`
  - `page22`
  - `page25`
  - `page26`
- `page_uni2charset[256]` indexes those sparse reverse pages.
- `charset2lower[256]` and `charset2upper[256]` are sentinel-filled case tables provided to the NLS table.

## Conversion Logic
- `uni2char()` rejects zero output space with `-ENAMETOOLONG`, looks up the Unicode page and low byte, writes one output byte on exact mapping, and returns `-EINVAL` when no mapping exists.
- `char2uni()` indexes `charset2uni` by the input byte and returns `-EINVAL` if the resulting Unicode value is `0x0000`.

## Module Registration
Registers a `struct nls_table` with `.charset = "macceltic"` via `register_nls()` in module init and unregisters it in module exit. Module metadata uses `MODULE_DESCRIPTION("NLS Codepage macceltic")` and `MODULE_LICENSE("Dual BSD/GPL")`.

## Research Notes
The file is generated from Unicode charset data and contains only exact reverse mappings. It has no filesystem policy of its own; users are HFS/HFS-like or other filesystem paths that request the `macceltic` NLS table.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-celtic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-centeuro.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/mac-centeuro.c

## Purpose
Provides the `maccenteuro` NLS codepage module for Mac Central European filename character conversion.

## Main Data
- `charset2uni[256]` maps the Mac Central European byte set to Unicode, including Latin Extended-A characters used by Central/Eastern European languages.
- Reverse Unicode-page tables are:
  - `page00`
  - `page01`
  - `page02`
  - `page20`
  - `page21`
  - `page22`
  - `page25`
- `page_uni2charset[256]` indexes these pages.
- `charset2lower[256]` and `charset2upper[256]` are present as NLS case tables and are sentinel-filled in this generated file.

## Conversion Logic
`uni2char()` and `char2uni()` use the standard generated Mac NLS pattern: exact reverse lookup for Unicode-to-byte conversion, one-byte output, `-ENAMETOOLONG` for no output space, and `-EINVAL` for unmapped values.

## Module Registration
Registers `.charset = "maccenteuro"` with `register_nls()` and unregisters it on module exit. Module metadata declares the description `NLS Codepage maccenteuro` and dual BSD/GPL licensing.

## Research Notes
Compared with the Celtic/Gaelic variants, this file’s distinguishing content is its dense `page01` reverse map for Latin Extended-A characters such as A/E/I/L/N/O/R/S/T/U/Z variants used in Central European alphabets.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-centeuro.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-croatian.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/mac-croatian.c

## Purpose
Provides the `maccroatian` NLS codepage module for Mac Croatian filename character conversion.

## Main Data
- `charset2uni[256]` maps Mac Croatian bytes to Unicode. It includes common Mac Roman-style symbols plus Croatian/Central European letters such as C acute/caron, D stroke, S/Z caron, and related lowercase forms.
- Reverse Unicode-page tables are:
  - `page00`
  - `page01`
  - `page02`
  - `page03`
  - `page20`
  - `page21`
  - `page22`
  - `page25`
  - `pagef8`
- `pagef8` handles the private-use mapping for `0xf8ff`.
- `page_uni2charset[256]` indexes the sparse reverse maps.
- `charset2lower[256]` and `charset2upper[256]` are sentinel-filled NLS case tables.

## Conversion Logic
Uses the same generated one-byte NLS conversion functions as the other Mac modules. Unicode-to-byte conversion is exact only; unmapped Unicode code points return `-EINVAL`.

## Module Registration
Registers `.charset = "maccroatian"` with the NLS core at module init and unregisters it at exit. Module metadata declares `NLS Codepage maccroatian` and `Dual BSD/GPL`.

## Research Notes
This variant is close to Mac Roman but replaces and extends selected byte positions for Croatian letters and includes the Apple private-use glyph mapping through Unicode page `0xf8`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-croatian.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-cyrillic.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/mac-cyrillic.c

## Purpose
Provides the `maccyrillic` NLS codepage module for Mac Cyrillic filename character conversion.

## Main Data
- `charset2uni[256]` maps bytes to Unicode. Byte range `0x80-0x9f` maps to uppercase Cyrillic letters, and much of `0xe0-0xfe` maps to lowercase Cyrillic letters. Byte `0xff` maps to Euro.
- Reverse Unicode-page tables are:
  - `page00`
  - `page01`
  - `page04`
  - `page20`
  - `page21`
  - `page22`
- `page04` is the main Cyrillic reverse map.
- `page_uni2charset[256]` indexes those sparse pages.
- `charset2lower[256]` and `charset2upper[256]` are sentinel-filled NLS case tables.

## Conversion Logic
`uni2char()` performs exact sparse-page lookup and writes one output byte. `char2uni()` performs byte-to-Unicode table lookup. Invalid or unmapped characters return `-EINVAL`; insufficient output buffer returns `-ENAMETOOLONG`.

## Module Registration
Registers `.charset = "maccyrillic"` via `register_nls()` and unregisters it on exit. Module metadata declares `NLS Codepage maccyrillic` and `Dual BSD/GPL`.

## Research Notes
This file is shorter than several Latin Mac variants because its reverse mapping concentrates heavily in Unicode page `0x04` for Cyrillic, plus a few shared punctuation/symbol pages.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-cyrillic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-gaelic.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/mac-gaelic.c

## Purpose
Provides the `macgaelic` NLS codepage module for Mac Gaelic filename character conversion.

## Main Data
- `charset2uni[256]` maps Mac Gaelic bytes to Unicode. It includes standard Mac Roman-like symbols plus Gaelic-specific dotted consonants and related Latin Extended Additional characters.
- Reverse Unicode-page tables are:
  - `page00`
  - `page01`
  - `page02`
  - `page1e`
  - `page20`
  - `page21`
  - `page22`
  - `page26`
- `page1e` is important for Latin Extended Additional dotted letters used by Gaelic mappings.
- `page_uni2charset[256]` indexes the sparse reverse maps.
- `charset2lower[256]` and `charset2upper[256]` are sentinel-filled NLS case tables.

## Conversion Logic
Uses the same generated exact-map conversion pattern as the other Mac NLS files: one-byte output, sparse Unicode-page reverse lookup, `-EINVAL` for missing mappings, and `-ENAMETOOLONG` when the caller supplies no output space.

## Module Registration
Registers `.charset = "macgaelic"` with the NLS core on init and unregisters on exit. Module metadata declares `NLS Codepage macgaelic` and `Dual BSD/GPL`.

## Research Notes
The distinguishing feature is the mapping coverage in Unicode page `0x1e` for Gaelic dotted consonant forms, plus a small page `0x26` symbol mapping. Like the other generated Mac modules, it contains no mutable state beyond NLS table registration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-gaelic.c -->