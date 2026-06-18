# sources/distributed-fs/ceph-client/include/media/videobuf2-dma-contig.h

Purpose: This header exposes the contiguous-DMA videobuf2 memory allocator. It is intended for drivers whose hardware consumes a single DMA address per plane.

Important APIs, types, and functions: `vb2_dma_contig_plane_dma_addr()` retrieves a `dma_addr_t` cookie from a vb2 plane via `vb2_plane_cookie()` and dereferences it. `vb2_dma_contig_set_max_seg_size()` configures the device DMA segment limit. `vb2_dma_contig_clear_max_seg_size()` is an inline no-op in this tree. `vb2_dma_contig_memops` is the allocator operations table to assign to `vb2_queue.mem_ops`.

Control flow: A driver sets `q->mem_ops = &vb2_dma_contig_memops`, initializes its queue, and after buffers are allocated or imported uses `vb2_dma_contig_plane_dma_addr()` inside prepare/queue paths to program hardware DMA registers.

State and persistence behavior: The header adds no state. Allocator-private state lives behind the plane cookie and is owned by the implementation of `vb2_dma_contig_memops`.

Dependencies and integration points: It depends on `videobuf2-v4l2.h` and Linux DMA mapping. It integrates with vb2 MMAP, USERPTR, or DMABUF memory flows depending on allocator support and with hardware that requires physically or DMA-contiguously mapped buffers.

Risks: The inline helper assumes `vb2_plane_cookie()` returns a valid `dma_addr_t *`; callers must validate plane indexes and queue setup. Segment-size setup must match device DMA limitations or DMA mappings may exceed hardware capability. Contiguous allocation can fail under memory pressure.

Test signals: Exercise buffer allocation under fragmentation, DMA address retrieval for all planes, exported/imported dmabuf paths, segment-size configuration on probe/remove, and DMA programming with multi-planar formats.
