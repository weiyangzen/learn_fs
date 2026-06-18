<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/counter.json

## Purpose
Declares the Elkhart Lake PMU counter inventory for perf's event table metadata. It contains one `core` unit entry with three fixed counters and four generic programmable counters.

## Important APIs, Types, And Functions
The schema fields are `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. `Unit: core` ties the counts to the CPU core PMU, while the counter counts inform perf and generated PMU metadata about scheduling capacity for simultaneous events.

## Control Flow
`jevents.py` processes this JSON alongside the other Elkhart Lake PMU files when generating architecture event tables. The table is selected through `arch/x86/mapfile.csv` for the Elkhart Lake CPUID pattern. Runtime perf uses the resulting metadata when presenting PMU capabilities and when planning event groups against available counters.

## State And Persistence
No mutable state is stored here. The values persist in the generated perf PMU table and describe hardware resources that remain fixed for the model.

## Dependencies And Integration Points
Integrates with the x86 PMU event generator and perf's event scheduling model. It must match the actual Elkhart Lake core PMU layout and stay consistent with event files that specify `Counter` constraints such as `0,1,2,3`.

## Risks And Edge Cases
Incorrect generic or fixed counter counts can cause perf to accept impossible event groups or reject valid ones. Because this file has only one object, JSON validity and exact field spelling are the main ingestion risks.

## Test Signals
Validate with `jq empty`, build the generated pmu-events table, and compare `perf list`/PMU capability output on Elkhart Lake hardware. Event group tests with more than four generic core events should reveal whether scheduling constraints are represented correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/counter.json -->
