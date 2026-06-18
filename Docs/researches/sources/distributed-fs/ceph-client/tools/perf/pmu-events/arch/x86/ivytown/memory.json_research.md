# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/memory.json

Purpose: Defines 41 Ivy Town memory-related core PMU aliases for memory-ordering machine clears, load latency sampling thresholds, precise store sampling, misaligned memory references, and LLC-miss offcore response classes. It extends the cache file's memory coverage with latency and remote/local DRAM attribution.

Important APIs/types/functions: Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `MSRIndex`, `MSRValue`, `PEBS`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Families include `MACHINE_CLEARS`, `MEM_TRANS_RETIRED`, `MISALIGN_MEM_REF`, and many `OFFCORE_RESPONSE.*.LLC_MISS.*` aliases. `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` variants share event select `0xCD` and are constrained to counter 3 for PEBS-style latency sampling thresholds.

Control flow: Perf exposes these aliases after JSON table generation. Runtime use maps ordinary aliases to core event fields and maps offcore aliases to offcore response event select plus MSR filters. Precise load/store events can drive sampling workflows, while offcore LLC-miss aliases feed memory locality and remote-hit diagnostics.

State and persistence: Static metadata only. Runtime state is in PMU counters, offcore filter MSRs, and PEBS records. The file persists threshold alias names and filter encodings.

Dependencies/integration: Depends on Ivy Town PMU offcore response and PEBS support. It complements `cache.json`, which covers many LLC-hit and request-side aliases. Metrics such as remote memory/cache, false sharing, memory latency, and synchronization diagnostics can depend on these offcore response names.

Risks: Many offcore aliases share visible event fields and differ only by MSR filter values, so filter metadata correctness is critical. Some descriptions in the offcore family use hit/miss wording that should be audited carefully. Counter 3 constraints on latency events can conflict with other events in a group. PEBS availability may depend on kernel/hardware support and privilege settings.

Test signals: Static tests should verify required `MSRIndex`/`MSRValue` fields for every offcore response alias and counter constraints for `MEM_TRANS_RETIRED`. Runtime smoke tests should exercise load-latency sampling, misaligned access counters, and local versus remote memory workloads where Ivy Town NUMA hardware is available.
