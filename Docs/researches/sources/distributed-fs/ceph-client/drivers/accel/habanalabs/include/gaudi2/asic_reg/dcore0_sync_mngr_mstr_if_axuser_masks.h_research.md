# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_mstr_if_axuser_masks.h

Purpose: Provides shift/mask constants for DCORE0 sync-manager AXUSER master-interface fields. It covers read/write ASID, MMU bypass, strong ordering, no-snoop, QoS, core, EMEM page, write-reduction, atomic read, reserved high/low bits, lock, coordinate, and override values.

Important APIs/types/functions: Exports 74 `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_*` field constants, represented by `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_ASID_WR_SHIFT` (0), `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_ASID_WR_MASK` (0x3FF), `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_ASID_RD_SHIFT` (16), `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_ASID_RD_MASK` (0x3FF0000), `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_HB_MMU_BP_WR_SHIFT` (0), and `DCORE0_SYNC_MNGR_MSTR_IF_AXUSER_LB_OVRD_VAL_MASK` (0xFFFFFFFF). There are no functions or types.

Control flow: No flow exists here. Callers combine these masks with `dcore0_sync_mngr_mstr_if_axuser_regs.h` addresses when packing AXUSER configuration writes.

State and persistence behavior: The constants are compile-time only; they control how driver writes mutate the sync-manager master-interface AXUSER hardware state.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. Integration is with sync-manager DMA/notification transactions and Gaudi2 security/MMU policy.

Risks: Incorrect bitfield packing can bypass the MMU, assign the wrong ASID, or set unintended ordering/cache attributes. Reserved-bit masks must remain synchronized with the hardware database.

Test signals: Bitfield encode/decode checks, AXUSER register readback, secured DMA tests, and negative tests for invalid ASID or MMU bypass policy.
