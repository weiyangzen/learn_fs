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
