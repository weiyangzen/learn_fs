<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/pxa-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/pxa-dma.h

## Purpose
Defines PXA DMA channel request metadata.

## Important APIs, Types, And Functions
`enum pxad_chan_prio` describes highest, normal, low, and lowest channel priority. `struct pxad_param` contains a DRCMR requestor line and minimal mandatory priority.

## Control Flow
Slave drivers pass `pxad_param` when requesting a DMA channel. The PXA DMA driver grants a channel with priority at least as strong as requested and programs the requestor line.

## State And Persistence
State is per-channel request configuration. No persistence exists.

## Dependencies And Integration Points
Integrates PXA peripheral drivers with the PXA DMAengine driver and SoC requestor-line routing.

## Risks And Edge Cases
Wrong DRCMR line routes transfers to the wrong peripheral. Priority is a minimum requirement, so callers should not assume an exact priority if a stronger channel is allocated.

## Test Signals
Tests should cover channel allocation for each priority, invalid requestor lines, priority fallback, and transfer routing for representative peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/pxa-dma.h -->
