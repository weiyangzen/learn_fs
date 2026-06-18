# File Research: sources/block-storage/linux-dm/drivers/md/dm-zoned.h

## Scope

This header defines the shared dm-zoned geometry constants, device and zone descriptors, zone state flags/accessors, logging helpers, and cross-file function prototypes used by `dm-zoned-target.c`, `dm-zoned-metadata.c`, and `dm-zoned-reclaim.c`.

## APIs And Constants

- Fixed logical block geometry: 4 KiB `DMZ_BLOCK_SIZE`, block/sector conversion macros, and bio-to-block/chunk helpers.
- Core structs: `struct dmz_dev` and `struct dm_zone`, plus opaque declarations for `dmz_metadata` and `dmz_reclaim`.
- Device flags: `DMZ_BDEV_DYING`, `DMZ_CHECK_BDEV`, `DMZ_BDEV_REGULAR`.
- Zone flags: cache/random/sequential type, offline/read-only condition, metadata/data/buffer/reserved use, reclaim state, sequential write error, and reclaim termination.
- Accessor macros: `dmz_is_cache()`, `dmz_is_rnd()`, `dmz_is_seq()`, `dmz_is_empty()`, `dmz_is_offline()`, `dmz_is_readonly()`, `dmz_in_reclaim()`, `dmz_is_meta()`, `dmz_is_buf()`, `dmz_is_data()`, `dmz_weight()`, and others.
- Metadata API prototypes for construction, locking, flushing, geometry, mapping/allocation, reclaim selection, and valid-block bitmap operations.
- Reclaim API prototypes for construction, suspend/resume, bio accounting, and scheduling.
- Target health prototypes: `dmz_bdev_is_dying()` and `dmz_check_bdev()`.
- Inline zone refcount helpers: `dmz_activate_zone()`, `dmz_deactivate_zone()`, and `dmz_is_active()`.

## State And Data Structures

- `struct dmz_dev` describes one backing device with block device pointer, metadata/reclaim back-pointers, name/UUID, capacity, index, zone count/offset, flags, zone size, and mapped/unmapped random/sequential zone lists and counters.
- `struct dm_zone` describes one logical dm-zoned zone with list linkage, parent device, flags, activation refcount, global zone id, write-pointer block, valid-block weight, mapped chunk id, and optional buffer/data peer pointer.
- A sequential data zone's `bzone` points to its random/cache buffer zone; a buffer zone's `bzone` points back to the data zone.

## Dependencies

- Linux block, Device Mapper, kcopyd, list, spinlock, mutex, workqueue, rwsem, RB tree, radix tree, and shrinker headers.
- The implementation files rely on these declarations to avoid circular dependencies among target, metadata, and reclaim code.

## Risks And Invariants

- All dm-zoned code assumes a 4 KiB block size regardless of backing-device sector size.
- Zone flags are bit positions in `unsigned long flags`; flag order is part of the local ABI between the header and implementation files.
- `dmz_deactivate_zone()` also accounts target activity to reclaim before decrementing the zone refcount, so callers should use the inline helper rather than raw atomic operations.
- The `bzone` bidirectional relationship must be maintained consistently by metadata mapping/unmapping and reclaim.
