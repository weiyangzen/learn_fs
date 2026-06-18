# sources/distributed-fs/ceph-client/drivers/spi/spi-au1550.c

## Purpose
Alchemy Au1550/Au1200/Au1300 PSC SPI host driver using the legacy `spi_bitbang` framework, platform data chip-select callbacks, IRQ-driven PIO, and optional Au1xxx DBDMA for 4 to 8 bit transfers.

## Important APIs, Types, and Functions
`struct au1550_spi` embeds `spi_bitbang`, stores PSC registers, IRQ, transfer cursors, word handlers, selected transfer backend, completion, DBDMA channel IDs, RX temporary DMA buffer, platform data, and MMIO resource. `au1550_spi_baudcfg()` computes hardware baud/divider fields. `au1550_spi_chipsel()` configures mode, word length, DMA disable, speed, and platform CS callbacks. `au1550_spi_dma_txrxb()` and `au1550_spi_pio_txrxb()` implement transfer backends. IRQ dispatch calls either DMA or PIO callback based on word size and DMA availability.

## Control Flow
Module init first validates the Alchemy CPU type and registers an 8-bit DBDMA memory device when DMA is enabled. Probe requires platform data, IRQ, DMA resources, and MMIO resource, manually reserves and maps registers, initializes bitbang callbacks, allocates DBDMA rings and RX temp buffer if available, configures word handlers, requests IRQ, computes host speed limits, initializes PSC SPI mode, and starts bitbang. During CS activation, the driver disables PSC device enable, writes CPOL/CPHA/LSB/word length/DMA/speed settings, waits for device ready, then calls platform CS activation. Transfers wait on `host_done`, completed by PSC events in IRQ context.

## State and Persistence
Word handler function pointers are updated by current bits-per-word. `usedma` is both module parameter and per-device flag. Temporary RX DMA buffer is persistent across transfers and resized as needed. Hardware state is manually restored only through PSC setup/remove paths and platform CS callbacks.

## Dependencies and Integration Points
It depends on MIPS Alchemy PSC and DBDMA headers/APIs, platform data `au1550_spi_info`, `spi_bitbang`, manual MMIO reservation, IRQs, and DMA mapping.

## Risks
The driver is legacy and non-devm; error unwinding is manual. DMA mapping errors are logged but do not always abort before DBDMA setup. DMA uses `virt_to_phys()` after `dma_map_single()`, which is suspicious on nontrivial DMA mappings. DMA only works for <=8 bpw; wider transfers use PIO. Completion waits have no timeout, so a lost IRQ can hang a transfer.

## Test Signals
Validate PIO and DMA transfers, all supported bpw ranges, missing RX buffer path using temp DMA buffer, DBDMA residue accounting after error, platform CS callbacks, module parameter `usedma=0`, probe unwind paths, and IRQ loss/error event behavior.
