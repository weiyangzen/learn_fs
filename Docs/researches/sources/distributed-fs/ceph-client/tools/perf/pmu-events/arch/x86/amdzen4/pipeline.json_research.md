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
