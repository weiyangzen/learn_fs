# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/virtual-memory.json

## Purpose

`virtual-memory.json` defines 16 core PMU events for Jaketown virtual-memory and TLB behavior. Unlike the uncore files in this work item, these records describe core events: DTLB load/store misses, ITLB misses, EPT walk cycles, ITLB flushes, and TLB flush attempts.

The file supplies user-facing perf aliases for diagnosing page-walk cost, STLB hit behavior, instruction/data TLB pressure, virtualization EPT walks, and TLB flush activity.

## Important API Surface and Data Shape

The file is a JSON array of 16 unique event objects. Keys are:

- `EventName`: public alias such as `DTLB_LOAD_MISSES.WALK_DURATION`.
- `EventCode`: core PMU event select code.
- `UMask`: unit mask variant.
- `Counter`: allowed core counters, consistently `0,1,2,3`.
- `SampleAfterValue`: default sampling period hint, consistently `2000003`.
- `BriefDescription` and sometimes `PublicDescription`.

Unlike the uncore files, there is no `Unit` or `PerPkg` field. These are ordinary core PMU events selected by CPU model.

Event families:

- `DTLB_LOAD_MISSES.*`: load-side TLB miss page walks, completed walks, walk duration, and STLB hits.
- `DTLB_STORE_MISSES.*`: store-side equivalents.
- `ITLB_MISSES.*`: instruction TLB miss page walks, completed walks, walk duration, and STLB hits.
- `EPT.WALK_CYCLES`: extended page table walk cycles for virtualization.
- `ITLB.ITLB_FLUSH`: instruction TLB flushes.
- `TLB_FLUSH.DTLB_THREAD` and `TLB_FLUSH.STLB_ANY`: DTLB and STLB flush attempts.

## Control Flow

There is no executable control flow. External flow:

1. perf's pmu-events generator reads the Jaketown core event JSON files.
2. Event records become generated table entries keyed by CPU model.
3. Runtime perf exposes aliases via `perf list`.
4. `perf stat`/`perf record` resolves aliases into core PMU `EventCode` plus `UMask`.
5. For sampling, `SampleAfterValue` provides the default period hint used by generated event metadata.

The family grouping mirrors the way users reason about memory translation: data load/store TLB behavior first, then virtualization and instruction-side events, then flushes.

## State and Persistence Behavior

The file persists static core PMU alias metadata. It has no runtime state. Counts and samples are collected by hardware PMU counters during perf sessions and are not persisted by this JSON file.

The absence of `PerPkg` is meaningful: these are core PMU events, not package-level uncore events. Aggregation semantics depend on perf's selected CPU/thread scope.

## Dependencies and Integration Points

Dependencies include:

- perf's core PMU event JSON schema.
- Jaketown/Sandy Bridge core PMU event encodings for TLB and EPT events.
- Generated perf event tables and CPU-model matching.
- Runtime PMU programming support for counters `0,1,2,3`.

This file integrates with memory and uncore PMU files during performance diagnosis. For example, high `DTLB_*WALK_DURATION` can be correlated with memory-controller queue pressure from `uncore-memory.json`, but the event domains and aggregation scopes differ.

## Risks and Edge Cases

- Thirteen records omit `PublicDescription`, so generated long help relies heavily on brief text.
- All events have `SampleAfterValue`; a parser regression that treats this as mandatory elsewhere could affect files that do not provide it.
- Event code reuse is extensive: load DTLB variants share `0x08`, store DTLB variants share `0x49`, ITLB miss variants share `0x85`, and TLB flush variants share `0xBD`. Correct `UMask` preservation is critical.
- The `EPT.WALK_CYCLES` description is virtualization-specific; users may misinterpret it as ordinary page-walk duration.
- Because these are core events, adding uncore fields such as `Unit` or `PerPkg` would be wrong and could confuse generated table handling.

## Test Signals

- `jq` parse succeeds and reports 16 unique event names.
- Every object has `EventCode`, `UMask`, `Counter`, `EventName`, and `SampleAfterValue`.
- No object should have `Unit` or `PerPkg`.
- Family masks should remain distinct for walk-causing misses, completed walks, walk duration, and STLB hits.
- Generated pmu-events code should build without warnings.
- Runtime smoke tests on supported hardware can use `perf stat -e DTLB_LOAD_MISSES.WALK_DURATION,ITLB_MISSES.STLB_HIT,TLB_FLUSH.STLB_ANY` on a small workload.
