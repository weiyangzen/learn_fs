# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json lines 6627-11744

## Scope

This chunk covers the middle of the Ice Lake Xeon uncore interconnect PMU event table used by `tools/perf/pmu-events`. The requested range starts inside the `UNC_M2M_TxR_HORZ_NACK.BL_UNCRD` object and ends inside the `UNC_M3UPI_RxC_OCCUPANCY_VN1.AD_RSP` object, so the first and last descriptors are partial at the chunk boundaries. Within the span, there are 472 `EventName` entries and 471 complete object starts visible in the raw line range. The complete source file parses as a JSON array with 1,689 event descriptors.

The chunk is data-only JSON. It declares hardware performance event metadata; it does not define executable functions, C types, mutable runtime state, or local control flow.

## Purpose

The file supplies Intel Ice Lake Xeon uncore interconnect event descriptions for Linux perf's PMU event database. `jevents.py` and related `pmu-events` build code consume this JSON and generate static event tables, which perf later uses to resolve symbolic event names, event codes, unit masks, descriptions, package scope, and counter eligibility.

This chunk is focused on interconnect traffic between common mesh stop, M2M, iMC, and UPI-facing units. It describes:

- `M2M` egress, vertical/horizontal ring, write-pending-queue, and write-tracker events.
- `M3UPI` mesh-to-UPI credit, ring, ingress arbitration, flit-generation, and receive-side queue events.

## Data Schema And API Surface

Each descriptor follows the perf PMU event JSON schema used throughout `tools/perf/pmu-events`:

- `EventName` is the stable symbolic user-facing name, for example `UNC_M2M_TxR_HORZ_OCCUPANCY.AD_ALL` or `UNC_M3UPI_RxC_INSERTS_VN0.BL_WB`.
- `EventCode` is the raw hardware event selector value.
- `UMask` selects a sub-event or traffic class within the event code.
- `Counter` lists allowed hardware counter indexes, usually `0,1,2,3` in this chunk.
- `Unit` binds the event to the uncore PMU block, mainly `M2M` or `M3UPI`.
- `PerPkg` marks package-scoped uncore measurement.
- `BriefDescription` and `PublicDescription` provide display text for `perf list` and event documentation.
- `Experimental: "1"` appears on most descriptors, signaling events that perf should expose but treat as experimental metadata.

The important compatibility contract is the string identity and field spelling. Perf's generator expects valid JSON objects with these known keys, and users/scripts depend on `EventName` strings remaining stable.

## Event Families Covered

### M2M Common Mesh Stop And Ring Events

The first 151 unit entries in the range are `M2M`. They cover Common Mesh Stop transgress/egress behavior:

- Horizontal egress NACK, occupancy, and starvation events for AD, AK, AKC, BL, and IV traffic classes.
- Vertical egress anti-deadlock slot use, bypass, fullness, not-empty cycles, inserts, NACKs, occupancy, and starvation. These are split across `*0` and `*1` event groups where the first group covers AD/AK/BL/IV agent variants and the second covers AKC/TGC-style variants.
- Vertical ring in-use counters for AD, AK, AKC, BL, IV, and TGC rings, with up/down and even/odd direction variants.

The M2M portion also tracks memory-side queues:

- `UNC_M2M_WPQ_FLUSH.*` and `UNC_M2M_WPQ_NO_*_CRD.*` describe write pending queue flushes and cycles lacking regular, PMM, or special credits for channels 0-2.
- `UNC_M2M_WR_TRACKER_*` describes write tracker fullness, inserts, not-empty cycles, occupancy, and posted/non-posted variants for memory channels and mirror paths.

These events are useful for diagnosing mesh pressure, ring utilization, anti-deadlock behavior, write queue backpressure, and memory-channel write tracking.

### M3UPI Credits, Rings, And Distress Signals

The remaining visible entries are `M3UPI`. The first large group measures Common Mesh Stop agent credits for AD and BL traffic:

- `UNC_M3UPI_AG0_*` and `UNC_M3UPI_AG1_*` split acquired and occupancy counters by agent, traffic class, and transgress target.
- The target indexes are represented as `TGR0` through `TGR10`, split across `*0` and `*1` groups because the hardware encodes them under adjacent event codes.

The chunk then describes M3UPI high-level state:

- `UNC_M3UPI_CHA_AD_CREDITS_EMPTY` for CBox request/snoop/VNA/writeback credit exhaustion.
- `UNC_M3UPI_CLOCKTICKS` and `UNC_M3UPI_CMS_CLOCKTICKS`.
- `UNC_M3UPI_D2C_SENT` and `UNC_M3UPI_D2U_SENT`.
- `UNC_M3UPI_DISTRESS_ASSERTED` for local/remote DPT and PMM, horizontal, vertical, IV-stalled, and no-credit distress conditions.
- Horizontal and vertical ring in-use, bounce, sink-starvation, and source-throttle events.
- `UNC_M3UPI_M2_BL_CREDITS_EMPTY` and `UNC_M3UPI_MISC_EXTERNAL` for M2 BL credit starvation and external MS2IDI-related signals.

These entries are integration points for users investigating socket fabric, UPI congestion, ring routing, and credit starvation.

### M3UPI Receive-Side Arbitration And Flit Generation

The final part of the chunk focuses on `RxC`, the receive/control path from CMS into UPI-facing queues:

- `UNC_M3UPI_RxC_ARB_LOST_VN0/VN1`, `ARB_NOCRD`, and `ARB_NOREQ` break arbitration failure reasons down by virtual network, AD request/response/snoop traffic, and BL NCB/NCS/RSP/WB traffic.
- `UNC_M3UPI_RxC_ARB_MISC` records parallel arbitration wins and no-progress cases for AD/BL and VN0/VN1.
- `UNC_M3UPI_RxC_BYPASSED`, `CRD_MISC`, and `CRD_OCC` describe bypass paths, background FIFO/path credits, D2K credits, transmit queue credits, flits in FIFO/path, and VNA usage.
- `UNC_M3UPI_RxC_CYCLES_NE_VN0/VN1`, `INSERTS_VN0/VN1`, and `OCCUPANCY_VN0` plus the start of `OCCUPANCY_VN1` provide the three related signals needed to reason about queue activity and latency: cycles not empty, allocations, and occupancy accumulation.
- Data/header flit families (`DATA_FLITS_NOT_SENT`, `FLITS_GEN_BL`, `FLITS_SLOT_BL`, `FLIT_GEN_HDR1`, `FLIT_GEN_HDR2`, `HDR_FLITS_SENT`, `HDR_FLIT_NOT_SENT`) expose why flits were or were not sent, pump wait states, slot occupancy, run-ahead behavior, rate-matching stalls, and message packing efficiency.
- `UNC_M3UPI_RxC_HELD` records messages held because AD/BL traffic could not be slotted or because VN0/VN1 state prevents immediate flit assembly.

The chunk ends before the full `UNC_M3UPI_RxC_OCCUPANCY_VN1` family completes; subsequent lines continue that family.

## Control Flow And State

There is no runtime control flow in this chunk. Its effective flow is build-time:

1. The JSON file is read by perf's PMU event generation scripts.
2. Event objects are transformed into generated C event tables.
3. Perf runtime code exposes the generated events through `perf list`, event parsing, metric resolution, and PMU selection.

There is no persistence behavior beyond the checked-in JSON data and generated build artifacts. Runtime counter values are provided by CPU uncore PMU hardware, not stored by this file.

## Dependencies And Integration Points

This chunk depends on:

- The `tools/perf/pmu-events` JSON schema and `jevents.py` generator behavior.
- The x86 Ice Lake Xeon model mapping that selects this architecture directory.
- Kernel/perf uncore PMU names matching `Unit` values such as `M2M` and `M3UPI`.
- Intel uncore event encoding correctness for `EventCode`, `UMask`, and counter constraints.

Integration points include:

- `tools/perf/util/pmu.c` and related PMU parsing code, which use generated event tables.
- `tools/perf/tests/pmu-events.c` and parser tests that validate generated event metadata.
- User workflows such as `perf list`, `perf stat -e <event>`, and scripts that reference symbolic `EventName` strings.

## Risks And Edge Cases

- The assigned chunk boundaries split JSON objects. Any merge or reconciliation step must use the complete source file or neighboring chunks to avoid treating the line range alone as standalone JSON.
- Many event families are repetitive and hardware-encoded by masks. Copy/paste errors in `UMask`, `EventCode`, or suffixes such as `AG0/AG1`, `TGR8/TGR9/TGR10`, `VN0/VN1`, and `CH0/CH1/CH2` would silently map a symbolic event to the wrong counter.
- Several descriptions appear mechanically duplicated or inconsistent. For example, some "Cycles CMS Vertical Egress Queue Is Full" descriptions mention "Not Full", and some `VN0` occupancy descriptions mention `VN1`. These may be inherited vendor text, but they are user-visible through perf.
- `Experimental: "1"` on most entries limits the confidence users should place in exact semantics and may affect downstream filtering or documentation expectations.
- Case varies in event codes, including lowercase `0xae` near otherwise uppercase codes. JSON parsing accepts it as a string, but style-sensitive validation or generated diffs could flag it.
- The range contains event-code reuse across different units and subfamilies. This is expected for PMU event tables, but consumers must always combine `Unit`, `EventCode`, and `UMask`.

## Test Signals

Useful validation signals for this chunk are:

- `jq length sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json` succeeds and returns the full descriptor count.
- `jq -r '.[].EventName' ...` succeeds without null or duplicate surprises for the full file.
- Perf's PMU event generation step rebuilds generated `pmu-events.c` without schema errors.
- `tools/perf` PMU event tests, especially tests including `pmu-events/pmu-events.h`, pass after generation.
- Manual `perf list` on an Ice Lake Xeon-capable build shows the expected `UNC_M2M_*` and `UNC_M3UPI_*` event names and descriptions.
