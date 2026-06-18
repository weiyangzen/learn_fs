# sources/distributed-fs/ceph-client/include/media/videobuf2-vmalloc.h

Purpose: This header exposes the vmalloc-backed videobuf2 allocator for drivers that need CPU-addressable, virtually contiguous buffers rather than DMA-oriented memory.

Important APIs, types, and functions: The sole public symbol is `vb2_vmalloc_memops`, a `struct vb2_mem_ops` implementation suitable for assigning to `vb2_queue.mem_ops`.

Control flow: Drivers select vmalloc memory ops at queue setup. vb2 core calls the allocator for allocation, vaddr lookup, userspace mapping, and release according to the queue's I/O mode.

State and persistence behavior: Allocator-private buffer state lives behind vb2 plane cookies and memory private pointers. The header adds no state or persistence.

Dependencies and integration points: It depends on `videobuf2-v4l2.h` and integrates with CPU-driven capture/output drivers, virtual devices, test drivers, or transports that do not require physically contiguous DMA buffers.

Risks: vmalloc memory is not physically contiguous and is unsuitable for DMA engines that cannot scatter/gather or use an IOMMU. Drivers must use `vaddr` paths rather than assuming DMA cookies. Large vmalloc allocations can fail or fragment virtual address space.

Test signals: Validate read/write file I/O, mmap, CPU access through `vb2_plane_vaddr()`, allocation/release loops, and rejection or avoidance on drivers that require DMA addresses.
