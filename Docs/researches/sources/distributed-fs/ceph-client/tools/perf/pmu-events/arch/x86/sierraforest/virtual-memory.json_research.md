# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/virtual-memory.json

## Purpose
Defines Sierra Forest core virtual-memory PMU aliases for perf. The 17-entry JSON array covers demand-load, store, and instruction-side TLB misses, second-level TLB hits, page-walk completion by page size, pending page-walk cycles, and a retirement stall event tied to DTLB misses.

## Important APIs, Types, And Event Groups
Objects use the core perf PMU event schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and optional `SampleAfterValue`. Unlike the uncore Sierra Forest files, there is no `Unit` because these are core PMU events. Event groups include `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, `ITLB_MISSES.*`, and `LD_HEAD.DTLB_MISS_AT_RET`.

The aliases distinguish STLB hits from page walks, aggregate walk-completed masks from page-size-specific masks, and pending-walk cycle events from completed-walk counts. Load and store families use different event codes (`0x08` and `0x49`), while instruction-side events use `0x85`.

## Control Flow
Perf consumes the file declaratively. During build, entries are transformed into alias table rows. During runtime, selecting a virtual-memory alias programs a core PMU counter with the event code and umask. Analysis control flow is left to the user: compare STLB-hit counts with page-walk counts, split load/store/instruction behavior, and use pending-cycle events to estimate walk pressure.

## State And Persistence
The JSON persists static alias definitions only. Runtime state is per-process, per-CPU, or system-wide depending on the perf command used. Hardware counters hold counts during an active session; perf stores results in command output or `perf.data`, not in this file.

## Dependencies And Integration Points
The file depends on Sierra Forest core PMU support and perf's x86 PMU event-map mechanism. It integrates with broader perf workflows for page-size tuning, TLB pressure analysis, and front-end versus data-side stall attribution. It complements cache and memory-controller event files by explaining address-translation costs before memory/cache access.

## Risks
Some brief descriptions are terse and one entry says `DTLB_STORE_MISSES.WALK_COMPLETED` counts misses to a 1G page despite its aggregate `0xe` mask, so documentation review is needed before relying on that wording. Pending-walk events count outstanding walks per cycle, not completed walks. Aggregated aliases can double count if summed with page-size-specific aliases from the same event group.

## Test Signals
Tests include `jq empty`, perf table generation, and `perf list` visibility for each alias. Runtime smoke tests can run TLB-stressing workloads with small and huge pages and verify that 4K versus 2M/4M walk aliases move in expected directions. Sampling tests should verify `SampleAfterValue` handling where present.
