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
