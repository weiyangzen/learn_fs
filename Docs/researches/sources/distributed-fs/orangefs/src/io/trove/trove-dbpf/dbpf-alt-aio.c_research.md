# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-alt-aio.c

## Purpose
`dbpf-alt-aio.c` provides a pthread-backed replacement for the subset of POSIX AIO that DBPF needs for bytestream list I/O. It exists for configurations where real AIO is missing, unreliable, or replaced by OrangeFS's alternate path. The file wires this fallback into a `TROVE_bstream_ops` table named `alt_aio_bstream_ops`.

## Important APIs, types, and functions
The local `struct alt_aio_item` wraps one `struct aiocb`, the shared completion `sigevent`, master-thread metadata, and the thread id array. `alt_lio_listio()` is the only meaningful AIO operation: it spawns one thread per list entry, sets `__error_code` to `EINPROGRESS` when available, and either joins all threads for `LIO_WAIT` or makes the last worker the detached master for `LIO_NOWAIT`. `alt_lio_thread()` performs `pread()` or `pwrite()` according to `aio_lio_opcode`, stores optional libc-private `aiocb` error/return fields, and has the master join siblings before invoking `sigev_notify_function`. `alt_aio_bstream_read_list()` and `alt_aio_bstream_write_list()` delegate to `dbpf_bstream_rw_list()` with the alternate `dbpf_aio_ops`.

## Control flow and state
For `LIO_NOWAIT`, all non-master workers are joinable and the final worker is detached, joins earlier threads, frees the shared `tids` array, and triggers the bstream progress callback. For `LIO_WAIT`, `alt_lio_listio()` joins all workers before returning. Standalone `aio_read`, `aio_write`, `aio_cancel`, `aio_suspend`, and `aio_fsync` are stubs returning `-1`/`ENOSYS`.

## Persistence and integration
The file does not persist state directly. It integrates with `dbpf-bstream.c` through `struct dbpf_aio_ops` and `dbpf_bstream_rw_list()`, so persistence effects are the same as buffered bstream reads/writes: bytestream file I/O plus metadata updates in dspace after writes.

## Dependencies
It depends on pthreads, `pread`/`pwrite`, `aio.h` layout compatibility, `quicklist.h`, `dbpf.h`, `dbpf-alt-aio.h`, and OrangeFS gossip/debug infrastructure.

## Risks and test signals
The implementation relies on nonportable `struct aiocb` internals guarded by `HAVE_AIOCB_ERROR_CODE` and `HAVE_AIOCB_RETURN_VALUE`; without them, error and return reporting degrade to zero. Failure paths can leak already allocated `tmp_item` objects if allocation fails after earlier threads were spawned in `LIO_NOWAIT`. Tests should cover mixed read/write list conversion through `alt_aio_bstream_ops`, callback firing exactly once, short read/write return accounting, `LIO_WAIT` behavior, thread-create failure cleanup, and operation with libc configurations that do not expose private aiocb fields.
