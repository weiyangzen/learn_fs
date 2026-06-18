# File Research: sources/block-storage/linux-dm/drivers/md/raid1.c

## Purpose
Implements the Linux MD RAID1 personality: mirrored read balancing, replicated writes, write-behind for write-mostly devices, bad-block repair, disk failure handling, hot add/remove, resync/recovery/check/repair, resize/reshape, and personality registration.

## Main Interfaces
- Personality registration: `raid1_personality`, `raid_init()`, `raid_exit()`.
- Request path: `raid1_make_request()`, `raid1_read_request()`, `raid1_write_request()`, `read_balance()`.
- Completion path: `raid1_end_read_request()`, `raid1_end_write_request()`, `raid_end_bio_io()`, `r1_bio_write_done()`, `close_write()`.
- Retry/worker path: `raid1d()`, `reschedule_retry()`, `handle_read_error()`, `handle_write_finished()`, `handle_sync_write_finished()`.
- Resync/recovery: `raid1_sync_request()`, `sync_request_write()`, `end_sync_read()`, `end_sync_write()`, `fix_sync_read_error()`, `process_checks()`.
- Configuration/lifecycle: `setup_conf()`, `raid1_run()`, `raid1_free()`, `raid1_quiesce()`, `raid1_size()`, `raid1_resize()`, `raid1_reshape()`, `raid1_takeover()`.
- Device management: `raid1_add_disk()`, `raid1_remove_disk()`, `raid1_spare_active()`, `raid1_error()`.
- Serialization/barriers: `wait_for_serialization()`, `remove_serial()`, `raise_barrier()`, `lower_barrier()`, `wait_barrier()`, `wait_read_barrier()`, `freeze_array()`, `unfreeze_array()`.

## Control Flow
Normal bios enter `raid1_make_request()`. Flushes are delegated to `md_flush_request()`. Other bios are capped at the end of their 64 MiB barrier unit by `align_to_barrier_unit_end()` so normal I/O and resync barriers do not span barrier buckets. Reads call `raid1_read_request()`. Writes first call `md_write_start()` and then `raid1_write_request()`.

`raid1_read_request()` waits for an array-freeze read barrier, allocates or reinitializes an `r1bio`, chooses a mirror with `read_balance()`, splits if a bad-block or recovery boundary reduces the readable sector count, clones the bio to the chosen component, applies `data_offset`, optional failfast, and trace remap metadata, then submits it. `read_balance()` prefers in-sync, non-faulty, non-bad-block devices; handles recovery windows and clustered resync areas; preserves sequential reads where possible; otherwise balances by head distance for rotational media or pending I/O when non-rotational devices are present. It increments the chosen rdev's `nr_pending` before returning.

`raid1_write_request()` waits for clustered resync conflicts and local write barriers, allocates an `r1bio`, scans all primary and replacement mirrors under RCU, skips missing/faulty/bad-blocked targets, waits for blocked rdevs when necessary, splits around bad blocks or write-behind vector limits, starts bitmap write tracking, optionally creates a copied write-behind master bio for write-mostly targets, serializes overlapping writes when required, clones the bio to every target mirror, queues those component bios through plug-local or conf-global pending lists, and lets `raid1d()` flush them after bitmap updates.

Read completion sets `R1BIO_Uptodate` on success. On retryable read error it records `R1BIO_ReadError`, leaves the rdev pending reference held, and queues the r1bio to `raid1d()`. Write completion records write errors, replacement requests, degraded state, successful mirrors, bad-blocks made good, write-behind early completion, serialization removal, rdev pending drops, and final write completion or retry scheduling.

`raid1d()` is the personality thread. It runs MD recovery checks, completes delayed bio endio once pending superblock changes are clear, flushes pending writes, and processes retry-list entries. It routes sync bios to `sync_request_write()` or `handle_sync_write_finished()`, normal write repair to `handle_write_finished()`, and read repair to `handle_read_error()`.

Read repair in `handle_read_error()` freezes the array for writable, non-failfast arrays, calls `fix_read_error()` to synchronously find a good copy, writes it back to other mirrors, rereads to verify, records corrected errors, or marks bad blocks/fails devices when no repair is possible. Read-only arrays preserve an `IO_BLOCKED` marker and retry on another mirror without failing or rewriting the original device.

Resync/recovery is driven by `raid1_sync_request()`. It lazily initializes the resync buffer pool, skips clean bitmap ranges when allowed, raises a barrier for the current sector bucket, builds a resync `r1bio`, selects read and write targets across primaries and replacements, accounts bad blocks, caps the request by bitmap chunks, bad-block transitions, `resync_max`, and page capacity, sends clustered resync window updates, then submits either all readable devices for check/repair or one read source for recovery. Completion flows through `end_sync_read()`, `sync_request_write()`, `end_sync_write()`, and the retry worker.

Configuration starts in `setup_conf()`, which allocates barrier bucket arrays, mirror slots for primaries plus replacements, a temporary repair page, mempool metadata, the normal r1bio pool, the split bioset, and the raid1d thread, then copies current rdev placement into `conf->mirrors`. `raid1_run()` validates the level and reshape state, initializes write accounting, configures queue support, computes degraded count, requires at least one active mirror, installs the thread/config, sets failfast support, sets array capacity, updates discard support, and registers integrity state.

`raid1_reshape()` supports changing the number of mirrors without changing level/layout/chunk size. It allocates a new r1bio pool and mirror array, freezes the array, swaps pools, packs existing devices into low raid-disk numbers, updates sysfs links and degraded counts, unfreezes, schedules recovery, and destroys the old pool.

## State And Synchronization
`struct r1conf` in `mddev->private` owns the mirror table, raid disk count, retry lists, pending write list, barrier bucket arrays, mempools, split bioset, repair page, raid1d thread, clustered resync window, and locks/waitqueues.

The mirror table has `raid_disks * 2` entries: primary mirrors in the first half and replacements in the second half. `raid1_info.rdev` can become `NULL` asynchronously, so normal request selection uses RCU plus `rdev->nr_pending`; configuration paths use `mddev->reconfig_mutex` or recovery context.

`device_lock` protects retry lists, pending write queues, degraded/In_sync consistency in several paths, and queued counters. `resync_lock`, `wait_barrier`, `array_frozen`, and per-bucket atomics coordinate normal I/O, sync I/O, quiesce, reshape, disk removal, and read repair. Memory barriers in `_wait_barrier()` and `raise_barrier()` enforce ordering between pending I/O counters and raised barriers.

Write serialization uses per-rdev interval trees indexed by barrier bucket. `wait_for_serialization()` allocates a `serial_info`, waits until no overlapping range exists, inserts it, and completion removes it with `remove_serial()`.

## Integration Points
Uses MD core APIs for write lifecycle, flushes, recovery scheduling, bitmap start/end, bad-block recording/clearing, rdev pending references, device failure, hotplug, sysfs links, integrity registration, queue limit stacking, clustered resync callbacks, and personality registration. Uses block-layer APIs for bio cloning/splitting/plug callbacks, synchronous page I/O, discard and nonrotational queue attributes, remap tracing, and I/O accounting.

## Notable Behaviors
- RAID1 can serve reads from any readable mirror, including a recovering mirror only below its `recovery_offset`.
- Read-only read errors retry another mirror without failing or repairing the original device.
- Write-mostly devices can use write-behind: the master bio can complete after non-write-mostly mirrors finish while copied data continues to write to write-mostly mirrors.
- Discards are replicated like writes, but discard completion errors are treated specially and unsupported component discard can be ignored when flushing pending writes.
- If only one active in-sync mirror remains and `fail_last_dev` is false, `raid1_error()` avoids failing the last working disk and disables recovery attempts from it instead.
- User-requested check/repair reads all readable mirrors, compares pages, updates `resync_mismatches`, and only writes devices that mismatch or failed read, except pure check avoids rewriting successful mismatches.
- Hot removal of an original device can promote an existing replacement into the primary slot, but only after freezing the array and verifying no pending I/O on the replacement.
- Takeover is limited to two-disk RAID5; the resulting config is returned frozen so MD core activation can unquiesce it correctly.

## Risks And Review Focus
- Barrier accounting is central to correctness. Incorrect `nr_pending`, `nr_waiting`, `nr_queued`, or `barrier` transitions can deadlock resync/quiesce or permit overlapping normal and recovery I/O.
- `raid1_info.rdev` lifetime relies on the documented RCU plus `nr_pending` protocol; any dereference outside those rules can race disk removal.
- Retry handling intentionally holds some rdev pending references across asynchronous worker retries; missing a matching `rdev_dec_pending()` can block removal forever.
- Write-behind returns success before all component writes finish, so bitmap accounting, copied payload lifetime, serialization, and later error handling must remain consistent.
- Bad-block handling has many branches: reads may shorten, writes may split, sync may mark all targets bad, and inability to persist bad blocks escalates to device failure or recovery abort.
- `raid1_reshape()` updates sysfs links while packing devices; mistakes can expose stale `rdN` links or inconsistent `raid_disk` values.
- Clustered resync checks and window updates add distributed coordination to local barrier logic; missed wakeups or stale windows can block writes longer than expected.
