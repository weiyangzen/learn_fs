# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/cache.json

## Purpose
This JSON file defines Jake Town cache, memory-access, and offcore-response core PMU events for perf. Its 123 entries cover L1D allocation, replacement, eviction, pending misses, L2 lines and requests, lock cycles, retired memory uops, LLC hit and miss retirement, offcore requests, offcore outstanding requests, offcore response filters, and split lock signals. It supports cache hierarchy and memory-access analysis on Sandy Bridge-EP/Jake Town systems.

## Important APIs, Types, And Functions
The file is a declarative event table. Important fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `AnyThread`, `PEBS`, `MSRIndex`, `MSRValue`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Most entries use counters `0,1,2,3`, while `OFFCORE_RESPONSE` entries are constrained to counter `2` and program MSRs `0x1a6,0x1a7` with per-alias `MSRValue` filters. Families include `L1D*`, `L2_*`, `MEM_*`, `LONGEST_LAT_CACHE`, `OFFCORE_REQUESTS*`, `OFFCORE_RESPONSE*`, `LOCK_CYCLES`, and `SQ_MISC`.

## Control Flow
There is no executable flow in the file. Perf parses the descriptors into Jake Town aliases and, for ordinary events, programs the core PMU with event code and unit mask. For offcore response aliases, perf also programs the offcore response MSR filter indicated by `MSRIndex` and `MSRValue`; this is why these rows carry additional metadata and a narrower counter constraint. `CounterMask`, `AnyThread`, and `PEBS` alter how the kernel programs or samples the event.

## State And Persistence
The file persists static encoding and descriptive metadata. Runtime cache and offcore state is in hardware PMU counters and offcore MSRs during a perf session. PEBS-capable rows declare precise-event eligibility, but actual sampling buffers and records are allocated by perf and the kernel. Counter constraints are persistent metadata used to prevent invalid scheduling or to drive multiplexing decisions.

## Dependencies And Integration Points
The file integrates with perf's Jake Town model map, the x86 core PMU driver, and offcore-response MSR programming support. It is a dependency for metrics that reference memory hierarchy events and for user workflows that inspect local versus remote DRAM, LLC hit snoop outcomes, L2 request types, and pending miss pressure. The event names must match metric expressions in other JSON metric files if those metrics consume them.

## Risks And Edge Cases
Offcore response filters are the highest-risk area because a wrong `MSRValue` can still count a valid but different response class. Counter `2` restrictions on offcore aliases must be preserved. Some events use `CounterMask` to count cycles above an occupancy threshold rather than raw occurrences, so descriptions and metric formulas need to treat them differently. PEBS flags must align with hardware support or precise sampling may fail. Remote/local DRAM aliases depend on platform topology and may not behave intuitively on all systems.

## Test Signals
Validation includes `jq empty`, `jevents` parser success, duplicate-name checks, and inspection of generated offcore encodings. Runtime checks include `perf stat` on L1/L2/LLC workloads, PEBS sampling of retired memory-load events, offcore response counts changing under local and remote memory placement, and expected scheduling behavior when multiple counter-2-only offcore events are requested together.
