# File Research: sources/block-storage/linux-dm/drivers/md/dm-stats.h

## Purpose
Declares the device-mapper statistics API used by DM core code and implemented in `dm-stats.c`.

## Public Types
- `struct dm_stats`: owns the stats-region list, mutex, and per-CPU last-position tracking.
- `struct dm_stats_aux`: per-I/O auxiliary accounting state, currently merge flag and precise duration timestamp.
- Forward declaration of `struct mapped_device`.

## Public Functions
- Lifecycle:
  - `dm_statistics_init()`
  - `dm_statistics_exit()`
  - `dm_stats_init()`
  - `dm_stats_cleanup()`
- Message handling:
  - `dm_stats_message()`
- I/O accounting:
  - `dm_stats_account_io()`
- Helper:
  - `dm_stats_used()` returns whether any stats regions exist.

## Dependencies
- Kernel list/mutex/types headers.
- `sector_t` and block I/O direction conventions from kernel block types.

## Contract Notes
- `dm_stats_account_io()` requires callers to pass the same `dm_stats_aux` across I/O start/end if precise timing is used.
- `dm_stats_used()` only checks list emptiness; callers must use it in a context where list lifetime is valid.
