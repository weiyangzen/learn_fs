# subset-b-006624 Research

Grouped research for `subset-b-006624`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/recommended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/recommended.json

## Purpose

This file is the recommended AMD Zen 6 PMU metric catalog consumed by Linux `perf`'s `pmu-events` generation pipeline. It is declarative performance-analysis data rather than executable code. The file contains 48 metric records that define user-facing derived metrics for Zen 6 systems selected through the x86 PMU event mapping.

The metrics focus on common first-pass workload diagnosis: branch prediction, L1 data cache behavior, L2 and L3 cache activity, instruction and data TLB misses, decoder dispatch, mixed SSE/AVX stalls, retired macro-ops, and unified memory-controller bandwidth and command-rate indicators.

## Important Schema Fields

Each record follows the perf PMU events metric schema parsed by `tools/perf/pmu-events/jevents.py`:

- `MetricName` is the stable name exposed to `perf stat -M` and metric-group selection.
- `BriefDescription` is the short help text shown by perf metric listing commands.
- `MetricExpr` is the perf metric expression. It references AMD event aliases such as `ex_ret_brn_misp`, `l2_request_g1.dc_all`, `l3_lookup_state.l3_miss`, `ls_l1_d_tlb_miss.all`, and UMC events such as `umc_cas_cmd.rd`.
- `MetricGroup` classifies metrics into groups including `branch_prediction`, `l1_dcache`, `l2_cache`, `l3_cache`, `tlb`, `decoder`, and `memory_controller`.
- `ScaleUnit` controls presentation scaling, for example `1e3per_1k_instr`, `100%`, `1ns`, `1MB/s`, and `1per_memclk`.
- `PerPkg` is set on the memory-controller metrics so perf treats those UMC-derived metrics as package-scoped rather than per-core metrics.

The file intentionally does not define `Unit`, `MetricThreshold`, `PublicDescription`, `MetricConstraint`, or `MetricgroupNoGroup`; it is simpler than the Intel Topdown metric catalogs and mostly provides direct ratios or per-instruction normalizations.

## Metric Families

The branch metric `branch_misprediction_rate` computes a non-speculative retired-branch misprediction ratio with `d_ratio(ex_ret_brn_misp, ex_ret_brn)`.

The L1 data-cache family reports total data-cache accesses, demand data-cache fills by source, and all L1 fills per thousand instructions. These formulas normalize against `instructions`, with source breakdowns for local L2, same CCX, near/far cache, near/far DRAM or MMIO, and remote NUMA nodes.

The L2 family is the largest block. It reports accesses, misses, and hits per thousand instructions, split by source: L1 instruction-cache misses, L1 data-cache misses, and L2 hardware prefetcher activity. Several formulas aggregate request, prefetch-hit, and prefetch-miss aliases so that "all" metrics include both demand and hardware-prefetch traffic.

The L3 family exposes raw L3 accesses and misses through `l3_lookup_state`, plus average read-miss latency metrics using sampled latency counters. The latency formulas multiply sampled latency by 10 and divide by sampled request counts for all misses, local DRAM, and remote DRAM.

The TLB family reports L1/L2 instruction TLB misses, L1/L2 data TLB misses, and TLB flushes per thousand instructions. Instruction-side misses combine L1 miss plus L2 hit/miss events; data-side misses derive from `ls_l1_d_tlb_miss` aliases.

The remaining core metrics expose decoder dispatch (`de_src_op_disp.all`), mixed SSE/AVX stalls (`fp_disp_faults.sse_avx_all`), and retired macro-ops (`ex_ret_ops`). These lack `MetricGroup` for the latter two records, so they are addressable by metric name but not discoverable through a named group in this file.

The UMC metrics are package-scoped memory-controller indicators. They calculate data-bus utilization, CAS/ACTIVATE/PRECHARGE command rates, read/write CAS ratios, and estimated read/write/combined memory bandwidth using 64-byte command assumptions and `duration_time`.

## Control Flow and Evaluation

The JSON has no internal runtime control flow, but it becomes part of perf's generated metric tables:

1. The perf build runs `tools/perf/pmu-events/jevents.py` over the x86 PMU event tree.
2. `jevents.py` loads this file as JSON records, maps schema fields, and parses every `MetricExpr` through the perf metric expression parser.
3. Generated C tables are compiled into perf and selected at runtime for Zen 6 PMU model mappings.
4. When a user requests a metric or metric group, perf resolves all referenced event aliases, schedules the counters, evaluates the expression, applies `ScaleUnit`, and prints the result.

The expression language uses arithmetic and helpers such as `d_ratio(...)` to provide safer ratio handling. There are no explicit `if` expressions or threshold expressions in this file.

## State and Persistence

This file is persistent source-tree data. It does not mutate runtime state, write files, or own memory. Its durable effects are indirect: during a perf build, these metric definitions are embedded into generated PMU-event tables, and at runtime the metric names, groups, formulas, units, and package-scoping metadata become user-visible perf behavior.

Metric values themselves are ephemeral readings from current PMU, UMC, and synthetic `duration_time` counters. Changes to `MetricName`, `MetricGroup`, or formulas can break user scripts that depend on `perf stat -M` names or group names.

## Dependencies and Integration Points

Primary integration points are `tools/perf/pmu-events/jevents.py`, the perf metric expression parser, the generated `pmu-events.c` tables, and the x86 PMU mapfile that selects the `amdzen6` directory for matching AMD CPUs.

The metric expressions depend on neighboring AMD Zen 6 event JSON files to define aliases for branch, load/store, L2, L3, TLB, floating-point, decoder, instruction-retirement, and UMC counters. Runtime resolution also depends on kernel perf support for AMD core PMUs, uncore/UMC PMUs, package-scoped events, and synthetic variables such as `instructions` and `duration_time`.

## Risks and Edge Cases

- Many ratios divide by `instructions`, sampled request counts, memory clocks, or `duration_time`. `d_ratio(...)` is used for some ratios, but several expressions use direct division and rely on perf's metric evaluator to handle zero or unavailable denominators.
- UMC bandwidth estimates assume 64 bytes per CAS command. That is a useful convention but can mislead on unusual memory modes, partial writes, or platform-specific controller behavior.
- The L2 "all" metrics aggregate demand and prefetch aliases. If event definitions change, the aggregate can double-count or omit traffic.
- L3 latency metrics depend on sampled latency request events. Low sample counts can make results noisy, and the `ScaleUnit` of `1ns` should be checked against the expression's "core clocks" description.
- Records without `MetricGroup` are harder to discover through group listing.
- `PerPkg` memory-controller metrics require package-aware scheduling. Running them in per-core contexts or on systems without exposed UMC PMUs can fail or produce absent values.

## Test Signals

Useful validation signals are:

- `jq empty sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/recommended.json` succeeds.
- `jq 'length'` reports 48 records, and every record has `MetricName`, `BriefDescription`, and `MetricExpr`.
- A perf build regenerates PMU event tables without metric parser errors.
- `perf list metric` on Zen 6 hardware shows the expected groups, especially `l1_dcache`, `l2_cache`, `l3_cache`, `tlb`, and `memory_controller`.
- Runtime smoke tests for `branch_misprediction_rate`, `all_l2_cache_accesses_pti`, `l3_read_miss_latency`, and `umc_mem_bandwidth` resolve their event aliases.
- Package-scoped UMC metrics should be tested on single-socket and multi-socket systems to verify `PerPkg` behavior.
- Cache and TLB per-thousand-instruction metrics should remain finite on short workloads and should scale plausibly when workload memory locality changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/recommended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/arl-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/arl-metrics.json

## Purpose

This file is the Intel Arrow Lake PMU metric catalog consumed by Linux `perf`'s `pmu-events` build pipeline. It is declarative metric logic, not executable source. The file contains 337 metric records for Arrow Lake systems and models the platform as a hybrid CPU with separate `cpu_atom` and `cpu_core` PMU domains plus unscoped package, MSR, C-state, power, and uncore metrics.

The catalog exposes high-level default Top-Down Microarchitecture Analysis metrics, deeper TMA hierarchy nodes, bottleneck summaries, memory and frontend diagnostics, branch and speculation metrics, power and C-state residency metrics, SMI accounting, floating-point and instruction-mix summaries, and system-level utilization/frequency/bandwidth metrics.

## Important Schema Fields

The records use the perf PMU events metric schema:

- `MetricName` is the user-visible metric identifier. Some names intentionally appear once for `cpu_atom` and again for `cpu_core`, such as `tma_backend_bound`, `tma_bad_speculation`, `tma_frontend_bound`, `tma_branch_mispredicts`, `tma_itlb_misses`, `tma_machine_clears`, and `tma_retiring`.
- `MetricExpr` is the metric expression parsed by perf. It can reference raw event aliases, hybrid PMU names, other metrics, runtime variables, constants, uncore symbols, C-state counters, MSR counters, and conditional helpers.
- `Unit` scopes most entries to `cpu_atom` or `cpu_core`. The file has 91 `cpu_atom` records, 236 `cpu_core` records, and 10 unscoped C-state/SMI records.
- `MetricGroup` is a semicolon-separated discovery and grouping tag list. Frequent tags include `TopdownL1` through `TopdownL6`, `tma_L*_group`, `Default`, `Mem`, `MemoryTLB`, `FetchLat`, `FetchBW`, `Offcore`, `Branches`, `Flops`, `Power`, `Summary`, and `HPC`.
- `MetricThreshold` is present on 191 records and provides perf with boolean expressions for highlighting notable bottlenecks.
- `MetricConstraint` is present on 6 records and restricts scheduling or threshold/NMI use for metrics such as data sharing, lock latency, other light ops, and port-utilization details.
- `MetricgroupNoGroup` is present on 22 records and `DefaultMetricgroupName` on 8 records, controlling how high-level default and topdown groups are presented.
- `PublicDescription` is present on 113 records and carries longer user-facing descriptions for complex metrics.
- `ScaleUnit` is often `100%`, but some records are raw ratios, rates, latencies, bandwidth estimates, frequencies, or counts.

## Metric Families

The unscoped opening block defines package/core C-state residency metrics using `cstate_pkg@...@` and `cstate_core@...@` divided by `msr@tsc@`, plus SMI metrics based on `msr@smi@`, `msr@aperf@`, and `cycles`.

The `cpu_atom` block defines E-core topdown metrics. L1 categories use `TOPDOWN_BE_BOUND`, `TOPDOWN_BAD_SPECULATION`, `TOPDOWN_FE_BOUND`, and `TOPDOWN_RETIRING` events normalized by `8 * CPU_CLK_UNHALTED.CORE`. Lower-level entries split those categories into branch mispredicts, machine clears, frontend latency and bandwidth, branch detect/resteer, icache misses, decode/CISC stalls, core/resource bound, register/reorder-buffer limits, scheduler pressure, serialization, memory scheduler stalls, and related info metrics for IPC, CPI, uops per instruction, branch mix, FP mix, memory mix, and system utilization.

The `cpu_core` block is larger and defines P-core topdown logic. Its L1 categories divide `topdown-fe-bound`, `topdown-bad-spec`, `topdown-retiring`, and `topdown-be-bound` by their sum. Subsequent levels expand into frontend fetch latency/bandwidth, bad speculation, retiring/heavy/light operations, backend core and memory bound, cache and DRAM bound, TLB bound, branch resteers, CISC/microcode, DSB/MITE/LSD fetch paths, port utilization, divider pressure, FP/int vector mix, stores, locks, false sharing, data sharing, split accesses, and page-walk behavior.

The system and SoC metrics derive CPU utilization, CPUs utilized, kernel utilization, turbo utilization, core and uncore frequency, package power, DRAM bandwidth use, socket clocks, runtime, GFLOPS, and multiplexing indicators. These expressions reference `duration_time`, `msr@tsc,cpu=cpu_core@`, `power@energy-pkg@`, `UNC_CLOCK.SOCKET`, `UNC_M_TOTAL_DATA`, and online CPU/die variables.

Many Arrow Lake metrics are intentionally synthetic. Examples include bottleneck rollups such as useful work, big code, mispredictions, branching overhead, memory latency, memory bandwidth, memory data TLBs, synchronization, compute bound, irregular overhead, and other bottlenecks. These depend on other `tma_*` metrics and often use `min(...)`, `max(...)`, or conditional expressions to prevent negative or impossible component values.

## Control Flow and Evaluation

The JSON file has no imperative control flow, but perf evaluates it as a dependency graph:

1. The perf build runs `tools/perf/pmu-events/jevents.py` over the x86 PMU events tree.
2. `jevents.py` loads each JSON record, copies schema fields, parses `MetricExpr` with the metric expression parser, and emits generated C data.
3. Runtime CPU identification selects the generated Arrow Lake metric table.
4. A requested metric or metric group pulls in all referenced raw events and dependent metrics.
5. perf schedules counters on the appropriate PMU domain, honoring `Unit`, hybrid PMU names, uncore/power/MSR sources, and `MetricConstraint`.
6. perf evaluates the expression graph, applies scale units, and evaluates threshold expressions for highlighting.

Expression-level control logic is important in this file. Formulas use `if ... else`, `min(...)`, `max(...)`, `has_event(...)`-style availability patterns in nearby catalogs, SMT and topology variables, event modifiers such as user/kernel qualifiers, and direct cross-metric references. Threshold strings are separate boolean expressions and should not be assumed to follow the same parser simplification path as `MetricExpr`.

## State and Persistence

The file persists Arrow Lake metric definitions in the source tree. It does not mutate counters, store runtime state, or perform IO by itself. Its persistent build effect is that perf embeds these names, groups, descriptions, constraints, and formulas into generated PMU-event tables.

At runtime, metric values are ephemeral results from current PMU, MSR, C-state, power, uncore, and synthetic time/topology counters. Metric names and groups are effectively user-facing API: renames, unit changes, formula changes, and group membership changes can affect scripts, dashboards, and documentation that invoke `perf stat -M` or metric groups.

## Dependencies and Integration Points

Primary integration points are `tools/perf/pmu-events/jevents.py`, the perf metric expression parser, generated `pmu-events.c` tables, `pmu-events.h`, perf metric-group runtime code, and `tools/perf/pmu-events/arch/x86/mapfile.csv` entries that associate Arrow Lake CPUIDs with the `arrowlake` directory.

The expressions depend on adjacent Arrow Lake event alias files for `cpu_atom@...@`, `cpu_core@...@`, uncore, memory, branch, frontend, pipeline, floating-point, topdown, and power-related events. Runtime support also depends on Linux exposing hybrid PMUs, MSR aliases, C-state PMUs, RAPL/power counters, uncore clocks and memory counters, kernel/user event modifiers, and synthetic variables such as `duration_time`, `#num_cpus_online`, and `#num_dies`.

## Risks and Edge Cases

- Hybrid duplicate metric names are intentional but fragile. Resolution must preserve `Unit` context so a `cpu_atom` formula is not mixed with a `cpu_core` formula of the same `MetricName`.
- Cross-metric dependency depth is high. Renaming or removing a low-level `tma_*` metric can break high-level bottleneck summaries and threshold conditions far away in the file.
- Scheduling pressure is significant. Large metric groups can require many counters across core, atom, uncore, MSR, power, and C-state PMUs, increasing multiplexing and reducing accuracy.
- Several metrics use `MetricConstraint` because grouped scheduling or threshold/NMI use would be invalid or misleading. Those constraints need runtime coverage, not just JSON validation.
- Division by zero and missing-event behavior are common risks. Many formulas divide by clocks, retired instructions, L1 misses, event counts, or `duration_time`; some guard with conditionals, `min`, or `max`, while others rely on perf evaluator behavior.
- Threshold expressions are numerous and user-visible. Syntax mistakes, precedence surprises, or references to metrics unavailable in a PMU domain can surface only when thresholds are evaluated.
- Uncore, power, C-state, and MSR metrics depend on platform firmware, permissions, kernel drivers, and counter availability. On restricted systems, SoC/power/bandwidth/frequency metrics may fail even when core TMA metrics work.
- Some formulas are heuristic approximations. Bottleneck rollups, memory latency estimates, bandwidth estimates, false sharing, data sharing, and synchronization metrics can overlap siblings or exceed intuitive parent percentages under multiplexing or low sample counts.

## Test Signals

Useful validation signals are:

- `jq empty sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/arl-metrics.json` succeeds.
- `jq 'length'` reports 337 records, with `MetricName`, `BriefDescription`, and `MetricExpr` present on every record.
- Field-count sanity remains stable unless intentionally changed: 91 `cpu_atom` records, 236 `cpu_core` records, 10 unscoped records, 191 thresholded records, 6 constrained records, 22 `MetricgroupNoGroup` records, 8 default-group records, and 113 public descriptions.
- A perf build regenerates PMU-event tables without metric parser exceptions.
- Duplicate `MetricName` review confirms duplicates are only expected cross-domain metrics, not same-domain accidental collisions.
- `perf list metric`, `perf list TopdownL1`, and `perf list Default` on Arrow Lake expose expected core and atom metrics.
- Runtime smoke tests for `tma_backend_bound`, `tma_frontend_bound`, `tma_bad_speculation`, and `tma_retiring` should resolve separately for hybrid PMU domains.
- Multiplexing checks should monitor `tma_info_system_mux`; values far from 1.0 indicate counter pressure affecting metric quality.
- Constraint-sensitive metrics such as `tma_data_sharing`, `tma_lock_latency`, and port-utilization metrics should be exercised with grouped and ungrouped scheduling.
- Topdown L1 percentages should generally sum close to 1 per PMU domain, allowing for approximation, unavailable counters, and multiplexing noise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/arl-metrics.json -->
