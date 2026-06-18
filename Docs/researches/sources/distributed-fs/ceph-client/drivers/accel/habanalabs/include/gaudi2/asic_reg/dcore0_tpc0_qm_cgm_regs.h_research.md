# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_cgm_regs.h

Purpose: generated compact register map for the clock-gating manager sub-block of `DCORE0_TPC0_QM`. It exports three macros: `CGM_CFG` at `0x400AD80`, `CGM_STS` at `0x400AD84`, and `CGM_CFG1` at `0x400AD88`.

Important APIs/types/functions: no functions/types. The macro API names CGM configuration and status registers. `gaudi2_masks.h` defines `DCORE0_TPC0_QM_CGM_STS_AGENT_IDLE_MASK` and aliases `CGM_IDLE_MASK` for idle detection.

Control flow: none. Runtime code may write CGM config and poll CGM status when quiescing or power-managing the TPC QM.

State and persistence behavior: hardware clock-gating configuration and status persist in the QM block. Status indicates agent idle state; configuration can influence power and availability.

Dependencies and integration points: included by `gaudi2_regs.h`; status masks are integrated by `gaudi2_masks.h`; security and reset code may rely on this block when gating or checking QM idleness.

Risks: clock-gating mistakes can make the queue manager appear hung or prevent power savings. Polling an incorrect status bit can produce false idle decisions.

Test signals: idle polling tests, power/reset sequencing tests, readback of CGM status under active and idle workloads, and generated mask/address consistency checks.
