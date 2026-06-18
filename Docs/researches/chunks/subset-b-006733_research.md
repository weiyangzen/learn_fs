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
