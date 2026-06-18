<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-io.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-io.json

## Purpose
This JSON file defines Knights Landing M2PCIe uncore I/O PMU events for perf. It is static event metadata for measuring traffic between the M2PCIe block and CMS, including ingress queue occupancy and egress queue inserts, fullness, and non-empty cycles. The complete 218-line array was read and contains 24 records, all with `Unit` `M2PCIe` and `PerPkg` `1`.

## Important APIs, Types, and Functions
The exported API is the perf alias set under event families `UNC_M2P_EGRESS_INSERTS` (8 records), `UNC_M2P_EGRESS_CYCLES_FULL` (6), `UNC_M2P_EGRESS_CYCLES_NE` (6), and `UNC_M2P_INGRESS_CYCLES_NE` (4). The schema fields are consistently `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, `UMask`, and `Unit`. Counters are mostly `0,1,2,3`, with `UNC_M2P_EGRESS_CYCLES_NE.*` limited to `0,1`.

There are no local functions or types beyond the JSON record shape. The suffixes model message classes and lanes: `AD_0`, `AD_1`, `AK_0`, `AK_1`, `BL_0`, `BL_1`, plus `AK_CRD_0` and `AK_CRD_1` for egress inserts, and ingress selectors such as `ALL`, `CBO_IDI`, `CBO_NCB`, and `CBO_NCS`.

## Control Flow
The perf build includes this file through the generic `SRC_JSON` discovery in `tools/perf/pmu-events/Build`. `jevents.py` maps `Unit` `M2PCIe` to PMU name `uncore_m2pcie`, emits `EventCode` as `event=`, emits non-zero `UMask` as `umask=`, and preserves `PerPkg`. Runtime selection comes from the Knights Landing x86 map row `GenuineIntel-6-(57|85),v16,knightslanding,core`, after which perf exposes the generated M2PCIe aliases for uncore counting.

## State and Persistence
The file has no mutable runtime state. Persistent behavior is the generated perf event table. All records are per-package uncore aliases, so actual counter availability and instance enumeration are provided by the kernel `uncore_m2pcie` PMU. The descriptions encode the intended state being sampled: egress full cycles, egress non-empty cycles, egress queue inserts, and ingress non-empty cycles.

## Dependencies and Integration Points
Dependencies are the perf PMU JSON schema, `jevents.py`, the x86 model map, and the kernel uncore driver for Knights Landing M2PCIe. It integrates with the larger Knights Landing uncore picture by complementing `uncore-cache.json` ring/CMS traffic and `uncore-memory.json` memory-controller counters. Workloads involving PCIe devices, DMA, or I/O-originated memory traffic can correlate these aliases with cache home-agent and memory events to locate backpressure between M2PCIe and CMS.

## Risks
The file is small but matrix-like, so the main risk is mismatched lane suffixes and `UMask` values. The `UNC_M2P_EGRESS_INSERTS` masks include both base traffic classes and credit classes, while the cycles-full and cycles-not-empty families omit credit selectors; users can accidentally compare non-equivalent sets. The `BriefDescription` text contains duplicated words and terse class names, so generated `perf list` help is not self-explanatory. Counter constraints differ between families, and scheduler behavior can fail if users combine too many events with the `0,1`-limited egress non-empty records.

## Test Signals
Validation should include `jq empty`, successful `jevents.py` generation, and generated event strings under `uncore_m2pcie` with `perpkg=1` and the expected `event=0x10`, `0x23`, `0x24`, and `0x25` codes. Hardware tests should compare `UNC_M2P_INGRESS_CYCLES_NE.ALL` against the CBO-specific selectors and exercise PCIe/DMA traffic to ensure egress insert and fullness counters move. Multiplexing tests should verify the limited-counter `UNC_M2P_EGRESS_CYCLES_NE.*` records are schedulable only within their declared counter constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-io.json -->
