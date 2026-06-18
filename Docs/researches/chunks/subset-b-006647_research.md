# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-cache.json lines 12828-13057

## Scope

This chunk covers the final entries in the Cascade Lake Xeon `uncore-cache.json` PMU event table. It is data, not executable code: JSON objects that the perf `pmu-events` build pipeline converts into generated C event tables. The requested line range starts inside the first event object, so the first logical entry is continued from the preceding chunk: `UNC_H_WRITE_NO_CREDITS.MC1_SMI1` has its `BriefDescription` on line 12827 and the rest of the object in this slice. The chunk then contains the complete tail of the file, ending with the closing JSON array on line 13057.

The slice describes deprecated `UNC_H_*` uncore cache/home-agent aliases. Each entry points users toward the newer `UNC_CHA_*` event spelling while preserving the old alias in the model event database.

## Purpose

The purpose of these entries is compatibility for older Cascade Lake Xeon uncore event names. They allow perf users, scripts, and metric definitions that still reference `UNC_H_WRITE_NO_CREDITS.*` or `UNC_H_XSNP_RESP.*` to continue resolving a symbolic event, while marking the name deprecated and documenting the replacement.

The first event in the chunk maps the old home-agent write-credit alias `UNC_H_WRITE_NO_CREDITS.MC1_SMI1` to `UNC_CHA_WRITE_NO_CREDITS.MC1_SMI1`. The remaining twenty events map old external snoop response aliases under `UNC_H_XSNP_RESP` to the equivalent `UNC_CHA_XSNP_RESP` names.

## Important Data Fields

Every event object in this slice uses the perf PMU JSON schema fields consumed by `tools/perf/pmu-events/jevents.py`:

- `EventName`: the user-visible symbolic event name. `jevents.py` lowercases it when generating the compiled table, but perf matching still presents the original semantic name to users through the event database/listing path.
- `BriefDescription`: the only description field present for these entries. It states that the event is deprecated and names the replacement event.
- `Deprecated`: set to `"1"` for all entries in the chunk. This becomes the `deprecated` boolean in `struct pmu_event`.
- `Experimental`: set to `"1"` for all entries, indicating the event definition should be treated as experimental metadata.
- `EventCode` and `UMask`: the hardware selector fields that form the encoded perf event. `UNC_H_WRITE_NO_CREDITS.MC1_SMI1` uses event code `0x5A`, while every `UNC_H_XSNP_RESP.*` alias uses event code `0x32` with variant-specific unit masks.
- `Counter`: `"0,1,2,3"` for all entries, restricting them to the four CHA uncore counters.
- `Unit`: `"CHA"` for all entries. `jevents.py` maps this unit string to the target uncore PMU name for the generated event entry.
- `PerPkg`: `"1"` for all entries, so the generated `pmu_event` records are package-scoped uncore events rather than per-core CPU events.

The `UNC_H_XSNP_RESP` entries are organized by requester/source class and response class:

- `ANY_*` masks: `0xe4`, `0xf0`, `0xe2`, `0xe8`, and `0xe1`.
- `CORE_*` masks: `0x44`, `0x50`, `0x42`, `0x48`, and `0x41`.
- `EVICT_*` masks: `0x84`, `0x90`, `0x82`, `0x88`, and `0x81`.
- `EXT_*` masks: `0x24`, `0x30`, `0x22`, `0x28`, and `0x21`.

Within each group, the suffixes are `RSPI_FWDFE`, `RSPI_FWDM`, `RSPS_FWDFE`, `RSPS_FWDM`, and `RSP_HITFSE`. The repeated mask pattern suggests the high bits select the requester/source class and the low bits select the snoop-response condition.

## APIs, Types, And Generated Representation

This JSON is consumed by the perf PMU events generator rather than by normal C APIs directly. `jevents.py` reads each JSON object, constructs an internal event representation, and emits generated C into `pmu-events/pmu-events.c`. The generated data is exposed through `pmu-events/pmu-events.h`, especially:

- `struct pmu_event`, whose fields include `name`, `event`, `desc`, `pmu`, `unit`, `perpkg`, and `deprecated`.
- `pmu_events_table__for_each_event()`, which iterates events for a matched table and PMU.
- `pmu_events_table__find_event()`, which resolves a named event against a table and PMU.

For these records, `EventCode` and `UMask` become the event encoding string that perf uses to populate `perf_event_attr.config`. `BriefDescription` becomes `desc`; `Unit` influences the generated `pmu` binding; `PerPkg` and `Deprecated` become booleans. There are no `PublicDescription`, `Filter`, `ScaleUnit`, metric expression, or threshold fields in this chunk.

## Control Flow

There is no runtime control flow in the JSON file itself. The effective flow is:

1. During the perf build, `tools/perf/pmu-events/Build` invokes `jevents.py` for the selected architecture.
2. `jevents.py` recursively traverses `tools/perf/pmu-events/arch/x86`, reads model JSON files such as this `cascadelakex/uncore-cache.json`, and validates/transforms each event object.
3. The generator emits compact generated event tables into `pmu-events.c`.
4. The generated object is built into `libpmu-events.a` and then linked into perf.
5. At runtime, perf identifies the CPU model through `arch/x86/mapfile.csv`, selects the Cascade Lake Xeon event table, and exposes matching CHA events as symbolic aliases.
6. Commands such as `perf list`, `perf stat -e <event>`, and metric expansion can find these old aliases, while list-style output can also show the deprecated flag.

Because this chunk is the tail of the JSON array, syntax at the final object matters: the last `UNC_H_XSNP_RESP.EXT_RSP_HITFSE` object has no trailing comma and is followed by the closing `]`.

## State And Persistence Behavior

The only persistent state is the checked-in event metadata and the generated `pmu-events.c` produced from it at build time. The JSON does not create mutable program state, open files, or store runtime data.

At runtime, the event state lives in perf's generated event tables and in any `perf_event_attr` instances created from a selected alias. For these events, the relevant hardware state is package-level CHA uncore counter configuration. The `PerPkg` flag is important because perf should aggregate/count the event at package scope, not as a normal per-thread or per-core event.

The deprecated aliases are persistent compatibility surface. Removing or renaming them would not change the newer `UNC_CHA_*` events, but it would break older command lines and automation that still use the `UNC_H_*` names.

## Dependencies And Integration Points

This chunk depends on the perf PMU event infrastructure:

- `tools/perf/pmu-events/README` defines the JSON-directory, mapfile, generation, and runtime alias model.
- `tools/perf/pmu-events/jevents.py` parses fields such as `EventName`, `BriefDescription`, `Unit`, `PerPkg`, and `Deprecated`.
- `tools/perf/pmu-events/pmu-events.h` defines the generated event/metric table interfaces and `struct pmu_event`.
- `tools/perf/builtin-list.c` can print JSON/list output including `EventName`, `Deprecated`, and `BriefDescription`.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` maps x86 CPU IDs to model directories such as `cascadelakex`.
- The Linux uncore PMU driver and sysfs PMU descriptions must expose a compatible CHA PMU so the generated event encodings can be scheduled on real hardware.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file belongs to the vendored Linux perf tooling tree. It has no direct CephFS client control flow or distributed file-system behavior.

## Risks And Edge Cases

The line range begins in the middle of `UNC_H_WRITE_NO_CREDITS.MC1_SMI1`, so chunk-level review must avoid treating lines 12828-12835 as a standalone JSON object. The full file is valid because the opening brace and `BriefDescription` are immediately before the requested range.

Alias accuracy is the main semantic risk. The `BriefDescription` replacement names must match real `UNC_CHA_*` definitions elsewhere in the same model data. If an alias keeps the old name but carries the wrong `EventCode` or `UMask`, perf will successfully parse it but program a different CHA counter than users expect.

Deprecation handling is also a compatibility risk. These events should remain discoverable for old workflows, but UI and documentation should steer new users to `UNC_CHA_*`. Dropping the `Deprecated` flag would make stale names look current; deleting the aliases would break older command lines.

The event scope is package-level CHA uncore, so users may get confusing results if they compare these counters directly with per-core events or run on hardware whose uncore PMUs are unavailable, disabled, renamed, or permission-restricted.

The chunk's final `]` makes it sensitive to JSON syntax churn. A missing comma before this slice, an accidental trailing comma at the final event, or malformed quoting in any description would break `jevents.py` generation for the whole model table.

## Test Signals

Useful validation signals for this chunk include:

- Running the PMU event generation path for x86 and confirming `pmu-events.c` is produced without JSON parse errors.
- Building perf with jevents enabled so the generated event tables compile into `libpmu-events.a`.
- Running the perf PMU event tests, especially `tools/perf/tests/pmu-events.c`, to catch generated-table regressions.
- On Cascade Lake Xeon hardware, checking `perf list --details` or JSON list output for deprecated `UNC_H_WRITE_NO_CREDITS.MC1_SMI1` and representative `UNC_H_XSNP_RESP.*` aliases.
- Verifying that `perf stat -e` accepts both old `UNC_H_*` aliases and the replacement `UNC_CHA_*` names where the CHA uncore PMU is available.
- Spot-checking generated encodings for the `0x5A/0x2` write-credit event and several `0x32` XSNP response masks from the `ANY`, `CORE`, `EVICT`, and `EXT` groups.

## Cross-Chunk Notes

This document intentionally covers only lines 12828-13057. The previous chunk is needed for the full first object's `BriefDescription`, and the merge lane should combine adjacent chunks before producing a whole-file report for `uncore-cache.json`.
