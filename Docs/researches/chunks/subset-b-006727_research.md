# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-interconnect.json lines 6273-11875

## Scope

This chunk is a middle slice of the Skylake X uncore interconnect PMU event JSON. It starts inside the `UNC_M3UPI_RING_BOUNCES_HORZ.AK` record and ends inside the `UNC_M3UPI_VN0_CREDITS_USED.WB` record, so both boundary events are partial records that must be reconciled with adjacent chunks during the final per-file merge. Within the requested line window there are 514 visible `EventName` fields, 513 complete `Unit: M3UPI` fields, and 513 complete `Experimental: 1` fields. The full source file parses as a valid JSON array with 1291 event objects.

## Purpose

The lines in this chunk define symbolic `perf` aliases for Skylake X `M3UPI` uncore interconnect counters. The events describe mesh-to-UPI traffic behavior: ring bounces and starvation, RxC receive-channel arbitration and credit pressure, RxR receive-ring queue behavior, TxC flow-queue/arbitration behavior, TxR horizontal and vertical egress behavior, UPI peer credit exhaustion, prefetch spawning, vertical ring utilization, and the beginning of VN0 credit-use/no-credit counters.

These entries let users and tooling request named events such as `unc_m3upi_rxc_arb_lost_vn0.ad_req` rather than hand-writing raw PMU config strings. The data is hardware-model metadata, not executable logic, but incorrect fields directly change generated `pmu-events.c` aliases and therefore user-visible `perf list`, `perf stat -e ...`, and Python perf-event metadata.

## Data Model And Important Fields

Each complete object in this chunk follows the perf PMU-events JSON schema consumed by `tools/perf/pmu-events/jevents.py`:

- `EventName` is the symbolic alias. `jevents.py` lowercases it for the generated PMU table.
- `EventCode` is the base hardware event selector. Repeated families use one `EventCode` with distinct `UMask` values.
- `UMask` selects message class, virtual network, agent, direction, or queue subcondition. Some aggregate events, such as `UNC_M3UPI_RING_SRC_THRTL` and `UNC_M3UPI_UPI_PREFETCH_SPAWN`, have no visible `UMask` in this chunk.
- `Counter: "0,1,2"` constrains these events to M3UPI counters 0 through 2.
- `Unit: "M3UPI"` maps through `unit_to_pmu()` into the uncore M3UPI PMU name used by generated aliases.
- `PerPkg: "1"` marks package-scoped counting.
- `Experimental: "1"` marks the events as experimental; metric tooling can detect references to experimental events.
- `BriefDescription` and optional `PublicDescription` are normalized by `fixdesc()` and propagated to perf list output and Python bindings.

The source uses suffixes as structured dimensions: channel suffixes such as `AD`, `AK`, `BL`, and `IV`; protocol/message suffixes such as `REQ`, `RSP`, `SNP`, `WB`, `NCB`, and `NCS`; virtual-network suffixes such as `VN0`, `VN1`, and `VNA`; direction suffixes such as `UP`, `DN`, `HORZ`, and `VERT`; and agent suffixes such as `AG0` and `AG1`.

## Event Families In This Chunk

The first visible families cover ring-level behavior: horizontal and vertical ring bounces, sink starvation, source throttling, and vertical ring in-use counters. These are cycle or activity counters for mesh/interconnect pressure by ring type or direction.

The `UNC_M3UPI_RxC_*` families dominate the first half of the chunk. They describe receive-channel arbitration outcomes (`ARB_LOST`, `ARB_NOAD_REQ`, `ARB_NOCRED`, `ARB_MISC`), bypasses, flit collisions, credit occupancy and miscellaneous credit states, queue non-empty cycles, flits generated/sent/not-sent, held messages, inserts, occupancy, packing misses, SMI3 prefetch classes, and VNA credit behavior. Most of these are repeated across VN0/VN1 and AD/BL message classes with predictable `UMask` assignments.

The `UNC_M3UPI_RxR_*` families cover receive-ring busy/starved states, bypass, credit starvation, insert counts, and occupancy. These events separate ring direction/agent/channel dimensions and provide diagnostics for ring-side pressure after traffic is received from UPI-facing paths.

The `UNC_M3UPI_STALL_NO_TxR_HORZ_CRD_*` families record stalls caused by missing horizontal TxR credits for AD or BL traffic and for agent 0/1 variants. They bridge receive-side pressure and transmit-ring credit availability.

The `UNC_M3UPI_TxC_*` families describe transmit-channel flow queue and arbitration behavior, including AD/BL arbitration failures, FLQ bypasses, non-empty cycles, inserts, occupancy, snoop-filter groups, and speculative arbitration credit/new-message/no-other-pending conditions. The `AK_FLQ_*` records are smaller one-event families.

The `UNC_M3UPI_TxR_HORZ_*` and `UNC_M3UPI_TxR_VERT_*` families cover horizontal and vertical egress queues: ADS used, bypass, cycles full, cycles non-empty, inserts, NACKs, occupancy, and injection starvation. The vertical variants generally include AD/AK/BL agent split plus IV entries; the horizontal variants are similar but have fewer IV-only cases.

The chunk ends with UPI peer AD/BL credit-empty counters, a UPI prefetch spawn counter, vertical AD/AK/BL/IV ring-in-use counters, and the beginning of `UNC_M3UPI_VN0_CREDITS_USED` plus the first partial `UNC_M3UPI_VN0_NO_CREDITS` record in adjacent lines.

## Control Flow And Generation Path

There is no runtime control flow in this JSON file. The relevant flow is build-time and lookup-time:

1. The perf build reads JSON files under `tools/perf/pmu-events/arch/...` according to the architecture mapfile.
2. `jevents.py` parses each object, converts `EventName` to lowercase, canonicalizes `EventCode` and `UMask`, converts `Unit` to a PMU name, and assembles an event string such as `event=0x4b,umask=0x1`.
3. `jevents.py` emits generated `pmu-events.c` tables.
4. The generated object is compiled into perf and exposed through PMU event lookup.
5. Runtime tools such as `perf list`, `perf stat`, and perf Python bindings display or select these aliases and descriptions.

Because the chunk is JSON data, control-flow risk is mostly transformation risk: malformed JSON, duplicate aliases, wrong selector fields, or description/schema fields that the generator silently normalizes into misleading user-visible aliases.

## State And Persistence Behavior

The persistent state is the checked-in event metadata. Generated `pmu-events.c` is a derived build artifact and should not be manually edited for these events. `PerPkg: "1"` means the resulting events aggregate at package scope, which matters when interpreting counts on multi-socket systems. Counter selection state is constrained by `Counter: "0,1,2"` and the M3UPI PMU availability exposed by the running kernel and hardware.

No mutable runtime state is stored in this source file. Counter values are produced by hardware during perf sessions; this JSON only persists the mapping from symbolic event names to hardware selectors and descriptions.

## Dependencies And Integration Points

This chunk depends on the PMU-events schema implemented by `tools/perf/pmu-events/jevents.py`, the x86 mapfile that maps Skylake X CPU IDs to the `skylakex` event directory, and perf's PMU alias machinery in `tools/perf/util/pmu.c` and `tools/perf/util/pmu.h`. It also feeds user-facing list output in `tools/perf/builtin-list.c` and Python metadata in `tools/perf/util/python.c`.

The semantic dependency is Intel Skylake X uncore M3UPI hardware: the event codes and masks are only meaningful when the kernel exposes matching uncore M3UPI PMUs. The repeated `Experimental: "1"` flags also integrate with PMU metric helpers that can mark formulas using experimental events.

## Risks And Edge Cases

The requested slice begins and ends mid-object. A final merged report must not treat the first and last visible records as independently complete without adjacent chunk context.

Several families reuse the same `EventCode` with different masks. A single wrong `UMask` can create a valid but semantically incorrect alias that build tests may not catch unless compared with Intel reference data or hardware behavior.

Some visible descriptions appear inconsistent with event suffixes near the boundary and credit families. For example, the visible tail maps `UNC_M3UPI_VN0_CREDITS_USED.WB` to a brief description saying `RSP on BL`, while earlier BL suffixes distinguish `WB` from `RSP`. Similar AD/BL credit-empty brief descriptions should be checked against the hardware specification before relying on the prose.

The chunk has many near-duplicate families, so copy/paste drift is a realistic risk: swapped `VN0`/`VN1`, `AG0`/`AG1`, `AD`/`BL`, `HORZ`/`VERT`, or direction masks would still parse and generate aliases.

All complete visible events are marked experimental. Downstream metric formulas or documentation should avoid presenting these counters as stable architectural events unless the experimental status is intentional.

## Test Signals

Useful validation starts with syntax: `jq empty sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-interconnect.json` succeeds for the full file. In this workspace, the full file contains 1291 JSON objects.

Build-time validation should include the perf PMU-events generation path, especially the `jevents.py` rule that emits `pmu-events.c`. The generated table should contain lowercase aliases for the M3UPI names in this chunk and event strings that combine the expected `event=...` and `umask=...` pairs.

Runtime smoke signals, on matching Skylake X hardware, are `perf list` showing M3UPI aliases from these families and `perf stat -e` accepting representative aliases from ring, RxC, RxR, TxC, TxR, and UPI peer credit families. Hardware-level semantic validation requires comparing counts against workloads that create UPI traffic, ring pressure, or credit starvation.

Chunk-local guard checks used for this research: the requested lines expose 514 `EventName` fields, 513 complete `Unit: "M3UPI"` fields, and 513 complete `Experimental: "1"` fields. The one-field difference is expected because the line range starts and ends inside event objects.
