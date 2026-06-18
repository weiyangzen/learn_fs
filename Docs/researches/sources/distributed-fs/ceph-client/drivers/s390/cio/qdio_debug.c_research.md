# sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_debug.c

Purpose: provides QDIO debug feature areas and debugfs views for per-device queue state, SSQD descriptors, and performance statistics.

Important APIs/types/functions: initializes global debug areas through `qdio_debug_init()` and frees them through `qdio_debug_exit()`. Per-device debug areas are managed by `qdio_allocate_dbf()` and a reuse list. Debugfs setup/removal uses `qdio_setup_debug_entries()` and `qdio_shutdown_debug_entries()`. Show/write functions include `qstat_show()`, `ssqd_show()`, `qperf_show()`, and `qperf_seq_write()`.

Control flow: module init creates `/sys/kernel/debug/qdio` and debug feature buffers. Per-device setup creates a directory, statistics file, SSQD file, and one file per input/output queue. Queue state reads call `debug_get_buf_state()` for each SBAL and print symbolic states. Statistics writes of 0 clear counters and disable perf accounting; writes of 1 enable it.

State and persistence behavior: debug state is in debug feature buffers, debugfs dentries, a list of per-device debug areas, and optional performance counters in `struct qdio_irq`/`struct qdio_q`. It is volatile and removed on shutdown/exit.

Dependencies and integration points: depends on debugfs, seq_file, s390 debug feature, QDIO internal structures, SSQD query API, and queue buffer-state helpers.

Risks and test signals: debug-area reuse by device name must not leak stale pointers; debugfs reads race with teardown unless lifecycle ordering is correct. Tests should cover repeated allocate/free for the same device, statistics enable/disable, queue state formatting for all SLSB states, SSQD errors, and module exit with live/removed devices.
