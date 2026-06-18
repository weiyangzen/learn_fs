# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/counter.json

## Purpose
This JSON file declares Jake Town PMU counter inventory metadata for perf. Unlike event tables, it does not define event aliases; it tells perf how many fixed and generic counters exist for each core and uncore PMU unit. The listed units are `core`, `CBOX`, `PCU`, `UBOX`, `QPI`, `R3QPI`, `R2PCIe`, `HA`, `iMC`, and `IRP`.

## Important APIs, Types, And Functions
The schema contains `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. There are 10 entries. The `core` unit has three fixed counters and four generic counters. Most uncore units have zero fixed counters and four generic counters, with `UBOX` and `IRP` providing two generic counters and `R3QPI` providing three. There are no `EventName`, `EventCode`, `UMask`, metric, or description fields because this file models capacity rather than events.

## Control Flow
There is no runtime control flow in the JSON. Perf's event metadata tooling reads this inventory alongside Jake Town event tables and uses it to understand PMU scheduling capacity, display metadata, or validate event placement. User-selected events from other files are constrained by both their per-event `Counter` fields and the unit-wide counter counts declared here.

## State And Persistence
The file persists static hardware inventory. It does not store current counter allocations, multiplexing state, or active perf sessions. At runtime, perf and the kernel allocate counters according to hardware availability, event constraints, pinned/exclusive requests, and multiplexing policy. This file simply records the baseline counter counts for Jake Town units.

## Dependencies And Integration Points
This file integrates with the Jake Town perf PMU metadata set. It complements `cache.json`, uncore unit event files, and metrics by declaring available counter resources. It depends on perf's parser recognizing the counter-inventory schema and on unit names matching the units used by event descriptors, such as `PCU`, `R2PCIe`, and `iMC`.

## Risks And Edge Cases
Incorrect counts can cause perf to overestimate or underestimate schedulable events. Unit-name mismatches are risky because they can disconnect inventory from event tables. The file is concise, but it represents multiple PMU blocks with different capacities, so copying a default count across all units would be wrong for `UBOX`, `IRP`, and `R3QPI`. Platform steppings or disabled units may still make runtime availability differ from this static metadata.

## Test Signals
Test signals include JSON syntax validation, parser acceptance of entries without `EventName`, and consistency checks that unit names align with Jake Town event files. Runtime validation can compare perf's event scheduling and multiplexing behavior against expected counter capacity, especially for UBOX, IRP, and R3QPI units with fewer than four generic counters.
