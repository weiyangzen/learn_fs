# Group Research: group_954_linux_stable_sources_os_linux_linux_stable_fs_btrfs_scrub_c_sources__fc9fa2fb3c84

Scope: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/scrub.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/scrub.c

## Purpose

This file implements Btrfs scrub for a device: reading allocated extents, validating data checksums, validating metadata block headers/checksums/generations, repairing bad sectors from alternate mirrors, checking superblocks, and supporting device replace copy-out. It is the main scrub engine behind the exported APIs declared in `scrub.h`.

Scrub operates in `BTRFS_STRIPE_LEN` units, batches multiple stripes, and uses Btrfs logical addressing plus mirror-aware bio submission instead of directly issuing physical reads for most normal extent checks.

## Core Data Structures

- `struct scrub_sector_verification`: per-sector expected verification data. For data sectors it stores a checksum pointer; for metadata sectors it stores the expected tree block generation.
- `struct scrub_stripe`: represents one contiguous `BTRFS_STRIPE_LEN` logical range. It owns folios for IO, per-sector verification records, packed state bitmaps, physical/logical/mirror identity, writeback error state, checksum storage, wait queues, pending IO count, and async work.
- `struct scrub_ctx`: per-scrub run context. It owns the fixed stripe pool, optional RAID56 temporary data stripes, extent/csum paths, pause/cancel state, throttling state, device-replace write target state, write serialization, progress counters, and a refcount.
- Packed bitmaps track `has_extent`, `is_metadata`, aggregate `error`, `io_error`, `csum_error`, `meta_error`, and `meta_gen_error`. The file generates helpers with `IMPLEMENT_SCRUB_BITMAP_OPS`.

## Initialization And Lifetime

`scrub_setup_ctx()` allocates a large `scrub_ctx` with `kvzalloc`, initializes `SCRUB_TOTAL_STRIPES` inline stripes, prepares commit-root extent/csum search paths, initializes stats/locks, and records the dev-replace target when applicable. `init_scrub_stripe()` allocates folios, per-sector verification records, and checksum buffers sized to the filesystem sector and checksum sizes.

`scrub_put_ctx()` and `scrub_free_ctx()` release stripe folios, checksum buffers, sector arrays, optional context memory, and use a refcount to avoid freeing the context while worker completion paths can still wake wait queues.

## Verification Logic

`scrub_verify_one_sector()` skips unused sectors and sectors with IO errors, then dispatches metadata versus data verification.

For metadata, `scrub_verify_one_metadata()` validates:
- tree block bytenr matches the expected logical address;
- FSID matches `metadata_uuid`;
- chunk tree UUID matches the mounted filesystem;
- metadata checksum over the full tree block;
- tree block generation matches the generation from the extent item.

For data, the sector is considered valid if it has no checksum, otherwise `btrfs_check_block_csum()` compares disk data against the checksum loaded from the checksum tree. Failures set checksum and aggregate error bits.

## Read, Repair, And Writeback Flow

Initial reads are submitted by `scrub_submit_initial_read()`. For normal mappings it reads the whole stripe range within the chunk boundary; for RAID stripe tree update cases it uses `scrub_submit_extent_sector_read()` to split reads on mapped boundaries and handle preallocated extents that lack stripe-tree entries.

`scrub_read_endio()` records IO errors, drops the bio, and queues `scrub_stripe_read_repair_worker()` after the stripe’s initial reads complete.

The repair worker:
1. waits for initial IO;
2. verifies all extent-covered sectors;
3. records the initial error bitmap and error counters;
4. tries all alternate mirrors with large repair reads;
5. if errors remain, retries all mirrors sector by sector;
6. writes back sectors that were initially bad but later verified good, unless readonly;
7. for zoned filesystems, queues zone repair instead of in-place repair;
8. updates scrub stats and wakes the stripe repair wait queue.

`scrub_write_sectors()` builds contiguous repair/dev-replace write bios for selected sectors. `scrub_submit_write_bio()` uses `btrfs_submit_repair_write()` so writes target the selected mirror or dev-replace destination. Zoned writeback is serialized and updates the context write pointer.

## Error Reporting And Statistics

`scrub_stripe_report_errors()` converts initial and final bitmaps into repair reports, uncorrectable reports, device stat increments, and `btrfs_scrub_progress` counters. It reports fixed sectors separately from unrepaired sectors.

Detailed warning paths use:
- `scrub_print_common_warning()` to distinguish superblock, metadata, and data extent errors;
- extent-tree lookup plus backref walking to locate affected metadata trees or file paths;
- `scrub_print_warning_inode()` to resolve inode paths and include root/inode/offset/link information.

Counters updated include scrubbed data/tree extents and bytes, no-checksum sectors, read/checksum/verify/uncorrectable/corrected errors, super errors, and last physical progress.

## Stripe Batching

The context owns `SCRUB_GROUPS_PER_SCTX * SCRUB_STRIPES_PER_GROUP` stripes. `queue_scrub_stripe()` fills the next stripe from extent and checksum trees via `scrub_find_fill_first_stripe()`, submits each full group, and flushes all stripes when the pool is full.

`flush_scrub_stripes()` submits any partial group, waits for repair completion, performs dev-replace writes for all good extent sectors, waits for writeback, advances `last_physical`, resets stripes, and returns the first relevant error.

## Extent And Checksum Discovery

`find_first_extent_item()` searches the commit-root extent tree for the first extent overlapping a logical range, including extents that begin before the requested stripe. `get_extent_info()` extracts start, size, flags, and generation.

`scrub_find_fill_first_stripe()` resets a stripe, finds allocated extents, rounds to the containing scrub stripe, fills per-sector extent metadata, counts data/metadata extents, and loads data checksums from the commit-root checksum tree with `btrfs_lookup_csums_bitmap()`.

This design means scrub verifies committed extents and avoids racing directly with in-flight COW metadata changes.

## RAID Profile Handling

Simple mirror profiles (`SINGLE`, `DUP`, `RAID1`, `RAID1C*`) are handled by `scrub_simple_mirror()` over the block group range.

Striped simple profiles (`RAID0`, `RAID10`) use `scrub_simple_stripe()` to derive the logical range, mirror number, and physical progression for the selected device stripe, then reuse the mirror scrub path.

RAID56 has custom handling:
- `get_raid56_logic_offset()` maps physical stripes to logical data/parity positions.
- Data stripes can be scrubbed through the simple mirror path.
- Parity stripes use `scrub_raid56_parity_stripe()`, which first reads/verifies all data stripes in the full stripe into temporary scrub stripes, aborts if unrepaired data sectors remain, then calls `scrub_raid56_cached_parity()`.
- `scrub_raid56_cached_parity()` constructs a parity scrub rbio and supplies verified data folios as cache so parity can be checked/regenerated safely.

RAID56 scrub requires block groups to be readonly during key operations to avoid RMW races with cached data.

## Chunk Enumeration And Block Group Coordination

`scrub_enumerate_chunks()` walks the device tree’s `BTRFS_DEV_EXTENT_KEY` items for the target device and requested physical range. For each matching device extent it locates the block group, validates it against committed state, freezes it, attempts to mark it readonly, and then calls `scrub_chunk()`.

Important coordination behavior:
- Uses commit roots for device extents, extent items, and checksums.
- Skips removed or stale block groups whose logical addresses have been reused.
- Pauses scrub around block-group readonly transitions to avoid transaction commit deadlocks.
- Handles active swapfile refusal (`-ETXTBSY`) by skipping with a warning.
- For dev-replace, readonly block-group state is required because scrub copies committed data while regular writes are duplicated through the write path.
- For zoned dev-replace, only block groups flagged `BLOCK_GROUP_FLAG_TO_COPY` are copied, and ordered/nocow writes are drained before copying.

After scrub, it restores block-group state, returns unused empty groups to cleanup/discard paths, updates dev-replace cursors, and stops on write errors or allocation errors.

## Superblock Scrub

`scrub_supers()` reads each valid superblock mirror on the target device with `scrub_one_super()`. It validates checksum, expected generation, and full superblock structure. Superblock errors increment `super_errors`; if non-readonly scrub detects super errors, `btrfs_scrub_dev()` commits a transaction after scrub completes to attempt superblock repair through normal transaction commit paths.

Seed devices use their own generation; normal devices use the last committed transaction generation.

## Pause, Cancel, Progress, And Workers

`scrub_workers_get()` lazily creates a shared `btrfs-scrub` workqueue with `WQ_FREEZABLE | WQ_UNBOUND`, reference counted in `fs_info`. `scrub_workers_put()` destroys it when the last user exits.

Pause and cancellation are cooperative:
- `btrfs_scrub_pause()` increments `scrub_pause_req` and waits until running scrubs report paused.
- `btrfs_scrub_continue()` decrements pause request and wakes waiters.
- `should_cancel_scrub()` aborts on global cancel, per-device cancel, filesystem freeze, task freezing, or pending signal.
- `btrfs_scrub_cancel()` cancels all scrub activity on the filesystem.
- `btrfs_scrub_cancel_dev()` cancels one device’s active scrub context.
- `btrfs_scrub_progress()` copies current stats if a scrub context exists for the device.

## Public Entry Point

`btrfs_scrub_dev()` is the main exported entry point. It validates device availability and writable state, rejects concurrent scrub/dev-replace conflicts, installs `dev->scrub_ctx`, handles pause accounting, enters `GFP_NOFS` allocation context, optionally scrubs superblocks, enumerates chunks, copies final progress, tears down the workqueue/context references, clears `dev->scrub_ctx`, and optionally commits a transaction for superblock repair.

Return values distinguish missing device, readonly/writeability failures, concurrent operation, cancellation/interruption, IO/corruption errors, and allocation failures.

## Notable Design Constraints

- Scrub is commit-root based for stable extent/checksum/device metadata views.
- Repair is mirror-driven and escalates from broad alternate-mirror reads to sector-sized retries.
- Metadata errors are treated more conservatively during dev-replace; unrepaired metadata aborts copying.
- Zoned device support requires write pointer synchronization, zeroout of gaps, serialized writes, and sometimes relocation instead of in-place repair.
- RAID56 parity scrub depends on verified data stripe cache and aborts before parity repair if data remains corrupt.
- IO throttling is per device via `scrub_speed_max`, enforced in submission batches.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/scrub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/scrub.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/scrub.h

## Purpose

This header declares the public Btrfs scrub control API used by the rest of the filesystem. It intentionally exposes only high-level scrub operations and forward-declares the involved Btrfs types.

## Exposed Types

The header forward-declares:
- `struct btrfs_fs_info`
- `struct btrfs_device`
- `struct btrfs_scrub_progress`

It includes `<linux/types.h>` for fixed-width integer and boolean type availability.

## Exported Functions

- `btrfs_scrub_dev(...)`: starts scrub or device-replace scrub for a device ID over a physical range, optionally returns progress, and supports readonly mode.
- `btrfs_scrub_pause(...)`: requests all running scrubs on the filesystem to pause.
- `btrfs_scrub_continue(...)`: releases a previous pause request.
- `btrfs_scrub_cancel(...)`: cancels currently running scrub work for the filesystem.
- `btrfs_scrub_cancel_dev(...)`: cancels scrub for one device.
- `btrfs_scrub_progress(...)`: reads the current progress counters for a device scrub.

## Design Role

`scrub.h` is a narrow subsystem boundary. All scrub internals, including stripe structures, bitmap state, repair workers, RAID56 parity logic, block-group coordination, and superblock validation, remain private to `scrub.c`. The rest of Btrfs interacts with scrub through these lifecycle/progress functions only.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/scrub.h -->