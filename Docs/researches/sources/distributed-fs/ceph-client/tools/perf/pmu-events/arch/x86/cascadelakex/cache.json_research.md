# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/cache.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006638`: lines 1-6675, `Docs/researches/chunks/subset-b-006638_research.md`
- `subset-b-006639`: lines 6676-13381, `Docs/researches/chunks/subset-b-006639_research.md`
- `subset-b-006640`: lines 13382-13416, `Docs/researches/chunks/subset-b-006640_research.md`

## Chunk Research

### subset-b-006638: lines 1-6675

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/cache.json lines 1-6675

## Scope

This chunk is the first 6,675 lines of the Cascadelake-X `cache.json` PMU event table used by Linux `perf`'s `pmu-events` generation path. The full file is a JSON array; this chunk starts at the opening `[` and reaches the middle of the deprecated `OFFCORE_RESPONSE.ALL_PF_DATA_RD.L3_HIT.HITM_OTHER_CORE` record. The complete object continues through line 6678, so the merge lane must use the adjacent chunk for the final fields and closing delimiter of that record.

Within the complete objects visible through this range, the chunk contains 666 event records. The first complete event is `CORE_SNOOP_RESPONSE.RSP_IFWDFE`; the last complete event before the line-boundary continuation is `OFFCORE_RESPONSE.ALL_PF_DATA_RD.L3_HIT.ANY_SNOOP`.

## Purpose

The file is declarative data, not executable code. Its purpose is to describe cache, memory, and offcore-response performance monitoring events for Intel Cascadelake-X / Cooper Lake server CPUs. At build time, `tools/perf/pmu-events/jevents.py` reads JSON event descriptions from `tools/perf/pmu-events/arch/<arch>/<model>/`, converts each event into generated C tables in `pmu-events.c`, and links those tables into `perf`. At runtime, `perf list`, event alias lookup, and metric/event parsing use those generated tables so users can request named events instead of raw event/umask/MSR encodings.

This chunk is heavily weighted toward cache hierarchy and offcore memory-source observability:

- Core snoop response and IDI writeback hints.
- L1D pending-miss, fill-buffer, and replacement events.
- L2 line movement and L2 request classes.
- Last-level-cache reference/miss events with Skylake-family errata annotation.
- Retired memory instruction and precise memory-load events.
- A large matrix of `OCR.*` offcore-response events.
- Deprecated `OFFCORE_RESPONSE.*` aliases that point to newer `OCR.*` names.

## Data Schema And Important Fields

Each JSON object is an event descriptor consumed as a `JsonEvent` by `jevents.py`. In this chunk, every visible complete record carries `BriefDescription`, `Counter`, `EventCode`, `EventName`, `SampleAfterValue`, and `UMask`. The common schema fields and their integration meaning are:

- `EventName`: User-facing perf alias, lowercased by `jevents.py` when generating internal event names.
- `EventCode`: Raw architectural/per-model event selector. For offcore response events this is commonly `0xB7, 0xBB`; `jevents.py` uses the first code when composing the generated event string.
- `UMask`: Unit mask appended as `umask=` in the generated perf event syntax.
- `Counter`: Programmable counters where the event is valid. This chunk generally uses `0,1,2,3`.
- `SampleAfterValue`: Default sampling period emitted as `period=`.
- `CounterMask`: Present on cycle-threshold style events such as `L1D_PEND_MISS.PENDING_CYCLES` and offcore-outstanding cycle events; emitted as `cmask=`.
- `AnyThread`: Present on `L1D_PEND_MISS.PENDING_CYCLES_ANY`; emitted as `any=1`.
- `PEBS`: Marks precise-event support on retired memory/load events. `jevents.py` adds precise-event text to descriptions and exposes precision capability to perf.
- `Data_LA`: Present on load-address capable precise events in the memory-load families.
- `Errata`: Present on `LONGEST_LAT_CACHE.MISS` and `LONGEST_LAT_CACHE.REFERENCE` with `SKL057`; `jevents.py` appends the spec-update note to generated descriptions.
- `MSRIndex` and `MSRValue`: Present on offcore response events. `MSRIndex` is `0x1a6,0x1a7` in this chunk, selecting the two offcore response MSRs. `MSRValue` encodes request type, supplier, cache state, and snoop response filters. `jevents.py` maps the MSR index via `lookup_msr()` and appends the MSR programming term plus value into the generated event string.
- `Deprecated`: Present on 51 visible records, mostly legacy `OFFCORE_RESPONSE.*` aliases that refer users to equivalent `OCR.*` event names.

## Event Families In This Chunk

The first section describes direct core/cache counters:

- `CORE_SNOOP_RESPONSE.*` records count instruction/data snoop response classes such as forward modified/exclusive, hit forward shared/exclusive, and hit invalid.
- `IDI_MISC.WB_DOWNGRADE` and `IDI_MISC.WB_UPGRADE` describe cache-line writeback allocation/drop behavior into L3.
- `L1D.REPLACEMENT` and `L1D_PEND_MISS.*` cover L1D line replacement, fill-buffer pressure, outstanding L1D miss duration, and cycles with pending demand-read misses.
- `L2_LINES_IN.*`, `L2_LINES_OUT.*`, `L2_RQSTS.*`, and `L2_TRANS.L2_WB` describe L2 fills, writebacks, request references, misses, hits, prefetches, RFO traffic, and code reads.
- `LONGEST_LAT_CACHE.MISS` and `LONGEST_LAT_CACHE.REFERENCE` provide LLC miss/reference aliases with `SKL057` errata metadata.

The memory-retirement section provides precise load/store observability:

- `MEM_INST_RETIRED.*` counts retired load/store classes including all loads/stores, locks, split loads/stores, and STLB-miss loads/stores.
- `MEM_LOAD_L3_HIT_RETIRED.*` and `MEM_LOAD_L3_MISS_RETIRED.*` split retired load sources by L3 snoop outcomes and local/remote DRAM, PMM, forwarded, and HITM outcomes.
- `MEM_LOAD_MISC_RETIRED.UC` and `MEM_LOAD_RETIRED.*` cover uncacheable loads plus FB, L1, L2, L3, miss, and local PMM classes.

Most of the chunk is an offcore-response matrix:

- `OCR.ALL_DATA_RD.*`, `OCR.ALL_PF_DATA_RD.*`, `OCR.ALL_PF_RFO.*`, `OCR.ALL_READS.*`, `OCR.ALL_RFO.*`, `OCR.DEMAND_CODE_RD.*`, `OCR.DEMAND_DATA_RD.*`, `OCR.DEMAND_RFO.*`, `OCR.OTHER.*`, `OCR.PF_L1D_AND_SW.*`, `OCR.PF_L2_DATA_RD.*`, `OCR.PF_L2_RFO.*`, `OCR.PF_L3_DATA_RD.*`, and `OCR.PF_L3_RFO.*` all use offcore MSR filters to classify request type against supplier/cache-state/snoop-result dimensions.
- The repeated dimensions include `L3_HIT`, `L3_HIT_E`, `L3_HIT_F`, `L3_HIT_M`, `L3_HIT_S`, plus response outcomes such as `ANY_SNOOP`, `HITM_OTHER_CORE`, `HIT_OTHER_CORE_FWD`, `HIT_OTHER_CORE_NO_FWD`, `NO_SNOOP_NEEDED`, `SNOOP_HIT_WITH_FWD`, `SNOOP_MISS`, and `SNOOP_NONE`.
- `OFFCORE_REQUESTS.*`, `OFFCORE_REQUESTS_BUFFER.SQ_FULL`, and `OFFCORE_REQUESTS_OUTSTANDING.*` provide non-MSR request counts, store-queue/full pressure, outstanding counts, and cycle-qualified variants.
- Deprecated `OFFCORE_RESPONSE.ALL_DATA_RD.*` and the start of deprecated `OFFCORE_RESPONSE.ALL_PF_DATA_RD.*` mirror the newer `OCR.*` matrix and keep compatibility for existing perf event names.

## Control Flow And Integration Points

There is no local control flow in this JSON file. The effective control flow is in the surrounding perf build and runtime path:

1. `tools/perf/pmu-events/Build` includes JSON files under `pmu-events/arch` as dependencies of generated `pmu-events.c`.
2. `jevents.py` parses each object, normalizes names/descriptions, canonicalizes numeric values, converts known fields into perf syntax, and emits generated C tables.
3. `arch/x86/mapfile.csv` maps Intel family/model pattern `GenuineIntel-6-55-[56789ABCDEF]` to model directory `cascadelakex`, allowing runtime CPU matching to select this event table.
4. `tools/perf/util/pmu.c`, `metricgroup`, and perf tests consume the generated `pmu-events.h` / `pmu-events.c` tables for event alias discovery and event string expansion.

For this chunk, the key transformation is from an object such as an `OCR.*` event with `EventCode`, `UMask`, `MSRIndex`, `MSRValue`, and `SampleAfterValue` into a generated event string that includes raw event selection, unit mask, period, and offcore MSR programming. Any wrong field value here becomes a wrong hardware counter programming sequence in perf.

## State And Persistence Behavior

The file persists static CPU event metadata in the source tree. It does not store runtime state. Build outputs generated from it are persisted separately as `pmu-events.c` and object/library artifacts under the perf output directory. Runtime state is limited to perf's programmed PMU counters and offcore response MSRs while a measurement is active.

The event table has compatibility state encoded in data:

- Deprecated aliases remain available through generated tables but are marked with `Deprecated`.
- Default sampling state is represented by `SampleAfterValue`.
- Precise-event capability and address support are represented by `PEBS` and `Data_LA`.
- Errata notes are carried into descriptions so users see hardware caveats when listing or selecting events.

## Dependencies

Direct dependencies are the perf PMU event schema and the parser behavior in `jevents.py`. The chunk relies on:

- JSON array/object syntax remaining valid across chunk boundaries.
- `jevents.py` understanding `EventCode`, `UMask`, `CounterMask`, `AnyThread`, `SampleAfterValue`, `PEBS`, `Data_LA`, `Errata`, `Deprecated`, `MSRIndex`, and `MSRValue`.
- x86 offcore response MSR mappings for `0x1a6` and `0x1a7`.
- `arch/x86/mapfile.csv` mapping Cascadelake-X CPUs to the `cascadelakex` directory.
- Perf's PMU alias lookup and event parser accepting the generated raw event strings.

The surrounding source file also depends on adjacent chunks for the rest of the JSON array, including the completion of the object crossing line 6675 and the remaining `OFFCORE_RESPONSE` aliases.

## Risks And Edge Cases

- The requested line range ends mid-object. Chunk-level consumers must not validate this line slice alone as a standalone JSON document. The merged file remains valid JSON, and the research merge lane should reconcile the partial `OFFCORE_RESPONSE.ALL_PF_DATA_RD.L3_HIT.HITM_OTHER_CORE` record with the next chunk.
- Offcore events are dense and repetitive. A single incorrect `MSRValue` can silently count the wrong request/snoop/source category while preserving valid JSON and build success.
- `EventCode` values containing `0xB7, 0xBB` are interpreted by `jevents.py` with the first code for generated event syntax; compatibility with both offcore response MSRs depends on the associated `MSRIndex` handling.
- Deprecated `OFFCORE_RESPONSE.*` aliases must remain synchronized with the indicated `OCR.*` replacement names. Drift can confuse users and tests that compare old and new aliases.
- `PEBS` and `Data_LA` records affect precise sampling expectations. Missing or extra flags can change whether perf reports an event as precise/address-capable.
- `Errata` annotations are user-visible risk signals; dropping them would not break parsing but would hide known hardware caveats.
- Default `SampleAfterValue` choices affect sampling behavior. Bad defaults can create unexpectedly high interrupt rates or poor sample density.

## Test Signals

Useful validation signals for this chunk and the eventual merged file include:

- `python3 -m json.tool sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/cache.json` succeeds for the full file.
- Building perf with jevents enabled regenerates `pmu-events.c` without schema/parser errors.
- `tools/perf` PMU event tests pass, especially generated event table tests under `tools/perf/tests/pmu-events.c`.
- `perf list` on a matching Cascadelake-X class system exposes representative names from this range, including `l1d_pend_miss.pending`, `mem_load_retired.l3_miss`, `ocr.demand_data_rd.*`, and deprecated `offcore_response.*` aliases.
- Spot checks compare generated event encodings against source fields: `umask=`, `cmask=`, `any=`, `period=`, and offcore MSR filter values should match the JSON.
- Deprecated alias checks verify that visible `OFFCORE_RESPONSE.*` records point to existing `OCR.*` replacements.

### subset-b-006639: lines 6676-13381

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/cache.json lines 6676-13381

## Scope

This chunk covers the middle-to-late portion of the Cascade Lake X `cache.json` PMU event table used by Linux `perf`. The assigned range starts inside the tail of an `OFFCORE_RESPONSE.ALL_PF_DATA_RD.L3_HIT.ANY_SNOOP` object and ends inside the beginning of the `SW_PREFETCH_ACCESS.ANY` object, so the merge lane must combine it with adjacent chunks before treating the file as a syntactically complete JSON array.

Within the range, the visible `EventName` entries are dominated by deprecated `OFFCORE_RESPONSE.*` aliases: 608 event records in this range have `Deprecated: "1"` and `MSRIndex: "0x1a6,0x1a7"`. The chunk also contains the complete `SQ_MISC.SPLIT_LOCK` event and the start of the `SW_PREFETCH_ACCESS.ANY` event. All entries are data declarations, not executable code.

## Purpose

The file supplies symbolic PMU event metadata for the Cascade Lake X x86 CPU model. During the `perf` build, `tools/perf/pmu-events/jevents.py` reads JSON files under `tools/perf/pmu-events/arch`, converts each event object into generated C tables in `pmu-events.c`, and those tables are compiled into `libperf.a`. At runtime, `perf` selects the CPU-matching event table and exposes aliases so users can request named events instead of raw event/umask/MSR encodings.

This chunk mainly preserves compatibility aliases for older `OFFCORE_RESPONSE.*` event names. Each deprecated alias points users toward a newer `OCR.*` name in `BriefDescription`, while retaining the raw offcore-response encoding fields needed for existing scripts, command lines, metric formulas, and tests that still refer to the old names. The final non-deprecated records add cache-related monitoring for split locks sent to uncore and software prefetch instructions.

## Important Data Fields and Event Families

The common schema fields visible here are `BriefDescription`, `Counter`, `Deprecated`, `EventCode`, `EventName`, `MSRIndex`, `MSRValue`, `PublicDescription`, `SampleAfterValue`, and `UMask`.

`EventName` is the user-facing symbolic alias. `jevents.py` lowercases it when constructing generated `pmu_event` records, so name stability matters even though the source uses uppercase Intel-style names.

`EventCode` is `0xB7, 0xBB` for the deprecated offcore-response records. The converter uses the first code as the base event code; the paired code and `MSRIndex` reflect that these events can use the offcore response selector MSRs `0x1a6` and `0x1a7`.

`MSRValue` is the key selector payload for the offcore-response aliases. It encodes the request type, response supplier, cache-hit state, snoop state, and related response filters. The value changes systematically across the generated alias matrix, for example between data read versus RFO/prefetch request classes and between `L3_HIT_*`, `PMM_HIT_LOCAL_PMM`, and `SUPPLIER_NONE` supplier buckets.

The offcore aliases in this range cover repeated combinations of request and response categories:

- Request classes: `ALL_PF_DATA_RD`, `ALL_PF_RFO`, `ALL_READS`, `ALL_RFO`, `DEMAND_CODE_RD`, `DEMAND_DATA_RD`, `DEMAND_RFO`, `OTHER`, `PF_L1D_AND_SW`, `PF_L2_DATA_RD`, `PF_L2_RFO`, `PF_L3_DATA_RD`, and `PF_L3_RFO`.
- Response/supplier classes: `ANY_RESPONSE`, `L3_HIT`, `L3_HIT_E`, `L3_HIT_F`, `L3_HIT_M`, `L3_HIT_S`, `PMM_HIT_LOCAL_PMM`, and `SUPPLIER_NONE`.
- Snoop/result classes: `ANY_SNOOP`, `HITM_OTHER_CORE`, `HIT_OTHER_CORE_FWD`, `HIT_OTHER_CORE_NO_FWD`, `NO_SNOOP_NEEDED`, `SNOOP_HIT_WITH_FWD`, `SNOOP_MISS`, `SNOOP_NONE`, and `SNOOP_NOT_NEEDED` where applicable.

`SQ_MISC.SPLIT_LOCK` uses `EventCode: "0xF4"` and `UMask: "0x10"` to count cache-line split locks sent to uncore. Unlike the offcore aliases, it is not deprecated and includes both brief and public descriptions.

`SW_PREFETCH_ACCESS.ANY` begins at the end of the chunk with `EventCode: "0x32"` and `UMask: "0xf"` in the following lines outside the assigned range. Its purpose is to count executed software prefetch instructions across `PREFETCHNTA`, `PREFETCHW`, `PREFETCHT0`, `PREFETCHT1`, and `PREFETCHT2`.

## Control Flow and Data Lifecycle

There is no runtime control flow in the JSON itself. The effective flow is the `perf` PMU event generation path:

1. The build system runs `pmu-events/jevents.py` before building the `perf` binary.
2. `jevents.py` walks architecture JSON files and parses each event object.
3. For each JSON object, it reads fields such as `EventName`, `BriefDescription`, `PublicDescription`, `EventCode`, `UMask`, `MSRIndex`, `MSRValue`, and `Deprecated`.
4. It resolves known MSR names/indexes, canonicalizes numeric encodings, lowercases event names, and emits generated C `struct pmu_event` table entries.
5. `pmu-events.c` is compiled into `pmu-events.o` and linked into `libperf.a`.
6. At runtime, `perf` picks the CPU table via the x86 mapfile and exposes the generated aliases through event parsing, `perf list`, Python bindings, and metric lookup paths.

For an offcore response event in this chunk, user selection of the alias causes perf to program the programmable counter with event code/umask plus the offcore-response selector MSR payload. The `Counter: "0,1,2,3"` field indicates the general-purpose counters available for these events on this model.

The deprecated aliases do not redirect mechanically at runtime. The deprecation marker and description are metadata surfaced to listing/reporting paths; the raw event fields remain usable. This makes the aliases backward-compatible while nudging users toward the newer `OCR.*` names.

## State and Persistence Behavior

The JSON file is persistent source data. It is transformed into generated C at build time and then embedded into the `perf` binary. Changing a field here can affect generated aliases, event encodings, displayed descriptions, deprecation status, metric resolution, and users' existing scripts.

No event counts or runtime measurement state are stored in this file. Runtime state lives in PMU hardware counters and offcore response MSRs configured by perf. `SampleAfterValue` is metadata for default sampling periods: the offcore and split-lock entries in this range use `100003`, while the software-prefetch family uses `2000003` outside the chunk tail.

Deprecation is persistent compatibility metadata. Removing a deprecated `OFFCORE_RESPONSE.*` record can break command lines or metric expressions that still reference it, even if a corresponding `OCR.*` event exists elsewhere in the file.

## Dependencies and Integration Points

This chunk depends on the perf PMU event JSON schema understood by `tools/perf/pmu-events/jevents.py`. The converter reads these fields directly, including `Deprecated`, `BriefDescription`, `PublicDescription`, `EventName`, `EventCode`, `UMask`, `MSRIndex`, and `MSRValue`.

The generated data integrates with:

- `tools/perf/pmu-events/Build`, which drives generation of `pmu-events.c`.
- `tools/perf/pmu-events/arch/x86/mapfile.csv`, which maps Cascade Lake X CPU identifiers to this model's event table.
- `tools/perf/util/pmu.c` and related PMU alias code, which consume generated event tables at runtime.
- `tools/perf/builtin-list.c`, which can print `Deprecated`, descriptions, encodings, and event names in JSON/list output.
- `tools/perf/tests/pmu-events.c`, which validates generated PMU event tables against expected entries.
- Intel offcore-response programming semantics for MSRs `0x1a6` and `0x1a7`.

The source tree is under a Ceph client snapshot, but this file is not Ceph-specific filesystem logic. It is a vendored Linux perf tooling data file used by performance analysis tooling.

## Risks and Edge Cases

The assigned chunk is not standalone JSON because it starts and ends within event objects. Any parser or merge process must use the full `cache.json` file or adjacent chunks, not this range alone.

The offcore-response aliases are highly repetitive. Copy/paste or generation mistakes in `MSRValue`, request class, supplier class, or snoop suffix can silently map a symbolic name to the wrong hardware filter. Such bugs are hard to detect from syntax alone because the JSON remains valid.

The `Deprecated: "1"` field is important compatibility metadata. Dropping it makes obsolete aliases appear current; dropping the whole record can break older perf invocations and metrics. Conversely, changing `BriefDescription` references to the wrong `OCR.*` replacement can mislead users during migration.

`EventCode: "0xB7, 0xBB"` and `MSRIndex: "0x1a6,0x1a7"` encode offcore-response programming behavior. Any change must preserve what `jevents.py` and perf PMU alias code expect, especially because the converter takes the first event code while retaining MSR-related metadata for encoding.

The names include subtle distinctions such as `SNOOP_HIT_WITH_FWD` versus `HIT_OTHER_CORE_FWD`, `NO_SNOOP_NEEDED` versus `SNOOP_NOT_NEEDED`, and `L3_HIT` versus `L3_HIT_E/F/M/S`. These suffixes are semantically meaningful for cache-coherency analysis and should not be normalized casually.

The tail events are not deprecated and have different semantics from offcore response aliases. `SQ_MISC.SPLIT_LOCK` uses a normal event/umask pair without `MSRIndex`, while `SW_PREFETCH_ACCESS.ANY` begins here but its object is completed in the next chunk.

## Test Signals

Useful validation for this chunk includes:

- Full JSON parsing of `cache.json`, not isolated chunk parsing, to catch boundary and comma/object errors.
- Running the perf PMU event generation path so `jevents.py` emits `pmu-events.c` without schema, numeric-conversion, or MSR lookup failures.
- `perf test` coverage for PMU events, especially table generation and alias comparison in `tools/perf/tests/pmu-events.c`.
- `perf list --json` or equivalent listing checks that deprecated aliases still expose `Deprecated: "1"` and the expected brief descriptions.
- Spot checks that representative `OFFCORE_RESPONSE.*` aliases map to the intended `MSRValue`, `EventCode`, `UMask`, counters, and offcore MSR indexes.
- Regression checks for old command lines such as deprecated `OFFCORE_RESPONSE.*` names and new command lines using the referenced `OCR.*` replacements.
- Hardware or simulator validation on Cascade Lake X-class systems for offcore-response filters, split-lock counting, and software-prefetch counting.
- Diff-based review against upstream Linux perf PMU event tables when importing or refreshing this vendored data.

## Cross-Chunk Notes

The preceding chunk contains the beginning of the first event object represented here, including the `EventName` and deprecation fields for `OFFCORE_RESPONSE.ALL_PF_DATA_RD.L3_HIT.ANY_SNOOP`. The next chunk contains the remaining `SW_PREFETCH_ACCESS.ANY` fields and following software-prefetch subevents. The final per-file report should describe this as part of a large generated-style PMU event matrix rather than as independent hand-written program logic.

### subset-b-006640: lines 13382-13416

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
