# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_tensor_b_regs.h

Purpose: Defines the DCORE0 MME tensor B descriptor register addresses for tensor geometry and addressing. The block spans valid-elements, loop stride, ROI size, spatial stride, and start-offset fields at 0x40CB098-0x40CB0EC.

Important APIs/types/functions: Exports 22 `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_*` macros, including `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_VALID_ELEMENTS_0` (0x40CB098), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_VALID_ELEMENTS_1` (0x40CB09C), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_VALID_ELEMENTS_2` (0x40CB0A0), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_VALID_ELEMENTS_3` (0x40CB0A4), `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_VALID_ELEMENTS_4` (0x40CB0A8), and `mmDCORE0_MME_CTRL_LO_ARCH_TENSOR_B_START_OFFSET_3` (0x40CB0EC). No executable APIs are present.

Control flow: Descriptor construction writes tensor shape and stride registers before AGU and command launch logic uses them to generate memory transactions.

State and persistence behavior: Software state is absent; programmed values are hardware descriptor state for tensor B and remain until reset or reprogramming.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. Tensor B registers combine with base-address and AGU ROI-offset registers to define actual memory access patterns.

Risks: Tensor A, B, and COUT layouts are structurally similar but occupy different address windows; mixing them causes incorrect reads or output placement. Dimensional fields have fixed register counts, so caller loops must match the hardware-supported rank.

Test signals: Shape/stride unit tests, descriptor dump validation, and MME execution tests with nontrivial ROI sizes and start offsets are the main signals.
