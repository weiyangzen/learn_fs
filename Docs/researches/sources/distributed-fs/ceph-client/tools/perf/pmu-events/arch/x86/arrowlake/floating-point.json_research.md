# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/floating-point.json

## Purpose

`floating-point.json` defines Arrow Lake floating-point, vector-integer, floating-point assist, and divide-unit PMU aliases for perf. It contains 64 event records: 22 for `cpu_atom`, 29 for `cpu_core`, and 13 for `cpu_lowpower`. The file's topic is derived as `floating point` by `jevents.py`, so generated perf output groups these aliases under the floating-point topic.

This file lets users use symbolic aliases such as `FP_ARITH_OPS_RETIRED.256B_PACKED_SINGLE`, `ARITH.FPDIV_ACTIVE`, and `FP_FLOPS_RETIRED.FP64` instead of manually specifying raw event code and umask combinations.

## Important APIs, types, and data shape

The top-level structure is a JSON array of PMU event records. Relevant fields are:

- `EventName`, `EventCode`, `UMask`, `Counter`, and optional `CounterMask`.
- `Unit`, which separates P-core (`cpu_core`), E-core (`cpu_atom`), and low-power E-core (`cpu_lowpower`) definitions.
- `SampleAfterValue`, commonly `1000003`, `100003`, or `2000003`.
- `BriefDescription` and optional `PublicDescription`.
- `Deprecated`, present on compatibility aliases that should remain listable but direct users toward newer names.

The file does not use `MSRIndex`, `MSRValue`, `EdgeDetect`, `Invert`, or `Data_LA`. Its complexity is mostly in naming compatibility and unit-specific event families.

## Event coverage

The P-core section focuses on arithmetic retirement and dispatch:

- `ARITH.FPDIV_ACTIVE` tracks busy cycles for FP divide/square-root execution.
- `ASSISTS.FP` and `ASSISTS.SSE_AVX_MIX` expose microcode floating-point assist behavior.
- `FP_ARITH_DISPATCHED.V0` through `.V3` count FP arithmetic uops dispatched on vector ports.
- `FP_ARITH_OPS_RETIRED.*` provides scalar/vector and width-specific FP operation retirement aliases.
- `FP_ARITH_INST_RETIRED.*` provides deprecated compatibility names that point to `FP_ARITH_OPS_RETIRED.*`.

The Atom and low-power sections use different event families:

- `FP_INST_RETIRED.*` covers 32-bit/64-bit scalar and 128-bit/256-bit packed single/double variants.
- `FP_FLOPS_RETIRED.*` covers aggregate, FP32, and FP64 FLOP counters, with low-power compatibility aliases `SP` and `DP`.
- `FP_VINT_UOPS_EXECUTED.*` appears on `cpu_atom` for vector integer uop execution by port or category.
- `MACHINE_CLEARS.FP_ASSIST` and `UOPS_RETIRED.FPDIV` expose assist clears and retired FP divide uops on Atom/low-power units.

There are 52 unique event names. Several logical aliases repeat across `cpu_atom`, `cpu_core`, and `cpu_lowpower`, but their event codes differ.

## Control flow and integration

During build, `jevents.py` reads this file as a regular event JSON, derives topic `floating point`, parses each object via `read_json_events`, and emits generated C table entries. Those entries become part of the Arrow Lake event table selected by the `GenuineIntel-6-C[56]` mapfile row.

At runtime, perf's PMU alias lookup exposes these names for event selection. Metric formulas in Arrow Lake metric files can depend on the aliases. Top-down metric groups such as `Flops`, `Compute`, `tma_fp_arith_group`, and `tma_divider_group` are conceptually related, but the actual group descriptions live in `metricgroups.json` and metric expressions live in metric JSON files.

## State and persistence behavior

The file is immutable source data at runtime. Its contents persist only through generated `pmu-events.c` and the compiled perf binary. It carries no MSR side effects and no address-sampling flags. The `Deprecated` field is persistent metadata used by generated tables and perf output; removing a deprecated alias is a user-facing compatibility change even when a replacement alias exists.

## Dependencies and integration points

The file depends on perf's PMU event JSON schema and on Arrow Lake unit names matching runtime PMU names. The strongest integration points are:

- `pmu-events/jevents.py`, which requires valid array-of-object event JSON for files other than `metricgroups.json`.
- `pmu-events/arch/x86/mapfile.csv`, which selects this directory for Arrow Lake CPUIDs.
- `builtin-list.c` and PMU alias display paths, where `Deprecated` and descriptions become visible.
- Metric definitions in `arl-metrics.json` or generated extra metrics that may refer to these FP aliases.

## Risks and edge cases

The main risk is compatibility drift between deprecated and replacement names. There are 11 deprecated entries: nine `FP_ARITH_INST_RETIRED.*` P-core aliases that point to `FP_ARITH_OPS_RETIRED.*`, plus low-power `FP_FLOPS_RETIRED.DP` and `.SP` aliases that map conceptually to `.FP64` and `.FP32`. Removing them can break scripts, while changing only the deprecated or only the replacement form can make counters inconsistent.

Unit-specific semantics are another risk. `ARITH.FPDIV_ACTIVE` exists across all units but uses different event codes and umasks. P-core `FP_ARITH_OPS_RETIRED.*` and Atom `FP_INST_RETIRED.*` are not interchangeable even though both describe FP work. Any metric expression that assumes one family exists on all PMUs can fail or undercount on hybrid systems.

Counter masks for active-cycle events must stay intact because they encode cycle-occupancy semantics rather than simple occurrence counts. Sampling periods should be reviewed when adding high-frequency FLOP aliases because too-low periods can create large sampling overhead.

## Test signals

Validation should include JSON syntax checks, perf event generation, and generated alias inspection. Useful runtime probes on supported hardware include `perf list floating` and `perf stat -e cpu_core/FP_ARITH_OPS_RETIRED.SCALAR_DOUBLE/` or equivalent PMU-qualified aliases. Regression checks should include deprecated names to ensure they still parse and list as deprecated, and replacement names to ensure users have a working migration target.
