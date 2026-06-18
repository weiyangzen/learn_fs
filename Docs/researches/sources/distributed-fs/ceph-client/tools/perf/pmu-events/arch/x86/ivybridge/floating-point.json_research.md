# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/floating-point.json

## Purpose

`floating-point.json` defines 17 Ivy Bridge floating-point, SIMD, move-elimination, and assist events. It supports analysis of x87 and SSE computation, 256-bit SIMD operations, SIMD/x87 assists, AVX/SSE transition assists, and whether SIMD move elimination succeeds.

## Schema And API Surface

Entries are event objects with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, and sometimes `CounterMask` and `SampleAfterValue`. Event families include `FP_ASSIST`, `FP_COMP_OPS_EXE`, `SIMD_FP_256`, `MOVE_ELIMINATION`, and `OTHER_ASSISTS`. Representative aliases are `FP_COMP_OPS_EXE.SSE_PACKED_DOUBLE`, `FP_COMP_OPS_EXE.X87`, `SIMD_FP_256.PACKED_SINGLE`, `OTHER_ASSISTS.AVX_TO_SSE`, and `MOVE_ELIMINATION.SIMD_ELIMINATED`.

## Control Flow And Integration

`jevents.py` emits these aliases into the Ivy Bridge table. Runtime users consume them through `perf stat` or sampling, and `ivb-metrics.json` references several of them for FLOP, scalar/vector floating-point, assist, heavy-operation, and GFLOP estimates. There is no procedural control flow in the file; behavior is controlled by perf event scheduling and metric expression evaluation.

## State And Persistence

The file persists the mapping from floating-point alias names to hardware event encodings and default sampling hints. Measurements are per perf session. Some events count operations while others count assists or eliminated moves, so consumers need to preserve unit meaning when building metrics.

## Dependencies

Dependencies include Ivy Bridge PMU definitions and the metric formulas in `ivb-metrics.json` that use `FP_COMP_OPS_EXE.*`, `SIMD_FP_256.*`, and `OTHER_ASSISTS.*`. It also depends on perf's metric parser understanding arithmetic expressions over these aliases.

## Risks

Floating-point event names are used in formulas that weight packed/scalar widths differently. An alias rename or encoding error can skew FLOP and topdown compute metrics. AVX/SSE transition assists are workload- and compiler-dependent, so runtime zeros do not necessarily mean the event is broken. Counter constraints can also affect whether groups schedule without multiplexing.

## Test Signals

Check JSON syntax and `jevents.py` generation. Run metric tests for formulas referencing these aliases. Runtime smoke tests should include scalar SSE, packed SSE, 256-bit AVX, and AVX/SSE transition workloads, then verify corresponding `FP_COMP_OPS_EXE`, `SIMD_FP_256`, and `OTHER_ASSISTS` counters move plausibly.
