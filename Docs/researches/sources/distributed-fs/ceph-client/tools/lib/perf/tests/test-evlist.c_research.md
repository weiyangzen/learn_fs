<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-evlist.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-evlist.c

## Purpose
This suite validates libperf evlist behavior across CPU and thread stat events, event grouping, enable/disable, tracepoint mmap consumption, CPU-affinity event routing, and multiplexed count scaling.

## Important APIs, Types, and Functions
- `test_stat_cpu`, `test_stat_thread`, and `test_stat_thread_enable` create two software evsels in an evlist, set leaders/maps, open, read, enable/disable, and close.
- `test_mmap_thread` opens a `sys_enter_prctl` tracepoint for a forked child, mmaps the evlist, generates 100 `prctl` calls, consumes events, and checks the count.
- `test_mmap_cpus` opens a system-wide tracepoint, iterates online CPUs with `sched_setaffinity`, generates events, and expects at least one per CPU.
- `test_stat_multiplexing` compares a single hardware instruction event against 15 multiplexed events and validates scaled count error within 1%.
- `test_evlist` orchestrates all subtests.

## Control Flow and State
The tests build evlists, add evsels, bind maps, open kernel perf_event fds, enable workloads, read counts or mmap records, then close/delete. Mmap tests use `perf_mmap__read_init`, repeated `read_event`/`consume`, and `read_done`.

## Dependencies and Integration Points
The suite depends on debugfs/sysfs tracepoint IDs, `sched_getaffinity`, `sched_setaffinity`, `fork`, `pipe`, `waitpid`, `prctl`, public libperf headers, and `internal/evsel.h` for leader assertions.

## Risks and Test Signals
These are high-value integration tests but environment-sensitive: perf permissions, tracefs/debugfs mount state, CPU affinity restrictions, hardware event availability, and virtualization can cause failures unrelated to libperf logic. They cover evlist map ownership, grouping, polling/mmap consumption, and scaling behavior more thoroughly than isolated unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-evlist.c -->
