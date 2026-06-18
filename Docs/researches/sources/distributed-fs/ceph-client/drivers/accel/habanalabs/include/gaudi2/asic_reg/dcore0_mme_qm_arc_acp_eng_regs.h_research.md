# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_acp_eng_regs.h

Purpose: Defines DCORE0 MME QM ARC ACP engine registers. The map exposes 64-entry ACP producer, consumer, priority, and mask arrays plus selected-queue, grant-weight/counter, debug count, and debug control registers at 0x40CF000-0x40CF43C.

Important APIs/types/functions: Exports 272 `mmDCORE0_MME_QM_ARC_ACP_ENG_*` address macros, including `mmDCORE0_MME_QM_ARC_ACP_ENG_ACP_PI_REG_0` (0x40CF000), `mmDCORE0_MME_QM_ARC_ACP_ENG_ACP_PI_REG_1` (0x40CF004), `mmDCORE0_MME_QM_ARC_ACP_ENG_ACP_PI_REG_2` (0x40CF008), `mmDCORE0_MME_QM_ARC_ACP_ENG_ACP_PI_REG_3` (0x40CF00C), `mmDCORE0_MME_QM_ARC_ACP_ENG_ACP_PI_REG_4` (0x40CF010), and `mmDCORE0_MME_QM_ARC_ACP_ENG_ACP_DBG_REG` (0x40CF43C). No executable API is present.

Control flow: ARC/QMAN firmware or driver debug paths use these registers to observe or configure ACP queue arbitration and priority behavior.

State and persistence behavior: Register contents are live ACP queue/arbitration state. The header has no state and only binds macro names to addresses.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with MME QM ARC firmware, arbitration diagnostics, and privileged register-region policy.

Risks: The 64-entry arrays must be indexed consistently; off-by-one register selection changes queue priority or mask state. Debug counters may be volatile and require stable sampling.

Test signals: ARC firmware startup, ACP queue traffic tests, priority/weight arbitration tests, debug-counter readback, and security allowlist checks for the 0x40CF000-0x40CF43C window.
