# sources/distributed-fs/ceph-client/fs/netfs/buffered_write.c

## Purpose

`buffered_write.c` implements high-level netfs buffered writes into the pagecache and mmap write-fault handling. It supports normal dirtying, writethrough for synchronous writes, streaming writes that track dirty byte ranges in non-uptodate folios, cache-aware read-modify-write, folio grouping for filesystem-specific coherency domains such as Ceph snapshots, and dispatch selection between buffered and unbuffered write paths.

## Important APIs and Functions

Exported APIs are `netfs_update_i_size()`, `netfs_perform_write()`, `netfs_buffered_write_iter_locked()`, `netfs_file_write_iter()`, and `netfs_page_mkwrite()`. Internal helpers include `__netfs_set_group()`, `netfs_set_group()`, and `netfs_grab_folio_for_write()`.

Important state types are `struct netfs_inode`, `struct netfs_group`, `struct netfs_folio`, `struct netfs_io_request`, `struct writeback_control`, folios and address spaces. `NETFS_FOLIO_COPY_TO_CACHE` and `NETFS_FOLIO_INFO`-tagged private data distinguish cache-copy and streaming-write state from filesystem group pointers.

## Control Flow

`netfs_file_write_iter()` is the generic entry. It rejects empty writes, dispatches to unbuffered/direct write if `IOCB_DIRECT` or `NETFS_ICTX_UNBUFFERED` is set, otherwise starts netfs write exclusion, runs `generic_write_checks()`, calls `netfs_buffered_write_iter_locked()`, ends write exclusion, and performs `generic_write_sync()` for successful synchronous writes.

`netfs_buffered_write_iter_locked()` performs privilege stripping and timestamp update before delegating to `netfs_perform_write()`. `netfs_perform_write()` optionally begins a writethrough request for `IOCB_DSYNC`/`IOCB_SYNC`, then loops over the user iterator. For each chunk it faults in user pages before locking the destination folio, obtains the largest suitable folio, waits for writeback if private state exists, checks signals, and chooses one of several modification modes.

If a folio is uptodate, data is copied atomically and the folio is grouped. If the folio lies beyond `ctx->zero_point`, unwritten portions are zeroed and the folio becomes uptodate. Whole-folio writes can avoid prefetch. If the file is readable or caching is enabled, partial writes prefetch existing data with `netfs_prefetch_for_write()` to avoid losing old contents. If streaming is possible, a new `struct netfs_folio` tracks `dirty_offset` and `dirty_len`; contiguous writes extend it, while overlapping or incompatible writes flush the folio and retry.

After copying, the code flushes dcache, updates i_size and estimated blocks through `netfs_update_i_size()`, advances position and written count, either marks the folio dirty or advances a writethrough request, releases the folio, and throttles dirty pages. On exit it marks modified attributes, calls optional `post_modify()`, finishes writethrough, updates `ki_pos`, and returns either bytes written or the first error.

`netfs_page_mkwrite()` handles writable mmap faults. It starts pagefault write protection, locks the folio, waits for writeback, requires uptodate data, flushes incompatible group contents to disk if needed, tags the folio with the requested group, updates file time and modified-attr state, and returns `VM_FAULT_LOCKED` with the folio held for the VM.

## State and Persistence Behavior

The file changes pagecache contents, dirty tags, folio private/group state, inode size, estimated `i_blocks`, FS-Cache cookie size, netfs modified-attribute flags, and writeback/writethrough request state. Actual persistence is deferred to writeback or writethrough paths in other netfs files and filesystem backends. Synchronous writes use writethrough request machinery and later `generic_write_sync()` to satisfy durability expectations.

## Dependencies and Integration Points

It depends on buffered read support for `netfs_prefetch_for_write()`, write issue support for writethrough (`netfs_begin_writethrough()`, `netfs_advance_writethrough()`, `netfs_end_writethrough()`), direct write support for dispatch fallback, netfs locking helpers, FS-Cache cookie update/invalidation hooks, VFS generic write checks, folio/pagecache APIs, dirty throttling, and filesystem operations `update_i_size()` and `post_modify()`.

CephFS integration is visible through `netfs_group`, which lets dirty folios be associated with coherency groups such as snapshots and forces flushing when an incompatible group attempts to modify a folio.

## Risks and Edge Cases

The riskiest areas are partial writes to non-uptodate folios, streaming-write range tracking, group transitions, and interactions with writeback-owned private data. Incorrect group handling can mix data from different coherency domains. Incorrect dirty-range tracking can lose unwritten data, especially when copy faults produce partial progress. Writethrough error ordering must preserve `-EIOCBQUEUED` for async completion and report late writeback errors when no earlier error exists.

Other edge cases include beyond-EOF zeroing, `zero_point` advancement, large folio sizing, faulting user pages before locking destination folios to avoid deadlocks, signal interruption after partial writes, mmap faults against incompatible folio groups, and file-size/block accounting races when the server later reports authoritative metadata.

## Test Signals

Relevant tests include xfstests generic buffered writes, partial writes with copy faults, writes beyond EOF, mmap write faults, fsx-style mixed mmap/read/write/truncate workloads, Ceph snapshot/group coherency tests, FS-Cache enabled partial writes, synchronous writes and writethrough completion, large-folio writes, dirty throttling under memory pressure, and fault injection for allocation, prefetch, writeback wait, and writethrough submission.
