# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/goya_masks.h

Purpose: hand-maintained aggregate mask header for Goya register programming. It builds convenient multi-bit constants for queue-manager enable/stop/error/protection, reset control, interrupt decoding, idle checks, and a few cross-instance aliases.

Important APIs/types/functions: no functions or types. Key macros include `QMAN_DMA_ENABLE`, `QMAN_DMA_FULLY_TRUSTED`, `QMAN_DMA_PARTLY_TRUSTED`, `QMAN_DMA_STOP`, `QMAN_DMA_IS_STOPPED`, `QMAN_DMA_ERR_MSG_EN`, equivalent MME/TPC QMAN and CMDQ enable/stop/error/protection masks, reset masks (`DMA_MME_TPC_RESET`, `RESET_ALL`, `CA53_RESET`, CPU reset assert/deassert masks), HBW/LBW interrupt ID decoding masks and shifts, idle masks (`DMA_QM_IDLE_MASK`, `TPC_QM_IDLE_MASK`, `TPC_CMDQ_IDLE_MASK`, `TPC_CFG_IDLE_MASK`, `MME_QM_IDLE_MASK`, `MME_CMDQ_IDLE_MASK`, `MME_ARCH_IDLE_MASK`, `MME_SHADOW_IDLE_MASK`), TPC stall aliases, DMA QMAN stop-shift aliases for instances 1-4, and PSOC ETR AXI control masks.

Control flow: no executable flow, but these macros encode control decisions used by driver flows: enable engines, stop/flush engines, configure trusted/protected behavior, enable error messages/stop-on-error, assert resets, decode interrupts, and poll idleness before reset or power transitions.

State and persistence: the macros are compile-time constants. They affect persistent hardware state when written into Goya MMIO registers by the driver. Idle and interrupt masks decode live status/error words.

Dependencies and integration: includes `goya_regs.h`, which pulls in all needed register and bitfield headers. Included by `goya.c` and `goya_coresight.c`; it centralizes bit combinations so device initialization and teardown code do not repeat long shift expressions.

Risks: unlike the generated address headers, this file composes behavior. Missing a stop/error/protection bit can leave a hardware subunit active, unprotected, or silent on fault. Over-broad reset masks can reset more of the chip than intended. Aggregate masks based on instance-0 bitfields assume identical layouts across cloned queue managers.

Test signals: device bring-up and teardown, stop/idle polling before reset, reset sequencing, interrupt decode correctness, error injection that checks stop-on-error and message generation, and secure/non-secure access tests for trusted/partly trusted DMA modes.
