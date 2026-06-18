# sources/cloud-native/nydus/service/src/block_device.rs

## Purpose
`block_device.rs` presents a RAFSv6 image as a block-addressable device. It maps bootstrap metadata, holes, and data blobs into a single logical block address space so the image can be read as an EROFS-compatible disk or exported to NBD/UFFD.

## Important APIs, Types, And Functions
`BlockRange` represents `Hole`, `MetaBlob`, or `DataBlob`. `BlockDevice::new()` creates a private `BlobCacheMgr` from a `BlobCacheEntry`; `new_with_cache_manager()` builds the interval map from an existing cache manager. Public accessors include `meta_blob_id()`, `cache_mgr()`, `blocks()`, `block_size()`, `size_to_blocks()`, and `blocks_to_size()`. Read paths are `async_read()` and `fetch_ranges()`. `probe_blob_ranges()` identifies already cached data blob chunk ranges. `export()` and `do_export()` write the logical device to a raw disk image and optionally append dm-verity hashes.

## Control Flow
Construction inserts an initial free interval, loads the meta blob config, maps the metadata blob at the beginning, then iterates referenced data blobs. It inserts explicit `Hole` ranges when mapped block addresses leave gaps, validates TARFS mode consistency, computes block counts from blob sizes, creates `DataBlob` wrappers, and updates the interval tree. `async_read()` walks intervals covering the requested block range, zero-fills holes, reads metadata at absolute offsets, and reads data blobs at offsets relative to their mapped range. `fetch_ranges()` returns fd/offset/len/block-offset tuples, either fetching data first or probing readiness only. `export()` partitions the device into batches across up to 32 threads, each with a tokio-uring runtime, and optionally records Merkle leaf digests.

## State, Persistence, And Dependencies
The block layout is in-memory: `blocks`, `blob_id`, `cache_mgr`, `IntervalTree<BlockRange>`, and `is_tarfs_mode`. Reads and exports persist only through the output disk file and through cache population performed by `DataBlob::async_fetch()`. Dependencies include RAFS v6 layout constants, `dbs_allocator::IntervalTree`, `tokio_uring`, Nydus cache wrappers, and dm-verity helpers.

## Integration Points
`BlockDevice` is the common storage engine for `block_nbd.rs` and `block_uffd.rs`. It relies on `BlobCacheMgr` for scoped blob configuration and on RAFS `RafsBlobExtraInfo::mapped_blkaddr` for the logical disk map.

## Risks
`size_to_blocks()` truncates rather than rounds, so callers must pass aligned sizes. `fetch_ranges()` skips holes, which is correct for mmap-style zero-fill users but requires callers to handle missing ranges. Multi-threaded export rebuilds `BlockDevice` in each thread and shares a locked verity generator, so performance depends on metadata/cache construction and lock granularity. Output open uses `truncate(false)`, leaving stale bytes if overwriting a larger previous file.

## Test Signals
Tests cover construction, invalid ids, block-size conversion, async reads across metadata/hole/data/out-of-range regions, export digest stability for one and two threads, `fetch_ranges()` invalid/out-of-range/meta/data/hole/probe cases, and zero-block reads. Coverage is fixture-based and does not include TARFS images.
