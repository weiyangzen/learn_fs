<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/mediatek/Kconfig

## Purpose
Defines the MediaTek DMAEngine configuration options for High-Speed DMA, Command-Queue DMA, and UART APDMA drivers.

## Important APIs, Types, And Functions
The file declares `CONFIG_MTK_HSDMA`, `CONFIG_MTK_CQDMA`, and `CONFIG_MTK_UART_APDMA`. HSDMA and CQDMA depend on `ARCH_MEDIATEK || COMPILE_TEST`, select `DMA_ENGINE` and `DMA_VIRTUAL_CHANNELS`, and CQDMA additionally selects `ASYNC_TX_ENABLE_CHANNEL_SWITCH`. UART APDMA depends on device tree support and `SERIAL_8250_MT6577` and selects DMAEngine plus virtual channels.

## Control Flow
There is no runtime control flow. Kconfig selection controls whether the matching object files in the directory build and whether common DMAEngine/virtual-channel support is pulled into the kernel configuration.

## State And Persistence
Configuration state is persisted in the kernel `.config`. No runtime state exists in this file.

## Dependencies And Integration Points
Integrates MediaTek DMA drivers with the kernel Kconfig dependency graph, the 8250 MediaTek UART driver, and compile-test coverage for non-MediaTek builds. The selected symbols are consumed by the directory Makefile.

## Risks And Edge Cases
`MTK_UART_APDMA` is tied to `SERIAL_8250_MT6577`, so APDMA is not offered without the matching serial driver. HSDMA/CQDMA can be compile-tested off target, but real runtime still depends on matching device-tree bindings, clocks, IRQs, and SoC-specific register layouts.

## Test Signals
Kconfig tests should confirm symbol visibility under MediaTek and compile-test configurations, automatic selection of `DMA_ENGINE` and `DMA_VIRTUAL_CHANNELS`, and object inclusion when each symbol is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/Kconfig -->
