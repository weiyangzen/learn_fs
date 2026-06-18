# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/floating-point.json

## Purpose

`floating-point.json` defines 22 BroadwellX floating-point and vector-assist events. It covers retired scalar, packed, 128-bit, and 256-bit FP arithmetic instructions; x87/SIMD assist conditions; SIMD move elimination; AVX/SSE transition assists; and canceled SIMD physical register file dispatches.

## Important APIs, types, and schema

Entries use the standard event schema: `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and occasional `Errata`. `jevents.py` converts these into generated `pmu_event` aliases with event encoding components such as `event=0xc7,umask=...` and `period=2000003`.

Important families are `FP_ARITH_INST_RETIRED.*` with 12 variants, `FP_ASSIST.*` with 5 variants, `MOVE_ELIMINATION.*`, `OTHER_ASSISTS.AVX_TO_SSE`, `OTHER_ASSISTS.SSE_TO_AVX`, and `UOP_DISPATCHES_CANCELLED.SIMD_PRF`. The arithmetic descriptions document operation multipliers, for example packed 128-bit and 256-bit events representing multiple floating-point operations per retired instruction. Public descriptions repeatedly call out DAZ/FTZ MXCSR requirements for arithmetic counts.

## Control flow and integration

The build assigns these entries to the `floating point` topic and includes them in the BroadwellX core event table. `bdx-metrics.json` consumes these aliases for Top-down FP categories and derived metrics such as `tma_fp_arith`, `tma_fp_scalar`, `tma_fp_vector`, `tma_info_core_flopc`, `tma_info_system_gflops`, and instruction-mix ratios. Because these are core PMU events, the generated PMU defaults to `default_core`.

## State and persistence behavior

The file has no mutable state. Its persistent effect is generated alias data in `pmu-events.c`; runtime state is the programmed counter configuration. `CounterMask` on assist events changes the event encoding and can distinguish cycles or occurrences depending on the Intel event definition. Errata `BDM30` on AVX/SSE transition assists is preserved in descriptions by `jevents.py`.

## Dependencies

Dependencies include BroadwellX FP PMU semantics, perf's event parser, the metric expression parser, and any runtime support for precise ratios that consume these counters. The file is tightly coupled to metric expressions in `bdx-metrics.json`; missing arithmetic aliases make the FP and GFLOPS metrics unusable.

## Risks

The biggest semantic risk is misinterpreting instruction counts as operation counts. Several events count one retired instruction while descriptions explain that each count represents multiple computations; metrics must apply the correct multipliers. DAZ/FTZ requirements can make workload comparisons misleading if floating-point environment state differs. Errata-marked transition assists should not be used as definitive diagnosis without checking the relevant Intel specification update. Event-name changes break Top-down FP metrics.

## Test signals

Useful checks are JSON validation, generated alias presence for `fp_arith_inst_retired.scalar`, `fp_arith_inst_retired.128b_packed_double`, and `other_assists.avx_to_sse`, plus metric expansion for `tma_fp_arith`, `tma_fp_vector_128b`, and `tma_info_system_gflops`. For runtime validation, compare simple scalar/vector FP microbenchmarks against expected relative counter movement rather than exact absolute counts.
