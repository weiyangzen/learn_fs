<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_cgm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_cgm_regs.h

## Purpose
`pdma0_qm_cgm_regs.h` defines the PDMA0 queue-manager clock-gating management register block.

## Important APIs, types, and functions
The file exports `mmPDMA0_QM_CGM_CFG`, `mmPDMA0_QM_CGM_STS`, and `mmPDMA0_QM_CGM_CFG1`. There are no types or functions.

## Control flow
The header has no executable control flow. Power or reset code writes the CGM configuration registers and reads status to confirm whether the PDMA0 QMAN clock-gating state is compatible with queue activity, reset, or low-power entry.

## State and persistence
Hardware persists CGM configuration and status until reset or reprogramming. Incorrect state can affect the QMAN even though the PDMA core registers are otherwise correctly configured.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this block complements PDMA QMAN, ARC auxiliary, AXUSER, and core maps. It is part of PDMA bring-up, idle, reset, and power-management sequencing.

## Risks and test signals
Clock gating at the wrong time can wedge command processing or hide idle state. Test signals include PDMA queue submission before and after low-power transitions, CGM status matching expected active/idle state, and reset flows that do not time out waiting for the QMAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_cgm_regs.h -->
