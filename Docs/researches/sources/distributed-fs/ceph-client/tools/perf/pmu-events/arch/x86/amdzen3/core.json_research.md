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
