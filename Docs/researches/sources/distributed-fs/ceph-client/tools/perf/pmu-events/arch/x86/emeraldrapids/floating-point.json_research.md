<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/floating-point.json

## Purpose
Defines Emerald Rapids raw PMU events for floating-point activity, assists, FP dispatch ports, retired scalar/vector FP arithmetic, and half-precision FP arithmetic. The file provides the event encodings that perf exposes as named events and that derived metrics in `emr-metrics.json` use for FLOP and FP utilization calculations.

## Important APIs, Types, And Functions
- Top-level type: JSON array of 28 event records.
- Common event fields: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`.
- Optional precision fields: `PublicDescription` for user-facing detail and `CounterMask` for cycle-style events such as `ARITH.FPDIV_ACTIVE`.
- Major event families:
  - `ARITH.FPDIV_ACTIVE` and `ASSISTS.FP` / `ASSISTS.SSE_AVX_MIX` for FP divider and assist behavior.
  - `FP_ARITH_DISPATCHED.PORT_0`, `.PORT_1`, `.PORT_5` and aliases `.V0`, `.V1`, `.V2` for FP arithmetic dispatch by execution vector/port.
  - `FP_ARITH_INST_RETIRED.*` for scalar, 128-bit, 256-bit, 512-bit, vector, and combined FLOP-width buckets.
  - `FP_ARITH_INST_RETIRED2.*` for scalar, vector, complex scalar, and packed half-precision arithmetic.

## Control Flow
Perf loads the array as named event metadata for the Emerald Rapids model. When a user requests an event such as `FP_ARITH_INST_RETIRED.512B_PACKED_SINGLE` or a derived metric that references it, perf maps `EventCode` plus `UMask` and optional modifiers such as `CounterMask` onto a programmable PMU counter from the declared `Counter` set. Sampling defaults come from `SampleAfterValue`; counting mode uses the same event encoding without a sample overflow workflow unless the user asks for sampling.

## State And Persistence
The file has no mutable state. It persists the architectural encoding and descriptions in source control. Runtime state is the programmed counter selection and accumulated event counts. Several records count instructions where one retired instruction can represent multiple floating-point operations; interpretation depends on vector width and instruction semantics, not on state stored in this file.

## Dependencies And Integration Points
- Consumed by Linux perf's x86 pmu-events JSON pipeline and by generated event tables for Emerald Rapids.
- Referenced by derived metrics such as `tma_fp_arith`, `tma_fp_vector`, `tma_fp_scalar`, vector-width breakdown metrics, and GFLOPS-style informational metrics.
- Depends on Intel's Emerald Rapids PMU event encodings for event codes `0xb0`, `0xb3`, `0xc1`, `0xc7`, and `0xcf`.
- Integrates with user workflows that inspect SIMD width mix, FP assist cost, divider activity, and AVX/SSE transition or half-precision usage.

## Risks And Edge Cases
- Alias records deliberately share encodings, for example port names and `V0`/`V1`/`V2`; tools or tests must not treat identical encodings as accidental duplicates without checking aliases.
- Public descriptions note that DAZ and FTZ MXCSR flags need to be set for many FP arithmetic retired events. Measurements without those flags can be misleading.
- FLOP interpretation is not one-to-one with instruction count for DPP and FMA-style instructions; derived metrics must preserve the documented multiplication semantics.
- `FP_ARITH_INST_RETIRED2.SCALAR` uses `UMask` `0x3`, overlapping scalar half and complex scalar half buckets by design. Consumers must respect masks rather than assuming categories are disjoint.
- Counter availability is broad for many events but still bound by PMU scheduling pressure when combined with topdown or memory metrics.

## Test Signals
- JSON syntax validation should pass and every record should include `EventName`, `EventCode`, `UMask`, and `Counter`.
- `perf list` on an Emerald Rapids event table should show the FP event names and alias descriptions.
- `perf stat -e FP_ARITH_INST_RETIRED.SCALAR,FP_ARITH_INST_RETIRED.VECTOR,FP_ARITH_INST_RETIRED2.VECTOR` should parse and schedule on supported hardware.
- Workloads with known scalar, AVX2, AVX-512, and FP16 instruction mixes should move the corresponding event buckets.
- Derived FP metrics in `emr-metrics.json` should continue to resolve all referenced FP event names after edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/floating-point.json -->
