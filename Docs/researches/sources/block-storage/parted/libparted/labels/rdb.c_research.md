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
