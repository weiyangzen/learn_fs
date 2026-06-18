# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/floating-point.json

Purpose: defines 28 Westmere-EP SP floating-point and SIMD aliases. The content matches the DP floating-point topic in shape and event families, but is bound to the SP model directory.

Important APIs/types/functions: standard event records cover `FP_ASSIST.*`, `FP_COMP_OPS_EXE.*`, `FP_MMX_TRANS.*`, `SIMD_INT_128.*`, and `SIMD_INT_64.*`. Fields include `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PEBS` for precise assist events.

Control flow: `jevents.py` parses the file during perf build, derives the topic from `floating-point.json`, lowercases aliases, and emits generated `struct pmu_event` rows. Runtime table selection comes from `GenuineIntel-6-25,v4,westmereep-sp,core` in `mapfile.csv`.

State and persistence: no mutable state. perf configures generic counters and PEBS sampling only when aliases are requested.

Dependencies and integration points: integrates with floating-point assist diagnosis, SIMD utilization analysis, and legacy MMX/SSE transition detection. It shares the generated PMU event table API in `pmu-events.h`.

Risks: the table counts uops and assists, not high-level FLOPs metrics. Users must distinguish scalar, packed, single, double, SSE integer, and MMX rows. Incorrect PEBS labeling on assist events affects sampled attribution.

Test signals: valid JSON, successful perf event table generation, `perf list fp_` output on a build containing these tables, and hardware runs using floating-point/SIMD microbenchmarks to check expected counter movement.
