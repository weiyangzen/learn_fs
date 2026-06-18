# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/cache.json lines 13382-13416

## Scope

This chunk covers the final five entries in the Cascade Lake X `cache.json` PMU event table:

- `SW_PREFETCH_ACCESS.ANY`
- `SW_PREFETCH_ACCESS.NTA`
- `SW_PREFETCH_ACCESS.PREFETCHW`
- `SW_PREFETCH_ACCESS.T0`
- `SW_PREFETCH_ACCESS.T1_T2`

The selected range begins inside the `SW_PREFETCH_ACCESS.ANY` object, so the preceding chunk owns that record's opening fields. The complete object is visible by reading the adjacent lines: it uses `EventCode` `0x32`, `Counter` `0,1,2,3`, `SampleAfterValue` `2000003`, and `UMask` `0xf`. The remaining four objects are complete in this range and close the top-level JSON array.

This is declarative PMU metadata, not executable runtime logic. Its semantics are consumed by perf's PMU event generation pipeline and by metric expressions that reference these event names.

## Purpose

The covered records expose hardware counter encodings for software prefetch instructions retired or executed on Cascade Lake X class Intel CPUs. They let users and perf metrics distinguish:

- all supported software prefetches together via `SW_PREFETCH_ACCESS.ANY`;
- non-temporal prefetch instructions via `SW_PREFETCH_ACCESS.NTA`;
- write-intent prefetches via `SW_PREFETCH_ACCESS.PREFETCHW`;
- temporal prefetches targeting T0 via `SW_PREFETCH_ACCESS.T0`;
- temporal prefetches targeting T1 or T2 via `SW_PREFETCH_ACCESS.T1_T2`.

All five records share event selector `0x32` and differ by unit mask. The `ANY` record is the aggregate mask `0xf`, while the individual masks are `0x1`, `0x8`, `0x2`, and `0x4`. This makes `ANY` equivalent to the bitwise union of the four subtype events represented here.

## Important Data Shape and APIs

Each record is a JSON object using the common perf PMU event schema:

- `EventName` is the symbolic name used by `perf list`, metric formulas, and users invoking `perf stat -e`.
- `BriefDescription` is the short text exposed in generated event metadata.
- `EventCode` is the raw architectural or model-specific event selector. Here it is always `0x32`.
- `UMask` selects the prefetch subtype. Here `0xf` is the aggregate mask, `0x1` is NTA, `0x8` is PREFETCHW, `0x2` is T0, and `0x4` is T1/T2.
- `Counter` limits these events to programmable counters `0,1,2,3`.
- `SampleAfterValue` supplies the generated default sampling period. These records use `2000003`.

The important consumer API is the perf PMU event generator in `tools/perf/pmu-events/jevents.py`. Its JSON event parsing lowercases `EventName`, converts `EventCode` to an `event=` config field, and maps `UMask` and `SampleAfterValue` into generated perf event terms (`umask=` and `period=`). The result is compiled into generated PMU event tables that perf uses for model-specific event lookup.

The events are also referenced by metrics. `tools/perf/pmu-events/arch/x86/cascadelakex/clx-metrics.json` defines `tma_info_inst_mix_ipswpf` as `INST_RETIRED.ANY / SW_PREFETCH_ACCESS.ANY`. `tools/perf/pmu-events/intel_metrics.py` builds a software prefetch metric group from `SW_PREFETCH_ACCESS.NTA`, `SW_PREFETCH_ACCESS.T0`, `SW_PREFETCH_ACCESS.T1_T2`, and `SW_PREFETCH_ACCESS.PREFETCHW`.

## Control Flow

There is no direct control flow in this chunk. Runtime behavior is supplied by perf's generated event lookup path:

1. The PMU event build step reads `arch/x86/mapfile.csv`, which maps Intel family/model pattern `GenuineIntel-6-55-[56789ABCDEF]` to the `cascadelakex` event directory.
2. `jevents.py` parses `cache.json` along with the other Cascade Lake X JSON files.
3. For each object in this chunk, `JsonEvent` turns the fields into a generated event descriptor.
4. At perf runtime, model matching selects the Cascade Lake X table for matching CPUs.
5. `perf list`, `perf stat`, metric evaluation, and other PMU event consumers resolve `SW_PREFETCH_ACCESS.*` names through that generated table.

For command-line use, a name such as `SW_PREFETCH_ACCESS.T0` resolves to event selector `0x32` plus unit mask `0x2` on counters that can host this event. Metric formulas reuse the same symbolic names rather than duplicating raw event encodings.

## State and Persistence

This file stores persistent source metadata for PMU events. It does not hold mutable state, runtime counters, cached values, or local configuration.

The persistent contract is the mapping between symbolic event names and raw event encodings. If `UMask`, `EventCode`, or `EventName` changes here, the generated PMU table and any metric formulas using these names change behavior after regeneration or rebuild. The closing `]` at line 13416 also makes this chunk structurally important: malformed edits here can invalidate the entire `cache.json` array, not only these five events.

The chunk was validated as part of a syntactically valid JSON file with 13,416 lines. The formatted line count from `python3 -m json.tool` remained 13,416, which is a useful signal that this tail range is well-formed and consistently indented.

## Dependencies and Integration Points

Primary dependencies and integration points:

- `tools/perf/pmu-events/arch/x86/mapfile.csv` selects the `cascadelakex` model directory for Intel family 6 model 55 stepping ranges listed in the map.
- `tools/perf/pmu-events/jevents.py` parses these records and emits generated PMU event tables.
- `tools/perf/pmu-events/arch/x86/cascadelakex/clx-metrics.json` uses `SW_PREFETCH_ACCESS.ANY` in the `tma_info_inst_mix_ipswpf` metric.
- `tools/perf/pmu-events/intel_metrics.py` expects the subtype names `NTA`, `T0`, `T1_T2`, and `PREFETCHW` when constructing the generic Intel software prefetch metric group.
- `tools/perf/tests/pmu-events.c` and `tools/perf/tests/parse-metric.c` are the nearby validation surfaces for generated event tables and metric parsing.

The event naming is cross-model consistent. Similar `SW_PREFETCH_ACCESS.*` records appear in multiple other x86 model directories, and several model metric files use the same `INST_RETIRED.ANY / SW_PREFETCH_ACCESS.ANY` expression. That consistency is useful for reusable Intel metrics but raises the cost of accidental renames in one model directory.

## Risks

- The range starts mid-object. A chunk-level review that reads only line 13382 onward could miss the opening fields of `SW_PREFETCH_ACCESS.ANY`; the adjacent lines confirm its name, counter list, event code, and description.
- The `ANY` mask must remain the union of the subtype masks. If a subtype is added, removed, or corrected without updating `0xf`, aggregate software prefetch metrics will diverge from the sum of the individual events.
- Metric formulas depend on exact event names. Renaming `T1_T2` or `PREFETCHW`, changing case conventions, or replacing `ANY` with explicit subevent sums can break metric parsing or alter output names.
- All events are constrained to counters `0,1,2,3`. If the hardware constraint is wrong, perf may schedule the event on an unsupported counter or reject valid scheduling opportunities.
- `SampleAfterValue` is uniform across the five records. An incorrect period would not affect basic `perf stat` counts but can affect sampling defaults and comparisons against neighboring model data.
- Because this is the file tail, missing commas, an omitted closing brace, or an omitted closing array bracket would invalidate the whole event file.
- The brief descriptions say the events count instructions executed. If hardware documentation defines a different retirement or execution point for Cascade Lake X, users may misinterpret prefetch intensity metrics even when raw encodings are correct.

## Test and Validation Signals

Useful validation signals for this chunk include:

- Parse the source file with a strict JSON parser, for example `python3 -m json.tool tools/perf/pmu-events/arch/x86/cascadelakex/cache.json`.
- Regenerate or build perf PMU event tables and verify the generated Cascade Lake X table contains all five `sw_prefetch_access.*` events with event `0x32`, masks `0xf`, `0x1`, `0x8`, `0x2`, and `0x4`, and period `2000003`.
- Run the perf PMU event tests, especially generated event table checks in `tools/perf/tests/pmu-events.c`.
- Run metric parser tests that cover `clx-metrics.json`, confirming `tma_info_inst_mix_ipswpf` resolves `SW_PREFETCH_ACCESS.ANY`.
- Exercise `perf list` or equivalent generated-list output on a Cascade Lake X event table and confirm the descriptions appear for all five software prefetch events.
- For behavior checks on suitable hardware, compare `SW_PREFETCH_ACCESS.ANY` against the sum of `NTA`, `PREFETCHW`, `T0`, and `T1_T2` under workloads with controlled software prefetch instruction mixes.
