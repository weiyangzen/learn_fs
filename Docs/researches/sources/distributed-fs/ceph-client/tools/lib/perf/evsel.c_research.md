## sources/distributed-fs/ceph-client/tools/lib/perf/evsel.c

Purpose: Implements libperf event selector lifecycle, perf_event_open calls, per-CPU/thread FD arrays, mmap helpers, reads, ioctls, sample IDs, period storage, and count scaling.

Important APIs/functions: `perf_evsel__new/init/delete/open/close/mmap/munmap/read/enable/disable/apply_filter`, FD/id alloc/free helpers, `perf_evsel__cpus/threads/attr`, `perf_sample_id__get_period_storage()`, and `perf_counts_values__scale()`.

Control flow: Open fills an `xyarray` of FDs for each CPU/thread combination, resolving group leader FDs first. Read computes expected read size from `read_format`, handles group vs non-group formats, optionally uses mmap self-read fast path, and normalizes values into `perf_counts_values`. Enable/disable/filter iterate ioctls across FD dimensions. Sample ID storage allocates arrays and optional per-thread hash buckets.

State/persistence: Evsel owns attr, maps, FD xyarray, mmap xyarray, sample ID arrays, IDs, leader relation, per-stream period list, and flags. Kernel perf FDs and mmap regions persist until close/munmap.

Dependencies/integration: Uses `perf_event_open` syscall, libperf maps, thread maps, mmap internals, xyarray, readn, ioctls, and Linux perf formats.

Risks: Static fallback maps are never freed by design. Group FD lookup requires leader opened first. Read format handling must stay aligned with kernel ABI. `perf_evsel__exit()` asserts resources were already closed/freed. Permission errors from perf_event_open propagate as negative errno.

Test signals: Tests should cover per-thread/per-CPU opens, group leader/member ordering, read formats including LOST and GROUP, mmap read-self path, ioctl failures, filter application, sample ID allocation/freeing, per-thread period storage, and scaling when running time is zero or less than enabled.
