# sources/distributed-fs/ceph-client/include/trace/events/bcache.h

## Purpose
`bcache.h` defines tracing for the bcache block cache: request submission/completion, bypass decisions, reads/writes, journal pressure, btree operations, allocator behavior, garbage collection, and background writeback.

## Important APIs, types, and functions
Event classes include `bcache_request`, `bcache_bio`, `bkey`, `btree_node`, `cache_set`, and `btree_split`. Events include `bcache_request_start/end`, `bcache_bypass_*`, `bcache_read`, `bcache_write`, `bcache_read_retry`, `bcache_cache_insert`, journal events, btree read/write/alloc/free/split/compact/root/keyscan/insert events, GC events, allocator invalidate/alloc/fail events, and writeback collision events.

## Control flow
Tracepoints are arranged by bcache subsystem files: request path, journal, btree, allocator, and background writeback. Request and bio events use block-layer helpers to snapshot device, sector, size, and rwbs flags; btree and key events extract bucket, key inode/offset/size/dirty state; allocator events snapshot cache bucket and free-list pressure.

## State and persistence behavior
The header stores no state. Event records snapshot bio positions, cache-set UUIDs, bkey contents, btree node bucket/level, bucket offsets, free FIFO sizes, and ref/operation status.

## Dependencies and integration points
It depends on bcache internal types/macros (`struct bcache_device`, `cache_set`, `bkey`, `btree`, `cache`, `KEY_*`, `PTR_BUCKET_NR`, `GC_SECTORS_USED`) and block helpers such as `blk_fill_rwbs()` and `bio_dev()`. It integrates bcache diagnostics with block tracing.

## Risks and test signals
Risks include assumptions about bcache internal layout, confusing `bcache_write` print text naming writeback as hit, and pointer/bucket identity being transient. Test signals are cache hit/miss workloads, sequential/congested bypass, journal-full injection, btree split/GC scenarios, allocation failure pressure, and writeback collision traces.
