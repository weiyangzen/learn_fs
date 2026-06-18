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
