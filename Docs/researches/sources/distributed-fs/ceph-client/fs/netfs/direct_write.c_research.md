# sources/distributed-fs/ceph-client/fs/netfs/direct_write.c

## Purpose

`direct_write.c` implements netfs unbuffered and direct writes that send data to the server without storing it in the pagecache or local cache. It serializes subrequest dispatch to avoid leaving server-side gaps after partial failures, handles synchronous and asynchronous writes, invalidates overlapping cached folios, updates inode size, and invalidates FS-Cache contents for direct writes.

## Important APIs and Functions

Exported APIs are `netfs_unbuffered_write_iter_locked()` and `netfs_unbuffered_write_iter()`. Internal helpers are `netfs_unbuffered_write_done()`, `netfs_unbuffered_write_collect()`, `netfs_unbuffered_write()`, and `netfs_unbuffered_write_async()`.

The file uses `struct netfs_io_request` as a write request, stream 0 as the upload stream, `struct netfs_io_subrequest` for backend writes, request origins `NETFS_DIO_WRITE` and `NETFS_UNBUFFERED_WRITE`, request flags such as `NETFS_RREQ_USE_IO_ITER` and `NETFS_RREQ_UPLOAD_TO_SERVER`, and subrequest flags such as `NETFS_SREQ_FAILED`, `NETFS_SREQ_NEED_RETRY`, and `NETFS_SREQ_BOUNDARY`.

## Control Flow

`netfs_unbuffered_write_iter()` is the public entry. It rejects empty writes, starts direct-I/O exclusion, runs generic write checks, strips privileges, updates timestamps, waits for or invalidates overlapping pagecache depending on `IOCB_NOWAIT`, invalidates clean pagecache for the target range before submission, advances `ictx->zero_point` to cover the write, invalidates the FS-Cache cookie, then calls the locked helper and ends direct I/O.

`netfs_unbuffered_write_iter_locked()` allocates a write request, marks stream 0 available, extracts a stable iterator from user-backed buffers or copies kernel iterators, records request length, sets upload/use-iterator flags, and dispatches. Async writes initialize work, store `iocb`, queue to `system_dfl_wq`, and return `-EIOCBQUEUED`. Synchronous writes call `netfs_unbuffered_write()` directly, update `ki_pos`, return transferred bytes or error, and drop request references.

`netfs_unbuffered_write()` begins inode DIO accounting for direct writes, repeatedly prepares a write subrequest, truncates it to remaining data and stream limits, issues it, waits for that stream's in-progress work to finish, and then either collects success, handles failure, or retries. Retry resets iterators and subrequest fields, calls filesystem `retry_request()` when supplied, and either reruns `prepare_write()` or reissues through generic write helpers. Dispatch is serial so a later range is not written if an earlier range failed.

`netfs_unbuffered_write_done()` finalizes the request. On success it updates i_size, invalidates pagecache folios overlapping direct writes that may have appeared via mmap, ends inode DIO accounting, wakes waiters on `NETFS_RREQ_IN_PROGRESS`, completes async `kiocb` with bytes written or error, and clears subrequests.

## State and Persistence Behavior

This path directly changes server-side file contents through backend write operations. It mutates request transfer counters, stream collected positions, `ki_pos`, inode size through `netfs_update_i_size()`, `ictx->zero_point`, pagecache invalidation state, FS-Cache invalidation state, and direct-I/O exclusion counters. It avoids populating local cache or pagecache with the new data.

## Dependencies and Integration Points

The file depends on write request creation and preparation in `write_issue.c`, reissue helpers, write completion and wait helpers, iterator extraction, VFS generic write checks, pagecache invalidation, FS-Cache invalidation, and netfs direct-I/O locking. Backend integration occurs through stream `issue_write`, optional `prepare_write`, optional filesystem `retry_request`, and write subrequest termination.

## Risks and Edge Cases

Important risks include correctly pairing request references across async work and caller return, preserving `-EIOCBQUEUED`, avoiding gaps by serial dispatch, handling partial subrequest transfer before retry, invalidating pagecache without discarding dirty local data, and ensuring DIO accounting ends only after real completion. NOWAIT behavior can return `-EAGAIN` if cached pages would block invalidation.

The TODO bounce-buffer paths are explicit future integration points for encryption/compression/block expansion. Until implemented, filesystems needing transformed direct writes must either avoid this path or provide compatible iterators. Errors after partial transfer must return bytes written to the caller where VFS semantics require it.

## Test Signals

Relevant tests include direct write xfstests, async DIO/AIO/io_uring writes, NOWAIT writes with cached pages, mmap racing with DIO writes, partial backend failure and retry injection, FS-Cache invalidation checks after DIO, large writes sliced by backend limits, signal interruption during synchronous unbuffered writes, and truncate/read-after-direct-write coherency tests.
