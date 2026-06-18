# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_dma_rmgr.c

Purpose: allocates ISYS2401 DMA channels per DMA device.

Important functions/state: static `isys_dma_rsrc[N_ISYS2401_DMA_ID]`; init/uninit clear resource state; acquire finds the first inactive channel bit below the device's channel count and returns it; release clears an active channel bit and decrements the counter.

Control flow: acquire reads `N_ISYS2401_DMA_CHANNEL_PROCS[dma_id]`, checks `num_active`, iterates channel IDs, and marks the first free bit. Release validates channel range and active count before clearing.

State/persistence: per-DMA bitmap/counter state persists globally until uninit. No synchronization is provided.

Dependencies/integration: used by virtual ISYS channel creation to attach IBUF-to-VMEM/DDR transfer channels.

Risks: init/uninit call `memset(&isys_dma_rsrc, 0, sizeof(isys_dma_rsrc_t))`, which only clears one element rather than the whole array; if multiple DMA IDs exist, stale state can remain. Acquire iterates to `N_ISYS2401_DMA_CHANNEL` rather than `max_dma_channel` but guards by `num_active`.

Test signals: multi-DMA init reset, capacity exhaustion per DMA ID, release/reacquire, invalid DMA/channel assertions, and concurrent setup serialization.
