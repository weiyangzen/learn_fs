<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/sve.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/sve.json

## Purpose
Monaka SVE and SIMD operation topic. It covers SIMD/SVE retirement and speculation, SVE math, integer and non-FP operation classes, predicate generation and permutes, MOVPRFX modes, vector/scalar cross-pipeline transfers, SVE load/store/prefetch patterns, non-temporal accesses, gather/scatter, first-fault loads, precision-scaled FP operations, and integer dot/matrix operations.

## APIs, Types, and Functions
The file uses only `ArchStdEvent` records with Monaka descriptions. Important aliases include `SIMD_INST_RETIRED`, `SVE_INST_RETIRED`, `SVE_INST_SPEC`, `ASE_SVE_INST_SPEC`, `SVE_INT_SPEC`, `SVE_PRED_SPEC`, `SVE_MOVPRFX_Z_SPEC`, `SVE_MOVPRFX_M_SPEC`, `SVE_LDNT_CONTIG_SPEC`, `SVE_STNT_CONTIG_SPEC`, `SVE_LD_GATHER_SPEC`, `SVE_ST_SCATTER_SPEC`, `FP_*_SCALE_OPS_SPEC`, and `ASE_SVE_INT_MMLA_SPEC`.

## Control Flow, State, and Persistence
At build time, perf resolves all standard aliases into the generated Monaka PMU table. Runtime counters are selected by alias through perf; the JSON has no live state or persistence outside source control.

## Dependencies and Integration
Depends on ARM64 common/microarchitecture SVE event definitions. It integrates with `fp_operation.json`, `pipeline.json`, and cache topics for vectorization, predicate density, and memory behavior analysis.

## Risks and Test Signals
Risks include interpreting scalable operation counts without accounting for vector-length semantics, overlapping ASIMD/SVE aggregate aliases, and MOVPRFX fused versus unfused counts being subtle. Test signals are alias-resolution success, SVE integer/FP/gather/scatter/non-temporal microbenchmarks, predicate-density tests for empty/full/partial behavior, and comparison with scalar or ASIMD baselines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/sve.json -->
