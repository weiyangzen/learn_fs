
# sources/distributed-fs/ceph-client/include/linux/platform_data/dma-mcf-edma.h

## Purpose
This header defines ColdFire/Freescale eDMA platform data. It connects platform DMA channel counts and slave maps to the eDMA engine driver.

## Important APIs And Types
It declares `mcf_edma_filter_fn(struct dma_chan *chan, void *param)` and the helper macro `MCF_EDMA_FILTER_PARAM(ch)`. `struct mcf_edma_platform_data` contains the number of DMA channels, a pointer to a `dma_slave_map`, and the number of slave-map entries.

## Control Flow, State, And Persistence
No executable control flow is implemented here. Platform setup provides channel counts and slave mappings; DMA consumers use the filter parameter to match specific channels. State is static hardware routing.

## Dependencies And Integration Points
The header forward-declares `struct dma_slave_map` and uses `struct dma_chan`. It integrates ColdFire platform code, DMAengine slave maps, and eDMA consumer drivers.

## Risks And Test Signals
Risks include channel number mismatches, incomplete slave maps, and invalid filter parameters. Test signals include DMAengine slave channel lookup for every mapped peripheral, transfer completion, probe failure for missing maps, and concurrent channel allocation stress.
