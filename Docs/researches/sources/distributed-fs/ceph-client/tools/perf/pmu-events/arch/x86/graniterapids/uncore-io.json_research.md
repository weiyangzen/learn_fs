# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-io.json

## Purpose
This JSON file defines 168 Intel Granite Rapids integrated I/O uncore PMU events for perf. The events cover IIO completion-buffer activity, CPU-to-I/O and I/O-to-CPU data and transaction requests, IOMMU lookup/cache behavior, outstanding request occupancy, request target breakdowns, and posted write table occupancy. The source was read as a complete 1,925-line JSON array.

## Important APIs, Types, and Functions
The file uses perf's x86 PMU event schema. All 168 rows have `EventName`, `EventCode`, `BriefDescription`, `Counter`, `PerPkg`, `PortMask`, and `Unit`; most rows also have `UMask`, and selected rows have `FCMask`, `Experimental`, or `Deprecated`. `Unit` is always `IIO`, so the differentiation comes from event code, unit mask, port mask, filter mask, and event name. There are 168 unique event names and 14 unique event codes.

Important event families include `UNC_IIO_COMP_BUF_INSERTS/OCCUPANCY.CMPD.*`, `UNC_IIO_DATA_REQ_BY_CPU.*`, `UNC_IIO_DATA_REQ_OF_CPU.*`, `UNC_IIO_TXN_REQ_BY_CPU.*`, `UNC_IIO_TXN_REQ_OF_CPU.*`, `UNC_IIO_IOMMU0/1/3.*`, `UNC_IIO_NUM_OUTSTANDING_REQ_*`, `UNC_IIO_NUM_REQ_OF_CPU_BY_TGT.*`, and `UNC_IIO_PWT_OCCUPANCY`. Part-specific names such as `PART0` through `PART7` use `PortMask` to select IIO partitions, while `ALL_PARTS` names aggregate with wider masks. The file marks `UNC_IIO_NUM_OUSTANDING_REQ_FROM_CPU.TO_IO` deprecated, preserving the misspelled alias next to the corrected `UNC_IIO_NUM_OUTSTANDING_REQ_FROM_CPU.TO_IO`.

## Control Flow, State, and Persistence
There is no executable control flow. `jevents.py` parses the array during perf build generation, serializes it into generated event tables, and runtime perf lookup maps event aliases to raw IIO PMU selectors. The row order is useful for maintainers, but runtime lookup is by generated event name and PMU metadata.

Static state is encoded in the JSON fields. `PerPkg: "1"` makes these package-level uncore events, while `PortMask` and `FCMask` are hardware filter controls that change what traffic is counted. Occupancy events and outstanding-request events count cycles or queue depth proxies, not necessarily completed transactions, so state interpretation depends on event family. Persistence is limited to generated perf tables; measurements themselves are session-local.

## Dependencies and Integration Points
The file depends on the perf PMU JSON schema, Granite Rapids IIO PMU support in the kernel, and Intel's IIO event definitions. It integrates with `perf list` and `perf stat -e` for uncore IIO PMUs, and it complements memory/interconnect event files for system-level traffic diagnosis. IOMMU events are integration points for virtualization, DMA, and device assignment analysis because they expose IOTLB, context-cache, PASID-cache, and second-level paging cache behavior from the IIO block.

The deprecated misspelled outstanding-request event is a compatibility integration point. Removing it could break existing scripts, while keeping it requires downstream tooling to handle aliases carefully.

## Risks and Test Signals
Risks include incorrect `PortMask` or `FCMask` filters, confusion between per-part and all-part aliases, the deprecated misspelled event being selected accidentally, and broad experimental coverage across completion-buffer, IOMMU, and request events. Because all rows share `Unit: "IIO"`, a unit naming mismatch would invalidate the whole table at runtime. Another risk is semantic overloading: similarly named `DATA_REQ` and `TXN_REQ` families may not count the same hardware boundary.

Test signals include `jq` validation, `jevents.py` generation, `perf list` checks for both deprecated and corrected outstanding-request names, and Granite Rapids hardware smoke tests for representative IIO transaction, IOMMU, and occupancy events. Tests should also verify that per-part `PortMask` events produce plausible differences across active IIO partitions and that `ALL_PARTS` events are schedulable with available IIO counters.
