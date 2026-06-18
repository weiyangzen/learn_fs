<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip09/sys/uncore-cpa.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip09/sys/uncore-cpa.json

## Purpose
Hip09 system uncore CPA PMU table. It exposes CPA cycles, port 0 and port 1 read/write data counts, width-specific 64-bit and 32-bit read data counts, and derived average bandwidth metrics per port.

## APIs, Types, and Functions
Raw event records use `EventName`, `ConfigCode`, `Unit`, and `Compat`; metric records additionally use `MetricName`, `MetricExpr`, and `MetricGroup`. Aliases include `cpa_cycles`, `cpa_p1_wr_dat`, `cpa_p1_rd_dat`, `cpa_p1_rd_dat_64b`, `cpa_p1_rd_dat_32b`, `cpa_p0_wr_dat`, `cpa_p0_rd_dat`, and metric names `cpa_p1_avg_bw` and `cpa_p0_avg_bw`.

## Control Flow, State, and Persistence
The raw events and metric expressions are compiled into perf metadata. At runtime, perf can program the system uncore PMU by config code and evaluate average bandwidth formulas from data counts and cycles. The JSON contains no runtime persistence.

## Dependencies and Integration
Depends on the Hip09 CPA PMU compatible string, uncore unit naming, and perf metric-expression support. It integrates with system-level bandwidth analysis rather than core CPUID mapping alone.

## Risks and Test Signals
Risks include `Compat` strings not matching kernel PMU device names, bandwidth formulas assuming a fixed cycle/data unit scale, and per-port aggregation being misread as system total bandwidth. Test signals are `perf list` on Hip09, raw event increments under CPA traffic, metric evaluation without missing events, and bandwidth estimates matching external memory or interconnect benchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip09/sys/uncore-cpa.json -->
