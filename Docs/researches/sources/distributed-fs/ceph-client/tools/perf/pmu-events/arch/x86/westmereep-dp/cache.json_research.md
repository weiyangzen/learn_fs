<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/cache.json

## Purpose

`cache.json` is the Westmere EP DP cache and offcore-response PMU catalog for perf. It contains 286 core PMU event records covering L1D and L1I behavior, L2 requests/transactions/line movement/write locks, LLC reference/miss proxies, retired memory instruction latency thresholds, retired load/store outcomes, offcore requests, outstanding offcore requests, store queue conditions, split locks, and a large matrix of offcore response filters. It is the main source for cache hierarchy and memory-response attribution on this architecture.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects using `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and optional `MSRIndex`, `MSRValue`, and `PEBS`. Counter availability is mostly `0,1,2,3`, with some events restricted to `0`, `0,1`, or `3`. There are 185 records with offcore `MSRIndex` programming, 15 PEBS-capable records, and 185 records with `SampleAfterValue`.

Major event families include `CACHE_LOCK_CYCLES`, `L1D`, `L1D_PREFETCH`, `L1D_WB_L2`, `L1I`, `L2_DATA_RQSTS`, `L2_LINES_IN`, `L2_LINES_OUT`, `L2_RQSTS`, `L2_TRANSACTIONS`, `L2_WRITE`, `LONGEST_LAT_CACHE`, `MEM_INST_RETIRED`, `MEM_LOAD_RETIRED`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `OFFCORE_REQUESTS_SQ_FULL`, `OFFCORE_RESPONSE`, `SQ_MISC`, and `STORE_BLOCKS`. The largest family is `OFFCORE_RESPONSE` with 170 records spanning request types such as demand data, demand ifetch, demand RFO, prefetch data/ifetch/RFO, core writeback, and response locations such as local cache, local DRAM plus remote cache hit, remote cache HITM, IO/CSR/MMIO, and other-core hit states.

## Control Flow and Data Flow

There is no executable control flow. Perf's generator turns each row into an alias. For normal cache events, runtime perf programs the core event select, umask, and counter constraint. For offcore-response rows, perf must also program the offcore response MSR specified by `MSRIndex` with the filter in `MSRValue`; this filter is the actual selector for request type and response source. PEBS-capable retired memory rows can feed precise sampling, while ordinary rows feed counts.

The data flow supports layered analysis: L1/L2 rows show near-core behavior; `LONGEST_LAT_CACHE` and `MEM_LOAD_RETIRED` rows indicate LLC and retired-load outcomes; `OFFCORE_REQUESTS*` rows measure requests and outstanding demand; and `OFFCORE_RESPONSE.*` rows attribute misses or offcore traffic to cache, local DRAM, remote cache, HITM, or IO-like sources.

## State and Persistence Behavior

The file persists static event encodings and MSR filter values. Runtime counter state is interval-local. Offcore-response measurement has temporary hardware state in offcore response MSRs during a perf session; the JSON's `MSRIndex`/`MSRValue` pairs are therefore part of the event's semantic identity. PEBS rows can produce sampled records if the kernel and CPU support precise events, but samples are not persisted here.

## Dependencies and Integration Points

This catalog depends on Westmere EP DP core PMU support, PEBS support for precise retired-memory rows, and kernel/perf support for programming offcore response MSRs. It integrates with `perf list`, `perf stat`, `perf record`, cache-miss analysis, memory-latency and source attribution, NUMA/local-versus-remote investigations, false-sharing/HITM studies, prefetch efficiency analysis, split-lock/lock-cycle diagnosis, and event scheduling logic constrained by the `counter.json` topology.

## Risks and Edge Cases

The highest risk is losing or corrupting `MSRIndex` and `MSRValue` on offcore-response rows; the alias may still exist but count a different request/response class. Many offcore rows are combinations of similar request and response masks, so copy/paste or generator ordering errors are hard to spot by name alone. PEBS-capable rows may degrade or fail on unsupported kernels. Counter restrictions can force multiplexing or reject groups, especially with events limited to counter `3` or `0,1`. Offcore and package/NUMA interpretations are architecture-specific; Westmere EP DP semantics should not be assumed to match newer Intel LLC/offcore definitions exactly.

## Test Signals

Validation should include JSON parse success, perf event-table generation, and `perf list` exposure of normal, PEBS, and offcore aliases. Runtime tests should compare cache-resident, streaming, and random-access workloads to separate L1/L2/LLC behavior; use local versus remote NUMA memory where available to exercise offcore response location filters; use cross-core sharing workloads to move HITM-related rows; and run precise sampling smoke tests for `MEM_INST_RETIRED.*` and `MEM_LOAD_RETIRED.*`. Generator tests should assert that `MSRIndex` and `MSRValue` are preserved exactly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/cache.json -->
