# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_values.h

## Purpose

`t4_values.h` defines named hardware values for modal register fields in the Chelsio T4-family driver. Unlike `t4_regs.h`, which mostly defines register addresses and bit positions, this file names the concrete encoded values that callers write into those fields, especially for SGE behavior, congestion-manager modes, BAR2 user doorbell layout, mailbox owners, PCIe window shifts, and filter tuple composition.

## Important APIs, Types, and Constants

- SGE `CONTROL1`/`CONTROL2` values define RX packet CPL split mode, ingress PCIe/padding/packing boundary shifts and encodings, T6-specific padding encodings, GTS timer/counter registers, fetch burst min/max encodings, host flow-control modes, CIDX flush thresholds, update delivery mode, and response descriptor type values.
- Congestion manager helpers define context bit positions and values for channel- or queue-based congestion modes: `CONMCTXT_CNGTPMODE_*`, `CONMCTXT_CNGCHMAP_*`, `CONMCTXT_CNGTPMODE_CHANNEL_X`, and `CONMCTXT_CNGTPMODE_QUEUE_X`.
- BAR2/user doorbell layout constants define `SGE_UDB_SIZE`, kernel/simple doorbell offset `SGE_UDB_KDOORBELL`, GTS offset `SGE_UDB_GTS`, and write-combining doorbell offset `SGE_UDB_WCDOORBELL`.
- CIM mailbox owner constants include `X_MBOWNER_FW` and `X_MBOWNER_PL`.
- PCIe helper shifts define `WINDOW_SHIFT_X` and `PCIEOFST_SHIFT_X`.
- Compressed filter tuple widths define optional fields for FCoE, port, VNIC ID, VLAN, TOS, protocol, EtherType, MAC match, MPS hit type, and fragmentation.
- Filter tuple subfield helpers define VLAN-valid, VNID VF/PF ID, and VNID valid fields.

## Control Flow and State Behavior

This header has no executable control flow. It is used by initialization and configuration paths that choose encoded register values before writing registers from `t4_regs.h`. For example, SGE initialization selects ingress padding/packing boundaries, fetch burst sizes, host flow-control behavior, response types, and interrupt delivery modes. BAR2 doorbell setup uses the user-doorbell offsets to choose between simple doorbells, GTS writes, and write-combining doorbell buffers.

The state affected by these values lives in adapter registers, queue contexts, and filter configuration registers. The header owns no local state and performs no persistence.

## Dependencies and Integration Points

- Pure macro header with no includes.
- Integrates directly with `t4_regs.h` register fields such as SGE control, GTS, host flow-control, doorbell, PCIe window, CIM mailbox owner, TP VLAN priority map, and filter tuple configuration.
- Complements `t4_hw.h` SGE mode constants and `t4_msg.h` response/CPL type definitions.
- Used by filter-building code to calculate compressed filter tuple widths and set validity/subfield bits.

## Risks and Edge Cases

- These constants are encoded hardware values, not arbitrary software enums. Confusing `_X` encoded values with shifts or raw byte counts can program the wrong mode.
- T6 changes several SGE encodings (`T6_INGPADBOUNDARY_*`, `FETCHBURSTMIN_*_T6_X`); callers must choose values based on chip generation.
- BAR2 doorbell offsets are chosen to avoid undesirable write combining. Moving them or using the wrong offset can affect queue notification correctness and performance.
- Filter tuple width constants must stay synchronized with `TP_VLAN_PRI_MAP` semantics and tuple-building code; mismatches can shift later fields and break filter matching.
- `_V(x)` helpers here generally do not mask inputs, so callers must only pass bounded values.

## Test Signals

- Build coverage verifies macro availability and spelling.
- Queue initialization and high-rate TX/RX tests validate SGE modal values, burst settings, doorbell offsets, and response type expectations.
- T5/T6 adapter tests validate generation-specific padding and fetch-burst choices.
- Filter insertion/match tests validate compressed tuple widths and VLAN/VNIC subfield packing.
- Firmware mailbox tests validate owner values used with CIM mailbox control fields.
