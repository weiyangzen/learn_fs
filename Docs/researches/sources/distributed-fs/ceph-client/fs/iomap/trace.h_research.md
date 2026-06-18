## sources/distributed-fs/ceph-client/fs/iomap/trace.h

Purpose: declares iomap tracepoints for readpage/readahead, range operations, iterator mappings, ioend additions, direct-I/O begin/completion, and iterator calls.

Important APIs: defines event classes `iomap_readpage_class`, `iomap_range_class`, and `iomap_class`, plus concrete events such as `iomap_readpage`, `iomap_readahead`, `iomap_writeback_folio`, `iomap_dio_invalidate_fail`, `iomap_dio_rw_queued`, `iomap_iter_dstmap`, `iomap_iter_srcmap`, `iomap_add_to_ioend`, `iomap_iter`, `iomap_dio_rw_begin`, and `iomap_dio_complete`. String tables cover iomap types, iterator flags, iomap flags, and DIO flags.

Control flow: no filesystem logic; tracepoint macros define data capture and print formatting. Events collect device/inode identifiers, offsets, lengths, mapping type/flags, bdev, kiocb flags, AIO status, errors, and return values.

State and persistence: trace events are observational only. They can expose runtime state to tracing buffers but do not mutate filesystem or I/O state.

Dependencies and integration points: integrates with the Linux trace subsystem and uses VFS/inode fields, iomap structures, and `TRACE_IOCB_STRINGS`. `trace.c` supplies `CREATE_TRACE_POINTS`.

Risks and test signals: risks include stale enum string tables, missing new flags, format mismatches, and excessive trace overhead when enabled. Test with ftrace/perf tracepoint listing and sample workloads for direct I/O, writeback, and fiemap/seek iterator activity.
