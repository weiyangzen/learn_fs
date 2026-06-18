# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/other.json

## Purpose

`other.json` defines 21 Lunar Lake PMU events that do not fit the main cache, pipeline, or virtual-memory topic files. It covers hardware assists and page-fault assists on `cpu_core`, bus-lock behavior on `cpu_atom`, dynamic L2 prefetch throttling levels on `cpu_atom`, offcore response request filters for streaming writes, a core `XQ.FULL` occupancy/stall event, and atom-side prefetch-to-demand promotion events.

## Important APIs, Types, And Data Shape

The file is a JSON array of event objects. Core schema keys are `EventName`, `Unit`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. Some entries add `CounterMask`, `MSRIndex`, and `MSRValue`. `OCR.*` events use `MSRIndex` values `0x1a6,0x1a7` to program offcore response filters, while `XQ.FULL` uses `CounterMask: "1"`. The same logical name `OCR.STREAMING_WR.ANY_RESPONSE` appears twice, once for `cpu_atom` with event `0xB7` and once for `cpu_core` with events `0x2A,0x2B`; `Unit` is therefore part of the identity.

## Control Flow

During build generation, `jevents.py` reads the array with `read_json_events()`, creates `JsonEvent` instances, lowercases event names, maps `Unit` to the perf PMU name, converts event fields to config strings, and emits rows into the Lunar Lake event table. At runtime, perf resolves user names such as `assists.hardware`, `bus_lock.split_locks`, or `ocr.streaming_wr.any_response` against the PMU exposed by the running hybrid CPU.

## State And Persistence

No mutable state exists in the JSON. Persistent effects are generated event aliases and encoded MSR filter values compiled into perf. Runtime collection state is held by perf and the kernel PMU driver when counters are opened.

## Dependencies And Integration Points

This file depends on hybrid PMU naming (`cpu_core` and `cpu_atom`), Intel offcore response MSR programming, and the generic perf JSON event schema. It integrates with `jevents.py`, generated `pmu-events.c`, `perf list`, `perf stat`, and tests that compare generated `struct pmu_event` records. The topic is inferred from the filename as `other`.

## Risks

The highest-risk entries are the `OCR.*` filters because a bad `MSRValue` silently changes the memory transaction class being counted. Duplicate names across units must remain intentionally separated. Bus-lock and prefetch-throttler entries are atom-only; exposing them as core events would produce invalid aliases on P-cores. `PublicDescription` wording for assists is broad and includes several hardware mechanisms, so downstream metrics should avoid treating it as a single root cause.

## Test Signals

Validation should include `jq type` returning `array`, length 21, all entries having `EventName` and `Unit`, and successful generator output. Runtime signals include `perf list other` on Lunar Lake, `perf stat -e cpu_atom/bus_lock.split_locks/` on an atom-capable system, and offcore filter smoke tests that confirm `ocr.streaming_wr.any_response` is present for both hybrid units.
