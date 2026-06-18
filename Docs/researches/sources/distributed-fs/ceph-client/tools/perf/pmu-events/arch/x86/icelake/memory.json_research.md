# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/memory.json

## Purpose

This file is the Ice Lake client memory and transactional-memory event catalog for perf. It contains 60 raw event records covering L3-miss cycles and stalls, Hardware Lock Elision and RTM transaction starts/commits/aborts, memory-ordering machine clears, load-latency thresholds, offcore response categories, L3-miss demand-data requests, outstanding L3 misses, and transactional abort causes.

## Important APIs, Types, And Data

The records use the perf event JSON schema: `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `MSRIndex`, `MSRValue`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Important families are `CYCLE_ACTIVITY`, `HLE_RETIRED`, `MACHINE_CLEARS`, `MEM_TRANS_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `RTM_RETIRED`, `TX_EXEC`, and `TX_MEM`.

The `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` entries share event `0xcd` and use `MSRIndex` `0x3F6` with threshold-specific `MSRValue` values from `0x4` through `0x200`. The `OCR.*` entries share offcore response event selectors `0xB7, 0xBB` and program offcore MSRs `0x1a6,0x1a7` with response masks for demand code reads, demand data reads, RFO, L1D/software prefetch, L2 data reads, L2 RFO, other requests, and streaming writes against DRAM, local DRAM, or L3-miss responses. `CYCLE_ACTIVITY.*` and outstanding-request events use `CounterMask` to count cycles meeting stall or miss thresholds.

## Control Flow

During perf build, `jevents.py` parses each memory event record into generated PMU event-table entries. Event selector, umask, counter mask, sample period, and offcore or latency MSR programming fields are carried into generated config strings. At runtime, perf resolves aliases from the compiled table and programs the CPU PMU and any required extra MSR filters before reading or sampling the counter.

Metrics in `icl-metrics.json` then use these raw events to derive memory-bound, DRAM-bound, L3-bound, memory bandwidth, memory latency, synchronization, data sharing, contested access, store bound, false sharing, and transactional diagnostics.

## State And Persistence Behavior

The file persists static memory-event metadata and default sample periods only. Runtime state includes hardware counter values, offcore-response MSR state, latency-threshold MSR state, and perf aggregation state. Transactional-memory events reflect CPU execution state only while measured; no transaction state is persisted in the JSON.

## Dependencies And Integration Points

This file integrates with Ice Lake model selection, `jevents.py`, generated `pmu-events.c`, perf event alias resolution, and metrics that reference `CYCLE_ACTIVITY.STALLS_L3_MISS`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, `OCR.*`, `OFFCORE_REQUESTS.*`, `RTM_RETIRED.*`, `HLE_RETIRED.*`, and `TX_MEM.*`. It depends on kernel support for programming offcore response MSRs and on the raw event encodings matching Ice Lake client hardware.

## Risks And Edge Cases

Offcore response events are the highest-risk area because one alias requires both normal PMU selector fields and model-specific MSR response masks. Incorrect `MSRValue` can produce plausible but wrong traffic categories. `LOCAL_DRAM` and `DRAM` masks are identical in this file for several request classes, which may be intentional for this model but is easy to misread during edits. Transactional-memory events may be unsupported or low-value on systems where TSX is disabled by firmware, microcode, or kernel policy. Counter masks convert events into cycle counts rather than occurrence counts, and multiplexing can skew derived memory-bound metrics.

## Test Signals

Use `jq empty memory.json`, x86 `jevents.py` generation, `perf test pmu-events`, and generated-table inspection for `offcore_rsp`/MSR fields. Runtime validation includes pointer-chasing or memory-bandwidth workloads for L3/DRAM metrics, checks that `mem_trans_retired.load_latency_gt_64` and related thresholds are visible in `perf list`, and TSX-focused tests only on systems where HLE/RTM are enabled. Metric tests should verify that `MemoryBW`, `MemoryLat`, `Offcore`, and `LockCont` groups still expand.
