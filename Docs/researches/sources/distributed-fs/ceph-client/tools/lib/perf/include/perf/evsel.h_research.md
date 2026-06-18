<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/evsel.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/evsel.h

## Purpose
This public header declares the libperf event-selector API. An evsel wraps a `struct perf_event_attr`, the fd matrix produced by opening that event over CPU/thread maps, optional mmaps, and read/enable/disable operations.

## Important APIs, Types, and Functions
- `struct perf_counts_values` stores up to five read outputs: value, enabled time, running time, ID, and lost count.
- Lifecycle: `perf_evsel__new`, `delete`, `open`, `close`, `close_cpu`.
- Mmap access: `perf_evsel__mmap`, `munmap`, `mmap_base`.
- Runtime operations: `read`, `enable`, `enable_cpu`, `enable_thread`, `disable`, `disable_cpu`.
- Accessors expose bound `cpus`, `threads`, and mutable `attr`.
- `perf_counts_values__scale` scales multiplexed counts and reports scaling status through `pscaled`.

## Control Flow and State
The evsel is opened against CPU and/or thread maps, then read by CPU-map index and thread index. Group reads may involve leader/member relationships, and mmap reads expose kernel perf ring-buffer pages.

## Dependencies and Integration Points
It depends on `perf/core.h`, Linux types, and `struct perf_event_attr`. Evlist is a collection wrapper around evsels. Tests reach internal leader fields through `internal/evsel.h` to validate grouping behavior.

## Risks and Test Signals
Read-format handling must match kernel `read_format` combinations, including group reads and `PERF_FORMAT_LOST`. User-space counter reads depend on architecture support and kernel permissions. `test-evsel.c` validates CPU/thread stat reads, disabled/enabled behavior, mmap base access, hardware RDPMC/user reads on supported architectures, and read-format combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/evsel.h -->
