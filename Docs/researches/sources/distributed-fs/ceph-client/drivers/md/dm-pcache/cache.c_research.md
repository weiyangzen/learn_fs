
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache.c

## Purpose
Initializes and tears down the core pcache cache state: cache metadata discovery, segment initialization, tail/head positions, request key trees, per-CPU data heads, writeback/GC scheduling, and global cache-key slab setup.

## Important APIs, Types, And Functions
`key_cache` is the global slab for `pcache_cache_key`. `cache_info_init()` finds the latest persisted `pcache_cache_info`, validates immutable options such as data CRC, or creates defaults. `cache_info_write()` writes the next indexed metadata copy with CRC/sequence. `cache_pos_encode()`/`cache_pos_decode()` persist and recover key/dirty tail positions. `cache_init()`, `cache_segs_init()`, `cache_tail_init()`, and `cache_init_req_keys()` allocate runtime structures, initialize segments, decode or create tail positions, build request trees/ksets, allocate per-CPU data heads, and replay persisted keys. `pcache_cache_start()` wires cache/backing/cache-dev state, starts writeback and GC, marks init done, and persists cache info. `pcache_cache_stop()` flushes ksets, stops GC/writeback, destroys trees, and frees memory.

## Control Flow
Startup first allocates arrays/bitmaps/locks/work, points metadata addresses into the DAX cache device, initializes cache info, walks segment chains, initializes tails, replays keysets into rbtrees, initializes writeback, writes `INIT_DONE`, and queues GC. Shutdown flushes pending keysets, cancels GC, flushes clean work, exits writeback, destroys request keys if initialized, and frees segment state.

## State And Persistence
Persistent metadata includes redundant cache-info records, cache control tail positions, segment metadata, and keysets stored in DAX media. Runtime state includes segment arrays, bitmaps, rbtrees, per-CPU allocation heads, locks, work items, and writeback/GC contexts.

## Dependencies And Integration Points
Depends on `cache_dev` DAX mappings, backing-device size, segment helpers, metadata CRC helpers from pcache internals, key replay in `cache_key.c`, request handling in `cache_req.c`, writeback, and GC.

## Risks
Startup ordering is critical: tail decode and key replay depend on segments being initialized. Data CRC mode cannot change after formatting. New-cache initialization reserves segment 0 for metadata and writes redundant tail metadata. Failure cleanup must match partially initialized structures. `n_subtrees` scales with backing size and can become large.

## Test Signals
Test first-format and existing-cache starts, data_crc option mismatch, corrupted cache info/tails, segment-chain errors, key replay failures, low-memory cleanup paths, writeback init failure, clean shutdown with pending ksets, GC scheduling, and `pcache_cache_set_gc_percent()` bounds/persistence.
