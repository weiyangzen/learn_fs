<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/dma.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/dma.c

Purpose: supplies LoongArch DMA initialization and cache-coherency policy hooks.
Important APIs and types: implements architecture DMA setup/init hooks and coherent DMA decision helpers.
Control flow: device and platform initialization call DMA setup paths to configure masks/coherency and hand off to generic DMA mapping code.
State and persistence: device DMA attributes persist in device structures; no major local global state.
Dependencies and integration: integrates with OF/ACPI device enumeration, generic DMA mapping, cache maintenance, and IOMMU/SWIOTLB policy.
Risks and test signals: wrong coherency assumptions corrupt I/O buffers. Signals include storage/network DMA tests, IOMMU/SWIOTLB boot, and non-coherent device validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/dma.c -->
