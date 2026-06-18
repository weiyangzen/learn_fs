<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/imx-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/imx-dma.h

## Purpose
Defines i.MX DMA/SDMA peripheral metadata used by slave drivers and DMAengine channel selection.

## Important APIs, Types, And Functions
Defines `enum sdma_peripheral_type`, `enum imx_dma_prio`, `struct imx_dma_data`, helpers `imx_dma_is_ipu()` and `imx_dma_is_general_purpose()`, and `struct sdma_peripheral_config` for multi-FIFO audio devices.

## Control Flow
Slave drivers pass request lines, peripheral type, and priority in `imx_dma_data`. Audio drivers can pass `sdma_peripheral_config` to describe FIFO counts, strides, words per FIFO, and software done behavior. Helpers identify IPU and general-purpose SDMA/DMA channels by device or driver names.

## State And Persistence
State is static per-transfer or per-channel configuration. No persistence is defined.

## Dependencies And Integration Points
Depends on DMAengine channels, scatterlists, devices, and i.MX SDMA/DMA driver naming. Integrates serial, MMC, audio, display, I2C, SPI, ATA, memory, and other i.MX peripherals with DMAengine.

## Risks And Edge Cases
Name-based helpers are brittle if driver names change. Multi-FIFO audio configuration must match hardware FIFO layout and channel count. Secondary request lines and priority must match SoC data.

## Test Signals
Tests should cover channel matching, request-line setup, all relevant peripheral types, multi-FIFO SAI/micfil capture/playback, stride and wrap behavior, software-done mode, and driver-name helper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/imx-dma.h -->
