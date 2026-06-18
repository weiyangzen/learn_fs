# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/metrics.json

## Purpose
`metrics.json` defines 385 derived POWER8 performance metrics for Linux `perf`. Each row gives a user-facing metric name, arithmetic `MetricExpr`, optional `MetricGroup`, and short description. These metrics sit above the raw POWER8 PMU events from the same `power8` directory and let `perf stat -M ...` report higher-level ratios such as CPI components, cache locality, miss latency, branch prediction quality, translation behavior, LSU rejects, SMT mode share, and memory-source distribution.

The file is declarative JSON. It has no functions or mutable state of its own, but its contents become part of generated perf PMU metadata when `tools/perf/pmu-events/jevents.py` scans `arch/powerpc/power8`.

## Important schema and data surface
- Schema: array of objects with `MetricName`, `MetricExpr`, `BriefDescription`, and sometimes `MetricGroup`.
- Count: 385 metric rows.
- Grouped rows cover `branch_prediction`, `bus_stats`, `cpi_breakdown`, `dl1_reloads_percent_per_inst`, `dl1_reloads_percent_per_ref`, `estimated_dcache_miss_cpi`, `general`, `instruction_misses_percent_per_inst`, `instruction_mix`, `instruction_stats_percent_per_ref`, `l2_stats`, `latency`, `lsu_rejects`, `memory`, `pteg_reloads_percent_per_inst`, `pteg_reloads_percent_per_ref`, and `translation`.
- 64 rows are intentionally ungrouped. They include hit ratios, local/remote/distant Centaur memory ratios, L2/L3 machine usage estimates, store-forward ratios, store latency, sync stall CPI, and L3 prefetch waste.
- Three CPI rows lack `BriefDescription`: `mem_ecc_delay_stall_cpi`, `ntcg_all_fin_cpi`, and `ntcg_flush_cpi`.
- Expressions reference 269 unique `PM_*` raw events. A full-directory check across all POWER8 JSON files found all referenced events present in the same CPU directory, even though many dependencies live in sibling files such as `cache.json`, `memory.json`, `marked.json`, `frontend.json`, and `translation.json`.

## Control flow and integration
Build-time flow:
1. `jevents.py` traverses `tools/perf/pmu-events/arch/powerpc`.
2. `arch/powerpc/mapfile.csv` maps POWER8 PVR patterns, including `0x004[bcd][[:xdigit:]]{4}` and `0x0066[[:xdigit:]]{4}`, to the `power8` directory as `core` PMU metadata.
3. `metrics.json` is parsed with the other topic JSON files and encoded into generated perf PMU tables.
4. The generated tables are linked into `perf`; at runtime perf resolves the host CPU to the POWER8 table and exposes symbolic metrics.

Runtime flow is expression evaluation by perf. Users request metric names or groups, perf schedules the needed raw events subject to PMU constraints, reads counts, and evaluates the `MetricExpr` arithmetic.

## State and persistence behavior
The file is persistent source metadata. It does not write state, allocate resources, or hold runtime counters. The persistent effect is indirect: changing a metric name, expression, or group changes generated perf metadata and the user-facing metrics available in built perf binaries.

## Dependencies
- Depends on `jevents.py` and perf PMU-events schema support for metric objects.
- Depends on raw POWER8 event names in the same CPU directory. Local source checks show all referenced `PM_*` names resolve somewhere under `power8/*.json`.
- Depends on POWER8 event semantics such as marked load latency counters, L1/L2/L3 data-source counters, branch predictor counters, GCT occupancy, completion stall counters, and translation reload counters.

## Risks and edge cases
- Division by zero is common in low-sample or filtered workloads because expressions divide by events such as `PM_RUN_INST_CMPL`, `PM_L1_DCACHE_RELOAD_VALID`, `PM_DTLB_MISS`, or marked-event counts. Consumers need perf's metric handling to render unavailable values rather than treating them as source errors.
- Some metrics are difference formulas, for example "other" CPI buckets. Counter skid, multiplexing, or incompatible sampling windows can make those results negative or misleading.
- Several descriptions are missing, terse, or contain typos, and a few formulas encode domain assumptions that deserve scrutiny, such as `l3_no_conflict_latency` dividing `PM_MRK_DATA_FROM_L3_NO_CONFLICT_CYC` by `PM_MRK_DATA_FROM_L2`.
- Metrics rely on sibling raw-event files. Editing only this file can silently break metrics if event names are renamed elsewhere.
- The file has no explicit unit field. Units are implied by names and expressions (`percent`, `cpi`, `latency`, `ratio`), so naming consistency is part of the contract.

## Test signals
- JSON validity: parse as an array and require all rows to contain `MetricName` and `MetricExpr`; separately flag rows missing `BriefDescription`.
- Dependency check: extract `PM_*` tokens from every `MetricExpr` and verify each token appears as an `EventName` in `power8/*.json`.
- Build check: rebuild perf PMU events so `jevents.py` accepts every metric expression.
- Runtime smoke check on POWER8 or compatible fixture: `perf list` should show the metric aliases/groups, and representative `perf stat -M cpi,ipc,run_cpi` style commands should resolve.
- Regression tests should cover representative formulas from each group, especially CPI breakdown, memory locality, marked latency, branch prediction, and translation reload metrics.
