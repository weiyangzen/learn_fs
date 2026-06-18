# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/counter.json

## Purpose
This file is the Nehalem EX PMU counter inventory. It does not define event aliases; it declares the core PMU unit and the number of fixed and generic counters available to perf metadata consumers.

## Important APIs, Types, And Fields
The array contains a single object: `Unit: core`, `CountersNumFixed: 4`, and `CountersNumGeneric: 4`. Unlike the event tables, it has no `EventName`, `EventCode`, `UMask`, or descriptions. Its schema role is capacity metadata rather than alias metadata.

## Control Flow
There is no executable control flow. Build-time parsing treats this as an input to the same `pmu-events` data pipeline, allowing generated metadata to represent the PMU's counter resources for the `nehalemex` model.

## State And Persistence
The file persists static counter-count data. It does not store runtime counter state and does not change with workload execution. Generated perf tables may embed this metadata so user-facing tooling understands the available fixed and programmable counters.

## Dependencies And Integration Points
It depends on the perf JSON parser accepting counter metadata objects in architecture model directories. It integrates with `jevents.py`, generated `pmu-events.c`, and perf code that reports or reasons about PMU counter capabilities. It should remain consistent with fixed-counter aliases in the neighboring event files, such as fixed counter 1 for instructions retired and fixed counters 2/3 for unhalted/thread reference cycles.

## Risks
The file is tiny, but a wrong count has broad scheduling implications: perf may overstate or understate the number of simultaneously usable counters. The `CountersNumFixed: 4` value must be reconciled with any fixed aliases exposed elsewhere for this model. Because this object lacks `EventName`, tooling that assumes every JSON object is an event can fail or misclassify the file.

## Test Signals
Run `jq` validation and the perf `pmu-events` generator. Tests should include the generation path for model metadata, not only event aliases. A useful review check is to compare fixed-counter alias usage in `pipeline.json` against the declared fixed counter count here.
