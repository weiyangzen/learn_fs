# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/cache.json

Purpose: Defines 118 Ivy Town core PMU aliases for data cache, L2, LLC, load-source, offcore request/response, split-lock, and memory-ordering-adjacent cache behavior. This is a central dependency for Ivy Town topdown and memory metrics.

Important APIs/types/functions: Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `AnyThread`, `PEBS`, `MSRIndex`, `MSRValue`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Families include `L1D`, `L1D_PEND_MISS`, `L2_RQSTS`, `L2_TRANS`, `L2_LINES_IN`, `L2_LINES_OUT`, `LONGEST_LAT_CACHE`, `MEM_LOAD_UOPS_RETIRED`, `MEM_LOAD_UOPS_LLC_HIT_RETIRED`, `MEM_LOAD_UOPS_LLC_MISS_RETIRED`, `MEM_UOPS_RETIRED`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `OFFCORE_REQUESTS_BUFFER`, `OFFCORE_RESPONSE`, and `SQ_MISC`.

Control flow: Perf's build tooling converts this JSON array into Ivy Town event aliases. Runtime alias lookup translates names into core PMU encodings. Offcore-response aliases are special: they share event select values such as `0xB7, 0xBB` and require offcore MSR filter programming through `MSRIndex`/`MSRValue` or equivalent generated metadata. PEBS-tagged load events can be used for precise sampling and data-source analysis.

State and persistence: Static metadata persists event names and raw encodings. Runtime state is in core PMU counters, offcore response MSRs, and PEBS records. There is no file-local mutable state.

Dependencies/integration: Depends on Ivy Town PMU/offcore response definitions and perf support for MSR filters. `ivt-metrics.json` references many aliases from this file, including `MEM_LOAD_UOPS_RETIRED.*`, LLC hit/miss retired events, `OFFCORE_REQUESTS_OUTSTANDING.*`, `L1D_PEND_MISS.*`, `L2_LINES_IN.ALL`, and `LONGEST_LAT_CACHE.MISS`.

Risks: Offcore-response descriptions and filters are easy to mismatch because many entries share visible event/umask fields while differing in hidden MSR filters. Some aliases require specific counters or PEBS support, affecting scheduling and sampling availability. Long derived metrics divide by combinations of these events, so missing or renamed aliases can break topdown formulas. Similar hit/miss wording should be audited; a few descriptions in this PMU family historically contain copy/paste mistakes.

Test signals: Validate JSON uniqueness and required offcore MSR fields, run perf PMU event tests for ordinary cache and offcore aliases, and verify topdown metric parsing resolves every referenced cache event. Hardware smoke tests should compare L1/L2/LLC miss counters under cache-thrashing workloads and exercise at least one precise load event.
