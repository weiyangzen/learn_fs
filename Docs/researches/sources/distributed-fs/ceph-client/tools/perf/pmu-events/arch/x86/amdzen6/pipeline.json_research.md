# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/pipeline.json

Purpose: Defines 14 Zen 6 derived pipeline metrics for dispatch-slot based topdown analysis across frontend bound, bad speculation, backend bound, SMT contention, retiring, and level-2 subcategories.

Important APIs/types/functions: Uses perf metric fields `MetricName`, `MetricExpr`, `MetricGroup`, `ScaleUnit`, and `BriefDescription`. Expressions use `d_ratio(...)`, derived metric references, and raw event modifier syntax `cpu@de_no_dispatch_per_slot.no_ops_from_frontend\\,cmask\\=0x8@`.

Control flow: Perf evaluates these metrics on request. `total_dispatch_slots` is `8 * ls_not_halted_cyc`; L1 metrics divide frontend, backend, SMT, speculation, and retiring signals by total slots; L2 metrics split frontend latency/bandwidth, bad speculation by mispredicts versus `bp_fe_redir.resync`, backend memory/CPU, and fastpath/microcode retiring.

State and persistence: No mutable state. The stable contract is the metric expression graph and group naming (`PipelineL1`, `PipelineL2`, and subgroup tags).

Dependencies and integration: Depends on Zen 6 `load-store.json`, `decode.json`, `execution.json`, and `branch-prediction.json`. It mirrors the Zen 5 pipeline structure but uses Zen 6 branch redirect naming (`bp_fe_redir.resync`).

Risks: Any referenced event rename breaks metric evaluation. Escaped cmask syntax must survive JSON parsing and perf expression parsing. Slot percentages can be skewed by multiplexing or by counting events at incompatible scopes. Zero branch-mispredict/restart denominators rely on `d_ratio` behavior.

Test signals: Run `perf stat -M PipelineL1,PipelineL2`, verify all referenced Zen 6 events resolve, test parser handling for escaped cmask modifiers, and use frontend-bound, branch-mispredict, memory-stall, SMT, and microcode-heavy workloads for sanity.
