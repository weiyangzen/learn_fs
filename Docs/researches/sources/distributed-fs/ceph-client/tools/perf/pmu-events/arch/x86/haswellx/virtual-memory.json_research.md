# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/virtual-memory.json

## Purpose

`haswellx/virtual-memory.json` defines 49 HaswellX core PMU aliases for TLB misses, page walks, page-walker load sources, EPT walk cycles, ITLB flushes, and TLB flush classes. Unlike the uncore files in this work item, these entries omit `Unit` and therefore target the default core PMU. They let perf expose virtual-memory translation behavior for demand loads, stores, instruction fetches, and page-walk memory hierarchy outcomes.

## Important APIs, types, and schema

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and usually `PublicDescription`. Four records carry `Errata` notes. `Unit` is absent, so `jevents.py` maps these records to `default_core`. Every event allows counters `0,1,2,3`, and every record has a sampling period hint through `SampleAfterValue`.

Important families are `DTLB_LOAD_MISSES.*` and `DTLB_STORE_MISSES.*` for first-level and second-level DTLB outcomes, STLB hits, completed page walks by page size, and walk duration; `ITLB_MISSES.*` for instruction TLB miss and walk outcomes; `PAGE_WALKER_LOADS.*` for DTLB and ITLB page-walk accesses that hit L1, L2, L3, or memory; `EPT.WALK_CYCLES` for extended page-table walk cycle cost; `ITLB.ITLB_FLUSH`; and `TLB_FLUSH.DTLB_THREAD` plus `TLB_FLUSH.STLB_ANY`.

## Control flow and integration

The JSON is parsed into generated perf event tables for the HaswellX CPU model. `jevents.py` lowercases `EventName`, treats the missing `Unit` as `default_core`, preserves `SampleAfterValue`, and appends errata text to event descriptions when `Errata` exists. At runtime, perf core PMU alias lookup uses the generated rows to program the event select and umask on general-purpose core counters.

## State and persistence behavior

This file has no mutable state. Its persistent behavior is the mapping from TLB/page-walk alias names to core PMU encodings and default sample periods. `SampleAfterValue` is part of the profiling contract: changing it affects sampling frequency and overhead even when the raw event encoding is unchanged. Errata annotations are also persistent user-facing risk metadata.

## Dependencies

Dependencies include Intel HaswellX core PMU documentation, perf's PMU JSON schema, generated `pmu-events.c`, core PMU counter availability, and `jevents.py` support for `Errata` and `SampleAfterValue`. The file depends semantically on x86 paging concepts, STLB behavior, page sizes, page-miss handler cycles, EPT virtualization walks, and TLB shootdown/flush behavior.

## Risks

TLB events are easy to misaggregate because masks such as `WALK_COMPLETED` combine page sizes while sibling aliases isolate 4K, 2M/4M, and 1G walks. `PAGE_WALKER_LOADS` errata on L3 and memory outcomes must be preserved so users understand specification caveats. `EPT.WALK_CYCLES` is virtualization-specific and can be misread on non-virtualized workloads. High-frequency sampling of page-walk duration or STLB events can perturb workloads if `SampleAfterValue` is reduced too far.

## Test signals

Useful tests are JSON syntax validation, perf event table generation, `perf list` showing HaswellX virtual-memory aliases, and runtime `perf stat` checks on workloads with controlled TLB pressure. Huge-page versus 4K-page tests should shift the page-size-specific walk aliases. Virtualized workloads should exercise EPT walk cycles, while TLB shootdown tests can validate the flush aliases.
