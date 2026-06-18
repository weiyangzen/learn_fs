## sources/distributed-fs/ceph-client/include/uapi/linux/dma-heap.h

Purpose: This header defines the dma-buf heaps userspace allocation ABI. A heap device accepts an allocation request and returns a dma-buf file descriptor for memory from that heap.

Important APIs and types: `DMA_HEAP_VALID_FD_FLAGS` allows `O_CLOEXEC` and access-mode bits. `DMA_HEAP_VALID_HEAP_FLAGS` is currently zero, so heap-specific flags are not exposed here. `struct dma_heap_allocation_data` carries requested `len`, returned `fd`, `fd_flags`, and `heap_flags`. `DMA_HEAP_IOCTL_ALLOC` is the only ioctl in this header.

Control flow and state: Userspace opens a heap node, populates allocation data, calls `DMA_HEAP_IOCTL_ALLOC`, and receives a dma-buf fd in `fd`. Subsequent sharing, mmap, sync, and fencing use the dma-buf ABI, not this heap ABI. The heap object itself manages backing pages and lifetime through the returned file descriptor.

Persistence and dependencies: There is no on-disk persistence. Allocations persist while the returned dma-buf fd or its duplicates/imports are referenced. The header depends on Linux ioctl and type definitions and assumes open flags are visible through included userspace headers.

Integration points: This ABI feeds dma-buf consumers such as DRM, V4L2, camera, display, codecs, and userspace graphics pipelines. It is the replacement for older Android ion allocation patterns.

Risks and test signals: Risks include accepting unsupported heap flags, integer overflow or truncation in `len`, failing to set close-on-exec for sensitive buffers, assuming heap names imply security properties, and mismatched access mode expectations. Tests should cover zero and non-page-aligned lengths, invalid `fd_flags`/`heap_flags`, successful fd close-on-exec behavior, mmap and dma-buf sync through `dma-buf.h`, and allocation failure under memory pressure.
