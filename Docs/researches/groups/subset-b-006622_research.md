# Research group subset-b-006622

This grouped report covers AMD Zen PMU event JSON descriptors under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86`. These files are declarative data consumed by perf's PMU event generation pipeline rather than executable code. The key integration is `tools/perf/pmu-events/jevents.py`, which reads JSON event/metric records, maps AMD `Unit` values such as `L3PMC`, `DFPMC`, and `UMCPMC` to generated PMU names, parses `MetricExpr`, and emits generated PMU tables used by perf list/stat/reporting paths. The test signals for all files are JSON parse validity, jevents generation, metric expression parsing, generated `pmu-events.c` tests, and runtime `perf list`/`perf stat -M` behavior on matching AMD hardware.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/cache.json

## Purpose

`amdzen3/cache.json` defines 67 AMD Zen 3 cache, instruction-fetch, TLB, op-cache, and L3 PMU event records for perf. It provides raw event names, event select values, unit masks, short descriptions, and `Unit: L3PMC` markers for uncore L3 events so perf can expose these counters on Zen 3 systems.

## Important records and schema

Each entry is a JSON object with `EventName`, `EventCode`, optional `UMask`, optional `BriefDescription`, and optional `Unit`. Core PMU events omit `Unit`; L3 events use `Unit: L3PMC`, which `jevents.py` maps to the AMD L3 PMU name.

Important event families include:

- `l2_request_g1` and `l2_request_g2`: common and rare L2 request classes, including data reads, stores, instruction reads, prefetches, sized/non-cacheable reads, self-modifying-code invalidations, and bus-lock traffic.
- `l2_cache_req_stat`: L2 access status masks for instruction/data hits and misses; aggregate aliases such as `ic_dc_miss_in_l2` and `ic_dc_hit_in_l2` feed recommended metrics.
- `l2_pf_*`, `l2_latency`, `l2_fill_pending`, and `l2_wcb_req`: L2 prefetch hit/miss paths, fill latency/busy cycles, and write-combining-buffer requests.
- `ic_*` and `op_cache_hit_miss`: instruction-cache fills, fetch-window misses, stalls, invalidations, instruction-cache tag hit/miss, op-cache hit/miss, and op-cache/instruction-cache mode switches.
- `bp_l1_tlb_miss_l2_tlb_*`: instruction-side TLB miss events split by L2 TLB hit/miss and page size.
- `l3_request_g1`, `l3_lookup_state`, `l3_comb_clstr_state`, `xi_sys_fill_latency`, and `xi_ccx_sdp_req1`: L3 accesses, misses, and miss latency support.

One aggregate event, `l2_request_g1.all_no_prefetch`, intentionally has no description and uses `UMask: 0xf9` to combine non-prefetch L2 request masks.

## Control flow and integration

There is no runtime control flow in this file. Build-time control flow is:

1. perf's PMU event build scans model folders listed in `arch/x86/mapfile.csv`.
2. `jevents.py` parses this JSON array.
3. Records with `Unit: L3PMC` are routed to AMD L3 PMU tables; records without `Unit` become core PMU event aliases.
4. Generated tables are compiled into `pmu-events.c` and surfaced through perf event lookup.

`recommended.json` depends on many names from this file, especially `l2_request_g1.*`, `l2_pf_*`, `l2_cache_req_stat.*`, `l3_lookup_state.*`, `xi_sys_fill_latency`, `xi_ccx_sdp_req1`, `ic_tag_hit_miss.*`, and `op_cache_hit_miss.*`.

## State and persistence

The file is static source data. Its persistent contract is the event name/code/mask mapping. Changing a name breaks metric expressions and user-visible perf aliases; changing an event code or mask changes the hardware counter programmed by perf.

## Dependencies

Dependencies are the perf PMU JSON schema, AMD Zen 3 performance-monitoring event definitions, and perf's AMD PMU unit mapping. The file also depends indirectly on metric parser support for aliases referenced in `recommended.json`.

## Risks

The main risks are silent hardware miscounting from wrong event codes or masks, broken derived metrics if an alias is renamed, and bad PMU routing if L3 records lose `Unit: L3PMC`. Aggregate masks with sparse descriptions should be preserved carefully because they are consumed by formulas even when not directly user-facing.

## Test signals

Useful checks are `jq empty` for JSON validity, perf's PMU event generation target, metric tests for formulas referencing these events, `perf list` on Zen 3 for alias visibility, and hardware sanity checks such as comparing L2 access/hit/miss relationships and L3 latency formulas under controlled workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/core.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/core.json

## Purpose

`amdzen3/core.json` defines 23 Zen 3 core execution and retirement PMU events. It gives perf aliases for retired instructions, macro-ops, branch retirement/misprediction, floating-point instruction classes, divider activity, fused instructions, and IBS-tagged operation counts.

## Important records and schema

The schema is a JSON array of event objects with `EventName`, `EventCode`, optional `UMask`, `BriefDescription`, and for several events `PublicDescription`.

Important event families include:

- `ex_ret_instr` and `ex_ret_ops`: retired instructions and retired macro-ops; `ex_ret_ops` is the basis for macro-op retirement metrics.
- `ex_ret_brn*`: retired branches, taken branches, mispredicted branches, far transfers, resyncs, near returns, near-return mispredicts, indirect branch mispredicts, conditional branches, indirect branches, and direct-branch target mismatches.
- `ex_ret_mmx_fp_instr.*`: retired SSE, MMX, and x87 instruction class masks. The descriptions explicitly warn that these are instruction counts, not FLOP counts.
- `ex_tagged_ibs_ops.*`: tagged IBS operation retired and retired-to-order events.
- `ex_div_busy` and `ex_div_count`: divider occupancy/counting support.
- `ex_ret_fused_instr`: fused retired instruction tracking.

## Control flow and integration

The file is read by perf's event generation pipeline and converted into core PMU aliases. `recommended.json` consumes `ex_ret_brn`, `ex_ret_brn_misp`, `ex_ret_ops`, and `ex_ret_mmx_fp_instr.sse_instr` via metrics such as branch misprediction ratio, macro-ops retired, and mixed SSE/AVX stall context.

At runtime, perf resolves an alias such as `ex_ret_brn_misp` to the event select and mask from this table before programming the core PMU.

## State and persistence

The persistent state is the stable alias-to-hardware-event mapping. There is no mutable runtime state. Alias stability matters because higher-level metrics and user scripts reference these names.

## Dependencies

The file depends on the Zen 3 architectural PMU definitions and on perf's JSON event schema. It also integrates with branch and retirement metrics from `amdzen3/recommended.json`.

## Risks

Branch and retirement aliases are common denominator events for many analyses; incorrect masks or renames would break branch prediction, IPC-style, and retirement-based metrics. Another risk is misuse of `ex_ret_mmx_fp_instr.*` as FLOP counters despite the source warning that they include non-numeric instructions.

## Test signals

Run JSON validation, PMU table generation, and `perf list` checks for the aliases. Metric parsing should validate formulas using `ex_ret_brn_misp`, `ex_ret_brn`, and `ex_ret_ops`. Hardware tests can compare retired instruction counts with architectural events and verify branch misprediction ratios under branch-heavy benchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/core.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/data-fabric.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/data-fabric.json

## Purpose

`amdzen3/data-fabric.json` defines 12 Zen 3 data-fabric PMU events for package-level traffic accounting. It exposes remote outbound data-controller counters and DRAM channel data-controller counters used to estimate data-fabric link traffic and aggregate DRAM bandwidth.

## Important records and schema

Records contain `EventName`, `EventCode`, `UMask`, `PublicDescription`, `Unit: DFPMC`, and `PerPkg: "1"`. The `DFPMC` unit tells perf these are AMD data-fabric PMU events rather than core events, and `PerPkg` marks package-scoped counting.

Important records include:

- `remote_outbound_data_controller_0` through `_3`: remote link outbound data, each with event code `0x5d`, different unit masks, and public descriptions noting approximate outbound bytes for a node/die.
- `dram_channel_data_controller_0` through `_7`: DRAM channel byte counters for NPS1 node/die aggregation, with event code `0x38` and masks for individual channels.

## Control flow and integration

`jevents.py` maps `Unit: DFPMC` to the AMD data-fabric PMU. During event generation the package-scoped flag is persisted into the generated table, so perf can aggregate the event at the right scope. `amdzen3/recommended.json` defines `all_remote_links_outbound` and `nps1_die_to_dram` by summing these aliases.

## State and persistence

The file is immutable source metadata. Persistent semantics include the unit mask to channel/link mapping and the package-level scope. Changes alter how perf interprets data movement across dies, memory channels, and remote links.

## Dependencies

Dependencies are AMD Zen 3 data-fabric PMU definitions, perf's `DFPMC` mapping, and metric expressions in `recommended.json` that sum these counters.

## Risks

The descriptions use "Approximate", so downstream users should avoid treating these as exact byte accounting in all topology modes. Incorrect `PerPkg` or `Unit` metadata would cause perf to program the wrong PMU or aggregate at the wrong level. Channel-count assumptions are topology-sensitive.

## Test signals

Validate JSON and generated PMU tables, check `perf list amd_df` aliases on matching hardware, and run metric parser tests for the recommended data-fabric formulas. Hardware validation should compare DRAM channel sums with known memory bandwidth workloads and expected NPS/topology behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/data-fabric.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/floating-point.json

## Purpose

`amdzen3/floating-point.json` defines 22 Zen 3 floating-point and SIMD PMU events. It covers FPU pipe assignment, retired SSE/AVX operation classes, serialized operations, move elimination, and mixed SSE/AVX dispatch faults.

## Important records and schema

Entries use `EventName`, `EventCode`, `UMask`, `BriefDescription`, and often `PublicDescription`.

Important families include:

- `fpu_pipe_assignment.total`, `.total3`, `.total2`, `.total1`, `.total0`: counts FP scheduler pipe assignment at total and per-pipe masks.
- `fp_ret_sse_avx_ops.*`: retired add/sub, multiply, divide/square-root, multiply-add, and all SSE/AVX operations.
- `fp_retired_ser_ops.*`: serializing SSE bottom/top and x87 bottom/top operations.
- `fp_num_mov_elim_scal_op.*`: optimized and non-optimized scalar move elimination by single/double precision.
- `fp_disp_faults.*`: mixed SSE/AVX fault/stall categories including 128-bit, 256-bit, and all.

## Control flow and integration

The file is parsed by perf's PMU event generator into core PMU aliases. `amdzen3/recommended.json` references `fp_disp_faults.sse_avx_all` for the `sse_avx_stalls` event/metric surface. Users can combine the retired operation classes for FP throughput analysis, while the descriptions distinguish operation classes from instruction counts.

## State and persistence

There is no mutable state. The persistent contract is the relationship between event aliases, event code `0x00/0x03/0x04/0x05/0x0b` families, and masks. These aliases are part of perf's user-facing PMU vocabulary.

## Dependencies

Dependencies include AMD Zen 3 FPU event definitions and perf's JSON-to-C PMU generation. Recommended metrics and user workflows depend on stable names such as `fp_disp_faults.sse_avx_all`.

## Risks

Floating-point events are easy to misinterpret as direct FLOP metrics across vector widths and operation types. Renaming operation-class aliases can break external tooling, and changing masks can silently shift from per-class to aggregate counts.

## Test signals

Use JSON validation, PMU generation, and `perf list` alias checks. Metric tests should cover `sse_avx_stalls`. Hardware sanity checks can compare retired FP operation counts under synthetic SSE/AVX add, multiply, and divide loops, and check dispatch-fault behavior with mixed SSE/AVX code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/memory.json

## Purpose

`amdzen3/memory.json` defines 72 Zen 3 load/store, data-cache, DTLB, table-walker, lock, prefetch, fill-source, and memory-related core PMU events. It is the main Zen 3 source for L1 data-cache and load-store subsystem aliases.

## Important records and schema

Entries contain `EventName`, `EventCode`, optional `UMask`, `BriefDescription`, and in some cases `PublicDescription`.

Important families include:

- `ls_dispatch.*`: load, store, and load-store dispatch counts.
- `ls_dc_accesses`: all L1 data-cache accesses.
- `ls_mab_alloc.*` and `ls_alloc_mab_count`: miss address buffer allocation categories and outstanding miss counts.
- `ls_locks.*`: speculative/non-speculative lock and bus-lock events.
- `ls_dmnd_fills_from_sys.*`, `ls_any_fills_from_sys.*`, `ls_sw_pf_dc_fills.*`, and `ls_hw_pf_dc_fills.*`: demand, any, software-prefetch, and hardware-prefetch L1 data-cache fill sources split across local L2, same CCX, local/remote memory or IO, and external cache sources.
- `ls_l1_d_tlb_miss.*`, `ls_tablewalker.*`, and `ls_tlb_flush.all_tlb_flushes`: DTLB miss/reload, page-walk, and TLB flush events.
- `ls_pref_instr_disp.*` and `ls_inef_sw_pref.*`: software prefetch dispatch and ineffective prefetch conditions.
- `ls_misal_loads.*`, `ls_stlf`, `ls_st_commit_cancel2`, `ls_bad_status2.stli_other`: load/store forwarding, misalignment, store-cancel, and status hazards.
- `ls_not_halted_cyc`, `ls_ret_cl_flush`, `ls_ret_cpuid`, `ls_smi_rx`, `ls_int_taken`, `ls_rdtsc`: cycle and system/instruction-side memory/control support events.

## Control flow and integration

The file is converted into core PMU aliases by `jevents.py`. `amdzen3/recommended.json` references many aliases here for L1 data-cache fill metrics, DTLB metrics, all data-cache accesses, TLB flushes, and supporting stall/cycle formulas.

At runtime, perf users select aliases or derived metrics; perf uses the generated event table to program the core PMU event select and unit mask.

## State and persistence

No runtime state is stored here. Persistent state is the alias taxonomy and hardware event mapping. Fill-source masks encode locality semantics that are consumed by higher-level metrics and topology analysis.

## Dependencies

Dependencies are AMD Zen 3 load/store PMU definitions, perf's PMU JSON schema, and recommended metrics that reference `ls_*` aliases. The file also complements `cache.json`: L1/L2/cache-fill metrics often combine aliases from both files.

## Risks

Fill-source events have topology semantics; mistakes can mislead NUMA/locality analysis. Aggregate masks like `ls_l1_d_tlb_miss.all` and `ls_tlb_flush.all_tlb_flushes` are referenced by recommended metrics, so renames or mask changes are high impact. Some events are speculative or count conditions rather than retired architectural operations, which should be clear in user-facing analysis.

## Test signals

Run `jq empty`, PMU event generation, and metric parser tests. Validate that `recommended.json` formulas resolve all `ls_*` names. Hardware tests should exercise memory bandwidth, TLB miss/page-walk, lock, prefetch, and misaligned-load workloads to confirm relative counter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/other.json

## Purpose

`amdzen3/other.json` defines 17 Zen 3 decode/dispatch and scheduler-resource events that do not fit cleanly in cache, memory, core, or floating-point categories. These counters expose empty micro-op queues, decoder dispatch classes, and dispatch token stalls.

## Important records and schema

Entries use `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`.

Important event families include:

- `de_dis_uop_queue_empty_di0`: cycles where the micro-op queue is empty.
- `de_dis_cops_from_decoder.disp_op_type.any_integer_dispatch` and `.any_fp_dispatch`: integer and FP ops dispatched from decoder.
- `de_dis_dispatch_token_stalls1.*`: first group of dispatch token stalls, including FP flush recovery, FP scheduler/resource stalls, FP register file stalls, taken branch buffer stalls, integer scheduler miscellaneous stalls, store queue stalls, load queue stalls, and integer physical register file stalls.
- `de_dis_dispatch_token_stalls2.*`: second group of token stalls, including retire queue, AGSQ, and integer scheduler queue 0-3 token stalls.

## Control flow and integration

The file is generated into core PMU aliases by the standard perf PMU event pipeline. `amdzen3/recommended.json` references the decoder dispatch aliases in `macro_ops_dispatched`; users can combine token-stall aliases with cache/memory/core counters to diagnose backend dispatch bottlenecks.

## State and persistence

The file has no mutable state. Its durable behavior is the mapping from dispatch stall names to hardware event codes and masks.

## Dependencies

Dependencies include AMD Zen 3 decode/dispatch PMU definitions and perf's event schema. Metric expressions depend on the exact `de_dis_cops_from_decoder.*` names.

## Risks

Dispatch token events count cycles where a valid dispatch group is stalled and may also count cycles when a thread is not selected but would have stalled. Users may overinterpret them as exclusive bottleneck buckets. Renaming decoder dispatch aliases breaks `macro_ops_dispatched`.

## Test signals

Validate JSON and PMU generation. Metric tests should resolve `macro_ops_dispatched`. Hardware sanity checks can compare token-stall counters under queue-pressure or FP-heavy workloads, and verify aliases appear in `perf list` on Zen 3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/recommended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/recommended.json

## Purpose

`amdzen3/recommended.json` defines 34 recommended Zen 3 perf aliases and metrics. It mixes raw event aliases for commonly used counters with derived `MetricName`/`MetricExpr` records for branch prediction, L2/L3 cache, TLB, decoder, and data-fabric analysis.

## Important records and schema

The file includes two kinds of records:

- Event aliases with `EventName`, `EventCode`, `UMask`, optional `Unit`, optional `PerPkg`, and `BriefDescription`.
- Derived metrics with `MetricName`, `MetricExpr`, `MetricGroup`, optional `ScaleUnit`, optional `MetricConstraint`, and `BriefDescription`.

Important metrics include:

- `branch_misprediction_ratio`: `d_ratio(ex_ret_brn_misp, ex_ret_brn)`.
- L2 access/miss/hit metrics: `all_l2_cache_accesses`, `l2_cache_accesses_from_l2_hwpf`, `all_l2_cache_misses`, `l2_cache_misses_from_l2_hwpf`, and `all_l2_cache_hits`.
- L3 metrics: `l3_cache_accesses`, `l3_misses`, and `l3_read_miss_latency`, the last using `(xi_sys_fill_latency * 16) / xi_ccx_sdp_req1`.
- Frontend cache ratios: `op_cache_fetch_miss_ratio` and `ic_fetch_miss_ratio`.
- TLB metrics: `l1_itlb_misses`, `l2_itlb_misses`, `l1_dtlb_misses`, `l2_dtlb_misses`, and `all_tlbs_flushed`.
- Decoder/execution metrics: `macro_ops_dispatched`, `macro_ops_retired`, and `sse_avx_stalls`.
- Data-fabric metrics: `all_remote_links_outbound` and `nps1_die_to_dram`, marked package-scoped where applicable.

## Control flow and integration

`jevents.py` parses metric expressions using perf's metric parser and emits generated metric tables. At runtime, `perf stat -M <MetricName>` expands formulas into the referenced raw events. This file depends on raw aliases defined across `cache.json`, `core.json`, `memory.json`, `floating-point.json`, `other.json`, and `data-fabric.json`.

## State and persistence

The file persists user-visible recommended metric names and formulas. Derived metrics are effectively API contracts: scripts and documentation may reference names such as `branch_misprediction_ratio` and `all_l2_cache_misses`.

## Dependencies

Dependencies include all referenced Zen 3 event files plus perf metric functions such as `d_ratio`. `L3PMC` and `DFPMC` records depend on AMD uncore PMU routing, and `PerPkg` depends on package aggregation support.

## Risks

Formula drift is the main risk: a referenced alias rename or semantic change breaks metric parsing or changes metric meaning. Ratios require denominator safety; `d_ratio` helps, but unusual workloads can still produce unintuitive values. Data-fabric sums are approximate and topology-sensitive. Raw and derived records in one file increase maintenance risk because schema validation must accept both shapes.

## Test signals

Run JSON validation, `metric_test.py`/PMU event generation, and `perf list --details` checks. On Zen 3 hardware, run representative `perf stat -M` commands for branch, L2/L3, TLB, decoder, and data-fabric groups and confirm formulas resolve and produce plausible non-negative values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/recommended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/branch.json

## Purpose

`amdzen4/branch.json` defines 16 Zen 4 branch prediction and branch-retirement PMU events. It separates prediction-source events such as L2 BTB correctness and dynamic indirect prediction from retired branch counts and misprediction categories.

## Important records and schema

Entries use `EventName`, `EventCode`, and `BriefDescription`; this file does not use unit masks.

Important records include:

- `bp_l2_btb_correct`, `bp_dyn_ind_pred`, and `bp_de_redirect`: branch predictor and redirect events.
- `ex_ret_brn`, `ex_ret_brn_misp`, `ex_ret_brn_tkn`, and `ex_ret_brn_tkn_misp`: retired branch totals and taken/mispredicted subsets.
- `ex_ret_brn_far`, `ex_ret_near_ret`, `ex_ret_near_ret_mispred`, `ex_ret_brn_ind_misp`: far transfers, returns, return mispredicts, and indirect branch mispredicts.
- `ex_ret_cond`, `ex_ret_ind_brch_instr`, `ex_ret_msprd_brnch_instr_dir_msmtch`, `ex_ret_uncond_brnch_instr`, and `ex_ret_uncond_brnch_instr_mispred`: branch-type-specific retirement and misprediction aliases.

## Control flow and integration

The file is parsed into Zen 4 core PMU aliases. `amdzen4/recommended.json` uses `ex_ret_brn` and `ex_ret_brn_misp` for `branch_misprediction_ratio`; `amdzen4/pipeline.json` uses `ex_ret_brn_misp` with `resyncs_or_nc_redirects` to split bad speculation into branch mispredicts and pipeline restarts.

## State and persistence

There is no mutable state. Persistent state is the public alias mapping and branch metric dependency surface.

## Dependencies

Dependencies are AMD Zen 4 branch PMU definitions, perf's JSON schema, and metric formulas in `recommended.json` and `pipeline.json`.

## Risks

Branch events are foundational for pipeline and bad-speculation metrics. Removing or renaming `ex_ret_brn_misp` or `ex_ret_brn` breaks recommended metrics. Type-specific branch counters may overlap conceptually with aggregate counters, so user-facing interpretation should avoid treating all branch categories as independent totals unless the hardware definition supports that.

## Test signals

Validate JSON and generated PMU aliases. Run metric parser tests for branch and pipeline formulas. On Zen 4 hardware, check `perf stat` branch counts under predictable and unpredictable branch workloads, and verify `branch_misprediction_ratio` changes in the expected direction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/cache.json

## Purpose

`amdzen4/cache.json` defines 126 Zen 4 cache and cache-adjacent PMU events. It covers L1 data-cache fill sources, software/hardware prefetch behavior, L2 request and prefetch paths, instruction/op-cache behavior, and L3 lookup/latency counters.

## Important records and schema

Most records use `EventName`, `EventCode`, `UMask`, and `BriefDescription`. L3 records add `Unit: L3PMC` and may include `SliceId`, `EnAllSlices`, `ThreadMask`, and `EnAllCores` routing fields. One source key is misspelled as `BriefDescript6ion` on an L3 latency-related record; consumers that only read `BriefDescription` may ignore that text.

Important families include:

- `ls_mab_alloc.*`, `ls_alloc_mab_count`, and `ls_inef_sw_pref.*`: miss address buffer allocation, outstanding misses, and ineffective software prefetch conditions.
- `ls_dmnd_fills_from_sys.*`, `ls_any_fills_from_sys.*`, `ls_sw_pf_dc_fills.*`, and `ls_hw_pf_dc_fills.*`: demand, all, software-prefetch, and hardware-prefetch data-cache fills split across local L2, local CCX, near/far cache, near/far DRAM or IO, remote cache, and all categories.
- `ls_pref_instr_disp.*`: software prefetch instruction dispatch classes.
- `l2_request_g1.*`, `l2_cache_req_stat.*`, and `l2_pf_*`: L2 request classes, L2 hit/miss status, and L2 prefetch hit/miss by source/path. Zen 4 adds broader per-type prefetch masks than Zen 3.
- `ic_cache_fill_l2`, `ic_cache_fill_sys`, `ic_tag_hit_miss.*`, and `op_cache_hit_miss.*`: instruction-cache and op-cache access/miss aliases.
- `l3_lookup_state.*`, `l3_xi_sampled_latency.*`, and `l3_xi_sampled_latency_requests.*`: L3 coherent access/miss counts and sampled latency/request counters.

The aggregate `ls_inef_sw_pref.all` uses `UMask: 0x03` and has no description, acting as a combined ineffective software prefetch alias.

## Control flow and integration

`jevents.py` parses the array and routes L3 records to AMD L3 PMU generation through `Unit: L3PMC`. `amdzen4/recommended.json` depends heavily on this file for L1 data-cache fill metrics, L2 access/miss/hit formulas, L3 accesses/misses/latency, op-cache and instruction-cache miss ratios, and prefetch-related aliases.

At runtime, perf resolves aliases into core or L3 PMU events depending on the `Unit` field and generated table.

## State and persistence

The file is static metadata. Persistent semantics include alias names, masks, L3 routing fields, and topology categories like near/far cache or memory. Many formulas depend on exact names ending in `.all`, `.local_l2`, `.dram_io_far`, and similar suffixes.

## Dependencies

Dependencies include AMD Zen 4 cache/L3 PMU definitions, perf's AMD L3 PMU unit mapping, and recommended metrics that reference these aliases. The L3 routing fields depend on generated-table support in perf.

## Risks

The misspelled `BriefDescript6ion` key is a schema-risk signal and may lose documentation in generated outputs. L3 routing fields are easy to break when normalizing JSON because they are not used by most core events. Renaming `.all` or locality-specific aliases breaks many recommended formulas. Topology terms such as near/far memory/cache are hardware-specific and must remain aligned with AMD documentation.

## Test signals

Run JSON validation, PMU event generation, and metric parser tests for `amdzen4/recommended.json`. Check generated descriptions for records near the `BriefDescript6ion` typo. On Zen 4 hardware, validate `perf list` for core and `amd_l3` aliases, then sanity-check L2 hit/miss and L3 latency formulas under cache-fitting and memory-streaming workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/core.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/core.json

## Purpose

`amdzen4/core.json` defines 22 Zen 4 core execution, retirement, cycle, interrupt, lock, and no-retire PMU events. It supplies the retirement and stall primitives used by recommended and pipeline metrics.

## Important records and schema

Records contain `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`.

Important event families include:

- `ex_ret_instr`, `ex_ret_ops`, `ex_ret_ucode_instr`, and `ex_ret_ucode_ops`: retired instruction, macro-op, and microcode-retirement aliases.
- `ex_no_retire.*`: no-retire cycles split by not-complete, load-not-complete, AGU not-complete, ALU not-complete, FPU not-complete, and effective-address generation not-complete.
- `ex_tagged_ibs_ops.*`: tagged IBS op retired counts.
- `ex_div_busy` and `ex_div_count`: divider activity.
- `ex_ret_fused_instr`: fused instruction retirement.
- `ls_not_halted_cyc` and `ls_not_halted_p0_cyc`: cycle bases used by metrics.
- `ls_locks.bus_lock`, `ls_ret_cl_flush`, `ls_ret_cpuid`, `ls_smi_rx`, and `ls_int_taken`: system/serialization/interrupt/lock support events.

## Control flow and integration

The file feeds perf's generated core PMU table. `amdzen4/pipeline.json` uses `ls_not_halted_cyc`, `ex_ret_ops`, `ex_ret_ucode_ops`, and `ex_no_retire.*` to build top-down pipeline metrics. `amdzen4/recommended.json` exposes `macro_ops_retired` via `ex_ret_ops`.

## State and persistence

There is no runtime state. The persistent contract is the availability and semantics of retirement/no-retire aliases. Pipeline metrics depend on these counters retaining their names and meanings.

## Dependencies

Dependencies are AMD Zen 4 core PMU definitions, perf's JSON schema, and pipeline/recommended metric formulas.

## Risks

Pipeline metrics are sensitive to denominator and component semantics. Incorrect `ls_not_halted_cyc` or `ex_no_retire.*` aliases can misclassify frontend/backend/retiring shares. Microcode-retirement split metrics depend on `ex_ret_ucode_ops` being present and comparable to `ex_ret_ops`.

## Test signals

Validate JSON and generated aliases. Run metric parser tests for `pipeline.json`. On Zen 4 hardware, check basic retirement counters against known instruction loops, and verify top-down metrics remain bounded and sum plausibly for simple CPU, memory, and branch workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/core.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/data-fabric.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/data-fabric.json

## Purpose

`amdzen4/data-fabric.json` defines 136 Zen 4 data-fabric PMU events. It exposes DRAM data beats for local and remote processors, local/remote socket upstream I/O beats, socket inbound/outbound CPU fabric beats, and outbound link beats for package-level data movement analysis.

## Important records and schema

Records contain `EventName`, `EventCode`, `UMask`, `PublicDescription`, `Unit: DFPMC`, and `PerPkg: "1"`. The schema is uniform and package-scoped.

Important groups include:

- `local_processor_read_data_beats_cs0` through `cs11` and `local_processor_write_data_beats_cs0` through `cs11`: DRAM read/write data for the local processor by chip-select/channel-style suffix.
- `remote_processor_read_data_beats_cs0` through `cs11` and `remote_processor_write_data_beats_cs0` through `cs11`: DRAM read/write data for remote processors.
- `local_socket_upstream_read_beats_iom0` through `iom3` and write equivalents: local socket upstream DMA/I/O traffic.
- `remote_socket_upstream_read_beats_iom0` through `iom3` and write equivalents: remote socket upstream DMA/I/O traffic.
- `local_socket_inf{0,1}_{inbound,outbound}_data_beats_ccm0` through `ccm7` and remote equivalents: inbound/outbound data to/from CPU CCMs over socket interfaces.
- `local_socket_outbound_data_beats_link0` through `link7`: outbound data from all local socket links.

## Control flow and integration

The file is converted by `jevents.py` into AMD data-fabric PMU aliases using the `DFPMC` unit mapping. `amdzen4/recommended.json` builds many package-level bandwidth and fabric metrics by summing these aliases, such as DRAM read/write data for local/remote processors and local/remote socket inbound/outbound data.

## State and persistence

Static source data persists the exact mapping from event masks to data-fabric lanes/channels/links. The `PerPkg` flag is part of the contract and affects aggregation semantics.

## Dependencies

Dependencies include AMD Zen 4 data-fabric PMU definitions, perf's `DFPMC` support, package-scope event handling, and recommended metric formulas that reference large sums of these aliases.

## Risks

The large repeated matrix is vulnerable to copy/paste errors in suffixes, masks, or descriptions. Any missing channel or duplicated mask can skew aggregate bandwidth metrics. Because these counters are package-scoped and topology-dependent, tests on one socket layout may not cover all paths.

## Test signals

Run `jq empty`, generated PMU table checks, and metric expression parsing for all recommended data-fabric sums. Hardware validation should compare local versus remote memory/I/O workloads, verify channel/link sums increase on expected paths, and check `perf list` under the AMD data-fabric PMU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/data-fabric.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/floating-point.json

## Purpose

`amdzen4/floating-point.json` defines 136 Zen 4 floating-point, SIMD, x87, packed integer, and width/type-specific retired operation events. It provides a much richer FP/SIMD taxonomy than the Zen 3 file.

## Important records and schema

Entries use `EventName`, `EventCode`, `UMask`, and `BriefDescription`.

Important families include:

- `fp_ret_x87_fp_ops.*`: x87 add/sub, multiply, divide/square-root, and aggregate operations.
- `fp_ret_sse_avx_ops.*`: SSE/AVX operation classes and aggregate counts.
- `fp_ops_retired_by_width.*`: retired FP ops by scalar/packed width categories.
- `fp_ops_retired_by_type.*`: retired FP ops by arithmetic type.
- `sse_avx_ops_retired.*`: SSE/AVX operations retired by packed/scalar and operation classes.
- `fp_pack_ops_retired.*`: packed FP operation categories.
- `packed_int_op_type.*`: packed integer operation classes, including arithmetic/logical/shift/compare-style buckets.
- `fp_retired_ser_ops.*`: serialized FP operation categories.
- `fp_disp_faults.*`: mixed SSE/AVX and width-specific dispatch fault/stall categories.

## Control flow and integration

The file is parsed into core PMU aliases. `amdzen4/recommended.json` references `fp_disp_faults.sse_avx_all` for `sse_avx_stalls`. Other aliases are direct user-facing perf event names for detailed FP/SIMD profiling and can be combined with pipeline metrics from `pipeline.json`.

## State and persistence

There is no mutable state. The persistent contract is the detailed alias taxonomy and the event-code/mask mapping for each operation class. Stable names matter because the aliases encode semantic categories used by scripts and perf users.

## Dependencies

Dependencies include AMD Zen 4 FP/SIMD PMU definitions, perf's JSON event schema, and the recommended metric using `fp_disp_faults.sse_avx_all`.

## Risks

The density and similar names create risk of swapped masks or misleading category names. Operation counts by width/type are not automatically normalized to FLOPs without understanding vector width and operation semantics. Renaming `fp_disp_faults.sse_avx_all` breaks the recommended stall alias.

## Test signals

Validate JSON and generated event tables. Run `perf list` on Zen 4 to check alias exposure. Hardware tests should use targeted scalar, packed, x87, packed integer, and mixed SSE/AVX kernels to verify the intended event groups increment while unrelated categories stay low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/memory-controller.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/memory-controller.json

## Purpose

`amdzen4/memory-controller.json` defines 13 Zen 4 unified memory controller PMU events. It exposes memory clock, activate/precharge/CAS command counts, and data-slot clock counters for memory-controller utilization and bandwidth metrics.

## Important records and schema

Records use `EventName`, `EventCode`, `PublicDescription`, `Unit: UMCPMC`, `PerPkg: "1"`, and sometimes `RdWrMask`. Unlike core PMU events, these are UMC PMU records.

Important records include:

- `umc_mem_clk`: memory clock cycle base.
- `umc_act_cmd.all`, `.rd`, `.wr`: activate command counts.
- `umc_pchg_cmd.all`, `.rd`, `.wr`: precharge command counts.
- `umc_cas_cmd.all`, `.rd`, `.wr`: CAS command counts used by read/write bandwidth and ratio metrics.
- `umc_data_slot_clks.all`, `.rd`, `.wr`: data-slot clock counts for utilization.

## Control flow and integration

`jevents.py` maps `Unit: UMCPMC` to the AMD UMC PMU. `amdzen4/recommended.json` uses these aliases for memory-controller data bus utilization, CAS command rates and read/write ratios, estimated memory read/write/combined bandwidth, activate command rate, and precharge command rate.

## State and persistence

Static metadata persists UMC event mappings, read/write mask semantics, and package-scoped aggregation. Formula correctness depends on these counters being available on the expected PMU.

## Dependencies

Dependencies include AMD Zen 4 UMC PMU definitions, perf's `UMCPMC` routing, package-scope aggregation, and recommended memory-controller formulas that use `duration_time`, `d_ratio`, and command counts.

## Risks

Memory bandwidth metrics assume a 64-byte transfer factor and use elapsed duration, so they can mislead if channel width, counting scope, or aggregation changes. `RdWrMask` is a specialized key and should not be dropped by schema normalization. Wrong `Unit` metadata would make the aliases unprogrammable or route them to the wrong PMU.

## Test signals

Validate JSON and generated UMC PMU tables. Metric parser tests should cover all `memory_controller` group formulas. On Zen 4 systems with UMC PMUs, compare read/write bandwidth metrics against controlled memory copy, read-only, and write-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/memory-controller.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/memory.json

## Purpose

`amdzen4/memory.json` defines 29 Zen 4 memory-side core PMU events centered on load/store dispatch, DTLB and ITLB/page-walk behavior, misaligned loads, store-to-load forwarding, store commit cancellation, and TLB flushes.

## Important records and schema

Entries use `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`.

Important families include:

- `ls_dispatch.*`: load, store, and load-store dispatch counts.
- `ls_bad_status2.stli_other`, `ls_stlf`, and `ls_st_commit_cancel2`: status, store-to-load forwarding, and store cancellation hazards.
- `ls_l1_d_tlb_miss.*`: DTLB misses/reloads split by 4K, coalesced, 2M, and 1G pages, and by L2 TLB hit/miss; includes aggregate `all` and `all_l2_miss`.
- `bp_l1_tlb_fetch_hit.*`, `bp_l1_tlb_miss_l2_tlb_hit`, and `bp_l1_tlb_miss_l2_tlb_miss.*`: instruction-side TLB fetch hits/misses and page-size splits.
- `ls_misal_loads.*`: cacheline and 4KB/page-crossing misaligned loads.
- `ls_tlb_flush.all`: all TLB flushes.

## Control flow and integration

The file feeds generated core PMU aliases. `amdzen4/recommended.json` references `bp_l1_tlb_miss_l2_tlb_hit`, `bp_l1_tlb_miss_l2_tlb_miss.all`, `ls_l1_d_tlb_miss.all`, `ls_l1_d_tlb_miss.all_l2_miss`, and `ls_tlb_flush.all` for TLB metrics.

## State and persistence

There is no mutable state. The persistent behavior is the page-size and L2-hit/miss split encoded by unit masks and alias suffixes.

## Dependencies

Dependencies include AMD Zen 4 load/store and TLB PMU definitions, perf's core PMU schema, and recommended TLB formulas.

## Risks

TLB aliases are split across instruction-side `bp_*` names and data-side `ls_*` names, so metric authors can easily reference the wrong side. Aggregate aliases such as `.all` and `.all_l2_miss` are formula dependencies and should be preserved. Page-size-specific counts may not be meaningful on workloads that do not use those page sizes.

## Test signals

Validate JSON and generated aliases. Metric tests should resolve all TLB formulas. Hardware checks can use page-walk-heavy workloads, huge pages, TLB shootdowns, and misaligned memory access kernels to verify expected counter movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/other.json

## Purpose

`amdzen4/other.json` defines 23 Zen 4 frontend/decode/dispatch and pipeline-support events. It exposes operation source counts, no-dispatch slot reasons, token stalls, op-queue empty cycles, and resync/non-cacheable redirects.

## Important records and schema

Entries use `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`.

Important families include:

- `resyncs_or_nc_redirects`: pipeline restart/resync or non-cacheable redirect count used by bad-speculation split metrics.
- `de_op_queue_empty`: op queue empty cycles.
- `de_src_op_disp.*`: macro-ops dispatched by decoder, op cache, loop buffer, and all sources.
- `de_dis_ops_from_decoder.*`: decoder dispatch classes for integer and FP dispatch.
- `de_no_dispatch_per_slot.*`: no-dispatch slots from frontend, backend stalls, and SMT contention.
- `de_dis_dispatch_token_stalls1.*` and `de_dis_dispatch_token_stalls2.*`: dispatch token stalls from FP resources, branch buffers, integer scheduler resources, store/load queues, retire queue, AGSQ, and scheduler queues.

## Control flow and integration

The file feeds generated core PMU aliases. `amdzen4/pipeline.json` depends on `de_no_dispatch_per_slot.*`, `de_src_op_disp.all`, and `resyncs_or_nc_redirects`. `amdzen4/recommended.json` uses `de_src_op_disp.all` for `macro_ops_dispatched`.

## State and persistence

There is no mutable state. Persistent behavior is the mapping of dispatch-source and no-dispatch categories to event masks. These counters provide denominators and classifiers for top-down pipeline metrics.

## Dependencies

Dependencies include AMD Zen 4 decode/dispatch PMU definitions, recommended metrics, and pipeline metrics.

## Risks

Top-down metrics depend on these events being semantically compatible with a six-slot dispatch model. Token stall categories may overlap or be non-exclusive in ways users should not treat as exact percentages unless formulas account for them. Renaming `de_no_dispatch_per_slot.*` or `de_src_op_disp.all` breaks pipeline formulas.

## Test signals

Validate JSON and generated aliases. Run metric parser tests for all `pipeline.json` formulas. Hardware checks should compare frontend-bound, backend-bound, SMT contention, and dispatch-source counts under instruction-cache pressure, memory stalls, single-threaded, and SMT workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/pipeline.json

## Purpose

`amdzen4/pipeline.json` defines 14 derived Zen 4 top-down pipeline metrics. It classifies dispatch slots into frontend-bound, bad-speculation, backend-bound, SMT-contention, and retiring categories, then provides second-level splits for frontend latency/bandwidth, bad speculation causes, backend memory/CPU, and retiring fastpath/microcode.

## Important records and schema

This file contains only metric records with `MetricName`, `MetricExpr`, `MetricGroup`, `BriefDescription`, and for top-level metrics `ScaleUnit: 100%`.

Important metrics include:

- `total_dispatch_slots`: `6 * ls_not_halted_cyc`, encoding a six-dispatch-slot Zen 4 model.
- Pipeline L1 metrics: `frontend_bound`, `bad_speculation`, `backend_bound`, `smt_contention`, and `retiring`.
- Frontend L2 splits: `frontend_bound_latency` and `frontend_bound_bandwidth`, using a constrained event syntax `cpu@de_no_dispatch_per_slot.no_ops_from_frontend\,cmask\=0x6@`.
- Bad-speculation L2 splits: `bad_speculation_mispredicts` and `bad_speculation_pipeline_restarts`.
- Backend L2 splits: `backend_bound_memory` and `backend_bound_cpu`.
- Retiring L2 splits: `retiring_fastpath` and `retiring_microcode`.

## Control flow and integration

`jevents.py` parses the metric expressions into generated metric tables. At runtime, perf expands `perf stat -M frontend_bound` or metric groups into referenced aliases from `amdzen4/core.json`, `amdzen4/branch.json`, and `amdzen4/other.json`.

The formulas depend on `ls_not_halted_cyc`, `de_no_dispatch_per_slot.*`, `de_src_op_disp.all`, `ex_ret_ops`, `ex_ret_ucode_ops`, `ex_no_retire.*`, `ex_ret_brn_misp`, and `resyncs_or_nc_redirects`.

## State and persistence

The persistent API is the metric name set and formulas. There is no mutable state, but formulas become user-visible performance-analysis contracts. The `MetricGroup` values organize top-down hierarchy in perf output.

## Dependencies

Dependencies include perf metric parser support for `d_ratio`, nested metric references, arithmetic, `1 - ...`, and raw PMU selector syntax with escaped commas/equal signs. It also depends on source event aliases in Zen 4 core, branch, and other JSON files.

## Risks

The six-slot denominator is architecture-specific; reusing the file for another Zen generation would be wrong if dispatch width changes. Top-level categories may not sum exactly to one for all workloads because formulas use event approximations. The escaped raw event syntax in `frontend_bound_latency` is fragile during JSON/string editing. Denominators involving `ex_ret_brn_misp + resyncs_or_nc_redirects` can be zero on trivial workloads; `d_ratio` mitigates divide-by-zero behavior.

## Test signals

Metric parser tests are mandatory for this file. Generated `pmu-events.c` should include all metrics and groups. On Zen 4 hardware, run `perf stat -M PipelineL1` and second-level groups under frontend, branch, memory, and microcode-heavy workloads to verify plausible category shifts and no expression-resolution failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/recommended.json -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/recommended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/branch-prediction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/branch-prediction.json

## Purpose

`amdzen5/branch-prediction.json` defines 16 Zen 5 branch-prediction and instruction-side TLB PMU events. It is an early Zen 5 category-specific file that combines predictor events, redirect counts, and instruction fetch TLB hit/miss breakdowns.

## Important records and schema

Entries use `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`.

Important event families include:

- `bp_l1_tlb_miss_l2_tlb_hit`: L1 ITLB miss with L2 ITLB hit.
- `bp_l1_tlb_miss_l2_tlb_miss.*`: L1 and L2 ITLB misses split by 4K, 2M, 1G, coalesced 4K, and all.
- `bp_l1_tlb_fetch_hit.*`: instruction fetch TLB hits split by page size/coalesced categories.
- `bp_l2_btb_correct`, `bp_dyn_ind_pred`, and `bp_de_redirect`: branch prediction and decode redirect primitives.
- `bp_redirects.*`: redirect counts from static, dynamic, and other sources.

## Control flow and integration

The file is parsed by perf's PMU event generator into Zen 5 core PMU aliases. Although this work item only includes the branch-prediction file, adjacent Zen 5 files such as `recommended.json`, `pipeline.json`, `inst-cache.json`, and `load-store.json` are likely to reference some of these aliases for branch and TLB metrics.

## State and persistence

There is no mutable state. The persistent contract is the branch-prediction and instruction-side TLB alias set. Because Zen 5 uses a more split folder taxonomy than Zen 3/4, the file path and names are part of the model organization contract.

## Dependencies

Dependencies are AMD Zen 5 branch-prediction PMU definitions, perf's JSON event schema, and any Zen 5 recommended/pipeline metrics that refer to these aliases.

## Risks

Instruction-side TLB aliases overlap conceptually with memory/load-store TLB counters but are in a branch-prediction file, so future metric authors must choose the correct side. The branch redirect categories may not be mutually exclusive unless hardware documentation says so. Since Zen 5 support is newer and split across renamed category files, cross-file formula references are a higher-risk area.

## Test signals

Validate JSON and generated PMU aliases. Run full Zen 5 PMU event generation and metric parsing across adjacent Zen 5 files. On Zen 5 hardware, use branch-heavy and instruction-TLB-heavy workloads to confirm predictor redirect and ITLB page-size counters move as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/branch-prediction.json -->
