# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/bdw-metrics.json

## Purpose
Broadwell PMU metric definition table for Linux `perf`. The file is a JSON array of 146 derived metrics used by the perf PMU-events generator to expose human-readable `perf stat -M ...` metrics for Broadwell x86 systems. It does not implement executable control flow; its behavior is expressed through perf metric schema fields and formulas.

The metrics cover power residency, SMI accounting, top-down microarchitecture analysis (`tma_*`), memory hierarchy behavior, floating-point throughput, frontend/backend bottlenecks, branch speculation, SMT/core-level normalization, OS/kernel utilization, and SoC/uncore bandwidth/frequency views. Many metrics are grouped under `TopdownL1` through `TopdownL6`, `TmaL*`, `Mem`, `Flops`, `Power`, `Summary`, `Pipeline`, `PortsUtil`, `FetchLat`, and related issue tags.

## Important APIs, Types, and Functions
The data contract is the perf PMU-events metric object schema:

- `MetricName`: exported symbolic metric name such as `tma_frontend_bound`, `tma_backend_bound`, `tma_info_thread_ipc`, `C7_Pkg_Residency`, or `UNCORE_FREQ`.
- `MetricExpr`: perf expression language formula. Expressions reference raw events from neighboring Broadwell event files, MSR/PMU aliases such as `msr@tsc@`, cstate aliases such as `cstate_pkg@c2-residency@`, uncore events such as `UNC_CLOCK.SOCKET`, constants like `#SMT_on` and `#num_cpus_online`, and helper metrics defined in this same file.
- `MetricGroup`: semicolon-separated grouping/indexing tags used by perf to list and select related metrics.
- `BriefDescription`: short text shown by perf metric listing/help.
- `ScaleUnit`: optional output unit, commonly `100%` for ratios or `1SMI#` for SMI count.

There are no functions or local types, but the metrics form a dependency graph. Base helper metrics such as `tma_info_thread_clks`, `tma_info_core_core_clks`, `tma_info_thread_slots`, `tma_info_system_time`, and `tma_info_inst_mix_instructions` feed higher-level ratios. Level-1 top-down categories are `tma_frontend_bound`, `tma_bad_speculation`, `tma_retiring`, and `tma_backend_bound`; later levels refine them into branch resteers, memory bound, core bound, frontend latency/bandwidth, ports utilization, FP vector/scalar use, and cache/TLB/store bottlenecks.

## Control Flow
Runtime control is owned by perf, not this file. During build or installation, perf's PMU-events tooling ingests this JSON with the other Broadwell tables and emits compiled metric maps. At collection time, perf resolves a requested metric group/name, parses `MetricExpr`, schedules the referenced events, substitutes runtime constants such as SMT state and CPU count, evaluates conditional expressions, and scales the result according to `ScaleUnit`.

The implicit control flow within the data is dependency ordering. For example, `tma_backend_bound` depends on the other L1 top-down metrics, `tma_core_bound` subtracts `tma_memory_bound` from backend bound, `tma_fetch_bandwidth` subtracts `tma_fetch_latency` from frontend bound, and detailed memory metrics reuse helper quantities like `tma_info_memory_load_miss_real_latency`. Conditional expressions handle SMT/core-wide differences, such as formulas switching between `CPU_CLK_UNHALTED.THREAD_ANY`, `CPU_CLK_UNHALTED.THREAD`, or divided core-wide counts.

## State and Persistence Behavior
The file is static architecture metadata. Persistent state is the checked-in JSON content and any generated perf tables derived from it. At runtime, metric values are ephemeral and depend on scheduled PMU readings, MSR readings, cstate counters, uncore counters, elapsed time, SMT topology, CPU online count, and multiplexing accuracy. No state is written back to this JSON.

Because metrics reference each other by name, renames or removals are persistent API changes: downstream metric formulas and user scripts using `perf stat -M` can break even though the JSON remains syntactically valid.

## Dependencies and Integration Points
This file integrates with the perf PMU-events subsystem under `tools/perf/pmu-events/arch/x86/broadwell`. It depends on event names defined across other Broadwell JSON files, including cache/memory events (`L1D_PEND_MISS.*`, `L2_RQSTS.*`, `MEM_LOAD_UOPS_RETIRED.*`, `OFFCORE_REQUESTS*`, `OFFCORE_RESPONSE.*`), frontend events (`IDQ*`, `ICACHE.*`, `DSB2MITE_SWITCHES.*`, `BACLEARS.*`), floating-point events (`FP_ARITH_INST_RETIRED.*`, `FP_ASSIST.*`, `OTHER_ASSISTS.*`), core pipeline/speculation events from other Broadwell tables, MSR/cstate aliases, uncore events, and perf expression variables.

The metrics also integrate with Intel Top-down Microarchitecture Analysis naming conventions. `MetricGroup` tags let `perf list` and `perf stat -M` expose hierarchical analysis groups rather than forcing users to know every individual event.

## Risks
Important risks are semantic rather than memory-safety related:

- Formula drift: a referenced event name must exist in the generated Broadwell event map. Missing or renamed events cause metric evaluation failures.
- Division by zero: several expressions divide by event totals such as retired instructions, load/store counts, or branch counts. Perf expression handling must tolerate zero-denominator workloads.
- Multiplexing accuracy: large metrics reference many events, so limited counters can require multiplexing. `tma_info_system_mux` exists as an accuracy signal, but derived metrics can still be misleading under heavy multiplexing.
- SMT normalization: formulas condition on `#SMT_on` and divide core-wide counts by two in places. Wrong topology detection or collection scope can skew ratios.
- Offcore programming constraints: formulas referencing `OFFCORE_RESPONSE.*` rely on special MSR programming described in `cache.json`; only limited offcore filters can be scheduled concurrently.
- Architectural specificity: these formulas are Broadwell-specific. Reusing them for another x86 generation can produce unsupported event selections or wrong top-down slot math.
- Typographical risk: expression strings are not type checked by a compiler in this source file; mistakes in event names, escaped perf syntax, or group tags are caught only by tooling/tests.

## Test Signals
Useful validation signals include `jq` syntax validation, perf PMU-events build success, generated metric map tests for Broadwell, and runtime smoke tests such as `perf list metric`, `perf stat -M tma_frontend_bound,tma_backend_bound,tma_retiring,tma_bad_speculation`, and `perf stat -M tma_info_thread_ipc,tma_info_system_mux`. Cross-file tests should ensure every event token referenced in `MetricExpr` resolves to an event or a known perf variable/helper metric, top-down L1 categories are schedulable together, power/cstate metrics work on systems exposing the required MSRs, and offcore-dependent metrics either collect correctly or fail with a clear unsupported-event diagnostic.
