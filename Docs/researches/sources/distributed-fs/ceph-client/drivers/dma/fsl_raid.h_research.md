# sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.h -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.h

### Purpose
`fsl_raid.h` defines Freescale RAID Engine register layouts, command descriptor block formats, compound frame formats, hardware descriptor formats, driver-private state, channel state, and async descriptor state used by `fsl_raid.c`.

### Important APIs, Types, And Functions
Key register-layout structures are `struct fsl_re_ctrl` for global engine registers and `struct fsl_re_chan_cfg` for job-ring registers. Command and frame types include `struct fsl_re_move_cdb`, `struct fsl_re_dpi`, `struct fsl_re_xor_cdb`, `struct fsl_re_noop_cdb`, `struct fsl_re_pq_cdb`, `struct fsl_re_cmpnd_frame`, and `struct fsl_re_hw_desc`. Runtime state is captured by `struct fsl_re_drv_private`, `struct fsl_re_chan`, and `struct fsl_re_desc`. The header also defines opcodes, CDB bit masks, ring sizes, descriptor alignment and size constants, frame descriptor fields, and engine/job-ring control bits.

### Control Flow, State, And Persistence
The header has no executable flow. It defines persistent state layouts: global driver state owns the DMAengine device, mapped global registers, job-ring pointers, and DMA pools; each channel owns job-ring software queues, inbound/outbound rings and counters, IRQ tasklet, and allocation count; each descriptor owns the async descriptor, hardware frame descriptor, compound frame/CDB memory, DMA addresses, and status.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on DMAengine, list/spinlock/tasklet infrastructure, big-endian register semantics, and DMA address handling supplied by includers. It integrates the RAID Engine hardware ABI with the Linux async_tx DMA API. Risks include packed hardware format assumptions without explicit `__packed` on every CDB-like structure, 40-bit address high/low field conventions, fixed ring and descriptor pool sizes, endian correctness of bitfields stored in `__be32`, and license header dual-licensing context. Test signals include structure-size/alignment checks, hardware acceptance of CDB/compound frame layouts, ring base address programming, and successful XOR/PQ/MOVE operations using descriptors allocated from the declared pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl_raid.h -->
