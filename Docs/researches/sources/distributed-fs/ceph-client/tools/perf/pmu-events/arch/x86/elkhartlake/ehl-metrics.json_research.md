<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/ehl-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/ehl-metrics.json

## Purpose
Defines eleven Elkhart Lake derived perf metrics. They turn raw events and built-in counters into user-facing formulas for IPC, CPI, clocks, branch density, branch misprediction cost, instruction count, L3 fill bandwidth, CPU utilization, average frequency, turbo utilization, and kernel utilization.

## Important APIs, Types, And Functions
Each object uses `MetricName`, `MetricExpr`, and `BriefDescription`. Expressions reference aliases from other PMU JSON files and perf built-ins: `INST_RETIRED.ANY`, `cycles`, `BR_MISP_RETIRED.ALL_BRANCHES`, `BR_INST_RETIRED.ALL_BRANCHES`, `LONGEST_LAT_CACHE.MISS`, `CPU_CLK_UNHALTED.REF_TSC`, `msr@tsc@`, and the kernel-filtered `cycles:k`.

## Control Flow
During build, `jevents.py` detects `MetricExpr`, parses it through `metric.ParsePerfJson(...).Simplify()`, and emits metric table entries separate from raw event entries. At runtime, perf resolves metric dependencies into the needed event list, programs those events, and evaluates formulas such as `INST_RETIRED.ANY / cycles` for `IPC` and `(cycles / CPU_CLK_UNHALTED.REF_TSC) * msr@tsc@ / 1000000000` for `Average_Frequency`.

## State And Persistence
The file is static; generated metric expressions persist in the compiled perf binary. Runtime state consists of the raw counter readings used to evaluate the formulas.

## Dependencies And Integration Points
Depends on event names from Elkhart Lake `pipeline.json` and `cache.json`, plus perf's synthetic `cycles`, `cycles:k`, and `msr@tsc@` support. The `L3_Cache_Fill_BW` metric specifically depends on `LONGEST_LAT_CACHE.MISS`; branch metrics depend on retired branch and mispredict events.

## Risks And Edge Cases
Formula names must exactly match generated event aliases. Ratios can divide by zero for very short runs or workloads with no branches/mispredicts. `CPU_Utilization`, `Average_Frequency`, and `Turbo_Utilization` depend on reference TSC semantics and may be misleading under virtualization, CPU hotplug, or constrained counter access.

## Test Signals
Run `tools/perf/pmu-events/metric_test.py` or the perf metric parse tests after generation. On hardware, `perf stat -M IPC,CPI,Average_Frequency,Kernel_Utilization` should resolve all dependencies and produce finite values for a non-trivial workload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/ehl-metrics.json -->
