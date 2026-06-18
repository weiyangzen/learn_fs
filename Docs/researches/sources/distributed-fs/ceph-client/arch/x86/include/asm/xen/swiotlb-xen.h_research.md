<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/swiotlb-xen.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/swiotlb-xen.h

Purpose: Declares x86 Xen SWIOTLB and contiguous-region helpers used to make DMA buffers suitable for devices when Xen memory layout or address-bit constraints require bounce or contiguous machine frames.

Important APIs/types/functions: `xen_swiotlb_fixup()`, `xen_create_contiguous_region()`, and `xen_destroy_contiguous_region()`.

Control flow: DMA/SWIOTLB setup calls the fixup helper after buffer allocation; device mapping code can request contiguous machine memory by physical start, order, and address-bit limit and later destroy the region.

State and persistence behavior: This header owns no state, but the declared functions mutate Xen memory reservations, DMA handles, and SWIOTLB slab backing memory.

Dependencies and integration points: Integrates with Xen memory management, DMA mapping, SWIOTLB, device address masks, and boot-time bounce-buffer setup.

Risks and test signals: Risks are leaked contiguous reservations, wrong DMA handle translation, and address-limit violations. Test PV/HVM DMA devices, highmem or encrypted-memory DMA paths, bounce-buffer allocation, contiguous region create/destroy failure injection, and IOMMU-disabled guests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/swiotlb-xen.h -->
