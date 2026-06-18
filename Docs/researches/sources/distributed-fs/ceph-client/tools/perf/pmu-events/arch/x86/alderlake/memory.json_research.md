# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/memory.json

## Purpose

This 38-entry file describes Alder Lake memory-latency and offcore memory PMU events for perf. It covers stalls while cache misses are outstanding, load-head classifications at retirement, memory-ordering machine clears, L1D/L2/L3 miss stalls, retired load-latency thresholds, store sampling, offcore response demand-code/data/RFO/prefetch DRAM and L3-miss filters, and outstanding L3-miss demand reads. The unit split is 21 `cpu_core` records and 17 `cpu_atom` records.

## Important APIs, Types, and Data

Entries use the standard event schema plus `CounterMask`, `Data_LA`, `MSRIndex`, and `MSRValue`. Ten entries have `Data_LA`, mostly load-latency threshold and store-sample records where sampled data addresses are useful. Twenty-two entries use MSR filters, including load-latency MSR `0x3F6` and offcore response MSRs `0x1a6,0x1a7`. Event families include `CYCLE_ACTIVITY`, `LD_HEAD`, `MACHINE_CLEARS`, `MEMORY_ACTIVITY`, `MEM_TRANS_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, and `OFFCORE_REQUESTS_OUTSTANDING`.

## Control Flow

There are no local functions. Perf converts the JSON into event aliases, then resolves user or metric requests into PMU programming. Load-latency events require perf to combine a base retired-memory event with a latency threshold selector. Offcore events require extra MSR programming that chooses request type and response class. During sampling, `Data_LA` can influence whether address data is requested and exposed in samples.

## State and Persistence Behavior

The file persists semantic names and hardware encodings. Runtime state is held in perf event descriptors, PMU counters, PEBS/sample buffers, and model-specific registers. Threshold values in `MSRValue` are durable source data; altering one changes the meaning of aliases such as `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128`. The same is true for offcore response masks that distinguish DRAM, L3 miss, and local miss categories.

## Dependencies and Integration Points

This file integrates with perf's memory metrics, topdown memory-bound analysis, load-latency profiling, `perf mem`-adjacent workflows, and offcore bandwidth/latency formulas. It depends on Alder Lake PMU support for PEBS/data address capture, latency-threshold MSR programming, offcore-response MSR programming, and hybrid unit routing. It overlaps with `cache.json` because both contain memory hierarchy and offcore response signals, but this file emphasizes latency/stall diagnosis rather than broad cache request accounting.

## Risks

MSR filter mistakes are high impact because they silently count a different memory class. `Data_LA` does not guarantee address sampling is available for every mode, privilege level, or kernel version. Load-latency threshold events are cumulative-style predicates; formulas must handle overlapping thresholds deliberately. Some event names appear with both core and atom encodings, and some have local/DRAM wording that may not map identically across PMUs. Counter masks on stall events can also turn simple-looking events into cycle-qualified predicates.

## Test Signals

Validation should include JSON/schema checks, generated MSR field checks, `perf list` coverage, and smoke measurements on pointer-chasing, streaming read/write, cache-contained, and store-heavy workloads. Tests should verify that load-latency aliases program MSR `0x3F6` with the intended thresholds, offcore aliases program `0x1a6/0x1a7`, and metrics referencing memory events either provide both core and atom paths or fail clearly when a PMU lacks the needed alias.
