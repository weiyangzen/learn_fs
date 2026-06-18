# subset-b-006700 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/frontend.json

## Purpose

This file is the Meteor Lake x86 frontend PMU event catalog for `perf`. It is not executable code; it is a build-time JSON data table consumed by `tools/perf/pmu-events/jevents.py` when generating `pmu-events.c`. The generated tables let users refer to symbolic frontend event names instead of raw event selectors in `perf list`, `perf stat`, metric expressions, and related PMU alias paths.

The file contains 58 event records: 45 for `cpu_core` and 13 for `cpu_atom`. The records describe branch resteers, decode penalties, Decode Stream Buffer and MITE delivery, microcode sequencer activity, instruction-cache stalls, IDQ bubbles, and retired-instruction attribution for frontend-bound behavior. Several logical event names intentionally appear in both core and atom forms or as aliases with different encodings.

## Important schema fields and generated API surface

Each array entry is a PMU event definition. The fields used here line up with `JsonEvent` parsing in `jevents.py`:

- `EventName`: canonical symbolic event name, lowercased by `jevents.py` for generated table storage.
- `EventCode` and `UMask`: raw event selector material used to build perf event config strings.
- `Unit`: maps the event to the PMU namespace, primarily `cpu_core` or `cpu_atom`.
- `Counter`, `CounterMask`, `EdgeDetect`, and `Invert`: constrain valid counters or counting mode for events such as IDQ cycle aliases and stall-period edge detection.
- `MSRIndex` and `MSRValue`: program extra model-specific selectors for PEBS/PDIST style events, especially `FRONTEND_RETIRED.*`.
- `SampleAfterValue`: default sampling period metadata surfaced through perf's generated event aliases.
- `BriefDescription` and `PublicDescription`: short and long help text surfaced by `perf list` and Python/perf utility bindings.

No functions or types are defined locally. The relevant functions are external integration points: `read_json_events`, `JsonEvent`, `preprocess_one_file`, and `process_one_file` in `jevents.py` parse this file and emit generated `struct pmu_table_entry` data; `describe_metricgroup` is unrelated to this file but shares the same generation unit.

## Content and control flow

Build flow is data driven:

1. `jevents.py` walks `tools/perf/pmu-events/arch/x86/meteorlake`.
2. `frontend.json` is accepted because it is a `.json` file and is not `metricgroups.json`.
3. The filename becomes the event topic via `get_topic(item.name)`.
4. Each JSON object is converted into a `JsonEvent`, descriptions are normalized, unit names are mapped to PMU names, event/umask/MSR fields are translated to generated strings, and entries are appended to the pending event table for the Meteor Lake model directory.
5. At build time the generated `pmu-events.c` is compiled into perf; at runtime perf selects the correct CPU table and builds aliases for the matching PMU.

The file's records cluster around these event prefixes:

- `FRONTEND_RETIRED` has 30 records, covering atom attribution categories (`ALL`, `BRANCH_DETECT`, `BRANCH_RESTEER`, `CISC`, `DECODE`, `ICACHE`, `ITLB_MISS`, `OTHER`, `PREDECODE`) and core PDIST/PEBS-like retired-instruction qualifiers (`ANY_DSB_MISS`, `DSB_MISS`, `L1I_MISS`, `L2_MISS`, `STLB_MISS`, latency thresholds from 1 to 512 cycles, unknown branches, ANT branches, and microcode flows).
- `IDQ`, `IDQ_BUBBLES`, and `IDQ_UOPS_NOT_DELIVERED` records expose DSB/MITE/MS uop delivery, frontend bubble slots, zero-uop-delivered cycles, and frontend-ok aliases.
- `ICACHE`, `ICACHE_DATA`, and `ICACHE_TAG` records cover atom line access/miss events plus core data/tag stall cycles and stall periods.
- `BACLEARS`, `DECODE`, `DSB2MITE_SWITCHES`, and `MS_DECODED` describe branch predictor correction, length-changing prefix stalls, microcode sequencer busy cycles, and DSB-to-MITE switch penalties.

## State and persistence behavior

The JSON file has no mutable state. Its persistent effect is indirect: it becomes compiled data inside generated `pmu-events.c` and ultimately `pmu-events.o`/`libperf.a`. Any change to an event name, raw code, unit, counter mask, MSR selector, or description changes the generated perf alias database. Runtime state is held by perf's PMU alias and metric machinery, not by this source file.

The ordering in the JSON is not a runtime state machine, but it is still useful for review because related variants are grouped together. Generated output may be sorted or table-packed by `jevents.py`, so consumers should not depend on source order.

## Dependencies and integration points

Primary dependencies are the perf PMU event generation pipeline:

- `tools/perf/pmu-events/README` defines the JSON contract and explains that `jevents` runs before the perf binary is built.
- `tools/perf/pmu-events/jevents.py` parses event objects, recognizes `EventName`, `BriefDescription`, `PublicDescription`, `Unit`, `EventCode`, `UMask`, `MSRIndex`, `MSRValue`, `Data_LA`, and other schema fields.
- `tools/perf/util/pmu.c`, `tools/perf/util/pmu.h`, `tools/perf/builtin-list.c`, and `tools/perf/util/metricgroup.c` consume the generated PMU tables for listing, alias creation, and metric evaluation.
- The x86 mapfile for Meteor Lake selects the generated table for matching CPU identifiers; this file is useful only when reachable through that mapping.

## Risks and maintenance notes

- `Unit` must match the actual PMU split on hybrid Meteor Lake systems. Mislabeling `cpu_core` versus `cpu_atom` can make events unavailable or incorrectly programmed.
- Reused `EventName` values across core and atom records are intentional but risky: edits must preserve the distinct `Unit`, `EventCode`, `UMask`, and optional MSR fields so perf selects the correct PMU-specific alias.
- `MSRIndex`/`MSRValue` pairs on `FRONTEND_RETIRED.*` records are fragile hardware contracts. A typo can compile cleanly while producing invalid sampling or misleading frontend attribution.
- Alias records such as `IDQ_BUBBLES.CYCLES_0_UOPS_DELIV.CORE` and `IDQ_UOPS_NOT_DELIVERED.CYCLES_0_UOPS_DELIV.CORE` share encodings and descriptions. Updating only one side creates documentation drift.
- Descriptions are user-facing. Typos or ambiguous wording propagate directly to `perf list` output and generated Python dictionaries.

## Test and validation signals

Useful checks are structural and generated-output oriented:

- `jq` parsing should confirm valid JSON and the expected 58 records.
- A perf build that runs `jevents.py` should regenerate `pmu-events.c` without schema errors.
- `perf list` on a matching Meteor Lake system or generated table test should show representative events such as `frontend_retired.dsb_miss`, `idq.dsb_uops`, `icache_data.stalls`, and `baclears.any` under the correct PMU.
- Existing perf tests under `tools/perf/tests/pmu-events.c` and metric parsing tests are the closest automated regression signals for generated PMU event tables.
- Review should compare core/atom encodings against Intel event documentation, especially all `FRONTEND_RETIRED.*` MSR selectors and IDQ counter-mask/invert combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/memory.json

## Purpose

This file is the Meteor Lake x86 memory PMU event catalog for `perf`. It provides build-time JSON metadata that `jevents.py` converts into generated PMU alias tables. The events let perf users inspect memory stalls, load latency sampling, machine clears, offcore request behavior, page splits, and DRAM/L3 miss attribution through symbolic names.

The file contains 39 records: 24 for `cpu_core` and 15 for `cpu_atom`. It covers both core PMU events and atom/offcore response style events, including cases where the same logical event name has different encodings for `cpu_core` and `cpu_atom`.

## Important schema fields and generated API surface

The file uses the standard perf PMU JSON event schema:

- `EventName`: symbolic event name used as the generated perf alias.
- `EventCode` and `UMask`: raw event selectors. Some core offcore response entries use multi-code strings such as `0x2A,0x2B`, while atom OCR entries use `0xB7`.
- `Unit`: selects `cpu_core` or `cpu_atom`.
- `Counter` and `CounterMask`: restrict eligible counters and define threshold/cycle counting behavior for activity and outstanding-request events.
- `Data_LA`: marks events that support address capture when precise, used by `jevents.py` to append extra description text.
- `MSRIndex` and `MSRValue`: program latency thresholds (`0x3F6`) or offcore response selectors (`0x1a6,0x1a7`).
- `SampleAfterValue`: default sampling period, especially important for rare high-latency events where the values are deliberately small.
- `BriefDescription` and `PublicDescription`: user-visible help text.

There are no local functions. The external API is the generated PMU event table created by `jevents.py` and consumed by perf PMU alias, list, stat, and metric code.

## Content and control flow

Build-time control flow is the same as other topic files:

1. The pmu-events walker enters the Meteor Lake model directory.
2. `memory.json` is treated as a regular topic event file.
3. `read_json_events` parses the array, and each object becomes a `JsonEvent`.
4. `JsonEvent` converts the schema fields into generated event strings and descriptions.
5. The generated table is compiled into perf; runtime perf table selection depends on CPU/mapfile matching and PMU unit names.

The records are organized around these prefixes:

- `CYCLE_ACTIVITY` and `MEMORY_ACTIVITY` expose core cycles/stalls while L1D, L2, or L3 miss demand loads are outstanding.
- `LD_HEAD` atom records count retirement stalls for the oldest load, split by L1 miss, page walk, store-address block, other block cases, and aggregate buckets.
- `MACHINE_CLEARS.MEMORY_ORDERING` appears for both atom and core with the same event/umask but different descriptions and sample periods.
- `MEM_TRANS_RETIRED` has load-latency thresholds from greater-than 4 cycles through greater-than 2048 cycles, plus `STORE_SAMPLE`. These records use `Data_LA` and MSR threshold values.
- `MISALIGN_MEM_REF` tracks atom 4K page-split loads and stores.
- `OCR` records count atom and core offcore response categories for demand code reads, demand data reads, and RFOs supplied by DRAM or missing L3.
- `OFFCORE_REQUESTS` and `OFFCORE_REQUESTS_OUTSTANDING` expose core L3-miss demand-data-read request counts and pending-cycle behavior.

## State and persistence behavior

The file is static source data. It stores no runtime state and has no side effects until the perf build runs `jevents.py`. After generation, the state persists as compiled PMU table entries in `pmu-events.c` and libperf-linked object code. Runtime perf commands use those entries to configure PMU counters and, for events with MSR selectors, to program associated model-specific registers.

Because many events encode thresholds in `MSRValue`, the persistent behavior is not just documentation: the numbers directly affect what the hardware counts. For example, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_64` and `LOAD_LATENCY_GT_2048` differ primarily through the MSR threshold and default sample period.

## Dependencies and integration points

The file depends on:

- `jevents.py` support for `Data_LA`, MSR selectors, multi-part `EventCode` values, `CounterMask`, and PMU unit mapping.
- x86 PMU hardware behavior for Meteor Lake core and atom PMUs.
- offcore response programming for `MSRIndex` `0x1a6,0x1a7`, and load-latency threshold programming through `0x3F6`.
- perf list/stat/record paths that expose aliases and program counters from generated tables.
- metric formulas in nearby Meteor Lake metric JSON files that may reference these event names for memory-bound, DRAM-bound, and load/store-bound topdown categories.

## Risks and maintenance notes

- `Data_LA` and MSR threshold events compile even if the threshold is wrong; bad values silently shift the meaning of load latency sampling.
- Very low `SampleAfterValue` values for high-latency thresholds are intentional. Normalizing them to common periods would make rare-event sampling less useful.
- Hybrid PMU duplication is easy to break. `OCR.DEMAND_DATA_RD.DRAM`, `OCR.DEMAND_DATA_RD.L3_MISS`, and `OCR.DEMAND_RFO.L3_MISS` have both atom and core records with different event codes/counter sets.
- Offcore response `MSRValue` masks are dense bitfields. They should be reviewed against vendor documentation instead of inferred from neighboring rows.
- The `MACHINE_CLEARS.MEMORY_ORDERING` core public description contains a typo ("dye"). Fixes are safe for help text but should be separated from semantic encoding changes for review clarity.
- Multi-code `EventCode` values depend on parser support that takes the first code for numeric handling while preserving generated event strings; changes here need generated-output inspection.

## Test and validation signals

Good validation includes:

- `jq` syntax validation and record count check for 39 event objects.
- A perf build running `jevents.py` without warnings or generated C syntax errors.
- Generated-table or `perf list` inspection for representative aliases such as `mem_trans_retired.load_latency_gt_64`, `memory_activity.stalls_l3_miss`, `ocr.demand_data_rd.dram`, and `offcore_requests.l3_miss_demand_data_rd`.
- Hardware smoke tests on a Meteor Lake system, checking that core-only events bind to `cpu_core` and atom-only OCR/page-split events bind to `cpu_atom`.
- Existing `tools/perf/tests/pmu-events.c` coverage for generated events and metric parse tests for any metric formulas referencing these event names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/metricgroups.json

## Purpose

This file is the Meteor Lake metric group description map for perf PMU metrics. Unlike `frontend.json` and `memory.json`, it is not an event array. It is a JSON object mapping metric group names to human-readable descriptions. `jevents.py` treats files named `metricgroups.json` specially and emits a generated lookup table used by perf to describe metric groups.

The file contains 148 group entries. Most legacy group names map to "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet"; topdown level names map to level-specific descriptions; newer `tma_*_group` entries map to category-specific text such as "Metrics contributing to tma_frontend_bound category".

## Important schema fields and generated API surface

The schema is a flat string-to-string map:

- Key: metric group identifier, for example `Backend`, `Frontend`, `MemoryBound`, `TopdownL1`, `tma_frontend_bound_group`, or `tma_issueTLB`.
- Value: user-facing group description.

`jevents.py` special-cases the basename `metricgroups.json` in `preprocess_one_file`. For every map entry, it appends NUL-terminated group and description strings to the generated big C string table, stores offsets in `_metricgroups`, and later emits:

- `static const int metricgroups[][2]`, a sorted offset table.
- `const char *describe_metricgroup(const char *group)`, a binary-search lookup over the generated table.

No event counters are described in this file. There are no `EventName`, `MetricName`, `MetricExpr`, or PMU programming fields here.

## Content and control flow

Generation flow:

1. `jevents.py` sees `metricgroups.json` during the preprocessing walk.
2. The file is loaded as a JSON object, not as event records.
3. Each key is asserted to have length greater than one, then both key and description are stored in the generated string table with metric-string accounting.
4. `_metricgroups` is sorted when `print_metricgroups()` emits the C offset array.
5. Runtime callers use `describe_metricgroup(group)` to retrieve descriptions for display or return `NULL` when the group is unknown.

The map covers several naming generations:

- Broad spreadsheet-derived names such as `Backend`, `BadSpec`, `Frontend`, `MemoryBound`, `Retire`, `Summary`, and `TopdownL*` compatibility names.
- Short topical groups such as `DSB`, `FetchBW`, `FetchLat`, `IcMiss`, `Mem`, `MemoryBW`, `MemoryLat`, `Pipeline`, `Power`, and `PortsUtil`.
- TMA category groups such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_microcode_sequencer_group`, `tma_retiring_group`, and load/store TLB or utilization groups.
- Issue-link groups such as `tma_issueFB`, `tma_issueLat`, `tma_issueRFO`, and `tma_issueTLB`, whose descriptions identify related issue variables.

## State and persistence behavior

The file is static metadata. It persists into the generated `metricgroups` offset table and the big generated string table inside `pmu-events.c`. Runtime lookup is read-only binary search. There is no mutation, caching, or external storage owned by this JSON file.

The sorting and string offset assignment happen at generation time. That makes duplicate keys impossible in normal JSON object semantics after parsing, but it also means source order is not significant. Changing a description affects user-visible output but not PMU programming.

## Dependencies and integration points

Integration points include:

- `jevents.py` special-case logic for `item.name.endswith('metricgroups.json')`.
- `print_metricgroups()` and generated `describe_metricgroup()`.
- `perf list metricgroups`, metric display code, and Python helpers that present metric group names/descriptions.
- Metric definition files for Meteor Lake and generated Intel metrics that assign metrics into these groups via `MetricGroup` strings.

This file has a looser coupling than event JSON files: a group description can exist even if no current metric uses that group, and a metric can refer to a group missing from this map but then lose descriptive help text.

## Risks and maintenance notes

- Missing or misspelled group keys do not break PMU event programming, but they degrade `perf list` and metricgroup display quality.
- Renaming keys is externally visible because users and scripts may filter metrics by group name.
- Several group names are legacy or compatibility aliases with similar meanings (`MemoryBW` and `Memory_BW`, `MemoryLat` and `Memory_Lat`, `MachineClears` and `Machine_Clears`). Removing apparent duplicates can break existing metric references.
- The generic spreadsheet description is repeated many times. That is expected, but category-specific `tma_*_group` text should remain aligned with the corresponding metric category.
- Since lookup is sorted at generation time, tests should verify generated output rather than relying on JSON source order.

## Test and validation signals

Useful checks are:

- `jq` syntax validation and key count check for 148 entries.
- A perf build that regenerates `pmu-events.c` and emits the `metricgroups` table without duplicate/invalid string issues.
- `perf list metricgroups` or generated output inspection for representative groups such as `TopdownL1`, `Frontend`, `MemoryBound`, `tma_frontend_bound_group`, and `tma_memory_bound_group`.
- Metric parse/list tests should confirm metrics that reference these groups still display group descriptions.
- Review of group references in Meteor Lake metric files should catch stale names that are absent from this map or unused descriptions that may be obsolete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/metricgroups.json -->
