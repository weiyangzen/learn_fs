# sources/distributed-fs/ceph-client/arch/parisc/include/asm/dma-mapping.h

Purpose: supplies PA-RISC DMA mapping hooks and cache-alignment policy to the generic DMA API.

Important APIs/types/functions: declares architecture DMA operations selection and includes generic noncoherent helpers as needed; it ties `arch_dma_alloc`, `dma_set_mask`, or cache synchronization behavior to PA-RISC IOMMU/direct-DMA capabilities.

Control flow: device drivers call the generic DMA API; generic code dispatches into PA-RISC direct or IOMMU mapping implementations based on device/bus state.

State and persistence: mapping state lives in IOMMU page directories or direct DMA masks outside this header. Dependencies and integration: integrates with SBA/LBA PCI, cache alignment, and generic DMA mapping code.

Risks and test signals: wrong ops selection can cause devices to DMA to invalid or stale memory. Test with PCI DMA stress, high-memory buffers, coherent allocations, and streaming map/unmap checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
