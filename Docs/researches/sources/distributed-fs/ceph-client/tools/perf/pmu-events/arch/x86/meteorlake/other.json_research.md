# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/other.json

## Purpose

`other.json` is a small Meteor Lake PMU event catalog for hardware events that do not fit the cache, frontend, memory, floating-point, pipeline, virtual-memory, or uncore topic files. It defines eight named event aliases: four for `cpu_core` and four for `cpu_atom`. The file supplies assist, LBR, streaming-write offcore-response, and uncore-request-backpressure events for perf discovery and metric composition.

## Important APIs, Types, And Data

The file uses the normal perf event JSON schema fields `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Unit`, plus optional `Deprecated`, `CounterMask`, `MSRIndex`, and `MSRValue`.

The event set is:

- `ASSISTS.HARDWARE` on `cpu_core`, event `0xc1`, umask `0x4`, for miscellaneous hardware assists or traps not covered by dedicated FP, SSE/AVX mix, or A/D assist sub-events.
- `ASSISTS.PAGE_FAULT` on `cpu_core`, event `0xc1`, umask `0x8`, for page-fault assists.
- `LBR_INSERTS.ANY` on `cpu_atom`, event `0xe4`, umask `0x1`, marked `Deprecated: "1"` and documented as an alias to `MISC_RETIRED.LBR_INSERTS`.
- `OCR.FULL_STREAMING_WR.ANY_RESPONSE` on `cpu_atom`, event `0xB7`, umask `0x1`, offcore response MSRs `0x1a6,0x1a7`, filter value `0x800000010000`.
- `OCR.PARTIAL_STREAMING_WR.ANY_RESPONSE` on `cpu_atom`, event `0xB7`, umask `0x1`, offcore response filter `0x400000010000`.
- `OCR.STREAMING_WR.ANY_RESPONSE` on `cpu_atom`, event `0xB7`, umask `0x1`, offcore response filter `0x10800`.
- `OCR.STREAMING_WR.ANY_RESPONSE` on `cpu_core`, event `0x2A,0x2B`, umask `0x1`, offcore response filter `0x10800`.
- `XQ.FULL_CYCLES` on `cpu_core`, event `0x2d`, umask `0x1`, `CounterMask: "1"`, for cycles when the active thread cannot send more requests to the uncore.

Duplicate `OCR.STREAMING_WR.ANY_RESPONSE` names are intentional because Atom and Core PMUs need different encodings for the same logical alias.

## Control Flow

The JSON has no local executable control flow. During the perf build, `tools/perf/pmu-events/jevents.py` parses each object into a `JsonEvent`. It lowercases `EventName` for generated aliases, maps `Unit` values to PMU names, parses the first event code from comma-separated `EventCode`, emits nonzero `UMask`, `CounterMask`, and `SampleAfterValue` fields into the event string, converts `MSRIndex` values through `lookup_msr()`, and appends the corresponding MSR filter value.

At runtime, perf selects the Meteor Lake table via the x86 mapfile, exposes these aliases through `perf list`, and programs the selected `cpu_core` or `cpu_atom` PMU when a user or metric requests one. For `OCR.*` events, perf must also program the offcore response MSR filter. For `XQ.FULL_CYCLES`, `CounterMask: 1` changes the event into a cycle predicate rather than a simple occurrence count.

## State And Persistence Behavior

This file persists event alias metadata in the source tree and generated perf tables. It owns no runtime state. Counts exist only while perf sessions run and are read from hardware counters. The `Deprecated` flag persists compatibility metadata for `LBR_INSERTS.ANY`; it should remain visible for old users while discouraging new dependencies.

The `MSRIndex` and `MSRValue` fields are persistent semantic state for the offcore-response events. They define which streaming-write requests are counted and must match Meteor Lake hardware documentation. The `SampleAfterValue` fields set default sampling periods and influence interrupt frequency when these events are used for profiling.

## Dependencies And Integration Points

This file integrates with `jevents.py`, generated `pmu-events.c`, `perf list`, perf event parsing, hybrid PMU routing, and any metric expressions that reference these aliases. It depends on kernel support for Meteor Lake `cpu_core` and `cpu_atom` PMUs and on offcore response MSR support for the `OCR.*` aliases.

It is closely related to:

- `mtl-metrics.json`, where assist, streaming store, and request-backpressure events can be used by higher-level metrics.
- `pipeline.json` and `floating-point.json`, which cover adjacent assist and retiring behavior.
- `memory.json` and cache files, which complement the streaming-write and uncore-backpressure view.
- `jevents.py` MSR handling, especially lookup of `0x1a6,0x1a7` as offcore response filters.

## Risks And Edge Cases

The file is small but high-risk because several entries rely on special interpretation. A wrong offcore `MSRValue` silently changes the meaning of streaming-write aliases while leaving the event syntactically valid. The Core `OCR.STREAMING_WR.ANY_RESPONSE` event uses comma-separated event codes `0x2A,0x2B`; `jevents.py` parses the first code for the generated event string, so behavior depends on established parser conventions for such entries.

The duplicate `OCR.STREAMING_WR.ANY_RESPONSE` name must remain separated by `Unit`. Tests that assume unique `EventName` values across the whole file will flag a false positive.

`LBR_INSERTS.ANY` is deprecated and should not be used by new metrics unless compatibility is required. New usage should prefer the replacement alias described in the event text.

`XQ.FULL_CYCLES` uses `CounterMask: 1`, so it measures cycles satisfying a condition. Treating it as a raw request count would produce misleading analysis.

The broad `ASSISTS.HARDWARE` description intentionally covers many assist/trap sources. It is useful as a symptom counter but not a root-cause classifier without more specific assist, pipeline, or workload evidence.

## Test Signals

Useful validation signals include:

- JSON validity: `jq empty sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/other.json`.
- Record sanity: `jq 'length'` should report 8, with four `cpu_core` and four `cpu_atom` entries.
- Schema sanity: every entry should have `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `Unit`, and `BriefDescription`.
- Generated encoding review: representative generated event strings should include the offcore response filter for all `OCR.*` entries and `cmask=1` for `XQ.FULL_CYCLES`.
- Deprecation visibility: `perf list` or generated JSON output should preserve the deprecated status of `LBR_INSERTS.ANY`.
- Runtime smoke: page-fault-heavy workloads should move `ASSISTS.PAGE_FAULT`; non-temporal or streaming-store microbenchmarks should move the `OCR.*STREAMING_WR*` aliases; memory-pressure workloads that saturate outbound requests should move `XQ.FULL_CYCLES`.
- Hybrid routing: `cpu_core` and `cpu_atom` aliases with the same logical name should resolve on the correct PMU domain on a Meteor Lake system.
