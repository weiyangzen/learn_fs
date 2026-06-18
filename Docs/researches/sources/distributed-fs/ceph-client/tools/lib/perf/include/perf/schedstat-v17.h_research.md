<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v17.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v17.h

## Purpose
This header is the X-macro field list for scheduler statistics version 17. It updates domain imbalance accounting by splitting prior aggregate imbalance counters into load, utilization, task-count, and misfit-task fields.

## Important APIs, Types, and Functions
- CPU fields match v15/v16 categories for scheduling, wakeups, runtime, delay, and timeslices.
- Domain fields include busy/idle/newidle load-balance counts, balanced/failed counts, split imbalance counters, gained/hot-gained counters, no-busy-queue/group counters, active load-balance counters, legacy exec/fork fields, and wakeup movement counters.
- Optional derived count and average macros expose success and average-pull metrics.

## Control Flow and State
Like the other schedstat headers, it has no standalone execution. The including macro definitions determine generated code or data.

## Dependencies and Integration Points
`event.h` uses it for `perf_record_schedstat_cpu_v17` and `perf_record_schedstat_domain_v17`. Version dispatch in schedstat readers must select this schema only for v17 records.

## Risks and Test Signals
The split imbalance fields make v17 structurally different from v15/v16. Reusing earlier parsers would misread subsequent fields. There is no direct unit test here; reliable coverage requires schedstat record fixtures or perf schedstat integration tests across versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v17.h -->
