<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_cgm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_cgm_regs.h

## Purpose
`dcore0_edma0_qm_cgm_regs.h` is the generated address map for the DCORE0 EDMA0 QMAN clock-gating manager, prototype `QMAN_CGM`. It defines `CFG`, `STS`, and `CFG1` register addresses in the 0x41CAD80-0x41CAD88 range.

## Important APIs, types, and functions
The file exports only `mmDCORE0_EDMA0_QM_CGM_CFG`, `mmDCORE0_EDMA0_QM_CGM_STS`, and `mmDCORE0_EDMA0_QM_CGM_CFG1`. These are the QMAN clock-gating control and status entry points; field masks are not present in this file.

## Control flow
Initialization or power-management code writes configuration before or after QMAN enable according to the hardware sequence and can read `STS` for state. Recovery code should return the CGM state to known defaults before restarting the EDMA0 QMAN.

## State and persistence behavior
The registers hold persistent clock/power configuration and live status. Bad state can manifest as QMAN idleness, missed progress, or reset timeouts rather than obvious register-access failure.

## Dependencies and integration points
This file integrates with the EDMA0 QMAN register block, ARC auxiliary block, and any common Gaudi2 `QMAN_CGM` programming helper. Its address base must remain aligned with generated DCORE0 EDMA0 block placement.

## Risks and edge cases
The primary risk is writing undocumented magic values or sequencing clock gating while queue pipes are active. Since the header lacks masks, consumers need external field definitions and must avoid assuming KDMA and EDMA CGM values are always interchangeable.

## Test signals
Tests should cover boot, reset, idle-to-active transitions, queue traffic with clock gating enabled, and status readbacks during power-management transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_cgm_regs.h -->
