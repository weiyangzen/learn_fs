
# sources/distributed-fs/ceph-client/include/linux/platform_data/crypto-ux500.h

## Purpose
This header defines platform data for ST-Ericsson UX500 crypto/hash hardware. It supplies DMA channel configuration and filter hooks used by the UX500 crypto drivers.

## Important APIs And Types
`struct hash_platform_data` carries a `mem_to_engine` filter parameter and a `dma_filter()` callback that selects a `dma_chan`. `struct cryp_platform_data` contains two `stedma40_chan_cfg` objects for memory-to-engine and engine-to-memory DMA directions.

## Control Flow, State, And Persistence
There is no executable control flow. Board or platform code fills these structures before driver probe. The crypto driver consumes them while requesting DMA channels and configuring transfer direction. State is static platform configuration and is not persisted by this header.

## Dependencies And Integration Points
It depends on the DMAengine API and `dma-ste-dma40.h`. It integrates UX500 crypto/hash drivers with the ST-Ericsson DMA40 controller and board-specific DMA request routing.

## Risks And Test Signals
Incorrect DMA filter parameters or channel configs can make crypto transfers hang, corrupt buffers, or silently fall back incorrectly. Test signals include successful DMA channel request, hash/cryp throughput tests, bidirectional DMA transfer completion, and probe deferral behavior when DMA resources are unavailable.
