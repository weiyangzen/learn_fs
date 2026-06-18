# sources/distributed-fs/ceph-client/drivers/dma/tegra186-gpc-dma.c

## Purpose
`tegra186-gpc-dma.c` is the DMAEngine provider for NVIDIA Tegra GPCDMA controllers on Tegra186, Tegra194, and Tegra234. It supports slave SG, cyclic peripheral DMA, memory copy, and memset using per-channel MMIO programming rather than hardware descriptor rings. It also programs memory-controller stream IDs for IOMMU integration.

## Important APIs, Types, and Functions
`struct tegra_dma_chip_data` captures SoC-specific channel count, channel register stride, maximum count, pause support, and termination method. `struct tegra_dma` owns the DMAEngine device, reset, base address, channel mask, stream-ID reservation bitmaps, and flexible array of channels. `struct tegra_dma_channel` wraps `virt_dma_chan`, channel identity, IRQ, slave ID, active descriptor, slave config, stream ID, status, and channel base offset. `struct tegra_dma_desc` is a virt-dma descriptor containing an array of `struct tegra_dma_sg_req`; each request stores a segment length and the exact channel register values to program.

Core paths are `tegra_dma_slave_config()`, `tegra_dma_prep_slave_sg()`, `tegra_dma_prep_dma_cyclic()`, `tegra_dma_prep_dma_memcpy()`, `tegra_dma_prep_dma_memset()`, `tegra_dma_issue_pending()`, `tegra_dma_start()`, `tegra_dma_configure_next_sg()`, `tegra_dma_isr()`, `tegra_dma_tx_status()`, `tegra_dma_terminate_all()`, pause/resume helpers, and probe/remove/PM functions.

## Control Flow
Probe matches chip data from OF, allocates channel storage, maps registers, resets the controller, obtains an IOMMU stream ID, reads `dma-channel-mask` or uses the default mask reserving channel 0, initializes enabled channels with IRQ numbers, base offsets, names, virt-dma state, and programmed stream IDs, registers DMAEngine capabilities, and registers OF DMA translation. OF translation allocates any slave channel and stores the request slave ID from the first specifier cell.

Preparation validates configuration and alignment, reserves slave IDs per direction to prevent conflicting MEM_TO_DEV or DEV_TO_MEM users, computes CSR/MMIOSEQ/MCSEQ fields, and records per-segment register images. Memcpy and memset require word-aligned addresses/lengths and single descriptors. Slave SG and cyclic split into one request per SG entry or period. Cyclic clears `ONCE` and wraps `sg_idx` on completion.

`issue_pending()` starts the next virt-dma descriptor if no descriptor is active. `tegra_dma_start()` writes WCOUNT, CSR, source/destination/high-address, fixed pattern, MMIO sequence, MC sequence, then enables the channel. The ISR decodes and clears errors, handles EOC, updates bytes transferred, invokes cyclic callbacks and preloads the next cyclic segment, or advances SG segments until completion. Completion frees the slave-ID reservation and clears the active descriptor.

## State and Persistence
State is volatile: channel registers, active descriptor pointer, SG index/count, bytes requested/transferred, pause status, channel mask, programmed stream IDs, and direction-specific slave-ID reservation bitmaps. No persistent storage is used. System suspend rejects busy channels. Resume resets the controller and reprograms each enabled channel stream ID.

## Dependencies and Integration Points
The driver uses DMAEngine, virt-dma, OF DMA, platform devices, resets, interrupts, IOMMU stream ID lookup, Tegra memory-controller DT bindings, MMIO polling, and scatterlists. It registers `DMA_SLAVE`, `DMA_PRIVATE`, `DMA_MEMCPY`, `DMA_MEMSET`, and `DMA_CYCLIC`, with 4-byte copy/fill alignment and burst residue granularity. Compatible strings are `nvidia,tegra186-gpcdma`, `nvidia,tegra194-gpcdma`, and `nvidia,tegra234-gpcdma`.

## Risks and Edge Cases
The driver requires 4-byte aligned memory addresses and lengths and rejects segments above the SoC maximum. Several error returns after `tegra_dma_sid_reserve()` in slave/cyclic preparation do not visibly free the reservation before returning, so repeated bad preparations for a slave ID can be a risk. Termination behavior differs by SoC: Tegra186 changes request selection and waits for TX/RX inactive, Tegra194 pauses, and Tegra234 ignores pause errors to recover flush states. `tegra_dma_get_residual()` uses EOC and word count state, which is delicate for cyclic transfers that may already have advanced. Pause/resume are exposed only for chips with hardware pause support.

## Test Signals
Validate probe with channel masks and stream-ID programming, OF xlate slave ID assignment, word-alignment rejection for memcpy/memset/slave, slave ID reservation conflicts by direction, SG chaining, cyclic callbacks and next-period preprogramming, pause/resume on Tegra194/234, Tegra186 stop-client termination, residue while running and paused, error register decode paths, suspend busy rejection, and resume stream-ID restoration.
