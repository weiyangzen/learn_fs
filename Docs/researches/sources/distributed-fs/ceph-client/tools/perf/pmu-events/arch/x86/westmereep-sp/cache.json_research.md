# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/cache.json

Purpose: defines the large 325-entry Westmere-EP single-processor cache and memory-locality event table. It spans L1D/L1I, L2 requests and transactions, cache line movement, retired memory operations, offcore requests, offcore responses, and load-latency threshold sampling.

Important APIs/types/functions: standard event fields are extended with `MSRIndex`, `MSRValue`, `CounterMask`, and `PEBS`. Major families include `L1D*`, `L1I.*`, `L2_RQSTS.*`, `L2_DATA_RQSTS.*`, `L2_LINES_*`, `L2_TRANSACTIONS.*`, `L2_WRITE.*`, `LONGEST_LAT_CACHE.*`, `MEM_INST_RETIRED.*`, `MEM_LOAD_RETIRED.*`, `MEM_UNCORE_RETIRED.*`, `OFFCORE_REQUESTS*`, and 203 `OFFCORE_RESPONSE.*` aliases.

Control flow: build-time `jevents.py` reads every row and emits generated PMU table entries. Offcore response rows use `MSRIndex` `0x1a6,0x1a7`; load latency threshold rows use `MSRIndex` `0x3F6`, which `JsonEvent` maps to `ldlat=`. Runtime perf programs normal event selectors plus MSR filters where required.

State and persistence: static source data only. Runtime state is active PMU counter configuration and MSR filter programming. PEBS retired-memory rows can carry sampled instruction attribution.

Dependencies and integration points: tied to CPUID `GenuineIntel-6-25` via `arch/x86/mapfile.csv`. Integrates with `perf list`, `perf stat`, `perf record`, memory hierarchy tuning, and locality analysis.

Risks: this file has the broadest blast radius in the assignment. Offcore and latency events depend on exact MSR bitmasks and thresholds; a typo can produce plausible but wrong numbers. Several aliases are constrained to counters `0` or `3`, which affects event grouping. The SP table has much richer locality names than the DP memory file, so model-specific semantics must be preserved.

Test signals: `jq empty`, successful `jevents.py` generation, `perf list cache`, inspection for `offcore_rsp=` and `ldlat=`, and hardware sanity workloads for L1/L2 misses, remote/local source attribution, and latency thresholds.
