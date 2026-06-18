# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/floating-point.json

Purpose: declares 28 Westmere EX floating-point, MMX, SSE, and SIMD integer PMU events for perf. The file covers x87/FP assists, FP-to-MMX transition behavior, computational FP operations, and 64-bit/128-bit SIMD integer operation classes.

Important APIs/types/functions: each row uses the perf event JSON schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`; three `FP_ASSIST.*` rows also carry `PEBS: "1"`. Event families are `FP_ASSIST`, `FP_COMP_OPS_EXE`, `FP_MMX_TRANS`, `SIMD_INT_128`, and `SIMD_INT_64`. All events allow generic counters `0,1,2,3`.

Control flow: no code executes here. The perf generator loads the rows, and runtime perf commands map symbolic event names to raw event code/unit-mask pairs. PEBS-capable assist events can be used for precise sampling when supported by the kernel and hardware.

State and persistence: static metadata only. At measurement time it affects PMU programming and, for precise assist events, PEBS sampling configuration; no state is persisted in the repository.

Dependencies: depends on Westmere EX event encodings and perf's event JSON schema. It also indirectly supports generated metric scripts that validate `Event(...)` names against loaded JSON events.

Integration points: these events are exposed to `perf list` and can be used by `perf stat`, `perf record`, or higher-level metric definitions for FP/SIMD workload characterization. The file complements `pipeline.json`, which also includes `SSEX_UOPS_RETIRED.*` precise SIMD uop retirement events.

Risks: FP and SIMD terminology overlaps with pipeline events, so event names and descriptions must stay precise enough to avoid users mixing executed operations with retired uops. PEBS flags on assist events are semantically important; removing them loses precise sampling. Incorrect `UMask` values can merge or split operation classes incorrectly.

Test signals: parse with `python3 -m json.tool`; verify all 28 rows have unique `EventName` values and required fields; verify all counters are `0,1,2,3`; verify only `FP_ASSIST.*` rows carry `PEBS` in this file. Integration signal is successful pmu-events generation and visibility of representative names such as `FP_COMP_OPS_EXE.SSE_FP` and `SIMD_INT_128.PACKED_ARITH` in generated event lists.
