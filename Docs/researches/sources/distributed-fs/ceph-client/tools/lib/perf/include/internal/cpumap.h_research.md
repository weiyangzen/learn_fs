## sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/cpumap.h

Purpose: Defines the internal layout and helpers for libperf CPU maps.

Important APIs/types: `DECLARE_RC_STRUCT(perf_cpu_map)` expands to a refcounted struct with `refcnt`, `nr`, and flexible `struct perf_cpu map[]`. Internal declarations expose allocation, index lookup, subset test, set-nr, and `perf_cpu_map__refcnt()`.

Control flow: Header has only inline refcount access. Runtime flow is in `cpumap.c`.

State/persistence: CPU map state is heap-owned and refcounted. Optional `rc_check.h` indirection can alter pointer layout in sanitizer builds.

Dependencies/integration: Includes public `<perf/cpumap.h>`, Linux refcount, and `rc_check.h`. Used by evlist/evsel and cpumap implementation.

Risks: Internal layout exposure means installed internal headers can create ABI coupling. Consumers must use `RC_CHK_ACCESS()`/helpers correctly under reference-count checking.

Test signals: Build with and without address/leak sanitizer refcount checking, verify flexible-array allocation sizes and refcount helper access.
