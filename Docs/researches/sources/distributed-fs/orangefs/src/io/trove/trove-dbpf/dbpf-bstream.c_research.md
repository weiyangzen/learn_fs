# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream.c

## Purpose
`dbpf-bstream.c` implements the buffered POSIX-AIO Trove bytestream backend. It queues list reads/writes, limits concurrent AIO globally, updates datafile size metadata after writes and resizes, supports flushing, and provides the `dbpf_bstream_ops` method table.

## Important APIs, types, and functions
Public bstream entry points include `dbpf_bstream_flush()`, `dbpf_bstream_rw_list()`, `dbpf_bstream_resize()`, `dbpf_pread()`, and `dbpf_pwrite()`. `dbpf_bstream_read_at()`, `dbpf_bstream_write_at()`, and `dbpf_bstream_validate()` return `-TROVE_ENOSYS`. Internal scheduling is handled by `issue_or_delay_io_operation()` and `start_delayed_ops_if_any()`. In threaded AIO mode, `aio_progress_notification()` drives completion and posts additional chunks; in non-threaded mode, `dbpf_bstream_rw_list_op_svc()` polls progress from the DBPF op queue.

## Control flow and state
`dbpf_bstream_rw_list()` validates the collection, allocates a queued op, records vector arrays and AIO ops, starts trace events, obtains a buffered open-cache descriptor, invalidates attr-cache entries on writes, and either queues service or immediately posts AIO depending on `__PVFS2_TROVE_AIO_THREADED__`. A fixed 64-entry aiocb array is reused as chunks are converted. Global state `s_dbpf_ios_in_progress` and `s_dbpf_io_ready_queue` enforce `TROVE_max_concurrent_io` and delay excess operations.

## Persistence and integration
Buffered I/O writes to bytestream files through AIO, flush uses `fdatasync()`, and resize uses `ftruncate()` followed by dspace attr update. Write completion may update `TROVE_ds_attributes.u.datafile.b_size`; if `TROVE_SYNC` requires metadata durability, the op is transformed into a `DSPACE_SETATTR` for sync coalescing.

## Dependencies
It depends on POSIX AIO, `dbpf-bstream-aio.c`, DBPF queued ops, open cache, attr cache, dspace attr helpers, sync coalescing, id generation, event tracing, and optional alternate AIO support.

## Risks and test signals
Concurrency accounting is subtle because `issue_or_delay_io_operation()` and `start_delayed_ops_if_any()` both adjust `s_dbpf_ios_in_progress`. Non-threaded read accounting treats reads differently because `aio_return()` may not report bytes with `SIGEV_NONE`. Cancellation can only cancel queued ops reliably; in-service AIO depends on backend `aio_cancel()`. Tests should cover concurrency limiting, delayed queue restart, write size extension, resize sync behavior, attr-cache invalidation, flush errors, cancellation states, and threaded versus non-threaded compile paths.
