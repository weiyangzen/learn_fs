# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/floating-point.json

## Purpose

`floating-point.json` defines 10 Skylake events for floating-point arithmetic retirement and floating-point/SSE assist cycles. The primary purpose is to expose FP operation mix and assist overhead to perf users profiling numerical workloads.

Most entries are variants of `FP_ARITH_INST_RETIRED.*`, all using event code `0xC7` with different unit masks for scalar, 128-bit packed, 256-bit packed, vector aggregate, and mixed four-flop classes. These records encode Intel's operation-count semantics in descriptions, including the fact that some DPP and FMA/FMS instructions count twice.

## Important schema/API surface

Important records include:

- `FP_ARITH_INST_RETIRED.SCALAR`, `.SCALAR_SINGLE`, `.SCALAR_DOUBLE`, `.128B_PACKED_SINGLE`, `.128B_PACKED_DOUBLE`, `.256B_PACKED_SINGLE`, `.256B_PACKED_DOUBLE`, `.4_FLOPS`, and `.VECTOR`.
- `FP_ASSIST.ANY`, event code `0xCA`, unit mask `0x1e`, `CounterMask: 1`, counting cycles with SSE/x87 assists.

The key fields are `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. The FP arithmetic descriptions are part of the effective API because consumers need them to convert instruction counts to operation counts correctly.

## Control flow and integration

Perf loads the file as a Skylake event category and exposes the names as aliases. Selecting one of the FP arithmetic names programs a generic counter with event code `0xC7` and the corresponding mask. The same base event with multiple masks is intentional and lets users break down scalar versus vector width and precision.

The FP assist event uses a counter mask to count cycles rather than simple occurrences. That affects how perf users interpret results: it is a stall/assist duration signal, not a retired-instruction count.

## State and persistence behavior

The file is static metadata. Runtime state resides in PMU counters and sampled perf records. There is no persistence beyond the source JSON and generated perf alias tables.

## Dependencies

The descriptors depend on Skylake's SIMD FP event semantics, MXCSR behavior, and perf's schema support. Several public descriptions state that DAZ and FTZ flags in MXCSR need to be set when using the FP arithmetic events, so measurement accuracy depends on workload floating-point environment as well as PMU programming.

## Risks and maintenance notes

Interpretation risk is high for FLOP counting. Event increments are not always equal to one arithmetic operation: vector width changes element count, packed single/double have different element counts, and some DPP/FMA/FMS instructions count twice. A downstream metric that treats raw event counts uniformly will misreport FLOPs.

`FP_ARITH_INST_RETIRED.VECTOR` lacks a detailed public description compared with the width-specific variants, so users may need to prefer the more specific events for documentation-rich analyses. Category-based tooling can treat this file as focused on FP arithmetic/assist coverage.

## Test signals

Syntax and schema validation should confirm all 10 entries have valid names and encodings. Alias smoke tests should include one scalar event, one 128-bit packed event, one 256-bit packed event, and `FP_ASSIST.ANY`. Documentation validation should preserve the MXCSR DAZ/FTZ notes and the doubled-count behavior for DPP/FMA/FMS instructions.
