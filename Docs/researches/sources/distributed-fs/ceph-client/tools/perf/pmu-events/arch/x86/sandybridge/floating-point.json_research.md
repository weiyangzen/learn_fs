## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/floating-point.json

### Purpose
`floating-point.json` defines 15 Sandy Bridge floating-point and SIMD PMU events. It covers FP assists, SSE scalar and packed operations, x87 work, AVX/SSE transition assists, AVX store assists, and 256-bit SIMD FP operations.

### Important APIs, Types, And Data Fields
The file is an event-object array with standard core PMU fields:

- `EventName` includes `FP_ASSIST.*`, `FP_COMP_OPS_EXE.*`, `OTHER_ASSISTS.AVX_*`, and `SIMD_FP_256.*`.
- `EventCode` and `UMask` encode the event selectors.
- `Counter` is generally `0,1,2,3`.
- `CounterMask` appears on `FP_ASSIST.ANY` to count cycles with any FP assist.
- `BriefDescription` describes the visible perf event.
- `SampleAfterValue` supplies sampling defaults.

No functions or types are implemented locally; the data schema is the interface.

### Control Flow And Data Flow
Perf generation converts each event object into a named PMU event. Runtime users select the events directly or through metrics. `snb-metrics.json` consumes these names in formulas including `tma_fp_scalar`, `tma_fp_vector`, `tma_fp_vector_128b`, `tma_fp_vector_256b`, `tma_x87_use`, `tma_info_core_flopc`, and `tma_info_system_gflops`.

### State And Persistence
This file is static metadata. It persists Sandy Bridge FP event encodings and descriptions. Runtime counter values are produced by hardware and are not stored here.

### Dependencies And Integration Points
The definitions depend on Sandy Bridge's FP/SIMD event model and integrate with perf event parsing, top-down metric evaluation, and HPC-oriented metric groups such as `Compute`, `Flops`, and `HPC`.

### Risks
The main risk is formula drift: if an FP event is renamed or encoded incorrectly, derived FLOP and top-down compute metrics become invalid. The descriptions include legacy terminology around AVX/GSSE and should remain aligned with perf's accepted event names. `CounterMask` handling for `FP_ASSIST.ANY` should be preserved because it changes the meaning from occurrences to cycles.

### Test Signals
Check JSON validity, schema fields, generated `perf list` entries for `FP_COMP_OPS_EXE.SSE_PACKED_DOUBLE` and `SIMD_FP_256.PACKED_SINGLE`, and metric parser tests for formulas that reference FP event names.
