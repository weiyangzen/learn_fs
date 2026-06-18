# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-dma-contig.c

## Purpose
`videobuf2-dma-contig.c` implements the vb2 memory backend for devices that require one DMA-contiguous address range. It supports MMAP allocation, USERPTR pin/import, DMABUF import, and exporting MMAP buffers as dma-bufs, with separate handling for coherent and non-coherent DMA memory.

## Important APIs, Types, and Functions
The exported memops table is `vb2_dma_contig_memops`, and the helper export is `vb2_dma_contig_set_max_seg_size()`. `struct vb2_dc_buf` stores the device, virtual address, size, DMA address cookie, DMA direction, attributes, scatterlist, frame vector, mmap handler/refcount, dma-buf attachment, owning `vb2_buffer`, and non-coherent flag. Important functions include `vb2_dc_alloc()`, `vb2_dc_alloc_coherent()`, `vb2_dc_alloc_non_coherent()`, `vb2_dc_put()`, `vb2_dc_prepare()`, `vb2_dc_finish()`, `vb2_dc_mmap()`, `vb2_dc_get_userptr()`, `vb2_dc_put_userptr()`, `vb2_dc_attach_dmabuf()`, `vb2_dc_map_dmabuf()`, `vb2_dc_unmap_dmabuf()`, `vb2_dc_get_dmabuf()`, and `vb2_dc_get_contiguous_size()`.

## Control Flow
For MMAP buffers, allocation chooses `dma_alloc_attrs()` for coherent memory or `dma_alloc_noncontiguous()` for non-coherent memory, records a device reference, initializes a VMA refcount handler, and returns private allocator state to vb2. MMAP maps coherent memory with `dma_mmap_attrs()` or non-coherent memory with `dma_mmap_noncontiguous()`. USERPTR checks DMA cache alignment, pins a complete frame vector, maps page-backed vectors through an sg table, or falls back to resource mapping for physically contiguous PFN vectors, then verifies the DMA mapping is contiguous enough for the requested size. DMABUF import attaches to the device, maps the attachment during prepare, verifies the mapped sg list has a sufficiently contiguous DMA span, and records `dma_addr`. Export builds or reuses a base sg table, creates a dma-buf, and gives it attach/map/vmap/mmap/release callbacks.

## State and Persistence
Buffer state is per allocation/import and persists only while vb2 or exported dma-buf references hold the refcount. `refcount` tracks kernel/VMA/dma-buf users. `vaddr` can be allocated immediately for coherent buffers, created on demand for non-coherent or imported buffers, and released on unmap/put. `dma_sgt` changes meaning by mode: internal non-coherent allocation, USERPTR mapping, or imported dma-buf mapping. USERPTR pages are marked dirty for device-to-CPU directions when released.

## Dependencies and Integration Points
This backend depends on the DMA mapping API, dma-buf framework, scatterlist helpers, frame-vector helpers from `videobuf2-memops.c`, common VMA ops, `vb2_queue` DMA direction/attributes/cache flags, and device DMA parameters. Drivers select this backend when hardware consumes one contiguous DMA address, often after raising max segment size with `vb2_dma_contig_set_max_seg_size()` for IOMMU-backed sharing.

## Risks and Edge Cases
The backend rejects unaligned USERPTR buffers based on DMA cache alignment because partial cache lines are unsafe. Imported USERPTR/DMABUF memory must map as one contiguous DMA span; otherwise `-EFAULT` is returned even if the physical pages exist. Coherent allocations with `DMA_ATTR_NO_KERNEL_MAPPING` cannot provide a kernel `vaddr`. Non-coherent memory requires correct `prepare`/`finish` cache maintenance unless vb2 cache hints skip it. Export attach code copies `sgt_base`, so stale or missing base sg tables break dma-buf export. Detach paths warn if callers detach still-mapped buffers.

## Test Signals
Exercise MMAP allocation/mmap, non-coherent cache sync, `EXPBUF`, DMABUF import with contiguous and fragmented mappings, USERPTR alignment failures, and IOMMU max-segment sizing. Runtime checks should confirm stable DMA addresses, successful vmap only when supported, dirtying of capture USERPTR pages, no leaked device references, and clean unmap/detach ordering under streamoff and process exit.
