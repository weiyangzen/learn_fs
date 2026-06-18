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
