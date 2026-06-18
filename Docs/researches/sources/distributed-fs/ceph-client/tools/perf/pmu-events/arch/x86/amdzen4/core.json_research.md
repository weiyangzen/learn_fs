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
