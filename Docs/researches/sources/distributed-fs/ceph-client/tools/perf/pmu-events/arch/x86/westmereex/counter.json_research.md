# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/counter.json

Purpose: declares the Westmere EX core PMU counter inventory for perf's event metadata system. It tells perf that the `core` PMU has four fixed counters and four generic programmable counters.

Important APIs/types/functions: the file contains a single JSON object with `Unit: "core"`, `CountersNumFixed: "4"`, and `CountersNumGeneric: "4"`. These fields are schema-level metadata rather than event definitions; there is no `EventName`, `EventCode`, or `BriefDescription` because the row describes the PMU unit itself.

Control flow: there is no executable flow. During pmu-events generation, the row is loaded alongside event rows and becomes model metadata used by perf tooling when displaying or reasoning about available counters.

State and persistence: static source metadata only. It does not store measurements or alter persistent system state.

Dependencies: depends on perf's PMU JSON parser recognizing unit rows with `Unit` and counter-count fields. It must stay consistent with counter constraints in sibling event files, especially fixed-counter rows in `pipeline.json` and counter-specific offcore/load-latency events in `cache.json` and `memory.json`.

Integration points: integrates with all Westmere EX event categories under the same directory by defining the counter capacity those events target. It also complements perf's runtime PMU discovery; mismatches between this static metadata and kernel PMU capabilities can cause confusing event scheduling or display behavior.

Risks: an incorrect generic or fixed counter count would skew perf's generated metadata and may lead users or tooling to expect unsupported counter scheduling. Because the row has no event name, validators must distinguish it from malformed event rows.

Test signals: JSON parsing is the primary syntax check. Schema tests should verify exactly one unit row for `core`, numeric string values for both counter counts, and consistency with event `Counter` references such as `Fixed counter 1`, `Fixed counter 2`, `Fixed counter 3`, and generic `0,1,2,3`.
