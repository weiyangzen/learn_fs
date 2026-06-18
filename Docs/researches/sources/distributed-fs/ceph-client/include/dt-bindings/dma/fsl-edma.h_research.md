# sources/distributed-fs/ceph-client/include/dt-bindings/dma/fsl-edma.h

## Purpose
Defines Freescale/NXP eDMA DT flag bits used in DMA specifiers.

## Important APIs, Types, and Constants
Exports `FSL_EDMA_RX`, `FSL_EDMA_REMOTE`, `FSL_EDMA_MULTI_FIFO`, `FSL_EDMA_EVEN_CH`, and `FSL_EDMA_ODD_CH`, with bit values from `0x1` through `0x10`. They encode direction, remote request usage, multi-FIFO behavior, and channel parity restrictions.

## Control Flow and State
No runtime flow. The flags are compile-time bitmasks; transfer state is in the eDMA engine and driver.

## Dependencies and Integration Points
Self-contained header included by DTS files that configure eDMA request cells and by drivers or examples that interpret those cells.

## Risks and Test Signals
Because these are flags, consumers must OR values rather than treat them as exclusive enums. Test signals include schema validation and DMA client tests for RX/TX, remote requests, multi-FIFO, and even/odd channel constraints.
