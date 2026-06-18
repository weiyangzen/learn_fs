# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/floating-point.json

## Purpose

`floating-point.json` defines Rocket Lake perf events for floating-point assists and retired SSE/AVX arithmetic instruction classes. It contains 13 event rows: one `ASSISTS.FP` row and twelve `FP_ARITH_INST_RETIRED.*` rows covering scalar, vector, packed single, packed double, and width-based FLOP categories from 128-bit through 512-bit.

## Important APIs, Types, and Data Fields

Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. `ASSISTS.FP` uses event `0xc1`, umask `0x2`, and counters `0-7`. All arithmetic rows use event `0xc7` with different umasks for scalar, scalar single, scalar double, vector, packed 128-bit, 256-bit, 512-bit, and combined `4_FLOPS`/`8_FLOPS` categories. Descriptions explicitly state how many operations each retired instruction represents and warn that DAZ and FTZ MXCSR flags need to be set for these events.

## Control Flow and Data Flow

Build-time flow is standard JSON-to-generated-table processing through `jevents.py`. Runtime flow is perf programming the core PMU for the chosen alias. The hardware increments counters as matching floating-point instructions retire or as floating-point microcode assists occur. Higher-level analysis often multiplies counts by lane widths to estimate operations or FLOP rates, using the descriptions to distinguish scalar, packed single, packed double, and vector rows.

## State and Persistence Behavior

The file stores static metadata and default sample periods only. Runtime SIMD width, instruction mix, MXCSR state, and assist causes are external state. The meaning of a count depends on instruction class: one count can represent different numbers of arithmetic operations depending on vector width and precision. `ASSISTS.FP` measures assist events rather than retired arithmetic throughput.

## Dependencies and Integration Points

This catalog depends on Rocket Lake core PMU support and perf event-table generation. It integrates with `perf stat`, HPC FLOP accounting, compiler vectorization analysis, numerical workload tuning, and Intel metrics that group floating-point throughput under FLOPS or top-down compute categories. It complements pipeline events for execution pressure and memory/cache events for distinguishing compute-bound from memory-bound code.

## Risks and Edge Cases

Counts are not automatically FLOPs; consumers must apply the documented operation multiplier and account for instructions that count twice, such as some DPP and fused multiply-add/subtract forms. MXCSR DAZ/FTZ requirements can affect validity. 512-bit categories may be irrelevant for workloads or systems where those instruction classes are unavailable or downclocked. `ASSISTS.FP` can indicate exceptional or denormal behavior but does not identify the exact instruction without sampling context.

## Test Signals

Validation should parse the JSON, build generated tables, and expose all `FP_ARITH_INST_RETIRED.*` aliases. Microbenchmarks using scalar, 128-bit, 256-bit, and 512-bit arithmetic should move the corresponding rows. Denormal or exception-heavy floating-point tests should raise `ASSISTS.FP`. FLOP-rate tests should verify that count-to-operation conversion uses the documented lane multipliers and special double-count cases.
