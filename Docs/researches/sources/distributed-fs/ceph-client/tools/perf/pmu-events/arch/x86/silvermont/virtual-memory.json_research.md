# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/virtual-memory.json

## Purpose
Defines Silvermont virtual-memory PMU aliases for perf. The seven-entry JSON array covers retired load uops that missed the DTLB and page-walk cycles/walk counts split between data side, instruction side, and aggregate I-side plus D-side behavior.

## Important APIs, Types, And Event Groups
The objects follow the core perf PMU schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, optional `PEBS`, and `Counter`. Event groups are `MEM_UOPS_RETIRED.DTLB_MISS_LOADS` and `PAGE_WALKS.*`. The page-walk aliases use event code `0x05` with masks `0x1`, `0x2`, and `0x3`; the same masks are exposed as both cycle-duration aliases and completed-walk aliases, relying on the event name and perf metadata to describe the intended interpretation.

## Control Flow
The file is declarative. Perf table generation creates aliases, and runtime selection programs normal Silvermont core PMU events. Analysis flow is to count load uops with DTLB misses, then compare page-walk cycles and walk counts by data side and instruction side. Aggregate `PAGE_WALKS.CYCLES`/`WALKS` should be used as totals rather than summed with their component aliases.

## State And Persistence
Static event metadata is persisted in the JSON. Runtime page-walk counts and cycle samples live only in perf event state and hardware counters. `PEBS` on `MEM_UOPS_RETIRED.DTLB_MISS_LOADS` means precise sampling may be available for identifying instructions causing DTLB-miss load uops.

## Dependencies And Integration Points
This file depends on Silvermont core PMU and PEBS support. It integrates with `other.json` through ITLB fetch-stall cycles, with `cache.json` through `MEM_UOPS_RETIRED.UTLB_MISS`, and with pipeline counters for cycles/instructions normalization. It is used in TLB and page-size tuning workflows.

## Risks
The page-walk aliases share event codes and masks between cycle and walk names, so consumers must verify that the underlying hardware and perf parser distinguish count modes as intended; otherwise the names may appear redundant. Aggregates overlap with I-side and D-side components. DTLB miss load events do not cover store or instruction-side misses, so broader virtual-memory analysis needs sibling events.

## Test Signals
Validate syntax and generated perf aliases. Runtime tests should run workloads with high data-side TLB pressure and instruction-side pressure separately, checking that D-side and I-side aliases respond differently. PEBS sampling on `MEM_UOPS_RETIRED.DTLB_MISS_LOADS` should produce precise attribution when the hardware and kernel support it.
