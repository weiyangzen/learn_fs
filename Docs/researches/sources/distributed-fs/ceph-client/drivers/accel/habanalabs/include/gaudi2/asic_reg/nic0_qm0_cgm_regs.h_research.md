<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm0_cgm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm0_cgm_regs.h

## Purpose
`nic0_qm0_cgm_regs.h` defines the tiny clock-gating management register block for NIC0 queue manager 0. It is an auto-generated address catalog for the QMAN clock-gating unit.

## Important APIs, types, and functions
The file exports `mmNIC0_QM0_CGM_CFG`, `mmNIC0_QM0_CGM_STS`, and `mmNIC0_QM0_CGM_CFG1`. There are no C types or functions.

## Control flow
No code executes here. Gaudi2 initialization or power-management code can write the CFG registers to enable, disable, or tune clock gating and read STS to confirm the queue-manager clock-gating state. Replicated NIC queue-manager code should combine these base addresses with `NIC_QM_OFFSET`/`NIC_OFFSET` style calculations from `gaudi2_regs.h` when programming other NIC instances.

## State and persistence
The persistent state is hardware register state: clock-gating configuration and status for NIC0 QM0. The driver does not persist values in this header; it relies on reset-time programming and hardware retention rules.

## Dependencies and integration points
This header is included through `gaudi2_regs.h` and pairs with the larger `nic0_qm0_regs.h` QMAN map. It integrates with NIC bring-up, queue-manager power gating, reset quiesce checks, and any low-power handling that must avoid gating active queues.

## Risks and test signals
Wrong clock-gating addresses can leave the NIC QM stuck gated, ungated, or reporting false idle. Tests should exercise NIC queue submission after reset and low-power transitions, and should check that CGM status agrees with driver idle/active expectations before and after queue-manager reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm0_cgm_regs.h -->
