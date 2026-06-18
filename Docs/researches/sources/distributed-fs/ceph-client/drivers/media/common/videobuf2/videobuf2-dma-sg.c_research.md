# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-dma-sg.c

## Purpose
`videobuf2-dma-sg.c` implements the scatter/gather DMA memory backend for vb2. It allocates page-backed buffers, maps them as scatterlists for DMA, supports USERPTR and DMABUF import, allows dma-buf export, and provides optional kernel virtual mappings through `vm_map_ram()` or dma-buf vmap.

## Important APIs, Types, and Functions
The exported table is `vb2_dma_sg_memops`. `struct vb2_dma_sg_buf` stores device, kernel vaddr, pages, frame vector, offset, DMA direction, internal sg table, active DMA sg table, size, page count, refcount/VMA handler, dma-buf attachment, and owning `vb2_buffer`. Key functions are `vb2_dma_sg_alloc_compacted()`, `vb2_dma_sg_alloc()`, `vb2_dma_sg_put()`, `vb2_dma_sg_prepare()`, `vb2_dma_sg_finish()`, `vb2_dma_sg_get_userptr()`, `vb2_dma_sg_put_userptr()`, `vb2_dma_sg_vaddr()`, `vb2_dma_sg_mmap()`, `vb2_dma_sg_get_dmabuf()`, `vb2_dma_sg_attach_dmabuf()`, `vb2_dma_sg_map_dmabuf()`, and the dma-buf ops for attach/map/cpu access/vmap/mmap/release.

## Control Flow
MMAP allocation allocates a page pointer array, attempts compacted high-order page allocation with fallback to lower orders, creates an sg table from pages, maps it with `dma_map_sgtable(..., DMA_ATTR_SKIP_CPU_SYNC)`, and initializes VMA refcount state. `prepare` and `finish` perform explicit DMA sync unless vb2 skip flags are set. USERPTR pins a frame vector, requires page-backed memory, creates an sg table with the user offset, maps it for DMA, and later unmaps/dirties pages on release. MMAP maps pages into userspace with `vm_map_pages()`. `vaddr` maps internal pages with `vm_map_ram()` or imported dma-bufs with `dma_buf_vmap_unlocked()`. Export copies the active sg table for each attachment and maps/unmaps it per importer direction. Import attaches to the dma-buf and defers mapping until `map_dmabuf`.

## State and Persistence
State is volatile per buffer. Internal allocations keep `dma_sgt` pointing at `sg_table`; imported dma-bufs set `dma_sgt` only while pinned/mapped. `refcount` tracks MMAP and exported dma-buf references. `vaddr` is cached after first kernel mapping and unmapped on release/unmap. USERPTR page arrays are borrowed from the frame vector and released by `vb2_destroy_framevec()`.

## Dependencies and Integration Points
The backend integrates with page allocator, scatterlist and DMA mapping APIs, vmalloc mapping helpers, dma-buf, common vb2 VMA operations, and frame-vector helpers. It is appropriate for devices capable of scatter/gather DMA or IOMMU mappings that do not require one contiguous DMA address.

## Risks and Edge Cases
High-order allocation fallback reduces failure risk but can still fail under memory pressure after partial allocations. Unlike dma-contig, this backend does not enforce contiguous DMA mappings; drivers that need contiguity must not use it. USERPTR requires page-backed frame vectors and returns allocation-style errors for pin/map failures. Cache synchronization is explicit; wrong skip flags can expose stale data. Imported dma-buf `dma_sgt` being non-NULL indicates an active mapping, and detach warns/unmaps if vb2 lifecycle is violated. `vm_map_ram()` mappings must be released on all put paths.

## Test Signals
Test MMAP allocation under fragmentation, USERPTR import with aligned and offset addresses, DMABUF import/export, repeated vaddr requests, poll/streamoff while mapped, and cache sync on capture/output queues. Useful signals include no leaked pages after refcount drop, proper dirtying for capture USERPTR pages, sg table map/unmap balance, and successful dma-buf CPU access sync callbacks.
