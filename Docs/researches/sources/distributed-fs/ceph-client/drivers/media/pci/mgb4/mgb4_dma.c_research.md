# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_dma.c

- Purpose: DMAengine wrapper around AMD XDMA channels for frame transfers between FPGA queues and vb2 scatter-gather buffers.
- Important APIs/types/functions: `mgb4_dma_transfer()`, `mgb4_dma_channel_init()`, `mgb4_dma_channel_free()`, and callback `chan_irq()`.
- Control flow: Channel init requests named `c2hN` and `h2cN` DMA channels and initializes completions. Transfer configures direction and device address, prepares SG transfer, sets completion callback, submits, issues pending, waits up to 10 seconds, and terminates on timeout. Free releases channels.
- State and persistence: Per-channel `dma_chan` and `completion` live in `struct mgb4_dev`; no persistence.
- Dependencies and integration points: Used by vin/vout workqueues for every captured/output frame; depends on XDMA platform device and DMAengine slave SG support.
- Risks: Completion is not reinitialized before each transfer, so a previously completed channel can make later waits return immediately unless DMAengine guarantees completion state is reset elsewhere. Timeout is coarse; error handling maps many failures to `-EIO`. Partial channel-init failure does not release earlier channels before returning.
- Test signals: Stress capture/output DMA, timeout injection, repeated transfers on one channel, partial channel request failure, and unload after DMA errors.
