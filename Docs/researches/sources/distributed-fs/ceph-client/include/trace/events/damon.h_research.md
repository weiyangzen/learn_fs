# sources/distributed-fs/ceph-client/include/trace/events/damon.h

## Purpose
`damon.h` traces DAMON monitoring and DAMOS scheme activity: scheme statistics, estimated size, before-apply details, interval tuning, and aggregated region observations.

## Important APIs, types, and functions
Events are `damos_stat_after_apply_interval`, `damos_esz`, `damos_before_apply`, `damon_monitor_intervals_tune`, and `damon_aggregated`. `damos_before_apply` is conditional on a `do_trace` argument.

## Control flow
DAMON emits aggregate stats after each apply interval, estimated size events for schemes, conditional per-region details before a scheme applies, monitor interval tuning events, and region aggregation events after sampling.

## State and persistence behavior
The header stores no state. Records snapshot context/scheme/target indices, DAMOS stat counters, region start/end/accesses/age, number of regions, estimated size, and sample interval.

## Dependencies and integration points
It depends on `<linux/damon.h>` structures and tracepoint support. It integrates with memory access monitoring, DAMOS policy debugging, and BPF/ftrace consumers.

## Risks and test signals
Risks include high volume when `damos_before_apply` is enabled, potentially sensitive address ranges in traces, and unit confusion between base-point and raw access counters. Test signals are DAMON selftests/workloads with known regions, scheme apply counts, interval tuning, and conditional event suppression when `do_trace` is false.
