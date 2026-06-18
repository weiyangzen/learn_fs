# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/memory.json

## Purpose

This file defines 64 Ice Lake Xeon core PMU events focused on memory behavior, offcore responses, L3 miss pressure, transactional memory, and memory ordering. It complements the higher-level metric formulas in `icx-metrics.json` by providing raw event aliases used to diagnose load latency, demand data/code/RFO misses, prefetch traffic, streaming stores, local versus remote DRAM/PMM placement, SNC-local versus SNC-distant memory, outstanding offcore requests, RTM commits and aborts, and TSX abort causes.

The event families are `CYCLE_ACTIVITY`, `MACHINE_CLEARS`, `MEM_TRANS_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `RTM_RETIRED`, `TX_EXEC`, and `TX_MEM`. The largest family is `OCR.*`, with 38 offcore-response aliases that program Intel offcore response MSRs for specific request and response filters.

## Important APIs, Types, And Data

The file uses the perf PMU event JSON schema consumed by `jevents.py`. Fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `MSRIndex`, `MSRValue`, `Data_LA`, `Deprecated`, `BriefDescription`, and `PublicDescription`.

`EventName` is the user-facing alias. `EventCode`, `UMask`, `Counter`, and optional `CounterMask` become the perf config string. `SampleAfterValue` provides default sampling periods, commonly `100003` for memory and offcore events, `200003` for transactional events, and `1000003` for `TX_EXEC` entries. `MSRIndex` and `MSRValue` are critical for `OCR.*` and `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`: they program offcore response MSRs `0x1a6,0x1a7` or load-latency MSR `0x3F6`. `Data_LA` on load-latency entries marks load-address precise sampling support. `Deprecated` marks `OFFCORE_REQUESTS_OUTSTANDING.L3_MISS_DEMAND_DATA_RD` as a compatibility alias that should no longer be preferred.

The load-latency family uses `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_4`, `_8`, `_16`, `_32`, `_64`, `_128`, `_256`, and `_512` with the same event selector and different MSR latency thresholds. The offcore-response aliases distinguish demand code reads, demand data reads, demand RFOs, L1D/software prefetches, L3 hardware prefetches, ITOMs, miscellaneous traffic, all prefetches, reads to core, streaming writes, and write-estimate traffic across DRAM, PMM/remote memory, local/remote sockets, and SNC-specific placement.

## Control Flow

At build time, `jevents.py` parses the JSON array into generated PMU event entries for the Ice Lake Xeon table. It lowercases aliases, converts `EventCode` and `UMask` into event config fields, preserves `CounterMask` as `cmask`, preserves default periods, and records MSR programming requirements.

At runtime, `perf list` displays these aliases. `perf stat -e` or metrics from `icx-metrics.json` can request the aliases, after which perf resolves them to PMU events and asks the kernel to program the hardware counter and any required offcore/load-latency MSR filter. For `OCR.*`, the same base event code pair `0xB7, 0xBB` and `UMask 0x1` is specialized almost entirely through `MSRValue`, so correct runtime behavior depends on preserving that extra register programming metadata.

## State And Persistence Behavior

The JSON file persists static event metadata only. Runtime counter values, load-latency samples, TSX abort counts, and offcore response counts live in hardware PMU state and perf file descriptors. MSR filters are not persisted by this file at runtime; they are declarative fields that perf applies when the event is opened.

`Deprecated` is persistent metadata for user-facing compatibility. It keeps an older alias visible while signaling that `OFFCORE_REQUESTS_OUTSTANDING.L3_MISS_DEMAND_DATA_RD_GE_6` or `CYCLES_WITH_L3_MISS_DEMAND_DATA_RD` provide clearer semantics.

## Dependencies And Integration Points

This file integrates with `icx-metrics.json`, especially memory bandwidth, latency, NUMA, store, streaming-store, and top-down memory-bound formulas. It also integrates with `jevents.py`, generated `pmu-events.c`, perf alias lookup, kernel x86 PMU support for Ice Lake server, offcore response MSR handling, precise load-latency sampling support, and TSX event availability.

The model mapping in `arch/x86/mapfile.csv` selects this directory for Ice Lake Xeon model IDs. User-facing paths include `perf list`, `perf stat -e OCR.*`, `perf mem`-style workflows where precise load address matters, and `perf stat -M` metrics that indirectly expand these events.

## Risks And Edge Cases

The highest risk is incorrect MSR filter metadata. Most `OCR.*` entries share event selectors, so a wrong `MSRValue` silently counts the wrong request or response class. SNC, local socket, remote socket, DRAM, PMM, and CXL-style memory distinctions are topology-sensitive; descriptions must remain precise because the same alias can mean different locality scopes when Sub-NUMA Cluster mode is enabled.

Load-latency events use randomized load selection and threshold MSR programming, so users can misread them as exact counts of all loads above a threshold. TSX events may be unavailable or disabled on some systems. Deprecated aliases should remain parseable but should not be used as the preferred semantic source. Counter masks on outstanding-request events distinguish "at least one" from "at least six" outstanding L3-miss demand reads; losing `CounterMask` changes event meaning.

## Test Signals

Validation includes `jq empty`, x86 `jevents.py` generation, `perf test pmu-events`, and generated event-string inspection for `MSRIndex`/`MSRValue`, `CounterMask`, `Data_LA`, and `Deprecated`. Runtime smoke tests should check `perf list` visibility for representative aliases such as `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128`, `OCR.DEMAND_DATA_RD.LOCAL_DRAM`, `OCR.READS_TO_CORE.REMOTE_MEMORY`, `OFFCORE_REQUESTS_OUTSTANDING.L3_MISS_DEMAND_DATA_RD_GE_6`, `RTM_RETIRED.START`, and `TX_MEM.ABORT_CONFLICT`.

Behavioral checks should run memory-locality and memory-bandwidth workloads, pointer-chasing latency tests, TSX tests on TSX-capable systems, and SNC or multi-socket locality tests where hardware is available. For non-hardware CI, generated-table and alias-expansion tests are the main signal.
