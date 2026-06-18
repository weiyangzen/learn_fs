# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/execution.json

Purpose: Defines 32 Zen 5 execution and retirement events for instructions, macro-ops, branches, divider activity, no-retire reasons, microcode retirement, fused instructions, and tagged IBS operations.

Important APIs/types/functions: This declarative table uses `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`. Important families include `ex_ret_instr`, `ex_ret_ops`, `ex_ret_brn*`, `ex_div_*`, `ex_no_retire.*`, `ex_ret_ucode_*`, `ex_tagged_ibs_ops.*`, and `ex_ret_fused_instr`.

Control flow: Perf exposes these as core PMU event names. `pipeline.json` uses `ex_ret_ops`, `ex_ret_brn_misp`, `ex_no_retire.load_not_complete`, `ex_no_retire.not_complete`, and `ex_ret_ucode_ops`; `recommended.json` uses branch and macro-op retirement events for high-level ratios.

State and persistence: The file has no mutable state. It persists the mapping from Zen 5 raw encodings to named retirement and execution events used by scripts and derived metrics.

Dependencies and integration: Integrates with branch-prediction, decode, pipeline, and recommended metrics. IBS-tagged event names also tie into AMD IBS sampling semantics, although the file only defines countable event aliases.

Risks: Some events count speculative or microarchitectural conditions while others are retired/non-speculative, so formulas must not mix them without ratio guards. `ex_no_retire.*` masks overlap, including `all` and `load_not_complete`, making naive totals misleading. Rename drift from Zen 6 branch-event names can break shared dashboards.

Test signals: Validate `perf list ex_`, run branch-heavy and divide-heavy workloads, compare `instructions` against `ex_ret_instr`, verify pipeline metrics that depend on `ex_ret_ops`, and test IBS-related aliases on hardware that exposes them.
