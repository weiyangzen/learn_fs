# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/frontend.json

## Purpose

`frontend.json` defines Arrow Lake front-end PMU event aliases for branch resteers, decode restrictions, instruction cache stalls, microcode-sequencer delivery, decoded-stream-buffer versus MITE delivery, and retired instructions tagged with front-end causes. It contains 82 event records: 26 `cpu_atom`, 43 `cpu_core`, and 13 `cpu_lowpower`.

Perf consumes this file to let users diagnose front-end-bound behavior through symbolic event names such as `FRONTEND_RETIRED.L1I_MISS`, `IDQ.MITE_UOPS`, `BACLEARS.ANY`, and `ICACHE.MISSES`.

## Important APIs, types, and data shape

The file is a JSON array of PMU event records. Important fields include:

- `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and optional `CounterMask`.
- `Unit` for PMU selection across Arrow Lake core types.
- `BriefDescription` and optional `PublicDescription`.
- `MSRIndex` and `MSRValue` on many `FRONTEND_RETIRED.*` P-core aliases, especially latency and source-classification filters.
- `EdgeDetect` on `ICACHE_DATA.STALL_PERIODS` and `IDQ.MS_SWITCHES`.
- `Invert` on `IDQ_BUBBLES.CYCLES_FE_WAS_OK`.
- `Deprecated` on `IDQ_BUBBLES.CYCLES_0_UOPS_DELIV.CORE`.

There are 67 unique event names. The dominant prefix is `FRONTEND_RETIRED`, with 38 records.

## Event coverage

Atom and low-power front-end records include:

- `BACLEARS.*` for BTB correction/resteer categories such as conditional, indirect, return, and unconditional branches.
- `DECODE_RESTRICTION.PREDECODE_WRONG` on Atom.
- `FRONTEND_RETIRED.*` for retired instructions associated with branch detect, branch resteer, CISC, decode, icache, ITLB miss, predecode, and other front-end causes.
- `FRONTEND_RETIRED_SOURCE.*` on Atom for icache L2/L3 and ITLB STLB source buckets.
- `ICACHE.ACCESSES`, `.HIT`, `.MISSES`, and `MS_DECODED.*`.

P-core records include:

- `BACLEARS.ANY` for unknown branches.
- `DECODE.LCP` and `DECODE.MS_BUSY`.
- `DSB2MITE_SWITCHES.PENALTY_CYCLES`.
- `FRONTEND_RETIRED.*` source and latency-threshold aliases using `MSRIndex` `0x3F7`.
- `ICACHE_DATA.*` and `ICACHE_TAG.*` stall events.
- `IDQ.*` delivery counters for DSB, MITE, and MS sources.
- `IDQ_BUBBLES.*` starvation, fetch-latency, and zero-delivery cycle aliases.

## Control flow and integration

The build flow is the standard PMU event path. `jevents.py` derives topic `frontend`, parses all event objects, interns strings, and emits generated table entries. The generated table is selected for Arrow Lake through `arch/x86/mapfile.csv`.

Runtime consumers include:

- `perf list frontend` or raw event listing paths.
- `perf stat -e` aliases for branch and instruction-delivery analysis.
- Top-down and front-end metric formulas that combine aliases such as `IDQ_UOPS_NOT_DELIVERED`, `FRONTEND_RETIRED.*`, or related generated metrics.
- `describe_metricgroup()` output for related metric groups, although group descriptions are sourced from `metricgroups.json`.

The `MSRIndex` `0x3F7` records are effectively a mini-API for front-end retirement filtering. `jevents.py` preserves those fields into generated event encodings so perf can program the extra register values when users select the alias.

## State and persistence behavior

The JSON is static source data. Build output persists the records in generated C. Runtime state only appears when perf programs PMU counters and extra registers. P-core front-end retired events with `MSRIndex` `0x3F7` are stateful from a hardware-programming perspective because each alias selects a distinct filter value, such as latency thresholds from `LATENCY_GE_2` through `LATENCY_GE_512` or source categories like `L1I_MISS`, `ITLB_MISS`, and `UNKNOWN_BRANCH`.

The deprecated `IDQ_BUBBLES.CYCLES_0_UOPS_DELIV.CORE` alias preserves compatibility as an alias to `IDQ_BUBBLES.STARVATION_CYCLES`.

## Dependencies and integration points

Key dependencies are `jevents.py`, `pmu-events/README`, `arch/x86/mapfile.csv`, and the runtime PMU alias code in `util/pmu.c`. Hybrid PMU naming must match sysfs names for `cpu_core`, `cpu_atom`, and `cpu_lowpower`.

This file integrates strongly with top-down analysis. Front-end metric groups in `metricgroups.json` include `Frontend`, `Fed`, `FetchBW`, `FetchLat`, `IcMiss`, `Ifetch`, `DSB`, `DSBmiss`, `MicroSeq`, `tma_frontend_bound_group`, `tma_fetch_bandwidth_group`, `tma_fetch_latency_group`, `tma_icache_misses_group`, `tma_itlb_misses_group`, `tma_mite_group`, and `tma_microcode_sequencer_group`.

## Risks and edge cases

The highest-risk entries are `FRONTEND_RETIRED.*` P-core filters because many aliases share `EventCode` `0xc6` and depend on distinct `MSRValue` settings. A single wrong filter value can make a named alias measure another front-end condition. Latency threshold names must remain monotonically aligned with their threshold values.

`EdgeDetect` and `Invert` fields materially alter event semantics. For example, `ICACHE_DATA.STALL_PERIODS` counts stall periods rather than cycles, and `IDQ_BUBBLES.CYCLES_FE_WAS_OK` inverts the condition. These fields are easy to lose in bulk edits because most rows do not use them.

Hybrid-unit asymmetry is significant. Many P-core `IDQ` and `FRONTEND_RETIRED` aliases do not exist on Atom/low-power PMUs, while Atom exposes `FRONTEND_RETIRED_SOURCE.*` aliases not present on P-cores. Scripts should use PMU-qualified names or check availability.

## Test signals

Test with `jq empty`, a perf build with jevents enabled, and generated alias listing. Good representative aliases are `BACLEARS.ANY` across units, `FRONTEND_RETIRED.LATENCY_GE_64`, `IDQ.MS_SWITCHES`, `ICACHE_DATA.STALL_PERIODS`, and the deprecated `IDQ_BUBBLES.CYCLES_0_UOPS_DELIV.CORE`. Runtime validation should confirm extra MSR filters appear in `perf list --details` and that PMU-qualified aliases resolve on hybrid hardware.
