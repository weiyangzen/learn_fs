# sources/distributed-fs/ceph-client/fs/cachefiles/io.c

## Purpose
`io.c` implements CacheFiles netfs-cache operations: direct reads and writes to backing files, occupancy queries, read-source selection, write preparation, write submission, and operation cleanup.

## Important APIs, Types, and Functions
Important functions are `cachefiles_read`, `cachefiles_query_occupancy`, `cachefiles_write_complete`, `__cachefiles_write`, `cachefiles_write`, `cachefiles_do_prepare_read`, `cachefiles_prepare_read`, `cachefiles_prepare_ondemand_read`, `__cachefiles_prepare_write`, `cachefiles_prepare_write`, `cachefiles_prepare_write_subreq`, `cachefiles_issue_write`, `cachefiles_end_operation`, and `cachefiles_begin_operation`. The local `struct cachefiles_kiocb` wraps a kernel `kiocb`, object ref, completion callback, invalidation generation, range data, async state, and in-flight block count.

## Control Flow
Reads wait for a readable FS-Cache operation, optionally seek to data to skip holes, zero-fill holes when requested, allocate a `cachefiles_kiocb`, submit direct `vfs_iocb_iter_read`, and complete synchronously or asynchronously through `cachefiles_read_complete`. Completion checks the cookie invalidation counter and calls the netfs termination callback. Writes prepare a similar kiocb, account in-flight blocks in `cache->b_writing`, submit direct `vfs_iocb_iter_write`, and on completion subtract accounting, marks `FSCACHE_COOKIE_HAVE_DATA`, and terminates the netfs request. Read preparation uses `SEEK_DATA` and `SEEK_HOLE` to choose cache read, server download, zero fill, or on-demand userspace fetch. Write preparation enforces page/DIO alignment, checks allocation status and free space, and may punch partially allocated regions when space is insufficient.

## State and Persistence Behavior
Persistent effects are direct writes, punched holes, and file allocation changes in the backing cache file. Runtime state includes kiocb refs, object refs, `b_writing`, cookie invalidation counters, `NO_DATA_TO_READ`, `HAVE_DATA`, and netfs subrequest flags such as `NETFS_SREQ_COPY_TO_CACHE` and `NETFS_SREQ_ONDEMAND`.

## Dependencies and Integration Points
This file plugs CacheFiles into `struct netfs_cache_ops`. It depends on FS-Cache operation gating, VFS direct I/O, `llseek` hole/data reporting, fallocate, netfs request/subrequest APIs, on-demand read requests, tracepoints, and credential override helpers.

## Risks and Edge Cases
Alignment is strict because backing files are opened with `O_DIRECT`; partial DIO ranges are skipped or extended only in controlled cases. Invalidation races are detected by comparing counters after reads. Hole/data seeking must handle `-ENXIO` distinctly from real errors. Space checks must include in-flight writes or writes can overrun culling thresholds. Async and sync completion share refcounted cleanup, so double completion or missed `cachefiles_put_kiocb` would leak or free early.

## Test Signals
Test cache hits, holes, partial cached extents, `SEEK_DATA`/`SEEK_HOLE` errors, on-demand read retry, direct-I/O misalignment, low-space write preparation, fallocate punch failures, async read/write completion, invalidation during read, and netfs write-subrequest termination accounting.
