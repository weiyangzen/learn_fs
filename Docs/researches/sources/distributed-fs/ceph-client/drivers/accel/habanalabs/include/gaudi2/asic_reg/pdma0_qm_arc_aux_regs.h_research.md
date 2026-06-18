<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_arc_aux_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_arc_aux_regs.h

## Purpose
`pdma0_qm_arc_aux_regs.h` maps the ARC auxiliary block for the PDMA0 queue-manager ARC. It controls ARC halt/reset/debug, memory-region mapping, software interrupts, ECC/error reporting, DCCM queues, and QMAN interrupt/status interaction.

## Important APIs, types, and functions
The file exports `mmPDMA0_QM_ARC_AUX_*` macros. Important groups are run/halt/reset/debug and identity registers, SRAM/PCIe/CFG/HBM/general-purpose address windows, context ID and CID offset registers, software interrupt registers, IRQ masks, ARC SEI/REI status/clear/mask/halt registers, ECC syndrome/address registers, LBW terminate error captures, DCCM queue push/pop/control/status registers, ARC cache/pipeline controls, and QMAN interrupt mask/status registers.

## Control flow
There is no C flow. PDMA firmware/ARC startup writes reset vector and address windows, releases the ARC, signals via software interrupts, and monitors run/halt acknowledgement. Reset/error flows halt the ARC and read SEI/REI/ECC/termination diagnostics.

## State and persistence
Hardware persists ARC execution state, address mappings, interrupt masks/pending bits, context IDs, ECC records, DCCM queue state, and QMAN interrupt status until reset or reprogramming.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file pairs with PDMA QMAN and core registers. It is structurally parallel to the NIC ARC auxiliary map, allowing shared ARC helper code with per-block bases.

## Risks and test signals
Bad memory-window setup can make PDMA ARC firmware fetch from the wrong address or corrupt memory. Interrupt-mask errors can hide ARC fatal conditions. Test signals include PDMA ARC firmware ready, halt/run handshake completion, software interrupt delivery, no unexpected ECC/SEI/REI status under DMA load, and useful diagnostics on injected ARC faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_arc_aux_regs.h -->
