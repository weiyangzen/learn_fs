<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-omnitek.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-omnitek.h

Purpose: Defines the Omnitek DMA descriptor layout and declares DMA/descriptor helper APIs.

Important APIs/types: `struct sg_dma_descriptor` matches the hardware descriptor format with PCI address, local sync marker, next pointer, byte count, and reserved fields. Public functions initialize DMA, start/abort/check channels, create descriptor lists, chain/loop/end descriptor lists, allocate/free coherent descriptor memory, and toggle descriptor interrupts.

Control flow: Header declarations support V4L2 queue setup, streaming start/stop, and IRQ completion.

State/persistence: No header state. Descriptor instances persist per vb2 buffer while allocated.

Dependencies/integration: Includes Linux scatterlist and Cobalt driver definitions. Used by V4L2 and IRQ modules.

Risks: The descriptor struct must remain exactly aligned with FPGA expectations; field reordering or type changes would break DMA.

Test signals: Build checks and runtime DMA streaming across all stream directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-omnitek.h -->
