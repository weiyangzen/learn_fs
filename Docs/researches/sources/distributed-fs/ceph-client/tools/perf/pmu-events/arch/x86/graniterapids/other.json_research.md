# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/other.json

## Purpose

`other.json` is a Granite Rapids x86 perf PMU event topic file for miscellaneous core events that do not fit the larger pipeline/cache/memory topic files. It is a JSON array of seven event-definition objects consumed by perf's `pmu-events` build pipeline. The entries describe hardware assists, hardware interrupts, streaming write occupancy filtering, and request queue full cycles for the Granite Rapids CPU model directory selected by `arch/x86/mapfile.csv`.

The file does not implement executable logic. Its behavioral role is declarative: each object becomes metadata for a perf event alias, including the event select code, unit mask, usable counters, sample period, descriptions, and optional model-specific MSR filters.

## Important APIs, Types, And Event Fields

Perf's `jevents.py` treats each object as a `JsonEvent`-compatible record. The important fields present here are:

- `EventName`: user-facing symbolic alias, such as `ASSISTS.HARDWARE`, `ASSISTS.PAGE_FAULT`, `HW_INTERRUPTS.RECEIVED`, `OCR.STREAMING_WR.ANY_RESPONSE`, and `XQ.FULL_CYCLES`.
- `EventCode` and `UMask`: raw PMU select and unit mask values translated into perf event configuration.
- `Counter`: allowed programmable counter list. Most entries allow counters `0,1,2,3,4,5,6,7`; `OCR.STREAMING_WR.ANY_RESPONSE` and `XQ.FULL_CYCLES` are constrained to `0,1,2,3`.
- `CounterMask`: only used by `XQ.FULL_CYCLES` to count cycles satisfying a minimum threshold.
- `MSRIndex` and `MSRValue`: used by `OCR.STREAMING_WR.ANY_RESPONSE` to program offcore response filtering through MSRs `0x1a6,0x1a7` with value `0x10800`.
- `SampleAfterValue`: default period hints for sampling.
- `BriefDescription` and `PublicDescription`: short and long descriptions surfaced by perf tooling.

The file's event families are compact: two `ASSISTS.*` records share event code `0xc1`, three `HW_INTERRUPTS.*` records share `0xcb`, the offcore response record uses `0x2A,0x2B`, and `XQ.FULL_CYCLES` uses `0x2d`.

## Control Flow

At build time, `tools/perf/pmu-events/Build` includes JSON and CSV files under `pmu-events/arch`, copies them into the output tree if needed, and runs `pmu-events/jevents.py`. `jevents.py` walks the architecture tree, parses JSON records, lowers event names, converts fields such as `CounterMask` to perf encodings such as `cmask=`, converts `MSRIndex` through its MSR lookup path, and emits `pmu-events.c` tables. The generated object is linked into perf.

At runtime, perf matches the local CPU against `arch/x86/mapfile.csv`; Granite Rapids maps `GenuineIntel-6-A[DE]` to the `graniterapids` directory. Perf then exposes these rows as aliases that users can pass to commands such as `perf stat -e assists.hardware` or equivalent normalized names.

## State And Persistence Behavior

This file is persistent static metadata. It has no runtime mutable state, local cache, or side effects by itself. The only persistence it influences is generated build output (`pmu-events.c` and `pmu-events.o`) and perf's runtime alias table compiled from those generated artifacts. Changes to event encodings or names alter the ABI-like alias surface seen by perf users on Granite Rapids systems.

## Dependencies And Integration Points

The direct dependencies are the perf PMU event schema expected by `jevents.py`, Granite Rapids selection in `arch/x86/mapfile.csv`, and Linux perf code that consumes generated `struct pmu_event` tables. The `OCR.STREAMING_WR.ANY_RESPONSE` record also depends on correct offcore response MSR handling: both the comma-separated event code and the comma-separated MSR index must be understood by the generator and runtime PMU programming path.

The file sits beside topic siblings such as `pipeline.json`, `cache.json`, `memory.json`, and uncore event files. Together they form the complete Granite Rapids event table.

## Risks And Edge Cases

The main risks are data-quality risks. Incorrect `EventCode`, `UMask`, `Counter`, `MSRIndex`, or `MSRValue` values would silently expose misleading aliases. The offcore response entry is higher risk because it uses paired event codes and paired MSRs; a parser or schema regression around comma-separated values could break only this style of event. `ASSISTS.HARDWARE` has a broad public description and overlaps conceptually with more specific assist events in other topic files, so users may misinterpret it as an exhaustive architectural assist counter.

Counter constraints are also important: if `Counter` is widened incorrectly for PDIST/offcore-style events, perf may schedule an event on a counter that cannot support the filter. If narrowed incorrectly, perf may reject valid groups or multiplex more than necessary.

## Test Signals

Useful validation signals are: all JSON parses cleanly with `jq`; `jevents.py` generation succeeds for x86; generated `pmu-events.c` contains aliases for all seven `EventName` values; `perf list` on Granite Rapids includes these names; and a Granite Rapids `perf stat` smoke test can schedule representative events from each family, especially `OCR.STREAMING_WR.ANY_RESPONSE` and `XQ.FULL_CYCLES`. Diffing generated encodings before and after edits is a strong regression check because this file is pure declarative input.
