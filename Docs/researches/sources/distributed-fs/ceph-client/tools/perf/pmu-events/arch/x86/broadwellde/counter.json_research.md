# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/counter.json

## Purpose
Broadwell-DE PMU counter inventory. It tells perf and related tooling how many fixed and generic counters exist for each core and uncore unit represented by this architecture directory.

## Important APIs, Types, and Functions
The schema has one object per PMU unit with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The file declares `core` with 3 fixed and 4 generic counters, `CBOX` with 4 generic counters, `HA` with 4, `IRP` with 2, `PCU` with 4, `R2PCIe` with 4, `UBOX` with 2, and `iMC` with 4. There are no functions or executable code paths; the unit names are the interface.

## Control Flow
Perf tooling reads this metadata while building or loading event tables, then uses it to reason about event scheduling capacity and unit-specific counter constraints. Core event files reference counters explicitly, while uncore files reference units such as CBOX, HA, PCU, UBOX, R2PCIe, and iMC.

## State and Persistence
The file is static architecture metadata. Runtime state appears only when perf opens events and the kernel PMU driver allocates real counters. Persistence risk is that these counts become the assumed hardware contract for Broadwell-DE event scheduling.

## Dependencies and Integration
This file integrates all sibling Broadwell-DE event JSON files with perf's counter scheduler. It is especially important for groups and metrics that attempt to collect multiple events simultaneously, since the 4 generic core counters and smaller 2-counter IRP/UBOX units bound what can be measured without multiplexing.

## Risks
Incorrect counter counts cause misleading schedulability decisions, excessive multiplexing, or event-open failures. The file does not encode all event-specific counter restrictions, so it must be interpreted with each event's `Counter` field and metric constraints.

## Test Signals
Validation signals are `jq empty`, schema checks for all expected units, and perf event group tests that intentionally approach the core and uncore counter limits. Counter scheduling should be checked for both raw event groups and derived metric groups with constrained metrics.
