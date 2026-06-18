# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/floating-point.json

## Purpose
This JSON file defines 10 Intel Haswell core PMU events for floating-point, SIMD, AVX/SSE transition, and SIMD move-elimination analysis in perf. The source was read as a complete 93-line JSON array.

## Important APIs, Types, and Functions
Every row has `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`; eight rows include `PublicDescription`. Some rows include `CounterMask`, and the AVX/SSE transition events include `Errata: "HSD56, HSM57"`. There are 10 unique event names over four event codes: `AVX_INSTS.ALL` (`0xC6`), `FP_ASSIST.*` (`0xCA`), `MOVE_ELIMINATION.SIMD_*` (`0x58`), and `OTHER_ASSISTS.*` (`0xC1`). Counters are generic `0,1,2,3`.

The event set includes approximate AVX instruction counting, SIMD and x87 FP assists for input/output values, SIMD move-elimination candidates that were eliminated or not eliminated, and transition penalties from AVX-256 to legacy SSE or from SSE to AVX-256. There are no metric expressions or uncore fields.

## Control Flow, State, and Persistence
The file is declarative. `jevents.py` parses it during build generation and emits generated event metadata. Runtime perf resolves aliases to core PMU selectors and counts or samples them with the configured sample-after defaults.

Static state is the event selector mapping, sample period, counter mask, and errata metadata. `FP_ASSIST.ANY` aggregates multiple assist unit masks, while the specific `SIMD_INPUT`, `SIMD_OUTPUT`, `X87_INPUT`, and `X87_OUTPUT` aliases break down causes. Persistence is through generated perf tables; observed assist and transition counts are workload-local.

## Dependencies and Integration Points
Dependencies include Haswell PMU definitions, perf's JSON schema, `jevents.py`, and kernel core PMU support. The file integrates with `perf list`, `perf stat`, and sampling workflows for floating-point-heavy applications. It is useful with compiler vectorization analysis, numerical workloads, AVX/SSE mixed-code investigations, and microarchitecture tuning.

These events integrate conceptually with frontend/backend and retirement events, since FP assists and AVX/SSE transitions can create pipeline penalties not visible from instruction count alone.

## Risks and Test Signals
Risks include approximate semantics for `AVX_INSTS.ALL`, errata on `OTHER_ASSISTS.AVX_TO_SSE` and `OTHER_ASSISTS.SSE_TO_AVX`, and confusion between assist cycles and assist occurrences depending on the specific event. Transition events may depend on code generation, OS XSAVE behavior, and library mixing, so zero counts do not necessarily mean the event is broken.

Test signals include JSON validation, generated event-table checks, `perf list` visibility, and targeted Haswell workloads: AVX2 loops for `AVX_INSTS.ALL`, denormal or exceptional FP inputs for assist events, register move-heavy SIMD code for move elimination, and mixed AVX/SSE call paths for transition assists. Errata should be reviewed against the exact CPU stepping used for validation.
