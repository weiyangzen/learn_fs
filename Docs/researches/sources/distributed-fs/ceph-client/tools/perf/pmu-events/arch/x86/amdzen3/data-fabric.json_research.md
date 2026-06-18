# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/data-fabric.json

## Purpose

`amdzen3/data-fabric.json` defines 12 Zen 3 data-fabric PMU events for package-level traffic accounting. It exposes remote outbound data-controller counters and DRAM channel data-controller counters used to estimate data-fabric link traffic and aggregate DRAM bandwidth.

## Important records and schema

Records contain `EventName`, `EventCode`, `UMask`, `PublicDescription`, `Unit: DFPMC`, and `PerPkg: "1"`. The `DFPMC` unit tells perf these are AMD data-fabric PMU events rather than core events, and `PerPkg` marks package-scoped counting.

Important records include:

- `remote_outbound_data_controller_0` through `_3`: remote link outbound data, each with event code `0x5d`, different unit masks, and public descriptions noting approximate outbound bytes for a node/die.
- `dram_channel_data_controller_0` through `_7`: DRAM channel byte counters for NPS1 node/die aggregation, with event code `0x38` and masks for individual channels.

## Control flow and integration

`jevents.py` maps `Unit: DFPMC` to the AMD data-fabric PMU. During event generation the package-scoped flag is persisted into the generated table, so perf can aggregate the event at the right scope. `amdzen3/recommended.json` defines `all_remote_links_outbound` and `nps1_die_to_dram` by summing these aliases.

## State and persistence

The file is immutable source metadata. Persistent semantics include the unit mask to channel/link mapping and the package-level scope. Changes alter how perf interprets data movement across dies, memory channels, and remote links.

## Dependencies

Dependencies are AMD Zen 3 data-fabric PMU definitions, perf's `DFPMC` mapping, and metric expressions in `recommended.json` that sum these counters.

## Risks

The descriptions use "Approximate", so downstream users should avoid treating these as exact byte accounting in all topology modes. Incorrect `PerPkg` or `Unit` metadata would cause perf to program the wrong PMU or aggregate at the wrong level. Channel-count assumptions are topology-sensitive.

## Test signals

Validate JSON and generated PMU tables, check `perf list amd_df` aliases on matching hardware, and run metric parser tests for the recommended data-fabric formulas. Hardware validation should compare DRAM channel sums with known memory bandwidth workloads and expected NPS/topology behavior.
