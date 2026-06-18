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
