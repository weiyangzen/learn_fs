# File Research: sources/block-storage/lvm2/lib/device/bcache.h

## Purpose
Declares the block-cache API, IO-engine abstraction, cache block type, byte-range utility helpers, and fd-table helper functions.

## Public Surface
- IO engines: `create_async_io_engine()`, `create_sync_io_engine()`.
- Cache lifecycle: `bcache_create()`, `bcache_destroy()`.
- Geometry: `bcache_block_sectors()`, `bcache_nr_cache_blocks()`, `bcache_max_prefetches()`.
- Cache access: `bcache_prefetch()`, `bcache_get()`, `bcache_put()`.
- Persistence/invalidation: `bcache_flush()`, `bcache_invalidate()`, `bcache_invalidate_di()`, `bcache_abort_di()`.
- Byte helpers: read, write, zero, set, prefetch, and invalidate byte ranges.
- Boundary and fd helpers: `bcache_set_last_byte()`, `bcache_unset_last_byte()`, `bcache_set_fd()`, `bcache_clear_fd()`, `bcache_change_fd()`.

## Data Model
Clients may access only `struct block` fields `di`, `index`, and `data`; the remaining fields are internal cache state. `GF_ZERO` implies dirty access and can avoid a read for full-block overwrites. `GF_DIRTY` marks a block for later writeback.

## Risk Notes
The header documents that invalidating a held block fails, and `bcache_abort_di()` aborts if any blocks for the descriptor are still held.
