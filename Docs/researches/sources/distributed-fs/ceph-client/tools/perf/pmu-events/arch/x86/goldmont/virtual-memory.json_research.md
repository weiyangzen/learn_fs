## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/virtual-memory.json

**Purpose:** Goldmont virtual-memory topic with seven PMU events for ITLB misses, retired memory uops that missed the DTLB, and page-walk cycle accounting. It exposes translation-related performance aliases used to distinguish instruction-side misses, data-side misses, and page-walk duration.

**Schema and important records:** Records use the event schema fields `EventName`, `EventCode`, `UMask`, descriptions, `Counter`, `SampleAfterValue`, and optional `PEBS`/`Data_LA`. `MEM_UOPS_RETIRED.DTLB_MISS_LOADS` and `MEM_UOPS_RETIRED.DTLB_MISS_STORES` are precise/data-address capable retirement events; `PAGE_WALKS.CYCLES`, `PAGE_WALKS.D_SIDE_CYCLES`, and `PAGE_WALKS.I_SIDE_CYCLES` count cycles with page walks in progress.

**Control flow and integration:** `jevents.py` tags these records with the `virtual-memory` topic and emits them into Goldmont's PMU event table. Runtime perf consumers can discover them with `perf list virtual-memory` and program them through the generated alias metadata.

**State and persistence:** The only persisted state is static event metadata compiled into perf. Counter accumulation occurs in hardware PMU counters during a perf session; the JSON itself has no persistence or control logic.

**Dependencies:** Depends on perf's `pmu_event` JSON conversion and Goldmont PMU encoding. It is conceptually linked to pipeline load-blocking events such as `LD_BLOCKS.UTLB_MISS` and to any metrics that divide TLB misses by retired instructions.

**Risks:** The file mixes speculative ITLB fill accounting with retired DTLB miss events, so descriptions must stay precise or users may compare non-equivalent counts. PEBS/data linear address flags are important for address attribution and should not be dropped during schema changes.

**Test signals:** `jq empty` confirms structural validity; perf jevents build confirms schema acceptance. On target hardware, `perf list | rg -i 'dtlb|itlb|page_walk'` and targeted `perf stat -e ITLB.MISS,PAGE_WALKS.CYCLES` can verify aliases resolve.
