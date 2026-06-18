# sources/distributed-fs/ceph-client/fs/netfs/buffered_read.c

## Purpose

`buffered_read.c` implements high-level netfs buffered read support. It drives readahead, single-folio reads, deprecated `write_begin` read-for-write preparation, prefetch for writes, and the generic buffered `read_iter` dispatch. The file abstracts the choice among local cache, server download, and zero-fill while using pagecache folios and rolling buffers as I/O destinations.

## Important APIs and Functions

Exported APIs are `netfs_readahead()`, `netfs_read_folio()`, `netfs_write_begin()`, `netfs_prefetch_for_write()`, `netfs_buffered_read_iter()`, and `netfs_file_read_iter()`. The read pipeline uses `struct netfs_io_request`, `struct netfs_io_subrequest`, `struct netfs_inode`, `struct netfs_cache_resources`, `struct readahead_control`, `struct rolling_buffer`, and folio/private state from `internal.h`.

Important internal helpers include `netfs_cache_expand_readahead()`, `netfs_rreq_expand()`, `netfs_begin_cache_read()`, `netfs_prepare_read_iterator()`, `netfs_cache_prepare_read()`, `netfs_read_cache_to_pagecache()`, `netfs_queue_read()`, `netfs_issue_read()`, `netfs_read_to_pagecache()`, `netfs_create_singular_buffer()`, `netfs_read_gaps()`, and `netfs_skip_folio_read()`.

## Control Flow

`netfs_readahead()` allocates a request for the readahead window, offloads collection, begins a cache read operation if possible, lets cache and filesystem expand the window, initializes a rolling destination buffer, then calls `netfs_read_to_pagecache()`. The request is released immediately after submission; completion is handled by the collector path.

`netfs_read_to_pagecache()` is the central slicer. For each remaining range it allocates a subrequest, asks the cache to prepare a read, clamps server reads to the inode zero point and I/O stream limits, optionally calls filesystem `prepare_read`, prepares the iterator over pagecache folios, queues the subrequest on stream 0 under the request lock, and issues cache/server/zero-fill work. On allocation or preparation failure it sets `NETFS_RREQ_ALL_QUEUED`, wakes the collector, and records the first error in `rreq->error`.

`netfs_read_folio()` handles `->read_folio`. Dirty folios with partial streaming-write state go to `netfs_read_gaps()`, which builds a bvec layout that reads only the gaps and discards the dirty middle into a temporary sink folio. Clean non-uptodate folios use a singular rolling buffer, call the central pagecache read path, wait synchronously, and return with the folio unlocked by the collection path.

`netfs_write_begin()` and `netfs_prefetch_for_write()` preload data before a partial buffered write. They avoid reads when a full folio write or beyond-EOF write can safely zero gaps, otherwise they allocate a read-for-write request, mark the folio as not to be unlocked by normal read completion, read into the folio, and wait. `netfs_buffered_read_iter()` gates `filemap_read()` with netfs read locking. `netfs_file_read_iter()` chooses unbuffered/direct read when `IOCB_DIRECT` or `NETFS_ICTX_UNBUFFERED` is set; otherwise it uses the buffered path.

## State and Persistence Behavior

The file mutates in-memory pagecache folios, folio uptodate state, folio dirty/private state, rolling-buffer cursors, request flags, subrequest lists, transferred/submitted positions, and netfs statistics. It does not persist metadata directly. It respects `ctx->zero_point` to synthesize zeros beyond known server data and uses FS-Cache cookies via `fscache_begin_read_operation()` when caching is available.

## Dependencies and Integration Points

The code depends on filesystem-provided `netfs_inode` operations: `issue_read`, optional `prepare_read`, optional `expand_readahead`, and optional `check_write_begin`. It integrates with FS-Cache through `fscache_begin_read_operation()` and cache resource ops `expand_readahead`, `prepare_read`, and `read`. It also relies on netfs object allocation, read collection, retry handling, rolling-buffer helpers, iterator limiting, VFS `filemap_read()`, readahead APIs, and folio primitives.

## Risks and Edge Cases

Key risks are iterator lifetime errors, mismatched folio references from readahead extraction, incorrect zero-fill boundaries around `zero_point` and EOF, deadlocks between read-for-write and writeback/private folio state, and collector races around `NETFS_RREQ_ALL_QUEUED` and stream activation. `netfs_read_gaps()` is especially sensitive because it mixes real folio bvecs with a sink folio to preserve dirty data while filling gaps.

Partial reads, cache holes, cache withdrawal, large folio alignment, `IOCB_NOIO`/`IOCB_NOWAIT` behavior inherited from filemap, and deprecated `netfs_write_begin()` users are regression-prone. Incorrect handling can expose stale data, fail to zero beyond EOF, unlock folios incorrectly, or lose errors after some subrequests were already queued.

## Test Signals

Useful tests include xfstests generic buffered read/write, readahead, mmap and write_begin coverage on netfs users; FS-Cache enabled/disabled reads; reads beyond EOF and beyond `zero_point`; cache hole reads; large-folio and THP-sized readahead; dirty streaming-write folio gap reads; direct-vs-buffered dispatch tests; fault injection for allocation, cache prepare, and filesystem prepare failures; and tracepoint/stat counter inspection for read source selection.
