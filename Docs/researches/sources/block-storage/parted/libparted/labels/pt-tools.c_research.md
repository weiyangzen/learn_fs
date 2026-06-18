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
