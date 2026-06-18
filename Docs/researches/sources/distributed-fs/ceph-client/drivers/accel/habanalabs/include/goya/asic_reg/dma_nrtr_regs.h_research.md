# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_nrtr_regs.h

Purpose: auto-generated register-address map for the Goya DMA north router (`DMA_NRTR`). It gives the driver MMIO offsets for DMA mesh arbitration, split policy, range routing, regulators, and scrambling.

Important APIs/types/functions: no functions or types. The `mmDMA_NRTR_*` macros cover HBW/LBW max credits, debug arbitration registers for E/W/N/S/L directions, split coefficient slots 0-9, split config and token/timeout registers, HBW range hit plus 8 split low/high mask/base entries, LBW range hit plus 16 mask/base entries, regulator config/result registers, and scrambling controls.

Control flow: declarative. Driver initialization can program credits, split policies, and range tables; runtime diagnostics can read arbitration and range-hit/status registers. Field layout is defined by `dma_nrtr_masks.h`.

State and persistence: router state is hardware-resident and persists until reset or explicit rewrite. It affects all DMA traffic passing through the DMA north-router block. `goya_blocks.h` maps the containing block at `mmDMA_NRTR_BASE` and max offset `0x608`.

Dependencies and integration: included by `goya_regs.h`. `goya_security.c` calls `goya_pb_set_block(hdev, mmDMA_NRTR_BASE)`, so these offsets participate in the protected-register layout. The structure mirrors router headers for MME/TPC/PCI blocks, enabling common driver logic to reason about mesh routers.

Risks: incorrect offsets can break global DMA routing, cause deadlock via bad credits, or bypass intended range controls. Address range arrays must stay aligned with the mask header widths. Scrambling/regulator controls can have security and data-integrity impact if programmed incorrectly.

Test signals: successful DMA initialization, transfer throughput under concurrent channels, readback of configured routing ranges, forced bad-route or RAZWI scenarios, rate-limit behavior, and protection-bit checks covering the DMA router window.
