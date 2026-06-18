
# sources/distributed-fs/ceph-client/tools/perf/util/mmap.c

Purpose: wraps libperf ring-buffer mmap handling with perf tool features: CPU affinity masks, optional compression staging buffers, optional AIO write buffers, auxtrace mmap hooks, and buffer draining.

Important APIs/types/functions: `mmap__mmap_len` delegates ring length calculation to libperf. Weak auxtrace hooks (`auxtrace_mmap__mmap`, `auxtrace_mmap__munmap`, parameter init/set-idx) allow auxtrace-enabled builds to override behavior. AIO helpers allocate per-control-block data buffers, optionally bind them to NUMA nodes, assign AIO priorities, and release them. Public `mmap__mmap` creates the perf ring buffer, affinity mask, zstd state, compression staging mmap, auxtrace mmap, and AIO buffers. `mmap__munmap` tears them down. `perf_mmap__push` drains ring data in one or two chunks across wraparound and calls a caller-supplied push callback.

Control flow: mapping starts with `perf_mmap__mmap`; affinity setup is skipped for system affinity and otherwise builds CPU or NUMA-node masks. zstd is initialized before optional compression staging allocation. Auxtrace mapping is attempted before AIO setup. Unmapping frees the bitmap, compression state, AIO resources, main data buffer, and auxtrace state. `perf_mmap__push` reads the head, initializes a read transaction, handles `-EAGAIN` as "try later", pushes wrapped and linear portions, advances `start`, records `prev`, and consumes the buffer.

State and persistence: state lives in `struct mmap`: `core` libperf mmap state, optional `aio` arrays, `affinity_mask`, `data` compression buffer, `file`, and zstd data. It reflects live kernel mmap buffers and anonymous user buffers only; nothing is persisted.

Dependencies: depends on libperf `perf_mmap`, Linux bitmap helpers, `page_size`, zstd compression helpers, CPU/NUMA topology utilities, optional `HAVE_AIO_SUPPORT`, optional `HAVE_LIBNUMA_SUPPORT`, auxtrace, and debug logging.

Integration points: used by record/top/report-like paths that read perf ring buffers. Compression and AIO fields are consumed by perf data writing code, while auxtrace hooks connect Intel PT/ARM SPE style auxiliary buffers.

Risks: partial setup failures can leave resources allocated unless callers follow cleanup paths. NUMA binding uses `node_index + 1 + 1`, so mask sizing changes need care. `perf_mmap__push` assumes callbacks can handle exact buffer fragments and must not consume after errors. Test signals include perf record smoke tests with and without compression/AIO/auxtrace, ring wraparound reads, NUMA affinity debug output at `verbose == 2`, and leak checks on failed setup.
