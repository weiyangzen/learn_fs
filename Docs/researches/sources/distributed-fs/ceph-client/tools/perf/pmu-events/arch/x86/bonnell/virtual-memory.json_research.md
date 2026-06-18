# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/virtual-memory.json

## Purpose

This file defines 15 Bonnell virtual-memory events. It covers data TLB misses for loads and stores, L0 DTLB misses, ITLB hits/misses/flushes, retired load DTLB misses, and page-walk cycles or walk counts for data side, instruction side, or combined paths.

## Important APIs, Types, And Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `PEBS`, and `BriefDescription`. Families include `DATA_TLB_MISSES`, `ITLB`, `MEM_LOAD_RETIRED`, and `PAGE_WALKS`. `ITLB.MISSES` and `MEM_LOAD_RETIRED.DTLB_MISS` include PEBS metadata.

## Control Flow

The build path converts each event into generated Bonnell perf aliases. Event and mask fields become perf config strings, sampling periods become generated default periods, and PEBS-capable entries gain precise-event description text. Runtime perf uses the generated aliases to program TLB and page-walk counters.

## State And Persistence Behavior

The JSON stores static event metadata. TLB contents, misses, and page walks are runtime hardware state. PEBS capability and default sampling periods persist through generated tables but do not allocate buffers or samples by themselves.

## Dependencies And Integration Points

This file depends on Bonnell x86 model mapping, `jevents.py`, generated PMU tables, perf alias lookup, and PMU tests. It integrates with memory-translation diagnosis, page-size analysis, and instruction-fetch miss investigation on Bonnell systems.

## Risks And Edge Cases

`PAGE_WALKS` contains both cycle-duration and number-of-walk events with overlapping event codes and masks, so descriptions are essential. Load/store DTLB aliases can be confused with retired load-only PEBS events. ITLB hit/miss/flush counts may not compose cleanly into ratios if flushes or speculation intervene.

## Test Signals

Validate JSON and generated aliases. Runtime tests can use pointer-chasing, store-heavy TLB stress, instruction-footprint stress, and page-size changes. Generated entries should preserve PEBS metadata for `ITLB.MISSES` and `MEM_LOAD_RETIRED.DTLB_MISS`.
