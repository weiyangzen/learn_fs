# sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.h -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.h

### Purpose
`dpaa2-qdma.h` defines the private data structures, descriptor command bits, pool sizing, and helper prototypes shared by the DPAA2 QDMA driver. It captures how Linux virtual DMA channels map to DPAA2 DPDMAI queues and how command/frame-list buffers are tracked.

### Important APIs, Types, And Functions
Important types are `struct dpaa2_qdma_sd_d`, `struct dpaa2_qdma_chan`, `struct dpaa2_qdma_comp`, `struct dpaa2_qdma_engine`, `struct dpaa2_qdma_priv`, and `struct dpaa2_qdma_priv_per_prio`. It defines `NUM_CH`, `DPAA2_QDMA_STORE_SIZE`, coherent read/write command encodings, QMan frame descriptor flags, frame-list flags, `FD_POOL_SIZE`, and the `soc_fixup_tuning` table for LX2160A. Static prototypes declare component/channel cleanup helpers used across the C file.

### Control Flow, State, And Persistence
The header has no executable control flow, but it defines persistent runtime ownership. `dpaa2_qdma_priv` owns MC/DPIO resources, queue attributes, the DPDMAI handle context, and per-priority notification stores. `dpaa2_qdma_engine` owns the DMAengine device and fixed channel array. Each channel owns DMA pools plus used/free completion lists, while each completion object owns one frame descriptor, one frame-list block, one source/destination descriptor block, DMA addresses, and the virtual descriptor.

### Dependencies, Integration Points, Risks, And Test Signals
The definitions depend on DPAA2 frame descriptor types, DPDMAI attributes, DMA pools, `virt_dma_chan`, Management Complex devices, IOMMU domains, and SoC device matching. Risks include packed bitfield layout assumptions in `struct dpaa2_qdma_sd_d`, fixed eight-channel scaling, typo-prone hardware flag names, and the header-local static SoC table being included only by the implementation. Test signals include descriptor layout validation on hardware, channel-to-FQID assignment for multiple priorities, DMA pool alignment, and LX2160A command selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.h -->
