# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/virtual-memory.json

## Purpose

This 20-entry JSON file defines Sapphire Rapids core virtual-memory PMU aliases for TLB misses and page walks. It covers demand-load DTLB misses, demand-store DTLB misses, and instruction-side ITLB misses, including STLB hits, active or pending page walks, completed walks, and completed walks by page size. The catalog supports perf analysis of translation overhead and page-size effects.

## Important APIs, Types, and Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, and `CounterMask` for active page-walk cycle events. `DTLB_LOAD_MISSES` uses event `0x12`, `DTLB_STORE_MISSES` uses `0x13`, and `ITLB_MISSES` uses `0x11`. Load and store groups include 4K, 2M/4M, and 1G completed-walk variants; instruction fetch lacks a 1G-specific variant here. `WALK_ACTIVE` adds `CounterMask: 1` to count cycles with at least one page miss handler active, while `WALK_PENDING` counts outstanding walks per cycle.

## Control Flow

Perf ingests the static table and exposes aliases for the Sapphire Rapids core PMU. Runtime use programs the specified event and mask on generic counters `0,1,2,3`. Users compare STLB hits, walk-completed counts, and walk-active cycles to determine whether translation misses are frequent, whether large pages are effective, and whether page walking is consuming significant execution time.

## State and Persistence Behavior

The file persists the event encoding and sampling defaults; runtime counter values are per perf event and usually per CPU/thread depending on how perf is invoked. `SampleAfterValue` values provide default sampling periods but do not imply persistent state. Page-walk events may include walks that end with or without faults, so fault attribution requires additional kernel or exception signals. Counter-mask cycle events have different semantics from completed-walk event counts.

## Dependencies and Integration Points

This file integrates with perf core PMU support, `perf stat`, `perf record`, virtual-memory tuning, huge-page investigations, and topdown metrics that include frontend or backend stalls from page walks. It complements Sierra/Sapphire cache and memory events by explaining whether cache misses are accompanied by address-translation bottlenecks.

## Risks

A common risk is mixing event counts and cycle-style occupancy counts in ratios without normalization. Page-size variants are not symmetrical across load/store/instruction groups, so formulas must not assume every group has a 1G instruction event. STLB hits are cheaper than page walks but still indicate first-level TLB pressure. Shared-system noise and kernel activity can affect per-CPU counts. Hardware errata or kernel PMU constraints may affect precise attribution for sampled translation events.

## Test Signals

Validation should include JSON parsing, perf alias listing, and smoke workloads that deliberately thrash data and instruction TLBs. Huge-page and 4K-page variants should shift the relevant `WALK_COMPLETED_*` counts. Sampling tests should verify default periods are accepted. Metric tests should separately validate count-based ratios and cycle-based page-walk residency calculations.
