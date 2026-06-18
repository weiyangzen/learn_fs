<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm_arc_aux0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm_arc_aux0_regs.h

## Purpose
`nic0_qm_arc_aux0_regs.h` defines the ARC auxiliary register block attached to the NIC0 queue-manager ARC. It covers ARC halt/reset/debug control, address-region configuration, context IDs, software interrupts, ECC status, termination errors, cache/pipeline controls, DCCM queue access, and QMAN/ARC interrupt plumbing.

## Important APIs, types, and functions
The file exports `mmNIC0_QM_ARC_AUX0_*` macros only. Key groups are run/halt/reset registers (`RUN_HALT_REQ`, `RUN_HALT_ACK`, `RST_VEC_ADDR`, `ARC_RST*`), ARC identity/debug registers, SRAM/PCIe/CFG/HBM and general-purpose address windows, context ID and CID offset registers, `SW_INTR_*`, IRQ masks, SEI/REI status/clear/mask/halt controls, ECC syndrome/address registers for DCCM/I-cache/D-cache, LBW termination diagnostics, DCCM queue push/pop/control registers, and QMAN-related interrupt masks/status.

## Control flow
There is no C control flow. Firmware bring-up and reset flows write reset vectors and memory windows, release or halt the ARC, wait for halt acknowledgements, configure region access, and use software interrupts for host-to-ARC signaling. Error paths read SEI/REI/ECC/termination status and may halt the ARC depending on mask configuration.

## State and persistence
Hardware state includes ARC execution state, configured address windows, context IDs, interrupt masks, outstanding software interrupt bits, ECC records, and DCCM queue contents. These values are reset-sensitive and must be reprogrammed after ARC or device reset.

## Dependencies and integration points
The header is included by `gaudi2_regs.h` and works with `nic0_qm0_regs.h` for the queue-manager datapath. It is structurally similar to `pdma0_qm_arc_aux_regs.h`, enabling common ARC auxiliary handling with per-block bases. Consumers include firmware load/start, reset, queue-manager diagnostics, event collection, and security configuration.

## Risks and test signals
Bad ARC auxiliary addresses can prevent NIC firmware from starting or can route ARC memory accesses to the wrong SRAM/HBM/PCIe window. Interrupt-mask mistakes may hide fatal ARC errors or halt on benign events. Test signals include ARC halt/run handshakes completing, firmware reaching expected ready state, software interrupts being observed, no unexpected SEI/REI/ECC status after traffic, and correct error capture when injecting ARC/DCCM faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm_arc_aux0_regs.h -->
