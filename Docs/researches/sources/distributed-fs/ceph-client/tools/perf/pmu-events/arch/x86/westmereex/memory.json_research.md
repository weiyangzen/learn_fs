# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/memory.json

Purpose: declares 68 Westmere EX memory-locality PMU events for perf. It focuses on misaligned stores and offcore response classifications for DRAM, LLC miss, local DRAM, and remote DRAM outcomes across request types.

Important APIs/types/functions: most rows are `OFFCORE_RESPONSE.*` events with `EventCode` `0xB7`, `UMask` `0x1`, `Counter` `2`, `MSRIndex` `0x1A6`, and a request/response-specific `MSRValue`. The lone non-offcore row is `MISALIGN_MEM_REF.STORE` using `EventCode` `0x5`, `UMask` `0x2`, generic counters `0,1,2,3`, and sample-after `200000`.

Control flow: there is no executable control flow. Perf's event-generation path reads the JSON objects and produces event tables. At runtime, selecting an offcore event causes perf to program the raw event plus the offcore response MSR filter so the counter observes the requested memory outcome.

State and persistence: static metadata in the repository. Runtime state is limited to transient PMU counter programming and offcore MSR configuration during perf measurements.

Dependencies: depends on the x86 offcore response programming model for Westmere EX and perf support for `MSRIndex`/`MSRValue` fields. It overlaps intentionally with `cache.json`, which contains broader offcore response categories including cache, IO/MMIO, and combined cache/DRAM outcomes.

Integration points: exposed as `perf` event aliases for memory locality and NUMA-like analysis on Westmere EX. Request classes include data reads, instruction fetches, RFOs, writebacks, demand/prefetch splits, and aggregate request groups. These event names can also be referenced by generated metrics after `metric.py` loads model events.

Risks: every offcore row is counter-specific and MSR-specific; wrong `MSRValue` values would produce plausible but false locality data. The `OTHER.LOCAL_DRAM` combination is absent while related combinations exist, so validators should avoid assuming a complete 4-way matrix for every request prefix. Moving rows between `memory.json` and `cache.json` without preserving names may break metric references.

Test signals: JSON parse; 68 rows; 67 rows with `MSRIndex` `0x1A6`; all offcore rows constrained to counter `2`; unique event names; valid hex `MSRValue` strings. Integration checks should build the pmu-events tables and inspect generated `perf list` output for representative local/remote DRAM aliases.
