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
