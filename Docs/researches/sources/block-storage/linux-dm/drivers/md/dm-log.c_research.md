# File Research: sources/block-storage/linux-dm/drivers/md/dm-log.c

## Purpose

`dm-log.c` implements Device Mapper dirty-region log registration plus the built-in `core` and `disk` dirty log types used by mirror-like targets to track clean, dirty, synchronized, and recovering regions.

## Type Registry

The file maintains `_log_types` under `_lock`. `dm_dirty_log_type_register()` and `dm_dirty_log_type_unregister()` add and remove `dm_dirty_log_type` implementations. `dm_dirty_log_create()` resolves a type by name, loads modules named `dm-log-<type>` with fallback truncation at hyphens, takes the module reference, allocates `struct dm_dirty_log`, and calls the selected constructor. Destroy calls the type destructor, drops the module reference, and frees the log.

## Core Data Model

`struct log_c` stores the target, region size/count, sync count, flags for dirty/clean bitmap updates, optional persistent log state, and three bitmaps:

- `clean_bits`: whether each region is clean.
- `sync_bits`: whether each region is synchronized.
- `recovering_bits`: regions currently assigned for resync work.

`log_set_bit()` marks cleaned state touched; `log_clear_bit()` marks dirtied state touched. Region size must be a power of two, at least two sectors, and no larger than the target.

## Core Log

The `core` type is memory-only. Constructor arguments are `<region_size> [sync|nosync]`. `nosync` initializes all regions synchronized; default and `sync` initialize them needing resync unless later state says otherwise. The core log implements region clean/dirty marking, sync queries, resync work selection, sync completion accounting, and table/info status. `core_flush()` is a no-op because state is not persistent.

## Disk Log

The `disk` type uses arguments `<log_device> <region_size> [sync|nosync]`. It embeds the on-disk header at sector 0 and the clean bitmap after `LOG_OFFSET` sectors in one vmalloc buffer, accessed through `dm_io`. The disk header stores `MIRROR_MAGIC`, disk version 2, and `nr_regions`.

`disk_resume()` reads the header, initializes a new log if forced or magic is absent, rejects incompatible versions, adjusts bitmap state for grown/shrunk target sizes, copies `clean_bits` into `sync_bits`, recalculates `sync_count`, writes the updated header/bits, and flushes the log device. Read or write failures mark the log device failed and trigger a table event.

## Flush And Failure Semantics

`disk_flush()` writes persistent changes only when clean or dirty state was touched. If regions were marked clean and the caller supplied `flush_callback_fn`, that callback must succeed first; if it fails, all regions are marked dirty because the target cannot trust which clean transitions reached storage. Dirtying changes are followed by a preflush to the log device. Status reports log-device state as active, device failed, or flush failed.

## Invariants And Risks

- Persistent dirty log correctness depends on writing the clean bitmap and issuing required flushes after dirty transitions.
- On log-device read failure, all regions must be treated as out-of-sync; the code resets header region count and continues conservatively.
- `recovering_bits` prevents duplicate resync assignment for the same region.
- `sync_count` must track `sync_bits` transitions exactly.
- `flush_failed` suppresses later clean marking to avoid false-clean regions after an ordering failure.
- Disk log buffer size is rounded to the log device logical block size and rejected if larger than the log device.

## Test Focus

Test type registration duplicates/unregister misses, module autoload name fallback, invalid region sizes, `sync`/`nosync` initialization, disk header version rejection, target grow/shrink behavior, read/write/flush log-device failures, flush callback failure marking all dirty, resync work allocation with recovering bits, sync count updates, and status/table output for core and disk logs.
