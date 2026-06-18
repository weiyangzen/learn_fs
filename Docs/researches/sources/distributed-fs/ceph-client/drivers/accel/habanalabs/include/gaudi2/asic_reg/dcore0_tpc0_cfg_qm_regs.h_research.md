# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_qm_regs.h

Purpose: generated register map for the queue-manager-facing TPC kernel configuration region in `DCORE0_TPC0_CFG`. It exports 53 `mmDCORE0_TPC0_CFG_QM_*` address constants from `0x400BAE4` to `0x400BBB4`.

Important APIs/types/functions: macro-only API for QM kernel base address low/high, TID base/size per dimension, tensor ID, kernel configuration, coefficient sections, and base-size high/low registers. The layout mirrors the non-QM kernel configuration header with a separate address window.

Control flow: none. Driver code or firmware-facing setup paths program these registers when a queue manager drives TPC kernel execution state.

State and persistence behavior: represents MMIO-backed queue-manager kernel launch state. Programmed values persist until reconfigured/reset and affect the command processor or QM path's view of kernel address and thread geometry.

Dependencies and integration points: included by `gaudi2_regs.h`; tightly related to `dcore0_tpc0_cfg_qm_tensor_0_regs.h`, `dcore0_tpc0_cfg_qm_sync_object_regs.h`, and `dcore0_tpc0_qm_regs.h`. It integrates with security tables that expose or restrict selected QM ranges.

Risks: duplicated kernel-layout names with a QM prefix create copy/paste risk between `CFG_KERNEL` and `CFG_QM` spaces. Address mistakes could route setup through the wrong launch path. 64-bit addresses split across low/high macros require ordering discipline.

Test signals: compare against non-QM kernel register spacing where expected; hardware queue submission tests that program TPC kernels via QM; register readback on Gaudi2 after command submission; generated-register diff review.
