# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_sbte0_mstr_if_axuser_regs.h

Purpose: Defines AXUSER attribute register addresses for the `MME_SBTE0_MSTR_IF_AXUSER` DCORE0 master interface. The registers cover high-bandwidth and low-bandwidth ASID, MMU bypass, strong ordering, snoop, write-reduction, QoS, core, reserved, lock/coordination, and override fields at 0x40D1A80-0x40D1ACC.

Important APIs/types/functions: Exports 19 `mmDCORE0_*_AXUSER_*` address macros, including `mmDCORE0_MME_SBTE0_MSTR_IF_AXUSER_HB_ASID` (0x40D1A80), `mmDCORE0_MME_SBTE0_MSTR_IF_AXUSER_HB_MMU_BP` (0x40D1A84), `mmDCORE0_MME_SBTE0_MSTR_IF_AXUSER_HB_STRONG_ORDER` (0x40D1A88), `mmDCORE0_MME_SBTE0_MSTR_IF_AXUSER_HB_NO_SNOOP` (0x40D1A8C), `mmDCORE0_MME_SBTE0_MSTR_IF_AXUSER_HB_WR_REDUCTION` (0x40D1A90), and `mmDCORE0_MME_SBTE0_MSTR_IF_AXUSER_LB_OVRD` (0x40D1ACC). There are no functions or C types.

Control flow: Initialization, security, or firmware setup code writes these registers before the associated engine issues AXI transactions; runtime data movement then carries the programmed AXUSER attributes.

State and persistence behavior: Attribute values are hardware configuration state and persist until reset or reprogramming. The header itself is pure compile-time metadata.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with MMU/security policy, cache/snoop behavior, and engine-specific DMA paths.

Risks: Incorrect ASID, MMU bypass, or strong-order settings can break isolation or memory ordering. Secured and nonsecured variants must not be interchanged.

Test signals: Security allowlist validation, MMU translation tests, protected/unprotected DMA smoke tests, and register readback of AXUSER setup for this interface.
