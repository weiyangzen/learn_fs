<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/cache.json

## Purpose
Defines 125 Emerald Rapids core cache PMU aliases. Coverage includes core snoop responses, L1D pending and hardware-prefetch misses, L2 request/line/transaction behavior, LLC and L3 hit/miss retired-load classifications, memory instruction retirement, offcore requests and outstanding cycles, software prefetches, store queue behavior, and offcore-response filters.

## Important APIs, Types, And Functions
The schema uses `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `Counter`, `CounterMask`, `EdgeDetect`, `MSRIndex`, `MSRValue`, `Data_LA`, and `Deprecated`. Thirty-eight entries are `OCR.*` offcore-response aliases with MSR filters. Twenty-four entries carry `Data_LA`. Six entries use `CounterMask`, and one uses edge detection.

## Control Flow
`jevents.py` reads the file when generating x86 PMU tables, and `arch/x86/mapfile.csv` selects the `emeraldrapids` directory for `GenuineIntel-6-CF`. At runtime perf exposes names such as `CORE_SNOOP_RESPONSE.*`, `L2_RQSTS.*`, `MEM_LOAD_L3_HIT_RETIRED.*`, `OFFCORE_REQUESTS.*`, and `OCR.*`; perf programs event selectors and, for OCR aliases, the required offcore MSR filters.

## State And Persistence
The JSON is static repository data. Generated perf tables persist in the binary. Runtime state is PMU counter configuration, offcore MSR filter state, and optional sampled address records for events whose generated descriptions indicate data-address support.

## Dependencies And Integration Points
Depends on the Emerald Rapids mapfile entry, the x86 PMU JSON parser, and perf support for offcore response filters. It complements Emerald Rapids uncore files in the same directory, while this file itself describes only core PMU cache aliases. `counter.json` advertises the core PMU has eight generic counters, which affects feasible grouping of these events.

## Risks And Edge Cases
Emerald Rapids has broader PMU capacity and server uncore context, so confusing core events with uncore events can lead to wrong PMU selection. OCR MSR values are high-risk data because a bad bitmask silently changes the measured memory source. Two entries are deprecated. Counter masks and edge detection change counting semantics and require accurate conversion by `jevents.py`.

## Test Signals
Validate with `jq empty`, build perf with jevents, and inspect `perf list` for representative `L2_RQSTS`, `MEM_LOAD_RETIRED`, `OFFCORE_REQUESTS`, and `OCR` aliases. On Emerald Rapids hardware, run event groups that combine cache aliases with offcore aliases and confirm perf either schedules them or reports clear constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/cache.json -->
