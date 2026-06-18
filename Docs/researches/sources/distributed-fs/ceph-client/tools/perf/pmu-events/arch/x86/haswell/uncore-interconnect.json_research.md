# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/uncore-interconnect.json

## Purpose

This file defines six Haswell uncore interconnect/ARB events. They count ARB tracker occupancy and request allocations for coherent and non-coherent core outgoing traffic, including all requests, cycles with any outstanding request, coherency tracker requests, and write transactions.

## Important APIs, Types, And Data

The records use `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and some `PublicDescription` fields. `Unit` is `ARB`, `PerPkg` is set, and counters are `0` or `0,1`. Events include `UNC_ARB_COH_TRK_OCCUPANCY.All`, `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_TRK_OCCUPANCY.ALL`, `UNC_ARB_TRK_OCCUPANCY.CYCLES_WITH_ANY_REQUEST`, `UNC_ARB_TRK_REQUESTS.ALL`, and `UNC_ARB_TRK_REQUESTS.WRITES`.

## Control Flow

`jevents.py` generates uncore ARB aliases from this array, preserving package scope and converting selector/mask pairs into perf configs. At runtime, perf matches the generated aliases against ARB uncore PMU devices and aggregates package-level interconnect request tracking.

## State And Persistence Behavior

The file persists static metadata only. Queue occupancy, outstanding requests, and write allocation counts are runtime hardware state. Package-level persistence and aggregation are handled by perf's uncore PMU support.

## Dependencies And Integration Points

These events integrate with Haswell uncore discovery, generated PMU tables, `perf list`, `perf stat`, and Haswell system/memory metrics. `hsw-metrics.json` uses `UNC_ARB_TRK_REQUESTS.ALL` and `UNC_ARB_COH_TRK_REQUESTS.ALL` for DRAM bandwidth-use estimation.

## Risks And Edge Cases

Occupancy events and allocation-count events have different units; treating occupancy as requests can lead to incorrect bandwidth or pressure conclusions. `UNC_ARB_TRK_OCCUPANCY.ALL` and `.CYCLES_WITH_ANY_REQUEST` share event/mask fields but differ semantically through the counter configuration/description, so tests should verify generated aliases remain distinct. Multi-socket aggregation can make per-package traffic appear duplicated if users sum incorrectly.

## Test Signals

Run `jq empty`, x86 generation, and `perf test pmu-events`. On Haswell hardware or fixtures, verify `perf list` exposes ARB aliases and run memory/write-heavy workloads to check that request and write counts move in the expected direction. Metric validation should include `tma_info_system_dram_bw_use`.
