# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/transaction.json

## Purpose
Defines a single zEC12 derived metric named `transaction` that reports total transactional-execution activity.

## APIs, Types, and Functions
The metric record has `BriefDescription`, `MetricName: transaction`, and a `MetricExpr` summing `TX_C_TEND`, `TX_NC_TEND`, `TX_NC_TABORT`, `TX_C_TABORT_SPECIAL`, and `TX_C_TABORT_NO_SPECIAL`.

## Control Flow, State, and Persistence
At build time perf parses the metric expression and stores it in generated tables. At runtime perf schedules the referenced counters from zEC12 `extended.json`, collects counts, and reports their sum. There is no `has_event()` guard in this older metric, so all referenced event aliases must resolve.

## Dependencies and Integration
Depends directly on zEC12 `extended.json` transaction aliases and on perf metric expression parsing. It also depends on the kernel being able to schedule the required CPU-M-CF counters together or in a valid multiplexed configuration.

## Risks and Test Signals
Risks include hard failure on systems where one transaction event is unavailable, counter scheduling constraints, and division-free but still semantically broad aggregation of committed and aborted transactions. Test signals are metric parser success, `perf list -M transaction`, and hardware `perf stat -M transaction` on zEC12.
