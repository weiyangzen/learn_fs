<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v16.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v16.h

## Purpose
This header is the X-macro field list for scheduler statistics version 16. It represents the same broad CPU/domain counter categories as v15 while preserving v16-specific field ordering and derived metric names.

## Important APIs, Types, and Functions
- CPU fields mirror v15: yield, legacy, schedule, go-idle, wakeup, runtime, delay, and timeslice counters.
- Domain categories are busy, idle, newly idle, active load balance, legacy exec/fork balancing, and wakeup information.
- Optional derived macros define load-balance success counts and average pulled-task metrics. In v16 the newly-idle derived average macro is named `newidle_lb_avg_count`.

## Control Flow and State
This file is inert unless included with field macros. It is a schema source for generated structs or display metadata.

## Dependencies and Integration Points
`event.h` uses it to generate `perf_record_schedstat_cpu_v16` and `perf_record_schedstat_domain_v16`. It must remain aligned with any parser/renderer that interprets schedstat version 16 payloads.

## Risks and Test Signals
The most important risk is accidental normalization across versions. Even small ordering or name changes would corrupt record interpretation or output. There is no direct test in this subset; consumers should compare generated layouts and parsed scheduler-stat output for v16 kernels or fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v16.h -->
