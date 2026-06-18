# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-cache.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006732`: lines 1-5272, `Docs/researches/chunks/subset-b-006732_research.md`
- `subset-b-006733`: lines 5273-8543, `Docs/researches/chunks/subset-b-006733_research.md`

## Chunk Research

### subset-b-006732: lines 1-5272

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-cache.json lines 1-5272

## Scope

This chunk covers the first 5,272 lines of `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-cache.json`, a Linux `perf` PMU event metadata table for Snow Ridge X x86 uncore cache/home-agent events. The file is JSON data, not executable code: its exported interface is the event record schema consumed by the perf PMU event tooling and by users selecting named uncore events. The full file has 8,543 lines; this chunk ends in the middle of the `UNC_CHA_TOR_INSERTS.IA_MISS_CRD_PREF` record, so the merge lane must combine it with the following chunk before treating the JSON array as syntactically complete.

## Purpose

The chunk defines 490 `UNC_CHA_*` event names for the `CHA` unit. These records describe how perf should map human-readable event names to uncore hardware selectors for cache/home-agent monitoring: `EventCode`, optional `UMask`, counter availability, package scope, descriptions, and compatibility flags. Most events are marked `Experimental`, a few are `Deprecated`, and almost all are package-scoped via `PerPkg`.

The data is organized as a long array of event objects. Each object is one perf event variant or subevent. The `EventName` prefix groups related measurements, while the suffix after `.` names a subfilter such as traffic class, coherence state, ring direction, retry reason, hit/miss qualifier, or transgress selector.

## Schema And API Surface

Important fields in this chunk:

- `EventName`: primary public API. Perf users and higher-level metric tooling refer to strings such as `UNC_CHA_LLC_LOOKUP.READ_MISS`, `UNC_CHA_RxC_ISMQ0_RETRY.AD_REQ_VN0`, or `UNC_CHA_TOR_INSERTS.IA_HIT_RFO`.
- `EventCode`: raw hardware event selector. Many event families share one code and differentiate subevents through `UMask`.
- `UMask`: subevent bitmask or encoded filter. Simple families use powers of two; lookup/TOR families use wider composite masks such as `0xc001ffff`.
- `Counter`: allowed CHA counters. In this chunk, 489 records use `0,1,2,3`; `UNC_CHA_RxC_OCCUPANCY.IRQ` is counter `0` only.
- `Unit`: always `CHA` in this chunk, binding records to the CHA uncore PMU rather than core PMUs or memory-controller PMUs.
- `PerPkg`: almost always `1`, indicating package-scoped aggregation/availability.
- `BriefDescription` and `PublicDescription`: user-visible descriptions surfaced by perf event listing and documentation generation. `PublicDescription` often contains critical caveats that are not inferable from the event name.
- `Experimental`: present on 464 records, signaling event stability or documentation confidence risk.
- `Deprecated`: present on 7 records, redirecting old names to newer aliases.

There are no functions or types in the source file. The implicit type is a perf PMU JSON event object, and the main compatibility contract is field spelling plus valid JSON array syntax.

## Event Families In This Chunk

The opening section defines CMS agent credit acquisition and occupancy events for agent 0/1, AD/BL channels, and transgress selectors 0-10. These include families such as `UNC_CHA_AG0_AD_CRD_ACQUIRED0`, `UNC_CHA_AG0_AD_CRD_OCCUPANCY0`, `UNC_CHA_AG1_BL_CRD_ACQUIRED1`, and related variants. They all target `CHA`, use counters `0,1,2,3`, and encode transgresses through `UMask` bits.

The next major group covers CHA bypass, clock, snoop, direct-GO, distress, egress, and ring-use behavior. Examples include `UNC_CHA_BYPASS_CHA_IMC`, `UNC_CHA_CLOCKTICKS`, `UNC_CHA_CMS_CLOCKTICKS`, `UNC_CHA_CORE_SNP`, `UNC_CHA_DIRECT_GO`, `UNC_CHA_DIRECT_GO_OPC`, `UNC_CHA_DISTRESS_ASSERTED`, `UNC_CHA_EGRESS_ORDERING`, and horizontal ring-use families for AD, AK, AKC, BL, and IV. Public descriptions for the ring events explain left/right, even/odd, clockwise/counter-clockwise behavior, which matters when interpreting per-CHA tile counts.

The LLC and snoop-filter region is centered on `UNC_CHA_LLC_LOOKUP`, the largest family in this chunk with 41 variants. It includes request classes, hit/miss variants, MESI/F-state selectors, local/remote home qualifiers, and deprecated aliases. The descriptions warn that lookup filtering is nonstandard: state bits must be selected or the event may count nothing, and some requests may increment multiple times if they perform multiple lookups. Related families include `UNC_CHA_LLC_VICTIMS`, `UNC_CHA_SF_EVICTION`, `UNC_CHA_SNOOPS_SENT`, `UNC_CHA_SNOOP_RESP_LOCAL`, and `UNC_CHA_SNOOP_RSP_MISC`.

Memory-controller-facing CHA traffic is represented by `UNC_CHA_IMC_READS_COUNT` and `UNC_CHA_IMC_WRITES_COUNT`, covering normal/priority reads and full/partial writes. These are still CHA-unit events even though the descriptions mention iMC/HA paths.

Request, retry, reject, and queue pressure families dominate the middle of the chunk. They include `UNC_CHA_PIPE_REJECT`, `UNC_CHA_READ_NO_CREDITS`, `UNC_CHA_REQUESTS`, `UNC_CHA_MISC`, `UNC_CHA_MISC_EXTERNAL`, `UNC_CHA_RxC_INSERTS`, `UNC_CHA_RxC_IRQ*_REJECT`, `UNC_CHA_RxC_ISMQ*_REJECT`, `UNC_CHA_RxC_ISMQ*_RETRY`, `UNC_CHA_RxC_OTHER*_RETRY`, `UNC_CHA_RxC_PRQ*_REJECT`, `UNC_CHA_RxC_REQ_Q*_RETRY`, and `UNC_CHA_RxC_OCCUPANCY`. These records expose reasons such as no AD/BL VN0 credit, non-UPI AK/IV injection failure, LLC/SF way conflicts, victims, physical-address matches, and allow-snoop gating.

Ring and response-router telemetry appears in `UNC_CHA_RING_BOUNCES_HORZ`, `UNC_CHA_RING_BOUNCES_VERT`, `UNC_CHA_RING_SINK_STARVED_HORZ`, `UNC_CHA_RING_SINK_STARVED_VERT`, `UNC_CHA_RING_SRC_THRTL`, and `UNC_CHA_RxR_*` families. `RxR` variants distinguish occupancy, inserts, bypass, busy starvation, and credit starvation across AD, BL, AK, AKC, and IV traffic classes.

The final visible section begins `UNC_CHA_TOR_INSERTS`, with 24 variants present before the chunk boundary. It defines TOR insertion counts for all requests, DDR, evictions, hits, IA-originated requests, CLFLUSH/CLFLUSHOPT, CRD/DRD/RFO types, hit/miss qualifiers, and page-walk PTE reads. The chunk stops after the `EventName` and `PerPkg` lines for `UNC_CHA_TOR_INSERTS.IA_MISS_CRD_PREF`; its `PublicDescription`, `UMask`, `Unit`, closing object, and following entries are outside this chunk.

## Control Flow And Consumption

Runtime control flow is external to this JSON file. Perf's PMU event build/listing path reads architecture/model JSON files, validates/parses each object, generates event tables or lookup data, and later resolves user-facing event names into raw event selectors. For any one event in this chunk, the effective flow is:

1. Select the Snow Ridge X PMU event map.
2. Match a user-supplied event name to `EventName`.
3. Bind the event to the `CHA` PMU because `Unit` is `CHA`.
4. Program one of the listed counters using `EventCode` plus `UMask` when present.
5. Apply package scope and report descriptions/flags in listing/help output.

The file itself has no branches, loops, runtime mutation, or persistence. Its order is nevertheless significant for reviewability and generated table determinism, and duplicate/deprecated aliases may intentionally coexist for compatibility.

## State And Persistence

The JSON records are static source-controlled state. They persist hardware event knowledge in the repository and are transformed by perf tooling into compiled metadata or installed event map files. There is no runtime state stored by this file, but downstream behavior depends on stable event names, masks, and descriptions. Renaming, deleting, or changing masks is a compatibility-impacting data change for scripts, dashboards, and tests that reference these event names.

Deprecated records preserve old public names while steering users to newer event names. Experimental flags preserve uncertainty/stability metadata and should not be stripped mechanically.

## Dependencies And Integration Points

Primary dependencies are the Linux perf PMU event JSON schema and the perf parser/generator that expects exact field names such as `BriefDescription`, `EventCode`, `EventName`, `UMask`, `Unit`, `Counter`, `PerPkg`, `Experimental`, and `Deprecated`. The source path places this data under `tools/perf/pmu-events/arch/x86/snowridgex`, so it integrates with the x86 Snow Ridge X model mapping rather than with Ceph runtime code despite living under the repository's `sources/distributed-fs/ceph-client` mirror.

Integration points include:

- `perf list` and generated event documentation, which expose names/descriptions.
- `perf stat` or similar event selection paths, which rely on event names resolving to valid raw CHA selectors.
- PMU event table generation tests that parse all JSON files and reject malformed arrays, invalid fields, or duplicate unintended names.
- Architecture model mapping files that decide when Snow Ridge X events are available.

## Risks And Edge Cases

The largest risk in this chunk is data correctness rather than algorithmic behavior. Incorrect `EventCode` or `UMask` values silently measure the wrong hardware condition. This risk is especially high for composite masks in `UNC_CHA_LLC_LOOKUP` and `UNC_CHA_TOR_INSERTS`, where many variants differ by small encoded bit changes.

Several `UNC_CHA_LLC_LOOKUP` descriptions require specific state/filter selections. If users or derived metrics compose these events without the required state bits, they can observe zero counts or misleading counts. The event may also count multiple increments for requests that perform multiple lookups, so it is not necessarily a one-request-one-count metric.

The 7 deprecated records are intentional compatibility aliases. Removing them may break old perf command lines; keeping them without clear replacement text may confuse users. This chunk includes deprecated LLC lookup aliases such as `CODE`, `DATA_RD`, `DATA_READ_ALL`, `DMND_READ_LOCAL`, `RFO_PREF_LOCAL`, and `WRITE_LOCAL`, plus `UNC_CHA_TOR_INSERTS.DDR4` pointing to `UNC_CHA_TOR_INSERTS.DDR`.

The chunk boundary is inside an object, so line-limited processing cannot parse this chunk alone as standalone JSON. Any validator for this chunk must either parse the complete source file or understand that this is a partial chunk artifact.

Nearly every record is package-scoped and counter `0,1,2,3`, but `UNC_CHA_RxC_OCCUPANCY.IRQ` is counter `0` only. Tooling that assumes all CHA events can use all four counters would mishandle this event.

Some descriptions contain legacy or platform-specific wording such as CBo, JKT, HA, CMS, ISMQ, PRQ, IRQ, TOR, and VN0. These are domain terms rather than local code identifiers; cleanup that rewrites descriptions for style could remove necessary hardware semantics.

## Test Signals

Useful validation signals for this chunk and the eventual merged file:

- The complete `uncore-cache.json` must parse as one valid JSON array; this chunk alone should not be required to parse independently because it ends mid-record.
- Every complete record in this chunk should have `EventName` and `Unit`, and `Unit` should remain `CHA`.
- Event names should remain unique unless perf intentionally permits aliases through deprecated records.
- `Deprecated` records should include replacement guidance in `BriefDescription` where available.
- `Counter` values should be checked against PMU capabilities; at minimum preserve the `Counter: "0"` special case for `UNC_CHA_RxC_OCCUPANCY.IRQ`.
- Composite `UMask` values in LLC lookup and TOR insertion families should be compared against authoritative vendor data or neighboring architecture files before modification.
- Perf-side generation tests should cover listing representative events from each major family: credit occupancy, LLC lookup, IMC reads/writes, RxC retry/reject, RxR occupancy/inserts, snoop responses, and TOR inserts.

### subset-b-006733: lines 5273-8543

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-cache.json lines 5273-8543

## Scope

This chunk is the tail of the Snow Ridge Xeon D `uncore-cache.json` PMU event table in the vendored Linux `tools/perf` tree. It is declarative JSON metadata, not executable CephFS logic. The complete file has one top-level JSON array of Intel uncore cache/home-agent event descriptors, and this chunk runs through the closing `]` at line 8543.

The line range starts inside the prior `UNC_CHA_TOR_INSERTS.IA_MISS_CRD_PREF` object: its `EventName` and `PerPkg` fields are on lines immediately before 5273, while its description, `UMask`, and `Unit` are inside this chunk. For chunk-level accounting, the visible tail from that split object through EOF contains 304 CHA event records, all `PerPkg: "1"` and `Unit: "CHA"`. Of those records, 262 are marked `Experimental`; 26 omit `UMask`; all visible records include `PublicDescription`.

## Purpose

The file supplies Linux perf's PMU event generator with symbolic event names and raw selector encodings for Snow Ridge uncore CHA counters. These records let users request events such as `UNC_CHA_TOR_INSERTS.IO_MISS`, `UNC_CHA_TOR_OCCUPANCY.IA`, `UNC_CHA_TxR_VERT_INSERTS0.AD_AG0`, or `UNC_CHA_XPT_PREF.SENT0` instead of manually constructing event-selector and umask strings.

This tail focuses on request tracking, mesh/ring traffic, writeback behavior, memory-controller credit pressure, and XPT prefetch activity:

- `UNC_CHA_TOR_INSERTS.*` counts successful Transaction Order Table inserts for request classes, request origins, and hit/miss filters.
- `UNC_CHA_TOR_OCCUPANCY.*` measures cycles or occupancy associated with matching TOR entries, using many of the same subfilters as inserts.
- `UNC_CHA_TxR_HORZ_*` and `UNC_CHA_TxR_VERT_*` describe horizontal and vertical transfer-ring occupancy, inserts, cycles-full, cycles-not-empty, bypass, nack, starvation, and AD/AK/AKC/BL/IV/TGC traffic classes.
- `UNC_CHA_VERT_RING_*_IN_USE.*` counts cycles when vertical AD, AK, AKC, BL, IV, and TGC rings are in use by direction and even/odd ring selection.
- `UNC_CHA_WB_PUSH_MTOI.*`, `UNC_CHA_WRITE_NO_CREDITS.*`, and `UNC_CHA_XPT_PREF.*` cover WbPushMtoI destination, iMC write-credit exhaustion by memory controller, and XPT prefetch sent/drop outcomes.

## Effective API And Schema

There are no functions or classes in this JSON file. The effective API is the perf PMU event schema consumed by `tools/perf/pmu-events/jevents.py` and exposed after generation through `struct pmu_event` and PMU event table lookup helpers in `pmu-events.h`.

Important fields in this chunk:

- `EventName` is the public symbolic name accepted by perf. Names are family-prefixed with `UNC_CHA_` and use suffixes to encode source, filter, direction, ring, agent, or memory-controller selection.
- `EventCode` is the base hardware event selector. The dominant families in this chunk use `0x35` for TOR inserts, `0x36` for TOR occupancy, `0x90`-`0x9E` for vertical TxR events, `0xA0`-`0xA7` for horizontal TxR events, `0xB0`-`0xB5` for vertical ring-in-use events, `0x56` for WbPushMtoI, `0x5A` for write-no-credits, and `0x6f` for XPT prefetches.
- `UMask` refines the event to a subevent. It may encode request origin (`IA`, `IO`, local/all), LLC hit/miss state, opcode class (`CRD`, `RFO`, `ITOM`, `PCIRDCUR`, `WCIL`, writeback variants), ring channel (`AD`, `AK`, `AKC`, `BL`, `IV`, `TGC`), agent (`AG0`, `AG1`), direction (`UP`, `DN`), or memory-controller filter. It is optional in this schema; 26 tail records omit it.
- `Counter` constrains counter placement. TOR inserts and all non-TOR ring/credit/prefetch records here use `0,1,2,3`; the TOR occupancy records use `0`.
- `Unit: "CHA"` binds every visible event to the Snow Ridge CHA uncore PMU.
- `PerPkg: "1"` marks all visible events as package-scoped.
- `Experimental: "1"` is common and should be preserved as a stability/documentation signal.
- `BriefDescription` and `PublicDescription` are user-facing perf list/help text. They often explain that TOR events exclude addressless requests such as locks and interrupts, and ring-in-use events count pass-by and sink cycles but not send-from-stop cycles.

The chunk contributes these visible event-family counts: 54 `UNC_CHA_TOR_INSERTS`, 71 `UNC_CHA_TOR_OCCUPANCY`, 76 horizontal TxR records, 72 vertical TxR records, 22 vertical ring-in-use records, 2 `UNC_CHA_WB_PUSH_MTOI`, 14 `UNC_CHA_WRITE_NO_CREDITS`, and 6 `UNC_CHA_XPT_PREF`.

## Event Groups

The TOR inserts section continues the large `EventCode: "0x35"` table. It covers IA miss/read/write filters (`IA_MISS_DRDPTE`, `IA_MISS_DRD_OPT`, `IA_MISS_RFO`, `IA_MISS_WCIL/F`, `IA_WBMTOI`, and related prefetch/writeback forms), IO request filters (`IO`, `IO_HIT`, `IO_MISS`, `ITOM`, `ITOMCACHENEAR`, `PCIRDCUR`, `RFO`, `WBMTOI`), interrupt and PRQ request classes, and aggregate location or attribute filters such as `LOC_ALL`, `LOC_IA`, `LOC_IO`, `NEARMEM`, `NONCOH`, and `MMCFG`.

The TOR occupancy section mirrors much of the TOR insert filter space under `EventCode: "0x36"` but with `Counter: "0"`. Its records are intended for occupancy/cycle attribution rather than insert counts. It includes aggregate DDR/hit/miss filters, IA and IO request classes, hit/miss variants, writeback and streaming write variants, interrupt/PRQ filters, local-source filters, near-memory/non-coherent filters, and opcode-matching placeholders.

The horizontal TxR section uses event codes `0xA0` through `0xA7`. Families classify horizontal ring behavior by AD, AK, AKC, BL, and IV traffic, and split some masks into credited and uncredited subchannels. These events describe occupancy, inserts, cycles full, cycles not empty, nack, bypass, starved, and address/data slots used. Most public descriptions call out a horizontal ring stop, with counts for packets passing by, sinking, or experiencing pressure conditions depending on family.

The vertical TxR section uses event codes `0x90` through `0x9E`. It is organized around agent/channel masks such as `AD_AG0`, `AD_AG1`, `AK_AG0`, `AK_AG1`, `BL_AG0`, `BL_AG1`, `IV_AG0`, plus the separate `_1` families for AKC agent counters and a `TGC` starvation selector. These events cover inserts, occupancy, cycles full, cycles not empty, nack, bypass, address/data slots used, and starvation on the vertical transfer resources.

The `UNC_CHA_VERT_RING_*_IN_USE` families use event codes `0xB0` to `0xB5` to count ring-use cycles by traffic class. AD, AK, AKC, BL, and TGC expose `UP_EVEN`, `UP_ODD`, `DN_EVEN`, and `DN_ODD` masks; IV exposes only `UP` and `DN`. The descriptions are topology-sensitive: Snow Ridge has clockwise and counter-clockwise vertical rings, and the mapping of UP/DN to physical ring direction changes between left and right sides of the ring.

The final tail records include `UNC_CHA_WB_PUSH_MTOI.LLC` and `.MEM` (`EventCode: "0x56"`) to distinguish whether WbPushMtoI data was pushed to LLC or memory, `UNC_CHA_WRITE_NO_CREDITS.MC0` through `.MC13` (`EventCode: "0x5A"`) to monitor lack of write credits from CHA into iMC channels, and `UNC_CHA_XPT_PREF.*` (`EventCode: "0x6f"`) to track XPT prefetch sends and drops due to no credits or AD CMS write-port contention.

## Control Flow And Runtime Integration

This JSON does not execute at runtime. The expected integration flow is:

1. `tools/perf/pmu-events/Build` includes PMU event JSON inputs during a perf build.
2. `tools/perf/pmu-events/jevents.py` reads model directories such as `arch/x86/snowridgex`, parses event objects, canonicalizes fields, and emits generated `pmu-events.c` data.
3. Generated tables use `struct pmu_event` and `struct pmu_events_table` interfaces from `pmu-events.h`.
4. `arch/x86/mapfile.csv` maps Snow Ridge CPU identifiers to the `snowridgex` model directory so perf can select these tables on matching hardware.
5. At runtime, perf event lookup resolves a user event name to its unit, event code, umask, counter constraints, descriptions, and flags, then the kernel/hardware PMU path owns actual counter programming and sampling.

Because this chunk is the end of one JSON array and begins inside an object, the merge lane must combine it with earlier chunks for whole-file syntax and semantic conclusions. Isolated parsing of only lines 5273-8543 is not valid JSON; full-file parsing is the meaningful validation signal.

## State And Persistence Behavior

The source file is checked-in static metadata. It does not allocate memory, mutate process state, record samples, or persist runtime measurements. Persistence is limited to the JSON source itself and generated perf tables produced during the build.

Runtime state exists only after perf programs hardware counters described by these records. `PerPkg: "1"` means the event should be interpreted at package scope, not as a normal per-core event. `Counter` constraints are part of the persisted contract because they govern which uncore counter slots can validly count each event family. `Experimental` flags persist lower-confidence or less-stable event status without removing the names from perf's public event namespace.

## Dependencies And Integration Points

- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/jevents.py` is the parser/generator that consumes fields used here, including optional `UMask`, `Experimental`, `PerPkg`, `Unit`, and descriptions.
- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/pmu-events.h` defines generated event table interfaces such as `struct pmu_event`, `pmu_events_table__for_each_event()`, `pmu_events_table__find_event()`, `perf_pmu__find_events_table()`, and `find_core_events_table()`.
- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/README` documents model directories, event JSON files, mapfile-driven table selection, and generated `pmu-events.c`.
- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/mapfile.csv` selects the Snow Ridge model directory for appropriate Intel family/model patterns.
- Kernel uncore PMU support for Snow Ridge CHA units must understand the same event-selector, umask, package scope, and counter-slot constraints represented by this metadata.

## Risks And Edge Cases

- The chunk boundary splits `UNC_CHA_TOR_INSERTS.IA_MISS_CRD_PREF`, so a chunk-local reader sees the object body without its `EventName`. Per-file reconciliation must include the previous chunk.
- `UMask` is intentionally absent on 26 records, including aggregate TOR filters and `WRITE_NO_CREDITS.MC8` through `.MC13`. Generators and tests must tolerate missing masks rather than treating them as malformed.
- The `WRITE_NO_CREDITS` memory-controller records are not ordered numerically (`MC10`-`MC13` appear between `MC1` and `MC2`) because the JSON order is lexicographic/string-derived. UI or documentation code should not infer topology order from file order.
- Many records are `Experimental`; scripts should avoid treating them as stable names unless the broader perf policy accepts experimental PMU aliases.
- Some descriptions are generic or repeated. For example the streaming-write insert descriptions mention data read from local IA and snoop-filter misses, while the event names distinguish full and partial streaming writes. Selector fields and event names are more reliable than prose for programming behavior.
- Ring direction descriptions are topology-dependent: UP/DN and even/odd do not map uniformly across all CHA stops. Aggregation across CHAs can hide this distinction if tooling treats masks as a single physical direction.
- `Counter: "0"` on all TOR occupancy records is a narrower constraint than the `0,1,2,3` used elsewhere. Ignoring it could lead to invalid event scheduling or confusing multiplexing failures.
- Any edit near the file tail must preserve JSON comma placement and the final closing bracket, because one syntax error disables generation for the entire Snow Ridge cache event table.

## Test Signals

Useful validation signals for this chunk and the later merged per-file report include:

- `python3 -m json.tool sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-cache.json` succeeds on the full file.
- The complete file parses to 793 event objects; the reconciled tail from `UNC_CHA_TOR_INSERTS.IA_MISS_CRD_PREF` through EOF accounts for 304 CHA records.
- All 304 tail records have `Unit: "CHA"` and `PerPkg: "1"`; 233 have `Counter: "0,1,2,3"` and 71 TOR occupancy records have `Counter: "0"`.
- The generator accepts records with missing `UMask`, including aggregate TOR filters and `WRITE_NO_CREDITS.MC8`-`.MC13`.
- Representative perf-list/generated-table lookups include `UNC_CHA_TOR_INSERTS.IO_MISS`, `UNC_CHA_TOR_OCCUPANCY.IA_MISS_RFO`, `UNC_CHA_TxR_HORZ_OCCUPANCY.BL_ALL`, `UNC_CHA_TxR_VERT_INSERTS0.AD_AG0`, `UNC_CHA_VERT_RING_TGC_IN_USE.UP_ODD`, `UNC_CHA_WRITE_NO_CREDITS.MC7`, and `UNC_CHA_XPT_PREF.DROP1_NOCRD`.
- Tests or review should preserve the final array terminator at line 8543 and should validate the full source file, not this line range alone.
