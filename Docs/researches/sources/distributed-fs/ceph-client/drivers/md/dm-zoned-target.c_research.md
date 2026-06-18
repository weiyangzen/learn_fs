# sources/distributed-fs/ceph-client/drivers/md/dm-zoned-target.c

## Purpose

`dm-zoned-target.c` registers and implements the `zoned` DM target. It exposes a regular drive-managed block device on top of zoned media by mapping logical chunks to zones, serializing I/O per chunk, buffering unaligned sequential writes, periodically flushing metadata, and running reclaim.

## Important APIs, Types, and Functions

`struct dmz_target` holds target devices, metadata, chunk-work radix tree/workqueue, clone bioset, flush queue/workqueue, and backing-device descriptors. `struct dmz_bioctx` tracks per-bio clone references and active zone. `struct dm_chunk_work` serializes bios for one chunk. Target callbacks are `dmz_ctr()`, `dmz_dtr()`, `dmz_map()`, `dmz_io_hints()`, `dmz_prepare_ioctl()`, `dmz_suspend()`, `dmz_resume()`, `dmz_iterate_devices()`, `dmz_status()`, and `dmz_message()`. I/O helpers include `dmz_handle_read()`, `dmz_handle_write()`, `dmz_handle_direct_write()`, `dmz_handle_buffered_write()`, `dmz_handle_discard()`, and `dmz_submit_bio()`.

## Control Flow

Setup validates a single zoned device or a regular first device followed by zoned devices of matching zone size, initializes metadata, sets target size from chunk count, creates workqueues/bioset, and starts reclaim workers. `dmz_map()` checks device health, enforces 4 KiB alignment, queues flush bios, splits bios at zone boundaries, and queues work per chunk. `dmz_handle_bio()` takes metadata access, obtains a chunk mapping, activates zones, dispatches read/write/discard, releases mapping, and completes the bio.

Reads prefer valid data-zone blocks, then buffer-zone blocks, and zero-fill holes. Writes go direct to random/cache zones or sequential zones at the write pointer; unaligned sequential writes go to a buffer zone. Discards and write-zeroes invalidate bitmap ranges.

## State and Persistence Behavior

Target state is transient: chunk work objects, bio contexts, health flags, flush queue, bioset, and workqueues. Durable state is updated through metadata mappings and valid-block bitmaps. Periodic flush work, explicit flush bios, reclaim, and destructor paths call `dmz_flush_metadata()`.

## Dependencies and Integration Points

The target integrates with DM through `module_dm(zoned)` and uses DM device acquisition, per-bio data, `dm_accept_partial_bio()`, queue-limit hints, and target status/message callbacks. It is the main consumer of `dm-zoned-metadata.c` and owner of reclaim lifecycle.

## Risks and Test Signals

Misaligned bios are killed, clone reference accounting must be exact, stale bitmap invalidation can return old data, sequential write errors require later repair, and partial mappings are unsupported. Test constructor layouts, chunk serialization, reads from holes, direct and buffered writes, discard/write-zeroes invalidation, flush completion status, suspend/resume, status output, ioctl forwarding, backing-device death, and explicit reclaim.
