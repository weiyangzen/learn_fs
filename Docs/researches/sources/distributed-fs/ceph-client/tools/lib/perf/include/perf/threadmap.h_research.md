<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/threadmap.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/threadmap.h

## Purpose
This public header declares libperf's thread-map API. Thread maps identify target PIDs/TIDs for per-thread perf_event opens and hide the concrete map/refcount layout from callers.

## Important APIs, Types, and Functions
- Constructors are `perf_thread_map__new_dummy()` for a single dummy `-1` entry and `perf_thread_map__new_array(int nr_threads, pid_t *array)`.
- Mutation/query APIs include `set_pid`, `pid`, `comm`, `nr`, and `idx`.
- Refcount APIs are `perf_thread_map__get` and `perf_thread_map__put`.

## Control Flow and State
The public contract treats `NULL` maps similarly to a single dummy thread in some implementation paths. A dummy map initially contains PID `-1`; tests often change it to `0` to target the current thread/process.

## Dependencies and Integration Points
It depends on `perf/core.h` and `sys/types.h`. Evsel and evlist use thread maps to open perf events for selected threads and to index reads by thread slot.

## Risks and Test Signals
Callers must keep indices within `nr`; public accessors do not advertise bounds checking. The returned `comm` pointer is owned by the map. `test-threadmap.c`, `test-evsel.c`, and `test-evlist.c` validate allocation, mutation, lookup, refcounting, and current-thread perf reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/threadmap.h -->
