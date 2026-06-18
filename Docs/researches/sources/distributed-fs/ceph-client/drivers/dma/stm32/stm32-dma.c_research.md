# sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-dma.c

## Purpose
`stm32-dma.c` is the DMAEngine driver for the classic STM32 DMA controller. It supports slave SG transfers, cyclic transfers, optional memory-to-memory transfers, pause/resume, residue reporting, runtime PM clock control, and optional interaction with STM32 MDMA through peripheral config.

## Important APIs, Types, And Functions
Important types are `struct stm32_dma_device`, `struct stm32_dma_chan`, `struct stm32_dma_desc`, `struct stm32_dma_sg_req`, `struct stm32_dma_chan_reg`, `struct stm32_dma_cfg`, and `struct stm32_dma_mdma_config`. The descriptor is a flexible array of per-SG register snapshots. Each channel keeps a `virt_dma_chan`, current descriptor, next SG index, DMA slave config, cached register config, FIFO threshold, memory width/burst, status, and MDMA trigger metadata.

DMAEngine operations are implemented by `stm32_dma_alloc_chan_resources`, `stm32_dma_free_chan_resources`, `stm32_dma_tx_status`, `stm32_dma_issue_pending`, `stm32_dma_prep_slave_sg`, `stm32_dma_prep_dma_cyclic`, `stm32_dma_prep_dma_memcpy`, `stm32_dma_slave_config`, `stm32_dma_pause`, `stm32_dma_resume`, `stm32_dma_terminate_all`, and `stm32_dma_synchronize`. Platform integration is through `stm32_dma_probe`, `stm32_dma_of_xlate`, and the `st,stm32-dma` match table.

## Control Flow
Probe maps registers, enables the clock, optionally resets hardware, configures DMAEngine capabilities, initializes eight virtual channels, registers the DMA device, requests per-channel IRQs, registers the OF DMA controller, and enables runtime PM. OF translation expects four cells: channel id, request line, stream config, and feature flags. It reserves a slave channel and calls `stm32_dma_set_config`, which seeds stream register bits, request line, interrupts, FIFO threshold/direct mode, alternate acknowledge, and MDMA stream id.

Transfer preparation validates channel configuration and builds a software descriptor. `stm32_dma_set_xfer_param` computes data widths, burst sizes, FIFO/direct mode, direction bits, peripheral address, and register fields. Slave SG and cyclic prep fill one register snapshot per SG or period; memcpy prep splits large copies into aligned chunks. `issue_pending` pulls the next virtual descriptor, programs SCR/SPAR/SM0AR/SM1AR/SFCR/SNDTR, clears pending IRQs, and enables the stream.

The IRQ handler decodes FIFO, direct mode, transfer complete, half-transfer, and error flags. Transfer complete advances cyclic callbacks or completes non-cyclic descriptors, then starts queued work. Pause disables the stream and snapshots NDTR/address-relevant register state. Resume adjusts peripheral/memory addresses by the consumed offset and re-enables the stream; cyclic double-buffer mode has special reconfiguration paths.

## State And Persistence
Runtime state is per-channel in memory and hardware registers. Descriptors store immutable register snapshots for each segment. `chan->desc`, `next_sg`, `busy`, and `status` are protected by the virt-dma lock. Runtime PM only gates the clock; this driver does not save and restore active channel registers across runtime suspend because resources are held while channels are allocated and system suspend refuses if streams are enabled.

## Dependencies And Integration Points
The driver depends on DMAEngine, `virt-dma`, OF DMA, platform resources, clocks, reset controls, runtime PM, scatterlists, DMA mapping, bitfield helpers, and iopoll. It integrates with STM32 device-tree clients via DMA spec cells and with STM32 MDMA by filling `stm32_dma_mdma_config` in `dma_slave_config.peripheral_config` when requested.

## Risks
Pause/resume and cyclic double-buffer handling are the most complex paths, especially address offset correction after NDTR changes and CT/DBM toggling. FIFO threshold and burst selection must avoid configurations that leave bytes stuck in FIFO. The IRQ handler logs some errors but does not always complete descriptors as failed. The residue computation explicitly handles races where hardware swaps double buffers around the NDTR read; this is an important but fragile approximation. Probe requests exactly eight IRQs matching `STM32_DMA_MAX_CHANNELS`, so device-tree IRQ layout must be correct.

## Test Signals
Signals include successful `st,stm32-dma` probe, DMAEngine dmatest memcpy when `st,mem2mem` is set, slave RX/TX SG tests with 1/2/4 byte widths, cyclic audio periods with one and multiple periods, pause/resume during cyclic and SG transfers, residue under active double-buffer mode, MDMA-triggered transfers, runtime suspend/resume while idle, and system suspend refusal while a stream is enabled.
