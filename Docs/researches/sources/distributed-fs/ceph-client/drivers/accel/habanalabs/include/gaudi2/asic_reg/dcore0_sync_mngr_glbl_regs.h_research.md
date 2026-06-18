# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_glbl_regs.h

Purpose: Defines DCORE0 sync-manager global SOB registers. The map covers SEI mask/cause, L2H completion masks, ASID/security controls, LBW delay, producer-index sizing, CQ interrupt controls, 64 completion-queue base/size/PI/security/inc-mode entries, and 64 LBW address/data entries at 0x411E000-0x411E94C.

Important APIs/types/functions: Exports 590 `mmDCORE0_SYNC_MNGR_GLBL_*` address macros. Large repeated families include 64 CQ base-low/high, size, PI, security, increment-mode, and LBW address/data registers; representative macros are `mmDCORE0_SYNC_MNGR_GLBL_SM_SEI_MASK` (0x411E000), `mmDCORE0_SYNC_MNGR_GLBL_SM_SEI_CAUSE` (0x411E004), `mmDCORE0_SYNC_MNGR_GLBL_L2H_CPMR_L` (0x411E008), `mmDCORE0_SYNC_MNGR_GLBL_L2H_CPMR_H` (0x411E00C), `mmDCORE0_SYNC_MNGR_GLBL_L2H_MASK_L` (0x411E020), and `mmDCORE0_SYNC_MNGR_GLBL_CQ_INC_MODE_63` (0x411E94C).

Control flow: Driver setup configures sync-manager queues, security attributes, and interrupt masks; runtime synchronization objects and monitors drive CQ/LBW updates that software or firmware consumes.

State and persistence behavior: The header is stateless, while the registers hold live synchronization, CQ, interrupt, and LBW transaction state. Values persist until reset, queue teardown, or explicit reconfiguration.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with sync-object/monitor object masks, command-completion queues, host interrupts, and security ASID policy.

Risks: Queue base/PI/size mistakes break completion delivery. Security and MMU-bypass fields affect isolation, and LBW address/data registers can generate unintended transactions if misprogrammed.

Test signals: Sync-manager queue setup, SOB/monitor completion tests, CQ interrupt delivery, ASID/security negative tests, LBW write/readback validation, and register dump decode for all 64 queue slots.
