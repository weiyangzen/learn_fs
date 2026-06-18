# Group Research: group_712_linux_sources_os_linux_linux_fs_btrfs_scrub_c_sources_os_linux_linux_79e15ba96ac3

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/scrub.c -->
# File Research: sources/os/linux/linux/fs/btrfs/scrub.c

## Purpose
Implements Btrfs scrub for one device/range, including normal scrub and device-replace copy. It reads allocated extents and superblocks, verifies data checksums and metadata integrity, retries failed sectors from alternate mirrors, writes repaired sectors back when allowed, and handles RAID56 parity verification/regeneration.

## Main Data Model
- `struct scrub_ctx`: per-run state. Owns a fixed pool of `SCRUB_TOTAL_STRIPES` stripe objects, extent/csum tree paths, cancellation state, read-only/dev-replace flags, zoned write-pointer state, write target device, throttling counters, progress stats, and a refcount protecting worker wakeups from use-after-free.
- `struct scrub_stripe`: represents a `BTRFS_STRIPE_LEN` logical range. It stores folios for sector data, per-sector verification metadata, logical/physical/device/mirror identity, pending I/O counters, packed state bitmaps, write-error tracking, per-stripe checksums, and async repair work.
- `struct scrub_sector_verification`: stores either a data checksum pointer or the expected metadata generation for a tree block sector.
- Packed bitmap families track sectors with extents, metadata sectors, aggregate errors, I/O errors, checksum errors, metadata header/checksum errors, and metadata generation errors.

## Initialization And Lifetime
- `scrub_setup_ctx()` allocates the context with `kvzalloc`, initializes commit-root read-only paths for extent/csum lookup, allocates every stripe's folios, sector verification array, and checksum buffer, and records dev-replace target state.
- `release_scrub_stripe()`, `scrub_free_ctx()`, and `scrub_put_ctx()` tear down stripe allocations and context lifetime.
- `scrub_workers_get()` lazily creates the shared `btrfs-scrub` workqueue and refcounts it; `scrub_workers_put()` destroys it when the last scrub releases it.

## Verification
- `scrub_verify_one_metadata()` validates tree block bytenr, metadata UUID, chunk tree UUID, checksum over the whole tree block, and expected generation. It marks metadata or generation errors across the whole tree block.
- `scrub_verify_one_sector()` skips unused sectors and sectors already known to have I/O errors. Metadata sectors are verified as whole tree blocks; data sectors are checked with `btrfs_check_block_csum()` when a checksum exists. NODATACSUM data is accepted if the read succeeded.
- `scrub_verify_one_stripe()` walks a supplied sector bitmap and skips over the rest of a metadata tree block after checking its first sector.

## Read, Repair, And Writeback Flow
- Initial reads are submitted by `scrub_submit_initial_read()`. Normal chunks are read as whole stripe ranges, while stripe-tree update cases use `scrub_submit_extent_sector_read()` to read only extent sectors and split at RST mapping boundaries.
- `scrub_read_endio()` records read errors, releases the bio, and queues `scrub_stripe_read_repair_worker()` when all initial I/O for a stripe is done.
- `scrub_stripe_read_repair_worker()` waits for reads, verifies the stripe, saves the initial error bitmap, retries failed sectors from alternate mirrors using large repair reads, then retries sector-by-sector across all mirrors as a final fallback.
- Repaired sectors are written back via `scrub_write_sectors()` and `btrfs_submit_repair_write()` unless the scrub is read-only. Zoned filesystems avoid in-place repair and queue zone repair/relocation instead.
- `scrub_write_endio()` records write errors in a spinlock-protected bitmap and increments device write error stats.

## Reporting And Progress
- `scrub_stripe_report_errors()` converts initial/final error bitmaps into repaired and unrepaired counts, emits rate-limited messages, updates device stats, and updates `btrfs_scrub_progress`.
- Detailed warning paths use `scrub_print_common_warning()` and `scrub_print_warning_inode()` to resolve metadata tree backrefs or data extent inode paths through Btrfs backref walking.
- Progress tracks data/tree extents and bytes scrubbed, no-checksum sectors, read/checksum/verify errors, corrected and uncorrectable errors, malloc and superblock errors, and `last_physical`.

## Extent And Checksum Discovery
- `find_first_extent_item()` searches committed extent roots for the next extent item overlapping a scrub range, including extents that start before the current stripe.
- `scrub_find_fill_first_stripe()` finds the first populated stripe in a logical range, fills `has_extent` and metadata-generation state from extent items, counts data/metadata extents, and fetches data checksums from the appropriate csum root.
- `fill_one_extent_info()` marks per-sector coverage and metadata identity for the portion of an extent overlapping the stripe.

## Stripe Batching
- Scrub uses `SCRUB_STRIPES_PER_GROUP` and `SCRUB_GROUPS_PER_SCTX` to cap memory and in-flight work.
- `queue_scrub_stripe()` fills a stripe slot, submits every full group for initial read, and flushes the context when all slots are used.
- `flush_scrub_stripes()` submits any partial group, waits for all repair workers, performs device-replace writes of verified good sectors, updates `last_physical`, and resets stripes for reuse.

## RAID Profile Handling
- `scrub_stripe()` dispatches by chunk profile.
- SINGLE/DUP/RAID1/RAID1C profiles use `scrub_simple_mirror()`.
- RAID0/RAID10 use `scrub_simple_stripe()` to map the requested device stripe into repeated `BTRFS_STRIPE_LEN` simple mirror ranges.
- RAID5/6 use `get_raid56_logic_offset()` to distinguish data and parity strips. Data strips are scrubbed like single stripes; parity strips are handled by `scrub_raid56_parity_stripe()`.
- `scrub_raid56_parity_stripe()` reads and verifies all data stripes in a full stripe with normal reporting suppressed, aborts if allocated sectors remain unrepaired, builds an extent bitmap, and calls `scrub_raid56_cached_parity()` to check/regenerate P/Q through RAID56 parity helpers while caching recovered data folios.

## Device Replace And Zoned Behavior
- Device replace routes verified good sectors to `wr_tgtdev` after scrub verification and aborts on unrepaired metadata errors.
- For zoned targets, `fill_writer_pointer_gap()` zero-fills gaps before writes, `scrub_submit_write_bio()` serializes writes and advances the context write pointer only after successful completion, and `sync_write_pointer_for_zoned()` reconciles the target zone write pointer after a stripe.
- `finish_extent_writes_for_zoned()` waits for reservations, NOCOW writers, and ordered roots before committing, so device replace does not copy stale committed data over newer writes.

## Chunk Enumeration
- `scrub_enumerate_chunks()` walks committed `DEV_EXTENT` items for the device and requested physical range.
- It looks up and freezes the corresponding block group, skips removed or stale committed block groups, handles zoned device-replace `TO_COPY` filtering, marks block groups read-only when needed, coordinates scrub pause state to avoid transaction deadlocks, updates device-replace cursors, invokes `scrub_chunk()`, then unfreezes and releases the block group.
- Read-only setup is mandatory for device replace and RAID56 scrub; non-replace non-RAID56 scrub may continue after `-ENOSPC` when marking a block group read-only fails.

## Superblock Scrub
- `scrub_supers()` iterates valid superblock mirror locations for the device, bounds-checks them against committed device size, and calls `scrub_one_super()`.
- `scrub_one_super()` reads the superblock, verifies its checksum, generation, and structural validity.
- If normal scrub finds superblock errors and the scrub is writable, `btrfs_scrub_dev()` records that a transaction commit is needed after scrub finishes, so superblock rewrite can happen outside the active scrub pause context.

## Pause, Cancel, And Public Entry Points
- Pause/resume uses `scrub_pause_req`, `scrubs_paused`, `scrubs_running`, `scrub_lock`, and `scrub_pause_wait`; scrub periodically calls `scrub_blocked_if_needed()`.
- `should_cancel_scrub()` cancels on global/per-context scrub cancellation, filesystem freeze, task freeze, or pending signal.
- `btrfs_scrub_dev()` validates the target device, rejects incompatible concurrent replace/scrub states, installs `dev->scrub_ctx`, sets NOFS allocation context, scrubs superblocks and chunks, copies progress out, clears scrub state, and releases workers/context.
- `btrfs_scrub_pause()`, `btrfs_scrub_continue()`, `btrfs_scrub_cancel()`, `btrfs_scrub_cancel_dev()`, and `btrfs_scrub_progress()` implement the exported control API declared in `scrub.h`.

## Important Dependencies
Uses Btrfs chunk mapping, extent and csum roots, block-group freeze/read-only state, ordered/NOCOW write draining, device replace state, zoned helpers, RAID56 parity helpers, repair-write bio submission, backref path resolution, and device stat/progress accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/scrub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/scrub.h -->
# File Research: sources/os/linux/linux/fs/btrfs/scrub.h

## Purpose
Declares the public Btrfs scrub control API used by the rest of the filesystem.

## Interfaces
- `btrfs_scrub_dev()`: starts a scrub or device-replace scrub for a specific device id and physical range, optionally returning `btrfs_scrub_progress`.
- `btrfs_scrub_pause()` and `btrfs_scrub_continue()`: coordinate transaction-safe pausing and resuming of active scrub workers.
- `btrfs_scrub_cancel()`: cancels all active scrubs for a filesystem.
- `btrfs_scrub_cancel_dev()`: cancels the scrub associated with one device.
- `btrfs_scrub_progress()`: copies the current progress for a device or reports that no scrub is active.

## Dependencies
Forward-declares `struct btrfs_fs_info`, `struct btrfs_device`, and `struct btrfs_scrub_progress`, and includes `<linux/types.h>` for fixed-width integer and boolean types used in the prototypes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/scrub.h -->