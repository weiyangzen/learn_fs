<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-memory.json

## Purpose

`uncore-memory.json` defines 6 Tiger Lake integrated memory-controller free-running PMU events. It exposes read CAS counts, write CAS counts, and total request counts for two memory-controller free-running units, allowing perf to estimate DRAM read/write traffic and aggregate memory-controller request pressure.

## Important APIs, Types, and Data Fields

The file is a JSON event array using `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. All entries use `EventCode: 0xff` and `PerPkg: 1`. The first controller uses `Unit: imc_free_running_0` with counters `0`, `1`, and `2`; the second uses `Unit: imc_free_running_1` with counters `3`, `4`, and `5`.

The six aliases are `UNC_MC0_TOTAL_REQCOUNT_FREERUN`, `UNC_MC0_RDCAS_COUNT_FREERUN`, `UNC_MC0_WRCAS_COUNT_FREERUN`, `UNC_MC1_TOTAL_REQCOUNT_FREERUN`, `UNC_MC1_RDCAS_COUNT_FREERUN`, and `UNC_MC1_WRCAS_COUNT_FREERUN`. Read and write CAS entries describe 64-byte DRAM transfers. Total request entries count 64-byte read and write requests entering the memory controller, with a note that same-cache-line full and partial writes can be combined into one 64-byte DRAM transfer.

## Control Flow and Data Flow

There is no executable flow. Perf parses the metadata into IMC free-running aliases, then maps selected aliases to the appropriate free-running counter. Data flows from memory-controller hardware counters to perf counts. Analysis usually sums the controller 0 and controller 1 read/write events, then multiplies CAS counts by 64 bytes and divides by measurement time to derive bandwidth.

## State and Persistence Behavior

The source file stores static counter metadata only. Runtime free-running counters may be continuously advancing hardware counters, and perf reads deltas over the measurement interval. Counts are package-scoped and memory-controller-scoped, not process-local. The file does not persist bandwidth calculations or sampled data.

## Dependencies and Integration Points

The catalog depends on Tiger Lake IMC free-running PMU support and perf's uncore event-table generation. It integrates with memory bandwidth metrics in `tgl-metrics.json`, `perf stat` memory studies, and uncore interconnect events that measure request pressure before memory-controller service. The event naming and `Unit` values must match kernel PMU names for the free-running IMC devices.

## Risks and Edge Cases

The fixed counter mapping is the critical risk: each alias is tied to a specific free-running counter number, and a bad counter assignment would silently report the wrong channel/controller statistic. Package-level aggregation can include unrelated system traffic. CAS-to-bandwidth conversion assumes 64-byte transfers, while total request count has write-combining semantics that differ from CAS counts. Systems without matching free-running IMC PMUs may expose none of these aliases.

## Test Signals

Checks should include JSON parsing, generated perf tables, and `perf list` visibility for `imc_free_running_0` and `imc_free_running_1` aliases. Runtime smoke tests should show read CAS counters moving under read-heavy streams, write CAS counters moving under write-heavy streams, and low deltas at idle. A bandwidth sanity test should compare summed CAS-derived GB/s against another trusted memory bandwidth source within expected platform variance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-memory.json -->
