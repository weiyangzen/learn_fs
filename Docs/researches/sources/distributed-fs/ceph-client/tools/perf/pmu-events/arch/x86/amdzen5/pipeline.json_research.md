# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/pipeline.json

Purpose: Defines 14 Zen 5 derived pipeline metrics for topdown-style slot attribution: frontend bound, bad speculation, backend bound, SMT contention, retiring, and level-2 breakdowns.

Important APIs/types/functions: This is perf metric schema, not raw event schema. Objects use `MetricName`, `MetricExpr`, `MetricGroup`, `ScaleUnit`, and `BriefDescription`. Expressions use perf functions and syntax such as `d_ratio(...)`, `cpu@event\\,cmask\\=0x8@`, and derived metric references like `total_dispatch_slots`.

Control flow: Perf evaluates `MetricExpr` when users request the metric group. `total_dispatch_slots` is `8 * ls_not_halted_cyc`; L1 metrics divide empty/unused/retired slots by that denominator; L2 metrics split frontend latency/bandwidth, mispredict/restart speculation, memory/CPU backend stalls, and fastpath/microcode retirement.

State and persistence: No mutable state. Persistent dependencies are the metric names, grouping (`PipelineL1`, `PipelineL2`, and subgroup tags), and formulas.

Dependencies and integration: Depends on Zen 5 event names from `load-store.json`, `decode.json`, `execution.json`, and branch-prediction events, especially `bp_redirects.resync`. The formula layer integrates with perf's metric expression parser rather than a PMU driver directly.

Risks: Formula correctness depends on all referenced events being schedulable together or on perf multiplexing accurately. The cmask expression must remain escaped correctly in JSON. `bad_speculation_from_*` divides by `ex_ret_brn_misp + bp_redirects.resync`, so zero-event workloads need safe `d_ratio` behavior.

Test signals: Run `perf stat -M PipelineL1,PipelineL2` on Zen 5, validate parser handling of escaped raw event modifiers, compare slot percentages for sane totals, and test frontend-bound, branch-mispredict, memory-stall, and microcode-heavy workloads.
