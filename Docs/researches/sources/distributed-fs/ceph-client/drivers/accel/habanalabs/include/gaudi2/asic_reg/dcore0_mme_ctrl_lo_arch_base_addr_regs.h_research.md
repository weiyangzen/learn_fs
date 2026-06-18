# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_base_addr_regs.h

Purpose: Defines the DCORE0 MME low-control base-address descriptor registers for the MME address descriptor prototype. It maps low/high address pairs for COUT1, COUT0, tensor A, and tensor B at 0x40CB008-0x40CB024.

Important APIs/types/functions: The public surface is eight `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_*` macros: `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_COUT1_LOW` (0x40CB008), `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_COUT1_HIGH` (0x40CB00C), `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_COUT0_LOW` (0x40CB010), `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_COUT0_HIGH` (0x40CB014), `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_A_LOW` (0x40CB018), and `mmDCORE0_MME_CTRL_LO_ARCH_BASE_ADDR_B_HIGH` (0x40CB024). There are no structs, functions, or inline helpers.

Control flow: MME setup code writes these base address registers before tensor dimension, stride, and AGU offset registers are consumed by the hardware launch path.

State and persistence behavior: The header is stateless. Programmed register values represent device-local descriptor state and persist until the MME control block is reset or reprogrammed.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates directly with tensor A/B/COUT descriptor and AGU offset headers.

Risks: Low/high register ordering and COUT0/COUT1 selection are correctness-critical for 64-bit device addresses. Stale base addresses can cause DMA to the wrong memory region.

Test signals: Descriptor programming tests should validate 64-bit address split/merge, COUT0/COUT1 selection, and register dump comparison for the 0x40CB008-0x40CB024 descriptor area.
