<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-power.json

## Purpose
This JSON file defines the Grand Ridge uncore power-control topic for perf. The complete 11-line file was read, containing a single `PCU` event record, `UNC_P_CLOCKTICKS`. Its purpose is to expose the PCU clock as a wall-time-like uncore reference counter.

## Important APIs, Types, and Functions
The record uses `EventName`, `EventCode`, `Unit`, `Counter`, `PerPkg`, `BriefDescription`, and `PublicDescription`. `EventCode` is `0x01`, `Unit` is `PCU`, counters are `0,1,2,3`, and `PerPkg` is `1`. There are no functions or classes. The exported alias is the PMU event name that perf users can request when the Grand Ridge `uncore_pcu` PMU is present.

## Control Flow, State, and Persistence
`jevents.py` converts the single record into a generated event descriptor with `event=0x1` and PMU name derived from `PCU`. Because the record has no `UMask`, `PortMask`, or other filters, the generated event string is simple. Runtime perf reads the PCU counter through the kernel PMU driver. State is static; the JSON is source data and the generated C table is the build artifact.

## Dependencies and Integration Points
The file depends on perf's PMU event schema and on kernel support for the Grand Ridge PCU uncore PMU. It integrates with package-level timing for other uncore measurements, where PCU clockticks can be used as a reference for elapsed uncore time or power-management state analysis.

## Risks and Test Signals
The main risk is availability: if the platform or kernel does not expose the PCU PMU, the alias may be generated but unusable at runtime. Since this file has only one event, schema breakage is easy to detect. Test signals include JSON validation, generated `unc_p_clockticks` alias presence, `perf list` visibility, and a `perf stat` smoke test confirming the counter increments near the documented fixed 1 GHz PCU clock while enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-power.json -->
