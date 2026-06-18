# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/iobuf.h

## Purpose
Defines GlusterFS pooled I/O buffers and iobref containers used to manage memory backing vector I/O without excessive allocation churn.

## APIs, Types, and Functions
`iobuf_pool` owns arenas bucketed by page size, filled lists, purge lists, default page size, arena size, miss count, and arena count. `iobuf_arena` represents an mmap region with passive/active lists, counts, allocation stats, and flexible `iobufs`. `iobuf` stores arena link, lock, atomic refcount, usable pointer, page size, and allocated buffer. `iobref` is a refcounted list of iobuf pointers. APIs create/destroy pools, allocate/ref/unref iobufs, convert to iovec, allocate small/page-aligned buffers, create/ref/unref/add/merge/clear iobrefs, compute sizes, dump stats, and copy an iovec into pooled storage. Macros provide alignment and pointer/page-size access.

## Control Flow, State, and Persistence
I/O buffers are process-local pooled memory. Allocation chooses a size bucket or small buffer path, moves buffers between passive/active lists, and returns arenas to purge when idle. Iobrefs group buffers so request/response vectors keep backing memory alive across async callbacks.

## Dependencies and Integration
Depends on mmap flags, atomics, locks, list, and `struct iovec`. Used by readv/writev callbacks, protocol serialization, quick-read/content paths, and translator data movement.

## Risks and Test Signals
Risks include refcount leaks, arena-list corruption, alignment mistakes, copying beyond iovec lengths, unbounded large-buffer misses, and use-after-unref in async paths. Test signals include iobuf ref/unref stress, iobref merge tests, valgrind/ASAN on read/write paths, alignment tests, and stats dump verification.
