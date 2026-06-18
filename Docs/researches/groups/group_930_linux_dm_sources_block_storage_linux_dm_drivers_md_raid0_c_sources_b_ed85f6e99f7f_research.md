# Group Research: group_930_linux_dm_sources_block_storage_linux_dm_drivers_md_raid0_c_sources_b_ed85f6e99f7f

Scope: `Docs/research_subset_a.md`; source tree `sources/block-storage/linux-dm`.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid0.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/raid0.c

## Purpose
Implements the Linux MD RAID0 personality: striped request mapping, uneven-device multi-zone layout construction, discard splitting, metadata-free array sizing/status, and takeover from selected redundant personalities.

## Main Interfaces
- Personality registration: `raid0_personality`, `raid0_init()`, `raid0_exit()`.
- Configuration/lifetime: `create_strip_zones()`, `raid0_run()`, `raid0_free()`, `free_conf()`, `dump_zones()`.
- Request mapping: `raid0_make_request()`, `raid0_handle_discard()`, `find_zone()`, `map_sector()`.
- Array properties: `raid0_size()`, `raid0_status()`, `raid0_quiesce()`.
- Takeover paths: `raid0_takeover()`, `raid0_takeover_raid45()`, `raid0_takeover_raid10()`, `raid0_takeover_raid1()`.

## Control Flow
`raid0_run()` validates that a chunk size exists and no bitmap is configured, initializes MD accounting biosets, builds or reuses `mddev->private`, configures queue limits around chunk-sized requests, stacks component queue limits, sets array sectors from rounded component sizes, dumps the zone map for debugging, and registers integrity metadata.

`create_strip_zones()` rounds each component size down to a chunk boundary, counts unique post-rounding sizes as strip zones, selects the RAID0 multi-zone layout, validates slot coverage, allocates `strip_zone[]` and the flattened per-zone `devlist`, then builds zone boundaries. Zone 0 contains all devices up to the smallest device size; later zones contain only devices that extend beyond the previous zone's device offset.

`raid0_make_request()` handles flushes through the MD core, routes discards to RAID0-specific discard expansion, splits normal bios at chunk boundaries, accounts non-md bios, locates the logical strip zone, maps the sector using either original or alternate multi-zone semantics, checks for a broken target, remaps the bio to the component device plus `data_offset`, applies write-same/write-zeroes validation, and submits it.

`raid0_handle_discard()` first splits a discard that crosses a strip zone. It then converts the logical range into per-disk ranges for each device participating in the zone and calls `md_submit_discard_bio()` for each non-empty component span before completing the original bio.

Takeover helpers validate source-specific preconditions, rewrite `mddev` level/layout/chunk/disk-count fields, force a clean recovery checkpoint, clear unsupported RAID0 flags, and create a new RAID0 strip-zone configuration.

## State And Synchronization
`mddev->private` points to `struct r0conf`, which owns `strip_zone[]`, `devlist`, zone count, and selected layout. RAID0 has no private thread and `raid0_quiesce()` is empty; normal suspension and lifecycle coordination is handled by the MD core. Request-side state is read without additional RAID0-local locking, so configuration must be stable while the personality is active.

## Integration Points
Depends on MD core APIs for personality registration, bitmap rejection, accounting biosets, flush handling, write-same/write-zeroes checks, broken-device detection, queue/integrity setup, and capacity updates. Uses Linux block APIs for bio splitting/chaining, remap tracing, discard capability checks, and queue limit stacking. Includes `raid5.h` for RAID4/5 layout constants used by takeover validation.

## Notable Behaviors
- Multi-zone RAID0 assembly requires an explicit layout when component sizes differ; otherwise it refuses assembly and asks for `raid0.default_layout` 1 or 2.
- The original and alternate layouts differ only for multi-zone arrays; single-zone arrays force `RAID0_ORIG_LAYOUT`.
- `raid0_size()` sums each component size rounded down to a chunk multiple and warns if called as a generic reshape size function.
- Queue discard is enabled if any member supports discard, while per-target discard behavior is delegated to `md_submit_discard_bio()`.
- Takeover from RAID1 collapses to one active disk and chooses the largest chunk size up to 64 KiB that evenly divides the array and is at least `PAGE_SIZE`.

## Risks And Review Focus
- Multi-zone layout selection is compatibility-sensitive because Linux 3.14 changed mapping behavior for uneven RAID0 arrays; wrong layout selection silently changes data placement.
- `create_strip_zones()` mutates `rdev->sectors` by rounding down to chunk size, so callers must not expect the original component sector count afterwards.
- Normal I/O is split only at chunk boundaries before zone mapping; zone-boundary correctness depends on the relationship between chunk-aligned zone construction and `find_zone()`.
- Discard mapping fans out one logical discard into per-disk discards and manually adjusts zone-relative offsets; off-by-one errors here would discard wrong component sectors.
- Takeover paths alter live `mddev` geometry and unsupported flags before returning the private config, so failed or partial takeover paths require careful MD-core cleanup.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid0.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid0.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/raid0.h

## Purpose
Defines private RAID0 layout structures and the two supported multi-zone layout identifiers used by `raid0.c`.

## Main Interfaces
- `struct strip_zone`: logical end sector, component zone start sector, and number of devices in the zone.
- `enum r0layout`: `RAID0_ORIG_LAYOUT` and `RAID0_ALT_MULTIZONE_LAYOUT`.
- `struct r0conf`: zone array, flattened zone/device pointer table, zone count, and active layout.

## Control Flow
No executable control flow. The declarations support RAID0 zone construction and request mapping.

## State And Synchronization
`r0conf` is the personality-private state stored in `mddev->private`. It has no RCU head or internal lock; active configurations are expected to remain stable for the personality lifetime.

## Integration Points
Included by `raid0.c`; uses MD-local `struct md_rdev` pointers through the flattened `devlist`.

## Notable Behaviors
- The header documents the Linux 3.14 multi-zone layout compatibility issue and gives both layout modes stable numeric values.
- `devlist` is indexed as `zone_index * raid_disks + disk_index`, with only the first `strip_zone[zone].nb_dev` entries meaningful for each zone.

## Risks And Review Focus
- Structure changes must preserve the mapping assumptions in `map_sector()`, `dump_zones()`, and `raid0_handle_discard()`.
- The layout enum values are persisted/used as externally selected compatibility choices, so renumbering would be unsafe.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid0.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid1-10.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/raid1-10.c

## Purpose
Provides small shared definitions and helper routines used by RAID1 and RAID10 implementations for resync/recovery bio allocation and special bio markers.

## Main Interfaces
- Resync sizing/constants: `RESYNC_BLOCK_SIZE`, `RESYNC_PAGES`, `NR_RAID_BIOS`.
- Special bio sentinels: `IO_BLOCKED`, `IO_MADE_GOOD`, `BIO_SPECIAL()`.
- Resync page container: `struct resync_pages`.
- Helpers: `rbio_pool_free()`, `resync_alloc_pages()`, `resync_free_pages()`, `resync_get_all_pages()`, `resync_fetch_page()`, `get_resync_pages()`, `md_bio_reset_resync_pages()`.

## Control Flow
`resync_alloc_pages()` allocates the fixed number of pages required for one resync block and unwinds partial allocation on failure. `resync_free_pages()` drops page references, while `resync_get_all_pages()` increments references when multiple bios share the same underlying resync pages. `md_bio_reset_resync_pages()` rebuilds a bio's vector table from the stored pages after `bio_reset()`.

## State And Synchronization
`struct resync_pages` stores the owning raid bio pointer and an array of pages. The helpers do not provide locking; ownership and completion ordering are handled by the including RAID personality.

## Integration Points
Textually included by `raid1.c` here. It is written as shared implementation rather than a separately compiled object, so constants and static helpers become part of the including file.

## Notable Behaviors
- `IO_BLOCKED` and `IO_MADE_GOOD` are encoded as low pointer values and guarded by `BIO_SPECIAL()` before normal bio reference handling.
- User-requested check/repair in RAID1 may allocate distinct page sets per mirror; normal resync can share page references among component bios.

## Risks And Review Focus
- Any code walking `r1bio->bios[]` or equivalent arrays must check `BIO_SPECIAL()` before `bio_put()` or dereferencing.
- `md_bio_reset_resync_pages()` assumes the bio has enough vector capacity for `RESYNC_PAGES`.
- Shared page references require balanced `get_page()` and `put_page()` across all mirrors; mismatches leak or prematurely free resync pages.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid1-10.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid1.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid1.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid1.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/raid1.h

## Purpose
Defines private RAID1 data structures, barrier bucket constants, per-mirror state, per-array configuration, per-I/O `r1bio` state, and the sector-to-barrier-bucket hash helper.

## Main Interfaces
- Barrier sizing: `BARRIER_UNIT_SECTOR_BITS`, `BARRIER_UNIT_SECTOR_SIZE`, `BARRIER_BUCKETS_NR_BITS`, `BARRIER_BUCKETS_NR`.
- Per mirror: `struct raid1_info`.
- Mempool metadata: `struct pool_info`.
- Per array: `struct r1conf`.
- Per logical I/O: `struct r1bio`.
- State bits: `enum r1bio_state`.
- Helper: `sector_to_idx()`.

## Control Flow
Only `sector_to_idx()` has executable logic; it hashes a sector shifted by the 64 MiB barrier unit size into the fixed number of barrier buckets. All other content is structure and flag definition.

## State And Synchronization
The header documents the safe access rules for `raid1_info.rdev`: hold `mddev->reconfig_mutex`, operate during known resync/recovery context, or use RCU and increment `rdev->nr_pending` before dropping the RCU lock. `r1conf` includes `device_lock`, `resync_lock`, `wait_barrier`, per-bucket atomic arrays, retry lists, pending bio queues, mempools, split bioset, and clustered resync bounds.

## Integration Points
Included by `raid1.c` and dependent on MD core types (`mddev`, `md_rdev`, `md_thread`), block types (`bio`, `bio_set`), kernel synchronization primitives, mempools, pages, atomics, waitqueues, and linked lists.

## Notable Behaviors
- The mirror table is sized for primaries plus replacements; comments explain that `pool_info.raid_disks` is twice the configured RAID1 disk count for the same reason.
- Barrier bucket arrays are sized so each atomic array occupies one page.
- `struct r1bio` ends with a flexible `bios[]` array; comments explicitly prohibit adding fields after it.
- `R1BIO_BehindIO`, `R1BIO_Returned`, `R1BIO_MadeGood`, `R1BIO_WriteError`, and `R1BIO_FailFast` encode important completion and error policy decisions used by `raid1.c`.

## Risks And Review Focus
- Any change to barrier constants affects both normal I/O splitting and sync exclusion granularity.
- Misusing `sector_to_idx()` with a range that crosses a barrier unit can mix accounting for unrelated buckets; `raid1_make_request()` avoids this by splitting at unit boundaries.
- Adding fields after `r1bio->bios[]` would corrupt the contiguous allocation pattern used by the mempool allocator.
- The asynchronous `rdev` access rules are easy to violate and are central to safe hot-remove behavior.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid1.h -->