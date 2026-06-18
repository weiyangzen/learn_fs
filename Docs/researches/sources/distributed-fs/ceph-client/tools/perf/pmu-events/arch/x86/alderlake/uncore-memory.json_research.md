# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/uncore-memory.json

## Purpose

This 25-entry catalog defines Alder Lake uncore memory-controller events. It includes free-running read/write CAS counters for memory controllers 0 and 1, standard integrated-memory-controller request and CAS counts, activation counts, clock ticks, page empty/hit/miss classifications, thermal warm/hot events, precharge/page-miss counts, prefetch reads, and virtual-channel read/write request counts. The file is package-level memory subsystem data for perf.

## Important APIs, Types, and Data

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and optional `PublicDescription`. Units are `iMC` for 21 normal memory-controller events plus `imc_free_running_0` and `imc_free_running_1` for four free-running controller-specific counters. All records are `PerPkg: 1`. Families include `UNC_M_CAS_COUNT_*`, `UNC_M_ACT_COUNT_*`, `UNC_M_DRAM_PAGE_*`, `UNC_M_DRAM_THERMAL_*`, `UNC_M_PREFETCH_RD`, `UNC_M_PRE_COUNT_*`, and `UNC_M_VC*`.

## Control Flow

Perf ingests the JSON as uncore event metadata and exposes package-level memory-controller aliases. At runtime, normal `iMC` events are programmed through memory-controller PMU counters, while `imc_free_running_0/1` entries use free-running counter units with fixed counter `0`. Aggregation is package-level, not per-thread. Users or metrics often normalize CAS counts to bytes by multiplying by cache-line width or compare read/write/page events to memory bandwidth and locality expectations.

## State and Persistence Behavior

The persistent state is the mapping from uncore memory aliases to event encodings and units. Runtime counts persist only for the duration of the perf session and are shared across the package. Free-running counters may have different reset/read semantics from normal programmable counters, so the unit distinction is part of the persistent behavior contract. `PerPkg` prevents accidental per-CPU interpretation.

## Dependencies and Integration Points

This file integrates with perf uncore support, memory-bandwidth metrics, DRAM page-locality analysis, thermal diagnostics, and package-level `perf stat` workflows. It depends on kernel support for Alder Lake iMC and imc free-running PMUs. It complements core memory/cache events by measuring actual controller traffic rather than core-side misses or offcore request filters.

## Risks

Uncore memory PMU availability may vary by SKU, firmware, and kernel. Free-running counters and programmable iMC counters have different scheduling and overflow behavior. CAS-to-bandwidth formulas must account for the 64-byte request granularity described by the free-running events and should avoid double-counting controller 0 and 1. Package-level counts are vulnerable to noise from unrelated processes and other cores. Thermal events can be sparse and platform-policy dependent.

## Test Signals

Validation should include JSON parsing, `perf list` uncore-memory aliases, smoke bandwidth tests with streaming reads and writes, comparison of read/write CAS counts against expected bytes, page hit/miss sensitivity tests, and checks that free-running controller units are exposed separately from normal `iMC` events. Aggregation tests should verify one package-level result per package rather than per logical CPU.
