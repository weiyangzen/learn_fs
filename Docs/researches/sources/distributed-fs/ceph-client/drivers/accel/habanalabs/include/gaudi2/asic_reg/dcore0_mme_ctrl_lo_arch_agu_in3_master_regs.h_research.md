# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_agu_in3_master_regs.h

Purpose: Auto-generated Gaudi2 DCORE0 MME low-control AGU register map for the IN3 master address-generation core. It exposes five ROI base-offset MMIO addresses for the `MME_AGU_CORE` prototype at 0x40CB1D4-0x40CB1E4.

Important APIs/types/functions: There are no C functions or types. The exported API is the macro family `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_MASTER_ROI_BASE_OFFSET_0` (0x40CB1D4), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_MASTER_ROI_BASE_OFFSET_1` (0x40CB1D8), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_MASTER_ROI_BASE_OFFSET_2` (0x40CB1DC), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_MASTER_ROI_BASE_OFFSET_3` (0x40CB1E0), `mmDCORE0_MME_CTRL_LO_ARCH_AGU_IN3_MASTER_ROI_BASE_OFFSET_4` (0x40CB1E4), one register per ROI base-offset slot 0 through 4.

Control flow: No executable control flow exists in this header. Runtime flow is created by MME descriptor programming code that writes these offsets while configuring tensor or output regions before launching MME work.

State and persistence behavior: The file stores no runtime state; the macros name persistent hardware registers in DCORE0. Values written to these registers live in the device until reset or later driver/firmware programming overwrites them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These AGU offsets pair with the tensor/base-address descriptor headers in the same `dcore0_mme_ctrl_lo_arch_*` block.

Risks: The master/slave and input/output variants are adjacent and easy to confuse; writing the wrong ROI offset can redirect tensor reads or COUT writes. Because the file is generated, manual edits would drift from the hardware database.

Test signals: Build coverage catches missing macro names. Hardware or simulator tests should program MME descriptors using this IN3 master lane, verify expected tensor addressing, and compare register dumps against the 0x40CB1D4-0x40CB1E4 address window.
