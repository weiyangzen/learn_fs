# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-io.json

## Purpose

This 394-entry file defines Cascade Lake X uncore I/O PMU aliases for Linux perf. Every record targets unit `IIO` with `PerPkg: 1`, so the events describe package-level Integrated I/O traffic rather than per-core execution. The table covers PCIe/MMIO traffic, CPU-to-device and device-to-CPU requests, inbound/outbound transactions, payload-byte accounting, completion-buffer inserts and occupancy, VT-d translation behavior, link retry/error counts, mask-match helpers, and two higher-level `LLC_MISSES.PCIE_*` metric aliases for PCIe read/write bandwidth.

## Important APIs, Types, and Data

The file is declarative JSON consumed by perf's PMU event tooling. Common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and optional `PublicDescription`. Many IIO events also use `FCMask` and `PortMask`; the two PCIe bandwidth metric aliases add `MetricExpr`, `MetricName`, `Filter`, and `ScaleUnit`.

The main event families are `UNC_IIO_DATA_REQ_BY_CPU`, `UNC_IIO_DATA_REQ_OF_CPU`, `UNC_IIO_TXN_REQ_BY_CPU`, `UNC_IIO_TXN_REQ_OF_CPU`, `UNC_IIO_TXN_IN`, `UNC_IIO_TXN_OUT`, `UNC_IIO_PAYLOAD_BYTES_IN`, `UNC_IIO_PAYLOAD_BYTES_OUT`, `UNC_IIO_COMP_BUF_INSERTS`, `UNC_IIO_COMP_BUF_OCCUPANCY`, `UNC_IIO_VTD_ACCESS`, and `UNC_IIO_VTD_OCCUPANCY`. Single or small families cover `UNC_IIO_CLOCKTICKS`, `UNC_IIO_SYMBOL_TIMES`, `UNC_IIO_LINK_NUM_RETRIES`, `UNC_IIO_LINK_NUM_CORR_ERR`, `UNC_IIO_MASK_MATCH*`, and `UNC_IIO_NOTHING`.

The encodings cluster around a few event codes: `0x83` for inbound data requests/payload bytes, `0x84` for inbound transactions/transaction requests, `0xC0` for outbound data requests/payload bytes, `0xC1` for outbound transactions/transaction requests, `0xC2` for completion-buffer inserts, `0xD5` for completion-buffer occupancy, `0x40`/`0x41` for VT-d occupancy/accesses, and `0x0E`/`0x0F` for link retries/correctable errors. `Counter` availability is split across `0,1`, `2,3`, and `0,1,2,3`, which affects event scheduling.

Traffic qualifiers are encoded in event-name suffixes and masks. Request types include `CFG_READ`, `CFG_WRITE`, `IO_READ`, `IO_WRITE`, `MEM_READ`, `MEM_WRITE`, `PEER_READ`, `PEER_WRITE`, `ATOMIC`, `ATOMICCMP`, and `MSG`. Target selectors include `PART0` through `PART3` plus `VTD0` and `VTD1`; `PortMask` maps those selectors to IIO parts or VT-d paths.

## Control Flow

There is no executable control flow in this file. Build-time/perf tooling parses the JSON array, validates the schema, and generates PMU alias metadata. At runtime, `perf list` exposes the aliases and `perf stat` or metric evaluation resolves selected aliases into uncore IIO PMU encodings.

When a user selects a low-level alias, perf programs the event code, umask, counter constraints, and any filter/mask fields on an IIO PMU instance for each package. When a user selects `LLC_MISSES.PCIE_READ` or `LLC_MISSES.PCIE_WRITE`, perf evaluates the `MetricExpr` by summing the corresponding `UNC_IIO_DATA_REQ_OF_CPU.*.PART0..PART3` aliases and applies the declared four-byte scale. Occupancy events such as completion-buffer and VT-d occupancy require interpretation over the measurement interval, usually normalized against clockticks or requests.

## State and Persistence Behavior

The persistent state is the checked-in event catalog: names, descriptions, hardware encodings, metric expressions, package scope, experimental/deprecated markers, and counter constraints. Runtime state resides in hardware uncore counters and perf's event scheduler. Because all records are `PerPkg`, counts are shared at package/socket scope and should not be treated as per-thread, per-CPU, or per-process values.

The file contains 309 `Experimental` records and 175 `Deprecated` records. The deprecated records are concentrated in `UNC_IIO_PAYLOAD_BYTES_IN`, `UNC_IIO_PAYLOAD_BYTES_OUT`, `UNC_IIO_TXN_IN`, and `UNC_IIO_TXN_OUT`, which keeps old aliases visible while signaling that newer request-count aliases are preferred. The two metric aliases are persistent derived metrics rather than hardware events and depend on the availability and semantics of their component aliases.

## Dependencies and Integration Points

This table integrates with perf's PMU event JSON loader, generated event tables, `perf list`, `perf stat`, metric expression evaluation, and Linux kernel uncore PMU support for Cascade Lake X IIO units. It also depends on platform topology: PCIe slots, risers, lane grouping, VT-d paths, BIOS configuration, and kernel-exposed PMU instance names determine which parts and filters produce meaningful counts.

The file is adjacent to other Cascade Lake X uncore catalogs and complements memory-controller, cache, and interconnect events. In distributed-storage or Ceph-client profiling, these aliases are useful for separating PCIe/NVMe/NIC traffic from core-side CPU work and memory-controller pressure.

## Risks

The largest risk is misinterpreting package-level IIO counts as process-local behavior, especially when profiling a single workload on a busy host. `PART0` through `PART3` depend on physical slot/lane topology, so formulas can be wrong if the device is behind a riser, bridge, or unexpected lane group. Counter constraints are tight for some families, so broad event groups can multiplex or fail to schedule.

Experimental aliases may not be stable across kernel, firmware, or silicon revisions. Deprecated payload/transaction aliases should not be used for new metrics without an explicit compatibility reason. VT-d events are only meaningful when IOMMU paths are active and correctly mapped. The `LLC_MISSES.PCIE_*` names can be confusing because the underlying expressions count IIO read/write requests in four-byte units rather than conventional core LLC miss events.

## Test Signals

Validation should start with JSON parsing and generated perf table checks. `perf list` on Cascade Lake X hardware should show the IIO aliases with package scope, experimental/deprecated annotations, and the two PCIe bandwidth metrics. Smoke tests should run `perf stat` against known PCIe traffic, such as NVMe reads/writes or NIC DMA, and confirm that relevant `PART*` counters move while unrelated parts remain low.

Scheduling tests should request representative events from each counter set (`0,1`, `2,3`, and `0,1,2,3`) to catch constraint regressions. Metric tests should verify that `LLC_MISSES.PCIE_READ` and `LLC_MISSES.PCIE_WRITE` expand to the four `UNC_IIO_DATA_REQ_OF_CPU` part aliases and preserve the `4Bytes` scale. Platform tests should compare counts under VT-d enabled/disabled configurations and under different PCIe slot placements to confirm that `PortMask` assumptions match observed topology.
