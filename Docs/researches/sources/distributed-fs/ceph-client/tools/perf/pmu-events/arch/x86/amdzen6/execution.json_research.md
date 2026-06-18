# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/execution.json

Purpose: Defines 35 Zen 6 execution and retirement PMU events for instructions, macro-ops, branch classes, divider activity, no-retire causes, microcode, fused instructions, execution IBS, and memory-profiler IBS.

Important APIs/types/functions: The event table uses `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`. Key families include `ex_ret_*`, `ex_div_*`, `ex_no_retire.*`, `ex_tagged_ibs_ops.*`, and `ex_mprof_ibs_ops.*`.

Control flow: Perf exposes these aliases to users and to metric expressions. Pipeline metrics use `ex_ret_ops`, `ex_ret_brn_misp`, `ex_no_retire.load_not_complete`, `ex_no_retire.not_complete`, and `ex_ret_ucode_ops`; branch recommended metrics use branch retirement aliases.

State and persistence: No mutable state. The persistent mapping names Zen 6 retirement and IBS event encodings.

Dependencies and integration: Integrates with branch-prediction and pipeline metrics, plus IBS-related profiling flows. Zen 6 adds memory-profiler IBS events and uses clearer branch names such as `ex_ret_brn_ind`, `ex_ret_brn_cond`, and `ex_ret_brn_cond_misp`.

Risks: IBS tagged, filtered, valid, and rollover counters have specialized semantics and should not be treated as ordinary retired events. `ex_no_retire.*` masks are diagnostic and may overlap. Cross-generation formula reuse must account for renamed branch and IBS fields.

Test signals: Validate `perf list ex_`, run branch, divide, microcode-heavy, and no-retire memory-stall workloads, and verify pipeline metric groups evaluate on Zen 6.
