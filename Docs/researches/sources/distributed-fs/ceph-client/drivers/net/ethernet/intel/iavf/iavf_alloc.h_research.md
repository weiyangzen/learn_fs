# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_alloc.h

Purpose: this header declares the iavf memory allocation abstraction used by AdminQ and shared hardware-code layers.

Important APIs/types: it defines `enum iavf_memory_type` values for ARQ/ASQ/ATQ buffers and rings, page descriptors, backing pages, jumbo backing pages, and reserved memory. It declares `iavf_allocate_dma_mem`, `iavf_free_dma_mem`, `iavf_allocate_virt_mem`, and `iavf_free_virt_mem`.

Control flow and state: callers pass an `iavf_hw` pointer, destination memory descriptor, memory type, size, and alignment for DMA allocations. AdminQ uses these APIs to allocate descriptor rings and indirect command/event buffers, then frees them during queue shutdown or unwind.

Dependencies and integration: this file forward-declares `struct iavf_hw`; concrete memory descriptor types are supplied by included iavf type headers in callers. It abstracts OS allocation details away from common Intel hardware code.

Risks and test signals: allocation type values may be used for diagnostics or platform-specific behavior, so reordering can be risky. Tests should cover AdminQ allocation/unwind paths, DMA alignment, zero-size/oversize failures, and remove/reset cleanup with no leaks.
