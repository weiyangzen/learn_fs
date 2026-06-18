<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-evsel.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-evsel.c

## Purpose
This suite validates individual evsel behavior: opening events over CPU/thread maps, reading counts, enabling disabled events, user-space mmap counter reads, and multiple `read_format` combinations.

## Important APIs, Types, and Functions
- `test_stat_cpu` opens CPU-clock counters for online CPUs and reads each CPU slot.
- `test_stat_thread` opens task-clock for the current thread.
- `test_stat_thread_enable` verifies disabled events read zero until `perf_evsel__enable`.
- `test_stat_user_read(event)` opens hardware events, mmaps page 0, checks user rdpmc/PMU metadata on supported architectures, and verifies monotonically increasing work-loop counts.
- `test_stat_read_format_single` and `test_stat_read_format_group` verify `PERF_FORMAT_TOTAL_TIME_ENABLED`, `RUNNING`, `ID`, and `LOST` for single and group reads.
- `test_stat_read_format` drives all format combinations.

## Control Flow and State
Each helper creates maps and an evsel, opens kernel fds, optionally mmaps, performs workload loops, reads into `struct perf_counts_values`, then closes/deletes and drops maps. Group tests manually set internal leader/member relationships.

## Dependencies and Integration Points
It depends on Linux perf_event hardware/software events, public libperf APIs, and `internal/evsel.h`. User counter validation is architecture-gated for x86 and arm64.

## Risks and Test Signals
Hardware counter availability, perf_event permissions, kernel support for `PERF_FORMAT_LOST`, and user rdpmc access can affect results. Some helpers skip old-kernel read-format failures by returning success when open fails. The suite is a strong regression signal for evsel read layout and enable/disable semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-evsel.c -->
