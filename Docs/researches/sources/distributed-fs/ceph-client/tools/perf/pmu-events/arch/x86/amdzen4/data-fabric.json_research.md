# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/data-fabric.json

## Purpose

`amdzen4/data-fabric.json` defines 136 Zen 4 data-fabric PMU events. It exposes DRAM data beats for local and remote processors, local/remote socket upstream I/O beats, socket inbound/outbound CPU fabric beats, and outbound link beats for package-level data movement analysis.

## Important records and schema

Records contain `EventName`, `EventCode`, `UMask`, `PublicDescription`, `Unit: DFPMC`, and `PerPkg: "1"`. The schema is uniform and package-scoped.

Important groups include:

- `local_processor_read_data_beats_cs0` through `cs11` and `local_processor_write_data_beats_cs0` through `cs11`: DRAM read/write data for the local processor by chip-select/channel-style suffix.
- `remote_processor_read_data_beats_cs0` through `cs11` and `remote_processor_write_data_beats_cs0` through `cs11`: DRAM read/write data for remote processors.
- `local_socket_upstream_read_beats_iom0` through `iom3` and write equivalents: local socket upstream DMA/I/O traffic.
- `remote_socket_upstream_read_beats_iom0` through `iom3` and write equivalents: remote socket upstream DMA/I/O traffic.
- `local_socket_inf{0,1}_{inbound,outbound}_data_beats_ccm0` through `ccm7` and remote equivalents: inbound/outbound data to/from CPU CCMs over socket interfaces.
- `local_socket_outbound_data_beats_link0` through `link7`: outbound data from all local socket links.

## Control flow and integration

The file is converted by `jevents.py` into AMD data-fabric PMU aliases using the `DFPMC` unit mapping. `amdzen4/recommended.json` builds many package-level bandwidth and fabric metrics by summing these aliases, such as DRAM read/write data for local/remote processors and local/remote socket inbound/outbound data.

## State and persistence

Static source data persists the exact mapping from event masks to data-fabric lanes/channels/links. The `PerPkg` flag is part of the contract and affects aggregation semantics.

## Dependencies

Dependencies include AMD Zen 4 data-fabric PMU definitions, perf's `DFPMC` support, package-scope event handling, and recommended metric formulas that reference large sums of these aliases.

## Risks

The large repeated matrix is vulnerable to copy/paste errors in suffixes, masks, or descriptions. Any missing channel or duplicated mask can skew aggregate bandwidth metrics. Because these counters are package-scoped and topology-dependent, tests on one socket layout may not cover all paths.

## Test signals

Run `jq empty`, generated PMU table checks, and metric expression parsing for all recommended data-fabric sums. Hardware validation should compare local versus remote memory/I/O workloads, verify channel/link sums increase on expected paths, and check `perf list` under the AMD data-fabric PMU.
