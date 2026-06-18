# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_cgm_regs.h

Purpose: Defines the tiny DCORE0 MME QMAN clock-gating/control-management register block. It exposes CGM configuration, status, and secondary configuration addresses at 0x40CAD80-0x40CAD88.

Important APIs/types/functions: The exported API is three address macros: `mmDCORE0_MME_QM_CGM_CFG` (0x40CAD80), `mmDCORE0_MME_QM_CGM_STS` (0x40CAD84), `mmDCORE0_MME_QM_CGM_CFG1` (0x40CAD88). No functions or types are defined.

Control flow: Power-management or bring-up code writes CGM config, observes status, and may adjust the second config register as part of QMAN clock gating.

State and persistence behavior: The header has no state. CGM registers hold hardware power/clock-gating state until reset or a later write.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with QMAN power management and diagnostics.

Risks: Bad CGM programming can gate clocks while QMAN is active or leave clocks ungated. Status sampling must account for hardware transition latency.

Test signals: Clock-gating enable/disable tests, QMAN activity across low-power transitions, and register readback for config/status consistency.
