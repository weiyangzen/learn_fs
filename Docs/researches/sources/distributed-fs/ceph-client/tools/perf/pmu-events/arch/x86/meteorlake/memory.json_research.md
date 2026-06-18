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
