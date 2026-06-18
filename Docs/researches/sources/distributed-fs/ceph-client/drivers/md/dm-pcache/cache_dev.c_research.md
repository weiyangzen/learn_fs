
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_dev.c

## Purpose
Initializes and manages the persistent-memory/DAX cache device used by pcache. It maps the DAX device into kernel virtual memory, formats or validates the pcache superblock, zeros metadata areas on first format, and tracks free cache segments.

## Important APIs, Types, And Functions
`cache_dev_dax_init()` validates minimum size, tries `dax_direct_access()` for a contiguous mapping, and falls back to `build_vmap()` for non-contiguous PFNs. `cache_dev_dax_exit()` unmaps vmap fallback. `cache_dev_zero_range()` zeroes and flushes DAX memory. Superblock helpers `sb_read()`, `sb_write()`, `sb_init()`, and `sb_validate()` handle magic, CRC, endian flags, segment count, and metadata zeroing. `cache_dev_start()` maps DAX, reads/formats/validates the superblock, initializes segment bitmap, and writes the new superblock after successful init. `cache_dev_stop()` frees bitmap and mapping. `cache_dev_get_empty_segment_id()` allocates a free segment id under `seg_lock`.

## Control Flow
Startup maps the full DAX block device, reads the superblock with machine-check-safe copy, formats if magic is zero, validates magic/CRC/endian, allocates the segment bitmap, and persists the superblock only after all validation/initialization succeeds. Formatting computes segment count from bytes after metadata offsets and zeroes cache-info/control metadata regions.

## State And Persistence
Persistent state includes `pcache_sb` at `PCACHE_SB_OFF`, cache-info/control areas, and data segments. Runtime state includes mapping pointer, `use_vmap`, segment count, segment bitmap, dm device, and segment lock.

## Dependencies And Integration Points
Depends on DAX direct access/read locking, PFN validity, vmap/vunmap, persistent-memory flush primitives, machine-check-safe copies, block device size helpers, CRC32C, and pcache cache metadata layout macros from `cache_dev.h`/`cache.h`.

## Risks
The full-device DAX mapping assumes stable direct access during target lifetime. Endianness is a format constraint; moving media across endian types is rejected. Formatting occurs when magic is zero and destroys prior metadata areas. Segment allocation only sets bits; freeing is handled by cache GC/segment code. `pfn_valid()` rejection limits device compatibility.

## Test Signals
Test too-small devices, contiguous and vmap DAX mappings, `dax_direct_access()` errors, invalid PFNs, blank-device format, corrupted magic/CRC/endian flags, segment count computation, metadata zeroing/flushing, bitmap allocation failure cleanup, segment allocation exhaustion, and stop/unmap behavior.
