# File Research: sources/block-storage/linux-dm/drivers/md/dm-zoned-metadata.c

## Scope

This file implements the dm-zoned metadata layer. It discovers zones, loads and validates the on-disk metadata format, caches metadata blocks, maintains chunk-to-zone mappings, tracks per-zone valid-block bitmaps and weights, allocates/frees zones, coordinates active I/O with reclaim, and flushes metadata using a dual-superblock/logging scheme.

## Public And Internal APIs Covered

- Constructor/destructor/resume: `dmz_ctr_metadata()`, `dmz_dtr_metadata()`, `dmz_resume_metadata()`.
- Locks: `dmz_lock_map()`, `dmz_unlock_map()`, `dmz_lock_metadata()`, `dmz_unlock_metadata()`, `dmz_lock_flush()`, `dmz_unlock_flush()`.
- Geometry/accessors: `dmz_start_sect()`, `dmz_start_block()`, `dmz_nr_chunks()`, `dmz_nr_zones()`, zone-size and zone-count helpers, `dmz_metadata_label()`.
- Device health: `dmz_check_dev()`, `dmz_dev_is_dying()`.
- Metadata flushing: `dmz_flush_metadata()` and internal dirty-block/superblock write helpers.
- Zone mapping/allocation: `dmz_get_chunk_mapping()`, `dmz_put_chunk_mapping()`, `dmz_get_chunk_buffer()`, `dmz_alloc_zone()`, `dmz_free_zone()`, `dmz_map_zone()`, `dmz_unmap_zone()`.
- Reclaim coordination: `dmz_lock_zone_reclaim()`, `dmz_unlock_zone_reclaim()`, `dmz_get_zone_for_reclaim()`.
- Valid-block bitmap operations: `dmz_validate_blocks()`, `dmz_invalidate_blocks()`, `dmz_block_valid()`, `dmz_first_valid_block()`, `dmz_copy_valid_blocks()`, `dmz_merge_valid_blocks()`.

## Control Flow And Behavior

- The on-disk format consists of a superblock, a chunk mapping table, and per-zone valid-block bitmap blocks. Two metadata sets are maintained; the non-primary set acts as a log while updating the primary.
- `dmz_ctr_metadata()` initializes locks/lists/xarray, reports or emulates zones, loads the best superblock set, marks metadata zones, loads the mapping table, registers a shrinker for cached metadata blocks, and prints geometry.
- Zone discovery sets `DMZ_RND`, `DMZ_SEQ`, or `DMZ_CACHE`, records write-pointer block offsets for sequential zones, marks offline/read-only zones, detects the primary superblock zone, and handles regular-device cache zones in multi-device configurations.
- `dmz_load_sb()` reads primary and secondary superblocks, validates magic/version/checksum/position/UUID/label/device UUIDs, recovers a bad set from the good set, and selects the highest generation as primary. Version 2 also checks tertiary superblocks on additional zoned devices.
- Metadata blocks are cached in an RB tree by metadata block number. Reads insert blocks in `DMZ_META_READING` state and waiters synchronize on bit wait queues. Dirty blocks sit on `mblk_dirty_list`; clean unused blocks sit on `mblk_lru_list` and can be reclaimed by the shrinker.
- `dmz_flush_metadata()` takes the metadata semaphore for write, serializes with the flush mutex, moves dirty blocks to a local write list, writes them to the secondary/log set, writes that set's superblock, writes the same blocks to the primary set, writes the primary superblock, clears dirty flags, and increments generation. On error it requeues dirty blocks and checks backing-device health.
- `dmz_load_mapping()` reads all mapping blocks, assigns each mapped data zone and optional buffer zone to a chunk, computes zone weights from bitmaps, populates mapped/unmapped lists, reserves configured sequential zones for reclaim, and counts cache/random/sequential zones per device.
- `dmz_get_chunk_mapping()` returns the active data zone for a chunk. Writes to unmapped chunks allocate a cache/random zone and update the mapping. If the mapped zone is under reclaim, it asks reclaim to terminate, waits, and retries. Sequential write-error zones are re-reported and invalidated after the real write pointer if needed.
- `dmz_put_chunk_mapping()` deactivates the data zone after I/O and opportunistically unmaps/frees empty inactive data or buffer zones.
- `dmz_get_chunk_buffer()` allocates a random/cache buffer zone for unaligned writes into a sequential data zone and records it as the mapping's `bzone_id`.
- `dmz_alloc_zone()` removes a zone from the appropriate unmapped list, schedules reclaim for normal allocations, can search other devices or reserved sequential zones for reclaim allocations, and skips offline/metadata zones. `dmz_free_zone()` resets sequential zones and returns them to the correct free/reserved list.
- Bitmap functions validate/invalidate ranges, find valid extents, copy/merge validity maps during reclaim, and keep each zone's `weight` in sync with set bits.
- `dmz_resume_metadata()` re-reports every zone and verifies that sequential write pointers match the saved metadata state, invalidating blocks beyond a changed write pointer.

## State And Data Structures

- `struct dmz_metadata` stores device array, label/UUID, zone/block geometry, counts, zone xarray, two superblock descriptors, metadata-block cache state, locks, mapping blocks, zone lists, counters, reserved sequential zones, and waitqueue for free zones.
- `struct dmz_super` is the on-disk superblock with magic/version/generation, block counts, mapping/bitmap sizes, label/UUIDs, and CRC.
- `struct dmz_map` maps each logical chunk to a data zone and optional buffer zone.
- `struct dmz_mblock` caches one 4 KiB metadata block with RB/list linkage, refcount, state bits, page, and data pointer.
- `struct dm_zone` is defined in `dm-zoned.h` and holds zone type/state flags, write pointer, validity weight, mapped chunk, buffer/data peer, refcount, and device pointer.
- Lists divide zones by cache/random/sequential, mapped/unmapped, reserved, and LRU order for reclaim selection.

## Dependencies

- Linux block zone APIs for zone reports, zone reset, zone conditions/types, device cache flush, and bio submission.
- DM-zoned target/reclaim callbacks through `dm-zoned.h`, especially `dmz_schedule_reclaim()` and backing-device health checks.
- Kernel xarray, RB tree, lists, shrinker, pages, bios, wait-bit primitives, rwsem/mutex/spinlock, CRC32, UUID helpers, and NOIO allocation contexts.

## Risks And Invariants

- The two-set metadata protocol assumes the primary remains clean until the log/secondary set is fully durable.
- `mblk_sem` prevents metadata flush from racing with target metadata mutation; `map_lock` protects the mapping table and all zone lists.
- Active zones cannot be reclaimed. Reclaim uses `DMZ_RECLAIM`, zone refcounts, termination bits, and wait queues to avoid moving data under I/O.
- Mapping-table entries, zone `chunk` fields, `bzone` back-pointers, zone list membership, and valid-block weights must remain consistent or reads may return stale data or zeros incorrectly.
- Sequential zone write pointers are authoritative for append-only data placement; write errors trigger re-report and bitmap invalidation to avoid trusting unwritten blocks.
- Regular cache devices in multi-device mode are emulated as cache zones, while tertiary superblocks and offsets bind all devices into one metadata set.
