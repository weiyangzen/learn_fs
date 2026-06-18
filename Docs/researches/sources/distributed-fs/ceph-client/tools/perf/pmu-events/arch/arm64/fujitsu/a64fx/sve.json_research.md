<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/sve.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/sve.json

## Purpose
A64FX SVE topic table made entirely from ARM64 architecture-standard event aliases. It provides perf names for SVE instruction retirement/speculation, MOVPRFX, predicate activity, SVE loads/stores/prefetches, gather/scatter, first-fault loads, and scalable versus fixed floating-point operation counts.

## APIs, Types, and Functions
Each entry contains `ArchStdEvent` only, so `jevents.py` dereferences names from `arch/arm64/common-and-microarch.json`. Key aliases include `SIMD_INST_RETIRED`, `SVE_INST_RETIRED`, `UOP_SPEC`, `SVE_MATH_SPEC`, `SVE_PRED_SPEC`, `SVE_MOVPRFX_SPEC`, `SVE_LD_GATHER_SPEC`, `SVE_ST_SCATTER_SPEC`, and `FP_*_SCALE_OPS_SPEC`/`FP_*_FIXED_OPS_SPEC`.

## Control Flow, State, and Persistence
Build-time flow is alias resolution from the architecture-standard table into the A64FX generated event table. Runtime state is limited to the selected PMU and active event counters; the JSON itself persists only event membership for the A64FX model.

## Dependencies and Integration
Depends strongly on the ARM64 standard event catalog and on the A64FX mapfile row. It integrates with pipeline predicate counters and A64FX floating-point counters to support vectorization and SVE utilization analysis.

## Risks and Test Signals
Risks are unresolved standard aliases, semantic mismatch between standard event text and A64FX implementation behavior, and analysis mistakes when scalable-operation counters increment by vector-length-normalized units. Test signals are successful alias generation, `perf list` exposing all SVE names, and hardware runs with SVE vector loops, MOVPRFX-heavy sequences, gather/scatter kernels, and scalar baselines showing expected counter separation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/sve.json -->
