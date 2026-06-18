# sources/distributed-fs/ceph-client/drivers/md/dm-writecache.c

## Purpose
`dm-writecache.c` implements the `writecache` device-mapper target, a persistent write-back cache in front of an origin block device. It supports persistent-memory (`p`) mode and SSD (`s`) mode, tracks cached blocks by original sector, commits metadata with sequence counts, services read/write/flush/discard bios, and asynchronously writes cached data back to the origin.

## Important APIs, Types, and Functions
Important persistent structures are `wc_memory_superblock` and `wc_memory_entry`. Runtime structures include `wc_entry`, `dm_writecache`, `writeback_struct`, and `copy_struct`. Major functions include `persistent_memory_claim()`, metadata accessors, `writecache_flush()`, `writecache_resume()`, `writecache_map_read()`, `writecache_map_write()`, `writecache_map_flush()`, `writecache_map_discard()`, `writecache_map()`, `writecache_end_io()`, endio/writeback thread functions, `writecache_writeback()`, `init_memory()`, `writecache_ctr()`, `writecache_dtr()`, and `writecache_status()`.

## Control Flow
The constructor parses mode, origin/cache devices, block size, and optional watermarks, writeback limits, autocommit, max age, cleaner, FUA, metadata-only, and pause settings. It maps or allocates cache metadata, validates or initializes the persistent superblock, allocates entries, workqueues, threads, mempools, and I/O clients. `writecache_map()` handles flush first, translates sectors to target offsets, enforces cache-block alignment, and dispatches to read/write/discard handlers. Writes allocate or reuse entries, copy data into pmem or remap to SSD cache blocks, and schedule metadata commits. Writeback selects committed LRU entries, groups contiguous runs, submits bios or kcopyd copies, and frees entries after endio.

## State and Persistence Behavior
Persistence is driven by `original_sector` and `seq_count` in cache metadata. Entries with sequence counts older than the superblock sequence are committed; uncommitted entries are flushed then the superblock `seq_count` is advanced. SSD mode uses an in-memory metadata map plus dirty bitmap flushed to the SSD cache device; pmem mode uses cache-line flushes and memory barriers. Resume rebuilds the rbtree/free list, discards incomplete entries, resolves duplicate sectors by newest sequence, and may flush repaired metadata.

## Dependencies and Integration Points
The target depends on device-mapper target APIs, dm-io, dm-kcopyd, dm-io-tracker, workqueues, timers, kthreads, biosets, mempools, DAX/libnvdimm for pmem, copy-machine-check helpers, rbtrees, waitqueues, and block queue-limit stacking. It registers as `writecache` with map, end_io, suspend/resume, message, status, iterate_devices, and io_hints hooks.

## Risks and Test Signals
Risks include metadata commit ordering, data loss on power failure, duplicate-sector resolution, pmem hardware poison handling, writeback races with reads/writes/discards, freelist starvation, and constructor option validation. Tests should cover fresh initialization, resume after partial commits, flush/FUA semantics, cleaner mode, metadata-only mode, pmem and SSD write paths, discard invalidation, low-watermark writeback, max-age writeback, writeback error propagation, status output, and all messages (`flush`, `flush_on_suspend`, `cleaner`, `clear_stats`).
