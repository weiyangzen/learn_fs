# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/memory.json

## Purpose
Broadwell-DE memory-ordering, misalignment, load-latency, and transactional-memory event catalog. It defines 39 events covering HLE and RTM starts, commits, abort categories, transaction execution and memory abort reasons, machine clears from memory ordering, misaligned loads/stores, and `MEM_TRANS_RETIRED` load-latency thresholds.

## Important APIs, Types, and Functions
All events have `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Optional fields include `PublicDescription` on 37 entries, `PEBS` on 10, `Data_LA` on 8 load-latency entries, `MSRIndex` and `MSRValue` on 8 latency-threshold events, and `Errata` on 8. Families are `HLE_RETIRED`, `RTM_RETIRED`, `TX_EXEC`, `TX_MEM`, `MEM_TRANS_RETIRED`, `MISALIGN_MEM_REF`, and `MACHINE_CLEARS`.

## Control Flow
Perf programs these aliases as raw events. The `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` aliases require latency-threshold MSR programming through the specified `MSRIndex`/`MSRValue`, then collect PEBS-capable load latency samples. Transactional-memory events are counted directly and can feed user analysis of TSX/HLE/RTM behavior. `MACHINE_CLEARS.MEMORY_ORDERING` is also used by top-down bad speculation and memory-ordering diagnosis.

## State and Persistence
The file is static, but some events create runtime PMU state beyond the event select register: latency events program an MSR threshold and can produce precise samples with data linear addresses. Transactional counters persist only during measurement and reflect workload use of HLE/RTM instructions.

## Dependencies and Integration
The memory file integrates with perf PEBS support, MSR programming support for load latency thresholds, pipeline machine-clear metrics, and cache/offcore files for broader memory-bound analysis. It complements but does not replace cache hierarchy events.

## Risks
Risks include latency-threshold events failing when MSR programming is unavailable, PEBS/Data_LA data being blocked by kernel permissions, TSX events being irrelevant or unavailable when TSX is disabled by microcode or kernel policy, and errata affecting transaction or latency counts. Misaligned and memory-ordering events are narrow signals that need context from cache and pipeline metrics.

## Test Signals
Validate JSON, list all `HLE_RETIRED`, `RTM_RETIRED`, `TX_*`, and `MEM_TRANS_RETIRED` aliases, and run `perf stat` on workloads with misaligned memory access, lock elision or RTM when available, and controlled load-latency patterns. PEBS tests should verify that latency-threshold events produce precise sample records with data addresses.
