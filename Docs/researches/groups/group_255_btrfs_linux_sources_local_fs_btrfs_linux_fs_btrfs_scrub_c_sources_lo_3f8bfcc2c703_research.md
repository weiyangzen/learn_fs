# Group Research: group_255_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_scrub_c_sources_lo_3f8bfcc2c703

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/scrub.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/scrub.c

## Purpose
Implements Btrfs scrub for a device: read allocated extents and superblocks, verify data checksums and metadata headers/checksums/generations, attempt repair from alternate mirrors, optionally write repaired data back, and drive device-replace copying. The implementation is stripe-oriented around `BTRFS_STRIPE_LEN`, with batched asynchronous reads and worker-based repair.

## Main Data Model
- `struct scrub_ctx`: per-scrub run state. Owns a fixed pool of `SCRUB_TOTAL_STRIPES` scrub stripes, extent/csum tree paths, cancellation state, throttling state, dev-replace target/write pointer state, progress stats, and refcounting for worker lifetime.
- `struct scrub_stripe`: represents one `BTRFS_STRIPE_LEN` logical range. Tracks folios holding read data, per-sector verification info, target device/physical/logical/mirror, pending I/O, repair wait state, packed bitmaps, write errors, data checksums, and worker item.
- `struct scrub_sector_verification`: stores either a data csum pointer or expected metadata generation.
- Packed bitmaps track `has_extent`, `is_metadata`, aggregate `error`, and specific `io_error`, `csum_error`, `meta_error`, `meta_gen_error`.

## Core Flow
1. `btrfs_scrub_dev()` validates state, allocates a `scrub_ctx`, starts/refs scrub workers, attaches the context to the device, optionally checks superblocks, then calls `scrub_enumerate_chunks()`.
2. `scrub_enumerate_chunks()` walks committed `DEV_EXTENT` items for the target device and requested physical range. For each block group, it freezes it, attempts to mark it read-only when required, coordinates dev-replace cursor state, and invokes `scrub_chunk()`.
3. `scrub_chunk()` finds the chunk map stripe matching the target device/physical extent and delegates to `scrub_stripe()`.
4. `scrub_stripe()` dispatches by profile:
   - simple mirrored profiles: `scrub_simple_mirror()`;
   - RAID0/RAID10: `scrub_simple_stripe()` over device stripes;
   - RAID5/6: data stripes plus parity verification/regeneration through RAID56 helpers.
5. `queue_scrub_stripe()` fills one stripe with extent and checksum metadata via `scrub_find_fill_first_stripe()`, batches reads in groups of `SCRUB_STRIPES_PER_GROUP`, and flushes when the context pool fills.
6. Initial read completion queues `scrub_stripe_read_repair_worker()`, which verifies sectors, retries failed sectors from alternate mirrors, optionally retries sector-by-sector, writes repaired sectors back when allowed, reports errors, and marks repair complete.
7. `flush_scrub_stripes()` waits for all queued repair workers. For dev-replace, it aborts on unrepaired metadata errors, then writes all verified good sectors to the replacement target.

## Verification
- Metadata verification checks tree block bytenr, filesystem UUID, chunk tree UUID, checksum over the full tree block, and expected generation.
- Data verification uses `btrfs_check_block_csum()` when a checksum exists. Nodatacsum sectors are treated as valid if I/O succeeded.
- Metadata blocks spanning stripe boundaries are warned about and skipped for full verification, noted as legacy layout handling.

## Repair And Writeback
- Repair reads only sectors currently marked bad.
- First retry phase reads large ranges from alternate mirrors; final fallback reads sector-by-sector across all copies, including the original mirror.
- Repaired sectors are written through `btrfs_submit_repair_write()`, targeting the affected mirror rather than normal multi-mirror writeback.
- Zoned filesystems avoid in-place repair; repaired zones are queued for relocation. Dev-replace on zoned devices serializes writes, zero-fills write pointer gaps, and synchronizes target write pointers.

## RAID56 Handling
- `get_raid56_logic_offset()` maps physical position to logical data/parity role.
- Data stripes are scrubbed into temporary scrub stripes with reporting suppressed.
- `scrub_raid56_parity_stripe()` verifies all data stripes in a full stripe first; if any allocated sector remains unrepaired, parity scrub aborts to avoid corrupting parity.
- `scrub_raid56_cached_parity()` uses RAID56 parity code to regenerate/check parity while caching recovered data folios to avoid rereads.

## Concurrency, Pause, Cancel
- Scrub workers are held by `scrub_workers_refcnt` and stored in `fs_info->scrub_workers`.
- Pause uses `scrub_pause_req`, `scrubs_paused`, `scrubs_running`, `scrub_lock`, and `scrub_pause_wait`; transaction commit can pause scrub safely.
- Cancellation checks global scrub cancel, per-context cancel, filesystem freezing, task freezing, and signals.
- Device-specific cancel increments `sctx->cancel_req` and waits for `dev->scrub_ctx` to clear.

## Progress And Errors
- `struct btrfs_scrub_progress` is updated under `stat_lock`: data/tree extents and bytes scrubbed, no-csum sectors, read/csum/verify errors, corrected and uncorrectable errors, super errors, malloc errors, and `last_physical`.
- Detailed warnings resolve extent owners: metadata tree backrefs are printed directly; data extents are mapped back to inode paths through backref walking.
- Device stats are updated for read errors, corruption errors, generation errors, and write errors.

## Public Entry Points Implemented
- `btrfs_scrub_dev()`: run scrub or dev-replace scrub for one device/range.
- `btrfs_scrub_pause()` / `btrfs_scrub_continue()`: pause/resume active scrub runs.
- `btrfs_scrub_cancel()`: cancel all active scrubs on the filesystem.
- `btrfs_scrub_cancel_dev()`: cancel the scrub attached to one device.
- `btrfs_scrub_progress()`: copy current progress for a device.

## Important Dependencies
Uses Btrfs extent/csum roots, chunk mapping, block-group freezing/RO state, dev-replace state, RAID56 parity helpers, zoned-device helpers, bio submission wrappers, backref path resolution, device stats, and scrub worker queues.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/scrub.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/scrub.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/scrub.h

## Purpose
Declares the Btrfs scrub public interface used by the rest of the filesystem. This header exposes only the scrub operations and keeps implementation details private to `scrub.c`.

## Contents
- Header guard: `BTRFS_SCRUB_H`.
- Includes `<linux/types.h>` for fixed-width integer and `bool`-related kernel types.
- Forward declarations:
  - `struct btrfs_fs_info`
  - `struct btrfs_device`
  - `struct btrfs_scrub_progress`

## Exported Functions
- `btrfs_scrub_dev(fs_info, devid, start, end, progress, readonly, is_dev_replace)`: starts scrub for a device physical range, optionally in readonly or dev-replace mode.
- `btrfs_scrub_pause(fs_info)`: blocks until active scrub workers reach pause points.
- `btrfs_scrub_continue(fs_info)`: releases a previous pause request.
- `btrfs_scrub_cancel(info)`: requests cancellation of active filesystem scrub runs.
- `btrfs_scrub_cancel_dev(dev)`: requests cancellation of the scrub tied to one device.
- `btrfs_scrub_progress(fs_info, devid, progress)`: reports current scrub progress for a device.

## Role In The Module Boundary
The header forms the control-plane API for scrub. Callers can start, pause, resume, cancel, and query scrub without depending on `scrub_ctx`, `scrub_stripe`, bitmap layout, worker logic, RAID handling, or repair internals.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/scrub.h -->