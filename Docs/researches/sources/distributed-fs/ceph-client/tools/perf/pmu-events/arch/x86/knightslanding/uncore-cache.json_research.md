<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-cache.json

## Purpose
This JSON file defines Knights Landing uncore cache, home-agent, TOR, ring, credit, and ingress/egress queue PMU events for perf. It is declarative input to the perf PMU event generator, not executable code. The full 3,786-line array was read and contains 421 event records, all with `Unit` `CHA` and `PerPkg` `1`.

## Important APIs, Types, and Functions
The public API is the set of perf event aliases exported from each `EventName`. Records use the perf PMU JSON schema fields `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `PerPkg`, and `BriefDescription`; 420 records specify `EventCode`, 417 specify `UMask`, and the clock-like entries rely on the default generated `event=0` form plus unit metadata.

There are no functions or classes. The important event families include `UNC_H_TOR_OCCUPANCY` (12 records), `UNC_C_TOR_INSERTS` (7), `UNC_H_TOR_INSERTS` (6), many eight-way agent and ingress retry families such as `UNC_H_AG0_AD_CRD_ACQUIRED`, `UNC_H_AG1_BL_CRD_OCCUPANCY`, `UNC_H_INGRESS_RETRY_IPQ0_REJECT`, and `UNC_H_INGRESS_RETRY_REQ_Q0_RETRY`, plus horizontal and vertical egress/ring families. The file exposes a much larger Knights Landing CHA/home-agent taxonomy than the smaller KNL memory and I/O event files, covering TOR inserts/occupancy, cache line victimization, SF lookups, CMS agent credits, ring backpressure, nack/bypass/starvation signals, and ingress retry behavior.

## Control Flow
Control flow is external to this file. `tools/perf/pmu-events/Build` discovers JSON files under `pmu-events/arch` for the selected `JEVENTS_ARCH` and feeds them to `jevents.py`. `jevents.py` converts `Unit` `CHA` to Linux PMU name `uncore_cha`, converts `EventCode` to `event=`, `UMask` to `umask=`, and preserves non-zero event modifiers in generated event strings. The x86 map entry `GenuineIntel-6-(57|85),v16,knightslanding,core` selects this model's events at runtime. Perf then exposes aliases such as `unc_h_tor_occupancy.*` and `unc_h_ingress_retry_*` through `perf list` and resolves them for `perf stat -e` or related commands on Knights Landing hardware.

## State and Persistence
The source JSON has no mutable state. Its persistent effect is the generated `pmu-events.c` table compiled into perf. `PerPkg` is retained as per-package aggregation metadata, while the unit mapping controls which kernel PMU namespace receives the alias. Because all records are uncore per-package events, runtime interpretation also depends on the kernel uncore CHA PMU topology and the number of package instances visible on the host.

## Dependencies and Integration Points
This file depends on the perf PMU event JSON schema, `jevents.py`, `pmu-events.h`, the x86 CPU map in `arch/x86/mapfile.csv`, and the kernel uncore PMU driver exposing `uncore_cha`. It integrates with adjacent Knights Landing topics: `uncore-memory.json` for MCDRAM/iMC counters, `uncore-io.json` for M2PCIe ingress/egress activity, and `virtual-memory.json` for core page-walk signals. The event family naming also integrates with perf user workflows that compare broad TOR/cache/ring totals against narrower queue, direction, or agent-specific subsets.

## Risks
The highest risk is data correctness. Many families are repeated matrices over agents, transgress indices, queue IDs, horizontal/vertical directions, and AD/AK/BL/IV message classes; a copy/paste error in `UMask` or event suffix would silently expose a misleading counter. Heavy reuse of nearby event codes and masks makes review by visual inspection weak. The file has no `PublicDescription`, so perf users rely on terse `BriefDescription` strings that contain some duplicated spacing and vendor terminology. The four records without `UMask` and one record without `EventCode` are likely clock or aggregate-style entries, but generator behavior for missing fields should be checked whenever schema handling changes.

## Test Signals
Useful validation starts with `jq empty` over the file and a perf tools build that regenerates `pmu-events.c`. Generated aliases should contain `pmu=uncore_cha`, `perpkg=1`, expected `event=`/`umask=` terms, and no malformed default entries for missing masks. Hardware smoke tests should run broad TOR and ring events together with narrower subevents to check that aggregate directions, queue classes, and agent-specific counts move under cache-heavy, remote-memory, and ring-pressure workloads. Regression tests should especially diff generated event strings for repeated families such as `UNC_H_INGRESS_RETRY_*`, `UNC_H_AG*_CRD_*`, and `UNC_H_EGRESS_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-cache.json -->
