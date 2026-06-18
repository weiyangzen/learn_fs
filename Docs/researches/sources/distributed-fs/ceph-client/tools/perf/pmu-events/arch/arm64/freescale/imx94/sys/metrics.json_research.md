<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx94/sys/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx94/sys/metrics.json

## Purpose
Provides 56 derived perf metrics for the NXP/Freescale SoC DDR uncore PMU model, covering derived perf metrics. The entries expose user-facing `MetricName` aliases such as imx94_bandwidth_usage.lpddr5, imx94_bandwidth_usage.lpddr4, imx94_ddr_read.all, imx94_ddr_write.all, imx94_ddr_read.a55_all, imx94_ddr_write.a55_all, imx94_ddr_read.a55_0, imx94_ddr_write.a55_0, imx94_ddr_read.a55_1, imx94_ddr_write.a55_1, and 46 more and translate raw events into ratios, byte counts, percentages, or bandwidth utilization values.

## APIs, Types, and Functions
The exported API is declarative metric metadata: `MetricName`/`MetricExpr` formulas, `Unit` PMU selectors, `Compat` filters. Metric expressions are perf JSON formulas parsed by `metric.ParsePerfJson()` and may reference raw events, architecture-standard aliases, PMU filter syntax, and `duration_time`. Example metric names include `imx94_bandwidth_usage.lpddr5`, `imx94_bandwidth_usage.lpddr4`, `imx94_ddr_read.all`, `imx94_ddr_write.all`, `imx94_ddr_read.a55_all`. Metric groups are not explicitly grouped.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON itself. Build-time flow is: perf scans the architecture directory, loads this file, parses each `MetricExpr`, validates event/PMU references, then emits generated metric tables into `pmu-events.c`. Runtime state is limited to hardware counters sampled by perf; this repository file persists only the metric definitions. The i.MX8 metric formulas multiply DDR read/write cycle events by bus width factors, while i.MX9 formulas compose raw `imx9_ddr0@...@` filtered events, beat counts, and `duration_time` for bandwidth utilization.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx9_ddr`, compatible string `imx94`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are malformed `MetricExpr`, stale event references, divide-by-zero denominators, or wrong scale units can make derived metrics invalid; incorrect `Compat` values prevent uncore events from matching the target device; AXI mask/id filters are easy to transpose between SoC revisions. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, metric parser coverage via `tools/perf/pmu-events/metric_test.py`, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx94/sys/metrics.json -->
