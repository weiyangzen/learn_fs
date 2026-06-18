# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-interconnect.json lines 6509-7626

## Scope

This chunk covers the tail of the Emerald Rapids `uncore-interconnect.json` PMU event table. It is declarative perf PMU metadata, not executable code. The requested line range starts inside the `UNC_UPI_RxL_BASIC_HDR_MATCH.NCB` object: lines 6507-6508 immediately before the range provide its `BriefDescription` and `Counter`, while lines 6509-6515 contain the rest of the record. The range then continues through UPI receive-side, UPI transmit-side, UPI link-power/credit, and UBOX message/RACU events, ending with the file's closing JSON array at line 7626.

The covered records are primarily for package-scoped uncore PMUs on Intel Emerald Rapids. Most entries use `Unit: "UPI"` and counters `0,1,2,3`; the final section uses `Unit: "UBOX"` with either counters `0,1` or counter `0`.

## Purpose

The purpose of this chunk is to expose model-specific event aliases for perf on Emerald Rapids systems. These aliases let users invoke symbolic names such as `UNC_UPI_RxL_FLITS.ALL_DATA`, `UNC_UPI_TxL_FLITS.NON_DATA`, or `UNC_U_EVENT_MSG.MSI_RCVD` instead of manually specifying raw event selector and unit-mask encodings.

The UPI records measure link-level activity across receive and transmit paths: header class matches, valid flit classes, per-slot flit accounting, RxQ/TxQ buffer bypass and occupancy, credit consumption and return behavior, CRC/LLR recovery, and L0/L0p power-state cycles. The UBOX records measure package uncore message-channel activity, M2U queue/full/empty conditions, PHOLD cycles, DRNG/RACU activity, and selected interrupt/message classes.

## Important Data Shape and Event Families

Every entry is a JSON object using the perf PMU event schema. Important fields in this slice are:

- `EventName`: the symbolic perf event name. It encodes the hardware block (`UNC_UPI` or `UNC_U`), sub-block/path (`RxL`, `TxL`, `TxL0P`, `M2U`, `RACU`), and event variant suffix.
- `EventCode`: the raw selector programmed into the target PMU event register.
- `UMask`: the variant selector. Many families share one `EventCode` and split subevents by mask bits.
- `Counter`: the allowed programmable counter set. UPI events here use `0,1,2,3`; UBOX event-message and PHOLD/RACU request records use `0,1`; many M2U and DRNG records are limited to counter `0`.
- `Unit`: the target PMU unit name used by the generated event table. This chunk uses `UPI` and `UBOX`.
- `PerPkg`: set to `"1"` throughout, so these are package-scoped uncore events.
- `Experimental`: set on most records in this chunk, indicating the metadata is not as stable as architectural core PMU events.
- `PublicDescription`: present for richer entries and used by perf listing output. Several low-level diagnostic records have only `BriefDescription`.
- `FCMask` and `PortMask`: only visible on `UNC_UPI_RxL_CREDITS_CONSUMED_VNA`, both set to zero, preserving filter-mask fields in the event schema even though this event does not enable a specific filter or port mask.

Major UPI receive families in this chunk:

- `UNC_UPI_RxL_BASIC_HDR_MATCH.*` uses event `0x05` with masks `0xe`, `0x10e`, `0xf`, and `0x10f` for non-coherent bypass/standard header matching, optionally with opcode matching enabled. The public description documents UMask bit roles for message class, opcode, locality, data/non-data headers, and single/dual-slot headers; link-layer control types are excluded.
- `UNC_UPI_RxL_BYPASSED.SLOT0..SLOT2` uses event `0x31` and masks `0x1`, `0x2`, `0x4` to count incoming flits that bypass the Rx flit buffer.
- `UNC_UPI_RxL_CRC_ERRORS` and `UNC_UPI_RxL_CRC_LLR_REQ_TRANSMIT` use events `0x0b` and `0x08` to track detected CRC errors and link-layer retry requests.
- `UNC_UPI_RxL_CREDITS_CONSUMED_VN0/VN1/VNA` uses events `0x39`, `0x3a`, and `0x38` to account for RxQ credit consumption.
- `UNC_UPI_RxL_FLITS.*` uses event `0x03`; masks distinguish slots `0x1/0x2/0x4`, data `0x8`, LLCRD `0x10`, null `0x20`, LLCTRL `0x40`, protocol header `0x80`, and aggregate masks such as `ALL_DATA` `0xf`, `ALL_NULL` `0x27`, and `NON_DATA` `0x97`.
- `UNC_UPI_RxL_INSERTS.SLOT0..SLOT2` and `UNC_UPI_RxL_OCCUPANCY.SLOT0..SLOT2` use events `0x30` and `0x32` for RxQ allocations and cycle-accumulated occupancy.
- `UNC_UPI_RxL_SLOT_BYPASS.*` uses event `0x33` with masks `0x1` through `0x20` for slot-to-RxQ bypass combinations. These have terse generated-style descriptions only.

Major UPI transmit and power families:

- `UNC_UPI_TxL0P_CLK_ACTIVE.*` uses event `0x2a` and masks individual L0p-active clock reasons or blocks: config/control, RxQ, RxQ bypass, RxQ credits, TxQ, retry, DFX, and spare.
- `UNC_UPI_TxL0P_POWER_CYCLES`, `UNC_UPI_TxL0P_POWER_CYCLES_LL_ENTER`, `UNC_UPI_TxL0P_POWER_CYCLES_M3_EXIT`, and `UNC_UPI_TxL0_POWER_CYCLES` use events `0x27`, `0x28`, `0x29`, and `0x26`. The documented entries distinguish L0p's reduced-lane power-saving state from L0's full-performance state and note that link power states are per-link and per-direction.
- `UNC_UPI_TxL_ANY_FLITS.*` uses event `0x4A` with slot/type masks mirroring the Rx "any flits" family immediately before the chunk.
- `UNC_UPI_TxL_BASIC_HDR_MATCH.*` uses event `0x04` with the same NCB/NCS and opcode-match mask pattern as the Rx basic header matcher.
- `UNC_UPI_TxL_BYPASSED`, `UNC_UPI_TxL_INSERTS`, and `UNC_UPI_TxL_OCCUPANCY` use events `0x41`, `0x40`, and `0x42` to expose Tx flit-buffer bypasses, allocations, and occupancy.
- `UNC_UPI_TxL_FLITS.*` uses event `0x02` with masks for all data, all LLCRD, all LLCTRL, all null, all protocol header, data, idle, LLCRD, LLCTRL, non-data, null, protocol header, and slots 0-2.
- `UNC_UPI_VNA_CREDIT_RETURN_BLOCKED_VN01` and `UNC_UPI_VNA_CREDIT_RETURN_OCCUPANCY` use events `0x45` and `0x44` for VNA credit-return backpressure and pending-return occupancy.

The final UBOX families:

- `UNC_U_EVENT_MSG.*` uses event `0x42` and masks `0x1`, `0x2`, `0x4`, `0x8`, and `0x10` for VLW, MSI, IPI, doorbell, and interrupt-priority messages.
- `UNC_U_M2U_MISC1.*` uses event `0x4d` and masks `0x1` through `0x80` for receive-channel cycles not empty and transmit-credit-overflow cycles across CBO/UPI and NCB/NCS classes.
- `UNC_U_M2U_MISC2.*` uses event `0x4e` for Rx/Tx BL queue full/empty states, VN0 credit-overflow states, and AK/AKC empty states.
- `UNC_U_M2U_MISC3.*` uses event `0x4f` for TxC AK and AKC full cycles.
- `UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK` uses event `0x45`, mask `0x1`, to count PHOLD assert-to-ack cycles.
- `UNC_U_RACU_DRNG.*` uses event `0x4c` and masks for `RDRAND`, `RDSEED`, and prefetch-buffer-empty DRNG-related states.
- `UNC_U_RACU_REQUESTS` uses event `0x46` to count outstanding register requests within the message channel tracker.

## APIs, Types, and Generated Representation

This JSON is consumed by perf's PMU event generator rather than by application code directly. In the perf build, `tools/perf/pmu-events/jevents.py` parses objects like these and emits generated C event tables. The generated data is exposed through perf's PMU event interfaces, including `struct pmu_event` and lookup/iteration helpers used by `perf list`, event parsing, and metric expansion.

For each object, `EventCode` and `UMask` become the raw encoded event terms used to configure `perf_event_attr.config` for the relevant uncore PMU. `BriefDescription` and `PublicDescription` become user-facing metadata. `Unit` selects the uncore PMU binding, while `PerPkg` marks package scope. `Counter` contributes scheduling constraints so perf does not attempt to place a UPI event on an unsupported counter.

There are no C functions, classes, or runtime callbacks defined in this file. The important "API" is the stable symbolic event-name contract between this checked-in JSON, generated perf event tables, user command lines, and any metric definitions that reference these names.

## Control Flow

There is no direct control flow in the JSON file. The effective flow is:

1. The perf PMU event build reads `arch/x86/mapfile.csv` and model directories such as `arch/x86/emeraldrapids`.
2. `jevents.py` parses `uncore-interconnect.json` and validates/normalizes fields from each event object.
3. The generator emits compact generated tables that include the UPI and UBOX records from this chunk.
4. At runtime, perf matches the running CPU model to the Emerald Rapids table.
5. Commands such as `perf list`, `perf stat -e`, and metric evaluation resolve symbolic names through the generated table.
6. When a selected event is opened, perf programs the relevant UPI or UBOX uncore PMU with the event selector, mask, package scope, and counter constraints represented by the generated record.

The closing `]` at line 7626 makes this chunk structurally significant: a syntax error near the tail invalidates the whole JSON table, not just the final UBOX records.

## State and Persistence Behavior

The persistent state is the checked-in event metadata plus the generated C event table produced during the perf build. This chunk does not create mutable state, store runtime samples, or perform I/O.

At runtime, state exists in perf's generated event descriptors, opened `perf_event_attr` instances, and hardware uncore counter registers. UPI records describe per-package link counters, often per direction, per slot, or per virtual network/credit class. UBOX records describe package-level message-channel and RACU/DRNG state. Because all records carry `PerPkg`, callers should interpret counts as package-scope observations rather than per-thread or per-core measurements.

The symbolic names are also persistent compatibility surface. A rename or mask change can break existing `perf stat -e UNC_UPI_...` command lines or silently change what a metric measures after regeneration.

## Dependencies and Integration Points

Primary dependencies and integration points:

- `tools/perf/pmu-events/jevents.py` parses the schema fields and generates perf event tables.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` maps Emerald Rapids CPU identifiers to this model directory.
- `tools/perf/pmu-events/pmu-events.h` defines the generated event table structures and lookup interfaces used by perf.
- `tools/perf/builtin-list.c` and the event parser consume generated event metadata for list output and event selection.
- The Linux x86 uncore PMU drivers and sysfs PMU descriptions must expose compatible UPI and UBOX PMUs, counters, and format fields for these encodings to schedule on real hardware.
- Higher-level metrics may reference these event names directly; even where they do not, user scripts often depend on `UNC_UPI_*` and `UNC_U_*` spelling stability.

Although this file is located under `sources/distributed-fs/ceph-client`, it is part of the vendored Linux perf tooling tree. It has no direct CephFS client protocol, caching, or distributed filesystem control flow.

## Risks and Edge Cases

- The requested range starts mid-object. A chunk-only reader could miss that `UNC_UPI_RxL_BASIC_HDR_MATCH.NCB` has `BriefDescription` and `Counter` fields immediately before line 6509.
- Many entries are `Experimental`; tooling should avoid treating these encodings as architectural guarantees across CPU generations.
- Header-match events rely on dense UMask semantics. Incorrectly changing `0xe`, `0xf`, `0x10e`, or `0x10f` can make NCB/NCS or opcode-match aliases count the wrong traffic while still parsing successfully.
- Flit type masks are compositional. Aggregate masks such as `ALL_DATA`, `ALL_NULL`, `ALL_LLCTRL`, `ALL_PROTHDR`, and `NON_DATA` must remain consistent with slot and type bit assignments.
- Rx and Tx families have intentionally similar names but different event codes (`RxL_FLITS` `0x03` versus `TxL_FLITS` `0x02`, `RxL_BASIC_HDR_MATCH` `0x05` versus `TxL_BASIC_HDR_MATCH` `0x04`). Copy/paste edits can easily swap direction-specific encodings.
- Several diagnostic records have no `PublicDescription`, so users may see terse names without explanatory context. That is acceptable for low-level uncore events but makes accidental renames or mask changes harder to review.
- Counter constraints differ between UPI and UBOX records. Scheduling bugs can occur if `Counter: "0"` UBOX M2U/DRNG records are widened or if UPI events are accidentally narrowed.
- Some descriptions contain spelling or text defects from the source metadata, such as `waitng`, `bypasssed`, and `ProtDDR`. These are user-visible through perf list output but are not syntax errors.
- Because this is the file tail, missing commas, malformed quotes, or an accidental trailing comma before the closing array would break JSON parsing for the entire Emerald Rapids uncore interconnect table.

## Test and Validation Signals

Useful validation signals for this chunk include:

- Parse the full file with a strict JSON parser, for example `python3 -m json.tool sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-interconnect.json`.
- Regenerate or build perf PMU event tables and confirm the Emerald Rapids generated table includes representative records from each family: `UNC_UPI_RxL_FLITS.ALL_DATA`, `UNC_UPI_RxL_OCCUPANCY.SLOT0`, `UNC_UPI_TxL0P_POWER_CYCLES`, `UNC_UPI_TxL_FLITS.NON_DATA`, `UNC_UPI_VNA_CREDIT_RETURN_OCCUPANCY`, `UNC_U_EVENT_MSG.MSI_RCVD`, and `UNC_U_RACU_REQUESTS`.
- Run perf PMU event table tests, especially generated event lookup and JSON/event parsing checks under `tools/perf/tests`.
- Inspect `perf list --details` on an Emerald Rapids-capable build to verify `Unit`, event code, unit mask, descriptions, package scope, experimental markers, and counter constraints are represented as expected.
- On suitable hardware, run `perf stat -e` with paired Rx/Tx events under known inter-socket traffic and verify directional counters respond plausibly.
- For link-quality checks, compare `UNC_UPI_RxL_CRC_ERRORS` and `UNC_UPI_RxL_CRC_LLR_REQ_TRANSMIT`; LLR requests should generally not exceed detected CRC errors as described by the metadata.
- For queueing/latency checks, compare Rx/Tx bypass, insert, and occupancy events under idle, NUMA-local, and heavy cross-socket workloads. Increased inserts/occupancy with lower bypass counts is the expected signal of link or ring-interface queueing.
- For UBOX records, verify `UNC_U_EVENT_MSG.*` events expose masks for VLW/MSI/IPI/doorbell/interrupt messages and that counter-0-only M2U/DRNG records are not scheduled on unsupported counters.

## Cross-Chunk Notes

This document intentionally covers only lines 6509-7626. The previous chunk contains the opening fields for the first event in this range and the preceding `UNC_UPI_RxL_ANY_FLITS.*` family. The merge lane should combine adjacent chunk notes before producing the final whole-file research document for `uncore-interconnect.json`.
