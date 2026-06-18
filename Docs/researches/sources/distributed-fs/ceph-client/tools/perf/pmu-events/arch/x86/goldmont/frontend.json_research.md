# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/frontend.json

## Purpose

`frontend.json` defines 8 Goldmont front-end PMU events for branch-address clears, predecode length prediction problems, instruction-cache line access/hit/miss accounting, and microcode sequencer entries. It supports diagnosis of instruction delivery and front-end speculation issues.

## Important APIs, Types, and Data Fields

Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Event groups are `BACLEARS.ALL`, `BACLEARS.COND`, `BACLEARS.RETURN`, `DECODE_RESTRICTION.PREDECODE_WRONG`, `ICACHE.ACCESSES`, `ICACHE.HIT`, `ICACHE.MISSES`, and `MS_DECODED.MS_ENTRY`.

The `ICACHE.*` descriptions explicitly warn that Goldmont counts instruction-cache line references differently from Intel processors based on Silvermont microarchitecture. `MS_DECODED.MS_ENTRY` counts starts of microcode sequencer flows rather than every uop read from MSROM.

## Control Flow and Data Flow

There is no executable flow. Perf loads the aliases and programs core PMU counters. Runtime data flows from branch prediction, predecode, I-cache, and microcode-sequencer hardware into perf counts. The branch-address clear rows split total BACLEARs into conditional and return subcategories.

## State and Persistence Behavior

The file persists static event metadata and default sample periods only. Runtime counts are per-core and session-local. Speculative front-end activity can be counted before later machine clears or branch recovery, especially for microcode sequencer starts.

## Dependencies and Integration Points

These definitions depend on Goldmont front-end PMU encodings and integrate with perf front-end analysis, branch prediction studies, instruction-cache locality tuning, and microcoded-instruction diagnosis. They complement `cache.json`, which has `FETCH_STALL.ICACHE_FILL_PENDING_CYCLES`, and `other.json`, which has broader fetch-stall and ITLB-related stall counters.

## Risks and Edge Cases

The I-cache accounting model is Goldmont-specific and should not be compared blindly to Silvermont or larger-core Intel CPUs. `MS_DECODED.MS_ENTRY` is not a retired-uop count and may include speculative flows. BACLEAR subevents may overlap conceptually with broader branch-misprediction metrics outside this file, so ratios need careful denominators.

## Test Signals

Validation should include JSON parsing, perf list exposure, and front-end workload tests. Large instruction-footprint workloads should increase I-cache misses. Branch-heavy tests should affect BACLEAR rows. Workloads with microcoded instructions or fault/assist paths should affect `MS_DECODED.MS_ENTRY`. Tests should compare `ICACHE.ACCESSES`, `ICACHE.HIT`, and `ICACHE.MISSES` for plausible relationships without assuming exact additive behavior across architectures.
