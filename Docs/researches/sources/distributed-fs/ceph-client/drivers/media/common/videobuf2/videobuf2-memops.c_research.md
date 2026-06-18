# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-memops.c

## Purpose
`videobuf2-memops.c` provides shared low-level memory helpers used by vb2 allocators. It creates and destroys frame vectors for USERPTR memory and provides common VMA operations that keep vb2 buffer refcounts balanced while buffers are mmap'ed.

## Important APIs, Types, and Functions
Exports are `vb2_create_framevec()`, `vb2_destroy_framevec()`, and `vb2_common_vm_ops`. The common VMA ops call `vb2_common_vm_open()` and `vb2_common_vm_close()` with a `struct vb2_vmarea_handler` stored in `vma->vm_private_data`.

## Control Flow
`vb2_create_framevec()` computes the page frame range covering a userspace address and length, allocates a frame vector, calls `get_vaddr_frames()`, requires a complete pin of all frames, and unwinds partial pins on failure. `vb2_destroy_framevec()` releases frames and destroys the vector. `vb2_common_vm_open()` increments the allocator-provided refcount when a VMA is duplicated or opened, while `vb2_common_vm_close()` calls the allocator-provided `put()` callback to drop the mapping reference.

## State and Persistence
Frame-vector state is temporary and owned by whichever allocator imported USERPTR memory. VMA state persists for the lifetime of userspace mappings and is represented by allocator-specific refcounts. There is no persistent storage.

## Dependencies and Integration Points
The file depends on mm frame-vector APIs, `get_vaddr_frames()`, `put_vaddr_frames()`, and the `vb2_vmarea_handler` contract shared with dma-contig, dma-sg, and vmalloc backends. Allocators install `vb2_common_vm_ops` after mapping their buffers into userspace.

## Risks and Edge Cases
Partial frame-vector acquisition is rejected with `-EFAULT` and must release any frames already pinned. USERPTR callers must pass the correct write flag so get-user-pages permissions and dirty tracking match DMA direction. The VMA close path trusts `vm_private_data` and the handler's refcount/put pointers; allocator mmap code must initialize them before calling `open()`. Refcount imbalance can keep orphaned buffers alive or free buffers while still mapped.

## Test Signals
USERPTR import tests should cover complete and partial/inaccessible ranges, write versus read mappings, and process exit while buffers are queued. MMAP tests should show refcount increments on mapping duplication and decrements on munmap/exit. KASAN/refcount warnings around `vb2_common_vm_close()` are high-value failure signals.
