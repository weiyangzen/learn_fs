# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/floating-point.json

## Purpose

`icelake/floating-point.json` defines 13 Intel Ice Lake core PMU aliases for floating-point assists and retired floating-point arithmetic instruction classes. The catalog exposes scalar, packed, vector-width, element-count, and aggregate FLOP-oriented encodings for SSE, AVX, and AVX-512 style computational floating-point instructions.

## Important APIs, types, and schema

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and usually `PublicDescription`. No `Unit` appears, so `jevents.py` routes all aliases to `default_core`. Every event can use counters `0,1,2,3,4,5,6,7`.

The file has one assist event, `ASSISTS.FP` with event code `0xc1` and mask `0x2`. The remaining 12 aliases use event code `0xc7` under `FP_ARITH_INST_RETIRED.*`. They distinguish scalar single/double and combined scalar events, 128-bit packed single/double, 256-bit packed single/double, 512-bit packed single/double, aggregate `4_FLOPS` and `8_FLOPS` masks, and `VECTOR` with mask `0xfc`. The descriptions repeatedly note that some instructions count twice and that DAZ and FTZ MXCSR flags need to be set when using these events.

## Control flow and integration

Build-time flow maps Ice Lake CPUIDs to the `icelake` model directory, then `jevents.py` parses the JSON records into generated PMU table entries. Runtime perf alias lookup programs the core PMU event select and umask. Because the aliases are retired-instruction events rather than derived metrics, formulas for FLOP rates or operation counts must be provided by users or metric files elsewhere; this file supplies the raw event building blocks.

## State and persistence behavior

The persistent contract is the set of floating-point alias names, event code `0xc7` masks, and sampling periods. Changing aggregate masks such as `4_FLOPS`, `8_FLOPS`, or `VECTOR` would alter derived FLOP accounting without a parser failure. `SampleAfterValue` controls default sampling behavior and overhead. The file has no mutable runtime state.

## Dependencies

Dependencies include Intel Ice Lake core PMU definitions, perf's JSON event schema, the x86 Ice Lake model map, and hardware support for the listed FP arithmetic retired events. The semantic accuracy depends on instruction-set details for SSE, AVX, AVX-512, FMA, DPP, DAZ, FTZ, and microcode floating-point assists.

## Risks

The main risk is incorrect interpretation rather than parsing failure. Counts are instruction-class events, and the descriptions state that each count can represent different numbers of operations depending on vector width and precision. Some instructions count twice, so naive FLOP formulas can overcount or undercount. DAZ/FTZ requirements are easy to miss and can affect reproducibility. Aggregate masks overlap with more specific masks, so users should avoid summing aliases without understanding mask inclusion.

## Test signals

Useful checks are JSON syntax, generated perf table tests, `perf list` on Ice Lake, and microbenchmarks with known scalar, 128-bit, 256-bit, and 512-bit floating-point instruction mixes. Tests should compare specific aliases against aggregate `VECTOR`, `4_FLOPS`, and `8_FLOPS` behavior, and should run with controlled MXCSR DAZ/FTZ settings. Floating-point assist tests can use workloads that trigger denormal or exceptional FP paths.
