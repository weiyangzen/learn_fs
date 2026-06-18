<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-io.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-io.json

## Purpose
This JSON file defines Grand Ridge integrated I/O (`IIO`) uncore PMU events for perf. The complete 1,380-line file was read, containing 121 event records. It gives perf symbolic names for PCIe completion buffering, CPU-to-I/O and I/O-to-CPU data and transaction requests, IOMMU activity, target routing, and posted write tracker occupancy.

## Important APIs, Types, and Functions
The schema fields include `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `PerPkg`, `BriefDescription`, `PortMask`, and frequent `FCMask`. All records use `Unit` `IIO`; 108 records include `FCMask`, and many records include `PortMask` values for `ALL_PARTS` or individual partitions. Event families are `UNC_IIO_DATA_REQ_OF_CPU` (24), `UNC_IIO_TXN_REQ_OF_CPU` (24), `UNC_IIO_DATA_REQ_BY_CPU` (18), `UNC_IIO_TXN_REQ_BY_CPU` (16), completion-buffer inserts and occupancy (9 each), `UNC_IIO_NUM_REQ_OF_CPU_BY_TGT` (8), `UNC_IIO_IOMMU0` (7), `UNC_IIO_IOMMU1` (4), plus `UNC_IIO_CLOCKTICKS` and `UNC_IIO_PWT_OCCUPANCY`. Port masks range across partition selectors such as `0x001` through `0x080` and aggregate `0x0FF`.

## Control Flow, State, and Persistence
This is build-time input. `jevents.py` translates `EventCode` into `event=`, `UMask` into `umask=`, `PortMask` into `ch_mask=`, and `FCMask` into `fc_mask=`. Zero-valued masks are omitted by canonicalization, while non-zero masks constrain the generated perf alias. At runtime, perf only sees generated aliases bound to the Grand Ridge `uncore_iio` PMU. There is no mutable state in the file; persistent behavior is the resulting generated C table compiled into perf.

## Dependencies and Integration Points
The file depends on the IIO uncore PMU implementation in the kernel and on perf's JSON generator knowing `FCMask` and `PortMask`. It integrates with PCIe/IOMMU performance analysis, device traffic attribution by partition, and memory request tracing between CPU and I/O agents. It relates to `virtual-memory.json` through IOMMU page-walk signals and to cache/interconnect topics through peer writes and CPU memory read/write transactions.

## Risks and Test Signals
Sixty-one records are marked `Experimental`, and only one record has `PublicDescription`, so the table is rich but user-facing semantics are sparse. The highest risk area is the repeated partition expansion pattern: a wrong `PortMask` or missing `ALL_PARTS` counterpart can make per-part totals impossible to reconcile. `FCMask` is present on most traffic records and is emitted as `fc_mask=`, so generator regressions in field handling would affect almost the whole file. Test signals include syntax validation, generated event strings containing expected `fc_mask` and `ch_mask` terms, `perf list` visibility under `uncore_iio`, and hardware tests that compare `ALL_PARTS` events against the sum of `PART0` through `PART7` for PCIe completion and CPU request traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-io.json -->
