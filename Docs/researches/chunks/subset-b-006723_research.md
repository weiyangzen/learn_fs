# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-cache.json lines 1-5912

## Scope

This chunk covers the beginning of the Skylake-X perf PMU uncore cache event table. The full source is a JSON array of event descriptor objects; this chunk contains the opening `[` plus 537 complete `UNC_CHA_*` event objects and then stops inside the next object, after the `PerPkg` field for `UNC_CHA_TxR_VERT_CYCLES_NE.BL_AG0`. Adjacent chunks are required to complete that partially visible record and the rest of the file.

## Purpose

The file is data, not executable code. It declares Intel Skylake-X uncore cache/home-agent PMU events consumed by Linux `perf` so users can select symbolic event names instead of writing raw uncore event encodings. All complete events in this chunk have `Unit: "CHA"`, which `tools/perf/pmu-events/jevents.py` maps to the runtime PMU name `uncore_cha`.

These descriptors cover CHA clock ticks, RxC request queues, core snoops, LLC lookups and victims, TOR inserts/occupancy, IMC-facing requests, snoop responses, HITME/IODC state changes, mesh/ring use, CMS credits, TxR/RxR occupancy and insertion events, ring starvation/bounce events, and horizontal/vertical transmit-ring behavior.

## Data Model And Generated API Surface

Each complete object in this chunk follows the perf JSON event schema used by `jevents.py`:

- `EventName`: symbolic perf event name, lowercased by generation into `struct pmu_event.name`.
- `EventCode`: base hardware event selector, converted to `event=<value>`.
- `UMask`: event unit mask, converted to `umask=<value>` when nonzero.
- `BriefDescription`: short description used as `struct pmu_event.desc`.
- `PublicDescription`: longer help text used as `struct pmu_event.long_desc` when distinct.
- `Unit`: source PMU unit name; `CHA` becomes `uncore_cha`.
- `PerPkg`: package aggregation flag, stored as `struct pmu_event.perpkg`.
- `Counter`: metadata about legal CHA counter slots; most records use `0,1,2,3`, while 37 records use only `0`.
- Optional `Experimental`, `Deprecated`, and `Filter` fields are preserved into generated attributes where supported.

The relevant generated C API is declared in `tools/perf/pmu-events/pmu-events.h`. `struct pmu_event` is the runtime representation with `name`, `event`, `desc`, `topic`, `long_desc`, `pmu`, `unit`, `perpkg`, and `deprecated` fields. Generated lookup/iteration APIs include `pmu_events_table__for_each_event`, `pmu_events_table__find_event`, `pmu_events_table__num_events`, and `perf_pmu__find_events_table`.

## Generation And Control Flow

Build-time flow:

1. `jevents.py` scans architecture/model JSON files such as this one.
2. `read_json_events()` loads the array with Python `json.load(..., object_hook=JsonEvent)`.
3. `JsonEvent.__init__()` canonicalizes fields: it lowercases `EventName`, builds an encoded event string from `EventCode` plus nonzero `UMask` and filters, maps `Unit` to a Linux PMU name, and normalizes descriptions.
4. Event objects are accumulated, sorted by PMU/name, and emitted into compressed generated C tables.
5. At runtime, perf selects the model table through CPU/PMU matching and uses generated table functions to iterate or binary-search events under the matching PMU name.

Runtime flow for these records is therefore lookup-driven rather than file-read-driven. A user-facing event such as `uncore_cha/event=.../` or a symbolic `UNC_CHA_*` name resolves through the generated table for Skylake-X and the `uncore_cha` PMU.

## Event Families In This Chunk

The chunk contains 537 complete records across these families:

- CMS/agent credit families: `UNC_CHA_AG0_AD_CRD_ACQUIRED`, `UNC_CHA_AG0_AD_CRD_OCCUPANCY`, `UNC_CHA_AG1_AD_CRD_ACQUIRED`, `UNC_CHA_AG1_AD_CRD_OCCUPANCY`, `UNC_CHA_AG0_BL_CRD_ACQUIRED`, `UNC_CHA_AG0_BL_CRD_OCCUPANCY`, `UNC_CHA_AG1_BL_CREDITS_ACQUIRED`, and `UNC_CHA_AG1_BL_CRD_OCCUPANCY`, each split across transgress masks `TGR0` through `TGR5`.
- RxC queue pressure and retry families: occupancy, inserts, IRQ/PRQ/IPQ/ISMQ/RRQ/WBQ rejects, request queue retries, and other retries, generally split across VN, HA, victim, snoop, and non-UPI masks.
- Cache/snoop/TOR families: `UNC_CHA_CORE_SNP`, `UNC_CHA_LLC_LOOKUP`, `UNC_CHA_LLC_VICTIMS`, `UNC_CHA_TOR_INSERTS`, `UNC_CHA_TOR_OCCUPANCY`, `UNC_CHA_REQUESTS`, `UNC_CHA_SNOOPS_SENT`, `UNC_CHA_SNOOP_RESP`, and `UNC_CHA_SNOOP_RESP_LOCAL`.
- Memory-controller and directory adjacency: `UNC_CHA_IMC_READS_COUNT`, `UNC_CHA_IMC_WRITES_COUNT`, `UNC_CHA_DIR_LOOKUP`, `UNC_CHA_DIR_UPDATE`, `UNC_CHA_READ_NO_CREDITS`, `UNC_CHA_BYPASS_CHA_IMC`, and `UNC_CHA_OSB`.
- HITME/IODC/miscellaneous state: HITME lookup/hit/miss/update, IODC alloc/dealloc, SF eviction, MISC, FAST asserted, egress ordering, ring source throttling, and CHA/CMS clockticks.
- Mesh/ring transport: ring bounce and starvation families, horizontal ring in-use families, `RxR_*`, `TxR_HORZ_*`, `TxR_VERT_ADS_USED`, `TxR_VERT_BYPASS`, `TxR_VERT_CYCLES_FULL`, and the beginning of `TxR_VERT_CYCLES_NE`.

Important boundary detail: lines 5906-5912 begin `UNC_CHA_TxR_VERT_CYCLES_NE.BL_AG0` but the chunk omits its `PublicDescription`, `UMask`, `Unit`, and closing brace. The last complete event before that partial object is `UNC_CHA_TxR_VERT_CYCLES_NE.AK_AG1`.

## State And Persistence Behavior

This file has no mutable state, persistence writes, function calls, or side effects. Persistence happens through source control and through generated `pmu-events.c` style tables produced during the perf build. At runtime the data is static read-only metadata embedded in the perf binary or build output.

`PerPkg: "1"` is set on all complete records in this chunk, which signals package-level aggregation. That matters because CHA uncore counters are package-wide resources rather than per-thread core PMCs. Most records are also marked `Experimental: "1"`; 468 complete records have that flag, while 69 complete records omit it.

## Dependencies And Integration Points

Primary dependencies:

- Python JSON parsing in `tools/perf/pmu-events/jevents.py`.
- The perf PMU event schema represented by `tools/perf/pmu-events/pmu-events.h`.
- Linux uncore PMU naming conventions; `Unit: "CHA"` maps to `uncore_cha`.
- Skylake-X model directory discovery under `tools/perf/pmu-events/arch/x86/skylakex/`.
- Runtime perf PMU discovery and wildcard PMU-name matching when looking up generated event tables.

Integration points include `perf list` display, `perf stat` event selection, generated table lookup by `perf_pmu__find_events_table()`, and tests under `tools/perf/tests/pmu-events.c` that validate generated event table behavior against expected JSON-derived entries.

## Risks And Edge Cases

- Chunk boundary risk: this chunk is not independently valid JSON because it stops inside an event object. Research or merge tooling must not parse only lines 1-5912 as a standalone file.
- Event-name spelling is part of the public perf interface. The family `UNC_CHA_AG1_BL_CREDITS_ACQUIRED` uses `CREDITS` while neighboring families use `CRD`; changing that would break existing symbolic event names.
- Several descriptions appear mechanically repeated or inconsistent. For example, vertical `CYCLES_FULL` records say the egress was "Not Full" in their public descriptions, which conflicts with the event name. This may be inherited vendor text, but it is a documentation risk.
- Generated event strings depend on nonzero `UMask`; a missing or zero mask would collapse variants into the same raw event encoding.
- Counter-slot metadata is mixed: 500 complete records allow counters `0,1,2,3`; 37 allow only counter `0`. Tooling that ignores `Counter` could permit unsupported scheduling.
- The JSON uses string values for booleans/enums such as `PerPkg` and `Experimental`; schema consumers must preserve the expected conversion behavior.

## Test Signals

Useful validation for this chunk and the eventual merged file:

- `jq` should parse the full `uncore-cache.json` successfully; parsing only this chunk should fail because of the intentional chunk boundary.
- Generated perf events should include all complete names in this chunk under PMU `uncore_cha`, with event strings formed from `EventCode` and `UMask`.
- `perf list` on a Skylake-X-capable build should show these `UNC_CHA_*` names or their lowercased generated forms in the uncore CHA topic.
- Existing PMU event tests should continue to exercise `pmu_events_table__for_each_event`, `pmu_events_table__find_event`, and generated table counts.
- Spot checks should verify package aggregation for these records, preservation of `Deprecated` where present, and no duplicate `(EventCode, UMask, EventName)` collisions introduced by edits.
