# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/floating-point.json

## Purpose

This 13-entry Sierra Forest table defines core PMU aliases for floating-point activity. It covers floating-point divider active cycles, retired floating-point operations by precision, retired floating-point instructions by vector width/precision, floating-point assists, and retired FP divide uops.

## Important APIs, Types, and Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, and `Deprecated`. `ARITH.FPDIV_ACTIVE` uses `CounterMask: 1` to count cycles with an active FP divider. `FP_FLOPS_RETIRED.*` uses event `0xc8`; `FP_FLOPS_RETIRED.DP` and `.SP` are deprecated aliases for `.FP64` and `.FP32`. `FP_INST_RETIRED.*` uses event `0xc7` for scalar and packed instruction classes. `MACHINE_CLEARS.FP_ASSIST` and `UOPS_RETIRED.FPDIV` capture assist and divider-uop signals.

## Control Flow

Perf maps each alias to a generic counter event on counters `0-7`. Users and metrics combine operation counts, instruction-width counts, divider occupancy, and assist counts to characterize FP throughput and slow paths. Deprecated aliases should still resolve for compatibility but should not be preferred by generated documentation or new metric formulas.

## State and Persistence Behavior

The persistent state is alias naming, encodings, default sampling periods, and deprecation markers. Runtime state is per-session core PMU counts. Cycle-style divider activity differs from retired operation counts, so calculations need consistent denominators. Assist counts are not a direct count of FP instructions or uops; they indicate slow assisted operations.

## Dependencies and Integration Points

This file integrates with perf list/stat/record, Sierra Forest metric groups such as `Flops`, and topdown analyses that correlate FP activity with backend pressure. It depends on core PMU support for the listed event encodings and on perf preserving deprecated aliases for compatibility.

## Risks

The main semantic risks are using deprecated `DP`/`SP` aliases in new formulas, treating weighted FLOP counts and retired instruction counts as interchangeable, and interpreting FP assists as normal operation volume. Workloads using vector widths not represented here may require companion events or derived formulas. Sampling periods differ significantly, so mixed sampled profiles can have uneven resolution.

## Test Signals

Tests should parse the JSON, expose aliases in `perf list`, and verify deprecated markers remain attached. Runtime smoke tests can use scalar single/double, packed 128-bit and 256-bit FP loops, FP divide loops, and denormal/assist-prone operations. Metric validation should compare expected FLOP ratios and ensure new formulas prefer `FP32`/`FP64` over deprecated `SP`/`DP`.
