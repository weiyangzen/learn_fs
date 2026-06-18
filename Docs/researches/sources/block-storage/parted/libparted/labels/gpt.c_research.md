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
