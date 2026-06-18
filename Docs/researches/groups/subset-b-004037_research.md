# Research Group: subset-b-004037

This grouped report covers the device-mapper zoned target, device-mapper zoned core helpers, generic device-mapper core, internal DM declarations, and early boot MD autodetection files listed for subset-b-004037.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-zone.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-zone.c

## Purpose

`dm-zone.c` provides the generic device-mapper integration layer for zoned block devices. It lets mapped devices expose `report_zones`, revalidate zone state while a new DM table is being bound, compute zoned queue restrictions, decide whether zone append must be emulated, translate zone append completions back to the original logical position, and build bitmaps for emulated `ZONE_RESET_ALL`.

## Important APIs, Types, and Functions

- `dm_blk_report_zones()` is the block-device `gendisk` report-zones operation exported through `dm_blk_dops` in `dm.c`. It chooses either the live table or the temporary `zone_revalidate_map` used during table binding.
- `dm_report_zones()` is exported for zoned target implementations. It wraps `blkdev_report_zones()` and remaps target-relative zone starts and write pointers to mapped-device sector space through `dm_report_zones_cb()`.
- `dm_revalidate_zones()` temporarily exposes a not-yet-live table to `blk_revalidate_disk_zones()` so zone write plug resources can be initialized during `__bind()`.
- `dm_set_zones_restrictions()` inspects each target's devices through `iterate_devices`, establishes max open/active zone limits, disables native zone append if any target requires emulation, and rejects incompatible reloads once zone plug resources exist.
- `dm_finalize_zone_settings()` updates `DMF_EMULATE_ZONE_APPEND` and clears zoned disk state when the table is effectively non-zoned.
- `dm_zone_endio()` adjusts the original bio sector after a successful `REQ_OP_ZONE_APPEND` clone completes.
- `dm_zone_get_reset_bitmap()` reports zones internally and marks the non-empty sequential zones that need individual reset for reset-all emulation.

The local helper structures `dm_device_zone_count` and `dm_zone_resource_limits` carry per-underlying-device accounting into target callbacks.

## Control Flow

Zone reporting starts in `dm_blk_report_zones()`, obtains a table under SRCU unless the caller is the revalidation task, then loops over targets with `dm_blk_do_report_zones()`. Each target must provide `report_zones`; the callback stops at the target end, remaps `start` and `wp`, optionally calls an internal callback, and finally emits the report with `disk_report_zone()`.

Queue setup calls `dm_set_zones_restrictions()` after table queue-limit calculation. It first determines whether native zone append can be used by checking target flags and the zoned status of all iterated devices. It then iterates all targets again to count mapped sequential zones and reduce max open/active limits. If no sequential zones are mapped, the DM device is downgraded to a regular block device by clearing zoned features and zone sizing.

Zone revalidation is special because the new table is not yet visible through `md->map`; `dm_revalidate_zones()` stores the table and current task in the mapped device, calls `blk_revalidate_disk_zones()`, then clears those temporary fields.

## State and Persistence Behavior

This file does not define durable metadata. Its state is transient DM core state: `md->zone_revalidate_map`, `md->revalidate_map_task`, `md->disk->nr_zones`, queue-limit fields, `DMF_EMULATE_ZONE_APPEND`, and zone write plug allocation state. Persistence belongs to individual targets such as `dm-zoned-metadata.c`.

## Dependencies and Integration Points

It depends on the block layer zoned APIs (`blkdev_report_zones`, `blk_revalidate_disk_zones`, queue limits, `blk_zone` conditions), DM table APIs (`dm_table_find_target`, `dm_table_get_target`, `dm_table_is_wildcard`), and target callbacks (`report_zones`, `iterate_devices`). `dm.c` calls `dm_zone_endio()` from clone completion, uses `dm_is_zone_write()` to avoid unsafe requeueing, and uses `dm_zone_get_reset_bitmap()` for `ZONE_RESET_ALL` emulation.

## Risks and Edge Cases

- Partially mapped underlying zoned devices can share zone resources with other mappings, so max open/active limits may be unreliable; the code warns but cannot globally enforce exclusivity.
- Once zone write plug resources exist, zone size and native/emulated append mode cannot be changed freely, so table reload validation is strict.
- Target `report_zones` implementations must return zones in the expected target-relative layout or the remapping callback can expose incorrect write pointers.
- Requeueing or changing sequential write behavior after write plug allocation risks breaking zone ordering; this file coordinates with `dm.c` to avoid that.

## Test Signals

Useful signals include `dmsetup` table reloads over whole and partial zoned devices, `blkzone report` through DM targets, `ZONE_APPEND` completion position checks, `ZONE_RESET_ALL` over tables that do and do not support native reset-all, table reload attempts with changed zone sizes, and tests where only conventional zones are mapped and the resulting device should not advertise zoned features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-zone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-zoned-metadata.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-zoned-metadata.c

## Purpose

`dm-zoned-metadata.c` owns the persistent and in-memory metadata model for the `dm-zoned` target. It discovers zones, validates and recovers superblocks, caches metadata blocks, loads the chunk-to-zone mapping table, tracks per-zone valid-block bitmaps and weights, manages free/mapped/reserved zone lists, arbitrates reclaim locks, and exposes mapping operations used by target I/O and reclaim code.

## Important APIs, Types, and Functions

- On-disk structures: `struct dmz_super` stores magic, metadata version, generation, metadata sizes, chunk count, labels, UUIDs, and CRC; `struct dmz_map` stores a data zone and optional buffer zone per chunk.
- In-memory structures: `struct dmz_metadata` stores device array, geometry, counts, xarray of `struct dm_zone`, two superblock sets, metadata block cache, zone map lock, map block array, zone lists, and wait queue for free zones. `struct dmz_mblock` caches a metadata block in an rbtree/LRU/dirty list.
- Constructor and destructor: `dmz_ctr_metadata()` initializes descriptors, loads superblocks and mappings, registers the shrinker, and reports geometry. `dmz_dtr_metadata()` frees shrinker, metadata blocks, mappings, and zones.
- Locking helpers: `dmz_lock_metadata()`, `dmz_unlock_metadata()`, `dmz_lock_map()`, `dmz_unlock_map()`, `dmz_lock_flush()`, `dmz_unlock_flush()`.
- Persistence path: `dmz_flush_metadata()`, `dmz_log_dirty_mblocks()`, `dmz_write_dirty_mblocks()`, `dmz_write_sb()`, `dmz_recover_mblocks()`, `dmz_load_sb()`.
- Mapping path: `dmz_get_chunk_mapping()`, `dmz_put_chunk_mapping()`, `dmz_get_chunk_buffer()`, `dmz_alloc_zone()`, `dmz_free_zone()`, `dmz_map_zone()`, `dmz_unmap_zone()`.
- Bitmap path: `dmz_validate_blocks()`, `dmz_invalidate_blocks()`, `dmz_block_valid()`, `dmz_first_valid_block()`, `dmz_copy_valid_blocks()`, `dmz_merge_valid_blocks()`.

## Control Flow

Construction starts by allocating `struct dmz_metadata`, initializing locks/lists, and calling `dmz_init_zones()`. For a single zoned device it reports hardware zones and chooses the first conventional zone as the primary superblock zone. For a multi-device setup it emulates zones on the first regular device as cache zones, reports zones on later devices, and assigns per-device zone offsets.

`dmz_load_sb()` reads and checks the primary and secondary metadata sets. If one set is corrupt, `dmz_recover_mblocks()` copies metadata from the valid set and rewrites the bad set's superblock. The valid set with the higher generation becomes `mblk_primary`. Metadata version 2 also verifies tertiary superblocks on additional zoned devices for label and UUID consistency.

`dmz_load_mapping()` reads map blocks into pinned metadata blocks, marks mapped data and buffer zones, computes zone weights from bitmap blocks, and puts zones on mapped lists. All remaining usable non-metadata zones are classified into unmapped cache, random, sequential, or reserved sequential lists.

The I/O path calls `dmz_get_chunk_mapping()`. For reads and discards of unmapped chunks it returns `NULL`; for writes it allocates a cache or random zone and maps it. If the mapped zone is under reclaim, it asks reclaim to terminate, waits briefly, and retries. Otherwise it activates the zone and rotates it in LRU order. `dmz_put_chunk_mapping()` deactivates the zone and opportunistically unmaps empty data or buffer zones.

## State and Persistence Behavior

Metadata is stored as two full metadata sets in conventional or cache zones: superblock, chunk map blocks, and bitmap blocks. Flush is log-first: dirty metadata blocks are first written to the non-primary set, that set's superblock generation is advanced, the same blocks are then written to the primary set, and finally the primary superblock is advanced. Only after both phases succeed are dirty bits cleared and `sb_gen` incremented. This protects against power loss during in-place updates.

Per-zone state includes flags (`DMZ_META`, `DMZ_DATA`, `DMZ_BUF`, `DMZ_RESERVED`, `DMZ_RECLAIM`, `DMZ_SEQ_WRITE_ERR`, offline/read-only bits), write pointer block, valid-block weight, mapped chunk, optional paired buffer zone, and activation refcount. Persistent validity is represented by bitmap blocks; list membership and refcounts are reconstructed in memory.

## Dependencies and Integration Points

This file depends heavily on `dm-zoned.h` types, block zoned reporting and reset APIs, Linux xarray/rbtree/list/shrinker primitives, bio submission for metadata I/O, CRC32, UUID helpers, and target/reclaim callbacks for device-health checks and reclaim scheduling. `dm-zoned-target.c` uses this layer for every read/write/discard decision, and `dm-zoned-reclaim.c` uses it to select zones, copy bitmap state, remap chunks, and flush durable updates after reclaim.

## Risks and Edge Cases

- Metadata flush correctness depends on strict ordering: log set, log superblock, primary blocks, primary superblock. Any change here can corrupt recovery semantics.
- Refcount, reclaim bit, and map lock ordering must stay consistent. Active zones cannot be reclaimed, and reclaim waits can temporarily drop both metadata and map locks.
- Multi-device version 2 metadata relies on label and UUID checks across devices; mismatches correctly fail setup but can be operationally surprising after device replacement.
- The target rejects zones whose capacity is smaller than zone size, and version 2 ignores a possible runt zone. Tests need hardware or emulation that exposes those cases.
- `dmz_alloc_zone()` can spin through offline or metadata zones and can block writers waiting for reclaim if free zones are exhausted.
- A sequential write error forces a write-pointer report and invalidates blocks between the new device write pointer and the previous in-memory pointer.

## Test Signals

High-value tests include format/load of valid metadata, CRC and generation failover between two metadata sets, tertiary superblock mismatch on multi-device setups, dirty metadata flush after writes/discards/reclaim, free-zone exhaustion with reclaim wakeup, sequential write error recovery, read-after-discard zeroing via bitmap invalidation, and shrinker pressure on the metadata block cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-zoned-metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-zoned-reclaim.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-zoned-reclaim.c

## Purpose

`dm-zoned-reclaim.c` implements background reclaim for `dm-zoned`. Its job is to keep enough random/cache zones free by moving valid blocks between data, buffer, random/cache, and sequential zones, then updating metadata atomically enough that the target can continue serving writes.

## Important APIs, Types, and Functions

- `struct dmz_reclaim` stores the metadata pointer, delayed work and workqueue, `dm_kcopyd` client and throttle, device index, copy state flag, and last access time.
- `dmz_ctr_reclaim()` and `dmz_dtr_reclaim()` allocate/destroy reclaim state, kcopyd client, and ordered workqueue.
- `dmz_suspend_reclaim()` and `dmz_resume_reclaim()` coordinate with target suspend/resume.
- `dmz_reclaim_bio_acc()` updates last access time; `dmz_schedule_reclaim()` starts reclaim immediately when thresholds require it.
- Copy/move helpers include `dmz_reclaim_copy()`, `dmz_reclaim_align_wp()`, `dmz_reclaim_buf()`, `dmz_reclaim_seq_data()`, `dmz_reclaim_rnd_data()`, and `dmz_reclaim_empty()`.
- Policy helpers include `dmz_reclaim_percentage()`, `dmz_should_reclaim()`, `dmz_target_idle()`, and `dmz_do_reclaim()`.

## Control Flow

The constructor queues reclaim work immediately. `dmz_reclaim_work()` aborts if any backing device is dying, computes the percentage of unmapped cache or random zones, and either reschedules for the idle period or runs reclaim. Reclaim throttling is set high when idle or critically low on free zones and lower when the target is busy.

`dmz_do_reclaim()` asks metadata for a reclaim candidate. Empty random/cache zones are simply unmapped and freed. Non-empty random/cache data zones are copied to a free sequential zone when possible, their validity bitmap is copied, and the chunk is remapped. Buffered sequential zones are handled in two ways: if buffer valid blocks are empty or after the data zone write pointer, buffer blocks are merged into the sequential data zone; otherwise data blocks are merged into the buffer zone so the original sequential zone can be freed and the buffer zone becomes the data mapping.

Every successful reclaim operation calls `dmz_flush_metadata()` before reporting success. If the target touches a zone being reclaimed, metadata sets `DMZ_RECLAIM_TERMINATE`, waits on the reclaim bit, and retries the mapping lookup.

## State and Persistence Behavior

Reclaim changes persistent state indirectly through metadata operations: valid-block bitmaps, chunk mapping entries, zone lists, and superblock generations. Data movement itself is done with `dm_kcopyd_copy()` and optional zeroout for sequential write-pointer alignment. The code takes `dmz_lock_flush()` around bitmap/map changes after copy completion to avoid racing with metadata flush and target modifications.

## Dependencies and Integration Points

The file depends on `dm-zoned-metadata.c` for candidate selection, zone allocation, bitmap copy/merge, mapping updates, and flush. It depends on `dm-kcopyd` for block copying and the block layer for zeroout. `dm-zoned-target.c` calls `dmz_reclaim_bio_acc()` on I/O completion paths, exposes a `reclaim` message that calls `dmz_schedule_reclaim()`, and suspends/resumes reclaim with the target.

## Risks and Edge Cases

- Sequential destination writes must be strictly ordered. `dmz_reclaim_align_wp()` zeroes holes to align write pointers before copying valid regions.
- Reclaim can be interrupted by foreground I/O through `DMZ_RECLAIM_TERMINATE`; interrupted reclaim must unlock the reclaim bit exactly once and leave mappings valid.
- If no free sequential or fallback zone exists, reclaim returns `-ENOSPC` and writers may remain pressure-dependent on future frees.
- Copy success and metadata persistence are separate. A copy can succeed but metadata flush can fail due to device errors, leaving the target in an error path.
- Cache-zone policy is asymmetric in multi-device setups: the first device can hold cache zones, but reclaim is not started for device index 0 when cache zones exist.

## Test Signals

Test with forced low free random/cache percentages, idle-triggered reclaim after `DMZ_IDLE_PERIOD`, foreground I/O racing reclaim termination, reclaim of empty zones, random-to-sequential migration, buffered sequential merge in both directions, metadata flush failure injection after copy, and manual `dmsetup message ... reclaim`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-zoned-reclaim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-zoned-target.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-zoned-target.c

## Purpose

`dm-zoned-target.c` registers and implements the `zoned` DM target. It exposes a regular drive-managed block device on top of one zoned device or a regular-plus-zoned multi-device layout by using metadata to map logical chunks to zones, serializing I/O per chunk, buffering unaligned writes to sequential zones, periodically flushing metadata, and running background reclaim.

## Important APIs, Types, and Functions

- `struct dmz_target` is the target-private object containing DM devices, `struct dmz_dev` array, metadata, chunk work radix tree and workqueue, clone bioset, flush list/workqueue, and flags.
- `struct dmz_bioctx` is per-bio context stored through `ti->per_io_data_size`; it tracks the backing device, active zone, original bio, and reference count across internal clones.
- `struct dm_chunk_work` serializes queued bios for one logical chunk.
- Target callbacks: `dmz_ctr()`, `dmz_dtr()`, `dmz_map()`, `dmz_io_hints()`, `dmz_prepare_ioctl()`, `dmz_suspend()`, `dmz_resume()`, `dmz_iterate_devices()`, `dmz_status()`, and `dmz_message()`.
- I/O helpers: `dmz_handle_read()`, `dmz_handle_write()`, `dmz_handle_direct_write()`, `dmz_handle_buffered_write()`, `dmz_handle_discard()`, `dmz_submit_bio()`, `dmz_bio_endio()`, and `dmz_clone_endio()`.
- Health helpers: `dmz_bdev_is_dying()` and `dmz_check_bdev()`.

## Control Flow

Setup validates that a single-device target uses a zoned device, while a multi-device target uses a regular first device followed by zoned devices of matching zone size. It initializes metadata, sets target size to `nr_chunks << zone_shift`, initializes a bioset, chunk workqueue, flush workqueue, and per-device reclaim workers.

`dmz_map()` rejects I/O if any device is dying, enforces 4 KiB block alignment, stores per-bio context, treats empty write bios as flush requests queued to `flush_list`, splits bios at zone boundaries with `dm_accept_partial_bio()`, and queues the bio to a per-chunk work item. The radix tree ensures all bios for a chunk are processed serially while different chunks can run on the workqueue concurrently.

`dmz_handle_bio()` takes the metadata read lock, gets or creates the chunk mapping, activates the zone, and dispatches based on bio operation. Reads select valid blocks from data zone first, then buffer zone, and zero-fill holes. Writes go directly to random/cache zones or to sequential zones only when aligned to the zone write pointer; otherwise they allocate/use a buffer zone. Discards and write-zeroes invalidate bitmap ranges in the data and buffer zones. Completion releases mappings, deactivates zones, and ends the original bio after all internal clone references complete.

Flush work periodically calls `dmz_flush_metadata()` and completes queued flush bios. Suspend flushes chunk work, suspends reclaim, and cancels delayed flush; resume restarts flush and reclaim.

## State and Persistence Behavior

The target itself keeps transient scheduling state: per-chunk work objects, bio context references, flush queue, workqueues, bioset, and device health flags. Durable state lives in metadata and is updated through validation/invalidation of blocks and chunk mapping changes. `dmz_flush_work()` and target destruction force metadata flush, while reclaim also flushes after successful remapping.

## Dependencies and Integration Points

This file plugs into the DM target registry through `module_dm(zoned)` with features `DM_TARGET_SINGLETON` and `DM_TARGET_MIXED_ZONED_MODEL`. It uses DM device acquisition (`dm_get_device`, `dm_put_device`), DM per-bio data, `dm_accept_partial_bio()`, queue-limit hints, and the block layer for bios, zoned geometry, and media-change checks. It is the main consumer of `dm-zoned-metadata.c` and starts/stops `dm-zoned-reclaim.c`.

## Risks and Edge Cases

- The target depends on strict 4 KiB logical block alignment. Misaligned bios are killed.
- `dmz_submit_bio()` advances the original bio as clones are submitted; partial failure paths must still complete the original bio through the per-bio refcount.
- Sequential write errors set `DMZ_SEQ_WRITE_ERR` and are repaired later by metadata write-pointer refresh.
- Buffered writes make read precedence and bitmap invalidation critical; stale valid bits in data or buffer zones can return old data.
- Flush bios complete with the metadata flush status, so metadata device failure propagates to upper layers.
- Multi-device layout validation is strict and does not support partial mappings.

## Test Signals

Exercise single-device and regular-plus-zoned constructors, rejected argument layouts, 4 KiB alignment checks, zone-boundary bio splitting, reads from unmapped chunks returning zeros, direct sequential writes at write pointer, unaligned sequential writes through buffers, discard/write-zeroes invalidation, periodic and explicit flush behavior, suspend/resume, status output, ioctl forwarding, backing-device dying paths, and the `reclaim` message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-zoned-target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-zoned.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-zoned.h

## Purpose

`dm-zoned.h` is the shared internal interface for the `dm-zoned` target, metadata manager, and reclaim worker. It defines the fixed 4 KiB block geometry, device and zone descriptors, zone state flags, logging helpers, and function prototypes that bind the three implementation files together.

## Important APIs, Types, and Functions

- Geometry macros define the target's fixed 4 KiB block size, sector/block conversions, and helpers such as `dmz_bio_block()`, `dmz_bio_blocks()`, `dmz_bio_chunk()`, and `dmz_chunk_block()`.
- `struct dmz_dev` describes a backing device, including block device pointer, metadata/reclaim backpointers, UUID, capacity, device index, zone offsets, zone size, free/mapped random and sequential zone lists, and health flags.
- `struct dm_zone` describes one logical zone, including list node, owning device, flags, activation refcount, id, write pointer block, valid-block weight, mapped chunk, and optional buffer-zone pairing.
- Zone flags classify cache/random/sequential type, offline/read-only critical states, metadata/data/buffer/reserved usage, and reclaim/write-error state.
- Inline helpers `dmz_activate_zone()`, `dmz_deactivate_zone()`, and `dmz_is_active()` manage active references and update reclaim bio access time on deactivation.
- Prototypes expose metadata construction, locking, flushing, geometry, allocation, mapping, bitmap, reclaim, and device-health helpers.

## Control Flow

This header has no runtime control flow beyond inline refcount helpers. Its main role is to make the target call metadata for mapping and bitmap updates, make reclaim call metadata and device-health helpers, and make metadata schedule reclaim or query backing-device health without circular type definitions in each C file.

## State and Persistence Behavior

The header declares state containers but does not persist anything itself. `struct dm_zone` fields represent the in-memory projection of persistent chunk maps and bitmaps plus transient activity and reclaim state. `struct dmz_dev` stores transient device lists/counters and durable UUID identity loaded from metadata.

## Dependencies and Integration Points

It includes kernel block, DM, kcopyd, list, spinlock, mutex, workqueue, rwsem, rbtree, radix-tree, and shrinker headers. It is included by `dm-zoned-target.c`, `dm-zoned-metadata.c`, and `dm-zoned-reclaim.c`. The logging macros wrap DM logging with device or metadata labels.

## Risks and Edge Cases

- The fixed 4 KiB block contract is assumed throughout metadata bitmaps and target alignment checks.
- Zone flag bits are shared across all three C files; changes must preserve meaning and bit ordering assumptions.
- `dmz_deactivate_zone()` assumes `zone->dev->reclaim` is valid, so lifecycle ordering must construct reclaim before I/O and destroy it after chunk work is stopped.
- Device flags use shifted constants rather than a conventional enum; callers treat them as bit masks, so additions must avoid overlap.

## Test Signals

Compile coverage is the primary signal for this header. Functional tests should verify 4 KiB alignment behavior, chunk/block conversions at zone boundaries, active refcount and reclaim exclusion, and state transitions using the shared flags across target, metadata, and reclaim code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-zoned.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm.c

## Purpose

`dm.c` is the generic device-mapper core driver. It registers the DM block major, creates and destroys mapped devices, owns gendisk/block-device operations, opens target devices, binds and swaps mapping tables, splits and maps bios to targets, handles completion/requeue/accounting, manages suspend/resume, exposes DAX and persistent reservation forwarding, and integrates zoned-device special handling.

## Important APIs, Types, and Functions

- Module lifecycle: `dm_init()`, `dm_exit()`, `local_init()`, `local_exit()` initialize DM subsystems, targets, kcopyd, ioctl interface, statistics, uevents, and the deferred-remove workqueue.
- Device lifecycle: `dm_create()`, `alloc_dev()`, `dm_destroy()`, `dm_destroy_immediate()`, `free_dev()`, `cleanup_mapped_device()`, `dm_get_md()`, `dm_get()`, `dm_put()`, `dm_hold()`.
- Table binding: `__bind()`, `__unbind()`, `dm_swap_table()`, `dm_setup_md_queue()`, `dm_get_live_table()`, `dm_put_live_table()`, `dm_sync_table()`.
- Bio path: `dm_submit_bio()`, `dm_split_and_process_bio()`, `__split_and_process_bio()`, `__map_bio()`, `alloc_io()`, `alloc_tio()`, `clone_endio()`, `dm_io_dec_pending()`, `dm_accept_partial_bio()`, `dm_submit_bio_remap()`.
- Abnormal and flush I/O: `is_abnormal_io()`, `__process_abnormal_io()`, `__send_empty_flush()`, `__send_abnormal_io()`, `__send_zone_reset_all()`.
- Suspend/resume: `dm_suspend()`, `dm_resume()`, `__dm_suspend()`, `__dm_resume()`, internal suspend/resume variants, `dm_wq_work()`, `dm_wait_for_completion()`.
- User-facing block ops: open/close/ioctl/getgeo/report_zones/poll_bio/get_unique_id/PR ops through `dm_blk_dops` and request-based equivalents.

Opaque state types such as `struct mapped_device`, `struct dm_io`, and `struct dm_target_io` are defined in `dm-core.h`; this file is their main implementation.

## Control Flow

Normal bio submission starts at `dm_submit_bio()`, obtains the live table under SRCU, queues bios if `DMF_BLOCK_IO_FOR_SUSPEND` is set, and otherwise calls `dm_split_and_process_bio()`. The splitter decides whether to split for abnormal operations or zoned constraints, optionally plugs zone writes, allocates `struct dm_io`, initializes `clone_info`, handles preflush, emulated or native `ZONE_RESET_ALL`, and maps one target-sized segment. If a remainder exists, it trims and resubmits the original bio so already-submitted pieces complete first.

`__split_and_process_bio()` finds the target, handles abnormal I/O, validates atomic and NOWAIT support, allocates a clone, and calls `__map_bio()`. `__map_bio()` invokes fast paths for linear/stripe targets or the target's map method, then interprets `DM_MAPIO_SUBMITTED`, `DM_MAPIO_REMAPPED`, `DM_MAPIO_KILL`, or `DM_MAPIO_REQUEUE`.

Completion starts at `clone_endio()`. It handles discard/write-zeroes capability fallback, calls `dm_zone_endio()` for zoned clones, invokes target `end_io`, blocks unsafe requeue of zoned writes, releases swap-bio throttles, frees clone state, and decrements `dm_io`. Final `dm_io` completion performs accounting, requeue handling, pending-I/O decrement, and original bio completion.

Table setup creates a mapped device with a default bio-based queue, then `dm_setup_md_queue()` calculates restrictions, adds the disk, links holders, initializes sysfs, and records the DM queue mode. Table swaps require suspension and bind a new table under `suspend_lock`, preserving queue limits in special noflush request-based cases.

Suspend sets pre-suspend flags, optionally freezes the filesystem, blocks new I/O, waits for SRCU readers/workqueues/in-flight I/O, optionally stops request queues, and calls target postsuspend hooks. Resume calls target resume hooks, unblocks queued bios, restarts queues, and thaws the filesystem.

## State and Persistence Behavior

DM core itself does not persist mapping data; userspace owns table definitions. Runtime state includes the IDR of minors, mapped-device holder/open counts, current table pointer, mempools, pending I/O counters, deferred and requeue lists, flags for deletion/suspend/freeing/no-flush, queue mode, uevent sequence, geometry, statistics, DAX object, and target-device reference list. Persistence-relevant behavior is in ordering: table changes require suspend, bios are accounted and completed exactly once, and flushes are forwarded or optimized according to table restrictions.

## Dependencies and Integration Points

`dm.c` depends on DM internal headers (`dm-core.h`, `dm-rq.h`, `dm-uevent.h`, `dm-ima.h`), block-layer bio/gendisk/queue APIs, blk-mq for request-based devices, DAX, blk-crypto, statistics, SRCU/RCU, IDR, mempools, and target type callbacks. It calls zoned helpers from `dm-zone.c` and exposes report zones through `dm_blk_dops`. It calls into table code for restrictions and target lookup, into interface/sysfs/uevent layers for userspace integration, and into persistent reservation operations by iterating a single target's devices.

## Risks and Edge Cases

- Requeue logic is deliberately conservative for zoned writes; requeueing a sequential write can violate ordering and is converted to I/O error.
- Split bio accounting is subtle because `dm_accept_partial_bio()` can reduce the segment after accounting state is recorded.
- `REQ_NOWAIT`, `REQ_POLLED`, flush-with-data, abnormal ops, and duplicated bios each have separate allocation and completion paths.
- Suspend/resume must coordinate SRCU, workqueue flushing, filesystem freeze, request queue stop/start, and target hooks without deadlocking.
- Table reloads with changed mempool front pads require replacing mempools for bio-based devices.
- DAX and persistent reservation forwarding only work for compatible single-target tables.

## Test Signals

Signals include generic DM tests for create/open/close/remove/deferred remove, linear and stripe I/O, table load/suspend/resume/swap, flush and flush-with-data forwarding, discard/write-zeroes/secure-erase splitting, NOWAIT and polled bio behavior, target requeue handling, zoned bio splitting and reset-all emulation, request-based queue setup, DAX operations, persistent reservation forwarding, and uevent/cookie sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm.h

## Purpose

`dm.h` is the internal device-mapper header shared by core DM modules, table code, target registry, sysfs/interface code, and built-in targets. It declares the cross-file APIs used to manage tables, mapped-device state, target types, zoned integration, suspend/resume, table devices, uevents, mempools, and common linear/stripe targets.

## Important APIs, Types, and Functions

- Table APIs cover event callbacks, target lookup, data-device checks, queue-limit calculation, table restrictions, device list access, suspend/resume target hooks, queue mode, immutable target lookups, request-based checks, wildcard target access, and size-change support.
- Mapped-device APIs cover queue setup, type locking, deletion/suspension tests, internal suspend/resume, destroy/open-count/delete locking, table device reference management, uevents, and mempool cleanup.
- Zoned declarations conditionally expose `dm_blk_report_zones()`, `dm_is_zone_write()`, `dm_zone_get_reset_bitmap()`, `dm_set_zones_restrictions()`, `dm_revalidate_zones()`, `dm_finalize_zone_settings()`, and `dm_zone_endio()` when zoned block support is enabled.
- Target registry declarations include init/exit, get/put target type, iterate target types, and command argument splitting.
- Utility definitions include suspend/status flags and hash-lock sizing/index helpers used by DM subsystems.

## Control Flow

This file has minimal inline control flow. The zoned `dm_is_zone_write()` fallback returns false when `CONFIG_BLK_DEV_ZONED` is disabled, and `dm_has_zone_plugs()` becomes false. The hash-lock helpers compute a power-of-two lock count based on CPU count and a stable hash index for sector/block-level locking.

## State and Persistence Behavior

The header declares no persistent state. Its flags and prototypes define how other files manipulate runtime mapped-device state. The suspend flags and zoned prototypes are especially important because they coordinate how `dm.c`, table code, and `dm-zone.c` update queues and mapped-device flags.

## Dependencies and Integration Points

It includes core Linux filesystem, DM, block, backing-dev, geometry, completion, kobject, refcount, and log2 headers plus `dm-stats.h`. It is included across the DM implementation, while `dm.c` and `dm-zone.c` provide many of the declared functions. Consumers must also understand opaque structures defined in `dm-core.h`.

## Risks and Edge Cases

- Function declarations here are internal contracts; mismatched assumptions between table code, core, and target implementations can break suspend ordering or queue setup.
- Conditional zoned declarations mean non-zoned builds compile out key behavior; callers must be prepared for false/null behavior from the stubs.
- `dm_target_bio_based`, `dm_target_request_based`, and `dm_target_hybrid` are simple callback-presence tests, so target type initialization must set callbacks accurately.
- `dm_hash_locks_index()` assumes the lock count is a power of two.

## Test Signals

Build coverage across zoned and non-zoned configurations is the main signal. Runtime tests should exercise table restrictions, suspend/resume hooks, target registry load/unload, internal suspend users, zoned builds with `report_zones`, and non-zoned builds where zoned helpers compile to safe stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/md-autodetect.c -->
# sources/distributed-fs/ceph-client/drivers/md/md-autodetect.c

## Purpose

`md-autodetect.c` implements early boot setup for built-in Linux MD RAID arrays. It parses `raid=` and `md=` kernel command-line options, optionally autodetects marked RAID partitions after device probing, and assembles explicitly configured arrays before normal userspace is available.

## Important APIs, Types, and Functions

- `struct md_setup_args` records one command-line MD array definition: minor, partitioned flag, level, chunk size, and comma-separated device names.
- `md_setup()` parses `md=` options, supporting partitionable `mdd`, persistent-superblock arrays (`LEVEL_NONE`), RAID0, and linear legacy non-persistent forms.
- `md_setup_drive()` resolves device names, allocates an `mddev`, sets array info for non-persistent arrays, adds disks, and calls `do_md_run()`.
- `raid_setup()` parses `raid=` options: `noautodetect`, `autodetect`, `partitionable`, and `part`.
- `autodetect_raid()` waits for device probing and calls `md_autostart_arrays()`.
- `md_run_setup()` is the externally called boot-time entry that runs autodetect unless disabled and then processes all collected `md=` entries.

## Control Flow

`__setup("md=", md_setup)` records each boot-line MD definition in `md_setup_args`, replacing earlier definitions for the same minor/partitioned pair and capping at 256 entries. `__setup("raid=", raid_setup)` configures global autodetect behavior.

At boot setup time, `md_run_setup()` first either skips autodetection or calls `autodetect_raid()`, which waits for all device probes and autostarts arrays for detected RAID partitions. It then iterates stored `md=` entries and calls `md_setup_drive()` for each. Drive setup resolves each component through `early_lookup_bdev()` and initramfs-visible `/dev/...` stat checks, allocates/locks the md device, skips if it was already autodetected, optionally initializes non-persistent array info, adds component disks, starts the array, and unlocks/releases the `mddev`.

## State and Persistence Behavior

State is boot-only `__initdata`: `raid_noautodetect`, `raid_autopart`, `md_setup_args`, and `md_setup_ents`. The file does not persist RAID metadata; persistent arrays rely on MD superblocks discovered by MD core. Non-persistent command-line arrays are described by `mdu_array_info_s` and component `mdu_disk_info_s` at boot.

## Dependencies and Integration Points

It integrates with the kernel command-line parser through `__setup`, early block-device lookup/stat helpers, MD core (`md_alloc`, `mddev_suspend_and_lock`, `md_set_array_info`, `md_add_new_disk`, `do_md_run`, `md_autostart_arrays`), and RAID UAPI structures from `md_u.h` and `md_p.h`. It depends on built-in MD support; module-only MD setups are not handled here.

## Risks and Edge Cases

- Device-name parsing mutates the command-line device list by replacing commas with NUL bytes.
- Autodetected arrays can race conceptually with explicit `md=` definitions; explicit setup skips arrays that already have disks or `raid_disks`.
- If any component device cannot be resolved, parsing stops at that point and may assemble with fewer devices than expected for non-persistent arrays.
- Legacy non-persistent RAID0/linear parsing uses chunk factor conversion `1 << (factor + 12)`, so malformed factors can produce surprising sizes.
- The code is `__init`/`__initdata`, so it cannot be reused after boot.

## Test Signals

Boot tests should cover `raid=noautodetect`, forced `raid=autodetect`, partitionable arrays, duplicate `md=` replacement, persistent-superblock `md=n,devs`, non-persistent RAID0 and linear forms, unresolved devices, already-autodetected arrays, and successful `do_md_run()` invocation for built-in MD configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/md-autodetect.c -->
