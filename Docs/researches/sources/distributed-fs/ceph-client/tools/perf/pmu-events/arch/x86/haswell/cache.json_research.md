# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/cache.json

## Purpose
This JSON file defines 94 Intel Haswell core PMU cache, memory, offcore, and memory-uop events for perf. It covers L1D replacement and pending misses, L2 line/request/transaction activity, lock and split-lock behavior, retired load/store memory uops, offcore request and outstanding-request events, and offcore response filters for L3 hit and peer-core snoop outcomes. The source was read as a complete 926-line JSON array.

## Important APIs, Types, and Functions
The file uses perf's x86 event JSON schema. Every row has `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`; 51 rows include `PublicDescription`. Specialized fields include `PEBS`, `Data_LA`, `AnyThread`, `CounterMask`, `Errata`, `MSRIndex`, and `MSRValue`. There are 94 unique event names and 19 unique event codes. Most events use generic counters `0,1,2,3`, while `OFFCORE_RESPONSE` rows use counter `2`, reflecting Haswell offcore response constraints.

Key families include `L1D.*`, `L1D_PEND_MISS.*`, `L2_LINES_IN/OUT.*`, `L2_RQSTS.*`, `L2_TRANS.*`, `LOCK_CYCLES.*`, `LONGEST_LAT_CACHE.*`, `MEM_LOAD_UOPS_*`, `MEM_UOPS_RETIRED.*`, `OFFCORE_REQUESTS.*`, `OFFCORE_REQUESTS_BUFFER.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, `OFFCORE_RESPONSE.*`, and `SQ_MISC.SPLIT_LOCK`. PEBS-capable rows are concentrated in retired load and memory-uop events. Twenty offcore response rows program MSRs `0x1a6,0x1a7` with specific `MSRValue` filters.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON. During build generation, `jevents.py` records standard event fields and Haswell-specific MSR filter metadata. Runtime perf resolves aliases, schedules events on core counters, and programs extra offcore-response MSR filters when `MSRIndex`/`MSRValue` is present. PEBS and data linear-address fields influence sampling behavior for supported events.

Static state includes event encodings, sample periods, counter masks, errata annotations, offcore filter MSR programming values, and PEBS capabilities. Persistence is through generated perf event tables. Runtime counts and PEBS samples are session data and depend on workload, privilege mode, and CPU stepping.

## Dependencies and Integration Points
Dependencies include Haswell PMU definitions, perf's JSON schema, `jevents.py`, kernel x86 PMU and PEBS support, and offcore response MSR programming support. The file integrates with `perf list`, `perf stat`, `perf record`, top-down or memory-analysis workflows, and user scripts that rely on stable Intel event aliases.

Offcore response events are a major integration point: they combine the generic `OFFCORE_RESPONSE` event with model-specific MSR filters to classify L3 hits, HITM, and no-forward peer-core outcomes for demand reads, RFOs, code reads, prefetches, and all requests. Memory-retired PEBS events integrate with data address sampling and are useful for load-latency and memory locality investigations.

## Risks and Test Signals
Risks include extensive errata coverage, especially for `MEM_LOAD_UOPS_*`, `MEM_UOPS_RETIRED.*`, `L2_RQSTS.*`, and `OFFCORE_REQUESTS_OUTSTANDING.*`; offcore MSR filter mistakes; PEBS/Data_LA exposure on unsupported kernels; and counter scheduling constraints for offcore response aliases. `AnyThread` and `CounterMask` fields change event interpretation, and sample-after values vary from `20011` through multi-million defaults.

Test signals include JSON validation, `jevents.py` generation, generated-table inspection for MSR fields, `perf list` visibility, `perf stat` smoke tests for L1/L2/offcore families, and `perf record` tests for PEBS-capable memory events. Hardware validation should compare cache-sensitive workloads, streaming memory, locked operations, and cross-core sharing workloads against the relevant aliases while checking errata notes for the tested Haswell stepping.
