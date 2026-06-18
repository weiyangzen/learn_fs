# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/branch-prediction.json

Purpose: Defines 16 Zen 6 branch-prediction and instruction TLB frontend events for perf.

Important APIs/types/functions: The table uses `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`. Families include `bp_l1_tlb_miss_l2_tlb_hit`, `bp_l1_tlb_miss_l2_tlb_miss.*`, `bp_pipe_correct`, `bp_var_target_pred`, `bp_early_redir`, `bp_l1_tlb_fetch_hit.*`, and `bp_fe_redir.*`.

Control flow: Perf turns these JSON entries into CPU PMU aliases. Zen 6 pipeline metrics use `bp_fe_redir.resync` to split bad speculation into branch mispredicts versus frontend restarts; recommended metrics outside this work item use ITLB miss families for TLB rates.

State and persistence: No runtime state. The stable contract is Zen 6 branch/ITLB event naming and raw encoding.

Dependencies and integration: Integrates with `pipeline.json`, execution branch-retirement events, and TLB metrics in Zen 6 recommended metrics. It also replaces some Zen 5 names (`bp_l2_btb_correct`, `bp_dyn_ind_pred`, `bp_de_redirect`, `bp_redirects.*`) with Zen 6-specific names.

Risks: Cross-generation name drift is intentional but hazardous for shared formulas. ITLB page-size masks include aggregate `.all` and must not be double-counted with individual page sizes. `bp_fe_redir.all` has no explicit `UMask`, so validators must accept base-event aliases.

Test signals: Validate `perf list bp_`, run branch-heavy and indirect-branch workloads, exercise ITLB misses with varied page sizes, and verify Zen 6 pipeline metrics resolve `bp_fe_redir.resync`.
