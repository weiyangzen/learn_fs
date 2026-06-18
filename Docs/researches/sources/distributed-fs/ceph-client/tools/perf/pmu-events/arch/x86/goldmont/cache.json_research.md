# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/cache.json

## Purpose

`cache.json` defines 103 Goldmont core PMU events for cache behavior, retired memory uops, L1/L2 hits and misses, dirty evictions, fetch stalls caused by I-cache fill, L2 queue rejection, and a large offcore-response matrix. It is the main Goldmont perf catalog for cache hierarchy and offcore memory-response analysis.

## Important APIs, Types, and Data Fields

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and optional `PEBS`, `Data_LA`, `MSRIndex`, and `MSRValue`. Families include `LONGEST_LAT_CACHE.*`, `MEM_LOAD_UOPS_RETIRED.*`, `MEM_UOPS_RETIRED.*`, `OFFCORE_RESPONSE.*`, `DL1.DIRTY_EVICTION`, `FETCH_STALL.ICACHE_FILL_PENDING_CYCLES`, `CORE_REJECT_L2Q.ALL`, and `L2_REJECT_XQ.ALL`.

The 83 `OFFCORE_RESPONSE.*` rows are notable because they use `MSR_OFFCORE_RESP` programming through `MSRIndex` values such as `0x1a6,0x1a7` and detailed `MSRValue` filters. Retired load/uop rows are precise-capable (`PEBS: 2`) and mark load-address support with `Data_LA: 1`.

## Control Flow and Data Flow

The file has no executable control flow. Perf tooling translates the JSON rows into Goldmont event aliases. For normal cache and retired-uop rows, perf programs core event select/umask counters. For offcore-response rows, perf also writes the offcore response MSR filter to select request types and response categories such as L2 hit, L2 miss, HITM from another core, snoop miss, outstanding demand data reads, RFOs, code reads, prefetches, streaming stores, and bus locks.

## State and Persistence Behavior

Static event definitions are persistent in the source tree; runtime counter values and PEBS samples are session-local. Offcore rows have hidden state in the programmed MSR filter during the perf session. Precise retired-memory rows can produce sampled data-address records when the kernel and CPU support PEBS with data linear address.

## Dependencies and Integration Points

The catalog depends on Goldmont core PMU support, PEBS support for precise rows, and kernel support for programming offcore-response MSRs. It integrates with perf cache analysis, memory-load latency and source analysis, false-sharing/HITM studies, non-temporal and streaming-store analysis, prefetch efficiency studies, front-end fetch-stall diagnosis, and lock/split-lock investigations.

## Risks and Edge Cases

Offcore-response rows are sensitive to correct `MSRIndex`/`MSRValue` handling; losing those fields changes the event meaning completely. Some rows can use both offcore MSRs, while `COREWB` and `OUTSTANDING` rows list only `0x1a6`; scheduling may be constrained. PEBS rows require hardware/kernel support and may fail or degrade to counting only on unsupported setups. `LONGEST_LAT_CACHE` counts L2-oriented requests on Goldmont and should not be assumed to match larger-core LLC semantics. `FETCH_STALL.ICACHE_FILL_PENDING_CYCLES` belongs in this cache file but measures front-end stall cycles.

## Test Signals

Validation should include JSON parsing, perf table generation, and `perf list` checks for normal, PEBS, and offcore aliases. Cache-resident versus streaming workloads should separate L1/L2 hit and miss counts. Cross-core sharing tests should move HITM offcore rows. Non-temporal store workloads should exercise streaming-store rows. PEBS smoke tests should confirm precise sampling and data-address capture for `MEM_LOAD_UOPS_RETIRED.*` where supported. Offcore tests should verify MSR filters are programmed and restored correctly.
