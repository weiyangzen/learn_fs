<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-interconnect.json

## Purpose

`uncore-interconnect.json` defines 11 Tiger Lake package-level ARB uncore PMU events for coherent interconnect/request-tracker behavior. It exposes request allocation counts and occupancy for coherent and non-coherent traffic, with aliases for data-read tracker requests and occupancies. The catalog helps perf users inspect traffic leaving cores toward the fabric and memory subsystem.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects using `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, plus optional `Experimental` and `Deprecated`. All rows use `Unit: ARB` and `PerPkg: 1`. Counter availability is split between event-counting requests on counters `0,1` and occupancy-style events on counter `0`.

Important events are `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_TRK_REQUESTS.ALL`, `UNC_ARB_TRK_REQUESTS.RD`, `UNC_ARB_TRK_OCCUPANCY.ALL`, `UNC_ARB_TRK_OCCUPANCY.RD`, `UNC_ARB_REQ_TRK_REQUEST.DRD`, `UNC_ARB_REQ_TRK_OCCUPANCY.DRD`, `UNC_ARB_DAT_OCCUPANCY.ALL`, and `UNC_ARB_DAT_OCCUPANCY.RD`. Two rows are deprecated aliases: `UNC_ARB_DAT_REQUESTS.RD` points users toward `UNC_ARB_REQ_TRK_REQUEST.DRD`, and `UNC_ARB_IFA_OCCUPANCY.ALL` points toward `UNC_ARB_DAT_OCCUPANCY.ALL`.

## Control Flow and Data Flow

The file has no executable control flow. Perf's PMU event generator ingests the rows, emits uncore ARB aliases, and at runtime programs package-level uncore counters with the encoded `EventCode`/`UMask`/counter constraints. Request events count allocations; occupancy events count valid tracker entries over cycles. The event families form a small analysis flow from all outgoing tracker traffic to coherent data-read-only traffic.

## State and Persistence Behavior

Static event metadata is persistent in the repository and generated perf tables. Runtime counter values are package-scoped and interval-local. The occupancy rows represent integrated hardware state, not discrete transactions, so they need a cycle denominator or comparable workload interval to be interpreted as pressure. Deprecated rows remain persistent aliases for compatibility but should not be treated as preferred API names.

## Dependencies and Integration Points

This file depends on Tiger Lake ARB uncore PMU support in perf and the kernel. It integrates with `perf list`, `perf stat`, uncore fabric analysis, memory traffic diagnosis, and sibling uncore-memory counters that observe traffic after it reaches the memory controller. It also provides raw events that can be referenced by higher-level metrics or user scripts.

## Risks and Edge Cases

Package-level ARB counts aggregate all activity on the package, not just the profiled process. Several rows are marked `Experimental`, so availability or exact semantics may vary by kernel, firmware, or stepping. Deprecated aliases can confuse users if both old and new names appear. Occupancy and request-count rows use different units and should not be summed directly. Counter restrictions matter because all occupancy rows require counter `0`, creating scheduling conflicts with each other.

## Test Signals

Validation should include JSON parse success, perf table generation, and `perf list` exposure of ARB aliases with deprecation metadata preserved. Runtime tests can compare idle, single-thread memory, and multi-thread memory workloads: request counters should rise with fabric traffic, while occupancy counters should increase under pressure. Tests should verify that deprecated aliases still parse but documentation and preferred metric formulas use the non-deprecated names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-interconnect.json -->
