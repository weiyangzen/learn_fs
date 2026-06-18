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
