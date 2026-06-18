<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/mxs-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/mxs-dma.h

## Purpose
Defines MXS DMA PIO control bits and a wrapper for preparing PIO transfers through DMAengine.

## Important APIs, Types, And Functions
Macros are `MXS_DMA_CTRL_WAIT4END` and `MXS_DMA_CTRL_WAIT4RDY`. `mxs_dmaengine_prep_pio()` wraps `dmaengine_prep_slave_sg()` by casting an array of PIO words to a scatterlist pointer when using PIO-style transfers.

## Control Flow
Drivers prepare PIO command words and call the wrapper with a DMA channel, word count, transfer direction, and flags. The MXS DMAengine interprets the passed words as PIO instructions when the direction indicates the special mode expected by the controller.

## State And Persistence
State is transient DMA descriptor/PIO word state. No persistence exists.

## Dependencies And Integration Points
Depends on DMAengine and MXS controller semantics. The wrapper exists to make the unusual PIO-as-SG cast explicit at call sites.

## Risks And Edge Cases
The cast is intentionally nonstandard; only MXS DMAengine consumers should use it. Direction and `npio` must match the controller's expectations, and the PIO word storage must remain valid until the descriptor is prepared.

## Test Signals
Tests should cover PIO command preparation, wait-for-end/ready flags, correct word count, invalid direction rejection by the DMAengine driver, and transfer completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/mxs-dma.h -->
