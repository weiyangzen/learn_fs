<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/cpumap.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/cpumap.h

## Purpose
This public header declares libperf's CPU-map API. It abstracts sets of CPUs, including the special `any CPU` dummy value `-1`, and provides constructors, lifetime management, set operations, queries, and iteration macros.

## Important APIs, Types, and Functions
- `struct perf_cpu` wraps a signed 16-bit CPU number to reduce confusion between CPU IDs and map indices.
- `struct perf_cache` names cache level/index pairs.
- Constructors include `perf_cpu_map__new_any_cpu`, `perf_cpu_map__new_online_cpus`, `perf_cpu_map__new(const char *cpu_list)`, and `perf_cpu_map__new_int`.
- Refcount functions are `perf_cpu_map__get` and `perf_cpu_map__put`.
- Set and query APIs include `merge`, `intersect`, `has`, `equal`, `min`, `max`, `nr`, and several `any CPU`/empty predicates.
- Iteration macros expose all CPUs, skip dummy CPUs, or iterate indices.

## Control Flow and State
The header is declarative; the implementation stores map contents elsewhere. The public contract treats empty maps specially: `perf_cpu_map__nr` returns one so invalid-index reads can behave like the dummy `-1` CPU.

## Dependencies and Integration Points
It depends on `perf/core.h`, `stdbool.h`, and `stdint.h`. Evsel and evlist use CPU maps to decide which perf_event file descriptors to open and which mmaps to allocate.

## Risks and Test Signals
The `-1` dummy value is subtle: APIs distinguish empty, has-any, and is-any-or-empty. Callers must not treat iteration length as a count of real CPUs without checking for `-1`. `test-cpumap.c`, `test-evsel.c`, and `test-evlist.c` exercise online CPU construction, refcounting, iteration, and perf-event reads across mapped CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/cpumap.h -->
