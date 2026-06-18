# Group Research: group_1465_parted_sources_block_storage_parted_libparted_labels_pc98_c_sources_c10739663271

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/block-storage/parted`, which is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/pc98.c -->
# File Research: sources/block-storage/parted/libparted/labels/pc98.c

## Purpose

`pc98.c` implements libparted’s PC-98 partition table backend. It registers the `pc98` disk type, probes PC-98 labels, reads/writes the fixed 16-entry partition table, maps raw PC-98 type/flag fields into libparted partitions, and enforces PC-98 cylinder-aligned geometry.

## Main Responsibilities

- Defines on-disk PC-98 raw table structures:
  - 510 bytes boot code,
  - 16-bit magic `0xAA55`,
  - 16 packed `PC98RawPartition` entries.
- Probes only 512-byte-sector devices and reads two sectors for the table.
- Accepts labels with the PC-98 magic and known IPL signatures: `IPL1`, `Linux 98`, or `GRUB/98 `.
- Converts PC-98 CHS tuples to/from libparted sectors using device hardware geometry.
- Reads non-empty raw entries into `PedPartition` objects, preserving partition number, type, boot flag, hidden flag, name, IPL sector, and probed filesystem type.
- Writes existing boot code when recognizable; otherwise installs a dummy IPL boot-code stub.
- Supports partition names up to 16 bytes and exposes `PED_DISK_TYPE_PARTITION_NAME`.
- Supports `PED_PARTITION_BOOT` and `PED_PARTITION_HIDDEN`.
- Reserves the first cylinder as metadata.
- Limits primary and supported partition count to 16.

## Key Structures

- `PC98RawPartition`: packed raw partition entry with type bytes, IPL CHS, start CHS, end CHS, and 16-byte name.
- `PC98RawTable`: two-sector PC-98 table image.
- `PC98PartitionData`: libparted per-partition private data containing IPL sector, system type, boot/hidden flags, and cached name.

## Important Functions

- `pc98_probe()` validates sector size, reads the raw table, checks magic, then checks IPL signature.
- `read_table()` imports raw entries into libparted partitions.
- `fill_raw_part()` converts a `PedPartition` back into a raw PC-98 entry.
- `pc98_write()` reads the existing two-sector header, preserves or initializes boot code, rewrites the partition array, and syncs the device.
- `pc98_partition_set_system()` maps filesystem types to PC-98 system IDs.
- `pc98_partition_set_flag()` and `pc98_partition_get_flag()` implement boot/hidden flags.
- `pc98_partition_align()` enforces cylinder-aligned starts and ends.
- `pc98_alloc_metadata()` adds a metadata partition covering cylinder 0.
- `PT_define_limit_functions(pc98)` wires common max-start/max-length checks.

## Behavior Details

PC-98 labels use CHS addressing. `legacy_end()` treats raw end head/sector zero as shorthand for the last sector of the raw end cylinder. Reads reject partitions whose actual libparted geometry changes during insertion, because non-cylinder-aligned PC-98 partitions are unsupported.

`pc98_partition_set_system()` defaults to Linux/ext-style `0x2062`, changes IDs for FAT16/FAT32/NTFS/UFS, and marks unknown/ext-like filesystems bootable with `0xa062`. The boot and hidden booleans are then encoded back into high bits of the type bytes.

Names are space-padded on write. Empty names fall back to the filesystem type name if available.

## Dependencies and Interactions

- Uses `pt-tools.h` for sector read helpers.
- Uses `pt-common.h` for disk operation initializer macros and partition limit callbacks.
- Uses core libparted allocation, disk, geometry, constraint, exception, and filesystem probing APIs.

## Notable Edge Cases

- The backend is skipped from generic label tests by `tests/common.c`, indicating known incomplete or problematic coverage.
- Writes fail if a partition end is not at the last sector of a cylinder.
- `pc98_partition_set_name()` trims trailing spaces by indexing from `strlen(name) - 1`; empty names are a fragile case in that loop.
- `pc98_duplicate()` creates a fresh empty label rather than copying existing partition private data at the disk level; partitions themselves have a duplicate routine.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/pc98.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/pt-common.h -->
# File Research: sources/block-storage/parted/libparted/labels/pt-common.h

## Purpose

`pt-common.h` factors repeated disk-label backend boilerplate into macros used by multiple libparted partition table implementations.

## Main Responsibilities

- Defines `NULL_IF_DISCOVER_ONLY()` so write callbacks disappear in discover-only builds.
- Defines `PT_define_limit_functions(PT_type)` to generate:
  - `PT_type_partition_check()`,
  - `PT_type_partition_max_start_sector()`,
  - `PT_type_partition_max_length()`.
- Defines `PT_op_function_initializers(PT_type)` to populate the common `PedDiskOps` function pointers for a backend.

## Dependencies and Interactions

The generated limit functions call `ptt_partition_max_start_len()`, `ptt_partition_max_start_sector()`, and `ptt_partition_max_length()` from `pt-tools.c`. Backends include this header near the end of their file after defining the required `PT_type_*` functions.

## Notable Details

The macros encode libparted’s expected naming convention for disk-label backends. A backend using `PT_op_function_initializers(foo)` must provide functions such as `foo_probe`, `foo_read`, `foo_partition_new`, `foo_partition_align`, and related partition methods.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/pt-common.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/pt-tools.c -->
# File Research: sources/block-storage/parted/libparted/labels/pt-tools.c

## Purpose

`pt-tools.c` provides small shared helpers for partition table backends: sector read/write/zeroing helpers and partition-table representation limit checks.

## Main Responsibilities

- Writes sector 0 from a partial buffer, zero-filling the rest of the sector.
- Reads one or more sectors into newly allocated memory.
- Clears sector ranges using a static 16 KiB zero buffer.
- Clears sectors relative to a `PedGeometry`.
- Includes generated/static `pt-limit.c` lookup data via `__pt_limit_lookup`.
- Checks whether a partition exceeds a label type’s maximum representable start sector or length.
- Returns max start sector and max length for known partition table types.

## Important Functions

- `ptt_write_sector()` allocates a sector-sized buffer, copies caller data, zero-fills, and writes sector 0.
- `ptt_read_sectors()` allocates `n_sectors * sector_size`, reads into it, and returns it through `buf`.
- `ptt_clear_sectors()` writes zero chunks across a sector range.
- `ptt_partition_max_start_len()` throws libparted exceptions when a partition exceeds table-imposed limits.
- `ptt_partition_max_start_sector()` and `ptt_partition_max_length()` expose representation limits.

## Dependencies and Interactions

- Used by disk-label backends through `pt-tools.h`.
- Used indirectly through `pt-common.h` generated callbacks.
- Relies on `pt-limit.c` for label-type limit data.

## Notable Edge Cases

`ptt_read_sectors()` asserts successful allocation rather than gracefully returning failure when `ped_malloc()` returns `NULL`. `ptt_clear_sectors()` assumes the device sector size is no larger than the static 16 KiB zero buffer.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/pt-tools.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/pt-tools.h -->
# File Research: sources/block-storage/parted/libparted/labels/pt-tools.h

## Purpose

`pt-tools.h` declares shared helper APIs for libparted partition table backends.

## Contents

- Sector IO helpers:
  - `ptt_write_sector()`
  - `ptt_read_sector()`
  - `ptt_read_sectors()`
  - `ptt_clear_sectors()`
  - `ptt_geom_clear_sectors()`
- Representation-limit helpers:
  - `ptt_partition_max_start_len()`
  - `ptt_partition_max_start_sector()`
  - `ptt_partition_max_length()`

## Dependencies and Role

The header includes `<parted/disk.h>` and is consumed by label implementations such as PC-98, Amiga RDB, and Sun labels. It provides a thin internal contract around common raw-sector and partition-limit operations.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/pt-tools.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/rdb.c -->
# File Research: sources/block-storage/parted/libparted/labels/rdb.c

## Purpose

`rdb.c` implements libparted’s Amiga Rigid Disk Block backend, registered as disk type `amiga`. It reads and writes Amiga hardblock structures, partition linked lists, checksums, filesystem type codes, partition names, and Amiga-specific flags.

## Main Responsibilities

- Defines and handles Amiga block IDs:
  - `RDSK`, `BADB`, `PART`, `FSHD`, `LSEG`, `BOOT`, and free markers.
- Reads blocks with ID validation and checksum validation.
- Offers exception-driven repair for bad block checksums.
- Locates the RDB within the first 16 sectors.
- Allocates a default RDB with geometry, logical hardblock range, and disk identification strings.
- Reads linked `PART` blocks into libparted partitions.
- Writes partition blocks into available hardblock space while preserving other linked hardblock lists.
- Supports Amiga BSTR-style partition names.
- Supports boot, hidden/no-mount, RAID, and LVM flags.
- Maps filesystem types to Amiga DOS type words.
- Reserves the hardblock region as metadata.

## Key Structures

- `AmigaBlock`: common ID, summed-long count, and checksum prefix.
- `RigidDiskBlock`: RDB root with geometry, linked-list heads, hardblock range, and disk/controller strings.
- `PartitionBlock`: raw Amiga partition descriptor with flags, drive name, environment vector, DOS type, and cylinder range.
- `LinkedBlock` and `Linked2Block`: generic linked hardblock records.

## Important Functions

- `_amiga_checksum()` and `_amiga_calculate_checksum()` validate and update Amiga block checksums.
- `_amiga_read_block()` reads a sector, validates optional IDs, and handles checksum exceptions.
- `_amiga_find_rdb()` scans sectors 0-15 for an `RDSK`.
- `amiga_alloc()` creates a fresh RDB in memory.
- `amiga_read()` imports RDB geometry and linked partition blocks.
- `_amiga_find_free_blocks()` walks existing hardblock lists to classify used blocks and detect loops.
- `amiga_write()` builds a new linked partition list in free hardblock slots and writes the updated RDB.
- `amiga_partition_new()` initializes default `PART` block fields.
- `amiga_partition_set_system()` maps ext2/ext3/swap/FAT/HFS/JFS/NTFS/ReiserFS/UFS/XFS to Amiga DOS type values.
- `amiga_partition_set_flag()` manipulates `PBFF_BOOTABLE`, `PBFF_NOMOUNT`, `PBFF_RAID`, and `PBFF_LVM`.
- `amiga_partition_align()` enforces cylinder alignment outside the hardblock area.

## Behavior Details

Amiga partitions are stored as cylinder ranges. `amiga_read()` computes `start = low_cyl * cylblocks` and `end = (high_cyl + 1) * cylblocks - 1`, then inserts the partition with an exact constraint.

`amiga_write()` first reconstructs a table of hardblock usage by walking bad-block, partition, filesystem-header, load-segment, and boot-block lists. It then allocates new `PART` blocks from free slots, writes each partition block with an updated checksum, and finally writes the updated RDB.

The backend tracks up to 128 partitions but reserves blocks 0 through `MAX_RDB_BLOCK` for metadata. New partitions default to drive name `dhx` and DOS type `LNX\0`.

## Dependencies and Interactions

- Uses `misc.h` for filesystem helpers such as Linux swap detection.
- Uses `pt-tools.h` and `pt-common.h`.
- Uses libparted disk, partition, geometry, constraint, exception, and filesystem probing APIs.

## Notable Edge Cases

- Generic libparted tests skip `amiga` labels due to “minor problems”.
- `_amiga_get_bstr()` modifies the source BSTR buffer by placing a terminating NUL.
- Several severe consistency errors call `exit(EXIT_FAILURE)` or rely on TODO repair paths.
- `amiga_write()` warns in comments that a failure while writing a partition block can lose the partition table because it overwrites the old table in place.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/rdb.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/sun.c -->
# File Research: sources/block-storage/parted/libparted/labels/sun.c

## Purpose

`sun.c` implements libparted’s classic Sun disk label backend, registered as disk type `sun`. It handles the sector-0 Sun label, VTOC-style partition info, checksum validation, geometry reconciliation, whole-disk partition behavior, and Sun partition flags.

## Main Responsibilities

- Defines the packed 512-byte `SunRawLabel`.
- Probes by checking magic `0xDABE` and, outside discover-only builds, checksum validity.
- Initializes fresh labels from BIOS geometry.
- Creates the conventional whole-disk partition in slot 2 with ID `0x05`.
- Reads non-whole-disk populated slots into `PedPartition` objects.
- Writes partition info and geometry back into sector 0.
- Supports Sun partition type flags:
  - boot,
  - root,
  - LVM,
  - RAID.
- Enforces cylinder-based alignment.
- Reserves alternate-cylinder space at the end of the disk as metadata when present.

## Key Structures

- `SunRawPartition`: start cylinder and sector count.
- `SunPartitionInfo`: partition ID and flags byte.
- `SunRawLabel`: complete 512-byte Sun disk label.
- `SunPartitionData`: libparted per-partition type and high-level flag booleans.
- `SunDiskData`: stores usable length and cached raw label.

## Important Functions

- `sun_compute_checksum()` and `sun_verify_checksum()` implement the label XOR checksum.
- `sun_probe()` validates magic and checksum.
- `sun_alloc()` initializes a fresh label and whole-disk slot.
- `_check_geometry_sanity()` reconciles on-disk geometry with OS geometry and warns on mismatches.
- `sun_read()` imports populated non-whole-disk partitions.
- `_use_old_info()` preserves old label informational fields when rewriting.
- `sun_write()` regenerates partition arrays, preserves or creates whole-disk slot 2, updates cylinder counts, recomputes checksum, and syncs.
- `sun_partition_set_system()` maps flags/filesystems to Sun IDs.
- `sun_partition_enumerate()` skips the whole-disk slot until no other slots remain.
- `sun_partition_align()` tries strict cylinder-end alignment, then a lax end alignment for weird existing tables.

## Behavior Details

The whole-disk partition is treated specially. Reads skip ID `0x05`; writes recreate it in slot 2 if the user has not explicitly allocated that slot. If all other slots are full, the user can accept a warning and overwrite the whole-disk slot.

`sun_partition_set_system()` gives priority to mutually exclusive boot/root/LVM/RAID booleans. Without those flags, it defaults to Linux `0x83`, maps Linux swap to `0x82`, and maps UFS to `0x06`.

## Dependencies and Interactions

- Uses `misc.h` for Linux swap detection.
- Uses `pt-tools.h` for sector reads.
- Uses `verify.h` for size checks.
- Uses `pt-common.h` to wire the standard disk operations and partition limit functions.

## Notable Edge Cases

- Warns if disk cylinders exceed the 16-bit Sun label maximum.
- Can accept mismatched disk/label CHS geometry after a warning and then mutates the device BIOS geometry.
- Label is in the first 512 bytes, so `sun_alloc_metadata()` does not reserve sector 0; it only reserves unusable alternate-cylinder tail space.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/sun.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/vtoc.c -->
# File Research: sources/block-storage/parted/libparted/labels/vtoc.c

## Purpose

`vtoc.c` implements lower-level IBM/S390 DASD VTOC helper routines used by libparted’s DASD support. It handles EBCDIC/ASCII conversion, volume labels, CCHH/CCHHB address encoding, DSCB format label initialization, label IO, and VTOC free-space extent updates.

## Main Responsibilities

- Provides ASCII-to-EBCDIC and EBCDIC-to-ASCII translation tables.
- Encodes and decodes DASD CCHH and CCHHB cylinder/head/block addresses, including large-volume cylinder bits.
- Converts CCHH/CCHHB addresses to block or track numbers.
- Reads and writes DASD volume labels.
- Handles a CMS/FBA special case where the label is at offset 512 within block zero.
- Gets and sets VOLSER and volume label identifiers.
- Reads and writes VTOC DSCB labels:
  - FMT1,
  - FMT4,
  - FMT5,
  - FMT7,
  - FMT9.
- Initializes FMT1, FMT4, FMT5, FMT7, FMT8, and FMT9 records.
- Updates FMT4 highest-used DSCB and unused-record counters.
- Maintains FMT5 free-space extents for smaller disks.
- Maintains FMT7 free-space extents for large disks.
- Chooses FMT5 or FMT7 free-space representation in `vtoc_set_freespace()`.

## Important Functions

- `vtoc_ebcdic_enc()` and `vtoc_ebcdic_dec()` translate fixed-size byte strings.
- `vtoc_set_cchh()`, `vtoc_get_cyl_from_cchh()`, and `vtoc_get_head_from_cchh()` manage CCHH addresses.
- `vtoc_set_cchhb()`, `vtoc_get_cyl_from_cchhb()`, and `vtoc_get_head_from_cchhb()` manage CCHHB addresses.
- `cchhb2blk()`, `cchh2blk()`, and `cchh2trk()` convert DASD addresses through geometry.
- `vtoc_volume_label_init()` fills a volume label with EBCDIC spaces.
- `vtoc_read_volume_label()` validates `VOL1`, `LNX1`, or `CMS1` labels.
- `vtoc_volume_label_set_volser()` uppercases, truncates, pads, and EBCDIC-encodes a VOLSER.
- `vtoc_read_label()` and `vtoc_write_label()` perform positional DSCB IO.
- `vtoc_init_format4_label()` initializes the VTOC anchor/format-4 DSCB with device geometry and FMT8/FMT9 support.
- `vtoc_init_format_1_8_label()` initializes common FMT1/FMT8 partition dataset fields.
- `vtoc_update_format5_label_add()` and `vtoc_update_format5_label_del()` merge/split FMT5 free extents.
- `vtoc_update_format7_label_add()` and `vtoc_update_format7_label_del()` merge/split FMT7 free extents.
- `vtoc_set_freespace()` dispatches free-space updates to FMT5 or FMT7 based on `BIG_DISK_SIZE`.

## Behavior Details

FMT5 extents represent free space using track/cylinder counts and track remainders. FMT7 extents represent large-disk free space using relative track addresses. Both add paths merge adjacent extents and both delete paths handle exact, left-bounded, right-bounded, and split removal cases.

When a disk is large enough to require FMT7, `vtoc_set_freespace()` marks FMT4 extended free-space state with `DS4VTOCI = 0xa0`, `DS4EFLVL = 0x07`, and sets `DS4EFPTR` to the FMT7 location.

## Dependencies and Interactions

- Includes `<parted/vtoc.h>`, `<parted/parted.h>`, and DASD geometry types such as `struct fdasd_hd_geometry`.
- Used by DASD/fdasd label code and by S390 volser/VTOC tests in this group.

## Notable Edge Cases

- Many internal consistency failures print `BUG:` and call `exit(EXIT_FAILURE)` rather than returning an error.
- `vtoc_error()` builds an 8192-byte stack buffer with `sprintf`.
- Several routines operate on fixed-width fields and intentionally do not NUL-terminate the on-disk data.
- `vtoc_read_volume_label()` returns success after copying the CMS/FBA fallback label without revalidating it.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/vtoc.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/libparted.c -->
# File Research: sources/block-storage/parted/libparted/libparted.c

## Purpose

`libparted.c` is the library initialization and teardown unit for libparted. It registers disk-label and filesystem handlers at load time, frees global device state at unload time, exposes the version string, and provides libparted allocation wrappers.

## Main Responsibilities

- Registers disk types in constructor `_init()`.
- Registers filesystem types in constructor `_init()`.
- Sets gettext domain when NLS is enabled.
- Calls `ped_set_architecture()`.
- Deregisters disk and filesystem types in destructor `_done()`.
- Frees all cached devices in `_done()`.
- Exposes `ped_get_version()`.
- Implements `ped_malloc()` and `ped_calloc()`.

## Disk Type Registration

`init_disk_types()` registers disk labels in an order chosen because probing happens in reverse registration order. `loop` is initialized first so it probes last. S390 DASD is registered only on S390 builds. PC-98 registration is controlled by `ENABLE_PC98`.

Registered labels include loop, DASD, Atari, Sun, PC-98, msdos, mac, GPT, DVH, BSD, Amiga, and AIX.

## Filesystem Registration

`init_file_system_types()` registers Amiga, XFS, UFS, ReiserFS, NTFS, Linux swap, JFS, HFS, FAT, F2FS, ext2, NILFS2, Btrfs, and UDF.

The destructor calls the corresponding `*_done()` functions, mostly in reverse-ish order.

## Notable Details

`ped_malloc()` throws a fatal libparted exception on allocation failure and returns `NULL`. `ped_calloc()` calls `ped_malloc()` then zeroes the returned buffer without checking for `NULL`, relying on fatal exception behavior.

A disabled DEBUG section contains old allocation debugging scaffolding that the comments explicitly describe as harmful and not useful.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/libparted.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/Makefile.am -->
# File Research: sources/block-storage/parted/libparted/tests/Makefile.am

## Purpose

`Makefile.am` defines the libparted unit test binaries and shell test wrappers.

## Main Responsibilities

- Declares shell tests:
  - `t1000-label.sh`
  - `t1001-flags.sh`
  - `t2000-disk.sh`
  - `t2100-zerolen.sh`
  - `t3000-symlink.sh`
  - `t4000-volser.sh`
- Builds Check-based test programs:
  - `label`
  - `disk`
  - `zerolen`
  - `symlink`
  - `volser`
  - `flags`
- Links tests against `libparted.la`, Check libraries, and pthreads.
- Adds include paths for source/build libparted headers.
- Creates a local `init.sh` symlink before test logs are produced.
- Exports `top_srcdir`, `abs_top_srcdir`, and `ENABLE_DEVICE_MAPPER` to test scripts.

## Dependencies and Interactions

This file connects the C tests in this directory to the broader GNU test harness under `tests/init.sh` and `tests/t-lib-helpers.sh`.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/common.c -->
# File Research: sources/block-storage/parted/libparted/tests/common.c

## Purpose

`common.c` provides shared helpers for libparted’s Check-based unit tests.

## Main Responsibilities

- Reads `PARTED_SECTOR_SIZE` and defaults to 512-byte sectors.
- Installs a test exception handler that aborts on any libparted exception.
- Creates temporary sparse-ish disk image files.
- Creates and commits a fresh disk label on a `PedDevice`.
- Filters disk-label types that the generic tests should skip.

## Important Functions

- `get_sector_size()` returns a sector size divisible by 512 from the environment or 512.
- `_test_exception_handler()` aborts the test with the exception type and message.
- `_create_disk()` creates `parted-test-XXXXXX`, seeks to `n_bytes`, writes one byte, closes it, and returns the filename.
- `_create_disk_label()` calls `ped_disk_new_fresh()` and `ped_disk_commit()`.
- `_implemented_disk_label()` skips `amiga`, `aix`, `pc98`, and non-512-sector Atari.

## Notable Details

The disk image helper writes one byte after seeking to `n_bytes`, so the resulting file length is `n_bytes + 1`. The label skip list is useful context for weaker backend coverage: Amiga and PC-98 are explicitly excluded from the generic label suite.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/common.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/common.h -->
# File Research: sources/block-storage/parted/libparted/tests/common.h

## Purpose

`common.h` declares shared helpers used by the libparted test programs.

## Contents

- `get_sector_size()`
- `_create_disk()`
- `_create_disk_label()`
- `_implemented_disk_label()`
- `_test_exception_handler()`

## Dependencies and Role

The header includes `<parted/parted.h>` and gives all tests a common way to create disk image fixtures, create labels, filter unsupported labels, and fail on unexpected libparted exceptions.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/common.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/disk.c -->
# File Research: sources/block-storage/parted/libparted/tests/disk.c

## Purpose

`disk.c` tests `ped_disk_duplicate()` on an msdos disk with an extended partition and logical partitions.

## Main Responsibilities

- Creates a temporary disk image sized from `PARTED_SECTOR_SIZE`.
- Creates an msdos disk label.
- Adds one extended partition and two logical ext2 partitions.
- Commits the disk.
- Duplicates the in-memory disk.
- Verifies that partitions 1, 5, and 6 have matching start and end sectors in the duplicate.

## Test Coverage

The test exercises partition duplication across primary/extended/logical msdos layout state, ensuring cloned partition geometry matches the source.

## Notable Details

The test destroys the original disk and device but does not explicitly destroy `disk_dup`, so the test emphasizes behavior over leak checking.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/flags.c -->
# File Research: sources/block-storage/parted/libparted/tests/flags.c

## Purpose

`flags.c` tests that setting filesystem/system type does not overwrite selected partition type flags.

## Main Responsibilities

- Creates an 80 MiB temporary disk image per test case.
- Tests GPT:
  - creates a GPT partition,
  - sets `PED_PARTITION_BIOS_GRUB`,
  - calls `ped_partition_set_system(ext4)`,
  - verifies the BIOS_GRUB flag remains set.
- Tests msdos:
  - creates an msdos partition,
  - sets `PED_PARTITION_BLS_BOOT`,
  - calls `ped_partition_set_system(ext4)`,
  - verifies the BLS_BOOT flag remains set.

## Dependencies and Interactions

Uses libparted GPT and msdos label implementations and the shared exception-aborting test handler.

## Notable Details

The comments in the msdos test say “BIOS_GRUB” even though the actual flag under test is `BLS_BOOT`.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/flags.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/label.c -->
# File Research: sources/block-storage/parted/libparted/tests/label.c

## Purpose

`label.c` provides generic create/probe/read/clone tests for implemented libparted disk-label backends.

## Main Responsibilities

- Creates an 80 MiB temporary disk image for each test case.
- Iterates all registered disk types via `ped_disk_type_get_next()`.
- Skips labels rejected by `_implemented_disk_label()`.
- Tests fresh label creation and commit.
- Tests probing the just-created label.
- Tests reading the just-created label with `ped_disk_new()`.
- Tests duplicating the just-created in-memory label.

## Test Cases

- `test_create_label`
- `test_probe_label`
- `test_read_label`
- `test_clone_label`

## Notable Details

The test prints each label name to stderr as it runs. It checks that probing and reading return the same disk type name as the one created. Skipped types include Amiga, AIX, PC-98, and Atari on non-512-byte sectors.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/label.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/symlink.c -->
# File Research: sources/block-storage/parted/libparted/tests/symlink.c

## Purpose

`symlink.c` tests that libparted preserves `/dev/mapper/...` paths instead of canonicalizing them to `/dev/dm-*`, avoiding operations on stale device-mapper targets after symlink retargeting.

## Main Responsibilities

- Creates a temporary disk image.
- Creates a temporary path under `/dev/mapper`.
- Replaces that temp path with a symlink to the first disk image.
- Gets a `PedDevice` through the `/dev/mapper` symlink.
- Creates a second temporary disk image.
- Retargets the `/dev/mapper` symlink to the second disk image.
- Calls `ped_disk_clobber(dev)`.
- Passes if the operation uses the remembered `/dev/mapper` path and therefore follows the updated symlink.

## Dependencies and Interactions

The shell wrapper requires root because it creates symlinks under `/dev/mapper`.

## Notable Details

The file documents the historical failure mode in detail: older behavior canonicalized `/dev/mapper/foo` to `/dev/dm-N`, and later LVM changes could make the `PedDevice` point at the wrong underlying device.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/t1000-label.sh -->
# File Research: sources/block-storage/parted/libparted/tests/t1000-label.sh

## Purpose

`t1000-label.sh` is the shell wrapper for the `label` Check test binary.

## Main Responsibilities

- Sources `tests/init.sh`.
- Prepends the current directory to `PATH`.
- Runs `label`.
- Exits through the shared `Exit` helper with accumulated failure status.

## Notable Details

The comments say the wrapper is used to find a directory supporting `O_DIRECT`, inherited from the broader test harness behavior.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/t1000-label.sh -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/t1001-flags.sh -->
# File Research: sources/block-storage/parted/libparted/tests/t1001-flags.sh

## Purpose

`t1001-flags.sh` is the shell wrapper for the partition flags unit test.

## Main Responsibilities

- Sources `tests/init.sh`.
- Prepends the current directory to `PATH`.
- Runs `flags`.
- Exits through the shared `Exit` helper.

## Behavior

This wrapper has no special privilege or device setup requirements; it delegates all test logic to `flags.c`.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/t1001-flags.sh -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/t2000-disk.sh -->
# File Research: sources/block-storage/parted/libparted/tests/t2000-disk.sh

## Purpose

`t2000-disk.sh` is the shell wrapper for the `disk` Check test binary.

## Main Responsibilities

- Sources `tests/init.sh`.
- Prepends the current directory to `PATH`.
- Runs `disk`.
- Exits through the shared `Exit` helper.

## Notable Details

Like the label wrapper, comments mention selecting a directory that supports `O_DIRECT`.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/t2000-disk.sh -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/t2100-zerolen.sh -->
# File Research: sources/block-storage/parted/libparted/tests/t2100-zerolen.sh

## Purpose

`t2100-zerolen.sh` sets up a Linux device-mapper test environment and runs the zero-length probing test.

## Main Responsibilities

- Sources `tests/init.sh` and `tests/t-lib-helpers.sh`.
- Requires root privileges.
- Requires device-mapper support.
- Skips unless running on Linux.
- Skips unless `ENABLE_DEVICE_MAPPER=yes`.
- Creates a loop device over a temporary file.
- Creates a linear device-mapper target named `plinear-$$`.
- Waits for `/dev/mapper/<name>` to appear.
- Runs `zerolen /dev/mapper/<name>`.
- Cleans up dmsetup and loop devices, retrying dm removal to tolerate udev races.

## Behavior Under Test

The wrapper supplies a real `/dev/mapper` path so `zerolen.c` can verify that probing a device reported as zero length does not raise an exception.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/t2100-zerolen.sh -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/t3000-symlink.sh -->
# File Research: sources/block-storage/parted/libparted/tests/t3000-symlink.sh

## Purpose

`t3000-symlink.sh` is the privileged shell wrapper for the `/dev/mapper` symlink test.

## Main Responsibilities

- Sources `tests/init.sh`.
- Prepends the current directory to `PATH`.
- Sources `tests/t-lib-helpers.sh`.
- Requires root privileges.
- Runs the `symlink` test binary.
- Exits through the shared `Exit` helper.

## Behavior Under Test

The wrapper provides the root context required for `symlink.c` to create and retarget a symlink under `/dev/mapper`.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/t3000-symlink.sh -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/t4000-volser.sh -->
# File Research: sources/block-storage/parted/libparted/tests/t4000-volser.sh

## Purpose

`t4000-volser.sh` is the shell wrapper for the S390 VOLSER/VTOC test binary.

## Main Responsibilities

- Sources `tests/init.sh`.
- Prepends the current directory to `PATH`.
- Runs `volser`.
- Exits through the shared `Exit` helper.

## Notable Details

The C test itself compiles meaningful tests only on `__s390__` or `__s390x__`; on other architectures it returns success without running VTOC checks.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/t4000-volser.sh -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/volser.c -->
# File Research: sources/block-storage/parted/libparted/tests/volser.c

## Purpose

`volser.c` tests DASD VOLSER and VTOC behavior on S390/S390x builds.

## Main Responsibilities

On S390/S390x only:

- Creates a 20 MiB temporary disk image.
- Creates a `dasd` disk label.
- Opens the device and initializes an fdasd anchor.
- Reads DASD geometry and checks the volume.
- Derives the default VOLSER from the device number.
- Tests reading the default VOLSER after writing labels.
- Tests VOLSER normalization:
  - long input is uppercased and truncated,
  - underscore/space case is normalized,
  - blank input falls back to device-number VOLSER.
- Tests changing the VOLSER and reading it back.
- Tests `fdasd_reuse_vtoc()` preserves the first FMT5 free-space extent.

## Dependencies and Interactions

- Includes `<parted/vtoc.h>`, `<parted/fdasd.h>`, and Linux-specific libparted internals.
- Uses the raw file descriptor from `LinuxSpecific`.
- Exercises code paths that depend on `vtoc.c` helpers.

## Notable Details

On non-S390 architectures, `main()` returns success without running any Check suite. The VTOC reuse comparison uses `&&` between field comparisons, so it aborts only if all compared FMT5 extent fields differ.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/volser.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/tests/zerolen.c -->
# File Research: sources/block-storage/parted/libparted/tests/zerolen.c

## Purpose

`zerolen.c` tests that libparted can probe a device reported as zero length without raising an exception.

## Main Responsibilities

- Accepts a device path argument.
- Sets `PARTED_TEST_DEVICE_LENGTH=0`.
- Installs the exception-aborting test handler.
- Calls `ped_device_get()` on the provided path.
- Destroys the device if it was returned.

## Behavior Under Test

The test is paired with `t2100-zerolen.sh`, which creates a device-mapper device and invokes this binary. Any unexpected libparted exception fails the test.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/tests/zerolen.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/timer.c -->
# File Research: sources/block-storage/parted/libparted/timer.c

## Purpose

`timer.c` implements libparted’s optional `PedTimer` progress reporting API, including nested timers for compound operations.

## Main Responsibilities

- Creates and destroys timers with caller-provided handlers.
- Creates nested timers that update a parent timer over a specified fraction of parent progress.
- Resets timers to the current time and zero progress.
- Updates progress fraction and predicts end time.
- Updates the current operation state name.
- Calls timer handlers whenever timer state changes.

## Important Functions

- `ped_timer_new()` allocates and initializes a timer.
- `ped_timer_new_nested()` creates a timer whose handler forwards progress to a parent.
- `ped_timer_destroy()` and `ped_timer_destroy_nested()` release timers and nested context.
- `ped_timer_touch()` refreshes `now`, clamps predicted end at least to `now`, and invokes the handler.
- `ped_timer_reset()` resets timing fields and progress.
- `ped_timer_update()` stores the new fraction and estimates `predicted_end`.
- `ped_timer_set_state_name()` updates the descriptive phase name.

## Behavior Details

Nested timers capture the parent’s current fraction as `start_frac` and multiply nested progress by `nest_frac`. Passing `NULL` timers is accepted by most operations and becomes a no-op, matching the optional nature of libparted progress reporting.

## Notable Edge Cases

`ped_timer_update()` computes predicted end only when `frac` is nonzero. There is no clamping of `frac` in the update path; only nested timer creation asserts that the nested fraction is between 0 and 1.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/timer.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/unit.c -->
# File Research: sources/block-storage/parted/libparted/unit.c

## Purpose

`unit.c` implements libparted’s `PedUnit` parsing and formatting layer. It converts sectors/bytes to user-facing location strings and parses user-provided locations into sectors plus optional fuzzy geometry ranges.

## Main Responsibilities

- Maintains a global default unit, initially `PED_UNIT_COMPACT`.
- Defines unit names for sectors, bytes, SI units, IEC units, compact, cylinders, CHS, and percent.
- Returns byte sizes for units on a specific device.
- Formats byte or sector locations in a requested or default unit.
- Implements compact formatting by choosing B/kB/MB/GB/TB based on magnitude.
- Parses CHS triplets.
- Parses numeric values with unit suffixes.
- Handles negative offsets as positions from the end of the device.
- Builds an optional `PedGeometry` range around fuzzy unit-based inputs.
- Treats IEC unit inputs as precise locations with zero fuzz radius.
- Clips parsed sectors to the device boundary after validating the range.

## Important Functions

- `ped_unit_set_default()` and `ped_unit_get_default()`.
- `ped_unit_get_size()`, `ped_unit_get_name()`, and `ped_unit_get_by_name()`.
- `ped_unit_format_custom_byte()`, `ped_unit_format_byte()`, `ped_unit_format_custom()`, and `ped_unit_format()`.
- `ped_unit_parse()` and `ped_unit_parse_custom()`.
- Internal helpers:
  - `strip_string()`,
  - `find_suffix()`,
  - `is_chs()`,
  - `parse_chs()`,
  - `parse_unit_suffix()`,
  - `geometry_from_centre_radius()`.

## Behavior Details

Formatting rounds cylinder, sector, and byte units down. Other units use decimal precision based on magnitude and a small epsilon adjustment to avoid surprising IEEE-754 round-half behavior.

Parsing rejects positive values less than 1 and asks callers to use a smaller unit. If no suffix is provided and the requested unit is compact, parsing falls back to the global default unit, or MB if the global default is also compact.

## Notable Edge Cases

- `ped_unit_get_size()` throws an error for `PED_UNIT_COMPACT`.
- CHS parsing accepts any punctuation as separators as long as exactly two punctuation characters are present.
- `strip_string()` removes spaces in place inefficiently and can skip adjacent whitespace because it shifts without decrementing the index.
- Percent unit size is integer-truncated to one percent of total device bytes.

<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/unit.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/parted/Makefile.am -->
# File Research: sources/block-storage/parted/parted/Makefile.am

## Purpose

`Makefile.am` defines the build rules for the `parted` frontend binary and its generated version helper library.

## Main Responsibilities

- Builds `sbin_PROGRAMS = parted`.
- Defines frontend sources:
  - `command.c/.h`,
  - `parted.c`,
  - `strlist.c/.h`,
  - `ui.c/.h`,
  - `jsonwrt.c/.h`,
  - `table.c/.h`.
- Builds an internal `libver.a` from generated `version.c` and `version.h`.
- Generates `version.c` with `Version = "$(PACKAGE_VERSION)"`.
- Links `parted` with `libver.a`, `libparted.la`, intl libs, and configured parted libs.
- Adds include paths for source lib, build include, and source include directories.
- Adds linker flags to ignore unused shared-library references.

## Notable Details

Generated version files are chmodded read-only before being moved into place and are removed by `DISTCLEANFILES`.

<!-- END FILE RESEARCH: sources/block-storage/parted/parted/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/parted/command.c -->
# File Research: sources/block-storage/parted/parted/command.c

## Purpose

`command.c` implements command registration, lookup, help display, and dispatch for the interactive/non-interactive `parted` frontend.

## Main Responsibilities

- Allocates `Command` objects with names, method callback, summary, help text, and non-interactive flag.
- Frees command name/summary/help string lists.
- Registers commands into a NULL-terminated command array.
- Resolves command names by exact or unambiguous partial match.
- Collects all command names into one `StrList`.
- Prints command summaries and help text with wrapping based on terminal width.
- Runs a command callback.

## Important Functions

- `command_create()`
- `command_destroy()`
- `command_register()`
- `command_get()`
- `command_get_names()`
- `command_print_summary()`
- `command_print_help()`
- `command_run()`

## Behavior Details

`command_get()` returns an exact match immediately. For partial matches, it returns the command only if exactly one command matches partially; ambiguous partials return `NULL`.

## Dependencies and Interactions

Uses `StrList` helpers, UI `screen_width()`, `xmalloc()`, and libparted device/disk pointer types in command callbacks.

<!-- END FILE RESEARCH: sources/block-storage/parted/parted/command.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/parted/command.h -->
# File Research: sources/block-storage/parted/parted/command.h

## Purpose

`command.h` declares the `Command` structure and command helper functions for the `parted` frontend.

## Contents

- `Command` fields:
  - `names`,
  - `method`,
  - `summary`,
  - `help`,
  - one-bit `non_interactive` flag.
- Function declarations for create, destroy, register, lookup, name aggregation, summary/help printing, and command execution.

## Dependencies and Role

Includes `<parted/parted.h>` for `PedDevice` and `PedDisk`, and `strlist.h` for command names and documentation text. This header is the frontend’s command-dispatch contract.

<!-- END FILE RESEARCH: sources/block-storage/parted/parted/command.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/parted/jsonwrt.c -->
# File Research: sources/block-storage/parted/parted/jsonwrt.c

## Purpose

`jsonwrt.c` is a small public-domain JSON writer used by the `parted` frontend for JSON output formatting.

## Main Responsibilities

- Escapes JSON string values.
- Optionally uppercases or lowercases ASCII/non-ASCII bytes while writing quoted strings.
- Maintains indentation level.
- Opens and closes JSON objects, arrays, and values.
- Handles comma insertion between closed elements.
- Writes raw values, strings, unsigned 64-bit numbers, booleans, and nulls.

## Important Functions

- `ul_jsonwrt_init()`
- `ul_jsonwrt_indent()`
- `ul_jsonwrt_open()`
- `ul_jsonwrt_close()`
- `ul_jsonwrt_value_raw()`
- `ul_jsonwrt_value_s()`
- `ul_jsonwrt_value_u64()`
- `ul_jsonwrt_value_boolean()`
- `ul_jsonwrt_value_null()`

## Behavior Details

String escaping handles double quotes, backslashes, standard control-character escapes, and other control characters as `\u00XX`. Object member names are lowercased by `ul_jsonwrt_open()` when a name is provided.

The writer uses three spaces per indent level. `after_close` controls whether commas/newlines are emitted before the next sibling.

## Notable Edge Cases

The case-conversion loop treats `char` bytes as unsigned for indexing but uses `toupper()`/`tolower()` on non-ASCII byte values; this is byte-oriented, not full Unicode case conversion. `ul_jsonwrt_close()` has special root-object behavior when `indent == 1`.

<!-- END FILE RESEARCH: sources/block-storage/parted/parted/jsonwrt.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/parted/jsonwrt.h -->
# File Research: sources/block-storage/parted/parted/jsonwrt.h

## Purpose

`jsonwrt.h` declares the small JSON writer API used by the `parted` frontend.

## Contents

- JSON node type enum:
  - `UL_JSON_OBJECT`,
  - `UL_JSON_ARRAY`,
  - `UL_JSON_VALUE`.
- `struct ul_jsonwrt` with output stream, indentation level, and `after_close` state.
- Core functions:
  - initialize,
  - indent,
  - open,
  - close.
- Convenience macros for root/object/array/value open and close operations.
- Value writer declarations for raw, string, u64, boolean, and null values.

## Dependencies and Role

The header assumes `FILE` and `uint64_t` are available through includers or previous includes. It is a frontend-local formatting API rather than a general libparted API.

<!-- END FILE RESEARCH: sources/block-storage/parted/parted/jsonwrt.h -->