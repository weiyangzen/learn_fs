# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/floating-point.json

## Purpose

`floating-point.json` defines 32 Meteor Lake floating-point and vector arithmetic PMU events. It covers floating-point divider activity, FP assists, SSE/AVX transition assists, core FP arithmetic dispatch ports, retired FP arithmetic by scalar/vector width and precision, atom floating-point operation counts, atom FP instruction retired classes, vector-integer/FP store-data port execution, FP-assist machine clears, and retired FP divide uops.

## Important APIs, Types, And Data Shape

The file is an event array with `EventName`, `Unit`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Deprecated`. It includes both `cpu_core` and `cpu_atom` encodings for `ARITH.FPDIV_ACTIVE`. Core events focus on `FP_ARITH_DISPATCHED.*` and `FP_ARITH_INST_RETIRED.*`; atom events include `FP_FLOPS_RETIRED.*`, `FP_INST_RETIRED.*`, `MACHINE_CLEARS.FP_ASSIST`, and `UOPS_RETIRED.FPDIV`. Deprecated aliases preserve older names `FP_FLOPS_RETIRED.DP` and `FP_FLOPS_RETIRED.SP`, pointing users toward `FP64` and `FP32`.

## Control Flow

The generator assigns topic `floating-point`, lowercases aliases, and emits the event records into generated perf tables. At runtime, perf users collect these aliases per PMU unit. Derived FLOP or vectorization metrics use the retired arithmetic counts and must account for Intel's documented weighting, especially packed and fused operations that count multiple operations per instruction.

## State And Persistence

The JSON is static. Generated tables preserve alias spellings, deprecation flags, event encodings, and long descriptions. Runtime PMU state is transient and per collection. There is no source-level persistence.

## Dependencies And Integration Points

Dependencies include Meteor Lake hybrid PMU encodings, SIMD width/precision semantics, and perf's PMU alias generator. Integration points include `perf list floating-point`, HPC metric groups such as `Flops`, `FpScalar`, `FpVector`, `Compute`, and generated metrics from Intel metric scripts. FP assist events also integrate conceptually with pipeline machine-clear and assist analysis.

## Risks

FLOP interpretation is the main risk. Several descriptions state that each count represents multiple computational operations and that FMA or DPP instructions can count twice, so downstream metrics must not equate event counts directly to instructions. Deprecated aliases should remain marked to guide users without breaking compatibility. Hybrid differences matter: core dispatch-port aliases do not apply to atom PMUs, and atom FP FLOP aliases do not imply the same encoding on core PMUs.

## Test Signals

Validation should check array length 32, both units present, deprecated flags on `FP_FLOPS_RETIRED.DP` and `FP_FLOPS_RETIRED.SP`, and successful generated C output. Runtime tests include `perf list floating-point`, simple scalar and vector FP kernels to exercise width-specific retired events, and divide-heavy workloads to validate `ARITH.FPDIV_ACTIVE` and `UOPS_RETIRED.FPDIV`.
