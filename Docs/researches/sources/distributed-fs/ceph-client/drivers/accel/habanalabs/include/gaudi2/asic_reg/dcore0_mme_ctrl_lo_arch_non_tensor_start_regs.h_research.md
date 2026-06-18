# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_non_tensor_start_regs.h

Purpose: Provides the opening non-tensor descriptor registers for DCORE0 MME low-control architecture programming. The block covers brains/header low/high words and EUS master/slave controls at 0x40CB028-0x40CB03C.

Important APIs/types/functions: Exports six `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_*` address macros including `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_BRAINS_LOW` (0x40CB028), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_BRAINS_HIGH` (0x40CB02C), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_HEADER_LOW` (0x40CB030), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_HEADER_HIGH` (0x40CB034), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_EUS_MASTER` (0x40CB038), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_START_EUS_SLAVE` (0x40CB03C). No code or types are defined.

Control flow: Firmware or driver descriptor assembly writes these registers before the detailed tensor and non-tensor end fields to seed MME command metadata.

State and persistence behavior: No software state is held. Register contents are device configuration state for the current MME work descriptor and are overwritten by later work or reset.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It complements `dcore0_mme_ctrl_lo_arch_non_tensor_end_regs.h` and the main `dcore0_mme_ctrl_lo_regs.h` command/status block.

Risks: Header/brains fields are opaque hardware contract words; incorrect bit packing in callers can make a descriptor invalid even though the macro address is correct.

Test signals: Validate generated descriptor images against firmware/hardware specs, read back the start registers after programming, and run MME smoke tests that exercise both EUS master and slave paths.
