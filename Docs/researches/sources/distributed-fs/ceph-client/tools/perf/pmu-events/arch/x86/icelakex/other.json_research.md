# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/other.json

## Purpose

This file defines five miscellaneous Ice Lake Xeon core PMU events that do not fit cleanly into the main cache, pipeline, frontend, virtual-memory, or memory event files. Three events report AVX/turbo license level residency through `CORE_POWER.*`, and two events provide offcore-response aliases for miscellaneous requests and streaming writes with any response.

The events are `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, `CORE_POWER.LVL2_TURBO_LICENSE`, `OCR.OTHER.ANY_RESPONSE`, and `OCR.STREAMING_WR.ANY_RESPONSE`. They support power/frequency analysis and derived store/offcore metrics in `icx-metrics.json`, including AVX license utilization and streaming-store bottleneck estimates.

## Important APIs, Types, And Data

The file uses the standard perf PMU event JSON array schema. Fields include `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `MSRIndex`, `MSRValue`, `BriefDescription`, and `PublicDescription`.

The `CORE_POWER.*` entries share `EventCode 0x28` and counters `0,1,2,3`, with masks `0x7`, `0x18`, and `0x20` for license levels 0, 1, and 2. Their descriptions distinguish baseline/non-AVX and lower-current vector code, high-current AVX2 or low-current AVX-512 behavior, and high-current AVX-512 behavior.

The `OCR.*.ANY_RESPONSE` entries share the offcore response event codes `0xB7, 0xBB`, `UMask 0x1`, counters `0,1,2,3`, and offcore MSRs `0x1a6,0x1a7`. `OCR.OTHER.ANY_RESPONSE` uses `MSRValue 0x18000`; `OCR.STREAMING_WR.ANY_RESPONSE` uses `MSRValue 0x10800`.

## Control Flow

At build time, `jevents.py` parses the five records, converts selector fields into generated event strings, and preserves MSR programming metadata for the offcore entries. At runtime, perf resolves the aliases from the generated Ice Lake Xeon event table.

The power events are counted directly by the core PMU. The offcore entries require perf/kernel handling for the offcore response MSRs, just like the `OCR.*` entries in `memory.json`. Metrics in `icx-metrics.json` can then consume these aliases as formula inputs.

## State And Persistence Behavior

The file stores static metadata only. Runtime residency cycles and offcore request counts are produced by hardware counters during a perf measurement interval. The MSR fields are declarative and are applied when perf opens the event; they are not persistent runtime state in this JSON.

## Dependencies And Integration Points

This file integrates with `icx-metrics.json` power and streaming-store formulas, `jevents.py`, generated `pmu-events.c`, perf alias lookup, and kernel PMU/offcore MSR support. It is selected through the `icelakex` x86 mapfile entry and exposed through `perf list` and `perf stat -e`.

The `CORE_POWER.*` entries are semantically tied to Intel AVX turbo license behavior. The `OCR.*` entries share the same offcore response machinery and risks as `memory.json`.

## Risks And Edge Cases

For power-license events, users can confuse residency in a license level with actual package frequency or throttling; these counters indicate the class of power delivery/turbo schedule in use, not a complete power model. Incorrect masks would swap license levels and mislead AVX frequency analysis.

For `OCR.*.ANY_RESPONSE`, the main risk is MSR filter correctness. The base event selectors are not enough to identify miscellaneous or streaming-write traffic, so `MSRValue` must be preserved. These events may compete with other offcore-response events for limited counters and MSR filter slots.

## Test Signals

Validation includes `jq empty`, `jevents.py` generation, and generated-table checks for masks and MSR metadata. Runtime smoke tests should verify that `perf list` exposes the three `CORE_POWER` aliases and two `OCR` aliases on Ice Lake Xeon tables. Workload tests can compare license-level counts under scalar, AVX2, and AVX-512 kernels, and compare streaming-write counts under non-temporal store workloads.
