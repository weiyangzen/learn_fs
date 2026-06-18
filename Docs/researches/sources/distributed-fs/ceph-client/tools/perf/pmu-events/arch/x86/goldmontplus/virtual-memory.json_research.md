## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/virtual-memory.json

**Purpose:** Goldmont Plus virtual-memory topic with 18 events for detailed DTLB/ITLB walk completion by page size, walk-pending cycles, EPT walk pending, retired DTLB-miss memory uops, and STLB flushes.

**Schema and important records:** Standard event schema with optional `PEBS` and `Data_LA`. Event families include `DTLB_LOAD_MISSES.WALK_COMPLETED_4K/2M_4M/1GB`, matching store-side events, `ITLB_MISSES.WALK_COMPLETED_*`, `*.WALK_PENDING`, `EPT.WALK_PENDING`, `MEM_UOPS_RETIRED.DTLB_MISS*`, `ITLB.MISS`, and `TLB_FLUSHES.STLB_ANY`.

**Control flow and integration:** Build-time conversion is standard. Runtime users get aliases grouped under virtual-memory; precise data-address metadata supports locating retired memory uops that missed the DTLB.

**State and persistence:** Static metadata only. PMU counters store per-session counts; the JSON persists page-size-specific selector semantics.

**Dependencies:** Depends on Goldmont Plus translation PMU encodings. Integrates with frontend fetch-stall/ITLB events, pipeline `LD_BLOCKS.UTLB_MISS`, and memory page-split events.

**Risks:** Page-size suffixes are semantically important; swapping `4K`, `2M_4M`, and `1GB` masks changes in huge-page behavior. `WALK_PENDING` cycle events are not equivalent to completed-walk events, so metrics must use the right family.

**Test signals:** `jq` validation and jevents build. On target hardware, `perf list | rg 'DTLB_LOAD_MISSES|ITLB_MISSES|TLB_FLUSHES'`; huge-page and small-page microbenchmarks can exercise page-size-specific aliases.
