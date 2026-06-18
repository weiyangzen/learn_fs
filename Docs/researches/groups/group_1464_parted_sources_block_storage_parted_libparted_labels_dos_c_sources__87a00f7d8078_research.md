# Group Research: group_1464_parted_sources_block_storage_parted_libparted_labels_dos_c_sources__87a00f7d8078

Scope verified against `Docs/research_subset_a.md`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/dos.c -->
# File Research: sources/block-storage/parted/libparted/labels/dos.c

This file implements libparted’s `msdos`/MBR disk label backend, including primary and extended partition parsing, type ID mapping, CHS/LBA compatibility handling, writeback, alignment, metadata reservation, and registration of the `msdos` `PedDiskType`.

Key structures and constants:
- Defines raw packed MBR structures: `RawCHS`, `DosRawPartition`, and `DosRawTable`; asserts `DosRawPartition == 16` and `DosRawTable == 512` at init.
- Uses `DosDiskData` for disk-level state, currently `cylinder_alignment`.
- Uses `DosPartitionData` for partition type ID, boot flag, and `OrigState` preserving original geometry/raw entry/LBA offset.
- Encodes common MBR type IDs for FAT, NTFS/HPFS/UDF, extended partitions, Linux, swap, LVM, RAID, ESP, PReP, PALO, diagnostics, LDM, GPT protective, IRST, and BLS boot.

Core behavior:
- `msdos_probe()` reads sector 0 via `ptt_read_sector()`, checks the `0xAA55` signature, rejects whole-disk FAT/NTFS filesystems, rejects invalid boot indicators, rejects protective GPT entries, rejects AIX physical volumes, and optionally defers to PC98 detection.
- `read_table()` recursively parses primary and extended boot records, protects against recursive extended entries, creates `PedPartition` objects, probes filesystems for non-extended partitions, and adds exact-geometry constraints.
- `msdos_read()` clears the disk partition list, parses from LBA 0, then optionally infers BIOS CHS geometry from partition entries/filesystems and rereads if the device geometry changes.
- Write support preserves the existing boot sector contents, generates a nonzero MBR signature when absent, fills primary entries, recursively writes EBR chains for logical partitions, writes empty extended tables when needed, and syncs the device.
- Type/flag support maps libparted flags to MBR type IDs, including `boot`, `hidden`, `lba`, `swap`, `raid`, `lvm`, `esp`, `prep`, `palo`, `diag`, `irst`, `bls_boot`, and `msft_reserved`.
- `msdos_partition_set_system()` derives type IDs from filesystem names but preserves special type IDs in `skip_set_system_types`.
- Alignment code supports legacy cylinder alignment, Vista-style first partition sector 2048, logical partition EBR gaps, and fallback non-CHS constraints.
- Metadata allocation creates placeholder partitions for the MBR/bootloader area, final partial cylinder, EBR sectors/gaps, and the beginning of the extended partition.
- Partition numbering is fixed to primary slots 1-4 and logical slots 5-64.

Integration:
- Depends on `misc.h` for `generate_random_uint32()` and `is_linux_swap()`.
- Depends on `pt-tools.h` for sector table I/O helpers.
- Uses `pt-common.h` / `PT_define_limit_functions(msdos)` to populate standard partition-table operations.
- Exposes type-ID get/set operations through `PED_DISK_TYPE_PARTITION_TYPE_ID`.

Risk notes:
- CHS inference and alignment logic is intentionally compatibility-heavy and sensitive to malformed historical partition tables.
- `msdos_partition_duplicate()` assumes active partitions have `disk_specific`; this matches local allocation patterns but is not defensive against unexpected inactive input.
- `msdos_partition_set_flag(PED_PARTITION_BOOT)` clears the boot flag from other active partitions, enforcing a single active boot partition.
- Extended partition parsing tolerates some invalid signatures through user exceptions, so behavior depends on libparted exception policy.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/dos.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/dvh.c -->
# File Research: sources/block-storage/parted/libparted/labels/dvh.c

This file implements libparted’s SGI disk volume header (`dvh`) backend.

Key structures:
- `DVHDiskData`: stores copied device parameters plus root, swap, and boot partition numbers.
- `DVHPartData`: stores SGI partition type, boot-file name, and real boot-file byte size.
- Uses constants from `dvh.h`: `VHMAGIC`, `NPARTAB`, `NVDIR`, `PTYPE_*`, and volume header/device structures.

Core behavior:
- `dvh_probe()` reads sector 0 and checks the big-endian SGI volume header magic.
- `dvh_alloc()` creates a fresh disk and adds a default volume header partition from sector 0 through `PTYPE_VOLHDR_DFLTSZ - 1`, using partition number 9 by convention.
- `dvh_read()` validates the two’s-complement checksum, parses normal partitions from `vh_pt[]`, skips the whole-volume partition, parses boot files from `vh_vd[]`, probes filesystems, and maps root/swap/boot flags.
- If no volume-header partition exists, `_handle_no_volume_header()` can create one and optionally write the fixed label back.
- `dvh_write()` rebuilds a 512-byte `struct volume_header`, emits partition table entries, boot file directory entries, root/swap indices, whole-disk partition slot, device geometry, checksum, and writes sector 0.
- `dvh_partition_set_system()` maps extended partitions to `PTYPE_VOLHDR`, XFS to `PTYPE_XFS`, and other normal partitions to `PTYPE_RAW`; logical partitions are boot files and keep their type.
- Root and swap flags are allowed only on primary partitions; boot is allowed only on logical boot-file partitions.
- Partition names are supported only for logical boot-file entries.
- Alignment constrains the volume header partition to include sector 0 and normal partitions to sectors 1 through end-of-device.
- Enumeration reserves the whole-volume slot, uses slots 1-16 for normal entries, slot 9 for volume header, and slots 17-31 for boot files.
- Metadata allocation adds sector 0 as metadata unless the extended volume-header partition already covers it.

Integration:
- Registers `PedDiskType` named `dvh` with `PED_DISK_TYPE_PARTITION_NAME | PED_DISK_TYPE_EXTENDED`.
- Uses `ptt_read_sector()` / `ptt_write_sector()` for sector-safe I/O.
- Uses `pt-common.h` operation initializers.

Risk notes:
- `dvh_duplicate()` copies only `dev_params`, not root/swap/boot state, which may be intentional but is a notable preservation gap.
- Boot file geometry uses `length / 512`, so non-512 device sector sizes and byte lengths that are not sector-aligned require care.
- The checksum assumes the in-memory `struct volume_header` layout remains exactly 512 bytes, enforced at init.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/dvh.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/dvh.h -->
# File Research: sources/block-storage/parted/libparted/labels/dvh.h

This header defines the on-disk SGI Disk Volume Header structures and constants consumed by `dvh.c`.

Key definitions:
- `struct device_parameters`: SGI/IRIX device geometry and controller parameters.
- `struct volume_directory`: named volume-header file entries with logical block and byte length.
- `struct partition_table`: SGI logical partition entries with first LBN, block count, and partition type.
- `struct volume_header`: 512-byte sector-0 SGI volume header containing magic, root/swap indices, boot filename, device parameters, volume directory, partition table, checksum, and fill.
- Partition type constants include `PTYPE_VOLHDR`, replacement areas, raw, BSD, SysV, EFS, volume, XFS, XFS log, XLV, XVM, and ARCS FAT/extended values.
- Defines `VHMAGIC`, `NPARTAB == 16`, `NVDIR == 15`, `VDNAMESIZE == 8`, and `BFNAMESIZE == 16`.

Behavioral context:
- Comments document the checksum rule: zero `vh_csum`, sum the full structure, store the 32-bit two’s-complement so validation sums to zero.
- Notes that the volume header is sector 0 and historically had unused sector-0 copies on each track of cylinder 0.

Risk notes:
- The header is a raw disk format contract; layout, endian conversion, and struct size assumptions are critical.
- `BOOTABLE` and `NOT_BOOTABLE` macros include trailing semicolons, but they are not used by the listed implementation.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/dvh.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/efi_crc32.c -->
# File Research: sources/block-storage/parted/libparted/labels/efi_crc32.c

This file provides the CRC32 implementation used by EFI/GPT code.

Key API:
- `__efi_crc32(const void *buf, unsigned long len, uint32_t seed)`: computes a table-driven CRC32 over `len` bytes using the caller-supplied seed.

Behavior:
- Uses a static 256-entry CRC32 table for polynomial `0xedb88320`.
- Iterates byte-by-byte, updating `crc32val` as `crc32_tab[(crc32val ^ s[i]) & 0xff] ^ (crc32val >> 8)`.
- GPT wraps this helper with seed `~0L` and final xor `~0L`.

Integration:
- Included through libparted’s CRC32 declaration path and used by `gpt.c` as `__efi_crc32()`.
- Source comments trace this implementation to Gary S. Brown’s public-domain CRC code with later EFI-oriented modifications.

Risk notes:
- No NULL guard exists; callers must pass a valid buffer for nonzero length.
- The function is pure with respect to input memory and has no allocation or I/O.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/efi_crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/fdasd.c -->
# File Research: sources/block-storage/parted/libparted/labels/fdasd.c

This file is the IBM s390 DASD/VTOC helper implementation used by libparted’s DASD support, adapted from Linux `fdasd`.

Key responsibilities:
- Maintains an `fdasd_anchor_t` with geometry, VTOC labels, volume label, partition list, free-space state, and DASD metadata.
- Reads, validates, recreates, prepares, and writes VOL1/VTOC labels.
- Creates and updates format 1, 4, 5, 7, 8, and 9 labels.
- Handles DASD-specific geometry, device type, API version, volume serial, and partition data set names.

Core behavior:
- `fdasd_initialize_anchor()` zeroes the anchor, initializes partition-number mappings, allocates label buffers, initializes the format 9 template, and creates a linked list of `partition_info_t` nodes.
- `fdasd_cleanup()` frees label buffers and partition-info nodes.
- `fdasd_error()` maps local failure enums to translated libparted exceptions.
- `fdasd_get_geometry()` uses regular-file simulation for tests, otherwise uses `BLKGETSIZE64`, `HDIO_GETGEO`, `BLKSSZGET`, and `BIODASDINFO`; it also supports fallback validation as DASD 3390 geometry.
- `fdasd_check_api_version()` checks the DASD kernel driver API unless operating on a regular file.
- `fdasd_check_volume()` reads the volume label, validates `VOL1`, `LNX1`, or `CMS1`, follows the VTOC pointer, initializes missing labels for unlabeled non-file devices, and handles FBA layout.
- `fdasd_valid_vtoc_pointer()` reads format 4 and processes valid or invalid VTOC cases.
- `fdasd_process_valid_vtoc()` scans VTOC records, loads FMT1/FMT8 partition labels, initializes missing FMT5/FMT7 labels, handles old partition-name numbering, reorganizes labels, and updates partition info.
- `fdasd_recreate_vtoc()` and `fdasd_reuse_vtoc()` rebuild free-space and partition labels while preserving relevant partition extents/name fields.
- `fdasd_add_partition()` allocates an unused FMT1/FMT8 label, computes track extents, inserts the partition in sorted order, updates FMT4 and free-space labels, and marks VTOC changed.
- `fdasd_prepare_labels()` and `fdasd_write_vtoc_labels()` generate or preserve EBCDIC data set names, emit VTOC labels, write FMT9 companions for FMT8 labels, and clear leftover label slots.
- `fdasd_write_labels()` writes volume and VTOC labels only when marked changed.
- `fdasd_check_volser()`, `fdasd_get_volser()`, and `fdasd_change_volser()` validate, read, and update six-character volume serials.

Integration:
- Depends heavily on `parted/vtoc.h`, `parted/fdasd.h`, `parted/device.h`, Linux DASD ioctls, and libparted exception handling.
- Track/cylinder conversions are delegated to VTOC helpers such as `cchh2trk()`, `cchhb2blk()`, `vtoc_set_extent()`, and EBCDIC conversion helpers.
- Unlike the disk-label backend files, this file does not register a `PedDiskType`; it is a helper layer for DASD label code elsewhere.

Risk notes:
- Several string operations use fixed VTOC field lengths and `sprintf`/`strncpy`; the surrounding buffers are fixed-size by format contract, so correctness depends on the hard-coded field sizes.
- Regular-file geometry simulation is explicitly for testing and may not model all DASD layout edge cases.
- `fdasd_error()` throws exceptions but returns `void`; callers rely on libparted exception semantics rather than direct error propagation in several paths.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/fdasd.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/gpt.c -->
# File Research: sources/block-storage/parted/libparted/labels/gpt.c

This file implements libparted’s EFI GUID Partition Table (`gpt`) backend.

Key structures and constants:
- Defines EFI GUID representation, GPT header, GPT partition-entry attributes, partition entries, protective MBR records, and disk/partition private data.
- `GPTDiskData` stores usable data area, entry count, disk UUID, PMBR boot flag, and backup header LBA.
- `GPTPartitionData` stores type GUID, unique GUID, UTF-16LE name, cached translated name, and GPT attributes.
- Defines GUID constants for EFI system, BIOS GRUB, MSR, Microsoft recovery/basic data, Linux data, swap, RAID, LVM, reserved, HP service, Apple HFS/TV recovery, PReP, IRST, ChromeOS kernel, BLS boot, and Linux home.

Core behavior:
- `gpt_probe()` requires a valid protective MBR and a GPT signature in either primary or backup header.
- Header helpers allocate variable-size header storage, copy raw sector data, reconstruct raw sector images, and compute GPT header CRC32.
- `_header_is_valid()` validates signature, header size, partition-entry size, `MyLBA`, `AlternateLBA`, partition-entry-array CRC, usable LBA range, and header CRC.
- `gpt_read_headers()` reads PMBR boot state, validates primary and backup headers, and chooses the backup LBA from the primary or device end.
- `gpt_read()` handles primary/backup corruption combinations, warns or repairs backup-header placement, parses header metadata, reads the partition-entry array, validates CRC, creates partitions for non-unused entries, probes filesystems, and optionally writes repairs.
- `_parse_header()` handles newer GPT revisions, detects grown devices, offers to move the backup GPT to the new end, and initializes `data_area`, entry count, and disk UUID.
- `gpt_write()` emits a protective MBR, primary header/table, and backup header/table with correct CRCs and syncs the device.
- Partition creation generates Linux data type GUIDs and unique GUIDs by default.
- Filesystem-to-GUID mapping chooses Microsoft basic data for FAT/UDF/NTFS, Apple HFS for HFS variants, Linux swap for swap, and Linux data by default, while preserving special GUIDs in `skip_set_system_guids`.
- Flag handling maps many libparted flags to type GUIDs and maps hidden, legacy boot, and no-automount to GPT attributes.
- Name support converts between the current locale codeset and `UCS-2LE` via `iconv`.
- UUID get/set functions expose disk, partition type, and partition UUIDs in byte-array form with EFI/RFC byte-order conversion.
- Metadata allocation reserves PMBR/header/table at the beginning and header/table at the end.

Integration:
- Uses `efi_crc32.c` through `__efi_crc32()`.
- Uses `pt-tools.h` for safe sector helpers and `pt-common.h` for standard operations.
- Uses gnulib helpers `xalloc.h`, `xalloc-oversized.h`, and `verify.h`.
- Registers `PedDiskType` named `gpt` with partition names, partition type UUIDs, disk UUIDs, and partition UUIDs.

Risk notes:
- `pth_new()` does not check its first allocation before assigning `Reserved2`, so allocation failure paths rely on `ped_malloc` behavior.
- `gpt_get_max_supported_partition_count()` attempts a fallback read at `disk->dev->length`, which is one past the last sector; the surrounding logic tolerates failure but the expression is notable.
- Name conversion failure closes `conv` even in the error path; if `iconv_open()` failed, `conv` is `(iconv_t)-1`.
- GPT repair behavior depends on interactive exception handling and may clear stale backup-header sectors when the user selects fix.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/gpt.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/loop.c -->
# File Research: sources/block-storage/parted/libparted/labels/loop.c

This file implements libparted’s `loop` pseudo-label backend, representing an entire device as one partition.

Key behavior:
- `loop_probe()` succeeds if sector 0 contains `GNU Parted Loopback 0` or if a filesystem is detected across the whole device.
- `loop_alloc()` rejects devices shorter than 256 sectors, allocates a disk, and creates a single normal partition covering the full device.
- `loop_read()` clears partitions, checks for the loop signature, probes a whole-device filesystem, and creates partition 1 spanning the whole device.
- `loop_write()` writes the loop signature into sector 0 only when partition 1 has no filesystem type; existing whole-device filesystems are not overwritten.
- Partition operations support setting filesystem type, alignment to caller constraints, enumeration as partition 1, and no partition flags.
- Metadata allocation is a no-op.
- Maximum primary and supported partition counts are both 1.

Integration:
- Registers `PedDiskType` named `loop` with no special feature flags.
- Uses `ptt_read_sector()` for initial sector reads and libparted filesystem probing for whole-device detection.
- Uses `pt-common.h` operation initialization.

Risk notes:
- `loop_alloc()` uses assertions after `_ped_disk_alloc()`, `ped_geometry_new()`, and `ped_partition_new()`; in non-debug behavior allocation failure handling is limited.
- `loop_write()` uses `alloca()` with sector size and `strcpy()` of a fixed short signature, which is safe for normal sector sizes but assumes sector size is large enough.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/loop.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/mac.c -->
# File Research: sources/block-storage/parted/libparted/labels/mac.c

This file implements libparted’s Apple Partition Map (`mac`) backend.

Key structures and constants:
- Defines packed on-disk structures `MacRawDisk`, `MacRawPartition`, and `MacDeviceDriver`.
- `MacDiskData` tracks ghost block size, partition map entry counts, active/free entry counts, block size, driver count, and driver descriptors.
- `MacPartitionData` stores Apple volume/type/processor names, boot/driver/root/swap/LVM/RAID flags, data/boot region lengths, boot addresses/checksum, status, and driver signature.
- Recognizes driver descriptor magic `0x4552` and partition magic values `0x5453` and `0x504d`.

Core behavior:
- `mac_probe()` reads sector 0 and validates the driver descriptor signature.
- `mac_alloc()` creates a fresh disk and immediately adds an `Apple_partition_map` partition starting at sector 1.
- `mac_read()` validates block 0, adjusts sector size to match the driver descriptor when accepted, detects ghost partition-map spacing, loads driver descriptors, scans partition map entries, validates map size consistency, skips inactive Apple free/void/scratch/extra entries, analyzes active partitions, probes filesystems, and auto-adds a missing partition-map entry if permitted.
- Ghost handling supports maps where OpenFirmware uses 512-byte blocks while device drivers use larger blocks; `_pad_raw_part()` fills non-real entries with `Apple_Void`.
- `_rawpart_analyse()` converts raw entries into `PedPartition` objects, detects boot, driver, root, swap, LVM, RAID, data/boot regions, status, driver signatures, and validates region coverage.
- `mac_write()` ensures a partition-map entry exists, generates raw entries for active partitions, generates Apple_Free entries for free-space regions, fills remaining entries with Apple_Void, writes the partition map, and rewrites block 0 driver descriptor data.
- `mac_partition_set_system()` maps HFS/HFS+/HFSX to Apple HFS types, boot partitions to `Apple_Bootstrap`, Linux swap names via `is_linux_swap()`, and default partitions to `Apple_UNIX_SVR2`.
- Flags support boot, root, swap, LVM, and RAID. Root/swap flags also update the Apple partition name to `root` or `swap`.
- Name support reads/writes the Apple partition name field; changing a root/swap name can clear those flags after warning.
- Enumeration assigns entries within the current partition-map capacity and reserves entries for free-space accounting.
- Metadata allocation reserves sector 0 and updates partition/free-entry counts during update-mode pop.
- Maximum primary count is computed from the partition-map partition size, ghost size, and current free-space entry count.

Integration:
- Uses `misc.h` for Linux swap detection.
- Uses `pt-tools.h` sector helpers and `pt-common.h` operation initialization.
- Registers `PedDiskType` named `mac` with partition-name support.

Risk notes:
- `mac_write()` mutates disk-private partition-map counts, hence the write op is cast from non-const to const in the ops table with a FIXME.
- The code can modify `disk->dev->sector_size` based on the on-disk driver descriptor after warning/ignore flow.
- Apple Partition Map requires entries for free space, so max-partition calculations depend on transient free-space partitions generated by libparted update mode.
- Several fixed-size Apple string fields are truncated to 31/32 bytes by design.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/mac.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/labels/misc.h -->
# File Research: sources/block-storage/parted/libparted/labels/misc.h

This header provides small shared inline helpers for libparted label implementations.

Key APIs:
- `generate_random_uint32()`: uses `uuid_generate()` to obtain random bytes, returns the first `uint32_t`, and substitutes `0xffffffff` if the generated value is zero.
- `is_linux_swap(char const *fs_type_name)`: returns true when a filesystem type name starts with `linux-swap`.

Integration:
- `dos.c` uses `generate_random_uint32()` for nonzero MBR disk signatures and `is_linux_swap()` for type-ID selection.
- `mac.c` uses `is_linux_swap()` when mapping filesystem types to Apple partition semantics.
- Requires `<uuid/uuid.h>` and `<inttypes.h>`; assumes callers include string declarations as needed through surrounding includes.

Risk notes:
- `generate_random_uint32()` intentionally uses only four bytes of a UUID, so uniqueness is limited to 32 bits.
- The helper avoids zero because zero can be interpreted as no FAT serial number or no MBR signature.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/labels/misc.h -->