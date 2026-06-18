# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/frontend.json

## Purpose
Defines Silvermont front-end PMU aliases for perf. The eight-entry JSON array covers branch-address clears, decode restriction due to wrong predecode length prediction, instruction-cache accesses/hits/misses, and microcode-sequencer entry from the front-end complex.

## Important APIs, Types, And Event Groups
The file uses perf's core PMU schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. Event groups are `BACLEARS.*`, `DECODE_RESTRICTION.PREDECODE_WRONG`, `ICACHE.*`, and `MS_DECODED.MS_ENTRY`. The branch-address-clear aliases share event code `0xE6` with different masks for all, conditional, and return-related clears.

## Control Flow
There is no executable flow. Perf table generation converts entries into named aliases. Runtime perf selection programs the core PMU with the relevant event code and umask. User analysis flow is usually hierarchical: start with aggregate front-end stalls or instruction-cache misses, then narrow to BACLEARS, wrong predecode, or microcode flow entries.

## State And Persistence
This JSON stores static event definitions only. Runtime count and sampling state belongs to perf and hardware counters. Instruction-cache hit/miss/access counts persist only in perf output or recorded perf data when explicitly collected.

## Dependencies And Integration Points
The file depends on Silvermont core PMU support and integrates with `other.json`, which includes fetch stall aliases for all reasons and ITLB pending cycles, and with `cache.json`, which has `FETCH_STALL.ICACHE_FILL_PENDING_CYCLES`. Together these files let users distinguish front-end redirection, decode, icache, and ITLB-related pressure.

## Risks
The branch-address-clear events are speculative or front-end oriented and should not be treated as retired branch counts. Instruction-cache access/hit/miss masks are simple but easy to double count if users add aggregate and component aliases. Microcode entry counts can include fault or assist-inserted flows, so interpretation requires workload context.

## Test Signals
Run JSON validation and perf table-generation checks. On Silvermont, `perf list` should expose all eight aliases. Runtime smoke tests can use branch-heavy code, instruction-cache-sensitive loops, and code paths that trigger microcode assists to verify that related aliases respond in expected directions.
