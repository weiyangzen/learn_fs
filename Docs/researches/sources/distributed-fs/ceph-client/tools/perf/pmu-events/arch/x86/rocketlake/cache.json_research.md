# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/cache.json

## Purpose

`cache.json` is Rocket Lake's perf PMU event catalog for cache hierarchy, retired memory operations, L1/L2 behavior, offcore response filtering, snoop outcomes, and software or hardware prefetch behavior. It contains 109 event rows and is the primary Rocket Lake source for cache-hit, cache-miss, L2 request, offcore response, and address-capable retired-load diagnostics.

## Important APIs, Types, and Data Fields

The JSON event objects use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and often `PublicDescription`. Optional fields include `CounterMask`, `EdgeDetect`, `MSRIndex`, `MSRValue`, and `Data_LA`. There is no explicit `Unit`, so perf treats these as core PMU events for the Rocket Lake model.

Major families are `L1D`, `L1D_PEND_MISS`, `L2_LINES_IN`, `L2_LINES_OUT`, `L2_RQSTS`, `L2_TRANS`, `LONGEST_LAT_CACHE`, `MEM_INST_RETIRED`, `MEM_LOAD_L3_HIT_RETIRED`, `MEM_LOAD_MISC_RETIRED`, `MEM_LOAD_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `SQ_MISC`, and `SW_PREFETCH_ACCESS`. Forty-five `OCR.*` rows use offcore response MSRs `0x1a6,0x1a7` with detailed `MSRValue` filters. Twenty retired memory/load rows have `Data_LA: 1`, meaning perf appends address-support wording for precise address sampling when used appropriately.

## Control Flow and Data Flow

There is no local control flow. `jevents.py` parses each row, converts event and umask fields into generated C metadata, lowercases aliases for lookup, and preserves MSR and data-address fields. At runtime, normal L1/L2 rows program core counters directly. `OCR.*` rows additionally program offcore response filter MSRs to count selected request and response combinations, such as demand code reads, demand data reads, RFOs, prefetches, L3 hits, snoop hitm, snoop miss, and any-response cases.

The analysis flow spans the cache hierarchy. `L1D_PEND_MISS` shows fill-buffer pressure and pending cycles. `L2_RQSTS` and `L2_LINES_*` show L2 access, fill, and eviction behavior. `MEM_LOAD_RETIRED` and `MEM_INST_RETIRED` identify retired memory operations and where loads were satisfied. `OCR` rows provide offcore response classification after requests leave the core.

## State and Persistence Behavior

The file persists only static PMU metadata. Runtime cache state, line ownership, snoop results, and offcore response counts live in hardware during perf sessions. `MSRValue` filters are critical persistent semantics in the generated table; changing a single mask changes the request/response category. `Data_LA` does not store addresses, but marks events that can support data address reporting when precise sampling is configured.

## Dependencies and Integration Points

This catalog depends on Rocket Lake core PMU support, offcore response MSRs, and perf's PMU event generator. It integrates with `perf stat`, `perf record`, `perf mem`, cache tuning, NUMA/coherency investigations, and Intel metric expressions that reference L1/L2/L3 and offcore events. It complements `memory.json`, which covers L3-miss DRAM and transactional-memory behavior, and `frontend.json`, which covers instruction-fetch side pressure.

## Risks and Edge Cases

The largest risk is offcore filter correctness: all `OCR.*` rows share event `0x2a` style programming but differ by `MSRValue`; any generator or manual edit that drops MSR fields collapses distinct aliases into wrong counts. `Data_LA` events need precise sampling support to produce useful addresses. `CounterMask` and `EdgeDetect` distinguish cycles from periods for rows like `L1D_PEND_MISS.FB_FULL_PERIODS`. L2 events, retired load events, and offcore rows count different stages and should not be summed blindly. Offcore response MSRs are limited resources and can conflict when grouping many filtered events.

## Test Signals

Validation should include JSON parsing, generated table build success, and `perf list` visibility for L1D, L2, retired-memory, and OCR aliases. Pointer chasing should raise `L1D_PEND_MISS` and deeper miss rows. L2-sized and LLC-sized working sets should separate L2 hits from misses. Cross-core sharing tests should exercise snoop and HITM OCR rows. Precise load sampling tests should confirm `Data_LA` rows expose address-capable descriptions and work with `perf mem` or precise `perf record` modes.
