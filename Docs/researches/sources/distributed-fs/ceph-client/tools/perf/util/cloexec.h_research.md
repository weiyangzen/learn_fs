# sources/distributed-fs/ceph-client/tools/perf/util/cloexec.h

Purpose: declares the cached `perf_event_open` cloexec flag probe.

Important APIs/types: `perf_event_open_cloexec_flag(void)` returns `PERF_FLAG_FD_CLOEXEC` or zero.

Control flow: callers add the returned flag to `perf_event_open` flags after probing.

State and persistence: no header state; implementation caches the probe.

Dependencies and integration: used by perf event-open paths that need close-on-exec behavior on mixed kernel versions.

Risks: callers must still handle event-open failures.

Test signals: compile and runtime event-open tests on old and new kernels.
