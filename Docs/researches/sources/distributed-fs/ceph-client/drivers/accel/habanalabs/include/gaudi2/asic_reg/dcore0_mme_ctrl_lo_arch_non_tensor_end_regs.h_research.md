# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_arch_non_tensor_end_regs.h

Purpose: Defines the closing non-tensor descriptor register addresses for DCORE0 MME low-control programming. It covers convolution metadata, loop/iteration fields, padding values, signal masks, store/rounding controls, activation enables, rates, and work-load id at 0x40CB280-0x40CB2DC.

Important APIs/types/functions: Exports 24 `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_*` macros, represented by `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_CONV_KERNEL_SIZE_MINUS_1` (0x40CB280), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_CONV_LOW` (0x40CB284), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_CONV_HIGH` (0x40CB288), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_OUTER_LOOP` (0x40CB28C), `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_NUM_ITERATIONS_MINUS_1` (0x40CB290), and `mmDCORE0_MME_CTRL_LO_ARCH_NON_TENSOR_END_WKL_ID` (0x40CB2DC). There are no functions or data structures.

Control flow: MME descriptor code writes these fields after base, tensor, and non-tensor-start words and before issuing `mmDCORE0_MME_CTRL_LO_CMD`.

State and persistence behavior: The header is compile-time metadata only. Hardware register state controls the next or current MME operation until reprogramming or reset.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. The fields tie MME computation semantics to sync objects and output storage behavior.

Risks: Off-by-one fields such as kernel size and iterations are named as minus-one values, so caller-side encoding errors can silently change shape. Signal mask and store enable fields affect completion behavior and output visibility.

Test signals: Convolution and GEMM descriptor tests should cover padding, rounding, activation, store-enable, work-load-id, signal-mask, and iteration edge cases with register readback.
