# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/floating-point.json

## Purpose

This file defines 10 HaswellX core floating-point, vector-transition, and SIMD move-elimination events. It covers AVX instruction counting, FP assists by SIMD/x87 input/output cause, SIMD move elimination success/failure, and AVX/SSE transition penalties.

## Important APIs, Types, And Data

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription` where helpful. Event families are `AVX_INSTS.ALL`, `FP_ASSIST.ANY`, `FP_ASSIST.SIMD_INPUT`, `FP_ASSIST.SIMD_OUTPUT`, `FP_ASSIST.X87_INPUT`, `FP_ASSIST.X87_OUTPUT`, `MOVE_ELIMINATION.SIMD_ELIMINATED`, `MOVE_ELIMINATION.SIMD_NOT_ELIMINATED`, `OTHER_ASSISTS.AVX_TO_SSE`, and `OTHER_ASSISTS.SSE_TO_AVX`.

## Control Flow

The generator converts these core event records into HaswellX aliases. Runtime perf uses them directly for event selection or indirectly through floating-point and assist metrics. `AVX_INSTS.ALL` is event `0xC6` mask `0x7`; `FP_ASSIST` uses event `0xCA`; SIMD move elimination uses event `0x58`; AVX/SSE transition assists use event `0xC1`.

## State And Persistence Behavior

The JSON persists event definitions and sample periods. Floating-point assists, move-elimination outcomes, and transition penalties are workload-dependent hardware events measured during a perf run.

## Dependencies And Integration Points

This file integrates with HaswellX mapfile selection, perf PMU alias generation, floating-point performance investigations, compiler/vectorization diagnostics, and metric groups such as `Flops`, `FpScalar`, `FpVector`, and assist-related top-down categories when those metrics are available for the model.

## Risks And Edge Cases

`AVX_INSTS.ALL` notes that a whole `rep` string counts once, so it is not an instruction-throughput substitute in every case. FP assist events count exceptional microcode/help paths rather than normal FP operations. AVX/SSE transition events depend on code generation and upper-lane state, so they can be mitigated by compiler options or inserted `vzeroupper` instructions. Move-elimination events are candidate-uop outcomes, not architectural moves.

## Test Signals

Validate JSON and generated aliases. Runtime tests can use vectorized AVX loops, scalar/x87/SIMD exceptional inputs, code with and without `vzeroupper`, and move-heavy SIMD instruction sequences. `perf list` should show all ten aliases under the HaswellX core PMU.
