# sources/distributed-fs/ceph-client/include/trace/events/readahead.h

Purpose: Defines page-cache readahead tracepoints for unbounded readahead, order-based folio readahead, and sync/async readahead operations.

Important APIs/types/functions: Events include `page_cache_ra_unbounded`, `page_cache_ra_order`, and event-class `page_cache_ra_op` used by `page_cache_sync_ra` and `page_cache_async_ra`. Fields include inode, file pointer, device, index, request count, order, readahead window size, async size, and return/allocated counts.

Control flow: Filemap/readahead code emits events when readahead is triggered directly, when larger-order folios are considered, and when sync or async readahead windows are calculated and submitted.

State and persistence: No state is owned. It observes file readahead state in `struct file_ra_state`, inode/page-cache indices, and allocation results.

Dependencies and integration points: Depends on MM, fs, pagemap, and tracepoints. It integrates with filesystems, page cache, block/network-backed file reads, and performance analysis.

Risks and test signals: Risks include index/count overflow on large files, misreading async window behavior, and high event volume on sequential workloads. Test sequential/random reads, mmap faults, large folio readahead, direct readahead calls, network filesystems, and memory-pressure allocation failures.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/readahead.h` completely for this pass (132 lines, 3680 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/readahead.h_research.md`.
