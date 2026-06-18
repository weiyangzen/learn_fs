## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/cache.json

**Purpose:** Goldmont Plus cache and memory-hierarchy topic with 101 records. It covers L1 dirty replacements, instruction-cache fill stalls, L2 references/misses/rejects, load hit-source retirement events, memory uop mix, split/locked accesses, and a large set of `OFFCORE_RESPONSE.*` aliases for request/response combinations.

**Schema and important records:** Standard event records use `EventName`, `EventCode`, `UMask`, `Counter`, descriptions, `SampleAfterValue`, and optional `PEBS`/`Data_LA`. Offcore response records also use `MSRIndex` and `MSRValue`; `jevents.py` maps MSR index `0x1A6`/`0x1A7` to the `offcore_rsp=` event field. The base `OFFCORE_RESPONSE` entry documents the need for MSR programming, while derived records encode request classes such as demand data read, RFO, code read, prefetches, streaming stores, writebacks, and bus locks with response classes such as L2 hit, HITM other core, true L2 miss, and outstanding cycles.

**Control flow and integration:** During build, `jevents.py` emits these as Goldmont Plus `pmu_event` entries. At runtime, aliases that include `MSRValue` cause perf to program the offcore response MSR selector in addition to the core event code. The load-retired and memory-uop aliases also support precise sampling where PEBS/data-address metadata is present.

**State and persistence:** Static catalog only; hardware counter state is session-scoped. Offcore aliases persist selector values in generated event strings, so the JSON is the durable source of request/response programming semantics.

**Dependencies:** Depends on Intel Goldmont Plus offcore response encodings, perf's MSR mapping in `jevents.py`, and PMU counter availability from `counter.json`. Metrics and user workflows depend on stable names like `MEM_LOAD_UOPS_RETIRED.L1_HIT`, `LONGEST_LAT_CACHE.MISS`, and `OFFCORE_RESPONSE.DEMAND_DATA_RD.OUTSTANDING`.

**Risks:** Offcore response aliases are especially fragile: bad `MSRValue` values can produce valid-looking but semantically wrong counts. Duplicate descriptions for the two offcore MSRs must remain intentional. PEBS `Data_LA` handling is required for load-source attribution.

**Test signals:** `jq` schema checks; perf jevents generation; `perf list` should show cache topic aliases. Runtime smoke tests should include a simple load benchmark with `MEM_LOAD_UOPS_RETIRED.L1_HIT,L2_MISS` and one offcore alias to ensure MSR programming succeeds.
