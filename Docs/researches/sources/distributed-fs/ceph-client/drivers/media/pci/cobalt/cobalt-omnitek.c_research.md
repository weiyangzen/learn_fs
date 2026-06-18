<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-omnitek.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-omnitek.c

Purpose: Implements support for the Omnitek scatter-gather DMA controller used by Cobalt streams, including channel discovery, descriptor creation, chaining, start, done, abort, allocation, and cleanup.

Important APIs/functions: `omni_sg_dma_init()` reads capability registers, determines channel count, 32/64-bit PCI support, counts memory channels before FIFO channels, aborts active channels, and logs capabilities. `omni_sg_dma_start()`, `is_dma_done()`, and `omni_sg_dma_abort_channel()` control a stream DMA channel. `descriptor_list_create()` converts a vb2 DMA scatterlist into hardware descriptors with line width/stride handling and interrupt-enabled loopback. `descriptor_list_chain()`, `descriptor_list_loopback()`, `descriptor_list_end_of_chain()`, and interrupt enable/disable helpers modify the final descriptor. Allocation/free use coherent DMA memory.

Control flow: V4L2 buffer init allocates/creates descriptors. Queuing loops a descriptor back to itself, disables its interrupt, adds it to the stream list, and chains all queued buffers. Streaming starts DMA at the first descriptor. Stop marks descriptor chains end-of-chain and waits or aborts.

State/persistence: Descriptor memory is per-buffer in `s->dma_desc_info[]`. Controller capabilities populate `cobalt->dma_channels`, `first_fifo_channel`, and `pci_32_bit`. Hardware channel control/status registers carry active/done/abort state.

Dependencies/integration: Tightly integrated with vb2 DMA-SG, Cobalt V4L2 queue ops, IRQ completion, and BAR0 DMA registers.

Risks: Descriptor generation assumes 4-byte alignment for addresses, size, stride, and descriptor bus addresses. The code rejects 64-bit DMA addresses when hardware reports 32-bit PCI mode. Descriptor memory sizing must cover worst-case pages per line; underruns could corrupt memory. `descriptor_list_create()` forces at least two descriptors for one-entry scatterlists. `descriptor_list_chain()` assumes `last_desc_virt` is valid.

Test signals: DMA capability logs, capture/output/audio streaming, high fragmentation USERPTR/DMABUF buffers, 32-bit DMA mask fallback, end-of-chain stop without timeout, abort path, and descriptor validation under max frame size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-omnitek.c -->
