# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-cache.json lines 1-5370

## Scope

This chunk covers the opening 5,370 lines of the Ice Lake Xeon `uncore-cache.json` PMU event table in the vendored Linux `tools/perf` tree. The file is static JSON metadata rather than executable CephFS logic. Perf's PMU event generator consumes these objects and emits model-specific event tables used by `perf list`, `perf stat`, and related event lookup paths.

The full JSON file has 11,977 lines and 1,111 event objects. This line range starts with the opening JSON array and contains 499 complete `EventName` records through `UNC_CHA_RxC_WBQ1_REJECT.HA`. Lines 5368-5370 also begin the next event object, `UNC_CHA_RxC_WBQ1_REJECT.LLC_OR_SF_WAY`, but the rest of that object is outside this chunk. The chunk is therefore not independently parseable as JSON even though it begins at the file start.

## Purpose

The metadata exposes Ice Lake Xeon CHA, or cache/home-agent, uncore events through stable symbolic names. These events let perf users analyze package-level cache, snoop, ring, request-queue, persistent-memory, memory-controller, and credit-pressure behavior without hand-encoding event select and unit-mask values.

The first entries are deprecated 2LM near-memory aliases that point users toward `UNC_CHA_PMM_MEMMODE_NM_*` names. The rest of the range defines live CHA event families, including CMS agent credit acquisition and occupancy, CHA and CMS clock ticks, core snoop distribution, LLC lookup and victim filters, directory lookup/update events, horizontal ring usage, PMM QoS and memory-mode events, ingress/request queue occupancy and rejects, pipe rejects, memory-controller read/write counts, read no-credit conditions, and the start of RxC WBQ reject conditions.

Although this file lives under `sources/distributed-fs/ceph-client`, it is part of a vendored Linux perf tooling subtree. It has no direct Ceph client, distributed filesystem, metadata server, network, or storage control flow.

## Important Data Fields

Each event object uses the perf PMU JSON schema:

- `EventName` is the symbolic perf event name, such as `UNC_CHA_LLC_LOOKUP.DATA_READ_LOCAL` or `UNC_CHA_RxC_PRQ0_REJECT.AD_REQ_VN0`.
- `EventCode` is the hardware event selector. This chunk uses many CHA selector values, including `0x34` for the large `UNC_CHA_LLC_LOOKUP.*` family, `0x37` for `UNC_CHA_LLC_VICTIMS.*`, `0x42` for `UNC_CHA_PIPE_REJECT.*`, `0x11` for `UNC_CHA_RxC_OCCUPANCY.*`, and `0x26` through `0x2B` for RxC queue reject/retry sets.
- `UMask` selects a subevent. Common patterns include single-bit masks such as `0x1`, `0x2`, `0x4`, and `0x80`, plus wider masks for LLC lookup source/state filters.
- `Counter` constrains usable CHA uncore counters. Most complete events in this range use `"0,1,2,3"`. Four `UNC_CHA_RxC_OCCUPANCY.*` events use `"0"`, which matters because occupancy events are counter-slot constrained.
- `Unit` is `"CHA"` for every visible complete event, binding the definitions to CHA PMU instances.
- `PerPkg` is `"1"` for every visible complete event, marking package-level uncore measurement semantics.
- `Experimental` appears on 483 of the 499 complete records, so most names should be treated as lower-stability hardware metadata rather than polished architectural ABI.
- `Deprecated` appears on 20 complete records. These are the opening 2LM aliases and several old `UNC_CHA_LLC_LOOKUP.*` names.
- `BriefDescription` and `PublicDescription` are user-facing text surfaced by perf event listing and generated event tables.

## APIs, Types, And Generated Representation

This JSON file defines no functions, classes, or C types. Its effective API is the generated perf event database:

- `tools/perf/pmu-events/jevents.py` parses event JSON and emits generated C data.
- `tools/perf/pmu-events/pmu-events.h` defines generated event-table interfaces and `struct pmu_event`-style records.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` maps x86 CPU identifiers to model directories such as `icelakex`.
- Perf's event parser and PMU event lookup paths resolve symbolic names from generated tables into event encodings.

For this chunk, the essential generated representation is the tuple of event name, CHA unit, event code, unit mask, counter constraint, descriptions, package scope, experimental/deprecated flags, and any additional qualifier fields. Runtime perf commands do not infer these masks from the event name; they rely on the explicit JSON fields.

## Control Flow

The JSON itself has no executable control flow. Its build and runtime path is:

1. The perf build scans x86 PMU event directories.
2. `jevents.py` reads `arch/x86/icelakex/uncore-cache.json` and validates each event object in the complete file.
3. The generator converts records into compiled PMU event tables.
4. At runtime, perf maps the detected CPU model to the Ice Lake Xeon table.
5. `perf list` displays events and descriptions; `perf stat -e <name>` resolves names such as `UNC_CHA_LLC_LOOKUP.READ_MISS` or `UNC_CHA_RxC_RRQ0_REJECT.BL_WB_VN0`.
6. The kernel uncore PMU driver programs compatible CHA counters using the selected event code, mask, and counter constraints.

Within the source, records are ordered by hardware family. This chunk proceeds from deprecated 2LM aliases into agent credit metrics, general CHA clocks and snoops, directory/direct-go/cache lookup behavior, memory and ring activity, pipe rejects, PMM and read-credit events, then RxC insert, occupancy, reject, and retry families.

## State And Persistence Behavior

The persistent state is the checked-in JSON metadata and the generated C event table produced during perf builds. The file does not mutate runtime state, open files, or store measurements.

At runtime, selected events become package-level CHA uncore counter configurations. The measured state is held in hardware counters for the lifetime of a perf session. Count-like events such as LLC lookups, victims, rejects, and memory-controller reads/writes accumulate occurrences. Occupancy events, notably the RxC ingress occupancy records in this chunk, count queue entries per cycle and usually require normalization against elapsed cycles or a traffic counter to be meaningful.

`PerPkg: "1"` means users should interpret results as package-scoped uncore observations rather than per-thread or per-core counts. Depending on perf syntax and kernel PMU exposure, a measurement may aggregate across multiple CHA PMU instances in a socket.

## Dependencies And Integration Points

The chunk integrates with Linux perf's PMU event infrastructure:

- `tools/perf/pmu-events/README` documents the JSON event format and generation flow.
- `tools/perf/pmu-events/jevents.py` parses fields present here.
- `tools/perf/pmu-events/pmu-events.h` exposes generated PMU event tables to perf code.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` selects the Ice Lake Xeon model directory for matching systems.
- Perf list/stat/reporting code consumes the generated metadata.
- The Linux x86 uncore PMU driver must expose compatible CHA PMUs and counter slots for these encodings to be usable.

The deprecation references also depend on replacement events elsewhere in this same file, especially `UNC_CHA_PMM_MEMMODE_NM_INVITOX.*`, `UNC_CHA_PMM_MEMMODE_NM_SETCONFLICTS*`, and newer `UNC_CHA_LLC_LOOKUP.*` names.

## Event Family Notes

The opening `UNC_CHA_2LM_NM_*` events are deprecated compatibility aliases for PMM memory-mode near-memory behavior. They cover invalidate-to-exclusive local/remote/set-conflict conditions and set conflicts in LLC, snoop filter, TOR, memory writes, and non-invalidating memory writes.

`UNC_CHA_AG0_*` and `UNC_CHA_AG1_*` dominate the first thousand lines. They count CMS Agent 0 and Agent 1 AD/BL credits acquired or occupied for transgress lanes `TGR0` through `TGR10`, split into low and high mask groups. These are useful for diagnosing fabric credit pressure and occupancy rather than cache hit behavior.

The middle of the chunk covers broad CHA activity: bypass to iMC, CHA/CMS clock ticks, core snoop classes, direct GO responses, directory lookup/update paths, distress assertions, egress ordering, HITME lookup/hit/miss/update behavior, horizontal ring AD/AK/AKC/BL/IV usage, and iMC read/write request counts.

`UNC_CHA_LLC_LOOKUP.*` is the largest family in this range with 64 complete records. It splits LLC lookups by request type, local versus remote home, read/RFO/write/flush/prefetch categories, hit/miss, cache state, snoop-filter state, and deprecated aliases. The related `UNC_CHA_LLC_VICTIMS.*` family counts victim outcomes by local/remote and MESI-like state.

`UNC_CHA_PIPE_REJECT.*` has 34 complete records. It covers rejects caused by egress credits, HA credits, snoop-filter or LLC way conflicts, go-track conditions, index-in-pipe, isolated read/write paths, memory, not-taken paths, physical-address match, QoS, SF victim state, TOR fullness, victim handling, and WC aliasing.

The PMM and QoS groups include current replacements for the deprecated 2LM aliases plus PMM QoS issued/bypassed/occupancy events. The read no-credit family splits MC, WPQ, and iMC credit-starvation cases, including local, remote, and priority variants.

The RxC section starts at insert and occupancy accounting, then expands into repeated reject/retry matrices for IPQ, IRQ, ISMQ, OTHER, PRQ, request queue, RRQ, and WBQ. Set 0 reject/retry records typically split AD request, AD response, BL response, BL writeback, BL NCB/NCS, and non-UPI AK/IV injection failures. Set 1 records split aggregate and structural causes such as `ANY0`, HA, LLC victim, SF victim, victim, allow-snoop, LLC-or-SF way, and physical-address match. This chunk ends after the complete `UNC_CHA_RxC_WBQ1_REJECT.HA` object and before the remainder of `UNC_CHA_RxC_WBQ1_REJECT.LLC_OR_SF_WAY`.

## Risks And Edge Cases

The chunk boundary is a real syntax edge case. Lines 5368-5370 open an event object but do not include its `EventName`, `PublicDescription`, `UMask`, `Unit`, or closing brace. The merge lane must combine this with the next chunk before validating object completeness or producing the final per-file report.

Counter constraints are semantically important. The four RxC occupancy events use only counter `0`; treating them like the common `"0,1,2,3"` counting events would allow invalid or misleading scheduling. Conversely, over-constraining the normal count events would reduce usable counter scheduling.

The deprecated aliases should remain usable while being clearly marked. Removing them can break scripts that still use 2LM or old LLC lookup names; hiding their deprecation can keep users on stale names.

The event names are highly patterned, so copy/paste drift is a major risk. Examples include local versus remote home, AD versus BL channel, Agent 0 versus Agent 1, acquire versus occupancy, reject versus retry, IPQ/IRQ/PRQ/RRQ/WBQ queue names, and set 0 versus set 1 reject causes.

Many records are marked experimental and some descriptions are terse or repetitive. Cosmetic edits to descriptions should not be mixed with hardware encoding changes, because a single wrong `EventCode` or `UMask` can still parse cleanly while measuring a different hardware condition.

## Test Signals

Useful validation for this chunk includes:

- Parse the complete `icelakex/uncore-cache.json` with a strict JSON parser; the line slice alone should not be expected to parse.
- Run perf's PMU event generation path and confirm the Ice Lake Xeon uncore cache table is emitted without schema errors.
- Build perf and run PMU event table tests, especially generated-event lookup coverage under `tools/perf/tests/pmu-events.c`.
- Verify representative generated events are listed with expected unit, code, mask, counter, package, and deprecation metadata: `UNC_CHA_2LM_NM_INVITOX.LOCAL`, `UNC_CHA_AG0_AD_CRD_ACQUIRED0.TGR0`, `UNC_CHA_LLC_LOOKUP.DATA_READ_LOCAL`, `UNC_CHA_LLC_VICTIMS.REMOTE_M`, `UNC_CHA_PIPE_REJECT.TOR_FULL`, `UNC_CHA_RxC_OCCUPANCY.RRQ`, and `UNC_CHA_RxC_RRQ0_REJECT.BL_WB_VN0`.
- On Ice Lake Xeon hardware with CHA uncore PMUs available, run `perf stat -a -e` spot checks for count and occupancy events and confirm the kernel accepts the counter constraints.
- Cross-check deprecated aliases against their replacement event definitions in later or earlier parts of the complete file.

## Cross-Chunk Notes

This document intentionally covers only lines 1-5370. Later chunks are needed for the rest of `UNC_CHA_RxC_WBQ1_REJECT.LLC_OR_SF_WAY`, the remaining WBQ1 reject records, and all later Ice Lake Xeon uncore-cache event families. The final per-file research document should reconcile this opening chunk with the continuation chunks before making file-wide statements.
