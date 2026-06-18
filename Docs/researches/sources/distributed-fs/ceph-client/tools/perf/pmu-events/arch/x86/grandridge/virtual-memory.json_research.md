<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/virtual-memory.json

## Purpose
This JSON file defines Grand Ridge core virtual-memory PMU events for perf. The complete 148-line file was read, containing 17 records. It exposes DTLB load misses, DTLB store misses, ITLB misses, and a load-head DTLB miss retirement signal.

## Important APIs, Types, and Functions
The records use core event fields `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and optional `PublicDescription`. Unlike the uncore files, these records have no `Unit`, so `jevents.py` treats them as core PMU events. Event families are `DTLB_LOAD_MISSES` (5), `DTLB_STORE_MISSES` (5), `ITLB_MISSES` (6), and `LD_HEAD` (1). All records specify counters `0,1,2,3,4,5,6,7` and include `SampleAfterValue`; load events use period-like values such as `200003`, while store and instruction walk events use larger defaults such as `2000003`.

## Control Flow, State, and Persistence
The file is declarative build input. `jevents.py` converts `EventCode` and `UMask` into core PMU config terms and maps `SampleAfterValue` to generated `period=` metadata. Perf then exposes aliases for TLB walk completion, page-size-specific walks, STLB hits, walk-pending cycles, and retirement-time DTLB-miss detection. The file has no mutable state; generated perf tables are the persistent derivative.

## Dependencies and Integration Points
It depends on perf's x86 core PMU event support and Grand Ridge model mapping. It integrates with `perf stat`, `perf record`, and event sampling defaults through `SampleAfterValue`. These events are useful for diagnosing page-table walk costs, STLB behavior, huge-page effects, and virtualization/EPT overhead called out in the walk-pending descriptions.

## Risks and Test Signals
The key risk is semantic precision around page sizes and walk states: `WALK_COMPLETED`, `WALK_COMPLETED_4K`, and `WALK_COMPLETED_2M_4M` share event codes with different masks, so mask accuracy determines whether derived analysis is valid. Sampling defaults are part of the generated alias and should not be accidentally dropped. Test signals include JSON validation, generated event strings with `period=` and `umask=`, `perf list` visibility, and workload smoke tests comparing TLB miss counters under 4K pages versus huge pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/virtual-memory.json -->
