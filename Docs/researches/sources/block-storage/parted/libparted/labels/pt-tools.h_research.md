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
