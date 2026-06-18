# sources/distributed-fs/ceph/src/osd/ECExtentCache.cc

## Purpose

Implements the modern EC extent cache used by `ECCommon::RMWPipeline` to avoid rereading shard extents for overlapping or sequential partial writes. It combines per-object active cache lines with a per-OSD-shard LRU of recently used lines and coordinates cache reads, invalidation, and write updates without reordering IO.

## Important APIs, Types, and Functions

Important methods are `Object::request`, `send_reads`, `read_done`, `insert`, `write_done`, `invalidate`, `get_cache`, `ECExtentCache::prepare`, `execute`, `read_done`, `write_done`, `on_change`, `on_change2`, `idle`, `LRU::add`, `LRU::find`, `LRU::remove_object`, `LRU::free_maybe`, `LRU::discard`, and `Op::get_pin_eset`. `check_seset_empty_for_range()` asserts no outstanding request overlaps a line being erased.

## Control Flow and Data Flow

Callers first `prepare()` cache ops, then `execute()` them. `Object::request()` pins line-aligned ranges spanning reads and writes, revives lines from the LRU or creates empty lines, subtracts cached/known-zero regions from read requests, coalesces backend reads, and updates `do_not_read` for in-flight reads, writes, and append holes. `send_reads()` allows at most one backend read per object. When reads finish, `read_done()` marks waiting ops ready, inserts returned shard extent maps into line caches, and `cache_maybe_ready()` completes front-of-queue ops once their reads are cached. `write_done()` inserts generated write buffers into the cache and runs on-write callbacks.

Invalidating operations wait for in-flight reads to finish, clear active lines and LRU entries for the object, reset request state, mark the invalidation honored, and replay outstanding ops for that object so their reads are planned against the empty cache.

## State and Persistence Behavior

The cache is volatile only. State includes `objects`, per-object `requesting`, `do_not_read`, `reading_ops`, `requesting_ops`, weak line map, active IO counters, object sizes, `waiting_ops`, and LRU `map`/`lru`/`size`. Mempool counters track cache item and byte usage. `on_change()` cancels waiting callbacks and clears queued reads; `on_change2()` discards the LRU and asserts all active objects and IO have drained.

## Dependencies and Integration Points

It depends on `ECExtentCache.h`, `ECUtil`, `shard_extent_set_t`, `shard_extent_map_t`, `extent_set`, `extent_map`, mempool accounting, and the backend-supplied `BackendReadListener`. In practice `ECCommon::RMWPipeline` implements backend reads by calling `objects_read_and_reconstruct_for_rmw()`.

## Risks and Edge Cases

Invalidation is the highest-risk path: inserting a late read after clearing cache would corrupt later writes, so invalidating ops block until the object's current read completes. Line ownership relies on `shared_ptr`/`weak_ptr` lifetimes and `Line::~Line()` moving data to the LRU; active IO counters and op destructors must stay balanced. Appends use object-size masks to treat newly grown holes as zero, so projected size drift can cause under-reads. `LRU::free_maybe()` assumes `max_size < size` implies a non-empty list.

## Test Signals

Test cache miss then read completion, cache hit with no backend read, overlapping writes, sequential writes crossing 32 KiB/chunk line boundaries, append holes, invalidating op replay, late read completion around invalidation, LRU revive/evict/remove/discard, mempool accounting, `on_change()` callback cancellation, and `on_change2()` idle assertions.
