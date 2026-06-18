# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/floating-point.json

Purpose: defines 28 Westmere-EP dual-processor core PMU aliases for floating-point, MMX, SSE, and SIMD integer execution. It is a static perf event topic file consumed by `tools/perf/pmu-events/jevents.py`, not executable logic.

Important APIs/types/functions: entries use perf's JSON event schema: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PEBS` where precise sampling is supported. The key groups are `FP_ASSIST.*`, `FP_COMP_OPS_EXE.*`, `FP_MMX_TRANS.*`, `SIMD_INT_128.*`, and `SIMD_INT_64.*`. `jevents.py` maps these records into generated `struct pmu_event` rows declared by `pmu-events.h`.

Control flow: during the perf build, the file is discovered under the `westmereep-dp` mapfile directory, parsed as a JSON array, normalized by `JsonEvent` into lowercase perf aliases, and emitted into generated `pmu-events.c`. At runtime, perf selects this table for CPUID `GenuineIntel-6-2C` and exposes names such as `fp_assist.all` and `fp_comp_ops_exe.x87`.

State and persistence: the file is persistent source data only. Runtime state lives in perf's generated tables and event selector setup. PEBS markings on `FP_ASSIST.*` indicate precise sampling capabilities but do not hold state.

Dependencies and integration points: depends on x86 mapfile binding, `jevents.py` field conversions, and the kernel PMU driver accepting event select and umask values. Integrates with `perf stat`, `perf record`, and symbolic event lookup.

Risks: incorrect event codes, umasks, counter availability, or PEBS tags silently mislead profiling. The table does not encode derived metrics, so users must know how to interpret overlapping SIMD categories. Counter fields list generic counters `0,1,2,3`, which must match Westmere-EP hardware constraints.

Test signals: `jq empty` validates syntax. Build-time `jevents.py` generation, perf PMU alias tests, and manual `perf list`/`perf stat -e fp_assist.all` on Westmere-EP hardware are the strongest validation signals.
