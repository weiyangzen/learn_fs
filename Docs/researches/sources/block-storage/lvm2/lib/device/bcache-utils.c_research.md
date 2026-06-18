# File Research: sources/block-storage/lvm2/lib/device/bcache-utils.c

## Purpose
Provides byte-range convenience operations on top of block-granular `bcache` APIs.

## Main APIs
- `bcache_prefetch_bytes()` prefetches every cache block intersecting a byte range.
- `bcache_read_bytes()` reads a byte range, handling unaligned leading/trailing block offsets.
- `bcache_write_bytes()` writes arbitrary byte ranges.
- `bcache_zero_bytes()` zeroes arbitrary byte ranges.
- `bcache_set_bytes()` fills a byte range with a byte value.
- `bcache_invalidate_bytes()` invalidates all blocks overlapping a byte range.

## Core Behavior
`byte_range_to_block_range()` converts byte ranges to cache-block indices and rejects `start + len` overflow. Reads prefetch the full range, then copy slices out of `bcache_get()` blocks. Writes/zeroes/sets share `_update_bytes()`, which handles a possible partial first block, whole middle blocks, and a partial final block.

Whole-block writes and fills use `GF_ZERO` to avoid reading a block that will be fully overwritten; partial updates use `GF_DIRTY`, forcing an existing block read before modification.

## Integration
Used by higher-level device IO wrappers that need byte-addressed reads/writes over the block cache.

## Risk Notes
The helpers assume `bcache_block_sectors(cache) << 9` fits the arithmetic being used. Partial writes require successful reads, so an unreadable sector can prevent a small overwrite even if the caller only wants to change part of the block.
