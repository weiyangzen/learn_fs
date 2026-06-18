# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/floating-point.json

## Purpose
`floating-point.json` defines 28 Sapphire Rapids core PMU events for floating-point assists, divide activity, FP dispatch ports, retired SSE/AVX/AVX-512 arithmetic instructions, and half-precision arithmetic. It supports `perf stat` and `perf record` analysis of scalar/vector FP intensity and FP pipeline behavior.

## Important APIs, types, and schema fields
This file uses the standard event object fields `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. `Counter` is consistently `0,1,2,3,4,5,6,7`, matching the 8 generic core counters in `counter.json`. `CounterMask` is used by `ARITH.FPDIV_ACTIVE` to count cycles where the divide unit is active.

## Control flow and integration
Perf's PMU event generator compiles these JSON entries into the Sapphire Rapids event table. At runtime, event names such as `FP_ARITH_INST_RETIRED.512B_PACKED_SINGLE` resolve to event select `0xc7` plus the appropriate umask. The `FP_ARITH_DISPATCHED.PORT_*` and `V*` pairs are aliases over identical encodings, so event lookup must preserve both names while programming the same hardware selector.

## State and persistence behavior
The file stores static FP event metadata and descriptions. Hardware counts are maintained in core PMU counters. The descriptions include semantic multipliers: packed single/double events describe how many operations each event represents and warn that some FMA/DPP instructions count twice. Several retired FP events require DAZ and FTZ flags in MXCSR for reliable use; that runtime precondition is documented here rather than enforced by perf.

## Dependencies
The entries depend on Sapphire Rapids FP PMU semantics, vector ISA support, and perf's core event parser. The file integrates with top-down and HPC metrics through event names like `FP_ARITH_INST_RETIRED.*`, and with `metricgroups.json` groups such as `Flops`, `FpScalar`, `FpVector`, `HPC`, `tma_fp_arith_group`, and `tma_fp_vector_group`.

## Risks and edge cases
The biggest correctness risk is interpreting counts as FLOPs without applying width and instruction semantics. The retired arithmetic events count instructions or operations depending on the description, and FMA/DPP can double count computational work. Alias pairs (`PORT_0`/`V0`, `PORT_1`/`V1`, `PORT_5`/`V2`) must stay synchronized. Half-precision entries in `FP_ARITH_INST_RETIRED2.*` have minimal public descriptions, so downstream documentation or metrics should avoid inventing semantics not present in the source.

## Test signals
Validate JSON syntax and generated tables. `perf list fp` on a Sapphire Rapids-enabled build should show all 28 names. Microbenchmarks with scalar double/single, 128/256/512-bit vector loops, half-precision operations, and divides can sanity-check selector/umask behavior. Metric tests should confirm aliases resolve to identical raw encodings and that FP events can schedule on generic core counters 0-7.
