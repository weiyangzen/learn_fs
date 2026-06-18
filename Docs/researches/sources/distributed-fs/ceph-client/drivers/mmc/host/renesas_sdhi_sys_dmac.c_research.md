# sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_sys_dmac.c

## Purpose
`renesas_sdhi_sys_dmac.c` is the SDHI front-end for Renesas controllers using external/system DMA channels. It provides older SoC OF configuration, DMA channel acquisition/configuration, bounce-buffer handling for unaligned single SG entries, DMA issue/completion coordination, and delegation to the shared SDHI core.

## Important APIs, Types, And Functions
The file defines OF data for default, RZ, R-Car Gen1, and R-Car Gen2 controllers, plus Gen2 SCC taps. The TMIO DMA ops are `renesas_sdhi_sys_dmac_start_dma()`, `renesas_sdhi_sys_dmac_enable_dma()`, `renesas_sdhi_sys_dmac_request_dma()`, `renesas_sdhi_sys_dmac_release_dma()`, `renesas_sdhi_sys_dmac_abort_dma()`, and `renesas_sdhi_sys_dmac_dataend_dma()`. Direction-specific setup is in `renesas_sdhi_sys_dmac_start_dma_rx()` and `_tx()`, and DMA completion is handled by `renesas_sdhi_sys_dmac_dma_callback()`.

## Control Flow
Probe calls `renesas_sdhi_probe()` with OF match data and system-DMAC ops. DMA request obtains TX and RX channels together, configures slave addresses/widths, allocates a one-page bounce buffer, initializes a completion, and enables SDHI DMA. Per request, start validates two-byte alignment and minimum length. Unaligned single-page SG entries use the bounce buffer; unsupported or failed DMA releases both channels and permanently falls back to PIO. Issue work enables DATAEND IRQ and submits pending DMA. Completion unmaps DMA, waits for TMIO DATAEND completion, then calls `tmio_mmc_do_data_irq()` under the host lock.

## State And Persistence
Runtime state lives in TMIO host channel pointers, `bounce_buf`, `bounce_sg`, `host->sg_ptr`, `host->dma_on`, and `dma_priv.dma_dataend`. No persistent state exists.

## Dependencies And Integration Points
The front-end depends on DMAengine slave channels, optional legacy SHDMA filters/platform channel private data, OF matches, TMIO DMA ops, the SDHI common core, MMC scatterlists, PM runtime callbacks, and system workqueues.

## Risks And Test Signals
Risks include permanent PIO fallback after any DMA setup failure, bounce-buffer copying for TX but not post-copying RX here, completion ordering between DMA and DATAEND, channel-pair all-or-nothing assumptions, and small-transfer bypass. Test signals include Gen1/Gen2/RZ probe, DMA channel configuration, aligned and unaligned read/write paths, small transfer PIO behavior, DMA failure fallback, DATAEND wait completion, abort termination, bounce buffer lifetime, and runtime PM suspend/resume.
