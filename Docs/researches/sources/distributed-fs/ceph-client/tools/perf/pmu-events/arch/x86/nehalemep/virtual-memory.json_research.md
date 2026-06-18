# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/virtual-memory.json

## Purpose
This file defines 14 Nehalem EP virtual-memory PMU aliases for data and instruction TLB behavior. It covers first-level DTLB misses, second-level TLB hits, completed page walks, ITLB flushes, ITLB misses, large ITLB hits, and precise retired load/store/instruction events that missed translation structures. It is byte-identical to the Nehalem EX `virtual-memory.json`, preserving shared event semantics under the EP source path.

## Important APIs, Types, And Fields
The schema is the perf PMU event JSON array. Objects use `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `SampleAfterValue`, and optional `PEBS`. Representative families are `DTLB_LOAD_MISSES`, `DTLB_MISSES`, `ITLB_MISSES`, `ITLB_MISS_RETIRED`, `LARGE_ITLB`, `MEM_LOAD_RETIRED.DTLB_MISS`, and `MEM_STORE_RETIRED.DTLB_MISS`. Most aliases can use counters `0,1,2,3`, and precise retired translation misses use `PEBS: 1`.

## Control Flow
The file has no executable flow. During perf builds, `jevents.py` loads the JSON for the selected x86 model directory, converts the aliases into generated C tables, and the perf frontend later resolves user-facing names into raw event selectors. At runtime, the hardware PMU performs counting; the JSON only controls how perf programs the event code and unit mask.

## State And Persistence
The persisted state is the event catalog. There is no mutable state, persistence layer, or runtime cache in the file itself. Its contents become static generated data in `pmu-events.c`. `SampleAfterValue` uses `2000000`, which affects the default sampling period exposed for these aliases.

## Dependencies And Integration Points
The file depends on Nehalem EP PMU definitions and the perf `pmu-events` schema. It integrates with model selection through the x86 mapfile, with alias display through `perf list`, and with event parsing for `perf stat`/`perf record`. The precise retired DTLB/ITLB events integrate with PEBS-capable sampling paths, while non-precise walk/miss aliases use generic counters.

## Risks
Translation events are often used for memory-latency diagnosis, so event-code or `UMask` mistakes can mislead performance investigations. The small table reduces maintenance surface, but the EP/EX duplication means fixes must be kept synchronized unless a real model difference is discovered. The `MEM_STORE_RETIRED.DTLB_MISS` event uses event code `0xC` while load-retired DTLB miss uses `0xCB`; these asymmetric encodings are easy to accidentally normalize.

## Test Signals
Validate JSON syntax and generated `pmu-events.c`. Use `perf list` on a mapped Nehalem EP build to verify all 14 aliases are present. Functional smoke tests should include at least one generic walk event and one PEBS retired miss event so both plain and precise paths are covered.
