# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/floating-point.json

## Purpose
Broadwell-DE floating-point and SIMD event catalog for perf. It defines 22 events for retired scalar/vector floating-point arithmetic, 128-bit and 256-bit packed operations, FP assists, SIMD move elimination, AVX/SSE transition assists, and SIMD physical-register-file cancellation.

## Important APIs, Types, and Functions
Every entry provides `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Optional fields include `PublicDescription` on 16 entries, `Errata` on 2, and one `CounterMask`. Event families are `FP_ARITH_INST_RETIRED` with 12 aliases, `FP_ASSIST` with 5, `MOVE_ELIMINATION` with 2, `OTHER_ASSISTS` with 2, and `UOP_DISPATCHES_CANCELLED` with 1.

## Control Flow
Perf converts these entries into raw event aliases. The metrics file consumes the arithmetic aliases to build `tma_fp_arith`, `tma_fp_scalar`, `tma_fp_vector`, `tma_fp_vector_128b`, `tma_fp_vector_256b`, instruction mix metrics, and GFLOPS estimates. Assist events contribute to heavy-operation and microcode-sequencer diagnosis.

## State and Persistence
The file is static. Runtime state is limited to counter values or PEBS-free sampling records collected by perf. The semantic persistence contract is that the retired arithmetic aliases continue to represent Broadwell-DE's scalar, packed, vector, and flop-count categories expected by top-down metrics.

## Dependencies and Integration
The file integrates with `bdwde-metrics.json` floating-point formulas and with pipeline events for assists, uop dispatch, and retirement. It depends on perf's core event parser and the Broadwell-DE PMU encodings.

## Risks
The biggest risks are formula misuse: retired FP instruction counts are not automatically equal to floating-point operations unless the metric weights match vector width and precision. Errata-marked events need conservative interpretation. AVX/SSE transition assists may be workload rare and can be hidden by multiplexing or sampling intervals.

## Test Signals
Use `jq empty`, `perf list | grep FP_ARITH_INST_RETIRED`, and controlled scalar SSE, AVX128, and AVX256 workloads to check the expected event families. Metric tests should validate `Flops`, `FpScalar`, and `FpVector` groups and compare rough GFLOPS output against known loop work.
