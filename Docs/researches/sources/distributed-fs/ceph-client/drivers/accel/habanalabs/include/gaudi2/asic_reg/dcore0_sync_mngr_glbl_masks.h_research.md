# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_glbl_masks.h

Purpose: Provides shift/mask constants for DCORE0 sync-manager global registers. It covers SEI overflow/unaligned/response-error fields, L2H masks, ASID/MMU-bypass controls, LBW delay and address/data fields, CQ base/size/PI/security/interrupt/inc-mode fields, and SOB-only enable.

Important APIs/types/functions: Exports 66 `DCORE0_SYNC_MNGR_GLBL_*` bitfield constants, represented by `DCORE0_SYNC_MNGR_GLBL_SM_SEI_MASK_SO_OVERFLOW_SHIFT` (0), `DCORE0_SYNC_MNGR_GLBL_SM_SEI_MASK_SO_OVERFLOW_MASK` (0x1), `DCORE0_SYNC_MNGR_GLBL_SM_SEI_MASK_MST_UNALIGN4B_SHIFT` (1), `DCORE0_SYNC_MNGR_GLBL_SM_SEI_MASK_MST_UNALIGN4B_MASK` (0x2), `DCORE0_SYNC_MNGR_GLBL_SM_SEI_MASK_MST_RSP_ERR_SHIFT` (2), and `DCORE0_SYNC_MNGR_GLBL_CQ_INC_MODE_MODE_MASK` (0x1). No executable code exists.

Control flow: Callers use these masks to pack writes and decode reads for the companion global sync-manager address header.

State and persistence behavior: The constants are compile-time metadata; they govern how software mutates or interprets live sync-manager register state.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. They pair with global sync-manager registers and queue/interrupt setup code.

Risks: Incorrect masks can break completion queues, interrupt routing, or security attributes. SEI cause fields should be cleared according to hardware semantics, not by arbitrary full-register writes.

Test signals: Bitfield encode/decode checks, CQ setup/readback, interrupt mask tests, SEI fault injection, and ASID/MMU-bypass validation.
