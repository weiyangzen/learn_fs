<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-record.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/perf-record.c

## Purpose

This selftest records a controlled `sleep 1` workload and validates `PERF_RECORD_*` records plus parsed `perf_sample` fields such as cpu, pid, tid, and monotonic sample time.

## Research

`sched__get_first_possible_cpu` trims the workload affinity mask to one CPU. `test__PERF_RECORD` creates a dummy or default evlist, prepares a workload, enables CPU/TID/TIME sample bits, configures and opens events, mmaps rings, starts the workload, and drains mmap buffers until `PERF_RECORD_EXIT` or timeout. It validates time ordering, cpu affinity, pid/tid consistency, expected comm name, and presence of mappings for the executable or coreutils wrapper, libc, dynamic loader, and vDSO. State includes a prepared workload pid, evlist maps and mmaps, a mutable `perf_sample`, event counters, and booleans for required mmap records. Dependencies include `sys_perf_event_open` permission, scheduler affinity, `sleep`, mmap ring helpers, and kernel record generation. Integration covers record pipeline correctness for workload setup, event parsing, and metadata records. Risks are environment-specific mappings, permissions (`-EACCES` skips), non-coreutils sleep locations, and slow systems hitting the wakeup limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-record.c -->
