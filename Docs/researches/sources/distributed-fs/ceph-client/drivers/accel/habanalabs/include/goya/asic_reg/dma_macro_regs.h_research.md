# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_macro_regs.h

Purpose: auto-generated address map for the Goya DMA macro block, the shared DMA routing/control layer below the individual DMA queue managers and channels.

Important APIs/types/functions: no functions or types. The `mmDMA_MACRO_*` macros cover LBW range hit/mask/base registers (`0x4B0000` onward), HBW range hit and split mask/base arrays, read/write enable and credit registers, `SRAM_BUSY`, and RAZWI valid/id capture registers for LBW and HBW read/write transactions.

Control flow: declarative register map only. Typical driver flow writes range masks/bases and read/write credits during device initialization, enables the macro, then reads `SRAM_BUSY` or RAZWI capture registers during reset/error handling. Field manipulation depends on `dma_macro_masks.h`.

State and persistence: route range, credit, and enable state lives in the DMA macro MMIO block. Diagnostic RAZWI state is hardware-owned. The block base in `goya_blocks.h` is `mmDMA_MACRO_BASE` with max offset `0x15C`; the register offsets in this file match that range.

Dependencies and integration: included by `goya_regs.h`. `goya_coresight.c` lists DMA macro trace, SPMU, CTI, funnel, and bus-monitor bases; `goya_security.c` indirectly relies on correct block protection and routing constants for safe DMA operation.

Risks: the DMA macro is shared, so bad register addresses affect all DMA channels. Mismatched array counts between address and mask headers can leave some routing windows unconfigured. Credit values can cause deadlock/starvation if programmed inconsistently with router and queue-manager limits.

Test signals: device initialization readbacks, DMA transfers through LBW and HBW routes, RAZWI/security tests, DMA macro CoreSight trace and bus-monitor activity, and stress tests that exercise concurrent DMA channels without credit exhaustion.
