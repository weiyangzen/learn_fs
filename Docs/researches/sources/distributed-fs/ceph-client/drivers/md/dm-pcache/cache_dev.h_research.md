
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_dev.h

## Purpose
Declares the pcache DAX cache-device layout, superblock format, runtime cache-device state, and cache-device management APIs.

## Important APIs, Types, And Functions
Defines `PCACHE_MAGIC`, superblock/cache-info/cache-control/segment offsets and sizes, minimum cache device size, 16 MiB segment size, and address macros such as `CACHE_DEV_SB()`, `CACHE_DEV_CACHE_INFO()`, `CACHE_DEV_CACHE_CTRL()`, `CACHE_DEV_SEGMENTS()`, and `CACHE_DEV_SEGMENT()`. `PCACHE_SB_F_BIGENDIAN` records media endianness. `struct pcache_sb` stores CRC, flags, magic, and segment count. `struct pcache_cache_dev` stores flags, segment count, DAX mapping, vmap mode, dm device, segment lock, and segment bitmap. APIs include `cache_dev_start()`, `cache_dev_stop()`, `cache_dev_zero_range()`, and `cache_dev_get_empty_segment_id()`.

## Control Flow
No runtime flow is implemented here. Other pcache files use these macros to locate persistent metadata and segment data within the mapped DAX device.

## State And Persistence
The header defines the persistent layout root for pcache. Offsets reserve space for redundant metadata and then segment data. Runtime state mirrors the mapped device and allocation bitmap.

## Dependencies And Integration Points
Depends on device-mapper device references, DAX-capable lower devices, and pcache internal ownership macros. `cache.c`, `cache_key.c`, `cache_gc.c`, and segment code use the layout macros to persist and replay cache state.

## Risks
Offset and size definitions are on-media format contracts. Changing them without migration would make existing cache devices unreadable. Segment size and minimum size determine capacity and metadata overhead. Endianness flags must be validated before interpreting metadata.

## Test Signals
Validate layout offsets, segment address calculations, superblock CRC coverage, endian flag handling, minimum-size enforcement, and successful compilation of all users of the runtime struct and APIs.
