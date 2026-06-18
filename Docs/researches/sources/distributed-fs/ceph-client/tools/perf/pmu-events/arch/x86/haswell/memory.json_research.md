# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/memory.json

## Purpose

This file defines 60 Haswell core PMU memory and transactional-memory events. It covers HLE and RTM retirement, transactional abort causes, memory-ordering machine clears, misaligned memory references, load-latency thresholds, and offcore-response L3-miss/local-DRAM classifications.

## Important APIs, Types, And Data

The records use the perf event JSON schema: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, optional `PEBS`, and descriptions. The file has no `Unit`, so entries are generated for the default core PMU selected by the Haswell mapfile.

Major event families are `HLE_RETIRED` with 8 entries, `RTM_RETIRED` with 8, `TX_EXEC` with 5, `TX_MEM` with 7, `MEM_TRANS_RETIRED` with 8 load-latency threshold events from greater-than-4 through greater-than-512 cycles, `MISALIGN_MEM_REF`, `MACHINE_CLEARS.MEMORY_ORDERING`, and 21 `OFFCORE_RESPONSE.*.L3_MISS.*` aliases covering demand, prefetch, code, data, RFO, all-reads, and all-requests views. PEBS is used where precise sampling is supported, notably memory transaction latency.

## Control Flow

During perf build generation, `jevents.py` reads each entry, lowercases the event alias, converts `EventCode` and nonzero `UMask` into perf event config strings, preserves sample periods, and records PEBS precision hints. The generated Haswell event table is then selected at runtime for matching Haswell CPU models.

At runtime, perf aliases from this file are used by direct `perf stat -e` or `perf record -e` requests and by metrics in `hsw-metrics.json`. Offcore response aliases are translated into event selectors plus offcore response match fields by the perf event generation path.

## State And Persistence Behavior

The file persists static event metadata. Transactional state, abort causes, load latencies, and offcore responses are measured by hardware during a perf run. `SampleAfterValue` persists as a default sampling period, while users may override sampling and counting behavior.

## Dependencies And Integration Points

Integration points include Haswell model selection, `jevents.py`, perf alias lookup, TSX/HLE hardware support, PEBS support for precise memory events, offcore response MSR encoding, and the Haswell metrics file. Memory-bound and data-sharing top-down metrics depend on aliases such as `MEM_TRANS_RETIRED.*`, `OFFCORE_RESPONSE.*`, `MEM_LOAD_UOPS_*`, and transactional abort events.

## Risks And Edge Cases

TSX/HLE events may be unavailable or disabled by microcode/kernel policy even on Haswell-family systems, so aliases can exist while counters are not useful. Offcore-response events are encoding-sensitive and can be easy to misclassify because request type and response type are both embedded in the alias. Load-latency threshold events are not equivalent to average latency; they count retired load events passing a threshold. PEBS hints must match hardware precision support or sampling users can get misleading expectations.

## Test Signals

Validate with `jq empty`, x86 PMU event generation, and `perf test pmu-events`. Runtime tests can use pointer-chasing or memory-load-latency workloads for `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, TSX-capable microbenchmarks for `RTM_RETIRED` and `HLE_RETIRED`, and memory-locality workloads for `OFFCORE_RESPONSE.*.LOCAL_DRAM` versus `.ANY_RESPONSE`.
