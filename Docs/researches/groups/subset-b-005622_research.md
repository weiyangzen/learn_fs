# subset-b-005622 Research

Grouped source research for the Btrfs scrub implementation and its exported scrub interface. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/scrub.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/scrub.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/scrub.c` implements Btrfs device scrub and the scrub-backed device-replace copy path. It walks committed device extents, freezes and optionally marks block groups read-only, reads allocated sectors from the selected device or mirror, verifies data checksums and metadata headers, attempts repair from alternate mirrors, writes repaired sectors when allowed, validates superblock mirrors, updates scrub progress/statistics, and coordinates pause/cancel/progress operations exposed through `scrub.h`. The source was read as a complete 3330-line file for this report.

## Important APIs, Types, and Functions

Core state is carried by `struct scrub_ctx`, which owns the fixed array of in-flight `struct scrub_stripe` objects, extent and checksum search paths, cancel/read-only/device-replace state, zoned write-pointer state, write target device, progress counters, and a refcount protecting asynchronous work completion. `struct scrub_stripe` represents one `BTRFS_STRIPE_LEN` logical range and stores folios, per-sector checksum or metadata-generation expectations, device/logical/physical/mirror identity, bitmaps for extent/metadata/error states, write-error tracking, and the repair work item. `struct scrub_sector_verification`, `struct scrub_warning`, and `struct scrub_error_records` hold verification metadata and reporting snapshots.

The public entry points are `btrfs_scrub_dev`, `btrfs_scrub_pause`, `btrfs_scrub_continue`, `btrfs_scrub_cancel`, `btrfs_scrub_cancel_dev`, and `btrfs_scrub_progress`. Internal setup and lifetime helpers include `scrub_setup_ctx`, `init_scrub_stripe`, `release_scrub_stripe`, `scrub_workers_get`, `scrub_workers_put`, and `scrub_put_ctx`. Verification and repair flow centers on `scrub_find_fill_first_stripe`, `scrub_submit_initial_read`, `scrub_read_endio`, `scrub_stripe_read_repair_worker`, `scrub_verify_one_sector`, `scrub_verify_one_metadata`, `scrub_stripe_submit_repair_read`, `scrub_write_sectors`, and `scrub_stripe_report_errors`.

Chunk/profile traversal is split across `scrub_enumerate_chunks`, `scrub_chunk`, `scrub_stripe`, `scrub_simple_mirror`, `scrub_simple_stripe`, and RAID56-specific helpers `get_raid56_logic_offset`, `scrub_raid56_parity_stripe`, and `scrub_raid56_cached_parity`. Zoned and device-replace support is handled by `fill_writer_pointer_gap`, `sync_write_pointer_for_zoned`, and `finish_extent_writes_for_zoned`. Superblock checking uses `scrub_supers` and `scrub_one_super`.

## Control Flow

`btrfs_scrub_dev` is the main orchestration entry point. It rejects closing filesystems, allocates a scrub context, obtains the shared scrub workqueue, finds and validates the target device under the device-list and scrub locks, rejects concurrent scrub or device replace conflicts, installs `dev->scrub_ctx`, honors any current pause request, increments `scrubs_running`, and switches allocations to `GFP_NOFS` for the active scrub. Normal scrub first checks superblock mirrors, then calls `scrub_enumerate_chunks`; device replace skips superblock repair and uses the same chunk path as a copy-and-verify engine.

`scrub_enumerate_chunks` searches the committed device tree for `BTRFS_DEV_EXTENT_KEY` items in the requested physical range. For each matching device extent it looks up the logical block group, skips stale or removed mappings, freezes the block group, pauses scrub while making block-group read-only transitions, applies stricter read-only requirements for device replace and RAID56, waits for nocow and ordered writes where needed, updates device-replace cursors, invokes `scrub_chunk`, then restores block-group state and cleanup/discard eligibility. The use of commit-root paths means scrub verifies a stable committed view while live writes either go through COW or are coordinated by RO/nocow waits for replace.

`scrub_chunk` maps the block group and selects stripes on the target device. `scrub_stripe` dispatches by profile: simple mirrored profiles call `scrub_simple_mirror` over the full block group, RAID0/RAID10 call `scrub_simple_stripe` for each data stripe that belongs to the device, and RAID56 iterates physical stripes, scrubbing data stripes directly and parity stripes through a parity-regeneration path. The simple path repeatedly calls `queue_scrub_stripe`, which fills the next available `struct scrub_stripe` from extent and checksum trees and submits groups of eight stripes; `flush_scrub_stripes` waits for repair workers, performs device-replace writes of verified good sectors, updates `last_physical`, and resets stripe slots.

Per-stripe IO starts with `scrub_submit_initial_read`. For normal mappings it reads the full stripe range within the chunk boundary; for stripe-tree update cases it reads only extent-covered sectors and splits according to RAID stripe tree mapping boundaries. `scrub_read_endio` records IO errors by sector and queues `scrub_stripe_read_repair_worker` after the last initial read bio completes. The worker verifies checksums or metadata headers, snapshots initial errors, tries alternate mirrors first with large reads, then retries all mirrors sector-by-sector as a final safety net, writes back repaired sectors when not read-only and not zoned, queues zoned block-group repair instead of in-place repair, reports statistics and warnings, and wakes any waiter through `repair_wait`.

RAID56 parity scrub is deliberately two-phase. `scrub_raid56_parity_stripe` builds temporary data stripes for all data members of a full stripe, reads and repairs them without normal reporting, aborts if any extent-covered data sector remains bad, builds an extent bitmap, and calls `scrub_raid56_cached_parity` so the RAID56 layer can check/regenerate P/Q using the recovered data folios as cache. This avoids trusting parity when data is still known corrupt.

Pause and cancellation are polled at chunk/stripe boundaries. `should_cancel_scrub` returns `-ECANCELED` for explicit global or device cancel requests and `-EINTR` for filesystem freeze, process freeze, or pending signal. `btrfs_scrub_pause` increments a pause request and waits until all running scrubs report paused; `btrfs_scrub_continue` drops the request and wakes waiters. Cancellation APIs set the relevant atomic flag and wait for `scrubs_running` or `dev->scrub_ctx` to clear.

## State and Persistence Behavior

Scrub persists progress and results only through in-memory kernel state and Btrfs device stats. `struct btrfs_scrub_progress` in `sctx->stat` accumulates bytes/extents scrubbed, no-csum sectors, read/checksum/verification/super/malloc errors, corrected and uncorrectable errors, and `last_physical`; callers can receive a final copy from `btrfs_scrub_dev` or a live copy through `btrfs_scrub_progress`. Device error counters are incremented for read, write, corruption, and generation errors via Btrfs device-stat helpers.

The operation intentionally uses commit-root extent/checksum/device-tree paths, so it verifies a stable committed filesystem image rather than racing arbitrary live tree mutations. Block group references, freeze state, RO state, device-replace cursor fields, and scrub pause counters are the main coordination state. For superblock errors found during read-write scrub, `btrfs_scrub_dev` defers the forced transaction commit until after scrub exits, because committing while the current scrub is running would deadlock against scrub pause.

No standalone on-disk scrub ledger is created by this file. Device replace does persist progress through `fs_info->dev_replace.cursor_left`, `cursor_right`, and `item_needs_writeback`, while actual target-device data is written through scrub writeback and normal write duplication. Zoned replace additionally tracks and synchronizes `sctx->write_pointer`, zero-fills gaps before sequential writes, clears zone-empty state, and commits/waits for writes before copying block groups.

## Dependencies and Integration Points

This file is tightly integrated with Btrfs core subsystems: extent and checksum trees (`ctree.h`, `file-item.h`, `extent_io.h`), device/chunk mapping (`volumes.h`, `raid-stripe-tree.h`), bio submission (`disk-io.h`, Btrfs bio helpers), block-group lifecycle (`block-group.h`), transactions and ordered data (`transaction.h`, `ordered-data.h`), backref resolution for warnings (`backref.h`), device replace (`dev-replace.h`), RAID56 parity (`raid56.h`), discard cleanup (`discard.h`), zoned mode (`zoned.h`), and filesystem-wide scrub counters/locks in `struct btrfs_fs_info`.

Important external contracts include `btrfs_map_block`, `btrfs_submit_bbio`, `btrfs_submit_repair_write`, `btrfs_lookup_csums_bitmap`, `btrfs_inc_block_group_ro`, `btrfs_freeze_block_group`, `btrfs_bio_counter_inc_blocked`, RAID56 rbio helpers, superblock validation helpers, and sysfs/ioctl-facing callers that use the declarations in `scrub.h`. The workqueue named `btrfs-scrub` is shared through `fs_info->scrub_workers_refcnt` and must be freezable so scrub does not block suspend/hibernate semantics.

## Risks and Edge Cases

Repair correctness depends on precise bitmap accounting. `has_extent`, `is_metadata`, `io_error`, `csum_error`, `meta_error`, and `meta_gen_error` are packed into one bitmap array sized by runtime sector count; off-by-one errors or wrong sector counts would misreport errors or write repaired data to the wrong sectors. Metadata verification also assumes tree blocks usually fit within one `BTRFS_STRIPE_LEN`; old filesystems with cross-stripe tree blocks are warned but cannot be fully verified in that path.

Concurrency risks are high around block-group RO transitions, transaction commits, scrub pause, and device replace. The code contains explicit deadlock avoidance for `btrfs_inc_block_group_ro` versus transaction pause, `GFP_NOFS` allocation during scrub, and deferred superblock-fix commits. Device replace adds corruption risk if nocow writes race scrub copy, which is why block groups must be RO or the replace path stops.

Profile-specific behavior is another risk area. RAID56 parity scrub must not regenerate parity when data repair failed. RAID0/RAID10 logical/physical stepping depends on `sub_stripes` and stripe-index mirror numbers. RAID stripe tree mapping can return `-ENODATA` for preallocated extents, which this path intentionally does not count as an error. Zoned filesystems cannot use normal in-place repair and rely on zone relocation or sequential write-pointer synchronization.

Operational edge cases include missing devices, read-only devices, target replace devices, active swapfile block groups (`-ETXTBSY` skip), removed block groups visible through commit roots, device extents whose logical address has been reused by a newer block group, filesystem closing, freeze/signal cancellation, and allocation failures in the large scrub context or RAID56 temporary stripes.

## Test Signals

Useful tests should cover clean scrub, read-only scrub, writable repair, device replace, and cancellation/progress on devices with SINGLE, DUP, RAID1/1C, RAID0, RAID10, and RAID56 profiles. Fault-injection should force initial read errors, checksum mismatches, metadata bytenr/fsid/chunk-uuid/checksum/generation failures, alternate mirror success, all-mirror failure, writeback failure, and superblock checksum/generation errors while checking progress counters and device stats.

Race-oriented tests should exercise scrub while transactions commit, while filesystem freeze or process signals interrupt scrub, while block groups are removed or marked unused, while active swapfiles cause `-ETXTBSY`, and while device replace copies over nocow/write-heavy workloads. Zoned tests should check sequential target gaps, write-pointer sync, zone-empty clearing, and relocation instead of in-place repair. RAID56 tests should include data-stripe repair before parity regeneration and unrepaired data aborting parity scrub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/scrub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/scrub.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/scrub.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/scrub.h` declares the Btrfs scrub interface used by the rest of the filesystem. It is the public local header for starting a device scrub or device-replace scrub, pausing/resuming active scrubs around transactions, canceling all or one-device scrub work, and querying live scrub progress. The source was read as a complete 22-line file for this report.

## Important APIs, Types, and Functions

The header forward-declares `struct btrfs_fs_info`, `struct btrfs_device`, and `struct btrfs_scrub_progress` so users do not need the full scrub implementation internals. `btrfs_scrub_dev(fs_info, devid, start, end, progress, readonly, is_dev_replace)` starts the actual scan/copy operation for a device physical range. `btrfs_scrub_pause(fs_info)` and `btrfs_scrub_continue(fs_info)` provide filesystem-wide pause coordination. `btrfs_scrub_cancel(fs_info)` cancels all active scrub work on the filesystem, while `btrfs_scrub_cancel_dev(dev)` cancels the scrub attached to one device. `btrfs_scrub_progress(fs_info, devid, progress)` returns live progress for a device if one is currently being scrubbed.

## Control Flow

Callers include ioctl/sysfs/device-replace paths rather than this header itself. A normal run calls `btrfs_scrub_dev`, which resolves the target device, installs a scrub context on `dev->scrub_ctx`, validates superblocks, enumerates device extents, and returns a final `btrfs_scrub_progress` copy if requested. Transaction or freeze-sensitive paths call `btrfs_scrub_pause` before work that needs scrub quiescence and `btrfs_scrub_continue` afterward. Cancel paths set the filesystem-wide or device-local cancel flag and block until the running scrub clears.

## State and Persistence Behavior

This header owns no storage and defines no persistent data. Its declarations expose functions that operate on state stored in `struct btrfs_fs_info`, `struct btrfs_device`, and `struct btrfs_scrub_progress`: pause/cancel atomics and wait queues, the per-device `scrub_ctx` pointer, device-replace state, and progress counters. The only caller-visible persisted output is the copied progress structure and the return code from each operation.

## Dependencies and Integration Points

The only direct include is `<linux/types.h>` for `u64` and `bool`-compatible kernel types used in prototypes. The declarations integrate `scrub.c` with Btrfs ioctl handling, transaction pause coordination, filesystem freeze behavior, device replace, and progress reporting. Because the implementation is intentionally hidden, callers should treat `struct btrfs_scrub_progress` as the stable progress contract and avoid depending on `struct scrub_ctx`.

## Risks and Edge Cases

The main contract risk is semantic rather than syntactic: callers must pass a valid device id/range, choose `readonly` consistently with filesystem/device writability, and set `is_dev_replace` only for the device-replace path because it changes writeback and missing-device handling. Pause and cancel functions can wait; they must not be called from contexts that cannot sleep. Progress returns `-ENOTCONN` when the device exists but has no active scrub, so callers must distinguish idle from missing-device `-ENODEV`.

## Test Signals

Compile coverage should ensure all scrub users include this header without requiring implementation-only types. Functional tests should start scrub through the public caller path, query progress during and after the run, cancel globally and by device, pause around transaction-heavy operations, and run both read-only and repair-capable scrub. Device-replace tests should verify the same `btrfs_scrub_dev` declaration supports source-device copying with `is_dev_replace=true`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/scrub.h -->
