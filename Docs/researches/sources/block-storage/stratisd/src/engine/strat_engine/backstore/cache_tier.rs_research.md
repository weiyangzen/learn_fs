# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/cache_tier.rs

This file implements `CacheTier<B>`, the backstore layer that manages block devices dedicated to dm-cache. It owns a `BlockDevMgr<B>`, cache data segments, and cache metadata segments. The implementation is generic over v1/v2 blockdevs for setup, serialization, destruction, partitioning, and invariants, with version-specific add/lookup wrappers.

`MAX_CACHE_SIZE` caps the cache subdevice at 32 TiB. The comments describe this as temporary, tied to the cache block size and the fixed 1 Mi-sector metadata subdevice size. Both v1 and v2 `add()` methods initialize new cache blockdevs through their manager, reject additions that would exceed the maximum cache size, roll back added blockdevs by removing/wiping them on that error, then allocate all newly available free space to the cache subdevice. They currently never grow the metadata subdevice and return `(cache_changed=true, meta_changed=false)`.

`setup()` reconstructs an existing cache tier from saved metadata. It requires the block manager to have no unallocated space, builds a uuid-to-device map, maps saved metadata and cache segment records back to dm target segments, and stores them as `AllocatedAbove`. This guards against metadata corruption where cache devices have free space that is not represented in saved allocations.

`new()` creates a fresh cache tier by allocating a fixed 1 Mi-sector metadata subdevice and all remaining available space to the cache subdevice. It asserts devices are large enough, destroys all newly initialized cache blockdevs if the resulting cache would exceed `MAX_CACHE_SIZE`, and returns the allocated segment sets.

`destroy()` wipes all managed cache blockdevs. `partition_cache_by_use()` separates blockdevs by whether their allocator has allocations beyond metadata. The test-only invariant requires all cache-tier blockdevs to be in use and to match the union of cache and meta segment UUIDs. Serialization records cache allocs first, metadata allocs second, and blockdev records.

Tests for both v1 and v2 create a cache tier, verify all free space is consumed, add more cache devices, verify size/accounting changes, and destroy the tier.
