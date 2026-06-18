# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-io.json

## Purpose

This file is a Sapphire Rapids PMU event topic table for Linux `perf`. It defines symbolic aliases for uncore I/O performance events so users and tools can request named events instead of raw event encodings. The events describe Intel IIO, M2PCIe, and IIO free-running counters used to observe PCIe/I/O request traffic, completion buffering, IOMMU behavior, P2P credit movement, and queue occupancy or pressure.

The JSON array contains 383 event records:

- 214 records use `Unit: "IIO"` for integrated I/O request, transaction, completion, IOMMU, arbitration, and clock events.
- 152 records use `Unit: "M2PCIe"` for M2PCIe clock, ingress/egress queue, peer-to-peer, credit, and CMS/IIO interaction events.
- 17 records use `Unit: "iio_free_running"` for fixed free-running IIO bandwidth and clocktick counters.

All records are per-package (`PerPkg: "1"`), so consumers should interpret counts at socket/package scope rather than as per-core events.

## Data Shape And Important Fields

Each array element is an event descriptor consumed by the perf PMU event generation pipeline. The file uses these fields:

- `EventName`: the public perf alias, such as `UNC_IIO_DATA_REQ_OF_CPU.MEM_READ.PART0` or `UNC_M2P_RxC_INSERTS.ALL`.
- `EventCode`: the raw PMU event selector. Examples include `0x83` for `UNC_IIO_DATA_REQ_OF_CPU`, `0xc0` for `UNC_IIO_DATA_REQ_BY_CPU`, and `0xff` for IIO free-running counters.
- `UMask`: the unit mask or subselector. Some base events omit it, such as clockticks, while most variants use it to distinguish transaction class, queue, credit, or part.
- `Counter`: the eligible hardware counter list. Many programmable events allow `0,1,2,3`, but some restrict to `0,1`, `2,3`, a single IOMMU counter, or a fixed free-running counter number.
- `Unit`: the target uncore PMU unit (`IIO`, `M2PCIe`, or `iio_free_running`).
- `BriefDescription` and `PublicDescription`: human-readable descriptions used by perf help/listing output.
- `PortMask`: an optional IIO port/part selector. It appears on 208 records and is central for partitioned PCIe/IIO accounting.
- `FCMask`: an optional flow-control mask. It appears on 185 records, mostly `0x07` for IIO completion/data/transaction classes and `0x00000000` for a small number of M2PCIe egress events.
- `Experimental`: marks 296 records as experimental. 87 records omit it.

There are no functions, classes, or executable control structures in this source. The effective API is the JSON schema and the event names/encodings it exports to generated perf tables.

## Event Families

The `IIO` unit entries cover:

- Clock and generic matching events: `UNC_IIO_CLOCKTICKS`, `UNC_IIO_MASK_MATCH_AND`, and `UNC_IIO_MASK_MATCH_OR`.
- Completion buffer accounting: `UNC_IIO_COMP_BUF_INSERTS` and `UNC_IIO_COMP_BUF_OCCUPANCY`, with all-parts and per-part variants.
- CPU-facing data and transaction requests: `UNC_IIO_DATA_REQ_OF_CPU`, `UNC_IIO_TXN_REQ_OF_CPU`, `UNC_IIO_DATA_REQ_BY_CPU`, and `UNC_IIO_TXN_REQ_BY_CPU`.
- Request counts and targets: `UNC_IIO_NUM_REQ_OF_CPU`, `UNC_IIO_NUM_REQ_OF_CPU_BY_TGT`, and `UNC_IIO_NUM_TGT_MATCHED_REQ_OF_CPU`.
- PCIe completion request classes: `UNC_IIO_REQ_FROM_PCIE_PASS_CMPL`, `UNC_IIO_REQ_FROM_PCIE_CL_CMPL`, and `UNC_IIO_REQ_FROM_PCIE_CMPL`.
- IOMMU events: `UNC_IIO_IOMMU0`, `UNC_IIO_IOMMU1`, and `UNC_IIO_IOMMU3`.
- Inbound arbitration and outbound request issue events: `UNC_IIO_INBOUND_ARB_REQ`, `UNC_IIO_INBOUND_ARB_WON`, `UNC_IIO_OUTBOUND_CL_REQS_ISSUED`, and `UNC_IIO_OUTBOUND_TLP_REQS_ISSUED`.

The `M2PCIe` unit entries cover:

- Clock and CMS clocktick events.
- Ingress queue cycles/inserts: `UNC_M2P_RxC_CYCLES_NE` and `UNC_M2P_RxC_INSERTS`.
- Egress ordering and fullness/not-empty signals: `UNC_M2P_EGRESS_ORDERING`, `UNC_M2P_TxC_CYCLES_FULL`, and `UNC_M2P_TxC_CYCLES_NE`.
- IIO credit usage: `UNC_M2P_IIO_CREDITS_USED`, `UNC_M2P_IIO_CREDITS_ACQUIRED`, and `UNC_M2P_IIO_CREDITS_REJECT`.
- Peer-to-peer shared/dedicated credit occupancy, received, returned, taken, and wait events split across local/remote and UPI/agent subchannels.
- Transmit credit classes `UNC_M2P_TxC_CREDITS.PMM` and `UNC_M2P_TxC_CREDITS.PRQ`.

The `iio_free_running` unit entries cover:

- `UNC_IIO_CLOCKTICKS_FREERUN` on counter 0.
- `UNC_IIO_BANDWIDTH_IN.PART0_FREERUN` through `PART7_FREERUN` on counters 1 through 8.
- `UNC_IIO_BANDWIDTH_OUT.PART0_FREERUN` through `PART7_FREERUN` on counters 9 through 16.

The bandwidth free-running descriptions state that each increment represents 32 bytes. Any rate calculation must divide by elapsed time and multiply counts by 32 bytes, while accounting for counter width and sampling interval.

## Control Flow And Generation Path

At build time, perf's `jevents` tool traverses `tools/perf/pmu-events/arch/x86`, reads JSON files with `.json` extensions, and combines them with `arch/x86/mapfile.csv`. The Sapphire Rapids map entry is `GenuineIntel-6-8F,v1.36,sapphirerapids,core`, which causes the directory containing this file to be compiled into generated PMU event tables.

The generated `pmu-events.c` encodes each descriptor into `struct pmu_event` data and builds a CPU mapping table. At runtime, perf matches the host CPU, selects the Sapphire Rapids table, and exposes aliases from `EventName` as user-facing event names. This file therefore participates in a data-driven flow:

1. JSON descriptors are parsed by `jevents`.
2. Event records are converted into generated C tables linked into perf.
3. Runtime CPU matching selects the Sapphire Rapids event table.
4. Perf builds PMU aliases for matching uncore PMU units.
5. Users request aliases with commands such as `perf stat -e <EventName> ...`.

## State And Persistence Behavior

This file is static source data. It does not persist runtime state, open files, mutate configuration, or record measurements. Persistence happens indirectly when its contents are compiled into perf's generated event tables and the resulting binary/libperf artifact is installed. Runtime counter state lives in kernel PMU drivers and hardware counters, not in this JSON file.

The event records encode persistent semantic contracts: alias names, raw encodings, counter eligibility, masks, and descriptions. Changing any of these fields can alter perf alias behavior for Sapphire Rapids systems.

## Dependencies And Integration Points

Primary dependencies and integration points are:

- The perf PMU event JSON schema understood by `tools/perf/pmu-events/jevents`.
- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/mapfile.csv`, which maps Sapphire Rapids CPUID `GenuineIntel-6-8F` to this directory.
- Sapphire Rapids uncore PMU kernel support exposing compatible `IIO`, `M2PCIe`, and free-running IIO units.
- Perf alias listing, parsing, and event scheduling code, which relies on valid `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `PortMask`, `FCMask`, and description fields.
- Neighboring Sapphire Rapids topic files such as `uncore-cache.json`, `uncore-cxl.json`, `uncore-interconnect.json`, `uncore-memory.json`, and `spr-metrics.json`, which together form the platform's full event catalog.

Because every event is `PerPkg: "1"`, integration with perf's aggregation/reporting should preserve socket/package scope. Tools that compare these aliases with core events need to avoid treating them as per-thread or per-core counts.

## Risks And Edge Cases

- Many entries are marked experimental. Consumers should expect possible semantic churn, incomplete validation, or hardware-stepping-specific behavior.
- Counter restrictions matter. For example, data request events often split between counters `0,1` and `2,3`, completion occupancy uses `2,3`, and free-running events bind to fixed counter numbers. Ignoring `Counter` can make event scheduling fail or silently choose an invalid counter.
- `PortMask` casing and width are not normalized across all records (`0x00FF`, `0x00ff`, `0xff`, and zero-padded forms all appear). Parsers should treat these as numeric masks, not string identity keys.
- `EventCode` values are reused across units. For example, `0xc0` appears for both IIO and M2PCIe families. The `Unit` field is required to disambiguate.
- Several event families expose all-parts and per-part variants. Double-counting can happen if a user sums `ALL_PARTS` with individual part aliases.
- Free-running bandwidth counters increment by 32-byte units and use fixed counter slots. A raw count is not directly bytes/second without scaling and elapsed-time normalization.
- Some descriptions are terse or repeat across variants; downstream documentation should not infer more topology detail than encoded by masks and event names.
- All events are package-scoped uncore events, so multi-socket machines require careful aggregation by package and PMU instance.

## Test Signals

Useful validation signals for this file include:

- JSON validity: `jq` should parse the file as one array with 383 objects.
- Schema consistency: every object should include `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, and `Unit`; optional masks and public descriptions should remain valid strings when present.
- Unit distribution should remain intentional: 214 `IIO`, 152 `M2PCIe`, and 17 `iio_free_running` records for the current file.
- All `PerPkg` values should be `1`.
- Event aliases should be unique across the file, especially where only suffixes such as `.PART0` or `.ALL_PARTS` differ.
- `jevents` generation should succeed for the Sapphire Rapids directory and produce event table entries without alias build failures.
- On Sapphire Rapids hardware or test fixtures with matching PMU support, `perf list` should expose representative aliases from all three units, and `perf stat` should accept events such as `UNC_IIO_CLOCKTICKS`, `UNC_IIO_COMP_BUF_INSERTS.CMPD.ALL_PARTS`, `UNC_M2P_RxC_INSERTS.ALL`, and `UNC_IIO_BANDWIDTH_IN.PART0_FREERUN`.
- Event scheduling tests should cover restricted counters and fixed free-running counters, because those are the highest-risk fields for runtime rejection.
