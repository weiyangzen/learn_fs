# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-cache.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006678`: lines 1-5370, `Docs/researches/chunks/subset-b-006678_research.md`
- `subset-b-006679`: lines 5371-10335, `Docs/researches/chunks/subset-b-006679_research.md`
- `subset-b-006680`: lines 10336-11977, `Docs/researches/chunks/subset-b-006680_research.md`

## Chunk Research

### subset-b-006678: lines 1-5370

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

### subset-b-006679: lines 5371-10335

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-cache.json lines 5371-10335

## Scope

This chunk covers lines 5371-10335 of the Ice Lake Xeon `uncore-cache.json` PMU event table. The file is declarative perf metadata, not executable Ceph client code. It is stored under a repository snapshot of Linux `tools/perf/pmu-events/arch/x86/icelakex/` and feeds Linux perf's PMU event table generation for Ice Lake server uncore cache/home-agent events.

The selected range is a chunked view of one large JSON array. It is not a standalone JSON document: line 5371 starts inside the object for `UNC_CHA_RxC_WBQ1_REJECT.LLC_OR_SF_WAY`, and line 10335 ends inside the object for `UNC_CHA_TxR_HORZ_CYCLES_NE.BL_ALL`. The full source file has 11,977 lines, contains 1,111 JSON array entries, and parses as valid JSON. This slice exposes 462 `EventName` fields, all for the `CHA` uncore PMU unit.

The chunk is dominated by two large CHA TOR families:

- `UNC_CHA_TOR_INSERTS`: 166 records, event code `0x35`, counting successful TOR insertions that match a subevent qualification.
- `UNC_CHA_TOR_OCCUPANCY`: 143 records, event code `0x36`, accumulating valid TOR entries per cycle for matching subevent qualifications.

The remaining records cover WBQ retry causes, receive-ring ingress/egress pressure, snoop behavior, snoop-filter eviction states, horizontal mesh transmit pressure, and target-group credit stalls.

## Purpose

The purpose of this chunk is to expose Ice Lake Xeon CHA performance events to perf users. CHA events measure package-level behavior around cache/home-agent queues, snoop filter state, transaction order queues, and mesh stop traffic. These counters are useful for diagnosing LLC/SF conflicts, snoop traffic, memory access locality, PMem-vs-DDR routing, streaming writes, IO-originated transactions, and mesh backpressure.

The range starts with the tail of `UNC_CHA_RxC_WBQ1_REJECT`, which reports writeback queue retries by rejection cause:

- LLC or snoop-filter way conflict.
- LLC victim and snoop-filter victim cases.
- Physical-address match against an outstanding rejected request.
- Generic victim-related retry conditions.

It then describes CMS receive-side events:

- `UNC_CHA_RxR_BUSY_STARVED` counts ingress starvation caused by another queue having priority.
- `UNC_CHA_RxR_BYPASS` counts packets bypassing CMS ingress.
- `UNC_CHA_RxR_CRD_STARVED` and `UNC_CHA_RxR_CRD_STARVED_1` count ingress starvation caused by lack of credit forwarding toward egress.
- `UNC_CHA_RxR_INSERTS` counts CMS ingress allocations.
- `UNC_CHA_RxR_OCCUPANCY` tracks CMS ingress-buffer occupancy.

The middle section provides snoop and snoop-filter visibility:

- `UNC_CHA_SF_EVICTION` splits snoop-filter evictions by E, M, and S states.
- `UNC_CHA_SNOOPS_SENT` splits snoops by local/remote and broadcast/direct delivery.
- `UNC_CHA_SNOOP_RESP` and `UNC_CHA_SNOOP_RESP_LOCAL` classify responses such as conflict, forwarded data, forwarded writeback, invalid, shared, and writeback responses.
- `UNC_CHA_SNOOP_RSP_MISC` captures partial and modified-response cases that hit LLC or snoop filter.

The largest sections are the TOR insert and TOR occupancy families. They expose the same conceptual qualifiers in two measurement modes: inserts are event counts; occupancy accumulates valid matching entries each cycle. The qualifiers include:

- All, hit, miss, eviction, local target, remote target, near memory, not-near memory, DDR, PMM, and non-coherent traffic.
- iA-originated traffic, including CLFLUSH/CLFLUSHOPT, clean reads, demand reads, page-table reads, RFO, ITOM, SpecITOM, LLC prefetch code/data/RFO, writeback state transitions, WCIL/WCILF/WIL, and streaming write variants.
- Local and remote splits for clean reads, RFO, WCIL/WCILF, full streaming writes, partial streaming writes, DDR, DRAM, and PMM.
- IO-originated traffic, including PCI read current, RFO, ITOM, ITOMCACHENEAR, writeback modified-to-invalid, hit/miss splits, and local/remote variants in the inserts family.
- IPQ, PRQ, RRQ, WBQ, IRQ from iA and non-iA, ISOC, MMCFG, opcode-match, and pre-morphed opcode-match filters.

The tail of the range starts horizontal transmit-ring events:

- `UNC_CHA_TxR_HORZ_ADS_USED` counts use of horizontal anti-deadlock slots.
- `UNC_CHA_TxR_HORZ_BYPASS` counts packets bypassing horizontal egress.
- `UNC_CHA_TxR_HORZ_CYCLES_FULL` counts cycles where horizontal egress queues are full.
- `UNC_CHA_TxR_HORZ_CYCLES_NE` begins the not-empty queue family and continues past this chunk boundary.

## Important Schema Fields and Event Families

Each JSON object uses the standard perf PMU event metadata schema:

- `EventName`: the symbolic perf event name, such as `UNC_CHA_TOR_INSERTS.IA_MISS_DRD_LOCAL_DDR`.
- `EventCode`: the hardware event selector. This chunk uses selectors including `0x29`, `0x35`, `0x36`, `0x3D`, `0x51`, `0x5C`, `0x5D`, `0x6B`, `0xA2`, `0xA3`, `0xA6`, `0xA7`, `0xD0`-`0xD7`, `0xE0`-`0xE5`, and one lowercase `0xe4`.
- `UMask`: the unit mask or extended umask selecting traffic class, source, target, hit/miss mode, memory type, opcode-match mode, or target group. Some records intentionally omit `UMask`.
- `BriefDescription`: short human-readable summary.
- `PublicDescription`: longer explanation; this chunk has 447 `PublicDescription` fields across 462 event names.
- `Counter`: allowed counters. Most records use `0,1,2,3`; TOR occupancy records use counter `0` only.
- `Unit`: `CHA` for every event in this chunk.
- `PerPkg`: package-scope marker, normally `1`.
- `Experimental`: present on 379 records in this slice.
- `Deprecated`: present on 9 records, including the deprecated `UNC_CHA_TOR_INSERTS.DDR4` alias.

Major event-code groupings visible in the range are:

- `0x29`: `UNC_CHA_RxC_WBQ1_REJECT`, 5 records.
- `0xE0`-`0xE5` and `0xe4`: CMS receive-ring ingress occupancy, insert, bypass, credit-starved, and busy-starved families.
- `0x3D`, `0x51`, `0x5C`, `0x5D`, and `0x6B`: snoop-filter eviction, snoops sent, snoop responses, local snoop responses, and miscellaneous snoop response cases.
- `0xD0`-`0xD7`: horizontal TxR credit-stall target-group families for AD and BL, agent groups 0/1, and target groups `TGR0`-`TGR10`.
- `0x35`: TOR insert events, 166 records.
- `0x36`: TOR occupancy events, 143 records.
- `0xA6`, `0xA7`, `0xA2`, and `0xA3`: horizontal TxR ADS-used, bypass, full-cycle, and not-empty-cycle families.

The common traffic-class suffixes in CMS and TxR records are `AD_ALL`, `AD_CRD`, `AD_UNCRD`, `AK`, `AKC_UNCRD`, `BL_ALL`, `BL_CRD`, `BL_UNCRD`, and `IV`. Target-group stall records use suffixes such as `TGR0` through `TGR10`, with separate base names encoding AD/BL and agent group.

## Control Flow

There is no local control flow in this JSON file. Runtime behavior is table-driven:

1. Perf build tooling reads architecture-specific PMU event JSON files under `tools/perf/pmu-events/arch/x86/`.
2. The Ice Lake Xeon event records are validated and converted into generated event tables.
3. At runtime, perf selects the matching CPU model and exposes matching `EventName` values through interfaces such as `perf list`.
4. When a user requests one of these symbolic events, perf resolves it to `EventCode`, `UMask`, `Unit`, `Counter`, and package-scope metadata.
5. The kernel uncore PMU support programs CHA counters on available package/home-agent instances and perf reports counts back to the user.

Within this chunk, the data layout encodes several repeated control patterns. A base event code identifies a hardware counter source, while suffix and umask select a subcondition. For example, `UNC_CHA_RxR_INSERTS.*` records share event code `0xE1` and differ by traffic class masks, while `UNC_CHA_TOR_INSERTS.*` records share `0x35` and use extended masks to qualify origin, opcode, hit/miss state, memory target, locality, and request type. `UNC_CHA_TOR_OCCUPANCY.*` mirrors many insert qualifiers with event code `0x36`, but occupancy is restricted to counter `0`.

## State and Persistence Behavior

The persistent state is the checked-in JSON metadata. The file does not allocate memory, perform I/O, mutate runtime process state, or store measurement results. Measurement state lives in hardware counters after perf programs them.

All records in this chunk are package-scoped CHA events, so consumers should treat counts as uncore/package activity rather than per-thread execution. The same package can expose multiple CHA instances; aggregation and filtering behavior depends on perf's uncore PMU implementation and the user's event syntax.

Counter availability is part of the state contract. The 319 non-occupancy records in this slice generally allow counters `0,1,2,3`, while the 143 TOR occupancy records allow only counter `0`. Event groups that overconstrain a single CHA PMU can fail to schedule or be multiplexed by perf.

The chunk boundaries are persistence hazards for downstream merge tooling. The first complete object begins before line 5371, and the last object continues after line 10335. Any final per-file report or validator must parse the full file, not the chunk as a standalone JSON fragment.

## Dependencies and Integration Points

This file integrates with Linux perf, not directly with CephFS runtime code. Key integration points are:

- Perf's PMU event JSON parser and generator, which expect full-file valid JSON and known schema keys.
- The `icelakex` CPU model mapping in the perf PMU events tree, which determines when these Ice Lake Xeon events are exposed.
- Kernel/perf support for CHA uncore PMUs, including package-scope counter discovery, counter constraints, and event programming.
- User-facing perf commands such as `perf list`, `perf stat -e`, and generated event documentation.
- Intel Ice Lake server uncore event definitions, which are the source of truth for event codes, umasks, descriptions, counter constraints, and deprecated aliases.
- Adjacent chunks of the same file. Earlier lines define the opening of the first WBQ reject object and preceding event families; later lines complete `UNC_CHA_TxR_HORZ_CYCLES_NE.BL_ALL` and continue the rest of the `uncore-cache.json` table.

For repository research, this chunk should merge into a final source-tree-aligned report for `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-cache.json` after all chunks for that file are complete.

## Risks and Edge Cases

The highest risk is silent metadata error. A wrong event code or umask can program a different hardware condition while still returning plausible counts. This is especially likely in this range because hundreds of TOR records differ only by long suffixes and extended masks.

The TOR families are easy to misinterpret. `UNC_CHA_TOR_INSERTS.*` counts entries inserted into TOR, while `UNC_CHA_TOR_OCCUPANCY.*` accumulates matching valid entries each cycle. Occupancy values are not raw request counts and generally need normalization by cycles, CHA count, and workload duration.

Some fields are intentionally absent or uneven. Several TOR qualifiers such as `DDR`, `HIT`, `MISS`, `MMCFG`, `NEARMEM`, `PMM`, and opcode-match variants omit `UMask` in this slice, while neighboring records carry large extended masks. Custom schema checks must distinguish valid optional omissions from accidental data loss. Descriptions are also repetitive and sometimes rely on hardware-documentation vocabulary that is not self-contained.

Deprecated and experimental markers matter. The chunk includes deprecated records such as `UNC_CHA_TOR_INSERTS.DDR4`, and most records are marked experimental. Tooling should preserve these flags so perf can warn or filter appropriately.

Counter constraints are uneven. TOR occupancy records are counter-0-only, while many surrounding records use any of counters 0-3. A perf command grouping multiple counter-0-only occupancy events may fail or multiplex differently than a group of insert events.

Line-range chunking is an edge case. Since this requested chunk starts and ends inside object bodies, line-local JSON parsing will fail even though the complete source file is valid. Research and validation should use full-file parsing plus line-aware inspection.

## Test Signals

High-signal validation for this chunk includes:

- `jq empty sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-cache.json` succeeds on the full file.
- Full-file parsing reports 1,111 top-level event objects.
- A line-range scan of 5371-10335 finds 462 `EventName` fields, all with `Unit: "CHA"` in the visible records.
- Representative event families are present with expected selectors: `UNC_CHA_RxC_WBQ1_REJECT.*` at `0x29`, `UNC_CHA_RxR_INSERTS.*` at `0xE1`, `UNC_CHA_TOR_INSERTS.*` at `0x35`, `UNC_CHA_TOR_OCCUPANCY.*` at `0x36`, and horizontal TxR events at `0xA2`, `0xA3`, `0xA6`, and `0xA7`.
- Perf PMU event table generation for the x86 `icelakex` directory succeeds without schema errors.
- On matching Ice Lake Xeon hardware, `perf list` exposes representative events from this range.
- `perf stat -e` can schedule simple individual events such as `UNC_CHA_TOR_INSERTS.IA_MISS_DRD`, `UNC_CHA_TOR_OCCUPANCY.IA_MISS_DRD`, `UNC_CHA_SNOOPS_SENT.REMOTE`, and `UNC_CHA_TxR_HORZ_CYCLES_FULL.AD_ALL`.
- Hardware sanity tests show expected directionality: TOR insert counts rise under memory traffic, occupancy rises under sustained queue pressure, snoop events rise under coherence-heavy traffic, and horizontal TxR full/not-empty cycles rise under mesh egress pressure.

## Cross-Chunk Notes

This is a chunk-level artifact only. It should not be treated as the final per-file research document.

The preceding chunk is needed for the complete opening object around `UNC_CHA_RxC_WBQ1_REJECT.LLC_OR_SF_WAY` and the earlier part of the `uncore-cache.json` table. The following chunk is needed to complete `UNC_CHA_TxR_HORZ_CYCLES_NE.BL_ALL` and the remaining horizontal transmit-ring/cache event definitions after line 10335.

### subset-b-006680: lines 10336-11977

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
