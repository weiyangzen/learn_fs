<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/emr-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/emr-metrics.json

## Purpose
Defines the Emerald Rapids derived metric catalog for Linux perf's x86 PMU events system. The file is a JSON array of 307 metric objects that convert raw core, offcore, uncore, MSR, cstate, and topdown events into higher-level user-facing metrics for `perf list`, `perf stat -M`, and related perf tooling. It is data, not executable code, but it is a contract consumed by perf's pmu-events generator and metric expression evaluator.

## Important APIs, Types, And Functions
- Top-level type: JSON array of metric records.
- Required record fields seen throughout the file: `MetricName`, `MetricExpr`, and `BriefDescription`.
- Classification and display fields: `MetricGroup`, `DefaultMetricgroupName`, `MetricgroupNoGroup`, `ScaleUnit`, `PublicDescription`, and `MetricThreshold`.
- Scheduling/constraint field: `MetricConstraint`, used by perf metric scheduling when an expression has grouping or counter constraints.
- Expression language dependencies: raw PMU event names such as `CPU_CLK_UNHALTED.THREAD`, `INST_RETIRED.ANY`, offcore/uncore names such as `UNC_M_CAS_COUNT.RD`, synthetic topdown slots such as `topdown-fe-bound`, helper variables such as `duration_time`, `source_count(...)`, `#num_packages`, `#num_dies`, and `#SYSTEM_TSC_FREQ`.
- Metric families include power and cstate residency, CPI/IPC/utilization, TLB and cache miss ratios, memory and IO bandwidth, NUMA locality, frontend delivery, topdown hierarchy levels, floating-point vector/scalar mix, branch and bad speculation diagnostics, memory latency/bandwidth bottlenecks, and system uncore signals.

## Control Flow
At build or install time, perf's pmu-events tooling reads this JSON with the other Emerald Rapids event files and emits architecture-specific metric tables. At runtime, perf matches the Emerald Rapids model, exposes these `MetricName` values, parses each `MetricExpr`, schedules the referenced hardware/software events, reads counters for the workload interval, and evaluates the expression into the declared `ScaleUnit`. Metrics reference each other heavily: first-level topdown metrics derive from topdown slots, lower-level TMA metrics derive from those parent metrics plus event counts, and informational metrics expose derived rates or ratios used by other metrics.

## State And Persistence
The file itself is static source-controlled metadata. Runtime state is limited to perf's selected metric list, scheduled counter groups, raw counter values, and derived printed results. It does not persist data or modify kernel state beyond normal perf event programming. Several metrics depend on system topology and run duration variables, so the same record can evaluate differently by socket count, die count, uncore availability, multiplexing, and workload duration.

## Dependencies And Integration Points
- Integrated with `tools/perf/pmu-events` JSON loading and generated event-table code in the Ceph-client copy of Linux perf.
- Depends on matching raw event definitions from sibling files in the Emerald Rapids directory and generic x86 event files.
- Depends on Intel Emerald Rapids PMU semantics, including topdown slot events, offcore response events, uncore CHA/IMC/PCU events, cstate PMUs, and model-specific counter availability.
- Integrates with perf metric grouping, threshold display, and metric group browsing through group names such as `Default`, `TopdownL1`, `TopdownL2`, `TopdownL3`, `TopdownL4`, `Mem`, `MemoryBW`, `MemoryLat`, `Flops`, `Frontend`, `Backend`, `Power`, `SoC`, and TMA internal groups.
- The metrics file is also coupled to documentation and user workflows because `MetricName` strings are command-line API surface for `perf stat -M <metric>`.

## Risks And Edge Cases
- Expression drift is the main risk: a metric can parse successfully but produce wrong results if an event name, topdown term, topology variable, or scale factor no longer matches perf's evaluator or the kernel PMU driver.
- Counter scheduling can fail or multiplex if metric expressions require too many constrained events, especially for uncore metrics spanning CHA, IMC, PCU, and offcore resources.
- Null or absent group fields are valid in this file; consumers must not assume every metric has a non-empty `MetricGroup` or `ScaleUnit`.
- Some metrics are ratios over `INST_RETIRED.ANY`, `duration_time`, or uncore clocks; very short runs, idle systems, zero denominators, or disabled uncore PMUs can lead to missing, zero, NaN, or misleading output.
- Metrics with thresholds are advisory. A stale threshold can cause false bottleneck highlighting even if the raw expression remains valid.
- This file is architecture-specific. Reusing it for a nearby x86 model without checking event encodings and uncore topology would risk silent mismeasurement.

## Test Signals
- `jq empty` or an equivalent JSON parser should accept the file.
- The pmu-events build should regenerate successfully and report no unknown fields or malformed expressions.
- `perf list metric` on Emerald Rapids should include representative entries such as `tma_frontend_bound`, `tma_backend_bound`, `tma_memory_bound`, `memory_bandwidth_total`, and `llc_demand_data_read_miss_latency`.
- `perf stat -M` smoke tests for topdown, memory bandwidth, cstate, and FP metrics should schedule without parser errors on supported hardware.
- Regression checks should look for stable metric counts, valid units, no duplicate `MetricName` values, and no unresolved event references after changes to sibling JSON event files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/emr-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/floating-point.json

## Purpose
Defines Emerald Rapids raw PMU events for floating-point activity, assists, FP dispatch ports, retired scalar/vector FP arithmetic, and half-precision FP arithmetic. The file provides the event encodings that perf exposes as named events and that derived metrics in `emr-metrics.json` use for FLOP and FP utilization calculations.

## Important APIs, Types, And Functions
- Top-level type: JSON array of 28 event records.
- Common event fields: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`.
- Optional precision fields: `PublicDescription` for user-facing detail and `CounterMask` for cycle-style events such as `ARITH.FPDIV_ACTIVE`.
- Major event families:
  - `ARITH.FPDIV_ACTIVE` and `ASSISTS.FP` / `ASSISTS.SSE_AVX_MIX` for FP divider and assist behavior.
  - `FP_ARITH_DISPATCHED.PORT_0`, `.PORT_1`, `.PORT_5` and aliases `.V0`, `.V1`, `.V2` for FP arithmetic dispatch by execution vector/port.
  - `FP_ARITH_INST_RETIRED.*` for scalar, 128-bit, 256-bit, 512-bit, vector, and combined FLOP-width buckets.
  - `FP_ARITH_INST_RETIRED2.*` for scalar, vector, complex scalar, and packed half-precision arithmetic.

## Control Flow
Perf loads the array as named event metadata for the Emerald Rapids model. When a user requests an event such as `FP_ARITH_INST_RETIRED.512B_PACKED_SINGLE` or a derived metric that references it, perf maps `EventCode` plus `UMask` and optional modifiers such as `CounterMask` onto a programmable PMU counter from the declared `Counter` set. Sampling defaults come from `SampleAfterValue`; counting mode uses the same event encoding without a sample overflow workflow unless the user asks for sampling.

## State And Persistence
The file has no mutable state. It persists the architectural encoding and descriptions in source control. Runtime state is the programmed counter selection and accumulated event counts. Several records count instructions where one retired instruction can represent multiple floating-point operations; interpretation depends on vector width and instruction semantics, not on state stored in this file.

## Dependencies And Integration Points
- Consumed by Linux perf's x86 pmu-events JSON pipeline and by generated event tables for Emerald Rapids.
- Referenced by derived metrics such as `tma_fp_arith`, `tma_fp_vector`, `tma_fp_scalar`, vector-width breakdown metrics, and GFLOPS-style informational metrics.
- Depends on Intel's Emerald Rapids PMU event encodings for event codes `0xb0`, `0xb3`, `0xc1`, `0xc7`, and `0xcf`.
- Integrates with user workflows that inspect SIMD width mix, FP assist cost, divider activity, and AVX/SSE transition or half-precision usage.

## Risks And Edge Cases
- Alias records deliberately share encodings, for example port names and `V0`/`V1`/`V2`; tools or tests must not treat identical encodings as accidental duplicates without checking aliases.
- Public descriptions note that DAZ and FTZ MXCSR flags need to be set for many FP arithmetic retired events. Measurements without those flags can be misleading.
- FLOP interpretation is not one-to-one with instruction count for DPP and FMA-style instructions; derived metrics must preserve the documented multiplication semantics.
- `FP_ARITH_INST_RETIRED2.SCALAR` uses `UMask` `0x3`, overlapping scalar half and complex scalar half buckets by design. Consumers must respect masks rather than assuming categories are disjoint.
- Counter availability is broad for many events but still bound by PMU scheduling pressure when combined with topdown or memory metrics.

## Test Signals
- JSON syntax validation should pass and every record should include `EventName`, `EventCode`, `UMask`, and `Counter`.
- `perf list` on an Emerald Rapids event table should show the FP event names and alias descriptions.
- `perf stat -e FP_ARITH_INST_RETIRED.SCALAR,FP_ARITH_INST_RETIRED.VECTOR,FP_ARITH_INST_RETIRED2.VECTOR` should parse and schedule on supported hardware.
- Workloads with known scalar, AVX2, AVX-512, and FP16 instruction mixes should move the corresponding event buckets.
- Derived FP metrics in `emr-metrics.json` should continue to resolve all referenced FP event names after edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/frontend.json

## Purpose
Defines Emerald Rapids raw PMU events for instruction fetch, decode, frontend delivery, decoded-stream-buffer behavior, microcode-sequencer delivery, unknown branches, instruction cache/tag stalls, and frontend-retired latency attribution. These events support perf users and topdown metrics that diagnose frontend bandwidth and latency bottlenecks.

## Important APIs, Types, And Functions
- Top-level type: JSON array of 43 event records.
- Common fields: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and often `PublicDescription`.
- Optional event programming fields: `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue`.
- Major event families:
  - `BACLEARS.ANY`, `DECODE.LCP`, and `DECODE.MS_BUSY` for branch resteers and decode penalties.
  - `DSB2MITE_SWITCHES.PENALTY_CYCLES` for decoded-stream-buffer to legacy decode transitions.
  - `FRONTEND_RETIRED.*` PEBS/PDIST-style events using `EventCode` `0xc6`, `MSRIndex` `0x3F7`, and specific `MSRValue` filters for DSB, ITLB, L1I, L2, STLB, latency thresholds, microcode flows, and unknown branches.
  - `ICACHE_DATA.*` and `ICACHE_TAG.*` for instruction-cache data/tag stalls.
  - `IDQ.*`, `IDQ_BUBBLES.*`, and `IDQ_UOPS_NOT_DELIVERED.*` for uop delivery source and frontend underdelivery cycles.

## Control Flow
Perf ingests the records as event definitions for the Emerald Rapids model. Simple events program an event select and umask into a general-purpose counter. Filtered retired frontend events additionally program the listed MSR index/value pair to select the precise distribution condition. For IDQ and bubble events, optional `CounterMask`, `Invert`, and `EdgeDetect` fields change the hardware condition from raw occurrences to cycles, optimal-delivery cycles, or transition counts. Derived TMA metrics then combine these counts to apportion frontend-bound slots into latency, bandwidth, DSB, MITE, ITLB, icache, branch-resteer, and microcode causes.

## State And Persistence
The file is static PMU metadata. Runtime state includes the selected frontend events, optional MSR filters programmed by perf, and counter values captured during a measurement. There is no persistence beyond source control and generated perf tables. Some events are precise distribution events and rely on hardware filtering state, so measurements can be affected by PEBS/PDIST availability and counter placement.

## Dependencies And Integration Points
- Consumed by the perf pmu-events generation path for x86 Emerald Rapids.
- Feeds metrics in `emr-metrics.json` such as `tma_frontend_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dsb`, `tma_mite`, `tma_icache_misses`, `tma_itlb_misses`, `tma_branch_resteers`, `tma_unknown_branches`, `percent_uops_delivered_from_decoded_icache`, and `percent_uops_delivered_from_legacy_decode_pipeline`.
- Depends on Intel frontend PMU semantics, decoded stream buffer, MITE legacy decode path, IDQ delivery accounting, PEBS/PDIST retired instruction attribution, and MSR filter `0x3F7`.
- Integrates with `perf stat`, `perf record`, `perf list`, and topdown analysis workflows for code layout, branch prediction, instruction-cache locality, and decode bottlenecks.

## Risks And Edge Cases
- `FRONTEND_RETIRED.*` records share the same event select and umask but differ by `MSRValue`; losing the MSR fields would silently collapse distinct events into the same measurement.
- Alias pairs exist between `IDQ_BUBBLES.*` and `IDQ_UOPS_NOT_DELIVERED.*`; duplicate encodings are intentional compatibility surface.
- Counter masks and invert flags are semantically important. Dropping `CounterMask` on `IDQ_BUBBLES.CYCLES_FE_WAS_OK` or latency-threshold events changes a cycle condition into a raw-event condition.
- Some frontend events are limited to counters `0,1,2,3`, while retired attribution events allow a broader counter set. Metric groups can fail to schedule if this is ignored.
- Descriptions for latency thresholds encode assumptions such as "not interrupted by a back-end stall"; users should avoid interpreting them as total wall-clock frontend stall cycles.

## Test Signals
- JSON syntax validation should pass and optional MSR/filter fields should be preserved by pmu-events generation.
- `perf list` should show frontend event names with public descriptions for DSB, MITE, IDQ, icache, and frontend-retired families.
- `perf stat -e IDQ_UOPS_NOT_DELIVERED.CORE,IDQ.DSB_UOPS,IDQ.MITE_UOPS,ICACHE_DATA.STALLS` should parse on supported hardware.
- A code-layout or icache-stress benchmark should increase icache/frontend latency events, while microcoded instruction workloads should move `IDQ.MS_UOPS` or related microcode events.
- Topdown frontend metrics in `emr-metrics.json` should resolve every referenced event after any edit to this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/memory.json

## Purpose
Defines Emerald Rapids raw PMU events for memory stalls, load latency sampling, offcore response classifications, transactional memory behavior, and cache/memory request attribution. These records support memory-bound topdown analysis, NUMA locality diagnostics, bandwidth/latency metrics, and TSX/RTM memory-conflict inspection in perf.

## Important APIs, Types, And Functions
- Top-level type: JSON array of 55 event records.
- Common fields: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`.
- Optional programming and sampling fields: `CounterMask`, `Data_LA`, `MSRIndex`, `MSRValue`, and `PublicDescription`.
- Major event families:
  - `CYCLE_ACTIVITY.STALLS_L3_MISS` and `MEMORY_ACTIVITY.*` for stall cycles while cache-miss demand loads are outstanding.
  - `MACHINE_CLEARS.MEMORY_ORDERING` for machine clears caused by memory-ordering conflicts.
  - `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` and `.STORE_SAMPLE` for PEBS/data-linear-address sampling using `EventCode` `0xcd`, `Data_LA`, and latency threshold MSR `0x3F6`.
  - `OCR.*` offcore response events using `EventCode` `0x2A,0x2B`, MSR indices `0x1a6,0x1a7`, and encoded response filters for code reads, data reads, RFOs, hardware prefetches, streaming writes, reads to core, DRAM, local/remote memory, SNC DRAM, L3 miss, and write-estimate categories.
  - `OFFCORE_REQUESTS.*` and `OFFCORE_REQUESTS_OUTSTANDING.*` for L3-miss demand data read counts and occupancy.
  - `RTM_RETIRED.*` and `TX_MEM.*` for TSX/RTM starts, commits, aborts, and abort causes.

## Control Flow
Perf loads these records as Emerald Rapids memory event definitions. Simple stall and transactional events program event select/umask fields directly. Load latency and store sample events also program PEBS/data address support and MSR filter `0x3F6` to select a latency threshold. Offcore response events program paired offcore MSR filters (`0x1a6`, `0x1a7`) with model-specific response bitmasks, then count matching requests through the declared event code pair. Derived metrics consume these records to compute memory-bound fractions, load latency, memory bandwidth, NUMA locality, offcore miss rates, store/RFO pressure, and TSX abort breakdowns.

## State And Persistence
The file persists only static PMU metadata. Runtime state includes event scheduling, offcore MSR filter programming, PEBS data-address capture, sampled load/store records, and accumulated counts. Offcore and load-latency events rely on hardware filter state, so simultaneous measurements can be constrained by shared MSRs, available counters, and perf grouping decisions.

## Dependencies And Integration Points
- Consumed by Linux perf's pmu-events pipeline for the Emerald Rapids x86 model.
- Feeds metrics in `emr-metrics.json` such as `tma_memory_bound`, `tma_l1_bound`, `tma_l2_bound`, `tma_l3_bound`, `tma_dram_bound`, `tma_mem_latency`, `tma_mem_bandwidth`, `tma_local_mem`, `tma_remote_mem`, `tma_data_sharing`, `tma_lock_latency`, memory bandwidth metrics, LLC miss latency metrics, and NUMA read locality metrics.
- Depends on Intel Emerald Rapids definitions for memory activity, MEM_TRANS_RETIRED latency thresholds, offcore response filter encodings, RTM/TSX events, SNC-mode interpretation, and PEBS data linear address behavior.
- Integrates with perf memory profiling, `perf mem`, `perf stat` metric groups, and server tuning workflows that distinguish local DRAM, remote DRAM, remote memory, SNC DRAM, L3 misses, and write estimates.

## Risks And Edge Cases
- Offcore response records have dense `MSRValue` bitmasks. A single-bit transcription error can produce a syntactically valid event with a different memory-source meaning.
- Several OCR descriptions are topology-dependent. In Sub NUMA Cluster mode, "local" and "SNC_DRAM" have different interpretations than in non-SNC mode.
- Load latency events are randomly selected PEBS samples and report dispatch-to-completion latency that can exceed pure memory latency; they should not be treated as deterministic exact latencies.
- `Data_LA` events require support for data linear address capture and may be unavailable or restricted depending on kernel, privilege, PEBS setup, and virtualization.
- Offcore MSR filters are shared resources; measuring multiple offcore categories in one group can fail, multiplex, or require separate runs.
- Some events are constrained to counters `0,1,2,3` or only counter `0` for store sampling, which affects derived metric schedulability.

## Test Signals
- JSON syntax validation should pass and every offcore/load-latency event should retain its `MSRIndex` and `MSRValue`.
- `perf list` should expose the `MEMORY_ACTIVITY`, `MEM_TRANS_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, `RTM_RETIRED`, and `TX_MEM` event names on the Emerald Rapids table.
- `perf stat -e MEMORY_ACTIVITY.STALLS_L3_MISS,OFFCORE_REQUESTS.L3_MISS_DEMAND_DATA_RD,OCR.DEMAND_DATA_RD.LOCAL_DRAM` should parse on supported hardware.
- Memory-latency microbenchmarks should increase the corresponding `LOAD_LATENCY_GT_*` buckets and L3-miss stall events.
- NUMA placement tests should change local versus remote OCR categories, and TSX workloads should exercise the RTM/TX_MEM abort and commit counters.
- Derived memory metrics should continue resolving all referenced event names after edits to this file or to `emr-metrics.json`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/memory.json -->
