<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cmn/sys/cmn.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cmn/sys/cmn.json

## Purpose
This JSON file defines 33 Arm CMN uncore mesh events for the system PMU. It maps HN-F, RN-I/D, SBSX, HN-I, and related node events to `arm_cmn` event IDs and compatibility filters. The source was read as a complete 267-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `EventName` (33), `EventidCode` (33), `NodeType` (33), `BriefDescription` (33), `Unit` (33), `Compat` (33). Event names include `hnf_cache_miss`, `hnf_slc_sf_cache_access`, `hnf_cache_fill`, `hnf_pocq_retry`, `hnf_pocq_reqs_recvd`, `hnf_sf_hit`, `hnf_sf_evictions`, `hnf_dir_snoops_sent`, `hnf_brd_snoops_sent`, `hnf_slc_eviction`, `hnf_slc_fill_invalid_way`, `hnf_mc_retries`, and 21 more. Event ID values range from 0x1 to 0x30 in file order. Units are `arm_cmn`; compat patterns are `(434|436|43c|43a).*`.

## Control Flow, State, and Persistence
`jevents.py` handles `EventidCode`, `NodeType`, `Unit`, and `Compat` as uncore PMU metadata rather than core PMU event aliases. Generated tables let perf match the running CMN PMU implementation and expose node-specific events only when the compatible hardware is present. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include wrong node type encodings, compatibility regexes that hide valid CMN revisions or expose unsupported ones, and bandwidth/retry events whose units are misread as core events. Test signals include JSON parsing, `jevents.py` output inspection, `perf list arm_cmn`, and hardware smoke tests on supported CMN revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cmn/sys/cmn.json -->
