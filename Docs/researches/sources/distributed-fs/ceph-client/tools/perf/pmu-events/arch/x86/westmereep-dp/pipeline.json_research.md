# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/pipeline.json

Purpose: provides 111 DP pipeline, branch, retirement, stall, uop, arithmetic, and clock aliases. It is the central Westmere-EP DP table for execution pipeline and top-level performance analysis.

Important APIs/types/functions: records use normal event fields plus advanced modifiers including `CounterMask`, `EdgeDetect`, `Invert`, `AnyThread`, and `PEBS`. Major families include `ARITH.*`, `BR_INST_EXEC.*`, `BR_MISP_EXEC.*`, `BR_INST_RETIRED.*`, `CPU_CLK_UNHALTED.*`, `ILD_STALL.*`, `INST_RETIRED.*`, `RESOURCE_STALLS.*`, `UOPS_DECODED.*`, `UOPS_EXECUTED.*`, `UOPS_ISSUED.*`, and `UOPS_RETIRED.*`.

Control flow: `jevents.py` transforms event names and modifiers into generated C table rows. Fixed-counter aliases such as `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF` rely on `JsonEvent.real_event` special handling instead of ordinary event-code fields. Runtime perf schedules these aliases subject to counter and modifier constraints.

State and persistence: only static JSON persists. Active event groups may program fixed counters, generic counters, PEBS precise events, edge detection, inversion, and any-thread counting depending on the selected alias.

Dependencies and integration points: depends on perf's generated PMU table APIs and Westmere event semantics. Integrates with branch analysis, IPC calculations, frontend/backend stall diagnosis, and uop port utilization.

Risks: many entries share raw selectors with different modifiers, so a dropped `CounterMask`, `Invert`, `EdgeDetect`, or `AnyThread` changes meaning completely. Several aliases are cycle-style derived encodings, not plain event counts. Fixed-counter aliases must remain compatible with perf's hardcoded mappings.

Test signals: generated table inspection, `perf list` for `uops_*` and `br_*`, event scheduling tests with and without grouping, and sanity checks such as retired instructions and cycles increasing with workload duration.
