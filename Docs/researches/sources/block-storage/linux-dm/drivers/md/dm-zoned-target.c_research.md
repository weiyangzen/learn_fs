# File Research: sources/block-storage/linux-dm/drivers/md/dm-zoned-target.c

## Scope

This file implements the Device Mapper `zoned` target. It exposes a regular block device backed by one zoned device or by a regular cache device plus zoned devices, routes reads/writes/discards through dm-zoned metadata mappings, serializes work per logical chunk, manages flush/reclaim workers, and reports target status.

## Public And Internal APIs Covered

- DM target entry points: `dmz_ctr()`, `dmz_dtr()`, `dmz_map()`, `dmz_io_hints()`, `dmz_prepare_ioctl()`, `dmz_suspend()`, `dmz_resume()`, `dmz_iterate_devices()`, `dmz_status()`, `dmz_message()`.
- Module lifecycle: `dmz_init()` and `dmz_exit()`.
- Backing-device health helpers exported through the header: `dmz_bdev_is_dying()`, `dmz_check_bdev()`.
- Bio/chunk processing: `dmz_queue_chunk_work()`, `dmz_chunk_work()`, `dmz_handle_bio()`, read/write/discard helpers, clone submission and completion.
- Flush processing: `dmz_flush_work()`.
- Device setup helpers: `dmz_get_zoned_device()`, `dmz_put_zoned_device()`, `dmz_fixup_devices()`.

## Control Flow And Behavior

- Constructor accepts one or more devices. A single-device table must use a zoned block device. A multi-device table uses the first regular block device as cache zones and all later devices as zoned devices with matching zone sizes.
- Device setup rejects partial target offsets, records capacity/name/dev index, computes per-device zone counts and zone offsets, initializes metadata, sets target length to the number of mappable chunks, and creates biosets, chunk workqueue, flush workqueue, and per-device reclaim contexts.
- `dmz_map()` rejects I/O if any backing device is dying, ignores non-write empty bios, enforces 4 KiB dm-zoned block alignment, handles empty write bios as flush requests, splits bios at zone/chunk boundaries, and queues work for the bio's chunk.
- `dmz_queue_chunk_work()` uses a radix tree keyed by chunk number so all bios targeting the same chunk are serialized through one `dm_chunk_work`. References keep a work item alive while queued bios and the workqueue own it.
- `dmz_handle_bio()` takes the metadata read lock, obtains or allocates the chunk mapping, activates the zone, records reclaim access, dispatches by operation, releases the mapping, completes the original bio context, and unlocks metadata.
- Reads from unmapped chunks are zero-filled. Reads from mapped chunks consult valid-block bitmaps in the data zone and then optional buffer zone; valid extents are cloned to the correct backing zone and holes are zero-filled.
- Writes to random/cache zones or sequential zones exactly at the write pointer are direct writes. Unaligned writes to sequential zones allocate/use a random/cache buffer zone. Direct and buffered writes update valid-block bitmaps and invalidate overlapping stale blocks in the peer zone.
- Discards invalidate valid blocks in data and buffer zones and do nothing for unmapped chunks.
- `dmz_submit_bio()` clones the original bio to the selected zone/device, advances the original bio, increments per-bio context references, submits the clone, and advances sequential write pointers for write clones.
- Completion records backing-device check-needed on errors, marks sequential write errors for failed writes to sequential zones, deactivates zones, and completes the original bio when all clones finish.
- Flush work periodically and on empty-write flushes calls `dmz_flush_metadata()` and completes queued flush bios.
- Suspend flushes chunk work, stops reclaim, and cancels flush work. Resume restarts flush and reclaim work. The `reclaim` target message schedules reclaim on all devices.

## State And Data Structures

- `struct dmz_target` stores DM devices, dm-zoned device descriptors, metadata pointer, chunk radix tree/lock/workqueue, clone bioset, and flush list/workqueue.
- `struct dmz_bioctx` is per-original-bio context containing current backing device, active zone, original bio, and reference count.
- `struct dm_chunk_work` serializes bios for one logical chunk with a work item, refcount, chunk id, target pointer, and bio list.
- Target type `dmz_type` is named `zoned`, version `{2, 0, 0}`, and has `DM_TARGET_SINGLETON | DM_TARGET_MIXED_ZONED_MODEL`.

## Dependencies

- dm-zoned metadata and reclaim APIs from `dm-zoned.h`.
- Device Mapper target/device APIs, target status/messages, and `dm_accept_partial_bio()`.
- Linux block APIs for bio cloning/submission, zone geometry, queue limits, disk events, flush/discard/write-zeroes flags, biosets, workqueues, radix tree, and refcounts.

## Risks And Invariants

- All bios for the same chunk must be serialized; metadata valid-block maps are not independently protected against concurrent same-chunk mutation.
- The original bio is advanced as clones are submitted, so reference counting in `dmz_bioctx` must match every clone plus the original completion path.
- Sequential zone `wp_block` is advanced optimistically on write submission; later errors are recorded as `DMZ_SEQ_WRITE_ERR` so metadata can revalidate the actual device write pointer.
- Reads must prefer the zone whose bitmap marks a block valid and zero-fill invalid/unwritten regions.
- Device health flags switch the target into failing-I/O behavior when queues die or media-change events indicate offline backing devices.
