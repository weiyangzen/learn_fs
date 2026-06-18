# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json lines 16793-17915

## Scope

This chunk covers the final portion of the Ice Lake Xeon uncore interconnect PMU event JSON file. It starts inside the object for `UNC_UPI_RxL_BASIC_HDR_MATCH.WB_OPC` and then lists UPI receive-link, transmit-link, link-power, credit, and UBOX events through the closing `]` of the JSON array.

The source is data consumed by Linux `perf`, not executable Ceph code. Each object describes a discoverable perf event with fields such as `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `Experimental`, `BriefDescription`, and sometimes `PublicDescription`. The records map human-readable event aliases to Ice Lake Xeon uncore PMU encodings.

## Purpose

The file gives perf's PMU event tooling enough metadata to expose architectural and model-specific uncore measurements by name. For this range, the focus is Intel UPI and UBOX telemetry:

- UPI receive-side packet/header matching, flit classification, RxQ bypass, RxQ allocation, RxQ occupancy, CRC/LLR retry handling, and credit consumption.
- UPI transmit-side link power state cycles, clock-active reasons during L0p, packet/header matching, flit classification, TxQ bypass, TxQ allocation, TxQ occupancy, and VNA credit return state.
- UBOX package-level events for uncore clockticks, received message categories, IDI lock/split-lock cycles, M2U queue/credit conditions, PHOLD timing, RACU DRNG activity, and RACU request occupancy.

The practical consumer is `perf stat`, `perf list`, and related pmu-events generation code. A user can request names such as `UNC_UPI_TxL_FLITS.ALL_DATA` instead of manually programming event select and unit-mask values.

## Important APIs, Types, and Data

There are no functions, structs, or classes in this chunk. The public surface is the JSON event schema used by perf's PMU event tables.

Important fields are:

- `EventName`: stable perf-facing event alias, using Intel uncore naming conventions such as `UNC_UPI_RxL_*`, `UNC_UPI_TxL_*`, and `UNC_U_*`.
- `EventCode`: event select value programmed into the target PMU unit.
- `UMask`: unit-mask bits for subevents. Some events omit `UMask` when the event select is sufficient.
- `Unit`: target uncore PMU block. This range uses `UPI` for Ultra Path Interconnect link counters and `UBOX` for package uncore box counters.
- `Counter`: legal counter slots. UPI events generally allow counters `0,1,2,3`; UBOX programmable events generally allow `0,1`; `UNC_U_CLOCKTICKS` uses the fixed counter.
- `PerPkg`: marks package-scoped uncore accounting.
- `Experimental`: marks many events as lower-stability or less-promoted metadata in perf's event list.
- `BriefDescription` and `PublicDescription`: user-visible text for `perf list` and generated documentation.

The UPI receive portion includes:

- `UNC_UPI_RxL_BASIC_HDR_MATCH.WB_OPC` with event code `0x05` and UMask `0x10d`, completing a receive-path basic-header match family that begins in the preceding chunk.
- `UNC_UPI_RxL_BYPASSED.SLOT0/1/2`, which count incoming flits that bypass the RxQ flit buffer and move directly across the BGF into egress.
- `UNC_UPI_RxL_CRC_ERRORS` and `UNC_UPI_RxL_CRC_LLR_REQ_TRANSMIT`, which expose CRC detection and link-level retry request behavior.
- `UNC_UPI_RxL_CREDITS_CONSUMED_VN0`, `VN1`, and `VNA`, which count consumed RxQ virtual-network credits.
- `UNC_UPI_RxL_FLITS.*`, which classify received legal flit time by data, non-data, NULL, LLCRD, LLCTRL, protocol-header, and slot-mask dimensions.
- `UNC_UPI_RxL_INSERTS.SLOT0/1/2` and `UNC_UPI_RxL_OCCUPANCY.SLOT0/1/2`, which support RxQ queueing and average lifetime/occupancy analysis.
- `UNC_UPI_RxL_SLOT_BYPASS.*`, which expose slot-to-RxQ bypass combinations with sparse descriptions.

The UPI transmit portion includes:

- `UNC_UPI_TxL0P_CLK_ACTIVE.*`, an L0p clock-active reason family for config/control, DFX, retry, RxQ, RxQ bypass, RxQ credit, TxQ, and spare causes.
- `UNC_UPI_TxL0P_POWER_CYCLES`, `UNC_UPI_TxL0P_POWER_CYCLES_LL_ENTER`, `UNC_UPI_TxL0P_POWER_CYCLES_M3_EXIT`, and `UNC_UPI_TxL0_POWER_CYCLES`, which measure link-layer power state residency and transitions.
- `UNC_UPI_TxL_BASIC_HDR_MATCH.*`, matching transmit headers by message class and optional opcode across non-coherent bypass, non-coherent standard, request, response conflict, invalid response, data response, no-data response, snoop, and writeback classes.
- `UNC_UPI_TxL_BYPASSED`, `UNC_UPI_TxL_INSERTS`, and `UNC_UPI_TxL_OCCUPANCY`, which characterize TxQ bypass, allocation, and occupancy.
- `UNC_UPI_TxL_FLITS.*`, the transmit counterpart to the receive flit classification family.
- `UNC_UPI_VNA_CREDIT_RETURN_BLOCKED_VN01` and `UNC_UPI_VNA_CREDIT_RETURN_OCCUPANCY`, which expose VNA credit return backpressure and pending-return occupancy.

The UBOX portion includes:

- `UNC_U_CLOCKTICKS`, the fixed 48-bit UBOX clock counter event.
- `UNC_U_EVENT_MSG.*` for doorbell, interrupt priority, IPI, MSI, and legacy virtual logical wire messages received by UBOX.
- `UNC_U_LOCK_CYCLES` for IDI lock/split-lock sequence starts.
- `UNC_U_M2U_MISC1`, `UNC_U_M2U_MISC2`, and `UNC_U_M2U_MISC3` subevents for CBO/UPI non-coherent queue non-empty cycles, transmit-credit overflow cycles, empty/full AK/AKC/BL queue states, and VN0 credit overflow.
- `UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK` for PHOLD assert-to-ack timing.
- `UNC_U_RACU_DRNG.*` and `UNC_U_RACU_REQUESTS` for RDRAND/RDSEED/prefetch-buffer-empty and register access control unit request occupancy.

## Control Flow

The runtime control flow is outside this file. During the perf build or packaging process, pmu-events tooling parses this JSON, validates the schema, and compiles the event records into perf's event map data. At runtime, perf resolves a user-provided event name to the generated record, chooses the uncore PMU instance matching `Unit`, programs `EventCode` and `UMask` into an allowed `Counter`, and formats the description in list/help output.

Measurement flow for the UPI link families is hardware-driven. Rx flit events count receive-path slots and packet types; RxQ events separate fast-path bypass from buffer allocation and occupancy; CRC and LLR events identify physical/link reliability and replay behavior; credit events expose virtual-network flow-control pressure. Tx events mirror the transmit direction and add link-power state residency for L0 and L0p, including the cost of lower-power operation on bandwidth and latency.

The basic-header match families encode a configurable match model in the `UMask`: message class, optional opcode match enable, local/remote selection, data versus non-data header selection, dual-slot versus single-slot header selection, and exclusion of link-layer control/null/LLCRD traffic. These rows are predefined aliases for common classes rather than procedural match code.

UBOX event flow is package-level and message-channel oriented. Message events count received interrupt/message categories; M2U miscellaneous events expose queue occupancy and credit overflow conditions between mesh/UPI/CBO paths and UBOX; RACU events track register-access and DRNG-related request state.

## State and Persistence Behavior

This JSON file stores persistent event metadata in the source tree. It does not store measured counter values, maintain runtime state, or mutate hardware.

The state represented by these events lives in processor uncore PMU counters while a perf session is active. UPI counters are per package and per UPI PMU instance, with legal programmable counters listed as `0,1,2,3`. UBOX events are per package and generally use counters `0,1`, except `UNC_U_CLOCKTICKS`, which uses the fixed counter. Counter values are reset, enabled, read, multiplexed, and scaled by perf and the kernel PMU driver, not by this JSON table.

Several event families are intended to be combined analytically. For example, RxQ/TxQ allocation and occupancy events can estimate average queue lifetime or average occupancy; bypass events can be compared against flit counts to detect queueing; CRC errors can be compared with LLR requests; L0/L0p cycle counts can be related to flit throughput and latency-sensitive workloads.

## Dependencies and Integration Points

The file depends on perf's pmu-events JSON schema and on Intel Ice Lake Xeon uncore PMU naming and event encodings. The exact `EventCode`, `UMask`, counter-slot, and unit values must match the CPU model's PMU specification and Linux uncore PMU driver behavior.

Integration points include:

- `tools/perf/pmu-events` generation scripts, which parse this JSON and build perf's event tables.
- `perf list`, which surfaces `BriefDescription`, `PublicDescription`, `Unit`, and `Experimental` status.
- `perf stat` and related event selection paths, which resolve these aliases to hardware encodings.
- Linux x86 uncore PMU support for Ice Lake Xeon UPI and UBOX units, including sysfs PMU names, event format files, counter constraints, package scoping, and fixed-counter handling.
- Intel UPI and UBOX hardware semantics for flits, slots, virtual networks, link-layer retry, L0/L0p power states, non-coherent classes, message routing, and RACU/DRNG activity.

Although this source tree is under a Ceph client mirror, this path is part of the vendored Linux perf tooling. Ceph runtime code does not directly call into these records.

## Risks and Edge Cases

- The chunk begins mid-object for `UNC_UPI_RxL_BASIC_HDR_MATCH.WB_OPC`; the event name and trailing fields are present here, while the opening brace belongs to the preceding lines. Reconciliation should join adjacent chunks before producing a whole-file report.
- Event-code or UMask drift can silently make a named perf event count the wrong hardware condition. This is especially risky for dense match families where related names differ by only one bit or suffix.
- Many events are marked `Experimental`; downstream tests and documentation should avoid treating their descriptions as a stable architectural contract.
- Some records intentionally lack `PublicDescription`, leaving only the brief event name. Generated docs and user-facing help may be sparse for `SLOT_BYPASS`, `TxL0P_CLK_ACTIVE`, some UBOX miscellaneous subevents, and DRNG subevents.
- `PerPkg` accounting can be misread as per-core or per-process accounting. These uncore counters measure package/link-level activity and often reflect all traffic on the socket.
- UPI link power states are directional and per link. A Tx-side L0/L0p event does not necessarily describe Rx-side residency or another UPI link.
- Flit-count events use slot masks and type masks. Data flits consume all slots, but the counted amount can depend on which slot bits are enabled; naive ratios can be wrong if slot and type masks are mixed inconsistently.
- Queue occupancy events accumulate queue depth over cycles, not a simple packet count. They need a divisor such as cycles-not-empty, inserts, or clockticks depending on the intended average.
- CRC and LLR events are reliability indicators but are not one-to-one: multiple CRC detections can be coalesced before a request/ack sequence completes.
- The UBOX fixed counter event uses `Counter: FIXED`, unlike the programmable UBOX events. Tooling must preserve that distinction.

## Test Signals

Useful validation signals for this chunk include:

- JSON syntax validation for the full `uncore-interconnect.json` file after adjacent chunks are considered.
- pmu-events generation coverage that compiles this file into perf's event tables without schema errors.
- `perf list` checks on an Ice Lake Xeon-capable perf build showing representative aliases from this chunk, including `UNC_UPI_RxL_FLITS.ALL_DATA`, `UNC_UPI_TxL_BASIC_HDR_MATCH.REQ`, `UNC_UPI_TxL0P_POWER_CYCLES`, `UNC_UPI_TxL_OCCUPANCY`, `UNC_U_CLOCKTICKS`, and `UNC_U_EVENT_MSG.MSI_RCVD`.
- Event encoding checks that generated tables preserve each `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `Experimental` field.
- Hardware smoke tests on Ice Lake Xeon systems using UPI traffic or NUMA workloads to confirm nonzero UPI flit, bypass, insert, occupancy, and L0/L0p counters where expected.
- Error/retry-oriented validation, where available, for `UNC_UPI_RxL_CRC_ERRORS` and `UNC_UPI_RxL_CRC_LLR_REQ_TRANSMIT`, with the expected relationship that LLR request counts are generally less than or equal to CRC detections.
- Ratio sanity checks comparing Rx/Tx flit counts with bypass, insert, and occupancy events to catch swapped masks or unit misregistration.
- UBOX validation using interrupt-heavy workloads for MSI/IPI/message events and lock/split-lock tests for `UNC_U_LOCK_CYCLES`.
- Fixed-counter handling tests for `UNC_U_CLOCKTICKS`, ensuring perf selects the fixed UBOX counter rather than a programmable slot.

## Cross-Chunk Notes

The previous chunk is needed to reconstruct the beginning of the `UNC_UPI_RxL_BASIC_HDR_MATCH.WB_OPC` JSON object. The final line in this chunk closes the whole JSON array, so subsequent source lines are not part of this event table.

The merge lane should keep this document aligned to `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json` and merge it with other chunks for that exact source path before creating any final per-file report.
