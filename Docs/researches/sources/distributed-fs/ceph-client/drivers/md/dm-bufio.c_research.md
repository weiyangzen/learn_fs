# sources/distributed-fs/ceph-client/drivers/md/dm-bufio.c

## Purpose
`dm-bufio.c` implements Device Mapper's buffered block I/O cache library. It gives metadata-heavy DM targets a block-oriented cache on top of a `block_device`, with read, get-if-present, new-buffer, prefetch, dirty tracking, writeback, discard/flush helpers, shrinker integration, and global cache-size enforcement.

## Important APIs, Types, and Functions
The central types are private `struct dm_bufio_client`, private `struct dm_buffer`, `struct dm_buffer_cache`, per-bucket `struct buffer_tree`, and an internal clock-style `struct lru`. Exported API includes `dm_bufio_client_create()`, `dm_bufio_client_destroy()`, `dm_bufio_client_reset()`, `dm_bufio_read()`, `dm_bufio_read_with_ioprio()`, `dm_bufio_get()`, `dm_bufio_new()`, `dm_bufio_prefetch()`, `dm_bufio_prefetch_with_ioprio()`, `dm_bufio_release()`, `dm_bufio_mark_buffer_dirty()`, `dm_bufio_mark_partial_buffer_dirty()`, `dm_bufio_write_dirty_buffers_async()`, `dm_bufio_write_dirty_buffers()`, `dm_bufio_issue_flush()`, `dm_bufio_issue_discard()`, `dm_bufio_forget()`, `dm_bufio_forget_buffers()`, `dm_bufio_set_minimum_buffers()`, `dm_bufio_get_device_size()`, and accessors for block number, data, aux data, client, block size, and dm-io client.

## Control Flow
Clients are created with a target block device, block size, reserve count, optional auxiliary per-buffer data, and optional callbacks. `new_read()` is the main read/new/get path: it first checks the rb-tree bucket without taking the client mutex, allocates or evicts a buffer if needed, inserts it with `B_READING` set for disk reads, submits I/O through `submit_io()`, waits unless doing `dm_bufio_get()`, and returns the data pointer plus a held `struct dm_buffer`. Dirty writes go through `dm_bufio_mark_partial_buffer_dirty()`, which moves buffers to the dirty LRU and records the dirty byte range. Writeback batches dirty buffers into a local list, submits writes under a plug, waits for `B_WRITING` to clear, moves clean buffers back to the clean LRU, and finally issues a flush for synchronous writeback.

## State and Persistence
Runtime state is in the client cache: rb-trees indexed by block, clean and dirty clock LRUs, hold counts, last access time, dirty/write byte ranges, and state bits `B_READING`, `B_WRITING`, and `B_DIRTY`. Persistent effects are only the block-device writes, flushes, and discards emitted by clients; the cache contents themselves are volatile. Module parameters control global cache size and retained bytes, while read-only counters expose current, peak, and allocator-class memory usage.

## Dependencies and Integration Points
The file depends on `linux/dm-bufio.h`, Device Mapper core logging, `dm-io`, block bio submission, workqueues, shrinkers, rbtrees, stack tracing in debug builds, and jump labels for no-sleep clients. DM metadata users such as persistent-data and cache metadata use bufio as their block cache. I/O uses direct bios when the buffer is not vmalloc-backed and small enough; otherwise it falls back to `dm_io()`.

## Risks and Edge Cases
Correctness depends on hold-count discipline: callers must release every buffer and must not dirty buffers still being read. `dm_bufio_get()` and prefetch intentionally avoid waiting for in-flight reads because they may be called from request context and waiting could deadlock. No-sleep clients switch from semaphores/mutexes to spinlocks and cannot evict buffers that require I/O waits. Shrinker and global cleanup race with normal use, so eviction predicates must reject held, dirty, writing, or reading buffers appropriately. Partial write ranges are aligned to at least 4 KiB and the physical block size, so wrong dirty ranges can write more data than the caller expects.

## Test Signals
Useful signals include repeated read/new/release cycles without leaked buffers, dirty partial writes followed by flush with correct on-disk data, prefetch not blocking request-context paths, shrinker-triggered eviction under memory pressure, no-sleep client behavior, discard and flush error propagation, module unload leak warnings staying quiet, and kmem/vmalloc allocation counters returning to zero after all clients are destroyed.
