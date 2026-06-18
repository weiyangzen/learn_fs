<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/evlist.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/evlist.h

## Purpose
This public header declares the libperf event-list API. An evlist owns an ordered collection of event selectors, shared CPU/thread maps, poll descriptors, and optional mmap buffers.

## Important APIs, Types, and Functions
- List management: `perf_evlist__new`, `delete`, `add`, `remove`, and `next`.
- Runtime operations: `open`, `close`, `enable`, `disable`, `poll`, and `filter_pollfd`.
- Map binding: `perf_evlist__set_maps(cpus, threads)`.
- Mmap lifecycle: `perf_evlist__mmap`, `munmap`, `next_mmap`, and the mmap iteration macro.
- Group helpers: `perf_evlist__set_leader` and `perf_evlist__nr_groups`.
- `perf_evlist__for_each_evsel` and `perf_evlist__for_each_mmap` provide public iteration syntax.

## Control Flow and State
The implementation iterates over evsels, opens each event against configured maps, controls all fds together, and exposes poll/mmap traversal. Group leadership ties later evsels to the first selector unless grouping rules create more groups.

## Dependencies and Integration Points
It depends on `perf/core.h` and forward-declared evsel, CPU-map, thread-map, and mmap types. Tests build evlists with software counters and tracepoints, set maps, open, enable, read, mmap, and delete them.

## Risks and Test Signals
Evlist correctness depends on coordinated ownership of maps, evsels, fds, poll descriptors, and mmaps. Tracepoint mmap tests require debugfs/sysfs event IDs and can fail on restricted hosts. `test-evlist.c` is the main signal for group leadership, CPU/thread stat reads, enable/disable, mmap event consumption, and multiplex scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/evlist.h -->
