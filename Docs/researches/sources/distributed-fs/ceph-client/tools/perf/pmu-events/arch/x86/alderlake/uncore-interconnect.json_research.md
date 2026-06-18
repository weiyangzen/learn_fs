# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/uncore-interconnect.json

## Purpose

This 11-entry file describes Alder Lake uncore arbitration/interconnect events for perf. All entries use unit `ARB` and `PerPkg: 1`, meaning they represent package-level uncore activity rather than per-logical-CPU core PMU events. The catalog measures coherency tracker requests, data occupancy and requests, IFA occupancy, request tracker occupancy, demand-read tracker requests, and aggregate tracker occupancy/requests.

## Important APIs, Types, and Data

The schema uses `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`, with optional `Deprecated` and `Experimental`. Event families include `UNC_ARB_COH_TRK_REQUESTS`, `UNC_ARB_DAT_OCCUPANCY`, `UNC_ARB_DAT_REQUESTS`, `UNC_ARB_IFA_OCCUPANCY`, `UNC_ARB_REQ_TRK_OCCUPANCY`, `UNC_ARB_REQ_TRK_REQUEST`, `UNC_ARB_TRK_OCCUPANCY`, and `UNC_ARB_TRK_REQUESTS`. Two entries are deprecated. The `Counter` field is limited to uncore counters `0,1`.

## Control Flow

The file is declarative. Perf parses it into uncore PMU aliases. At runtime, requests for these aliases bind to package-level `ARB` PMU instances rather than `cpu_core` or `cpu_atom`. Because the events are per-package, perf aggregation and display flow differs from per-thread or per-core events; results should be interpreted at socket/package scope.

## State and Persistence Behavior

The JSON persists uncore event names and encodings. Runtime state is held in uncore PMU counters, usually shared by all CPUs in the package. `PerPkg` is important persistent metadata because it tells tooling and users that counts should not be multiplied by active CPUs or interpreted as per-thread measurements. Deprecated markers preserve compatibility while discouraging new use.

## Dependencies and Integration Points

This file integrates with perf's uncore PMU event handling, `perf list` uncore aliases, package-level bandwidth/coherency analysis, and any metrics that use arbitration occupancy or request counts. It depends on kernel exposure of the Alder Lake ARB uncore PMU and proper package aggregation. It is adjacent to `uncore-memory.json`, which supplies memory-controller activity; together they describe off-core traffic pressure.

## Risks

Uncore PMU names and availability can vary by platform, BIOS, and kernel. Per-package events can be misread when measured alongside per-core events, especially under CPU filtering. Deprecated entries should not appear in new metric formulas without explicit compatibility reasons. Limited counters can cause scheduling conflicts if many uncore events are requested together. Occupancy events may require normalization by cycles or requests before they are actionable.

## Test Signals

Validation should include JSON parsing, uncore alias generation, `perf list` visibility under the ARB PMU, and smoke `perf stat` runs that generate memory/coherency traffic. Tests should check package aggregation behavior, counter scheduling with only counters 0 and 1, and deprecation handling for the two deprecated ARB records.
