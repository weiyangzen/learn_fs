# sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.c

### Purpose
`fsl_raid.c` is the DMAengine/ASYNC driver for the Freescale RAID Engine. It offloads RAID5/RAID6-related XOR, P/Q parity, and memcpy operations using hardware job rings, compound frames, and command descriptor blocks.

### Important APIs, Types, And Functions
Major DMAengine operations are `fsl_re_alloc_chan_resources()`, `fsl_re_free_chan_resources()`, `fsl_re_tx_submit()`, `fsl_re_issue_pending()`, `fsl_re_tx_status()`, `fsl_re_prep_dma_xor()`, `fsl_re_prep_dma_pq()`, and `fsl_re_prep_dma_memcpy()`. Internal helpers include `fsl_re_prep_dma_genq()`, `fill_cfd_frame()`, `fsl_re_init_desc()`, `fsl_re_chan_alloc_desc()`, `fsl_re_isr()`, `fsl_re_dequeue()`, `fsl_re_cleanup_descs()`, `fsl_re_desc_done()`, `fsl_re_chan_probe()`, `fsl_re_probe()`, `fsl_re_remove_chan()`, and `fsl_re_remove()`.

### Control Flow, State, And Persistence
Probe maps the RAID Engine register region, puts the engine in non-DPAA mode, programs the Galois-field polynomial, initializes DMAengine capabilities, creates DMA pools for compound/CDB blocks and hardware descriptor rings, scans job-queue and job-ring device-tree nodes, and creates one DMA channel per job ring. Channel probe maps job-ring registers by offset, creates a child platform device, requests the IRQ, allocates inbound/outbound rings, programs ring base/size registers, preserves LIODN bits from firmware, configures the job ring, and enables it. Prepared descriptors fill a CDB plus compound frames for MOVE, GenQ/XOR, or GenQQ/PQ operations. Submit queues descriptors in software; issue-pending copies descriptors into the inbound ring while slots are available. IRQs clear job-ring interrupt status and schedule a tasklet, which matches outbound descriptors to active software descriptors, completes callbacks, moves descriptors to the ack queue, and recycles acked descriptors.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on DMAengine async_tx, MD RAID clients, OF platform child nodes, big-endian register access, DMA pools, hardware job rings, tasklets, and 40-bit DMA addressing. Risks include weak error recovery that logs but cannot report rich failures to MD, descriptor matching by hardware address, resource cleanup only expecting descriptors on `free_q`, no explicit handling for active/submit descriptors during free, ignored return values from job-ring probe and DMA registration, fixed maximum data length of 1 MiB, source-count constraints, and special single-source PQ behavior. Test signals include RAID5 XOR, RAID6 PQ with and without `DMA_PREP_CONTINUE`, `DMA_PREP_PQ_DISABLE_P`, memcpy MOVE, ring wrap at 1024 entries, interrupt/error paths, descriptor reuse after async ack, multiple job rings, and remove after idle operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.c -->
