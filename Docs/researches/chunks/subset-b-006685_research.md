# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-io.json lines 1-5325

## Scope

This chunk covers the first 5,325 lines of the Ice Lake Xeon `uncore-io.json` perf PMU event table. The full file is a JSON array of event descriptor objects; this chunk contains the file opening, 430 complete event objects, and line 5,325, which is the opening brace of the next object. The last complete object in scope is `UNC_M2P_AG0_AD_CRD_OCCUPANCY0.TGR2` at lines 5314-5324; `UNC_M2P_AG0_AD_CRD_OCCUPANCY0.TGR3` starts immediately after the chunk boundary and must be handled by the next chunk.

## Purpose

The file supplies architecture-specific Intel Ice Lake Xeon uncore IO PMU metadata to Linux perf. It is not executable application logic; it is source data parsed by the perf PMU events build path, especially `tools/perf/pmu-events/jevents.py`, into generated `pmu-events.c` tables. At runtime, perf uses those generated tables to expose symbolic event names, descriptions, event selectors, masks, unit names, and package-scope behavior for `perf list`, `perf stat`, and related PMU lookup paths.

This chunk focuses on Integrated IO (`IIO`) and the beginning of M2PCIe (`M2PCIe`) events. It describes PCIe and IOMMU traffic moving between CPU, cards, and IO agents: free-running bandwidth and clock counters, completion-buffer occupancy/inserts, CPU-to-device and device-to-CPU request classes, IOMMU lookup/cache/invalidation counters, debug mask/match events, outbound queue/request issue counters, PCIe request completion pipeline states, transaction counters, and the first M2PCIe credit acquisition/occupancy counters.

## Data Shape And Important Fields

Each event object follows the perf PMU event JSON schema consumed by `jevents.py`:

- `EventName`: symbolic perf event name. Names in this chunk are mostly `UNC_IIO_*`, with `UNC_M2P_*` beginning at line 5175.
- `EventCode`: hardware event selector, such as `0xff` for free-running counters, `0xC1` for outbound transaction request classes, `0x84` for inbound transaction request classes, and `0x80`-series M2PCIe credit events.
- `UMask`: unit mask that selects a subcondition within an event selector. Most event families use repeated `UMask` values across `PART*`, `IOMMU*`, and request-type variants.
- `Counter`: valid programmable counter set. Common values are `0,1,2,3`; free-running events pin to individual counters, and some debug/occupancy events are limited to `0,1` or `2,3`.
- `Unit`: PMU unit name. This chunk contains 407 complete `IIO` entries, 9 `iio_free_running` entries, and 14 complete `M2PCIe` entries.
- `PerPkg`: present on every complete event in the chunk, marking package-level uncore counting semantics rather than per-core counting.
- `PortMask` and `FCMask`: IO-specific qualifiers translated by `jevents.py` into perf event terms such as `ch_mask=` and `fc_mask=`. They are present on the majority of IIO traffic events and encode lane/slot/flow-control filtering.
- `BriefDescription` and `PublicDescription`: human-readable descriptions for `perf list` and event documentation. Many descriptions encode topology assumptions such as `PART0`-`PART7` lane/slot mappings, `IOMMU0`/`IOMMU1` masks, outbound versus inbound direction, and cache-line versus transaction granularity.
- `Experimental`: present on 329 complete events in this chunk. These events should be considered less stable as a user-facing contract.

There are no `MetricName`, `MetricExpr`, or `ScaleUnit` fields in this chunk, so it defines raw events rather than derived perf metrics.

## Event Families In This Chunk

The chunk starts with nine free-running events: eight `UNC_IIO_BANDWIDTH_IN.PART*_FREERUN` counters and `UNC_IIO_CLOCKTICKS_FREERUN`. These use `Unit: iio_free_running`, individual counter IDs, and `EventCode: 0xff`. They are distinct from normal programmable `IIO` events and should be matched to the free-running PMU exposed by the kernel.

The early `IIO` section defines `UNC_IIO_CLOCKTICKS`, `UNC_IIO_COMP_BUF_INSERTS.CMPD.*`, and `UNC_IIO_COMP_BUF_OCCUPANCY.CMPD.*`. These events describe IIO traffic-controller clocks and PCIe completion-buffer activity. `PART0`-`PART7` variants filter through `PortMask` values from `0x01` through `0x80`; `ALL` and `ALL_PARTS` use `PortMask: 0xFF`.

The largest section is a regular matrix of request classifiers. `UNC_IIO_DATA_REQ_BY_CPU.*` and `UNC_IIO_TXN_REQ_BY_CPU.*` are outbound CPU/main-die initiated requests to card/device spaces. `UNC_IIO_DATA_REQ_OF_CPU.*` and `UNC_IIO_TXN_REQ_OF_CPU.*` are inbound card-initiated requests of the CPU/main die. Families are repeated across request classes such as `CFG_READ`, `CFG_WRITE`, `IO_READ`, `IO_WRITE`, `MEM_READ`, `MEM_WRITE`, `PEER_READ`, `PEER_WRITE`, `ATOMIC`, `CMPD`, and `MSG`. Most families provide ten variants: `IOMMU0`, `IOMMU1`, and `PART0` through `PART7`.

The IOMMU section defines lookup, hit, miss, page-walk, page-walk-cache, interrupt-cache, context-cache, and invalidation counters under `UNC_IIO_IOMMU0.*`, `UNC_IIO_IOMMU1.*`, and `UNC_IIO_IOMMU3.*`. These events are useful for diagnosing DMA translation behavior and IOTLB/context-cache churn.

Debug and queue-state events include `UNC_IIO_MASK_MATCH_AND.*`, `UNC_IIO_MASK_MATCH_OR.*`, `UNC_IIO_NOTHING`, `UNC_IIO_NUM_OUSTANDING_REQ_FROM_CPU.TO_IO` (note the spelling in the source event name), `UNC_IIO_NUM_OUTSTANDING_REQ_OF_CPU.*`, `UNC_IIO_NUM_REQ_FROM_CPU.*`, `UNC_IIO_NUM_REQ_OF_CPU.*`, and `UNC_IIO_NUM_REQ_OF_CPU_BY_TGT.*`. These encode arbitration, outstanding request occupancy, target classes such as memory, peer-to-peer, multicast, abort, Ubox, and packet/drop behavior.

The PCIe completion pipeline appears in `UNC_IIO_REQ_FROM_PCIE_PASS_CMPL.*`, `UNC_IIO_REQ_FROM_PCIE_CL_CMPL.*`, and `UNC_IIO_REQ_FROM_PCIE_CMPL.*`. Their descriptions distinguish pass completion, cache-line completion, and whole PCIe request completion, and they reuse subconditions such as `DATA`, `FINAL_RD_WR`, `REQ_OWN`, `WR`, `IOMMU_REQ`, and `IOMMU_HIT`.

The transaction section mirrors much of the earlier data-request section but counts transactions rather than doublewords or cache-line data. `UNC_IIO_TXN_REQ_BY_CPU.*` uses `EventCode: 0xC1`; `UNC_IIO_TXN_REQ_OF_CPU.*` uses `EventCode: 0x84`. This distinction matters for users comparing bandwidth-like data counters against request/transaction-rate counters.

At line 5175 the chunk enters `M2PCIe` with `UNC_M2P_AG0_AD_CRD_ACQUIRED0.TGR0` through `.TGR7`, `UNC_M2P_AG0_AD_CRD_ACQUIRED1.TGR8`, `.TGR9`, `.TGR10`, and `UNC_M2P_AG0_AD_CRD_OCCUPANCY0.TGR0` through `.TGR2`. These count CMS Agent0 AD credits acquired or in use per transgress. The family continues beyond this chunk.

## Control Flow And Integration

There is no local control flow in the JSON file. The effective control flow is the perf build and lookup pipeline:

1. The perf build system includes `pmu-events/arch` data and runs `pmu-events/jevents.py`.
2. `jevents.py` parses each JSON object, lowercases event names for generated table matching, maps fields such as `PortMask` and `FCMask` to perf event encodings, and emits generated `pmu-events.c`.
3. The generated events are compiled into `libpmu-events.a` and linked into perf.
4. Runtime perf PMU lookup code uses the generated tables to expose these event names and descriptions when the detected CPU model maps to Ice Lake Xeon.
5. Users select these events by symbolic name; perf converts the generated event string into kernel perf_event attributes for the matching uncore PMU instance.

The important integration point is that `Unit` must match kernel PMU names closely enough for perf to bind symbolic events to the right PMU. `IIO`, `iio_free_running`, and `M2PCIe` entries are not interchangeable, even when event names share the `UNC_` prefix.

## State And Persistence Behavior

The file stores static metadata in the source tree. It has no runtime persistence, mutation, or state machine. State enters through generated artifacts: changes to this JSON alter generated `pmu-events.c`, the compiled perf event table, and the user-visible `perf list` catalog. At runtime, counter state lives in hardware PMU registers and perf kernel/user-space data structures, not in this file.

The `PerPkg: 1` flag on every complete event in this chunk is a persistent semantic marker in the generated table. It tells perf consumers that these are package-scope uncore events and must not be interpreted as per-thread or per-core counts.

## Dependencies

This chunk depends on the perf PMU events schema and parser accepting Intel event fields:

- `jevents.py` must understand standard fields (`EventName`, `EventCode`, `UMask`, `Counter`, descriptions, `Unit`, `PerPkg`) and Intel uncore qualifiers (`PortMask`, `FCMask`).
- The Ice Lake Xeon CPU model mapping under `pmu-events/arch/x86/mapfile.csv` must select this directory for the relevant model IDs.
- The kernel must expose compatible uncore PMUs with names corresponding to `IIO`, `iio_free_running`, and `M2PCIe`.
- Tests and tooling assume the JSON remains syntactically valid as one complete array across all chunks of the full file.

## Risks And Edge Cases

The line range ends mid-object at line 5,325. This chunk report intentionally covers only complete objects through line 5,324 and records the dangling opening brace as a handoff point for the next chunk. A merge lane must not treat this chunk alone as a valid standalone JSON document.

Many event descriptions encode lane and slot topology. Incorrect `PortMask` values or stale lane descriptions would cause users to collect counts for the wrong PCIe segment. Several descriptions appear mechanically repeated; for example some early completion-buffer `PART3`/`PART7` descriptions mention `Part 2`, and `PART4`/`PART5` text repeats lower part numbers. That may be source-data drift rather than parser behavior, but it affects user-facing documentation.

The spelling `UNC_IIO_NUM_OUSTANDING_REQ_FROM_CPU.TO_IO` is preserved from the source. Renaming it to fix spelling would break the symbolic event name users may already reference.

`Experimental: 1` is widespread, including most IIO classifier and M2PCIe entries. Consumers should avoid treating all names here as stable architectural interfaces.

The data-request and transaction-request families are highly repetitive but not identical. Bulk edits risk swapping `EventCode`, `UMask`, `PortMask`, or direction text between outbound `BY_CPU` and inbound `OF_CPU` families. `IOMMU0`/`IOMMU1` entries use `PortMask` values `0x100` and `0x200`, while physical parts use `0x01`-`0x80`; those masks should not be normalized together.

Free-running events use different unit/counter semantics from regular programmable events. Treating `iio_free_running` entries like ordinary `IIO` events would select the wrong PMU or counter class.

## Test Signals

Useful validation signals for this chunk and the eventual merged file:

- JSON validation of the complete `uncore-io.json` array after all chunks are considered.
- Rebuild perf PMU events generation, especially the `pmu-events/jevents.py` path that emits `pmu-events.c`.
- Run perf PMU event tests such as `tools/perf/tests/pmu-events.c` coverage and metric/event parser tests where available.
- Check that `perf list` on a matching Ice Lake Xeon system exposes representative names from each unit: `UNC_IIO_CLOCKTICKS`, `UNC_IIO_DATA_REQ_BY_CPU.MEM_READ.PART0`, `UNC_IIO_TXN_REQ_OF_CPU.MSG.PART7`, `UNC_IIO_SYMBOL_TIMES`, and `UNC_M2P_AG0_AD_CRD_ACQUIRED0.TGR0`.
- On hardware, smoke-test representative events with `perf stat -e` against the correct uncore PMU and verify package-level behavior rather than per-core duplication.
- Diff generated `pmu-events.c` before and after any source edit to ensure only intended event rows changed.
