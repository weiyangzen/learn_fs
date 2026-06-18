# sources/distributed-fs/ceph-client/drivers/dma/fsl-qdma.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-qdma.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-qdma.c

### Purpose
`fsl-qdma.c` implements the DMAengine driver for the older NXP/Freescale Layerscape Queue DMA controller, currently matching `"fsl,ls1021a-qdma"`. It exposes memcpy through command queues, status queues, compound command descriptors, and source/destination descriptor buffers.

### Important APIs, Types, And Functions
Key types are `struct fsl_qdma_format`, `struct fsl_pre_status`, `struct fsl_qdma_chan`, `struct fsl_qdma_queue`, `struct fsl_qdma_comp`, and `struct fsl_qdma_engine`. Main functions are `fsl_qdma_probe()`, `fsl_qdma_reg_init()`, `fsl_qdma_halt()`, `fsl_qdma_irq_init()`, `fsl_qdma_prep_memcpy()`, `fsl_qdma_issue_pending()`, `fsl_qdma_enqueue_desc()`, `fsl_qdma_queue_handler()`, `fsl_qdma_queue_transfer_complete()`, `fsl_qdma_error_handler()`, `fsl_qdma_alloc_chan_resources()`, `fsl_qdma_free_chan_resources()`, `fsl_qdma_terminate_all()`, `fsl_qdma_synchronize()`, and `fsl_qdma_remove()`. Inline helpers encode and decode 40-bit descriptor addresses, queue IDs, offsets, status bits, format bits, and S/G lengths.

### Control Flow, State, And Persistence
Probe reads channel, queue, block, status-size, and queue-size device-tree properties, limits blocks to online CPUs, allocates coherent command/status rings, maps controller/status/block register windows, initializes queue state, assigns channels round-robin across queues and blocks, initializes hardware registers, requests error and queue IRQs, sets a 40-bit DMA mask, and registers the DMAengine device. Channel resource allocation creates DMA pools for command and descriptor buffers and preallocates queue completion objects. A memcpy prepare path fills a compound descriptor with a frame descriptor, source/destination S/G entries, and source/destination command words. Issue-pending copies the descriptor to the circular command queue and kicks enqueue. Queue IRQs drain status entries, match them against `comp_used`, set per-transfer error results if needed, complete cookies, and advance the status ring.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on `virt-dma`, endian wrappers from `fsldma.h`, platform resources, named IRQs, coherent DMA memory, DMA pools, OF properties, IRQ affinity hints, and DMAengine. Risks include ring pointer wrap logic, descriptor/status matching using per-CPU duplicate suppression, a likely invalid IRQ range condition using `id < 0 && id > block_number`, command queue full/XOFF handling that leaves descriptors pending, queue-size `ilog2()` assumptions, 40-bit address packing, lack of OF DMA controller registration despite freeing it in remove, and hardware halt timeouts. Test signals include memcpy completions under load, command/status ring wrap, status error mapping to DMA transaction results, multiple blocks and queues, big-endian register access, queue full behavior, interrupt affinity, halt/init after reset, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-qdma.c -->
