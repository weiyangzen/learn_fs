# sources/distributed-fs/ceph-client/drivers/dma/idxd/dma.c

## Purpose
`dma.c` exposes IDXD work queues as dmaengine channels for kernel clients, supporting interrupt descriptors and DSA memmove when available.

## Important APIs, Types, And Functions
Important functions are `idxd_register_dma_device`, `idxd_register_dma_channel`, `idxd_dmaengine_drv_probe/remove`, `idxd_dma_submit_memcpy`, `idxd_dma_prep_interrupt`, `idxd_dma_tx_submit`, and `idxd_dma_complete_txd`.

## Control Flow
The device registers a dmaengine device with no channels. When a kernel WQ binds to the `dmaengine` subdriver, it enables the WQ, allocates/registers a channel, initializes preallocated descriptors, and holds a WQ device ref. Preparing a transfer fills an IDXD NOOP or MEMMOVE descriptor. `tx_submit` assigns a cookie and submits immediately; `issue_pending` is empty.

## State And Persistence Behavior
State lives in the dmaengine device, per-WQ channel, preallocated descriptors, cookies, and completion records. Status returns `DMA_OUT_OF_ORDER`.

## Dependencies And Integration Points
It depends on dmaengine, IDXD allocation/submission helpers, DSA opcodes, WQ state, and descriptor completion from IRQ paths.

## Risks And Test Signals
Submit can fail after cookie assignment; invalid interrupt handles may trigger resubmit; memcpy length is capped by hardware. Test WQ binding, `dmatest`, interrupt descriptors, terminate flush, synchronize drain, and clean unbind.
