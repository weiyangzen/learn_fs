<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_arc_aux_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_arc_aux_regs.h

## Purpose
`dcore0_edma0_qm_arc_aux_regs.h` is the generated address map for the DCORE0 EDMA0 QMAN ARC auxiliary block, prototype `QMAN_ARC_AUX`. It defines 284 register addresses in the 0x41C8100-0x41C8920 range for ARC run/halt/reset/debug control, address-window setup, context ids, software interrupts, SEI/REI/ECC reporting, termination diagnostics, scratchpads, traffic counters, AXI override attributes, ordering, and engine-access controls.

## Important APIs, types, and functions
The exported API is `mmDCORE0_EDMA0_QM_ARC_AUX_*` constants. Major groups include `RUN_HALT_REQ/ACK`, reset vector and debug mode, cluster/ARC ids, wake event, DCCM system base, CTI mux/status, ARC reset request/status, SRAM/PCIe/CFG/HBM base and offset registers, seven general-purpose base pairs, CBU/LBU cache override registers, 8 context ids and CID offsets, 16 software interrupt registers, IRQ interrupt masks, ARC SEI status/clear/mask/cause/halt masks, ARC REI status/clear/mask, DCCM/I-cache/D-cache ECC address/syndrome registers, LBW terminate diagnostics, scratchpads, CBU/LBU total and inflight counters, AR/AWUSER and cache/prot overrides, ordering masks/addresses, and upper DCCM enable.

## Control flow
This header is address data only. Bring-up code programs address windows and reset vectors, releases or halts the ARC, and configures interrupt masks. Firmware and driver-side debug can use software interrupts and scratchpads for handshakes. Error paths read SEI/REI/ECC and termination diagnostics, clear latched causes, and may halt ARC execution depending on halt-mask configuration.

## State and persistence behavior
The ARC auxiliary bank contains long-lived firmware execution state and debug/error state. Reset vector, base address windows, context ids, interrupt masks, cache/prot/user overrides, and ordering controls persist while the QMAN ARC runs. Scratchpads and counters persist as diagnostic state. ECC and interrupt status are latched until cleared.

## Dependencies and integration points
This register map integrates with EDMA0 QMAN firmware boot, ARC control paths, interrupt/error handling, Gaudi2 address-window setup, and queue-manager recovery. It also connects to CTI/CoreSight-style debug paths and to the main EDMA0 QMAN register block, which may report ARC-related queue errors.

## Risks and edge cases
High-risk areas are ARC halt/reset sequencing, wrong base MSB/LSB setup for SRAM/PCIe/CFG/HBM windows, stale context ids, interrupt-mask mistakes that hide ECC or exception causes, and clearing latched diagnostics before software captures them. Because this header has addresses only, field semantics must come from hardware docs or matching mask headers elsewhere.

## Test signals
Validation includes ARC firmware boot/halt/reset, software interrupt delivery, scratchpad handshake, ECC/SEI/REI injection, LBW termination diagnostics, address-window access tests, and counter behavior showing CBU/LBU traffic drains during idle/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_arc_aux_regs.h -->
