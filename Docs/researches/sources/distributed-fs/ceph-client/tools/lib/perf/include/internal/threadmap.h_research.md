<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/threadmap.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/threadmap.h

## Purpose
This internal header exposes the concrete allocation layout for `struct perf_thread_map`, which is opaque in the public `perf/threadmap.h` API. It supports libperf internals that need direct access to thread IDs, command strings, refcounts, and the flexible-array map.

## Important APIs, Types, and Functions
- `struct thread_map_data` stores a `pid_t pid` and dynamically owned `char *comm`.
- `struct perf_thread_map` stores a `refcount_t`, element count `nr`, `err_thread`, and `map[]` flexible array.
- `perf_thread_map__realloc(struct perf_thread_map *map, int nr)` grows or allocates maps and is implemented in `threadmap.c`.

## Control Flow and State
The header itself has no control flow. Its state contract is ownership-oriented: `comm` strings are freed by `perf_thread_map__delete`, and the map object is lifetime-managed through refcounts.

## Dependencies and Integration Points
It depends on Linux `refcount_t`, `sys/types.h`, and `unistd.h`. Public thread-map functions create and retain these objects; evsel/evlist code consumes them when opening perf events.

## Risks and Test Signals
The flexible-array allocation must match `threadmap.c`; any size or field-order change can break internal users. Tests in `test-threadmap.c` validate dummy and array maps, refcount get/put behavior, PID mutation, and default `-1` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/threadmap.h -->
