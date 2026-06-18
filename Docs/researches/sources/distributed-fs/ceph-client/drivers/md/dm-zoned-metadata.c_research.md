# sources/distributed-fs/ceph-client/drivers/md/dm-zoned-metadata.c

## Purpose

`dm-zoned-metadata.c` owns the persistent and in-memory metadata model for the `dm-zoned` target. It discovers zones, validates and recovers superblocks, caches metadata blocks, loads the chunk-to-zone mapping table, tracks per-zone valid-block bitmaps and weights, manages free/mapped/reserved zone lists, arbitrates reclaim locks, and exposes mapping operations used by target I/O and reclaim code.

## Important APIs, Types, and Functions

- On-disk structures: `struct dmz_super` stores magic, metadata version, generation, metadata sizes, chunk count, labels, UUIDs, and CRC; `struct dmz_map` stores a data zone and optional buffer zone per chunk.
- In-memory structures: `struct dmz_metadata` stores device array, geometry, counts, xarray of `struct dm_zone`, two superblock sets, metadata block cache, zone map lock, map block array, zone lists, and wait queue for free zones. `struct dmz_mblock` caches a metadata block in an rbtree/LRU/dirty list.
- Constructor and destructor: `dmz_ctr_metadata()` initializes descriptors, loads superblocks and mappings, registers the shrinker, and reports geometry. `dmz_dtr_metadata()` frees shrinker, metadata blocks, mappings, and zones.
- Persistence path: `dmz_flush_metadata()`, `dmz_log_dirty_mblocks()`, `dmz_write_dirty_mblocks()`, `dmz_write_sb()`, `dmz_recover_mblocks()`, `dmz_load_sb()`.
- Mapping and bitmap paths: `dmz_get_chunk_mapping()`, `dmz_put_chunk_mapping()`, `dmz_get_chunk_buffer()`, `dmz_alloc_zone()`, `dmz_free_zone()`, `dmz_validate_blocks()`, `dmz_invalidate_blocks()`, `dmz_block_valid()`, `dmz_first_valid_block()`.

## Control Flow

Construction allocates metadata, initializes locks/lists, and calls `dmz_init_zones()`. Single-device mode reports hardware zones and chooses the first conventional zone for metadata. Multi-device mode emulates cache zones on the regular first device and reports real zones on later devices.

`dmz_load_sb()` reads/checks primary and secondary sets, recovers a bad set from a good set, and chooses the highest generation. Version 2 additionally checks tertiary superblocks for later devices. `dmz_load_mapping()` loads map blocks, marks mapped data/buffer zones, computes valid-block weights from bitmaps, and classifies the rest as free cache/random/sequential/reserved zones.

The I/O path calls `dmz_get_chunk_mapping()` to find or allocate a chunk zone. Reclaiming zones cause a wait-and-retry. `dmz_put_chunk_mapping()` deactivates zones and frees empty unbuffered mappings.

## State and Persistence Behavior

Metadata is stored as two complete sets: superblock, chunk map blocks, and bitmap blocks. Flush is log-first: write dirty blocks to the non-primary set, advance that superblock, write dirty blocks to the primary set, advance the primary superblock, then clear dirty bits and increment `sb_gen`. Persistent validity is represented by per-zone bitmaps; list membership, weights, and flags are reconstructed in memory.

## Dependencies and Integration Points

It depends on `dm-zoned.h`, block zoned reporting/reset APIs, xarray/rbtree/list/shrinker primitives, bio metadata I/O, CRC32, UUID helpers, and health/reclaim callbacks. `dm-zoned-target.c` uses it for every read/write/discard decision; `dm-zoned-reclaim.c` uses it for zone selection, bitmap copy/merge, remapping, and durable flush.

## Risks and Test Signals

Flush ordering is critical for recovery. Refcount/reclaim/map lock ordering is subtle, especially when foreground I/O interrupts reclaim. Multi-device label/UUID mismatches, runt zones, write-pointer error repair, free-zone exhaustion, metadata cache shrinker behavior, and injected I/O failures are high-value tests.
