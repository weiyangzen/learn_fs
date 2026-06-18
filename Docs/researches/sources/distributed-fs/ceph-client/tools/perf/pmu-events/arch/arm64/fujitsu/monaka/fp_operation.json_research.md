<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/fp_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/fp_operation.json

## Purpose
Monaka floating-point operation topic table. It covers scalar, Advanced SIMD, SVE, mixed ASIMD/SVE, precision-specific, divide, square-root, FMA, multiply, add/subtract, reciprocal estimate, conversion, reduction, dot-product, matrix-multiply, BF16, and FP8 operation families.

## APIs, Types, and Functions
Most records are `ArchStdEvent` aliases resolved from ARM64 standard metadata, with three direct Monaka records: `FP_MV_SPEC`, `FP_LD_SPEC`, and `FP_ST_SPEC`. Important families include `ASE_FP_*`, `SVE_FP_*`, `ASE_SVE_FP_*`, `FP_SCALE_OPS_SPEC`, `FP_FIXED_OPS_SPEC`, `ASE_SVE_FP_DOT_SPEC`, `ASE_SVE_FP_MMLA_SPEC`, and BF16/FP8 minimum operation counters.

## Control Flow, State, and Persistence
Build-time alias resolution merges standard event codes with local descriptions and direct Monaka event codes into the generated PMU table. Runtime perf sessions use the aliases as static event descriptors; no state persists in the JSON.

## Dependencies and Integration
Depends on the ARM64 standard event catalog for architecture-defined floating-point and vector events and Monaka-specific event codes for move/load/store FP register operations. It integrates with `sve.json`, `pipeline.json`, and `metrics.json`-style external calculations for FLOP and vector utilization analysis.

## Risks and Test Signals
Risks include double counting between aggregate and precision-specific aliases, scaled operation counters using element or vector-length units rather than instruction counts, and unsupported BF16/FP8 events on some hardware revisions. Test signals are `jevents.py` resolution success, microbenchmarks for scalar FP, ASIMD, SVE, FMA, reduction, BF16, and FP8 paths, and sanity checks that aggregate counters dominate their subfamilies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/fp_operation.json -->
