# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/memory-controller.json

## Purpose

`amdzen4/memory-controller.json` defines 13 Zen 4 unified memory controller PMU events. It exposes memory clock, activate/precharge/CAS command counts, and data-slot clock counters for memory-controller utilization and bandwidth metrics.

## Important records and schema

Records use `EventName`, `EventCode`, `PublicDescription`, `Unit: UMCPMC`, `PerPkg: "1"`, and sometimes `RdWrMask`. Unlike core PMU events, these are UMC PMU records.

Important records include:

- `umc_mem_clk`: memory clock cycle base.
- `umc_act_cmd.all`, `.rd`, `.wr`: activate command counts.
- `umc_pchg_cmd.all`, `.rd`, `.wr`: precharge command counts.
- `umc_cas_cmd.all`, `.rd`, `.wr`: CAS command counts used by read/write bandwidth and ratio metrics.
- `umc_data_slot_clks.all`, `.rd`, `.wr`: data-slot clock counts for utilization.

## Control flow and integration

`jevents.py` maps `Unit: UMCPMC` to the AMD UMC PMU. `amdzen4/recommended.json` uses these aliases for memory-controller data bus utilization, CAS command rates and read/write ratios, estimated memory read/write/combined bandwidth, activate command rate, and precharge command rate.

## State and persistence

Static metadata persists UMC event mappings, read/write mask semantics, and package-scoped aggregation. Formula correctness depends on these counters being available on the expected PMU.

## Dependencies

Dependencies include AMD Zen 4 UMC PMU definitions, perf's `UMCPMC` routing, package-scope aggregation, and recommended memory-controller formulas that use `duration_time`, `d_ratio`, and command counts.

## Risks

Memory bandwidth metrics assume a 64-byte transfer factor and use elapsed duration, so they can mislead if channel width, counting scope, or aggregation changes. `RdWrMask` is a specialized key and should not be dropped by schema normalization. Wrong `Unit` metadata would make the aliases unprogrammable or route them to the wrong PMU.

## Test signals

Validate JSON and generated UMC PMU tables. Metric parser tests should cover all `memory_controller` group formulas. On Zen 4 systems with UMC PMUs, compare read/write bandwidth metrics against controlled memory copy, read-only, and write-heavy workloads.
