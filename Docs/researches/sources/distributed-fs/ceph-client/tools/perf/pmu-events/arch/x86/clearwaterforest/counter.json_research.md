# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/counter.json

Purpose: Declares Clearwater Forest core PMU counter capacity metadata for perf. The single JSON object states that the core PMU has `CountersNumFixed: 3` and `CountersNumGeneric: 39` for `Unit: core`.

Important APIs/types/functions: This file uses a metadata-only variant of the perf PMU events JSON schema. It has no `EventName`; instead, `jevents.py` treats the object as PMU unit metadata. `Unit` identifies the affected PMU namespace, while `CountersNumFixed` and `CountersNumGeneric` describe fixed and generic counter counts available for scheduling and display logic.

Control flow: During build generation, the metadata is folded into the Clearwater Forest generated PMU table rather than becoming a user-facing event alias. At runtime, perf can use the generated counter-count metadata alongside normal event aliases from `cache.json`, `pipeline.json`, and other topic files when reasoning about available fixed and generic counters.

State and persistence behavior: The file contains static hardware capability metadata. It creates no counters, events, or persisted runtime measurements. The values persist in the generated perf binary until the PMU event tables are regenerated.

Dependencies: Depends on `jevents.py` accepting JSON records without `EventName` and on perf's generated PMU-events structures preserving counter metadata. It must stay consistent with Clearwater Forest hardware and with fixed-counter event rows in `pipeline.json`, where counters 36, 37, and 38 are used for topdown slots and fixed counters 0 through 2 are used for instructions/core/reference cycles.

Integration points: Integrates with the Clearwater Forest model directory and x86 mapfile row. It is the capacity companion to the event-topic files, especially `pipeline.json` where both fixed counters and high-number topdown counters are named explicitly.

Risks: Incorrect counter counts can cause perf to over-schedule events, reject valid groups, or display misleading hardware capabilities. Because the file has no `EventName`, validation scripts that assume every JSON object is an event can fail or report a false problem. The 39 generic-counter value is unusual enough that regressions should be checked against vendor PMU documentation and kernel PMU exposure.

Test signals: JSON parsing should report one object with no `EventName`. `jevents.py` generation should not emit an alias but should preserve counter metadata. On hardware or a generated-table inspection, perf should recognize 3 fixed counters and 39 generic counters for Clearwater Forest core PMU capacity.
