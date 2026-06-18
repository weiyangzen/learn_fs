# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/cache.json

## Purpose
`cache.json` is a declarative Sapphire Rapids core PMU event catalog for cache, memory-source, offcore, snoop, prefetch, and selected store-queue behavior. It contains 132 event objects consumed by perf's PMU event tooling, not executable code. The file lets users name events such as `L2_RQSTS.DEMAND_DATA_RD_MISS`, `MEM_LOAD_RETIRED.L3_MISS`, `OCR.READS_TO_CORE.REMOTE`, and `OFFCORE_REQUESTS_OUTSTANDING.DEMAND_DATA_RD` instead of spelling raw event select, umask, MSR filter, counter, and sampling attributes.

## Important APIs, types, and schema fields
The effective API is the JSON event schema used by `tools/perf/pmu-events/jevents.py` and exposed through `perf list` / event parsing. Common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. This file also uses `CounterMask`, `EdgeDetect`, `Deprecated`, `MSRIndex`, `MSRValue`, and `Data_LA`. `MSRIndex`/`MSRValue` are central for `OCR.*` offcore response filters using `0x1a6,0x1a7`; `Data_LA` marks data linear-address capable load/store events; `Deprecated` preserves aliases while steering users to replacement names.

## Control flow and integration
At build time perf's PMU event generator parses this JSON with the rest of the Sapphire Rapids model directory and emits compiled C tables. At runtime `perf list` prints the names/descriptions, and `perf stat`/`perf record` resolve names into raw encodings plus optional offcore MSR programming. There is no in-file execution order; dependencies are by schema and by event-family naming. Offcore response events are a two-part programming contract: `EventCode` `0x2A,0x2B` and `UMask` `0x1` select OCR counting while `MSRValue` chooses demand code/data/RFO, hardware prefetch, streaming write, local/remote DRAM, PMM, cache, snoop, and SNC response filters.

## State and persistence behavior
The file is static source data checked into the perf tree. It persists hardware encodings, descriptions, aliases, and sampling defaults. Runtime counter state lives in CPU PMU registers and offcore MSRs, not in this JSON. Any edit changes generated perf event tables and can affect user-visible event names, raw event encodings, PEBS/address-sampling affordances, and default sampling periods.

## Dependencies
This file depends on the Sapphire Rapids core PMU programming model, perf's JSON event schema, and `counter.json` for available core generic/fixed counter capacity. It integrates with sibling event groups (`memory.json`, `pipeline.json`, `frontend.json`, `floating-point.json`, `other.json`) and model mapping files that cause Sapphire Rapids CPUs to select this directory. Many event families are tied to Intel-specific facilities: offcore response MSRs, PEBS data source/load address sampling, SNC topology, and PMM naming.

## Notable event coverage
Major families are `OCR` (43 entries), `L2_RQSTS` (17), `OFFCORE_REQUESTS_OUTSTANDING` (8), `MEM_INST_RETIRED` (8), `MEM_LOAD_RETIRED` (8), `CORE_SNOOP_RESPONSE` (7), `L1D_PEND_MISS` (6), `SW_PREFETCH_ACCESS` (5), and smaller L1/L2/LLC and store-queue groups. There are aliases such as `L2_REQUEST.ALL` for `L2_RQSTS.REFERENCES` and `L2_REQUEST.MISS` for `L2_RQSTS.MISS`. `L1D_PEND_MISS.L2_STALL` and `OFFCORE_REQUESTS_OUTSTANDING.ALL_DATA_RD` are deprecated compatibility names.

## Risks and edge cases
Offcore events are high risk because incorrect `MSRValue` filters silently produce plausible but wrong locality, snoop, PMM, or SNC counts. Aliases and deprecations must remain consistent so scripts using older names continue to work while users can discover replacement names. Counter constraints matter: most events use core counters `0,1,2,3`, while load-retired PEBS style events also carry `Data_LA`; invalid counter masks or address-sampling tags can break `perf record` use cases. Descriptions contain hardware-specific semantics such as "true miss", "SNC", and "single snoop response counts on all hyperthreads"; these are part of the user contract and should not be simplified casually.

## Test signals
Useful validation is `jq empty cache.json`, `tools/perf/pmu-events/jevents.py` generation, `perf test` coverage for PMU event parsing, and `perf list` on a build that includes the Sapphire Rapids map. Spot checks should verify representative raw encodings for `L2_RQSTS.*`, deprecated replacement names, `Data_LA` events, and OCR MSR filters. Hardware validation on Sapphire Rapids should compare `perf stat -e` counts against known cache/memory microbenchmarks for local DRAM, remote DRAM, L2 hits/misses, and snoop-heavy sharing.
