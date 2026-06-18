# sources/distributed-fs/ceph-client/include/media/videobuf2-dma-sg.h

Purpose: This header exposes the scatter/gather DMA videobuf2 memory allocator for hardware that can consume an SG table or an IOMMU mapping rather than a single contiguous DMA address.

Important APIs, types, and functions: `vb2_dma_sg_plane_desc()` returns the per-plane `struct sg_table *` stored as the vb2 plane cookie. `vb2_dma_sg_memops` is the allocator operations table for vb2 queues.

Control flow: Drivers select `vb2_dma_sg_memops` during queue initialization. When a buffer reaches the driver through `buf_queue`, the driver retrieves the SG table for each plane and programs DMA descriptors or IOMMU-backed hardware.

State and persistence behavior: State is delegated to the allocator-private cookie and SG table lifetime. The header itself has no persistent state.

Dependencies and integration points: It depends on `videobuf2-v4l2.h`, vb2 core cookie lookup, and Linux scatterlist infrastructure through the opaque `struct sg_table` pointer. It integrates with DMA-capable media drivers, USERPTR pinning, and DMABUF attachment paths.

Risks: Drivers must not retain SG table pointers beyond buffer ownership. Cache synchronization and map/unmap order are owned by vb2 memory ops and must not be bypassed. Hardware descriptor limits may be exceeded if queue validation does not account for worst-case SG fragmentation.

Test signals: Validate SG table retrieval for MMAP, USERPTR, and DMABUF, streaming with fragmented buffers, map/unmap balance, DMA descriptor bounds, and teardown while buffers are queued or exported.
