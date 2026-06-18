# sources/distributed-fs/ceph-client/drivers/md/dm-zoned.h

## Purpose

`dm-zoned.h` is the shared internal interface for the `dm-zoned` target, metadata manager, and reclaim worker. It defines fixed 4 KiB block geometry, device and zone descriptors, zone state flags, logging helpers, and cross-file function prototypes.

## Important APIs, Types, and Functions

Geometry macros define 4 KiB block size and sector/block conversions (`dmz_blk2sect`, `dmz_sect2blk`, `dmz_bio_block`, `dmz_bio_blocks`, `dmz_bio_chunk`, `dmz_chunk_block`). `struct dmz_dev` represents a backing device with capacity, zone geometry, zone lists, metadata/reclaim backpointers, UUID, and health flags. `struct dm_zone` represents one zone with flags, active refcount, id, write pointer, valid-block weight, mapped chunk, and optional buffer-zone pairing. Inline helpers activate/deactivate zones and test active state.

## Control Flow

The header has little runtime control flow beyond active refcount helpers. Its prototypes connect target I/O to metadata mapping/bitmap operations, reclaim to metadata allocation/remapping/flush, and metadata to target backing-device health checks.

## State and Persistence Behavior

It declares in-memory state containers but does not persist data. `struct dm_zone` mirrors persistent mapping and bitmap state plus transient activity/reclaim bits. `struct dmz_dev` stores transient zone counters/lists and persistent UUID identity loaded from metadata.

## Dependencies and Integration Points

The header includes Linux block, device-mapper, kcopyd, list, lock, workqueue, rwsem, rbtree, radix-tree, and shrinker declarations. It is included by `dm-zoned-target.c`, `dm-zoned-metadata.c`, and `dm-zoned-reclaim.c`.

## Risks and Test Signals

The fixed 4 KiB block contract and shared flag layout are global assumptions. `dmz_deactivate_zone()` assumes reclaim state exists. Test through compile coverage, zone-boundary conversions, 4 KiB alignment behavior, active refcount and reclaim exclusion, and shared flag transitions.
