# sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_internal_dmac.c

## Purpose
`renesas_sdhi_internal_dmac.c` is the SDHI front-end for Renesas controllers with an integrated DMAC. It supplies SoC match data and TMIO DMA operations to the common SDHI core, including internal-DMAC register programming, DMA completion coordination, pre/post mapping, and SoC-specific HS400 quirks.

## Important APIs, Types, And Functions
The file defines internal DMAC registers (`DM_CM_DTRAN_*`, `DM_CM_INFO*`, `DM_DTRAN_ADDR`), DMA cookies, global one-RX-use flag, R-Car/RZ OF data, SCC tap data, calibration tables, quirk tables, and OF match entries. DMA ops are implemented by `renesas_sdhi_internal_dmac_start_dma()`, `renesas_sdhi_internal_dmac_enable_dma()`, `renesas_sdhi_internal_dmac_abort_dma()`, `renesas_sdhi_internal_dmac_dataend_dma()`, `renesas_sdhi_internal_dmac_end_dma()`, `renesas_sdhi_internal_dmac_dma_irq()`, request/release hooks, and pre/post request hooks.

## Control Flow
Probe selects OF data/quirks, may override quirks via `soc_device_match()`, sets max DMA segment size, and calls `renesas_sdhi_probe()` with internal DMAC ops. Start maps the SG list, enforces 128-byte alignment, chooses read/write channel mode, optionally enforces the one-RX-DMAC workaround, enables DMA, writes transfer mode/address, and marks `host->dma_on`. The DMAC IRQ and TMIO DATAEND path set separate bits; only when both have occurred does workqueue completion call `tmio_mmc_do_data_irq()`.

## State And Persistence
State includes `data->host_cookie` mapping state, `dma_priv.end_flags`, `host->dma_on`, fake non-null `chan_rx/chan_tx` flags, and a global RX-in-use bit for affected SoCs. No durable state exists.

## Dependencies And Integration Points
The file integrates with Renesas SDHI core, TMIO DMA ops, MMC pre_req/post_req, system workqueues, SoC revision matching, OF matching, DMA mapping API, and internal SDHI DMAC registers.

## Risks And Test Signals
Risks include alignment fallback to PIO, global RX serialization, two-edge completion races, old INFO1 layout quirks, fixed-address mode, DMA abort reset sequencing, and fake channel pointers used as enable flags. Test signals include Gen3/RZ probe, pre-mapped request reuse, unaligned buffer PIO fallback, simultaneous channel RX workaround, DMA IRQ plus DATAEND ordering, abort on errors, HS400 quirk selection by SoC revision, and suspend/resume through common SDHI PM.
