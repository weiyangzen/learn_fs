# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/metrics.json

## Purpose

This file defines 168 derived perf metrics for IBM POWER10 core PMU analysis. It is metadata, not executable code: each array entry names a metric and provides a `MetricExpr` that perf can parse into counter expressions. The metrics cover run-cycle rate, CPI and IPC, dispatch/issue/execution/completion stalls, instruction fetch misses, dL1 reload source attribution, memory locality, branch behavior, DERAT/DTLB translation behavior, and per-instruction operation rates.

## APIs, types, and schema

The effective API is the perf PMU JSON metric schema consumed by `tools/perf/pmu-events/jevents.py`. Entries use `MetricName`, `MetricExpr`, `MetricGroup`, `BriefDescription`, and `ScaleUnit`. There are no `EventCode` fields because this file does not define raw events; it defines formulas over event names such as `PM_RUN_CYC`, `PM_INST_CMPL`, `PM_EXEC_STALL_*`, `PM_DATA_FROM_*`, `PM_DERAT_MISS_*`, and `PM_INST_FROM_*`. Metric groups include `General`, `CPI`, `CPI;CPI_STALL_RATIO`, `Others`, `dL1_Reloads`, `Memory`, `Instruction_Stats`, `Instruction_Misses`, and `Translation`.

## Control flow and integration

At build time, perf's PMU event generation scans the `pmu-events/arch/powerpc` tree, parses metric expressions through the metric parser, and emits generated `pmu-events.c`. At runtime, perf list and metricgroup code expose these metrics by `MetricName` and group, and metric evaluation schedules the referenced raw events. The ordering is declarative: base metrics such as `CYCLES_PER_INSTRUCTION`, `IPC`, `RUN_CPI`, and `RUN_IPC` sit next to decompositions that divide stall counters by `PM_RUN_INST_CMPL` or miss counters by completed instructions.

## State and persistence

The file has no runtime state. Its persistent effect is compiled into generated perf event tables. Any change to metric names, groups, formulas, or scale units changes user-visible perf metric names and calculated values for POWER10 systems. The file also has one duplicate `MetricName`, `DISPATCH_STALL_FETCH_CPI`, appearing in the CPI group with the same expression pattern as part of two nearby stall lists; this is a persistence risk because generated lookup behavior may depend on duplicate-name handling.

## Dependencies

The formulas depend on corresponding POWER10 raw event definitions in sibling files such as `pipeline.json`, `pmc.json`, `translation.json`, and `others.json`, plus broader POWER PMU event availability. The metric parser must accept infix arithmetic, parentheses, percentages, and semicolon-separated metric groups. Consumers include `pmu-events/jevents.py`, `pmu-events/metric.py`, `util/metricgroup.h`, `util/pmu.c`, `builtin-list.c`, and the Python perf bindings that expose `MetricName` and `MetricExpr`.

## Risks

Many expressions divide by counters such as `PM_RUN_INST_CMPL`, `PM_LD_REF_L1`, `PM_L1_ICACHE_MISS`, `PM_LD_DEMAND_MISS_L1`, and `PM_DERAT_MISS` without the `1 + denominator` guard seen in some nest metrics. Short or filtered workloads can produce zero denominators. Spelling is part of the API, so typos such as `EXEC_STALL_UNKOWN_CPI` are user-visible even if historically intentional. Formula correctness also depends on every referenced event being present for POWER10 and correctly categorized in raw event JSON.

## Test signals

Useful checks are `jq` validity, uniqueness checks for `MetricName`, perf's PMU generation target, `pmu-events/metric_test.py`, and runtime `perf list --metrics` or `perf stat -M <MetricName>` on POWER10 hardware. Regression tests should verify expression parse success, referenced event resolution, group membership, and stable scale-unit behavior for percent metrics.
