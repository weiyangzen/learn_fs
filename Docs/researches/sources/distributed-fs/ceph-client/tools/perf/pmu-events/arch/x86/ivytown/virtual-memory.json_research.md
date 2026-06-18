# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/virtual-memory.json

## Purpose
This JSON file defines Ivy Town core PMU events related to virtual memory translation. Its 20 entries cover DTLB load misses, DTLB store misses, ITLB misses, second-level TLB hits, page-walk completions and durations, TLB flushes, instruction TLB flushes, and EPT walk cycles. It gives perf users symbolic names for translation overhead analysis on Ivy Town processors.

## Important APIs, Types, And Functions
The file contains event descriptors, not functions. Important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. All entries use programmable counters `0,1,2,3` and omit an uncore `Unit`, which means they are core PMU events. Families include `DTLB_LOAD_MISSES`, `DTLB_STORE_MISSES`, `ITLB_MISSES`, `TLB_FLUSH`, `ITLB.ITLB_FLUSH`, and `EPT.WALK_CYCLES`.

## Control Flow
There is no in-file control flow. Perf parses the JSON into Ivy Town core event aliases. When a user selects an alias, perf programs the core PMU with the specified event code and unit mask. Duration events count page-walk cycles, while completed or miss-cause aliases count occurrences; metrics and users must choose the appropriate form for rate versus latency analysis.

## State And Persistence
The JSON persists only event metadata and sampling defaults. Runtime TLB miss, walk, and flush counts are maintained by hardware counters and read through perf events. `SampleAfterValue` gives perf a default sampling period for some aliases but does not imply persistence in the source tree. Because these are core events, counts are scoped to selected CPUs, threads, or tasks according to normal perf event placement.

## Dependencies And Integration Points
The file integrates with perf's Ivy Town model event map and the kernel core PMU driver. The aliases are often consumed by top-down or memory-latency metrics, profiler recipes, and manual `perf stat` runs. `EPT.WALK_CYCLES` ties the table to virtualization analysis, where nested address translation can be a separate translation-cost source.

## Risks And Edge Cases
Load, store, and instruction TLB events have similar names but different event codes and masks; swapping masks would produce plausible but incorrect data. Page-walk duration events are cycle counts, not miss counts, so metric formulas must avoid treating them as occurrences. Some aliases distinguish demand-load walks from broader load walks, which affects workload interpretation. Virtualization-specific EPT events may be zero on non-virtualized workloads.

## Test Signals
Useful checks include JSON validation, successful perf table generation, `perf list` visibility, and opening representative load, store, instruction, and flush aliases. Runtime sanity tests include increased DTLB walk events under large random memory footprints, lower miss rates with huge pages, ITLB activity under instruction-cache stress, and EPT walk activity in virtualized workloads.
