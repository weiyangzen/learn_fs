<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-threadmap.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-threadmap.c

## Purpose
This suite validates public thread-map allocation, default values, PID mutation, and refcount behavior.

## Important APIs, Types, and Functions
- Local `libperf_print` routes diagnostics to stderr.
- `test_threadmap_array(int nr, pid_t *array)` creates a map, verifies size and initial values, mutates entries 1..nr-1, verifies values, and releases the map.
- `test_threadmap` tests dummy map refcounting, a NULL-array map initialized with `-1`, and an explicit PID array.

## Control Flow and State
The dummy map is retained and released twice to validate get/put. Array tests preserve the first element's initial value while changing later slots to `i * 100`.

## Dependencies and Integration Points
It uses `perf/threadmap.h` and the shared test harness. It supports evsel/evlist test coverage because thread maps are required for per-thread perf events.

## Risks and Test Signals
The test does not check `perf_thread_map__idx`, `comm` ownership, invalid indices, or reallocation growth. It does catch allocation, count reporting, default dummy PID behavior, explicit initialization, mutation, and refcount deletion regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-threadmap.c -->
