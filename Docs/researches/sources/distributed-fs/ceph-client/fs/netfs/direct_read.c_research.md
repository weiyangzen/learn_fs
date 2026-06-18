# sources/distributed-fs/ceph-client/fs/netfs/direct_read.c

## Purpose

`direct_read.c` implements netfs unbuffered and direct reads that bypass the pagecache and local disk cache. It slices user or kernel iterators into filesystem/server read subrequests, manages direct-I/O inode accounting, supports synchronous and asynchronous completion, and routes generic netfs read dispatch to filesystem `issue_read()` operations.

## Important APIs and Functions

Exported APIs are `netfs_unbuffered_read_iter_locked()` and `netfs_unbuffered_read_iter()`. Internal helpers are `netfs_prepare_dio_read_iterator()`, `netfs_dispatch_unbuffered_reads()`, and `netfs_unbuffered_read()`.

The central data types are `struct netfs_io_request`, `struct netfs_io_subrequest`, `struct netfs_io_stream`, `struct kiocb`, and `struct iov_iter`. The file uses request origins `NETFS_DIO_READ` and `NETFS_UNBUFFERED_READ`, stream constraints `sreq_max_len` and `sreq_max_segs`, and request flags such as `NETFS_RREQ_ALL_QUEUED`, `NETFS_RREQ_OFFLOAD_COLLECTION`, `NETFS_RREQ_PAUSE`, and `NETFS_RREQ_FAILED`.

## Control Flow

`netfs_unbuffered_read_iter()` is the unlocked public entry. It returns zero for empty reads, starts direct-I/O exclusion with `netfs_start_io_direct()`, calls the locked helper, and ends the direct-I/O section.

`netfs_unbuffered_read_iter_locked()` first waits for dirty pagecache data in the target range with `kiocb_write_and_wait()`, updates file access time, allocates a request at `ki_pos` for the iterator length, and chooses the origin based on `IOCB_DIRECT`. If the iterator is user-backed, it extracts and pins a stable bvec iterator because async I/O cannot rely on the caller's iterator after return. Kernel/non-user iterators are copied directly and advanced. Async requests store `iocb` and set offloaded collection.

`netfs_unbuffered_read()` validates nonzero length, begins inode DIO accounting, dispatches subrequests, and either waits synchronously through `netfs_wait_for_read()` or returns `-EIOCBQUEUED`. If nothing was submitted, it releases the request and ends DIO accounting immediately.

`netfs_dispatch_unbuffered_reads()` loops over the requested range. It allocates a subrequest, marks it as server download, appends it to stream 0 under the request spinlock, calls optional filesystem `prepare_read()`, clamps iterator length through `netfs_prepare_dio_read_iterator()`, updates `submitted`, marks all queued when the range is exhausted, and calls filesystem `issue_read()`. It honors request pause/failure flags between submissions.

## State and Persistence Behavior

The file does not update persistent filesystem state. It mutates request/subrequest lists, iterator positions, pinned bvec arrays, submitted/transferred counters, inode direct-I/O counters, and `ki_pos` on synchronous successful completion. Pagecache is intentionally bypassed, though dirty cached data is waited on before reading to avoid stale direct reads.

## Dependencies and Integration Points

It depends on netfs object allocation and collection, iterator extraction/limiting, direct-I/O locking in `locking.c`, VFS `kiocb_write_and_wait()` and `file_accessed()`, filesystem `netfs_ops->prepare_read` and `issue_read`, and read completion functions in `read_collect.c`. It is selected by `netfs_file_read_iter()` when direct or unbuffered mode is requested.

## Risks and Edge Cases

Risks include pinning and unpinning user pages correctly across async completion, advancing caller iterators only for bytes represented by the netfs-owned iterator, reporting partial submission when bvec allocation shortens a request, and pairing `inode_dio_begin()` with completion-side `inode_dio_end()`. A zero-sized dispatched request is treated as an internal error. Pause/retry/failure flags must prevent issuing further subrequests after backend failure.

Because direct reads bypass both pagecache and local cache, coherency depends on waiting for dirty pagecache data first and on filesystem backend consistency. Async completion must update `ki_pos` and invoke `ki_complete` through the collector path, not through this file after it returns `-EIOCBQUEUED`.

## Test Signals

Useful tests include direct read xfstests, async `io_uring`/AIO reads, reads from user and kernel iterators, dirty pagecache followed by direct read, backend `rsize`/segment-limit slicing, partial bvec extraction failures, signal interruption, request pause/retry injection, and DIO accounting checks that truncate/writeback wait correctly blocks buffered writers.
