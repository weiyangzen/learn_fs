<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mcf-edma-main.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mcf-edma-main.c

## Purpose
ColdFire-family platform glue for the Freescale/NXP eDMA DMAEngine implementation. It binds legacy platform-data-described ColdFire eDMA hardware to the shared `fsl-edma-common` channel implementation and exposes private slave/cyclic DMA channels to board code.

## Important APIs, Types, And Functions
`mcf_edma_tx_handler` and `mcf_edma_err_handler` service transfer and error IRQs by reading eDMA interrupt/error bitmaps and dispatching to `fsl_edma_tx_chan_handler` or `fsl_edma_err_chan_handler`. `mcf_edma_irq_init` and `mcf_edma_irq_free` acquire grouped platform IRQ resources named `edma-tx-00-15`, `edma-tx-16-55`, optional `edma-tx-56-63`, and optional `edma-err`. `mcf_edma_probe` allocates `struct fsl_edma_engine`, initializes `struct fsl_edma_chan` entries and DMAEngine callbacks, and registers the DMA device. `mcf_edma_filter_fn` matches a DMA request source id against this driver.

## Control Flow
Probe requires `struct mcf_edma_platform_data`, chooses the platform-supplied channel count or 64 channels, maps MMIO, initializes each virtual channel/TCD pointer, clears pending interrupt state, requests IRQs, then registers a DMAEngine device with private slave and cyclic capabilities. Transfer IRQs scan the 64-bit interrupt map, clear channel interrupt state through `regs->cint`, and hand completion to the common eDMA code. Error IRQs scan low and high error registers, disable requests, clear channel errors, and mark the channel or invoke the common error handler. Remove frees IRQs, cleans virtual channels, and unregisters the DMA device.

## State And Persistence
Runtime state is held in the devm-allocated `fsl_edma_engine`, channel array, MMIO register block, vchan lists, and platform filter map. Persistent hardware state includes TCD CSR clearing during probe, global interrupt clearing, and round-robin arbitration enabled through `EDMA_CR_ERGA | EDMA_CR_ERCA`. There is no filesystem persistence.

## Dependencies And Integration Points
Depends on Linux platform devices, legacy `platform_data/dma-mcf-edma.h`, DMAEngine, virt-dma through the common eDMA layer, and `fsl-edma-common.h`. Board files or platform data provide slave maps and IRQ names. DMA clients integrate through DMAEngine channel filtering with `mcf_edma_filter_fn` and the shared `fsl_edma_*` preparation/status callbacks.

## Risks And Edge Cases
IRQ initialization returns `-1` for missing mandatory grouped resources and can leak already-requested IRQs if a later request fails because error paths do not call `mcf_edma_irq_free`. The error handler returns `IRQ_NONE` if low error bits are empty even when high error bits may be pending, so high-half-only errors can be missed. The high-half error path sets `DMA_ERROR` without calling the common error handler, unlike low channels. Channel count from platform data is trusted against the fixed 64-channel interrupt/error bitmap assumptions.

## Test Signals
Useful signals are successful platform probe, DMAEngine registration, channel filtering by source id, cyclic/slave transfers completing through `fsl_edma_tx_chan_handler`, and injected hardware error IRQs updating channel status. IRQ resource naming and the high-half error path should be covered on ColdFire board or emulation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mcf-edma-main.c -->
