# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/floating-point.json

## Purpose
Broadwell floating-point and SIMD event table for Linux `perf`. The file is a JSON array of 22 event definitions used to count retired FP arithmetic by precision/vector width, FP assists, SIMD move elimination, AVX/SSE transition assists, and SIMD physical register file dispatch cancellations.

These events are the raw inputs for FP/HPC metrics in `bdw-metrics.json`, including scalar/vector FP fractions, vector-width breakdowns, FLOP rate estimates, FP arithmetic utilization, and x87/assist-related top-down categories.

## Important APIs, Types, and Functions
The event schema mirrors the other Broadwell PMU event files:

- `EventName`: aliases such as `FP_ARITH_INST_RETIRED.SCALAR_DOUBLE`, `FP_ARITH_INST_RETIRED.256B_PACKED_SINGLE`, `FP_ASSIST.ANY`, `OTHER_ASSISTS.AVX_TO_SSE`, and `UOP_DISPATCHES_CANCELLED.SIMD_PRF`.
- `EventCode`: mainly `0xc7` for FP arithmetic retirement, `0xCA` for FP assists, `0x58` for move elimination, `0xC1` for other assists, and `0xA0` for dispatch cancellations.
- `UMask`: subevent mask selecting precision, width, assist type, transition direction, or PRF cancellation category.
- `Counter`: all rows allow core programmable counters `0,1,2,3`.
- `CounterMask`: only `FP_ASSIST.ANY` uses `1`, making it a cycle-qualified assist event rather than a raw per-assist subevent like the other `FP_ASSIST.*` rows.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue`: descriptive and sampling metadata.

There are no functions. Event families define the data API. `FP_ARITH_INST_RETIRED.*` includes scalar single/double, packed 128-bit/256-bit single/double, aggregate scalar/vector/single/double/packed aliases, and the combined `4_FLOPS` category. Descriptions specify how many FP operations each retired instruction represents and note that some DPP or fused multiply-add/subtract instructions count twice.

## Control Flow
At build/load time, perf ingests these rows as Broadwell event aliases. At runtime, direct user requests or metric expressions resolve the alias to the event code and umask, then program one of the core generic counters. Metric expressions in `bdw-metrics.json` combine these counts with retired slots, instructions, elapsed time, or core clocks to derive FP ratios and FLOP rates.

The important data-driven control is aggregation. For example, metrics treat `FP_ARITH_INST_RETIRED.SCALAR` and `FP_ARITH_INST_RETIRED.VECTOR` as broad categories, while width-specific metrics use `128B_PACKED_*` and `256B_PACKED_*`. System GFLOP formulas weight scalar, 128-bit packed double, 4-FLOP, and 256-bit packed single events differently.

## State and Persistence Behavior
The JSON is persistent static metadata. Runtime values live in PMU counters during a perf session. Floating-point interpretation depends on workload MXCSR state and instruction mix but is not persisted here.

The public descriptions include an operational caveat: DAZ and FTZ flags in MXCSR need to be set when using many FP arithmetic events. That is not enforced by the metadata, so runtime state outside perf can affect count interpretability.

## Dependencies and Integration Points
This file integrates with perf PMU-events and with `bdw-metrics.json` FP-related metrics such as `tma_fp_scalar`, `tma_fp_vector`, `tma_fp_vector_128b`, `tma_fp_vector_256b`, `tma_info_core_flopc`, `tma_info_core_fp_arith_utilization`, `tma_info_system_gflops`, and instruction-mix metrics like `tma_info_inst_mix_iparith_*`.

It also depends on Broadwell PMU semantics for FP arithmetic retirement, SIMD/x87 assist classification, SIMD move elimination, AVX/SSE transition penalties, and scheduler dispatch cancellation events.

## Risks
Key risks are semantic accuracy and documentation consistency:

- Arithmetic events count retired instructions or microarchitectural events, not always mathematical operations directly. Metrics must apply the correct vector-width multipliers.
- Descriptions note doubled counts for some DPP and fused operations; users can over- or under-estimate FLOPs if they treat all counts uniformly.
- Several public descriptions mention DAZ/FTZ MXCSR requirements. Results can be misleading if workloads run with different denormal handling.
- `FP_ASSIST.ANY` uses a cmask cycle encoding while specific assist rows count assist occurrences; mixing them without recognizing the unit difference is risky.
- Aggregate aliases such as `FP_ARITH_INST_RETIRED.SINGLE`, `DOUBLE`, `PACKED`, `SCALAR`, and `VECTOR` overlap with more specific aliases, so summing them naively double-counts.
- Broadwell event semantics may differ from later Intel generations, especially around AVX widths and fused operations.

## Test Signals
Validation should include JSON parsing, generated event map checks, `perf list` visibility, and runtime smoke tests for scalar, packed, assist, transition, and move-elimination aliases. Metric-level tests should verify that `perf stat -M tma_fp_scalar,tma_fp_vector,tma_info_system_gflops` resolves all referenced events. Microbenchmarks with scalar FP, 128-bit packed FP, 256-bit packed FP, and denormal/assist-heavy operations can validate that the expected event families move while unrelated families remain comparatively low.
