# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/memory.json

## Purpose

`memory.json` defines 3 Goldmont core PMU events for memory-ordering machine clears and page-split retired memory operations. It focuses on correctness and alignment pathologies rather than general cache hit/miss behavior.

## Important APIs, Types, and Data Fields

Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and optional `PEBS`. Events are `MACHINE_CLEARS.MEMORY_ORDERING`, `MISALIGN_MEM_REF.LOAD_PAGE_SPLIT`, and `MISALIGN_MEM_REF.STORE_PAGE_SPLIT`. The load and store page-split events are precise-capable (`PEBS: 2`).

## Control Flow and Data Flow

Perf converts the rows into Goldmont event aliases and programs core PMU counters. Runtime data distinguishes machine clears caused by uncertain memory ordering from retired load/store uops that span a page boundary. The page-split rows can support precise sampling to locate offending instructions.

## State and Persistence Behavior

The JSON stores only static definitions and sampling defaults. Runtime machine-clear counts and page-split samples are not persisted here. PEBS records, when collected, are written by perf to its output stream.

## Dependencies and Integration Points

The file depends on Goldmont core PMU and PEBS support. It integrates with memory-ordering diagnostics, alignment tuning, page-layout analysis, and perf sampling workflows. It complements `cache.json` retired memory-uop rows and `virtual-memory` style TLB/page-walk analysis by identifying split accesses that cross page boundaries.

## Risks and Edge Cases

Page splits are not the same as cache-line splits; this file specifically tracks page-boundary splits. The machine-clear event can be affected by multicore snoop behavior and may not point to a single local instruction without corroborating samples. PEBS support is required for precise attribution of page-split load/store rows.

## Test Signals

Validation should include JSON parsing and perf alias visibility. Microbenchmarks with deliberately page-crossing loads and stores should increase the split rows. Multicore memory-sharing tests can exercise memory-ordering clears. PEBS tests should verify precise attribution for split load/store instructions where supported.
