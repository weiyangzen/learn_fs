# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/memory.json

## Purpose
`memory.json` defines 23 Tiger Lake events for memory latency, L3-miss stalls, memory-ordering machine clears, TSX/RTM transactional behavior, and transaction abort causes. It complements `cache.json` by focusing on latency thresholds and transactional memory failure modes rather than broad cache hierarchy request counts.

## Important APIs, Types, and Fields
The file uses `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `SampleAfterValue`, and optional `PublicDescription`. It includes `CounterMask` for `CYCLE_ACTIVITY.STALLS_L3_MISS`, `Data_LA` for eight `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` events, and `MSRIndex`/`MSRValue` for those same load-latency threshold events. Transactional events include `RTM_RETIRED.*`, `TX_EXEC.*`, and `TX_MEM.*` families.

## Control Flow and Data Flow
Perf turns these definitions into named Tiger Lake events. Runtime flow resolves threshold names such as `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128`, programs the core PMU and latency threshold MSR, and optionally records data linear addresses for sampled loads. TSX events count transaction starts, commits, aborts, and abort categories.

## State and Persistence Behavior
The JSON stores only definitions. Hardware PMU state tracks counts during a measurement. Load-latency events with `Data_LA` can lead to address samples in perf output. TSX counters reflect architectural transaction behavior, and on systems where TSX is disabled or unavailable, they may be unsupported or always zero.

## Dependencies and Integration Points
The file depends on Tiger Lake PMU support for precise memory latency thresholds and TSX event encodings. It integrates with `cache.json` load-source events, `pipeline.json` stall and machine-clear counters, and topdown memory latency groups in `metricgroups.json`.

## Risks and Edge Cases
Latency threshold events are not disjoint buckets; a load above 512 cycles also satisfies lower thresholds. MSR threshold programming can conflict with other events that use the same filter mechanism. TSX availability varies by microcode, BIOS policy, and kernel mitigations, so TSX events can be present in tables but not meaningful on a given machine. `MACHINE_CLEARS.MEMORY_ORDERING` is a pipeline recovery signal, not a direct memory bandwidth metric.

## Test Signals
Validate JSON and generated event tables. On Tiger Lake hardware, `perf list` should expose load-latency threshold events and TSX families. Runtime tests should use pointer-chasing or cache-miss workloads to observe monotonic threshold behavior across `LOAD_LATENCY_GT_*`. Transactional tests require a TSX-enabled system and should compare `RTM_RETIRED.START`, `COMMIT`, and abort categories.
