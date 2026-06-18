# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/recommended.json

## Purpose

`amdzen4/recommended.json` defines 62 recommended Zen 4 perf events and metrics. It aggregates commonly used branch, cache, TLB, decoder, floating-point stall, data-fabric, and memory-controller counters into stable aliases and formulas.

## Important records and schema

The file mixes raw event aliases and derived metric records:

- Raw event aliases use `EventName`, `EventCode`, `UMask`, and `BriefDescription`.
- Metrics use `MetricName`, `MetricExpr`, `MetricGroup`, optional `ScaleUnit`, optional `PerPkg`, and `BriefDescription`.

Important metric groups and examples include:

- `branch_prediction`: `branch_misprediction_ratio`.
- `l2_cache` and `l3_cache`: all L2 accesses/misses/hits, L2 source splits, L3 accesses/misses, and `l3_read_miss_latency`.
- `l1_dcache`: L1 fills from memory, remote node, same CCX, different CCX, all fills, and demand fill source splits.
- `tlb`: L1/L2 ITLB misses, L1/L2 DTLB misses, and all TLB flushes.
- `decoder`: `macro_ops_dispatched`; standalone execution aliases include `sse_avx_stalls` and `macro_ops_retired`.
- `data_fabric`: DRAM read/write data for local/remote processors, local/remote upstream DMA traffic, socket inbound/outbound CPU data, and outbound link sums.
- `memory_controller`: UMC data bus utilization, CAS command rates and read/write ratios, estimated bandwidth, ACTIVATE command rate, and PRECHARGE command rate.

The file also contains repeated metric names for `umc_cas_cmd_read_ratio` and `umc_cas_cmd_rate`; duplicate metric names deserve attention because generated tables or user output may have ambiguous duplicates depending on generator behavior.

## Control flow and integration

`jevents.py` parses raw aliases and metric expressions. Runtime perf metric expansion pulls events from `amdzen4/branch.json`, `cache.json`, `core.json`, `data-fabric.json`, `floating-point.json`, `memory-controller.json`, `memory.json`, and `other.json`.

Package-scoped data-fabric and UMC metrics rely on `PerPkg` and the AMD uncore PMU mappings. Memory bandwidth formulas use `duration_time` and fixed 64-byte CAS transfer assumptions.

## State and persistence

The persistent state is the public recommended metric set and formulas. These names are likely used directly by scripts, docs, and users through `perf stat -M`.

## Dependencies

Dependencies include nearly every Zen 4 PMU event file in this group, perf metric functions (`d_ratio`), generated metric support, package-scope aggregation, and special variables such as `duration_time`.

## Risks

Duplicate `MetricName` entries can create ambiguous display or override behavior. Formula dependencies are broad; a rename in any source event file can break this file. Large data-fabric sums are susceptible to omitted or duplicated aliases. UMC bandwidth formulas are estimates and may not match all memory configurations. L3 latency formula depends on sampled latency and request counters retaining the same scale factor.

## Test signals

Run JSON validation, full PMU event generation, and metric parser tests. Add explicit duplicate-name detection for metrics. On Zen 4 hardware, smoke-test major metric groups with `perf stat -M` and compare memory-controller bandwidth, data-fabric sums, L2/L3 ratios, and branch metrics against controlled workloads.
