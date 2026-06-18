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
