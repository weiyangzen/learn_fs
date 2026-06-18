# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/memory.json

Purpose: Defines two Clearwater Forest memory-topic offcore response aliases for demand data reads and demand RFOs that miss in L3. These are narrower memory-subsystem companions to the cache-topic `OCR.*.ANY_RESPONSE` aliases.

Important APIs/types/functions: Both records use `EventCode: 0xB7`, `UMask: 0x1`, counters `0,1,2,3,4,5,6,7`, `SampleAfterValue: 100003`, `MSRIndex: 0x1a6,0x1a7`, and offcore `MSRValue` filters. `OCR.DEMAND_DATA_RD.L3_MISS` uses `MSRValue: 0x33FBFC00001`; `OCR.DEMAND_RFO.L3_MISS` uses `MSRValue: 0x33FBFC00002`.

Control flow: At build time, `jevents.py` records these rows as Clearwater Forest aliases with extra MSR programming. At runtime, perf programs the core event selector plus the offcore response MSR mask, so only demand data read or RFO transactions not supplied by L3 are counted. The two events differ only in the low request-type bits of the MSR value.

State and persistence behavior: The JSON is static. Runtime state includes the selected offcore response MSR filter while perf owns the event and the per-core counter values. These are request/response filters, not durable memory state; counts depend on enabled intervals and scheduling.

Dependencies: Depends on perf support for `MSRIndex`/`MSRValue`, Clearwater Forest offcore response MSR semantics, and the core PMU event `0xB7`. It also depends on cache hierarchy semantics where "not supplied by L3" is the desired boundary for memory-level analysis.

Integration points: Integrates with `cache.json` through the matching `OCR.DEMAND_DATA_RD.ANY_RESPONSE` and `OCR.DEMAND_RFO.ANY_RESPONSE` events; the L3-miss variants should be subsets of those broader response counts. They also pair with `pipeline.json` backend-bound events and `virtual-memory.json` page-walk events to distinguish memory misses from translation or execution stalls.

Risks: Offcore response masks are dense and easy to mistype; both rows share the raw event selector and differ mainly by large `MSRValue` constants. Extra MSR filters may conflict if multiple OCR events are scheduled together. The events count demand requests and software prefetches for exclusive ownership for RFO, so they should not be interpreted as pure retired-store misses.

Test signals: JSON generation should preserve both `MSRIndex` and large `MSRValue` constants. `perf list` should show the two L3-miss OCR aliases. Hardware checks should compare streaming read and write/RFO workloads, and verify L3-miss counts are less than or equal to corresponding any-response aliases from `cache.json`.
