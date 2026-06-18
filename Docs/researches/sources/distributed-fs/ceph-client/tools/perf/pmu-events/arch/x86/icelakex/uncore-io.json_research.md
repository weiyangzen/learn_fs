# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-io.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006685`: lines 1-5325, `Docs/researches/chunks/subset-b-006685_research.md`
- `subset-b-006686`: lines 5326-10852, `Docs/researches/chunks/subset-b-006686_research.md`
- `subset-b-006687`: lines 10853-11088, `Docs/researches/chunks/subset-b-006687_research.md`

## Chunk Research

### subset-b-006685: lines 1-5325

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

### subset-b-006686: lines 5326-10852

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-io.json lines 5326-10852

## Scope

This chunk covers a large middle-to-late slice of the Ice Lake Xeon `uncore-io.json` PMU event table used by the vendored Linux `tools/perf` PMU event machinery. The range is declarative event metadata, not executable Ceph client logic.

The requested line range begins after the opening fields of `UNC_M2P_AG0_AD_CRD_OCCUPANCY0.TGR2`; the first complete event in the chunk is `UNC_M2P_AG0_AD_CRD_OCCUPANCY0.TGR3`. It ends inside the next event object, after the `EventName` for `UNC_M2P_VERT_RING_AD_IN_USE.DN_EVEN`; that object continues in the following chunk. Counting by `EventName` lines in the requested range, this slice contains 515 event-name occurrences, 514 complete `Unit` fields, and all visible events belong to the `M2PCIe` uncore PMU unit.

## Purpose

The file defines user-visible perf event names and their hardware encodings for Ice Lake Xeon uncore I/O monitoring. Perf consumes entries from this JSON to map event strings such as `UNC_M2P_IIO_CREDITS_USED.NCB_0` or `UNC_M2P_TxR_HORZ_OCCUPANCY.AD_CRD` to event select values, unit masks, counter constraints, package scope, and descriptions.

This chunk is specifically the M2PCIe/Common Mesh Stop portion of the table. It describes events for M2PCIe-to-IIO credits, CMS ingress and egress queues, horizontal and vertical mesh rings, agent/transgress credit use, starvation, NACKs, queue occupancy, queue-full/non-empty cycles, anti-deadlock-slot usage, and ring bounce/sink behavior. These events let perf users diagnose package-level I/O and mesh pressure rather than Ceph data-path behavior.

## Important Data and Event Families

Every visible event uses the perf PMU JSON schema: `BriefDescription`, `Counter`, `EventCode`, `EventName`, `Experimental`, `PerPkg`, `PublicDescription` where available, `UMask`, and `Unit`. Almost all entries advertise counters `0,1,2,3`; a smaller group uses `0,1` for narrower counter support. Most entries have `"Experimental": "1"` and all complete entries in this range have `"PerPkg": "1"`, meaning perf treats the event as package-scoped uncore metadata.

The leading family continues `UNC_M2P_AG*_AD/BL_CRD_*` definitions. These break CMS agent 0 and agent 1 AD/BL credit acquisition and occupancy into transgress selectors. Transgresses 0-7 are typically encoded in the `*0` event-code half with power-of-two unit masks, while transgresses 8-10 are represented by the `*1` event-code half. The chunk starts mid-family with agent 0 AD occupancy for transgress 3 and then covers BL credit acquisition/occupancy for agent 0, AD and BL credit acquisition/occupancy for agent 1, and related event-code pairs from `0x82` through `0x8f`.

The IIO credit families include `UNC_M2P_IIO_CREDITS_ACQUIRED`, `UNC_M2P_IIO_CREDITS_REJECT`, and `UNC_M2P_IIO_CREDITS_USED`. Their descriptions identify DRS, NCB, and NCS message classes and CMS port 0/1 splits. These events count acquired credits, failed acquisition attempts, and cycles with credits in use for BL-ring traffic moving from the M2PCIe agent into the IIO.

Peer-to-peer credit families include local and remote dedicated/shared P2P credit taken, returned, and wait events, along with received and occupancy events. Names distinguish local versus remote, dedicated versus shared, taken versus returned, and wait versus occupancy. This lets perf isolate pressure in P2P credit pools rather than only seeing aggregate ring traffic.

Ingress-side CMS families include `UNC_M2P_RxC_*` and `UNC_M2P_RxR_*`. They cover cycles non-empty, inserts, busy-starved, bypass, credit-starved, occupancy, and allocation behavior for traffic received from the mesh into CMS ingress structures. The unit masks further split ring classes such as AD, AK, AKC, BL, and IV, with credited/uncredited/all variants for some families.

Ring health families include horizontal and vertical ring in-use, bounce, source throttle, and sink-starvation events. `UNC_M2P_HORZ_RING_*_IN_USE` covers AD/AK/AKC/BL/IV ring use by direction and even/odd ring where applicable. `UNC_M2P_RING_BOUNCES_HORZ` and `UNC_M2P_RING_BOUNCES_VERT` count bounced incoming messages by ring type. `UNC_M2P_RING_SINK_STARVED_*` captures sink starvation by ring/message class, and `UNC_M2P_RING_SRC_THRTL` provides source-throttle coverage.

Transgress and egress families are heavily represented. `UNC_M2P_TxC_*` covers egress-to-CMS credits, queue full/non-empty cycles, and inserts. `UNC_M2P_TxR_HORZ_*` and `UNC_M2P_TxR_VERT_*` cover horizontal and vertical egress paths: ADS/bypass usage, cycles full, cycles non-empty, inserts, NACKs, occupancy, and injection starvation. These are split by ring type and by CMS agent where the hardware exposes agent-specific masks.

Stall families `UNC_M2P_STALL0_NO_TxR_HORZ_CRD_*` and `UNC_M2P_STALL1_NO_TxR_HORZ_CRD_*` count cycles where AD or BL agent egress buffers are stalled waiting for transgress credits. As with the credit families, the event-code suffix splits transgress 0-7 from transgress 8-10.

The chunk ends by starting the vertical ring in-use family with `UNC_M2P_VERT_RING_AD_IN_USE.DN_EVEN`. The complete object and the rest of the vertical ring in-use definitions continue after the requested line range.

## Control Flow

There is no in-file control flow. Runtime behavior is provided by perf's generated PMU event tables:

1. Perf detects the Ice Lake Xeon CPU model and selects the `arch/x86/icelakex` event metadata.
2. A user or tool requests an event by `EventName`.
3. Perf resolves the matching JSON object and checks the counter constraint, package scope, and PMU unit.
4. Perf programs the `M2PCIe` uncore PMU with the entry's `EventCode` and `UMask`.
5. Hardware accumulates counts for the selected queue, credit, ring, NACK, stall, starvation, or occupancy condition until perf reads the counter.

The apparent structure in this chunk is generated by hardware event decomposition rather than code branching. Event-code pairs, such as `*0` and `*1` families, extend one conceptual metric across more unit-mask selectors than one event code can carry. Perf does not infer those relationships from names; it consumes the explicit object for each event.

## State and Persistence Behavior

The JSON is static metadata. It does not store measurements and has no mutable state inside Ceph or perf. Its persistence behavior is repository/build persistence: changing an event name, code, mask, counter list, or description changes how built perf exposes Ice Lake Xeon uncore events.

At runtime, state exists in hardware PMU counters and perf event attributes. `PerPkg` indicates package-level accounting, so counts are tied to the package/uncore instance rather than a process, core, or thread. Many events are occupancy or cycles-in-condition metrics; their values depend on elapsed measurement time and need normalization against clockticks or a related cycle event for rate analysis.

The `Experimental` flag is persistent metadata too. It signals that these M2PCIe events may be less stable or less generally validated than non-experimental events, while still making them available to perf users.

## Dependencies and Integration Points

This file integrates with the Linux perf PMU event parser, generated perf event tables, and the Ice Lake Xeon uncore M2PCIe PMU. It is present under `sources/distributed-fs/ceph-client` as vendored Linux tooling data, so the relevant integration surface is perf, not Ceph's filesystem client runtime.

The event definitions depend on Intel's uncore hardware encodings for the `M2PCIe` unit. Correctness requires `EventCode`, `UMask`, `Counter`, and package-scope metadata to match the CPU model's PMU programming interface. The ring names and message-class names depend on Intel mesh terminology: AD, AK, AKC, BL, IV, DRS, NCB, NCS, credited/uncredited traffic, CMS agents, CMS ports, and transgress buffers.

Perf-side integration is name-driven. Scripts, dashboards, tests, and documentation can request these exact `UNC_M2P_*` names. Any rename or mask change has compatibility impact even though the file is data-only.

## Risks and Edge Cases

Chunk-boundary parsing is the first risk. The requested range starts and ends inside event objects, so the chunk alone is not valid JSON and should not be used as an independent parser fixture. Full-file validation must parse `uncore-io.json` as a whole.

The event families are highly repetitive, making copy/paste drift plausible. Common risks are swapped agent numbers, local versus remote P2P confusion, dedicated versus shared credit confusion, credited/uncredited/all mask drift, horizontal versus vertical ring mix-ups, and transgress 8-10 entries assigned to the wrong `*1` event code or unit mask.

Some descriptions appear inconsistent with names. For example, several `CYCLES_FULL` descriptions say "Not Full", and the final visible `UNC_M2P_TxR_VERT_STARVED1.TGC` entry describes "AKC - Agent 0" even though the event name is `TGC`. These may reflect upstream metadata quirks, but they are important because users often rely on `PublicDescription` for interpretation.

Case and formatting should be preserved. The chunk contains both `0x2D` and `0x2d` event-code spellings for `UNC_M2P_TxC_CREDITS.*`; JSON parsers accept both as strings, but tooling or tests that canonicalize encodings should avoid treating harmless case differences as semantic changes.

Many entries are package-level uncore events with counter constraints. Running several events from the same counter-constrained set at once may require multiplexing or may fail depending on perf/kernel scheduling. Interpreting occupancy and starvation counters without a cycle baseline can lead to misleading conclusions.

Hardware availability is model-specific. These names belong to `icelakex`; using them on another CPU family, or with a kernel/perf build whose uncore PMU support differs, may fail or count different hardware behavior.

## Test Signals

Useful validation starts with strict parsing of the complete `uncore-io.json` file and a schema check for every event object. For this chunk, checks should confirm that complete objects have `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, and `PerPkg`, with `Unit` equal to `M2PCIe` for the complete entries in range.

Generated perf event-table tests should verify representative names from each family: `UNC_M2P_AG1_BL_CRD_OCCUPANCY1.TGR10`, `UNC_M2P_IIO_CREDITS_REJECT.NCS`, `UNC_M2P_LOCAL_SHAR_P2P_CRD_WAIT_0.*`, `UNC_M2P_RxR_OCCUPANCY.*`, `UNC_M2P_RING_BOUNCES_VERT.BL`, `UNC_M2P_STALL0_NO_TxR_HORZ_CRD_AD_AG0.TGR0`, `UNC_M2P_TxC_CYCLES_FULL.*`, `UNC_M2P_TxR_HORZ_NACK.*`, and `UNC_M2P_TxR_VERT_STARVED1.*`.

Encoding tests should sample families with split event-code halves and confirm the transgress-to-mask mapping: transgresses 0-7 use masks `0x1` through `0x80` on the base event code, while transgresses 8-10 use masks `0x1`, `0x2`, and `0x4` on the paired event code.

Runtime smoke tests on Ice Lake Xeon hardware should use `perf list` to confirm the names are exposed under the M2PCIe/uncore unit, then run `perf stat` on low-risk representative events. Traffic-producing tests should exercise PCIe/IIO paths to see non-zero IIO credit counts, mesh pressure tests should affect RxR/TxR occupancy or inserts, and idle baselines should remain low for NACK/starvation events.

Documentation tests should flag mismatches between `EventName`, `BriefDescription`, and `PublicDescription`, especially the `CYCLES_FULL` text and `TGC`/`AKC` wording. These are not parser failures, but they are user-facing interpretation risks.

## Cross-Chunk Notes

The previous chunk is required to reconstruct the full `UNC_M2P_AG0_AD_CRD_OCCUPANCY0.TGR2` object and the earliest portion of the agent 0 AD occupancy family. The next chunk is required to finish `UNC_M2P_VERT_RING_AD_IN_USE.DN_EVEN` and cover the rest of the vertical ring in-use definitions.

The merge lane should combine this with other chunks for `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-io.json` before producing a final per-file report, because this document intentionally describes only the requested line slice and its immediate boundary context.

### subset-b-006687: lines 10853-11088

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-io.json lines 10853-11088

## Scope

This chunk covers the tail of the Ice Lake Xeon `uncore-io.json` PMU event table in the vendored Linux `tools/perf` tree. The file is static JSON metadata, not executable code. The perf PMU event generator consumes these objects and emits generated C event tables so users can request uncore IO events by symbolic names.

The requested range starts inside the `UNC_M2P_VERT_RING_AD_IN_USE.DN_EVEN` object: lines 10847-10852 contain its opening fields, while line 10853 begins at its `PublicDescription`. The rest of the chunk contains complete event objects and closes the JSON array at line 11088. Including the partially opened first object, this slice covers 22 M2PCIe vertical-ring usage events: four AD events, four AKC events, four AK events, four BL events, two IV events, and four TGC events.

## Purpose

These records expose Ice Lake Xeon M2PCIe uncore IO events for measuring cycles in which vertical ring links are in use at an M2PCIe ring stop. They are intended for low-level IO fabric analysis, especially determining whether traffic is occupying specific vertical ring directions, ring parities, and message classes.

The event families in this chunk are:

- `UNC_M2P_VERT_RING_AD_IN_USE.*` for AD ring usage.
- `UNC_M2P_VERT_RING_AKC_IN_USE.*` for AKC ring usage.
- `UNC_M2P_VERT_RING_AK_IN_USE.*` for AK ring usage.
- `UNC_M2P_VERT_RING_BL_IN_USE.*` for BL ring usage.
- `UNC_M2P_VERT_RING_IV_IN_USE.*` for IV ring usage.
- `UNC_M2P_VERT_RING_TGC_IN_USE.*` for TGC ring usage.

Each event counts cycles where the named vertical ring is being used at the ring stop, including packets passing by or being sunk. The descriptions explicitly exclude packets being sent from the ring stop, so these are not total injection counters.

## Important Data Fields

Each JSON object follows the perf PMU event schema used under `tools/perf/pmu-events`:

- `EventName` is the symbolic name exposed to `perf list` and accepted by `perf stat -e`.
- `EventCode` selects the M2PCIe hardware event family. This chunk uses `0xb0` for AD, `0xb1` for AK, `0xb2` for BL, `0xb3` for IV, `0xb4` for AKC, and `0xb5` for TGC.
- `UMask` selects direction and parity. `0x1` maps to up/even, `0x2` to up/odd, `0x4` to down/even or down for IV, and `0x8` to down/odd.
- `Counter` is `"0,1,2,3"` for all records, indicating these events can be scheduled on any of the four listed M2PCIe uncore counters.
- `Unit` is `"M2PCIe"` throughout the chunk, binding the events to M2PCIe uncore PMUs rather than core PMUs or other uncore units.
- `PerPkg` is `"1"` throughout, marking the events as package-scoped.
- `Experimental` is `"1"` throughout, warning consumers that these event definitions may be less stable or less broadly validated than non-experimental events.
- `BriefDescription` and `PublicDescription` provide user-facing summaries and longer `perf list --details` text.

## APIs, Types, And Generated Representation

There are no local functions, classes, or C types defined in this JSON file. Its API surface is the generated PMU event metadata:

- `tools/perf/pmu-events/jevents.py` traverses CPU model JSON files and generates `pmu-events.c`.
- `struct pmu_event` in `tools/perf/pmu-events/pmu-events.h` carries generated fields such as `name`, `event`, `desc`, `long_desc`, `pmu`, `unit`, and `perpkg`.
- `pmu_events_table__for_each_event()` iterates generated event records for display and alias construction.
- `pmu_events_table__find_event()` resolves a symbolic event name against the generated model table.
- Runtime perf commands such as `perf list` and `perf stat -e` consume these generated aliases and program the matching uncore PMU event selectors through the kernel perf event interface.

For this chunk, `EventCode`, `UMask`, `Counter`, `Unit`, and `PerPkg` are the operational fields. The descriptions are metadata for users, but mistakes in `EventCode` or `UMask` would change the hardware counter programmed by perf.

## Control Flow

The JSON has no direct runtime control flow. Its effective build and runtime flow is:

1. The perf build runs the PMU event generation path.
2. `jevents.py` reads `tools/perf/pmu-events/arch/x86/icelakex/uncore-io.json` along with the other Ice Lake Xeon topic JSON files.
3. The generator validates each event object and emits generated event-table entries.
4. The generated tables are compiled into perf.
5. At runtime, perf maps matching Intel CPUID patterns from `arch/x86/mapfile.csv` to the `icelakex` directory.
6. `perf list` exposes names such as `UNC_M2P_VERT_RING_TGC_IN_USE.UP_ODD`.
7. `perf stat -a -e <event>` or similar commands resolve the symbolic name and ask the kernel uncore PMU driver to program the package-level M2PCIe counter.

The chunk is ordered by ring/message class: AD, AKC, AK, BL, IV, then TGC. Within most families the records follow down/even, down/odd, up/even, up/odd. The IV family has only `DN` and `UP`, because the description says there is only one IV ring.

## State And Persistence Behavior

The persistent state is the checked-in JSON metadata plus the generated perf event table produced at build time. This source does not create files, mutate process state, persist measurements, or hold runtime state.

At runtime, the measured state lives in M2PCIe uncore hardware counters. These counters accumulate ring-use cycles for package-level IO fabric PMUs. Because `PerPkg` is set, results should be interpreted as package-scoped uncore measurements, not per-thread or per-core counts.

The distinction between passing/sunk packets and packets sent from the ring stop is important state semantics. These events describe observed ring occupancy at the stop, not outbound injection by that stop. For AD, AK, AKC, BL, and TGC, direction and parity split the measurement across two physical ring directions and even/odd ring classes. For IV, users must combine direction filters according to the description if they want an even-ring or odd-ring view; the naming does not expose separate even/odd IV event names in this chunk.

## Dependencies And Integration Points

This chunk integrates with the Linux perf PMU event stack:

- `tools/perf/pmu-events/README` documents JSON topic files, `mapfile.csv`, and generation of `pmu-events.c`.
- `tools/perf/pmu-events/jevents.py` parses these records and emits generated C tables.
- `tools/perf/pmu-events/pmu-events.h` defines the generated event-table interface.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` maps Ice Lake Xeon CPUID patterns `GenuineIntel-6-6[AC]` to the `icelakex` PMU event directory.
- The Linux x86 uncore PMU driver must expose compatible M2PCIe PMUs and counters for these aliases to work on real hardware.

Although the source path is under `sources/distributed-fs/ceph-client`, this file belongs to a vendored Linux perf tooling subtree. It has no direct CephFS client, distributed filesystem protocol, metadata-server, network IO, or storage control-flow integration.

## Event Family Notes

The AD, AK, AKC, BL, and TGC families each model a four-way direction/parity split:

- `.UP_EVEN` uses `UMask: "0x1"`.
- `.UP_ODD` uses `UMask: "0x2"`.
- `.DN_EVEN` uses `UMask: "0x4"`.
- `.DN_ODD` uses `UMask: "0x8"`.

The public descriptions explain that there are clockwise and counter-clockwise rings. On the left side of the ring, UP is clockwise and DN is counter-clockwise; on the right side this is reversed. They also warn that the first half of CBo stops and the second half are on opposite sides, so the same direction label can refer to different physical rings depending on CBo position.

The IV family is different. `UNC_M2P_VERT_RING_IV_IN_USE.DN` uses `UMask: "0x4"` and `.UP` uses `UMask: "0x1"`. The description says there is only one IV ring, then refers to selecting both `UP_EVEN` and `DN_EVEN` or both `UP_ODD` and `DN_ODD`; that text does not line up cleanly with the two exposed event names in this chunk. Consumers should treat IV event interpretation cautiously and verify against Intel uncore documentation or empirical perf behavior.

## Risks And Edge Cases

The first event in the requested range is incomplete when the chunk is viewed alone. Its `BriefDescription`, `Counter`, `EventCode`, `EventName`, `Experimental`, and `PerPkg` fields are on lines 10847-10852, just before the requested start. The merge lane must use adjacent chunks or full-file context before validating object completeness.

All events are marked experimental. Tooling should still parse and expose them, but users should be aware that names, masks, or descriptions may have weaker stability guarantees.

Several public descriptions contain rough inherited wording, including references to `JKT`, the phrase `We really have two rings in --`, and spacing issues such as missing spaces after periods. These are user-facing strings in perf output. Cleaning them up can improve readability, but doing so should not be mixed with semantic changes to event codes or masks.

The direction/parity mapping is easy to misread. A single swapped `UMask` between `UP_ODD` and `DN_EVEN`, for example, would still be valid JSON and likely still build, but it would silently measure the wrong physical ring class.

The final TGC object is followed by the file-closing `]` and has no trailing comma. Any edit at this tail must preserve complete JSON array syntax for the entire `uncore-io.json` file.

## Test Signals

Useful validation signals for this chunk include:

- Running JSON validation on the complete `icelakex/uncore-io.json`, not on this partial line slice alone.
- Running the perf PMU event generation path and confirming `pmu-events.c` generation succeeds without schema or parse errors.
- Building perf with generated PMU events enabled.
- Running perf PMU event tests that exercise generated table lookup, especially code paths using `pmu_events_table__find_event()`.
- Using `perf list --details` on an Ice Lake Xeon-capable perf build to spot-check events such as `UNC_M2P_VERT_RING_AD_IN_USE.DN_EVEN`, `UNC_M2P_VERT_RING_AK_IN_USE.UP_ODD`, `UNC_M2P_VERT_RING_IV_IN_USE.UP`, and `UNC_M2P_VERT_RING_TGC_IN_USE.DN_ODD`.
- On Ice Lake Xeon hardware with M2PCIe uncore PMUs exposed, running package-wide `perf stat` for representative UP/DN and even/odd variants and confirming scheduling succeeds and counts are plausible under IO traffic.

## Cross-Chunk Notes

This document intentionally covers only lines 10853-11088. Earlier chunks contain the opening fields for the first AD event in this range and the preceding M2PCIe event families. The final per-file research document should reconcile this tail chunk with prior chunks before making whole-file claims about total event counts or family coverage.
