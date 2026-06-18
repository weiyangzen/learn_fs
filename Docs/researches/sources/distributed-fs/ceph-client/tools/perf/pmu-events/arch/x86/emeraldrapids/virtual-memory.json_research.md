# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/virtual-memory.json

## Purpose

`virtual-memory.json` defines 20 Emerald Rapids core PMU events for data and instruction TLB misses, second-level TLB hits, page-walk completions by page size, page-walk active cycles, and outstanding page-walk pressure. It supports perf analysis of translation overhead for loads, stores, and instruction fetches.

## Important APIs, Types, and Data Fields

The file is a JSON event array using `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and optional `CounterMask`. Event families are `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, and `ITLB_MISSES.*`. Load and store families include `STLB_HIT`, `WALK_ACTIVE`, `WALK_COMPLETED`, `WALK_COMPLETED_1G`, `WALK_COMPLETED_2M_4M`, `WALK_COMPLETED_4K`, and `WALK_PENDING`. ITLB has the same shape except no 1G-specific completion row. `WALK_ACTIVE` rows use `CounterMask: 1`.

## Control Flow and Data Flow

Perf parses the metadata into event aliases and programs core counters when users request those aliases. At runtime, STLB-hit rows count first-level TLB misses resolved by the second-level TLB, walk-completed rows count misses that trigger completed page walks, walk-active rows count cycles with at least one busy page miss handler, and walk-pending rows count outstanding walks per cycle. Data flows from CPU translation hardware into perf samples or counts.

## State and Persistence Behavior

The file stores only static event definitions and default sampling periods. It does not store TLB contents, page tables, address mappings, or samples. Counters are per-core PMU events, so measured state is interval-local and workload/scheduling dependent.

## Dependencies and Integration Points

The definitions depend on Emerald Rapids core PMU event encodings and perf's x86 PMU event-table generator. They integrate with `perf stat`, `perf record`, page-size tuning, huge-page validation, TLB miss analysis, instruction-cache/front-end investigations, and memory-latency studies. The rows complement cache and uncore-memory catalogs by explaining translation cost before memory requests reach cache or memory-controller analysis.

## Risks and Edge Cases

`WALK_ACTIVE` and `WALK_PENDING` share the same event/umask shape but differ by counter-mask semantics, so generated metadata must preserve `CounterMask`. Walk-completed counts and walk-active cycles are different units. Page-size-specific rows should not be interpreted as interchangeable; 4K, 2M/4M, and 1G rows signal different mappings. Page walks can complete with or without a fault according to the descriptions. ITLB and DTLB events are separate and need workload-specific interpretation.

## Test Signals

Validation should include JSON parsing, perf event generation, and `perf list` visibility for all three families. Random-access memory workloads should increase DTLB load/store walk counters. Huge-page workloads should shift counts from 4K toward large-page rows. Code-footprint or branch-heavy instruction-fetch workloads should exercise ITLB events. Tests should check that `WALK_ACTIVE` produces cycle-like behavior while `WALK_COMPLETED` produces event counts.
