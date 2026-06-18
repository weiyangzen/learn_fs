# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream-direct.c

## Purpose
`dbpf-bstream-direct.c` implements the direct-I/O Trove bytestream backend. It bypasses buffered POSIX AIO and posts read/write work to the PINT manager thread pool, while handling direct-I/O alignment constraints, byte-range locking, metadata size updates, and operation cancellation.

## Important APIs, types, and functions
The exported ops table is `dbpf_bstream_direct_ops`. List operations are `dbpf_bstream_direct_read_list()` and `dbpf_bstream_direct_write_list()`, which allocate DBPF queued ops, acquire direct file descriptors from the open cache, and post service routines through `PINT_manager_id_post()`. `dbpf_bstream_direct_read_op_svc()` and `dbpf_bstream_direct_write_op_svc()` are the worker functions. Low-level helpers include `direct_aligned_read()`, `direct_read()`, `direct_locked_read()`, `direct_aligned_write()`, `direct_write()`, and `direct_locked_write()`. `dbpf_bstream_get_extents()` maps Trove memory/stream vectors into concrete stream extents. Grow serialization uses `grow_bstream_handle_table_init()`, `grow_bstream_handle_acquire_lock()`, and `grow_bstream_handle_release_lock()`.

## Control flow and state
Read and write requests become `struct dbpf_bstream_rw_list_op` payloads. Reads fetch current datafile size from dspace, derive extents, and perform locked direct reads. Writes derive extents, lazily initialize `grow_bstream_table`, acquire a per-handle grow lock before reading size, release it early if the write does not extend the file, perform locked direct writes, update `out_size_p`, and if the end-of-request exceeds recorded size, update dspace attributes and convert the queued op into a sync-coalesced `DSPACE_SETATTR`.

## Persistence and integration
Data persists through direct `pread`/`pwrite` against open-cache descriptors. Metadata persists through `dbpf_dspace_attr_get()` and `dbpf_dspace_attr_set()`, with sync coalescing through `dbpf_sync_coalesce()` when size changes. Resize updates attributes and truncates the direct-write file descriptor. Flush is a no-op complete because direct writes are treated as synchronous enough for this backend.

## Dependencies
This file depends on DBPF queued ops, open cache, dspace attr helpers, sync coalescing, `PINT_manager`, `fcntl` locks, `posix_memalign`, qhash, and direct-I/O flags such as `O_DIRECT` or `F_NOCACHE` when available.

## Risks and test signals
The alignment path is high risk: unaligned writes use aligned bounce buffers and read-modify-write edge blocks, so tests must cover front edge, tail edge, EOF extension, zero-fill beyond EOF, and already-aligned pass-through. `posix_memalign()` return values are not checked directly; only the pointer is tested. The direct header prototypes do not match the static function signatures in this file, and the functions are static, so the header appears stale. Grow-lock refcount/free logic should be stress-tested with concurrent extending writes to the same handle. Tests should also cover lazy reads before a bytestream exists, cancellation through `PINT_manager_cancel()`, size update coalescing, `ftruncate()` failure, and platforms without real direct-I/O flags.
