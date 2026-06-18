# sources/distributed-fs/ceph-client/include/trace/events/netfs.h

Purpose: Defines tracepoints and symbolic enums for the network-filesystem helper library. It covers read requests, write requests, subrequests, cache copy, folio state, collection/cleanup progress, reference changes, and folio-queue activity.

Important APIs/types/functions: Exported enum maps include `netfs_read_traces`, `netfs_write_traces`, `netfs_rreq_origins`, `netfs_rreq_traces`, `netfs_sreq_sources`, `netfs_sreq_traces`, `netfs_failures`, reference-trace enums, folio traces, donation traces, and folio-queue traces. Trace events include `netfs_read`, `netfs_rreq`, `netfs_sreq`, `netfs_failure`, `netfs_rreq_ref`, `netfs_sreq_ref`, `netfs_folio`, `netfs_write_iter`, `netfs_write`, `netfs_copy2cache`, `netfs_collect*`, and `netfs_folioq`.

Control flow: Netfs read/write paths emit request and subrequest events as operations are prepared, submitted to server/cache, retried, completed, redirtied, unlocked, or collected. Writeback and streaming-write collection events track gaps, streams, folios, and cleaned/collected offsets. Reference events trace lifecycle ownership.

State and persistence: The header owns no state. It observes `netfs_io_request`, `netfs_io_subrequest`, `folio`, `folio_queue`, cache cookies, inode numbers, flags, offsets, lengths, errors, refs, and stream progress. Durable data remains in backing servers, page cache, and fscache.

Dependencies and integration points: Depends on tracepoints and netfs/fscache structs supplied by including C files. It integrates with network filesystems such as CephFS, AFS, 9P, and cachefiles/fscache debugging.

Risks and test signals: Risks include enum/print mapping drift, tracing freed request/subrequest state, offset overflow in large files, missed error paths, and hot-path overhead during writeback. Test netfs readpage/readahead/direct I/O, writeback/writethrough/unbuffered write, cache copy, short reads, retry/error injection, folio invalidation, and request refcount balancing.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/netfs.h` completely for this pass (786 lines, 25452 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/netfs.h_research.md`.
