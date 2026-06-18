# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/cache.json

## Purpose

`cache.json` is the Arrow Lake cache and cache-adjacent memory event catalog consumed by perf's PMU event generator. It contains 209 JSON event records for the `cache` topic: 71 `cpu_atom`, 86 `cpu_core`, and 52 `cpu_lowpower` records. At build time, `tools/perf/pmu-events/jevents.py` reads this file, derives the topic name `cache` from the filename, and emits generated C table entries in `pmu-events.c`. At runtime, perf exposes these aliases through `perf list`, `perf stat`, `perf record`, and metric expressions that reference raw event names.

The file is selected for Arrow Lake by `arch/x86/mapfile.csv`, whose Arrow Lake entry maps `GenuineIntel-6-C[56]` version `v1.16` to the `arrowlake` model directory with event type `core`. This means the data becomes active when perf's x86 CPUID matching selects the Arrow Lake table.

## Important APIs, types, and data shape

The file is a top-level JSON array of event objects. The schema surface used by `jevents.py` is data-driven rather than function-based:

- `EventName`: perf alias such as `L2_RQSTS.MISS`, `MEM_LOAD_RETIRED.L3_MISS`, or `OCR.DEMAND_DATA_RD.L3_HIT.SNOOP_HITM`.
- `EventCode` and `UMask`: raw PMU selector fields rendered into perf event encodings.
- `Unit`: PMU scope selector, primarily `cpu_core`, `cpu_atom`, or `cpu_lowpower`; duplicate `EventName` values can intentionally exist with unit-specific encodings.
- `Counter` and optional `CounterMask`: constrain valid programmable counters or cycle-threshold forms.
- `SampleAfterValue`: default sampling period used by perf event aliases.
- `BriefDescription` and optional `PublicDescription`: user-facing descriptions shown by perf list and documentation-style output.
- Optional `MSRIndex` and `MSRValue`: extra model-specific register programming for latency threshold filters and offcore response filters.
- Optional `Data_LA`: marks events that support data linear-address sampling/precise load attribution in perf's generated metadata.

There are no metric definitions in this file; all records are event aliases. There are also no deprecated entries in this file.

## Event coverage

The catalog covers both P-core and E-core/low-power cache behavior. Major groups include:

- `L1D`, `L1D_MISS`, and `L1D_PENDING`: core L0/L1 replacement, fill-buffer pressure, L2 resource stalls, and outstanding load miss occupancy.
- `L2_LINES_IN`, `L2_LINES_OUT`, `L2_REQUEST`, and `L2_RQSTS`: L2 fills, evictions, hit/miss/reject accounting, code reads, demand data reads, and RFOs.
- `LONGEST_LAT_CACHE`: LLC references and misses across core, atom, and low-power PMUs.
- `MEM_LOAD_RETIRED`, `MEM_INST_RETIRED`, `MEM_UOPS_RETIRED`, and `MEM_LOAD_UOPS_RETIRED`: retired load/store/SW-prefetch aliases, split accesses, STLB hit/miss classification, load hit levels, and latency thresholds.
- `MEM_BOUND_STALLS_LOAD` and `MEM_BOUND_STALLS_IFETCH`: Atom and low-power stall classification for L2/LLC/local memory sources.
- `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, and `OCR.*`: offcore request classes, outstanding cycles, and filtered response categories.
- `LLC_PREFETCHES_THROTTLED`, `L2_PREFETCHES_THROTTLED`, and `SW_PREFETCH_ACCESS`: hardware/software prefetch activity and throttling.
- `LOCK_CYCLES.CACHE_LOCK_DURATION` and `SQ_MISC.BUS_LOCK`: locking and bus-lock visibility.

The file contains 154 unique event names, so about a quarter of the rows are unit variants or aliases that share a logical name but differ by PMU type.

## Control flow and integration

The control path is the perf PMU event pipeline:

1. `Makefile.perf` builds `libpmu-events.a` and runs the `pmu-events/Build` rules.
2. `pmu-events/Build` invokes `jevents.py` over `pmu-events/arch`.
3. `jevents.py` ignores `metricgroups.json`, then reads every other `.json` file in a model leaf directory. For this file it calls `read_json_events(item.path, "cache")`.
4. The parser converts each record into generated `struct pmu_table_entry` data, stores strings in the generated big C string table, and associates entries with the PMU unit.
5. Generated mapping code uses `arch/x86/mapfile.csv` to bind Arrow Lake CPUID strings to the generated Arrow Lake event table.
6. Runtime perf code in `util/pmu.c`, `builtin-list.c`, and `metricgroup.c` walks the generated tables to create aliases and resolve user-supplied event names.

Within this JSON file, array order is not a runtime control flow primitive, but it affects generated output ordering and therefore review diffs.

## State and persistence behavior

The file itself is static source data. It has no runtime mutable state and no persistence writes. Persistence happens indirectly when the build emits `pmu-events.c` into the perf output directory and compiles it into perf. Changes to any event record persist in the built binary until perf is rebuilt.

MSR-backed events carry important hidden state implications: aliases with `MSRIndex` `0x3F6` program load-latency threshold controls, while `OCR.*` records use `MSRIndex` `0x1a6,0x1a7` with large response-filter values. Those fields must stay aligned with the architectural event encodings or perf can program the wrong filter even though the JSON parses.

## Dependencies and integration points

Primary dependencies are `jevents.py`, `pmu-events/README`, `pmu-events/Build`, and `arch/x86/mapfile.csv`. Runtime consumers include perf PMU alias enumeration and metric formulas in neighboring Arrow Lake metric files, especially `arl-metrics.json`, which can reference event aliases defined here.

The file also depends on perf's JSON schema conventions: field names are case-sensitive, values are string-encoded even when they represent numbers, and PMU unit names must match Linux PMU names exposed in sysfs. The `cpu_core`, `cpu_atom`, and `cpu_lowpower` split is central on hybrid Arrow Lake systems.

## Risks and edge cases

The highest-risk rows are the offcore and latency-threshold aliases because they require correct `MSRIndex`/`MSRValue` pairing. A typo can silently produce an alias that lists correctly but measures the wrong response class or threshold. Unit-specific duplicates are also risky: changing only the `cpu_core` version of a shared name does not update `cpu_atom` or `cpu_lowpower` semantics. Consumers must specify or resolve the right PMU unit on hybrid systems.

Several records use `Data_LA`, especially retired memory-load aliases and load-latency aliases. Removing or adding this flag changes sampling capabilities and could affect users relying on data address capture. Counter restrictions such as `Counter: "2"` on `L1D_PENDING.*` must be preserved because invalid counter placement can fail at event scheduling time.

Descriptions are user-visible and often copied into generated C strings. Malformed JSON, missing commas, duplicate-but-inconsistent aliases, or non-string numeric fields can break `jevents.py` generation or produce confusing perf output.

## Test signals

Useful validation signals are:

- `jq empty sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/cache.json` for syntax.
- Running the perf PMU event generation path, for example the `pmu-events/Build` target or a normal `tools/perf` build for x86 with jevents enabled.
- `perf list cache` or `perf list --details` on an Arrow Lake-capable build to confirm aliases, descriptions, PMU units, and MSR extra config fields are emitted.
- `tools/perf/tests/pmu-events.c` and `tools/perf/tests/shell/stat_all_metricgroups.sh` as broad regression signals for generated event and metric tables.
- Targeted `perf stat -e` checks for representative aliases: `L2_RQSTS.MISS`, `MEM_LOAD_RETIRED.L3_MISS`, `MEM_UOPS_RETIRED.LOAD_LATENCY_GT_128`, and `OCR.DEMAND_DATA_RD.ANY_RESPONSE`.
