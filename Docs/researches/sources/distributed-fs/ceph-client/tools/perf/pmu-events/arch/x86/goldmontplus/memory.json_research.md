## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/memory.json

**Purpose:** Goldmont Plus memory topic with three aliases for memory-ordering machine clears and misaligned memory references that split pages. It targets correctness/replay costs rather than cache hit-source counting.

**Schema and important records:** Standard event fields plus PEBS where available. `MACHINE_CLEARS.MEMORY_ORDERING` records machine clears due to memory ordering conflicts. `MISALIGN_MEM_REF.LOAD_PAGE_SPLIT` and `.STORE_PAGE_SPLIT` count load/store references spanning page boundaries.

**Control flow and integration:** Build-time event conversion is standard `JsonEvent` processing. Runtime perf users can collect these aliases directly or combine them with load-blocking and machine-clear events from `pipeline.json`.

**State and persistence:** Static PMU metadata only. Hardware counters hold transient session state.

**Dependencies:** Depends on the same counter inventory as other Goldmont Plus core events. Semantic integration is strongest with `MACHINE_CLEARS.*`, `LD_BLOCKS.*`, and split cache-line events from `cache.json`.

**Risks:** Misalignment events are narrow and may be confused with cache-line split events; documentation must preserve page-split wording. Machine-clear categories can overlap in analysis, so event names and descriptions must remain distinct.

**Test signals:** `jq` validation and perf build. Runtime microbenchmarks with deliberately page-split accesses can check that load/store page-split aliases resolve and produce nonzero counts.
