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
