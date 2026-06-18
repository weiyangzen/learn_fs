# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/segment.c

## Purpose
Implements generic data movement between a pcache segment's pmem data area and block-layer bios, plus segment object initialization. It is the low-level copy layer beneath cache hits, cache fills, and writes into the persistent cache.

## Important APIs, Types, And Functions
`segment_copy_to_bio()` copies from `segment->data + data_off` into a bio iterator using `_copy_mc_to_iter()` so pmem read faults can be detected. `segment_copy_from_bio()` copies from a bio iterator into the segment using `_copy_from_iter_flushcache()` and persists with `pmem_wmb()`. `pcache_segment_init()` sets segment info type, owning cache device, physical segment id, data size, and data pointer according to `struct pcache_segment_init_options`.

## Control Flow
Both copy functions build an `iov_iter` from the current bio vector state and advance it by `bio_off` when requested. They require the low-level copy to transfer exactly `data_len`; otherwise they return `-EIO`. Initialization computes the usable data region as `PCACHE_SEG_SIZE - data_off`, allowing cache-specific segment headers/control areas to live before user data.

## State And Persistence
The copy-to-bio path reads persistent memory but does not mutate state. The copy-from-bio path writes into the DAX/pmem mapping with cache-line flushes and a write memory barrier, making data durable before upper metadata points to it. The segment object itself is volatile and points into the cache-device mapping.

## Dependencies And Integration Points
The file depends on Linux DAX/iov iterator helpers, `pcache_internal.h`, `cache_dev.h`, and `segment.h`. Higher cache request code uses these functions to serve reads from cache and populate cache data from writes or backing reads. Segment type metadata is defined in `segment.h` and later persisted by cache-segment code.

## Risks
The functions trust callers to pass valid offsets and lengths within the segment data area. Bio iterator setup depends on the current `bi_iter` fields, so incorrect `bio_off` can copy the wrong range. Partial copies are reported as `-EIO`, but already-written bytes may remain in pmem; callers must publish metadata only after successful full writes.

## Test Signals
Exercise copies with multi-segment bios, nonzero `bio_off`, boundary-length requests, pmem copy faults, and writes followed by reload/readback. Tests should verify that metadata is not committed when `segment_copy_from_bio()` returns an error.
