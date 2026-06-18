# subset-b-006623 Research

Grouped research for `subset-b-006623`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/data-fabric.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/data-fabric.json

Purpose: Defines 204 AMD Zen 5 Data Fabric PMU events for perf. The file maps package-level DFPMC counters to DRAM channel, upstream IO root complex, core-to-fabric interface, and cross-socket link traffic so `perf list`, `perf stat`, and metric expressions can name fabric bandwidth events instead of raw event/umask pairs.

Important APIs/types/functions: This is declarative PMU schema data, not executable code. Each object uses perf JSON fields `EventName`, `EventCode`, `UMask`, `Unit: DFPMC`, `PerPkg: "1"`, and `PublicDescription`. Event families encode local, remote, and local-or-remote socket read/write data beats for 12 DRAM channels, 8 IO root complexes, 16 CFI instances, and 6 cross-socket links.

Control flow: At perf build/runtime, pmu-events tooling parses the array, associates events with the Zen 5 model map, and exposes names such as `local_or_remote_socket_read_data_beats_dram_0` for command-line selection. `recommended.json` depends on many of these exact event names when computing fabric bandwidth metrics by summing channels and dividing by `duration_time`.

State and persistence: There is no mutable runtime state in this file. The persistent contract is the stable event-name to raw encoding mapping; `PerPkg` means counts are interpreted at package/socket scope rather than per logical CPU.

Dependencies and integration: Integrates with Linux perf's JSON pmu-events generator, AMD Zen 5 model tables, the `DFPMC` uncore PMU driver, and Zen 5 recommended metrics for DRAM, DMA, CFI, and link bandwidth. The channel counts and `ScaleUnit` assumptions in metrics must match these event inventories.

Risks: The large repeated matrix is vulnerable to off-by-one channel/link omissions, mismatched local/remote umasks, and stale channel counts on SKUs with fewer exposed counters. Renaming any event breaks `recommended.json` formulas. Per-package uncore events can be misread if users aggregate them like per-core counters.

Test signals: Validate JSON syntax, run `perf list` on Zen 5 hardware or generated pmu-events tables, sample representative DRAM/IO/CFI/link events, and run the dependent recommended bandwidth metrics to ensure every referenced `data_fabric` event resolves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/data-fabric.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/decode.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/decode.json

Purpose: Defines 19 Zen 5 decoder and dispatch PMU events used to diagnose frontend supply, op-cache versus x86-decoder source, dispatch stalls, and empty dispatch slots.

Important APIs/types/functions: The file is a perf PMU event table using `EventName`, `EventCode`, `UMask`, and `BriefDescription`. Key families are `de_op_queue_empty`, `de_src_op_disp.*`, `de_dis_ops_from_decoder.*`, `de_dispatch_stall_cycle_dynamic_tokens_part1.*`, `de_dispatch_stall_cycle_dynamic_tokens_part2.*`, `de_no_dispatch_per_slot.*`, and `de_additional_resource_stalls.dispatch_stalls`.

Control flow: Perf's pmu-events parser turns these objects into named CPU events. Zen 5 pipeline and recommended metrics consume them, especially `de_no_dispatch_per_slot.no_ops_from_frontend`, `de_no_dispatch_per_slot.backend_stalls`, `de_no_dispatch_per_slot.smt_contention`, and `de_src_op_disp.all`.

State and persistence: No runtime state is stored here. The durable state is the event-name contract and raw event/umask encodings for decoder-source and dispatch-stall attribution.

Dependencies and integration: Integrates with the core CPU PMU, pipeline topdown-style metrics, and recommended macro-op dispatch metrics. Its event names must remain aligned with formula references in `pipeline.json` and `recommended.json`.

Risks: Zen 5 uses names such as `any_fp_dispatch`, `any_integer_dispatch`, `al_tokens`, `ag_tokens`, and `retq` that differ from Zen 6 spellings, so cross-generation copy edits can silently break metric references or user scripts. Dynamic-token stall events are overlapping categories and should not be summed as disjoint causes without documentation.

Test signals: Check pmu-events generation, `perf list de_`, pipeline metric resolution, and targeted workloads that stress frontend starvation, op cache, SMT contention, load/store queue tokens, and retire queue stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/decode.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/execution.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/execution.json

Purpose: Defines 32 Zen 5 execution and retirement events for instructions, macro-ops, branches, divider activity, no-retire reasons, microcode retirement, fused instructions, and tagged IBS operations.

Important APIs/types/functions: This declarative table uses `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`. Important families include `ex_ret_instr`, `ex_ret_ops`, `ex_ret_brn*`, `ex_div_*`, `ex_no_retire.*`, `ex_ret_ucode_*`, `ex_tagged_ibs_ops.*`, and `ex_ret_fused_instr`.

Control flow: Perf exposes these as core PMU event names. `pipeline.json` uses `ex_ret_ops`, `ex_ret_brn_misp`, `ex_no_retire.load_not_complete`, `ex_no_retire.not_complete`, and `ex_ret_ucode_ops`; `recommended.json` uses branch and macro-op retirement events for high-level ratios.

State and persistence: The file has no mutable state. It persists the mapping from Zen 5 raw encodings to named retirement and execution events used by scripts and derived metrics.

Dependencies and integration: Integrates with branch-prediction, decode, pipeline, and recommended metrics. IBS-tagged event names also tie into AMD IBS sampling semantics, although the file only defines countable event aliases.

Risks: Some events count speculative or microarchitectural conditions while others are retired/non-speculative, so formulas must not mix them without ratio guards. `ex_no_retire.*` masks overlap, including `all` and `load_not_complete`, making naive totals misleading. Rename drift from Zen 6 branch-event names can break shared dashboards.

Test signals: Validate `perf list ex_`, run branch-heavy and divide-heavy workloads, compare `instructions` against `ex_ret_instr`, verify pipeline metrics that depend on `ex_ret_ops`, and test IBS-related aliases on hardware that exposes them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/execution.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/floating-point.json

Purpose: Defines 135 Zen 5 floating-point, SIMD, MMX/SSE/AVX integer, packed width/type, and FP dispatch fault events for perf.

Important APIs/types/functions: The JSON objects use `EventName`, `EventCode`, `UMask`, and `BriefDescription`. Major families cover `fp_ret_x87_fp_ops.*`, `fp_ret_sse_avx_ops.*`, `fp_ops_retired_by_width.*`, `fp_ops_retired_by_type.*`, `sse_avx_ops_retired.*`, `fp_pack_ops_retired.*`, `packed_int_op_type.*`, and `fp_disp_faults.*`.

Control flow: Perf parses the event table into named CPU PMU aliases. Users and derived metrics can count retired FLOPs, uops by vector width, integer vector categories, and SSE/AVX dispatch faults; `recommended.json` consumes `fp_disp_faults.sse_avx_all` as `sse_avx_stalls`.

State and persistence: No software state is mutated. The persistent contract is the detailed taxonomy of FP/SIMD event names and their masks, including aggregate `.all` aliases used for broad counting.

Dependencies and integration: Integrates with AMD core PMU encodings, perf list/stat, and any HPC tooling that derives FLOP rates from these aliases. It is adjacent to execution retirement events but separates floating/vector categories for analysis.

Risks: Several aggregate masks overlap with narrower masks, so summing all entries double-counts. Zen 5 lacks several Zen 6 additions such as FP16 scalar/packed names, bfloat move/shuffle/logical refinements, VNNI categories, 512-bit packed families, and non-schedulable queue read stalls. Event spelling differs from Zen 6, making formula sharing risky.

Test signals: Validate JSON generation, `perf list fp_`, FLOP microbenchmarks for x87/scalar/packed FP32/FP64, vector integer instruction tests, and workloads that intentionally trigger SSE/AVX dispatch faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/inst-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/inst-cache.json

Purpose: Defines 12 Zen 5 instruction-cache, op-cache, and fetch IBS PMU events for frontend cache diagnostics.

Important APIs/types/functions: The table uses `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`. It includes instruction cache fills from L2/system, fetch IBS tagging/filtering/validity events, `ic_tag_hit_miss.*`, and `op_cache_hit_miss.*`.

Control flow: Perf exposes these aliases to users. `recommended.json` depends on `op_cache_hit_miss.op_cache_miss`, `op_cache_hit_miss.all_op_cache_accesses`, `ic_tag_hit_miss.instruction_cache_miss`, and `ic_tag_hit_miss.all_instruction_cache_accesses` for frontend miss ratios.

State and persistence: No runtime state exists. The durable interface is the event naming for cache-hit/miss ratios and fetch IBS status counters.

Dependencies and integration: Integrates with core CPU PMU, AMD IBS fetch sampling concepts, and recommended frontend metrics. It complements branch-prediction ITLB events and decode frontend-supply events.

Risks: Op-cache and instruction-cache counters are related but not interchangeable; `ic_fetch_miss_ratio` explicitly notes that an instruction cache miss is not counted when there is an op-cache hit. Renaming Zen 5-specific `instruction_cache_*` or `op_cache_*` names breaks recommended formulas.

Test signals: Validate `perf list ic_ op_cache`, run icache-thrashing and op-cache-friendly loops, and verify recommended `op_cache_fetch_miss_ratio` and `ic_fetch_miss_ratio` produce finite values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/inst-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/l2-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/l2-cache.json

Purpose: Defines 44 Zen 5 L2 cache PMU events for request classes, WCB close requests, hit/miss status, prefetch outcomes, and fill response source attribution.

Important APIs/types/functions: The event schema is `EventName`, `EventCode`, `UMask`, and `BriefDescription`. Families include `l2_request_g1.*`, `l2_request_g2.*`, `l2_wcb_req.wcb_close`, `l2_cache_req_stat.*`, `l2_pf_hit_l2.*`, `l2_pf_miss_l2_hit_l3.*`, `l2_pf_miss_l2_l3.*`, and `l2_fill_rsp_src.*`.

Control flow: Perf exposes these as named core PMU aliases. `recommended.json` builds L2 accesses, misses, and hits per instruction from `l2_request_g1.*`, `l2_cache_req_stat.*`, and L2 prefetch families.

State and persistence: The file has no mutable state. It stores stable L2 event encodings and aggregate aliases such as `all_no_prefetch`, `all_dc`, and `all`.

Dependencies and integration: Integrates with load-store fill events, instruction-cache fill metrics, and recommended L2 cache metrics. Source attribution spans local CCX, near/far cache, DRAM/MMIO near/far, alternate memory, and all sources.

Risks: Some masks represent aggregate groups and overlap narrower masks. Recommended formulas rely on Zen 5 names like `all_no_prefetch`, `all_dc`, and `alternate_memories`; Zen 6 renames some of these, so metrics are not textually portable. Prefetch families split L1 data and L2 hardware prefetchers, which can be misinterpreted as demand misses.

Test signals: Validate event aliases, run L1 instruction/data miss workloads, hardware-prefetch-sensitive streams, and recommended L2 metrics; ensure every L2 event referenced from `recommended.json` resolves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/l2-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/l3-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/l3-cache.json

Purpose: Defines 17 Zen 5 L3 PMU events for coherent lookup hit/miss state and sampled cross-interconnect latency/request counters.

Important APIs/types/functions: The schema includes `EventName`, `EventCode`, `UMask`, `Unit: L3PMC`, `SliceId`, `ThreadMask`, `EnAllSlices`, and `EnAllCores`, plus descriptions. Families are `l3_lookup_state.*`, `l3_xi_sampled_latency.*`, and `l3_xi_sampled_latency_requests.*`.

Control flow: Perf maps these uncore/L3 aliases to the L3 PMU. Recommended metrics use lookup events for L3 accesses/misses and divide sampled latency counters by sampled request counters for all, local DRAM, and remote DRAM latency estimates.

State and persistence: No runtime state is kept in JSON. The persistent behavior is all-slice/all-core L3 counting via `EnAllSlices`/`EnAllCores` and fixed `SliceId`/`ThreadMask` settings.

Dependencies and integration: Integrates with the L3 PMU driver, recommended L3 metrics, and memory hierarchy analysis alongside L2 and load-store fill-source events.

Risks: Sampled latency values are only meaningful with matching request counters and nonzero denominators. The L3 events are uncore-style and may require careful aggregation across CCD/slice topology. Extension-memory and near/far source masks must track hardware documentation.

Test signals: Validate `perf list l3_`, run cache-working-set tests that hit and miss LLC, check all-slice aggregation, and verify recommended L3 latency metrics avoid divide-by-zero through `d_ratio` or equivalent handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/l3-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/load-store.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/load-store.json

Purpose: Defines 87 Zen 5 load-store PMU events for memory dispatch, locks, store-forwarding, MAB allocation, data fill sources, DTLB misses, prefetch activity, write-combining, cycles, and TLB flushes.

Important APIs/types/functions: Objects use `EventName`, `EventCode`, `UMask`, and mostly `BriefDescription`; one object uses the misspelled key `BriefDescript6ion`, which is part of the file's current schema surface. Families include `ls_dispatch.*`, `ls_dmnd_fills_from_sys.*`, `ls_any_fills_from_sys.*`, `ls_l1_d_tlb_miss.*`, `ls_pref_instr_disp.*`, `ls_sw_pf_dc_fills.*`, `ls_hw_pf_dc_fills.*`, `ls_alloc_mab_count`, `ls_not_halted_cyc`, and `ls_tlb_flush.all`.

Control flow: Perf exposes the aliases as core PMU events. Pipeline metrics depend on `ls_not_halted_cyc` to compute dispatch slots, and recommended metrics depend on dispatch, fill-source, DTLB, and TLB flush names.

State and persistence: No mutable state. The persistent contract is a detailed memory hierarchy naming scheme that separates demand versus any fills, software versus hardware prefetch fills, local/remote/near/far/alternate-memory sources, and page-size-specific DTLB miss masks.

Dependencies and integration: Integrates with L1 data-cache recommended metrics, pipeline dispatch-slot metrics, TLB metrics, and memory-locality analysis. It complements L2 response-source events and data-fabric bandwidth counters.

Risks: The misspelled `BriefDescript6ion` can be missed by strict description tooling. Fill-source masks overlap (`local_all`, `remote_cache`, `dram_io_all`, `far_all`, `all`), so totals require care. `ls_not_halted_cyc` drives many ratios; incorrect availability or multiplexing can distort topdown-style metrics.

Test signals: Validate JSON parsing despite the misspelled key, `perf list ls_`, memory locality workloads, TLB/page-size tests, software prefetch tests, and pipeline/recommended metrics that reference load-store events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/load-store.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/memory-controller.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/memory-controller.json

Purpose: Defines 13 Zen 5 unified memory controller PMU events for MEMCLK cycles and ACTIVATE, PRECHARGE, CAS, and data-slot cycles split by all/read/write masks.

Important APIs/types/functions: The schema uses `EventName`, `EventCode`, `RdWrMask`, `Unit: UMCPMC`, `PerPkg: "1"`, and `PublicDescription`. Event families are `umc_mem_clk`, `umc_act_cmd.*`, `umc_pchg_cmd.*`, `umc_cas_cmd.*`, and `umc_data_slot_clks.*`.

Control flow: Perf maps these JSON aliases to UMC PMU counters. `recommended.json` consumes them for data bus utilization, CAS/read/write ratios, bandwidth, activate rate, and precharge rate.

State and persistence: No runtime state. The persistent behavior is package-level UMC event naming and read/write mask semantics.

Dependencies and integration: Integrates with the UMC PMU driver and recommended memory-controller metrics. Bandwidth formulas assume 64-byte CAS data and use `duration_time`; utilization divides data-slot clocks by two before comparing to `umc_mem_clk`.

Risks: Per-package UMC counters are topology-sensitive and can be overcounted if users aggregate across CPUs incorrectly. `RdWrMask` differs from the core event `UMask` schema, so generic validators must allow this field. Memory clock and CAS semantics must match DDR generation and controller documentation.

Test signals: Validate `perf list umc_`, run read/write memory bandwidth workloads, compare recommended UMC bandwidth to an external benchmark, and test read/write ratio behavior on read-only and write-heavy streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/memory-controller.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/pipeline.json

Purpose: Defines 14 Zen 5 derived pipeline metrics for topdown-style slot attribution: frontend bound, bad speculation, backend bound, SMT contention, retiring, and level-2 breakdowns.

Important APIs/types/functions: This is perf metric schema, not raw event schema. Objects use `MetricName`, `MetricExpr`, `MetricGroup`, `ScaleUnit`, and `BriefDescription`. Expressions use perf functions and syntax such as `d_ratio(...)`, `cpu@event\\,cmask\\=0x8@`, and derived metric references like `total_dispatch_slots`.

Control flow: Perf evaluates `MetricExpr` when users request the metric group. `total_dispatch_slots` is `8 * ls_not_halted_cyc`; L1 metrics divide empty/unused/retired slots by that denominator; L2 metrics split frontend latency/bandwidth, mispredict/restart speculation, memory/CPU backend stalls, and fastpath/microcode retirement.

State and persistence: No mutable state. Persistent dependencies are the metric names, grouping (`PipelineL1`, `PipelineL2`, and subgroup tags), and formulas.

Dependencies and integration: Depends on Zen 5 event names from `load-store.json`, `decode.json`, `execution.json`, and branch-prediction events, especially `bp_redirects.resync`. The formula layer integrates with perf's metric expression parser rather than a PMU driver directly.

Risks: Formula correctness depends on all referenced events being schedulable together or on perf multiplexing accurately. The cmask expression must remain escaped correctly in JSON. `bad_speculation_from_*` divides by `ex_ret_brn_misp + bp_redirects.resync`, so zero-event workloads need safe `d_ratio` behavior.

Test signals: Run `perf stat -M PipelineL1,PipelineL2` on Zen 5, validate parser handling of escaped raw event modifiers, compare slot percentages for sane totals, and test frontend-bound, branch-mispredict, memory-stall, and microcode-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/recommended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/recommended.json

Purpose: Defines 63 recommended Zen 5 perf metrics spanning branch prediction, L1/L2/L3 cache behavior, op-cache and instruction-cache ratios, TLBs, macro-op dispatch/retire, SSE/AVX stalls, UMC memory-controller rates/bandwidth, and Data Fabric bandwidth.

Important APIs/types/functions: This file uses `MetricName`, `MetricExpr`, `MetricGroup`, `ScaleUnit`, `BriefDescription`, and sometimes `PerPkg`. Expressions reference events from many sibling JSON files plus perf built-ins such as `instructions` and `duration_time`, with `d_ratio(...)` used for ratio safety.

Control flow: Perf evaluates these metrics as user-facing recommended summaries. The file ties raw events together: branch misprediction from `ex_ret_brn_misp/ex_ret_brn`, L2 metrics from request/status/prefetch events, L3 latency from sampled latency divided by requests, TLB metrics from branch/load-store TLB events, UMC bandwidth from CAS commands, and fabric bandwidth from Data Fabric beat counters.

State and persistence: No runtime state. The persistent contract is cross-file metric dependency wiring and metric group names such as `branch_prediction`, `l1_dcache`, `l2_cache`, `l3_cache`, `tlb`, `decoder`, `memory_controller`, and `data_fabric`.

Dependencies and integration: Depends on Zen 5 `branch-prediction.json` even though that file is outside this work item, plus `decode`, `execution`, `floating-point`, `inst-cache`, `l2-cache`, `l3-cache`, `load-store`, `memory-controller`, and `data-fabric`. Integrates with perf's metric parser and generated pmu-events tables.

Risks: This file is the most fragile cross-file integration point: any event rename or generation-specific spelling difference breaks a metric. Long Data Fabric formulas hard-code 12 DRAM channels, 8 IO complexes, 16 CFI instances, and 6 links. `PerPkg` metrics must not be interpreted per core. Some ratios depend on nonzero denominators and compatible multiplexing groups.

Test signals: Run `perf list --metrics`, `perf stat -M` for each metric group, a dependency scan that resolves every referenced event/metric name, parser tests for long expressions, and workload sanity checks for cache, memory, branch, and fabric bandwidth metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/recommended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/branch-prediction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/branch-prediction.json

Purpose: Defines 16 Zen 6 branch-prediction and instruction TLB frontend events for perf.

Important APIs/types/functions: The table uses `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`. Families include `bp_l1_tlb_miss_l2_tlb_hit`, `bp_l1_tlb_miss_l2_tlb_miss.*`, `bp_pipe_correct`, `bp_var_target_pred`, `bp_early_redir`, `bp_l1_tlb_fetch_hit.*`, and `bp_fe_redir.*`.

Control flow: Perf turns these JSON entries into CPU PMU aliases. Zen 6 pipeline metrics use `bp_fe_redir.resync` to split bad speculation into branch mispredicts versus frontend restarts; recommended metrics outside this work item use ITLB miss families for TLB rates.

State and persistence: No runtime state. The stable contract is Zen 6 branch/ITLB event naming and raw encoding.

Dependencies and integration: Integrates with `pipeline.json`, execution branch-retirement events, and TLB metrics in Zen 6 recommended metrics. It also replaces some Zen 5 names (`bp_l2_btb_correct`, `bp_dyn_ind_pred`, `bp_de_redirect`, `bp_redirects.*`) with Zen 6-specific names.

Risks: Cross-generation name drift is intentional but hazardous for shared formulas. ITLB page-size masks include aggregate `.all` and must not be double-counted with individual page sizes. `bp_fe_redir.all` has no explicit `UMask`, so validators must accept base-event aliases.

Test signals: Validate `perf list bp_`, run branch-heavy and indirect-branch workloads, exercise ITLB misses with varied page sizes, and verify Zen 6 pipeline metrics resolve `bp_fe_redir.resync`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/branch-prediction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/decode.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/decode.json

Purpose: Defines 23 Zen 6 decode, op-source, and dispatch-stall PMU events used for frontend and backend dispatch-slot analysis.

Important APIs/types/functions: Uses `EventName`, `EventCode`, `UMask`, and `BriefDescription`. Families include `de_op_queue_empty`, `de_src_op_disp.*`, `de_dis_ops_from_decoder.*`, dynamic token stall parts 1 and 2, `de_no_dispatch_per_slot.*`, and `de_additional_resource_stalls.dispatch_stalls`.

Control flow: Perf exposes these aliases. Zen 6 pipeline metrics consume `de_no_dispatch_per_slot.*` and `de_src_op_disp.all`; recommended macro-op dispatch metrics consume `de_src_op_disp.all`.

State and persistence: No runtime state. The persistent API is the Zen 6 naming for decoder source and dispatch stalls.

Dependencies and integration: Integrates with load-store, execution, branch-prediction, and pipeline metric files. Compared with Zen 5, token stalls are enumerated as `int_sq0` through `int_sq5` and `ret_q`, with an aggregate `all`.

Risks: Renaming from Zen 5 spellings such as `any_fp_dispatch` to `any_fp` and `retq` to `ret_q` can break reused tooling. Dynamic token stall categories overlap and should be interpreted as attribution signals rather than exclusive buckets.

Test signals: Validate pmu-events generation, `perf list de_`, pipeline metric evaluation, and workloads that stress decoder bandwidth, op-cache supply, SMT contention, integer scheduler tokens, and retire queue pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/decode.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/execution.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/execution.json

Purpose: Defines 35 Zen 6 execution and retirement PMU events for instructions, macro-ops, branch classes, divider activity, no-retire causes, microcode, fused instructions, execution IBS, and memory-profiler IBS.

Important APIs/types/functions: The event table uses `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`. Key families include `ex_ret_*`, `ex_div_*`, `ex_no_retire.*`, `ex_tagged_ibs_ops.*`, and `ex_mprof_ibs_ops.*`.

Control flow: Perf exposes these aliases to users and to metric expressions. Pipeline metrics use `ex_ret_ops`, `ex_ret_brn_misp`, `ex_no_retire.load_not_complete`, `ex_no_retire.not_complete`, and `ex_ret_ucode_ops`; branch recommended metrics use branch retirement aliases.

State and persistence: No mutable state. The persistent mapping names Zen 6 retirement and IBS event encodings.

Dependencies and integration: Integrates with branch-prediction and pipeline metrics, plus IBS-related profiling flows. Zen 6 adds memory-profiler IBS events and uses clearer branch names such as `ex_ret_brn_ind`, `ex_ret_brn_cond`, and `ex_ret_brn_cond_misp`.

Risks: IBS tagged, filtered, valid, and rollover counters have specialized semantics and should not be treated as ordinary retired events. `ex_no_retire.*` masks are diagnostic and may overlap. Cross-generation formula reuse must account for renamed branch and IBS fields.

Test signals: Validate `perf list ex_`, run branch, divide, microcode-heavy, and no-retire memory-stall workloads, and verify pipeline metric groups evaluate on Zen 6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/execution.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/floating-point.json

Purpose: Defines 184 Zen 6 floating-point, SIMD integer, packed-width, 512-bit, dispatch-fault, and FP non-schedulable queue stall events.

Important APIs/types/functions: Uses `EventName`, `EventCode`, `UMask`, and `BriefDescription`. Families include `fp_ret_x87_fp_ops.*`, `fp_ret_sse_avx_ops.*`, `fp_ops_ret_by_width.*`, `fp_ops_ret_by_type.*`, `fp_sse_avx_ops_ret.*`, `fp_pack_ops_ret.*`, `fp_pack_int_ops_ret.*`, `fp_disp_faults.*`, `fp_pack_512b_ops_ret.*`, and `fp_nsq_read_stalls.*`.

Control flow: Perf maps these events into named aliases for FP and vector analysis. Recommended metrics outside this work item can use `fp_disp_faults.sse_avx_all`; users can separately count 128/256/512-bit FP and integer vector operation classes, VNNI, bfloat, FP16, and queue read stalls.

State and persistence: No runtime state. The persistent API is a much broader Zen 6 vector taxonomy than Zen 5, including explicit 512-bit categories and NSQ read-stall causes.

Dependencies and integration: Integrates with execution retirement analysis, HPC FLOP accounting, vector-instruction profiling, and any metrics that depend on dispatch faults or vector width.

Risks: Many masks are aggregates over narrower categories, so summing across `.all` and detailed entries double-counts. Some `fp_ret_sse_avx_ops` FP16 scalar/packed entries share the same mask as other categories and require hardware-doc interpretation. This file is especially sensitive to copy/paste mistakes because of the large matrix of operation type and width names.

Test signals: Validate `perf list fp_`, run FP32/FP64/FP16/bfloat/vector-integer/VNNI microbenchmarks, compare expected width-specific counts, and exercise dispatch fault and NSQ stall paths where hardware support is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/inst-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/inst-cache.json

Purpose: Defines 20 Zen 6 instruction-cache, op-cache, fetch IBS, and instruction-fill source PMU events.

Important APIs/types/functions: The schema uses `EventName`, `EventCode`, `UMask`, and `BriefDescription`. It includes `ic_cache_fill_l2`, `ic_cache_fill_sys`, `ic_fetch_ibs_events.*`, `op_cache_hit_miss.*`, and `ic_fills_from_sys.*` for local/remote/near/far/alternate-memory source attribution.

Control flow: Perf exposes the aliases as frontend cache events. Zen 6 recommended metrics use op-cache miss ratios, and instruction-fill source events can be used to locate instruction-fetch pressure in local L2, CCX, DRAM/MMIO, remote cache, far memory, or extension memory.

State and persistence: No mutable state. The persistent interface is the Zen 6 naming scheme for op-cache and instruction-fill source counters.

Dependencies and integration: Integrates with branch-prediction ITLB events, decode frontend-supply metrics, and recommended frontend metrics. Compared with Zen 5, Zen 6 adds `ic_fills_from_sys.*` and renames op-cache events to shorter `hit`, `miss`, and `all` suffixes.

Risks: Zen 6 removed the Zen 5 `ic_tag_hit_miss.*` names from this file, so any metric that expects those names must be generation-specific. Fill-source categories overlap through aggregate aliases. IBS fetch event names changed from `fetch_tagged/sample_*` to `tagged/filtered/valid`.

Test signals: Validate `perf list ic_ op_cache`, run instruction working-set tests, verify op-cache ratio metrics, and compare fill-source attribution under local-cache and memory-backed instruction fetch pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/inst-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/l2-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/l2-cache.json

Purpose: Defines 54 Zen 6 L2 cache PMU events for request classes, WCB requests, cache hit/miss status, prefetch outcomes, fill response sources, and system bandwidth utilization.

Important APIs/types/functions: Uses `EventName`, `EventCode`, `UMask`, and `BriefDescription`. Families include `l2_request_g1.*`, `l2_request_g2.*`, `l2_wcb_req.*`, `l2_cache_req_stat.*`, prefetch hit/miss families, `l2_fill_rsp_src.*`, and `l2_sys_bw.*`.

Control flow: Perf exposes the aliases and derived metrics can combine them for L2 access/miss/hit rates. `l2_sys_bw.*` adds Zen 6 source categories for local/remote DRAM fills, non-temporal writes, local/remote SCM/CXL fills, victims, and all bandwidth utilization.

State and persistence: No runtime state. The durable contract is event naming and mask encoding, including generation-specific aggregate names such as `dc_all`, `no_pf_all`, and `alt_mem`.

Dependencies and integration: Integrates with load-store fill events, instruction-cache fill events, and recommended L2 metrics. Source categories align with Zen 6 memory hierarchy and CXL/extension-memory descriptions.

Risks: Several Zen 5 names changed (`all_dc` to `dc_all`, `all_no_prefetch` to `no_pf_all`, `alternate_memories` to `alt_mem`), so formula reuse can fail. Prefetch and request-status aggregates overlap. New `l2_sys_bw` events require validation against hardware support and may not behave like ordinary cache-hit counters.

Test signals: Validate `perf list l2_`, run demand and prefetch-heavy memory tests, verify recommended L2 formulas for Zen 6 name compatibility, and test `l2_sys_bw.*` on local/remote memory and non-temporal write workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/l2-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/l3-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/l3-cache.json

Purpose: Defines 17 Zen 6 L3 PMU events for coherent L3 lookup state and sampled latency/request source attribution.

Important APIs/types/functions: Objects use `EventName`, `EventCode`, `UMask`, `Unit: L3PMC`, `SliceId`, `ThreadMask`, `EnAllSlices`, `EnAllCores`, and `BriefDescription`. Families are `l3_lookup_state.*`, `l3_xi_sampled_latency.*`, and `l3_xi_sampled_latency_requests.*`.

Control flow: Perf maps these aliases to the L3 PMU with all-core/all-slice settings. Recommended metrics can use lookup counters for L3 accesses/misses and latency/request pairs for average read miss latency by source.

State and persistence: No JSON-mutated state. The persistent behavior is the all-slice L3 event configuration and source-specific latency taxonomy.

Dependencies and integration: Integrates with Zen 6 recommended L3 metrics, L2 fill-source events, and memory locality analysis. The structure mirrors Zen 5 but remains a separate model-specific table.

Risks: Sampled latency requires matching request counts and safe handling of zero requests. L3 uncore aggregation can vary with CCD/slice topology. Source masks for extension memory and near/far cache should be checked against hardware documentation.

Test signals: Validate `perf list l3_`, exercise LLC hit/miss workloads, verify all-slice counting, and run latency metrics for local and remote DRAM scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/l3-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/load-store.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/load-store.json

Purpose: Defines 88 Zen 6 load-store PMU events covering memory dispatch, locks, CLFLUSH/CPUID, interrupts, store/load conflicts, MAB allocation, demand/any/prefetch fill sources, DTLB misses, misaligned loads, WCB closes, cycles, and TLB flushes.

Important APIs/types/functions: Uses `EventName`, `EventCode`, `UMask`, and mostly `BriefDescription`; like Zen 5, one object exposes the misspelled `BriefDescript6ion` key. Families include `ls_locks.*`, `ls_dispatch.*`, `ls_mab_alloc.*`, `ls_dmnd_fills_from_sys.*`, `ls_any_fills_from_sys.*`, `ls_l1_d_tlb_miss.*`, `ls_pref_instr_disp.*`, `ls_sw_pf_dc_fills.*`, `ls_hw_pf_dc_fills.*`, `ls_alloc_mab_count`, `ls_not_halted_cyc`, and `ls_not_halted_p0_cyc.p0_freq_cyc`.

Control flow: Perf exposes these aliases. Zen 6 pipeline metrics depend on `ls_not_halted_cyc`; recommended metrics depend on dispatch, fill-source, DTLB miss, and TLB flush aliases.

State and persistence: No runtime state. The durable interface is Zen 6's memory hierarchy taxonomy, including renamed short suffixes such as `ls_mab_alloc.ls`, `hwpf`, and `alt_mem`.

Dependencies and integration: Integrates with pipeline dispatch-slot formulas, L1 data-cache recommended metrics, TLB metrics, and memory locality analysis. It complements L2 and L3 source events.

Risks: The misspelled description key can break strict schema consumers. Fill-source categories overlap through aggregate aliases. Zen 5-to-Zen 6 renames (`ld_dispatch` to `pure_ld`, `hardware_prefetcher_allocations` to `hwpf`, `alternate_memories` to `alt_mem`) require generation-specific formulas.

Test signals: Validate JSON parsing and `perf list ls_`, run load/store dispatch tests, DTLB page-size tests, prefetch tests, memory locality tests, and `perf stat -M PipelineL1,PipelineL2` to confirm `ls_not_halted_cyc` integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/load-store.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/memory-controller.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/memory-controller.json

Purpose: Defines 13 Zen 6 UMC PMU events for memory clock cycles and ACTIVATE, PRECHARGE, CAS, and data bus slot activity split by all/read/write masks.

Important APIs/types/functions: The event schema uses `EventName`, `EventCode`, `RdWrMask`, `Unit: UMCPMC`, `PerPkg: "1"`, and `PublicDescription`. Event families are `umc_mem_clk`, `umc_act_cmd.*`, `umc_pchg_cmd.*`, `umc_cas_cmd.*`, and `umc_data_slot_clks.*`.

Control flow: Perf maps these aliases to memory-controller PMU counters. Zen 6 recommended metrics use them for utilization, command rates, read/write ratios, and memory bandwidth.

State and persistence: No runtime state. The persistent API is package-level UMC event naming and read/write mask behavior.

Dependencies and integration: Integrates with the UMC PMU driver and Zen 6 recommended memory-controller metrics. Bandwidth formulas assume CAS commands transfer 64 bytes and divide by `duration_time`.

Risks: Per-package UMC aggregation is topology-sensitive. `RdWrMask` is a UMC-specific field, so generic event validators must not require `UMask`. Command-rate formulas depend on `umc_mem_clk` being available and measured in the same interval as command counters.

Test signals: Validate `perf list umc_`, run read-heavy and write-heavy memory streams, compare bandwidth metrics to external tools, and verify per-package aggregation on multi-socket systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/memory-controller.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/pipeline.json

Purpose: Defines 14 Zen 6 derived pipeline metrics for dispatch-slot based topdown analysis across frontend bound, bad speculation, backend bound, SMT contention, retiring, and level-2 subcategories.

Important APIs/types/functions: Uses perf metric fields `MetricName`, `MetricExpr`, `MetricGroup`, `ScaleUnit`, and `BriefDescription`. Expressions use `d_ratio(...)`, derived metric references, and raw event modifier syntax `cpu@de_no_dispatch_per_slot.no_ops_from_frontend\\,cmask\\=0x8@`.

Control flow: Perf evaluates these metrics on request. `total_dispatch_slots` is `8 * ls_not_halted_cyc`; L1 metrics divide frontend, backend, SMT, speculation, and retiring signals by total slots; L2 metrics split frontend latency/bandwidth, bad speculation by mispredicts versus `bp_fe_redir.resync`, backend memory/CPU, and fastpath/microcode retiring.

State and persistence: No mutable state. The stable contract is the metric expression graph and group naming (`PipelineL1`, `PipelineL2`, and subgroup tags).

Dependencies and integration: Depends on Zen 6 `load-store.json`, `decode.json`, `execution.json`, and `branch-prediction.json`. It mirrors the Zen 5 pipeline structure but uses Zen 6 branch redirect naming (`bp_fe_redir.resync`).

Risks: Any referenced event rename breaks metric evaluation. Escaped cmask syntax must survive JSON parsing and perf expression parsing. Slot percentages can be skewed by multiplexing or by counting events at incompatible scopes. Zero branch-mispredict/restart denominators rely on `d_ratio` behavior.

Test signals: Run `perf stat -M PipelineL1,PipelineL2`, verify all referenced Zen 6 events resolve, test parser handling for escaped cmask modifiers, and use frontend-bound, branch-mispredict, memory-stall, SMT, and microcode-heavy workloads for sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/pipeline.json -->
