# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/metrics.json

## Purpose
This 17-entry common metrics file defines generic perf-derived metrics: CPU utilization, context-switch/migration/page-fault rates, IPC, stalled cycles per instruction, frontend/backend idle percentages, cycle and branch frequency, branch miss rate, cache miss rates, TLB miss rates, and L1 prefetch miss rate.

## Important Data Fields
Rows use `MetricExpr`, `MetricGroup`, `MetricName`, `ScaleUnit`, and often `MetricConstraint`, `DefaultShowEvents`, and `MetricThreshold`. Some expressions use escaped event names and explicit PMU syntax, such as `software@cpu-clock,...@` for CPU utilization.

## Control Flow And Integration
`jevents.py` parses the formulas through `metric.ParsePerfJson`, simplifies them, and emits generated metric rows. Runtime consumers include `perf stat -M`, `perf list --metrics`, and Python binding export of metric metadata.

## State, Dependencies, Risks, And Tests
The file is shared static state. Dependencies include common software/tool events, legacy hardware aliases, cache/TLB aliases, expression parser syntax, and threshold handling. Risks include parser regressions from escaping, divide-by-zero for rates, unavailable events on some architectures, and thresholds that imply misleading health signals. Test signals are `metric_test.py`, `tests/parse-metric.c`, `perf list --metrics`, and representative `perf stat -M Default` runs.
