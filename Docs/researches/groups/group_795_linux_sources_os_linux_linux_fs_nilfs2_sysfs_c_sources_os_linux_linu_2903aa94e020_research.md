# Group Research: group_795_linux_sources_os_linux_linux_fs_nilfs2_sysfs_c_sources_os_linux_linu_2903aa94e020

Scope confirmed against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/sysfs.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/sysfs.c

Implements NILFS2 sysfs exposure under `/sys/fs/nilfs2`. It creates the global NILFS kset, the global `features` group, per-device kobjects, device subgroups, and per-mounted-snapshot kobjects.

Main responsibilities:
- Creates `/sys/fs/nilfs2/features` with driver revision and README.
- Creates per-device `/sys/fs/nilfs2/<device>` with attributes for revision, block size, device size, free blocks, UUID, volume name, and README.
- Creates per-device subgroups: `mounted_snapshots`, `checkpoints`, `segments`, `superblock`, and `segctor`.
- Creates snapshot kobjects for current checkpoint and mounted historical snapshots.
- Deletes kobjects with completion-backed release handlers.

Important exposed telemetry:
- Snapshot: `inodes_count`, `blocks_count`.
- Checkpoints: checkpoint count, snapshot count, latest segment checkpoint, next checkpoint.
- Segments: total segments, blocks per segment, clean and dirty segment counts.
- Segment constructor: latest partial segment block, sequence, checkpoint, current/next segment cursor, write times, dirty data blocks.
- Superblock: write time, write count, writable `sb_update_frequency`.
- Device: raw superblock revision, block size, device size, free blocks, UUID, volume name.

Concurrency and correctness:
- Uses `ns_sem` for superblock/shared state.
- Uses `ns_segctor_sem` for segment-constructor state.
- Uses `ns_last_segment_lock` for last-written-segment cursor fields.
- Reads metadata file stats through `nilfs_cpfile_get_stat()` and `nilfs_sufile_get_stat()` under appropriate locks.
- `sb_update_frequency` parsing uses `kstrtouint(skip_spaces(...))` and clamps values below `NILFS_SB_FREQ` to 10 seconds.

Dependencies:
- `nilfs.h`, `mdt.h`, `sufile.h`, `cpfile.h`, `sysfs.h`.
- Runtime state from `struct the_nilfs` and `struct nilfs_root`.
- Kernel sysfs/kobject APIs.

Risk notes:
- `nilfs_dev_volume_name_show()` uses `scnprintf(buf, sizeof(raw_sb->s_volume_name), "%s\n", ...)`, so the sysfs output bound is the raw field size, not PAGE_SIZE. This is intentional-looking but unusual.
- Most attributes are read-only. The only mutating sysfs path in this file is `superblock/sb_update_frequency`.
- Kobject deletion uses `kobject_put()` for subgroups but does not explicitly wait on the completion fields in this file; lifecycle safety depends on broader NILFS teardown ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/sysfs.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/sysfs.h

Declares NILFS2 sysfs helper types and macros used by `sysfs.c`.

Main contents:
- Defines root sysfs group name `NILFS_ROOT_GROUP_NAME` as `nilfs2`.
- Defines `struct nilfs_sysfs_dev_subgroups`, holding kobjects and unregister completions for per-device subgroups: `superblock`, `segctor`, `mounted_snapshots`, `checkpoints`, and `segments`.
- Defines attribute wrapper structs for:
  - global feature attributes,
  - per-device and per-device subgroup attributes,
  - per-snapshot attributes.
- Provides macros to declare info/read-only/read-write attributes and to list them in attribute arrays.

Design notes:
- The header abstracts repeated sysfs boilerplate into type-specific macros while keeping show/store callbacks strongly typed to either `struct the_nilfs` or `struct nilfs_root`.
- Attribute mode conventions are `0444` for read-only and `0644` for read-write.
- It forward-relies on `struct the_nilfs` and `struct nilfs_root` declarations from NILFS internals.

Dependencies:
- Kernel `linux/sysfs.h`.
- Used directly by NILFS sysfs implementation and indirectly tied to `the_nilfs.h` kobject fields.

Risk notes:
- `NILFS_SEGMENTS_RW_ATTR(name)` expands to `NILFS_RW_ATTR(segs_info, name)`, unlike the other segment macros. No current code in this group uses it, but it looks like a stale or typo-prone macro.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/the_nilfs.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/the_nilfs.c

Implements lifecycle, mount-time initialization, superblock selection, recovery loading, space accounting, discard, and checkpoint-root management for `struct the_nilfs`.

Main responsibilities:
- Allocates and initializes `struct the_nilfs` with locks, lists, rb-tree root, default superblock update frequency, and dirty-block counters.
- Reads primary and secondary NILFS superblocks, validates magic/CRC/size, chooses the newest valid one, and handles fallback/swap.
- Stores disk layout from the superblock after validating revision, inode size, first inode, segment geometry, reserved segment percentage, and device-size bounds.
- Loads the latest super root and opens DAT, CPFILE, and SUFILE metadata files.
- Runs log scanning and recovery through `nilfs_search_super_root()` and `nilfs_salvage_orphan_logs()`.
- Creates the NILFS sysfs device group after metadata files are loaded and removes it on load/recovery failure.
- Provides segment discard coalescing over contiguous segment ranges.
- Counts free blocks from clean segment count and detects near-full state against reserved segments plus in-flight dirty data.
- Manages mounted checkpoint roots in an rb-tree, including sysfs snapshot group creation and deletion.

Key functions:
- `alloc_nilfs()` / `destroy_nilfs()`.
- `init_nilfs()` for superblock and disk layout initialization.
- `load_nilfs()` for super-root loading and recovery.
- `nilfs_set_last_segment()` for last written segment cursor and superblock dirty tracking.
- `nilfs_discard_segments()`, `nilfs_count_free_blocks()`, `nilfs_near_disk_full()`.
- `nilfs_lookup_root()`, `nilfs_find_or_create_root()`, `nilfs_put_root()`.

Concurrency and lifecycle:
- `ns_sem` protects shared superblock-derived mutable state.
- `ns_segctor_sem` protects log writer / segment-constructor state.
- `ns_last_segment_lock` protects latest partial segment cursor.
- `ns_cptree_lock` protects mounted checkpoint root rb-tree and refcount removal.
- `nilfs_find_or_create_root()` creates the rb-tree node before calling `nilfs_sysfs_create_snapshot_group()`; if sysfs creation fails, it frees the new node but does not erase it from the rb-tree in this file, which is a notable error-path concern.

Recovery behavior:
- If the filesystem is not clean, read-only mounts may temporarily enable write access for recovery unless `norecovery` or unsupported read-only compatible features prevent it.
- If primary super-root search fails with `-EINVAL`, it may roll back to the spare superblock when valid and consistent.
- After successful recovery, sets `NILFS_VALID_FS` and updates the superblock.

Dependencies:
- NILFS segment, allocation, checkpoint, segment-usage, DAT, and segment-buffer internals.
- Block device APIs for block size, read-only checks, flush/discard, and size.
- Sysfs device group functions from `sysfs.c`.

Risk notes:
- Error handling in `nilfs_find_or_create_root()` after sysfs snapshot creation failure appears incomplete because the inserted rb-node is not removed before freeing.
- Discard coalescing resets `nblocks` to zero after issuing a discard for a non-contiguous extent, then relies on later iterations to seed the next range; this matches the written control flow but should be reviewed carefully if modified.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/the_nilfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/the_nilfs.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/the_nilfs.h

Defines the shared NILFS2 in-memory supervisor object and mounted checkpoint root object.

Main contents:
- `struct the_nilfs`: per-block-device NILFS state shared across mount points.
- `struct nilfs_root`: per-mounted-checkpoint/snapshot state.
- State flags: initialized, discontinued, GC running, superblock dirty, purging.
- Mount option helpers.
- Segment geometry helpers.
- Superblock update helpers.
- Function prototypes implemented by `the_nilfs.c`.

Important state categories in `struct the_nilfs`:
- Back pointers: superblock, block device.
- Superblock buffers and parsed superblock state.
- Segment constructor cursor and write timestamps.
- Latest segment cursor protected by `ns_last_segment_lock`.
- Metadata files: DAT, CPFILE, SUFILE.
- Mounted checkpoint rb-tree and lock.
- Dirty file list and GC inode list.
- Mount options and reserved block ownership.
- Disk layout: block size, segment count, blocks per segment, inode size, CRC seed.
- Sysfs per-device kobject and subgroup pointer.

Inline behavior:
- `nilfs_sb_need_update()` checks time-based superblock update frequency.
- `nilfs_sb_will_flip()` determines superblock write target flip pattern from write count.
- Segment range/start/number helpers translate segment numbers and block numbers.
- `nilfs_flush_device()` issues a block-device flush once when barriers are enabled, with a write memory barrier before the flush.

Dependencies:
- Kernel buffer-head, rb-tree, fs, block-device, slab, and refcount APIs.
- Forward declarations for segment constructor and sysfs subgroup state.

Risk notes:
- The sysfs fields embedded here make `the_nilfs` lifecycle tightly coupled to `sysfs.c`.
- Several inline helpers assume valid initialized geometry; callers must not use them before `init_nilfs()` has completed.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/the_nilfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/Kconfig -->
# File Research: sources/os/linux/linux/fs/nls/Kconfig

Defines kernel configuration for Native Language Support.

Main responsibilities:
- Provides `menuconfig NLS`, building `nls_base` as built-in or module.
- Defines `NLS_DEFAULT`, defaulting to `iso8859-1`, with a list of accepted charset names.
- Exposes DOS/Windows codepages, ISO-8859 variants, KOI8 variants, ASCII, UTF-8, UCS2 utilities, and Macintosh codepages.
- Describes intended filesystem consumers, especially FAT/Joliet/NT/BEOS/NCP/SMB and HFS-family filesystems.

Mac options covered by this group:
- `NLS_MAC_CELTIC`: `macceltic`.
- `NLS_MAC_CENTEURO`: `maccenteuro`.
- `NLS_MAC_CROATIAN`: `maccroatian`.
- `NLS_MAC_CYRILLIC`: `maccyrillic`.
- `NLS_MAC_GAELIC`: `macgaelic`.

Dependencies and build linkage:
- This file only declares configuration symbols.
- Actual object selection is in `fs/nls/Makefile`.

Risk notes:
- Many help texts still use older filesystem wording and recommend `Y` for several legacy codepages.
- `NLS_ISO8859_8` builds CP1255 in the Makefile, which is intentional in this tree but non-obvious from the symbol name.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/Makefile -->
# File Research: sources/os/linux/linux/fs/nls/Makefile

Maps NLS Kconfig symbols to build objects.

Main responsibilities:
- Builds `nls_base.o` when `CONFIG_NLS` is enabled.
- Maps DOS/Windows, ISO-8859, KOI8, UTF-8, UCS2, and Macintosh charset options to object files.
- Some config symbols build multiple objects, such as CP932 also building `nls_euc-jp.o`, and KOI8-U also building `nls_koi8-ru.o`.

Mac mappings relevant to this group:
- `CONFIG_NLS_MAC_CELTIC` -> `mac-celtic.o`
- `CONFIG_NLS_MAC_CENTEURO` -> `mac-centeuro.o`
- `CONFIG_NLS_MAC_CROATIAN` -> `mac-croatian.o`
- `CONFIG_NLS_MAC_CYRILLIC` -> `mac-cyrillic.o`
- `CONFIG_NLS_MAC_GAELIC` -> `mac-gaelic.o`

Risk notes:
- The Makefile is straightforward object selection; the main maintenance risk is keeping symbol names aligned with Kconfig and module charset names.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-celtic.c -->
# File Research: sources/os/linux/linux/fs/nls/mac-celtic.c

Implements the `macceltic` NLS codepage module.

Main structure:
- Generated Unicode mapping data from Unicode Organization tables.
- `charset2uni[256]` maps single-byte Mac Celtic characters to Unicode.
- Reverse Unicode-to-charset pages include page tables for `0x00`, `0x01`, `0x03`, `0x1e`, `0x20`, `0x21`, `0x22`, `0x25`, and `0x26`.
- `charset2lower[256]` and `charset2upper[256]` are present but filled with sentinel values rather than meaningful case-folding mappings.
- `uni2char()` maps a Unicode codepoint to one byte or returns `-ENAMETOOLONG` / `-EINVAL`.
- `char2uni()` maps one byte to Unicode or returns `-EINVAL` for `0x0000`.
- Registers `struct nls_table` with charset name `macceltic`.

Lifecycle:
- `init_nls_macceltic()` calls `register_nls(&table)`.
- `exit_nls_macceltic()` calls `unregister_nls(&table)`.
- Declares module description `NLS Codepage macceltic` and license `Dual BSD/GPL`.

Risk notes:
- NUL byte maps to Unicode zero, and `char2uni()` treats zero as invalid. This is consistent with many Linux NLS tables for filename handling but matters to callers expecting raw byte round trips.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-celtic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-centeuro.c -->
# File Research: sources/os/linux/linux/fs/nls/mac-centeuro.c

Implements the `maccenteuro` NLS codepage module for Central European Macintosh filenames.

Main structure:
- Generated Unicode mapping data.
- `charset2uni[256]` maps the single-byte Central European Mac codepage to Unicode, including many Latin Extended-A characters.
- Reverse Unicode-to-charset pages include `0x00`, `0x01`, `0x02`, `0x20`, `0x21`, `0x22`, and `0x25`.
- Case conversion arrays are present but contain sentinel values rather than active case mappings.
- `uni2char()` performs page-indexed exact reverse lookup.
- `char2uni()` performs byte-indexed forward lookup and rejects Unicode zero.
- Registers as charset `maccenteuro`.

Lifecycle:
- `init_nls_maccenteuro()` registers the table.
- `exit_nls_maccenteuro()` unregisters it.
- Module description is `NLS Codepage maccenteuro`; license is `Dual BSD/GPL`.

Risk notes:
- Only exact mappings are supported. Unicode characters that have visual or compatibility equivalents but no exact table entry return `-EINVAL`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-centeuro.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-croatian.c -->
# File Research: sources/os/linux/linux/fs/nls/mac-croatian.c

Implements the `maccroatian` NLS codepage module.

Main structure:
- Generated Mac Croatian translation tables.
- `charset2uni[256]` includes base Mac Roman-like entries plus Croatian-specific characters such as Latin Extended forms and an Apple private-use mapping.
- Reverse Unicode-to-charset pages include `0x00`, `0x01`, `0x02`, `0x03`, `0x20`, `0x21`, `0x22`, `0x25`, and `0xf8`.
- Includes `charset2lower[256]` and `charset2upper[256]` sentinel tables.
- `uni2char()` and `char2uni()` follow the common single-byte NLS implementation pattern.
- Registers as charset `maccroatian`.

Lifecycle:
- `init_nls_maccroatian()` registers the NLS table.
- `exit_nls_maccroatian()` unregisters it.
- Module description is `NLS Codepage maccroatian`; license is `Dual BSD/GPL`.

Risk notes:
- The reverse table includes private-use page `0xf8`, so compatibility with non-Apple Unicode expectations depends on preserving that exact mapping.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-croatian.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-cyrillic.c -->
# File Research: sources/os/linux/linux/fs/nls/mac-cyrillic.c

Implements the `maccyrillic` NLS codepage module.

Main structure:
- Generated Mac Cyrillic translation tables.
- `charset2uni[256]` maps bytes `0x80` onward heavily into Cyrillic Unicode ranges, with additional punctuation and symbols.
- Reverse Unicode-to-charset pages include `0x00`, `0x01`, `0x04`, `0x20`, `0x21`, and `0x22`.
- Case conversion arrays are present but sentinel-filled.
- `uni2char()` performs exact page-table reverse mapping.
- `char2uni()` maps single bytes to Unicode and rejects Unicode zero.
- Registers as charset `maccyrillic`.

Lifecycle:
- `init_nls_maccyrillic()` registers the table.
- `exit_nls_maccyrillic()` unregisters it.
- Module description is `NLS Codepage maccyrillic`; license is `Dual BSD/GPL`.

Risk notes:
- Exact mapping behavior means Cyrillic compatibility variants outside the table are not accepted.
- The table includes Euro and Cyrillic extension mappings, so changes should be validated against source Unicode mapping data rather than edited manually.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-cyrillic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-gaelic.c -->
# File Research: sources/os/linux/linux/fs/nls/mac-gaelic.c

Implements the `macgaelic` NLS codepage module.

Main structure:
- Generated Mac Gaelic translation tables.
- `charset2uni[256]` includes Mac Roman-like base mappings plus Gaelic/Irish orthography-related Latin Extended and combining-era characters.
- Reverse Unicode-to-charset pages include `0x00`, `0x01`, `0x02`, `0x1e`, `0x20`, `0x21`, `0x22`, and `0x26`.
- Case conversion arrays are present but sentinel-filled.
- `uni2char()` performs exact lookup through `page_uni2charset`.
- `char2uni()` maps one input byte and rejects zero Unicode.
- Registers as charset `macgaelic`.

Lifecycle:
- `init_nls_macgaelic()` registers the table.
- `exit_nls_macgaelic()` unregisters it.
- Module description is `NLS Codepage macgaelic`; license is `Dual BSD/GPL`.

Risk notes:
- Like the other generated Mac NLS modules, the implementation is data-driven and should be regenerated from canonical Unicode tables if mappings need to change.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-gaelic.c -->