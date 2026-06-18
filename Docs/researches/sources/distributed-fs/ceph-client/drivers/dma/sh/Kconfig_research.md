# sources/distributed-fs/ceph-client/drivers/dma/sh/Kconfig

Purpose: Kconfig menu for Renesas/SuperH DMAEngine drivers under `drivers/dma/sh`.

Important APIs/types/functions: symbols include helper `RENESAS_DMA`, base helper `SH_DMAE_BASE`, controller options `SH_DMAE`, `RCAR_DMAC`, `RENESAS_USB_DMAC`, and `RZ_DMAC`. Several select `DMA_VIRTUAL_CHANNELS` or `RENESAS_DMA`.

Control flow: enabling architecture-appropriate options controls which objects in the adjacent Makefile are built. `SH_DMAE_BASE` gates legacy SuperH DMA support and enforces dependencies on `SUPERH`, `SH_DMA`, and `SH_DMA_API`. R-Car, USB DMAC, and RZ DMAC are available on `ARCH_RENESAS` or compile-test.

State/persistence: no runtime state; build-time configuration only.

Dependencies/integration: integrates Renesas DMA drivers with DMAEngine and architecture config symbols.

Risks: dependency expressions around SuperH legacy APIs are subtle; relaxing them could create conflicting DMA APIs. Some options select only `RENESAS_DMA`, while USB/RZ also select virtual channels according to their implementation needs.

Test signals: randconfig for `SUPERH`, `ARCH_RENESAS`, and `COMPILE_TEST`; verify each enabled symbol builds the intended object and selects DMAEngine support.
