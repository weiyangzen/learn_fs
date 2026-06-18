# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/virtual-memory.json

Purpose: declares 22 Westmere EX virtual-memory and TLB PMU events for perf. It covers DTLB load misses, general DTLB misses, ITLB misses and flushes, EPT walk cycles, large ITLB hits, and retired load/store DTLB misses.

Important APIs/types/functions: rows use `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`; three retired DTLB miss rows carry `PEBS: "1"`. Families include `DTLB_LOAD_MISSES`, `DTLB_MISSES`, `ITLB_MISSES`, `EPT`, `ITLB_FLUSH`, `ITLB_MISS_RETIRED`, `LARGE_ITLB`, `MEM_LOAD_RETIRED`, and `MEM_STORE_RETIRED`. All rows allow generic counters `0,1,2,3`.

Control flow: declarative only. The perf PMU event generator ingests the rows, and runtime perf maps symbolic aliases to event code/unit-mask programming. PEBS-capable retired memory rows can be used for precise sampling of DTLB-miss-causing memory operations.

State and persistence: static metadata. Runtime PMU state is temporary and bound to active perf measurements.

Dependencies: depends on Westmere EX DTLB/ITLB/EPT event encodings and perf's JSON schema. It complements memory locality rows in `memory.json` and cache-source rows in `cache.json`.

Integration points: exposed to `perf list`, `perf stat`, and `perf record` for virtual-memory performance diagnosis. These aliases help separate page-walk count, page-walk cycles, STLB hits, large-page walks, instruction-side misses, and retired load/store DTLB misses.

Risks: DTLB family names are similar and easy to confuse (`DTLB_LOAD_MISSES` versus `DTLB_MISSES`). PEBS markings on retired load/store misses should not be copied to non-retired walk events. Incorrect `UMask` values can conflate STLB hits, walks, PDE misses, and large page walks.

Test signals: JSON parse; 22 unique event names; all counters `0,1,2,3`; PEBS only on the intended retired miss rows; generated perf event tables include representative aliases such as `DTLB_LOAD_MISSES.WALK_CYCLES`, `ITLB_MISSES.WALK_COMPLETED`, and `MEM_STORE_RETIRED.DTLB_MISS`.
