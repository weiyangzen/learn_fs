<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/dw.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/dw.h

## Purpose
Declares the platform-facing interface for Synopsys DesignWare DMA and Intel iDMA32 controllers.

## Important APIs, Types, And Functions
`struct dw_dma_chip` describes controller device, instance id, IRQ, MMIO registers, clock, core private pointer, and platform data. APIs are `dw_dma_probe()`, `dw_dma_remove()`, `idma32_dma_probe()`, and `idma32_dma_remove()`, with stubs returning `-ENODEV` or 0 when the core is disabled.

## Control Flow
Platform glue fills `dw_dma_chip`, maps registers, provides clock/platform data, then calls the probe function. The core populates `chip->dw` and registers DMAengine channels. Remove tears down those resources.

## State And Persistence
State is the chip descriptor, MMIO mapping, clock handle, platform data, and core private `struct dw_dma`. No persistence exists.

## Dependencies And Integration Points
Depends on clocks, devices, DMAengine, and DesignWare platform data. It integrates platform/ACPI/PCI glue with the common DW DMA core.

## Risks And Edge Cases
Missing clock, bad IRQ, or wrong platform data can leave channels nonfunctional. Stub behavior must be handled by glue drivers when the core is not built.

## Test Signals
Build with and without `CONFIG_DW_DMAC_CORE`, probe/remove platform instances, DMAengine channel registration, IRQ handling, clock enable/disable, and iDMA32-specific probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/dw.h -->
