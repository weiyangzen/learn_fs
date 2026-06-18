<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/threadmap.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/threadmap.c

## Purpose
This file implements libperf thread-map allocation, mutation, lookup, and refcounted lifetime management.

## Important APIs, Types, and Functions
- `perf_thread_map__reset` zeroes newly allocated slots and sets `err_thread = -1`.
- `perf_thread_map__realloc` resizes the flexible-array object and resets only newly added entries.
- `perf_thread_map__new_array` allocates `nr_threads` entries, initializes PIDs from the supplied array or `-1`, sets `nr`, and initializes refcount to 1.
- `perf_thread_map__new_dummy` creates a one-entry dummy map.
- `perf_thread_map__delete` warns on unbalanced refcount, frees each `comm`, and frees the map.
- Public accessors/mutators implement get/put, `nr`, `pid`, `comm`, `set_pid`, and linear `idx` lookup.

## Control Flow and State
Maps are contiguous allocations containing header plus flexible array. Ownership is reference-counted. `NULL` maps are treated in accessors as one dummy PID slot for compatibility with callers that omit explicit thread maps.

## Dependencies and Integration Points
It includes public and internal thread-map headers, Linux refcount and bug/assert helpers, libc allocation/string headers, and is consumed by evsel/evlist open/read logic.

## Risks and Test Signals
`perf_thread_map__realloc` assumes growth rather than shrink and can leave callers responsible for preserving old pointers after failed realloc. Accessors do not perform general bounds checks. `comm` strings are freed but not assigned in this file. `test-threadmap.c` validates the primary allocation/refcount/mutation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/threadmap.c -->
