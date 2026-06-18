<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v15.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v15.h

## Purpose
This header is an X-macro field list for scheduler statistics version 15. It is included multiple times under macros such as `CPU_FIELD`, `DOMAIN_FIELD`, `DERIVED_CNT_FIELD`, `DERIVED_AVG_FIELD`, and `DOMAIN_CATEGORY` to generate record layouts, formatting tables, or derived metric logic.

## Important APIs, Types, and Functions
- CPU fields include yield count, legacy array expiration, schedule count, go-idle count, wakeup count/local wakeups, runqueue CPU time, run delay, and timeslice count.
- Domain fields cover idle, busy, and newly idle load-balancing counters; active load balance counters; legacy sched-balance exec/fork counters; and wakeup movement counters.
- Derived macros define success counts and average pulled-task metrics when enabled by the includer.

## Control Flow and State
There is no standalone control flow. The includer decides whether the entries generate struct fields, output descriptors, or calculations.

## Dependencies and Integration Points
`event.h` includes this file to build `perf_record_schedstat_cpu_v15` and `perf_record_schedstat_domain_v15`. Other perf schedstat renderers can include it with formatting-oriented macro definitions.

## Risks and Test Signals
Ordering and type widths are ABI-relevant for versioned schedstat records. Version 15 uses aggregate imbalance fields such as `*_lb_imbalance`, unlike v17's split load/util/task/misfit counters. Tests are likely in schedstat/perf record tooling outside this subset; no direct unit test here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v15.h -->
