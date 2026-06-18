<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/counter.json

## Purpose
This JSON file defines Granite Rapids PMU counter inventory metadata for perf. The complete 81-line file was read, containing 16 records. It does not define countable events; instead, it tells perf/generator consumers how many fixed and generic counters exist for the core and uncore units.

## Important APIs, Types, and Functions
The schema fields are `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. Units listed are `core`, `B2CMI`, `CHA`, `IMC`, `CXLCM`, `CXLDP`, `B2HOT`, `IIO`, `IRP`, `MDF`, `PCU`, `UBOX`, `UPI`, `B2UPI`, `B2CXL`, and `CHACMS`. The `core` unit has 4 fixed and 8 generic counters. Most uncore units have 0 fixed and 4 generic counters; `PCU` has 0 fixed and 6 generic counters. Some generic counts are JSON numbers and some are strings, so downstream parsing must tolerate both representations.

## Control Flow, State, and Persistence
This file is declarative metadata. It has no `EventName`, `EventCode`, or masks, so it is not an event alias table. The build pipeline reads it as part of the Granite Rapids PMU event directory so generated perf metadata can reflect counter capacity by PMU unit. There is no runtime mutation or persisted state beyond the checked-in JSON and generated tables.

## Dependencies and Integration Points
It depends on perf tooling that recognizes counter metadata records alongside event records. It integrates with Granite Rapids core and uncore event files by describing how many events can be scheduled simultaneously on each PMU unit. This matters for perf event grouping, multiplexing expectations, and validation of large event sets spanning core, CHA, IMC, IIO, CXL, UPI, and PCU units.

## Risks and Test Signals
The main risk is metadata drift relative to kernel PMU capabilities or hardware revisions. A wrong counter count can mislead scheduling decisions or user expectations about multiplexing. Mixed numeric/string JSON values for `CountersNumGeneric` are a compatibility risk if a stricter parser assumes one type. Test signals include JSON validation, successful `jevents.py` processing, generated metadata inspection, comparison with kernel-exposed PMU counter counts under `/sys/bus/event_source/devices`, and grouped `perf stat` tests that verify expected scheduling behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/counter.json -->
