# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-vmalloc.c

## Purpose
`videobuf2-vmalloc.c` implements the CPU-addressable vmalloc memory backend for vb2. It is useful for devices or software paths that do not need a hardware DMA-contiguous allocation, and it supports MMAP, USERPTR, DMABUF import, and dma-buf export when DMA support is enabled.

## Important APIs, Types, and Functions
The exported table is `vb2_vmalloc_memops`. `struct vb2_vmalloc_buf` stores vaddr, frame vector, DMA direction, size, refcount/VMA handler, and imported dma-buf pointer. Key functions include `vb2_vmalloc_alloc()`, `vb2_vmalloc_put()`, `vb2_vmalloc_get_userptr()`, `vb2_vmalloc_put_userptr()`, `vb2_vmalloc_vaddr()`, `vb2_vmalloc_mmap()`, `vb2_vmalloc_get_dmabuf()`, `vb2_vmalloc_attach_dmabuf()`, `vb2_vmalloc_map_dmabuf()`, `vb2_vmalloc_unmap_dmabuf()`, and dma-buf attach/map/vmap/mmap/release callbacks.

## Control Flow
MMAP allocation creates a `vmalloc_user()` buffer, initializes refcount/VMA handler state, and returns it to vb2. MMAP uses `remap_vmalloc_range()` and common VMA ops to track mappings. USERPTR creates a frame vector, maps page-backed vectors with `vm_map_ram()`, or ioremaps physically contiguous PFN vectors when page structs are unavailable, then stores a CPU pointer adjusted by page offset. USERPTR release unmaps RAM or I/O mapping, dirties pages for capture/bidirectional directions, destroys the frame vector, and frees state. Export builds an sg table from `vmalloc_to_page()` pages for each dma-buf attachment and maps it for importers. Import simply keeps the dma-buf pointer, vmap's it on `map_dmabuf`, and vunmap's it on unmap/detach.

## State and Persistence
The backend keeps per-buffer virtual address state and refcounts while mappings or exported dma-bufs exist. Imported dma-bufs use `vaddr == NULL` until mapped. USERPTR frame-vector state persists until vb2 releases the user pointer. No state is persistent across queue lifetime.

## Dependencies and Integration Points
It depends on vmalloc APIs, mm frame-vector helpers from `videobuf2-memops.c`, common VMA ops, dma-buf when available, and V4L2/vb2 memory contracts. DVB mmap support selects this backend through Kconfig because demux/DVR mmap buffers are CPU-filled rather than hardware DMA-contiguous.

## Risks and Edge Cases
This backend provides CPU virtual access but not a hardware-specific DMA address cookie, so it is unsuitable for drivers that need direct DMA addresses unless they only use dma-buf scatter mappings. USERPTR PFN vectors must be physically contiguous for ioremap fallback. `buf->vaddr += offset` stores an adjusted pointer, so release masks back to the page boundary before unmapping page-backed mappings. Export requires every vmalloc page to resolve through `vmalloc_to_page()`. Imported dma-buf vmap failures become `-EFAULT`.

## Test Signals
Test MMAP read/write paths, USERPTR with page-backed and PFN-backed ranges, DMABUF import/export, repeated mmap/munmap, and DVB mmap consumers. Signals include stable CPU vaddr access, correct dirtying on capture release, successful sg-table construction for exported vmalloc buffers, no VMA refcount leaks, and clean detach when imported dma-bufs are still mapped.
