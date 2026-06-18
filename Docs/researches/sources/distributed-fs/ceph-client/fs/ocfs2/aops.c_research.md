# sources/distributed-fs/ceph-client/fs/ocfs2/aops.c

## Purpose
`aops.c` implements OCFS2 address-space operations for page-cache reads, readahead, writeback, buffered writes, mmap writes, direct I/O, inline data, block mapping, and folio buffer lifetime. It is the bridge between Linux VFS/page-cache APIs and OCFS2 clustered metadata, extent maps, journaling, quotas, refcount/COW, and inode DLM locks.

## Important APIs, types, and functions
The exported objects are `ocfs2_aops`, `ocfs2_get_block`, `ocfs2_map_folio_blocks`, `ocfs2_unlock_and_free_folios`, `walk_page_buffers`, `ocfs2_write_begin_nolock`, `ocfs2_write_end_nolock`, `ocfs2_read_inline_data`, and `ocfs2_size_fits_inline_data`. Internal write state is held in `struct ocfs2_write_ctxt`, `struct ocfs2_write_cluster_desc`, and `struct ocfs2_unwritten_extent`; direct-I/O completion state uses `struct ocfs2_dio_write_ctxt`. Major paths include `ocfs2_read_folio`, `ocfs2_readahead`, `ocfs2_write_begin`, `ocfs2_write_end`, `ocfs2_dio_wr_get_block`, `ocfs2_dio_end_io_write`, and `ocfs2_direct_IO`.

## Control flow
Reads take the inode lock and `ip_alloc_sem` read-side before resolving extents; inline inodes are copied from the dinode, while regular files use block helpers. Buffered writes take the inode lock exclusive, hold `ip_alloc_sem` write-side, allocate a write context, optionally use inline data, zero sparse tails or expand nonsparse files, COW refcounted extents, populate per-cluster descriptors, reserve allocators, start a journal transaction, grab folios, map/zero buffers, and finish in `ocfs2_write_end_nolock` by committing buffers, updating size/times, dirtying metadata, unlocking folios, committing, and running deferred deallocs. Direct writes use `ocfs2_dio_wr_get_block` as the block mapper, attach private completion context to the mapping buffer, add expanding writes to the orphan directory, and clear unwritten extents/update size/delete orphan in `ocfs2_dio_end_io_write`.

## State and persistence behavior
Persistent effects are extent allocation, unwritten-to-written conversion, inline-data conversion, dinode size/timestamp/block-count updates, orphan directory membership for extending direct I/O, quota allocation, and journaled metadata changes. Runtime state includes folio buffer flags, clustered extent cache results, `ip_unwritten_list`, allocation reservations, dealloc contexts, and `kiocb->private` bits used to communicate rw-lock ownership to direct-I/O completion.

## Dependencies and integration points
This file depends on the VFS address-space API, buffer-head helpers, mpage, direct I/O, quotas, jbd2 transactions, OCFS2 extent maps/allocation/refcount tree, inode locks, DLM rw locks, inline-data helpers, and tracing. `ocfs2_aops` is installed on OCFS2 inodes and is called from generic read/write/mmap/direct-I/O paths.

## Risks and test signals
Risks include lock-order deadlocks between folios, `ip_alloc_sem`, inode/DLM locks, and journal barriers; stale-data exposure during partial allocation failures; direct-I/O orphan cleanup failures; races with remote truncate; incorrect unwritten extent tracking; inline-to-extent conversion edge cases; and fallback behavior for unsupported append DIO. Test signals include buffered writes across cluster/page boundaries, sparse and nonsparse extension, inline data growth and conversion, mmap page faults, direct writes beyond EOF with crash recovery, refcounted COW writes, ENOSPC retry through truncate-log freeing, remote truncate during reads/readahead, and DIO completion with short or failed I/O.
