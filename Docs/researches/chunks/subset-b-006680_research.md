# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-cache.json lines 10336-11977

## Scope

This chunk covers the tail of the Ice Lake Xeon `uncore-cache.json` PMU event table in the vendored Linux `tools/perf` tree. The file is declarative JSON metadata, not executable CephFS code. Perf's `pmu-events` generator consumes the complete file and emits generated C tables for symbolic uncore event lookup.

The requested range starts in the middle of the `UNC_CHA_TxR_HORZ_CYCLES_NE.BL_ALL` object: the object's opening brace, `BriefDescription`, and `Counter` fields are on lines 10333-10335, while this chunk begins at its `EventCode` on line 10336. The chunk then contains the remaining visible event objects through `UNC_CHA_XPT_PREF.SENT1` and the closing JSON array on line 11977. There are 150 visible `EventName` records in this slice, all for `Unit: "CHA"`.

## Purpose

These entries expose Ice Lake Xeon CHA uncore cache/home-agent events to Linux perf using stable symbolic names. The chunk focuses on mesh egress, vertical ring, writeback, memory-controller credit, and XPT prefetch behavior:

- Horizontal CMS egress events under `UNC_CHA_TxR_HORZ_*` count queue non-empty cycles, insertions, NACKs, occupancy, and injection starvation for AD, AK, AKC, BL, and IV packet classes.
- Vertical CMS transgress events under `UNC_CHA_TxR_VERT_*` count ADS usage, bypasses, full/not-empty cycles, insertions, NACKs, occupancy, and starvation for AG0/AG1 lanes and packet classes.
- Vertical ring in-use events under `UNC_CHA_VERT_RING_*_IN_USE` count cycles where AD, AKC, AK, BL, IV, or TGC traffic is present at the ring stop, split by up/down and even/odd where applicable.
- `UNC_CHA_WB_PUSH_MTOI.*` splits WbPushMtoI outcomes by whether the line was pushed to LLC or memory.
- `UNC_CHA_WRITE_NO_CREDITS.MC*` tracks CHA write stalls caused by missing iMC write credits, split across memory-controller filters `MC0` through `MC13`.
- `UNC_CHA_XPT_PREF.*` counts XPT prefetches sent or dropped due to conflicts or lack of egress credits.

This metadata is useful for low-level mesh, CHA, memory-controller, and prefetch-pressure analysis on Ice Lake server systems.

## Important Data Fields

Each JSON object follows the perf PMU event schema consumed by `tools/perf/pmu-events/jevents.py`:

- `EventName` is the user-facing symbolic event name accepted by `perf stat -e` and shown by `perf list`.
- `EventCode` is the hardware event selector. This chunk uses `0xA3`, `0xA1`, `0xA4`, `0xA0`, and `0xA5` for horizontal CMS egress conditions; `0x90` through `0x9E` for vertical transgress families; `0xB0` through `0xB5` for vertical ring-in-use families; `0x56` for WbPushMtoI; `0x5A` for iMC write-credit empty; and `0x6f` for XPT prefetch.
- `UMask` refines the subevent. Common packet-class masks include AD credited/uncredited/all values such as `0x10`, `0x1`, and `0x11`; BL values such as `0x40`, `0x4`, and `0x44`; AK as `0x2`; IV as `0x8`; and AKC as `0x80` or separate event-code-1 selectors. Some `UNC_CHA_WRITE_NO_CREDITS` filters intentionally omit `UMask` for `MC8` through `MC13`.
- `Counter` is `"0,1,2,3"` for the visible events, so they can use any of the four CHA uncore programmable counters listed by the metadata.
- `Unit` is `"CHA"` throughout this chunk, binding the records to CHA uncore PMUs.
- `PerPkg` is `"1"` throughout, marking the events as package-scoped uncore measurements rather than per-core CPU events.
- `Experimental` is `"1"` throughout the visible records, so generator and metric consumers can treat these as experimental event definitions.
- `BriefDescription` and `PublicDescription` provide user-visible explanations for `perf list`, including repeated details about CMS transgress buffers, horizontal/vertical ring directions, and iMC credit requirements.

No functions, classes, or runtime APIs are defined in this JSON file. Its contract is the schema shape and exact event encodings.

## APIs, Types, And Generated Representation

The important API surface is generated from this metadata:

- `tools/perf/pmu-events/jevents.py` parses each JSON object into an internal `JsonEvent` representation and emits C event tables.
- `tools/perf/pmu-events/pmu-events.h` defines `struct pmu_event` plus table lookup/iteration APIs such as `pmu_events_table__for_each_event()` and `pmu_events_table__find_event()`.
- `tools/perf/builtin-list.c` and perf's event parser expose generated entries to users through `perf list`, JSON list output, and `perf stat -e <event>`.
- The kernel x86 uncore PMU driver must expose compatible CHA PMU instances and counter slots so the generated event code, umask, and package scope can be scheduled.

For these records, `EventCode`, `UMask`, and optional related qualifier fields become the event encoding string used by perf to configure `perf_event_attr`. `EventName`, descriptions, `Unit`, `PerPkg`, and `Experimental` become generated table metadata used for lookup, display, and metric-expression validation.

## Control Flow

The JSON has no executable control flow. Its effective build/runtime flow is:

1. The perf build includes `tools/perf/pmu-events/Build`.
2. The build invokes `jevents.py` for x86 model data under `tools/perf/pmu-events/arch/x86`.
3. `jevents.py` reads the complete `icelakex/uncore-cache.json`, including this tail chunk, and converts event objects into generated C.
4. The generated `pmu-events.c` is compiled into `libpmu-events.a` and linked into perf.
5. At runtime, perf uses `arch/x86/mapfile.csv` to select the Ice Lake Xeon model event table for matching CPUs.
6. User commands such as `perf list --details` and `perf stat -e UNC_CHA_XPT_PREF.SENT0` resolve symbolic names through the generated tables and program package-level CHA counters when hardware and permissions allow it.

Because this range includes the file's final event and closing array bracket, JSON syntax here closes the complete source file. The final `UNC_CHA_XPT_PREF.SENT1` object has no trailing comma before `]`.

## State And Persistence Behavior

The persistent state is the checked-in JSON metadata and the generated `pmu-events.c` produced during a perf build. The JSON does not mutate files, store measurements, or participate in Ceph runtime state.

At runtime, the relevant mutable state is hardware counter configuration and counter values in CHA uncore PMU instances. `PerPkg: "1"` means these are package-level measurements, so results are interpreted differently from per-thread or per-core events. CMS egress occupancy/non-empty/starvation events are cycle-style pressure signals, while insert, NACK, write-credit, and prefetch events are count-style signals. Users often need to normalize cycle-style events against elapsed cycles, active CHAs, or traffic counts.

The event definitions are also compatibility state for user workflows. Renaming an `EventName`, changing a mask, or altering counter constraints can break scripts even when the JSON still parses successfully.

## Dependencies And Integration Points

This chunk integrates with the Linux perf PMU event stack:

- `tools/perf/pmu-events/README` documents the JSON event database, model directories, mapfile matching, and generated C tables.
- `tools/perf/pmu-events/Build` wires the JSON inputs, `jevents.py`, generated `pmu-events.c`, metric tests, mypy, and pylint checks into the perf build.
- `tools/perf/pmu-events/jevents.py` consumes fields used here, including `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, `PublicDescription`, and `Experimental`.
- `tools/perf/pmu-events/metric.py` tracks experimental events by scanning `EventName` and `Experimental` fields, which matters if metrics later reference these names.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` maps Ice Lake Xeon CPU identifiers to this model directory.
- `tools/perf/util/pmu.c` and `tools/perf/util/pmu.h` integrate generated JSON-event tables with runtime PMU discovery and event parsing.

Although the path is under `sources/distributed-fs/ceph-client`, this file belongs to the vendored Linux perf tooling subtree. It has no direct CephFS client, metadata-server, network, journal, object-store, or distributed-file-system control flow.

## Event Family Notes

The horizontal CMS egress block starts with the tail of `UNC_CHA_TxR_HORZ_CYCLES_NE` and then covers `INSERTS`, `NACK`, `OCCUPANCY`, and `STARVED`. These event families share packet-class suffixes and masks, but the starvation family only includes all/uncredited variants for AD and BL plus AK, AKC, and IV.

The vertical transgress block separates two event-code groups for ordinary packet classes and AKC/TGC variants. Families ending in `0` cover AD, AK, BL, and IV AG0/AG1 selectors; families ending in `1` cover AKC AG0/AG1, with `UNC_CHA_TxR_VERT_STARVED1.TGC` adding TGC starvation. `UNC_CHA_TxR_VERT_ADS_USED` is narrower and only covers AD and BL AG0/AG1.

The vertical ring-in-use block describes pass-by/sink usage at the ring stop. AD, AKC, AK, BL, and TGC are split into `DN_EVEN`, `DN_ODD`, `UP_EVEN`, and `UP_ODD`. IV has only `DN` and `UP` because the descriptions state there is a single IV ring and users should combine up/down by even or odd monitoring intent.

The write-credit block is notable because `MC0` through `MC7` have explicit power-of-two `UMask` values from `0x1` through `0x80`, while `MC8` through `MC13` omit `UMask`. That may be intentional generator behavior for higher controller filters, but it is the highest-risk schema irregularity visible in this slice.

The XPT prefetch tail uses event code `0x6f`: `SENT0` and `SENT1` use masks `0x1` and `0x10`; no-credit drops use `0x4` and `0x40`; conflict drops use `0x8` and `0x80`.

## Risks And Edge Cases

The requested line range starts inside `UNC_CHA_TxR_HORZ_CYCLES_NE.BL_ALL`. A chunk-level reader should not validate this slice as standalone JSON; the previous chunk is needed for that object's opening fields. The complete file does parse as JSON and contains 1,111 event objects.

The repeated mask patterns make copy/paste errors easy. A swapped mask between credited and uncredited AD/BL variants, or between AG0 and AG1 vertical selectors, would parse cleanly but program the wrong hardware subevent.

The missing `UMask` fields for `UNC_CHA_WRITE_NO_CREDITS.MC8` through `.MC13` deserve careful preservation or upstream-documentation validation. Adding guessed masks could be worse than leaving intentional omissions, while accidentally omitting masks from `MC0` through `MC7` would collapse distinct filters.

All visible events are marked experimental. Metrics that depend on these names may be flagged as experimental through `metric.py`; removing the flag would change user-facing stability signals, while adding these events to non-experimental metrics may affect test behavior.

The ring direction descriptions are topology-sensitive. They explain that up/down map to clockwise/counter-clockwise differently across left and right sides of the mesh. Consumers should avoid simplifying these into a single physical direction without considering CHA position.

The closing array bracket is in this chunk. Any trailing comma, malformed quote in a long `PublicDescription`, or accidental deletion of the final `]` breaks the entire Ice Lake Xeon uncore-cache event table generation.

## Test Signals

Useful validation signals for this chunk include:

- Parsing the complete file with a strict JSON parser, for example `python3 -m json.tool sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-cache.json`.
- Running the perf PMU event generation path and confirming `pmu-events.c` is emitted without schema or parse errors.
- Building perf with generated PMU events enabled so the generated event table compiles into `libpmu-events.a`.
- Running perf's PMU event tests, especially generated-table lookup tests under `tools/perf/tests/pmu-events.c`.
- Checking `perf list --details` or JSON list output on an Ice Lake Xeon-capable build for representative names such as `UNC_CHA_TxR_HORZ_INSERTS.AD_ALL`, `UNC_CHA_TxR_VERT_OCCUPANCY0.BL_AG1`, `UNC_CHA_VERT_RING_TGC_IN_USE.UP_ODD`, `UNC_CHA_WRITE_NO_CREDITS.MC7`, and `UNC_CHA_XPT_PREF.DROP1_NOCRD`.
- On Ice Lake Xeon hardware with CHA uncore PMUs available, running `perf stat -a -e` for a small set of these events and confirming scheduling succeeds and counts are plausible under memory or mesh traffic.

## Cross-Chunk Notes

This is chunk 3 of 3 for `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-cache.json`. The merge lane must combine it with `subset-b-006678` and `subset-b-006679`, because this chunk starts inside an event object and only the complete file is valid JSON. The final per-file report should preserve the whole-file view that the source is a 1,111-object CHA PMU event table for Ice Lake Xeon.
