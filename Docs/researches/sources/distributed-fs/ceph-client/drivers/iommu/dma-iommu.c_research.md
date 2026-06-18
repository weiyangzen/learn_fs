# sources/distributed-fs/ceph-client/drivers/iommu/dma-iommu.c

## Purpose
Generic DMA API to IOMMU API glue layer. It prepares IOMMU domains for DMA mappings, owns IOVA allocation, reserved-region handling, MSI doorbell remapping, optional deferred IOVA freeing through flush queues, coherent/noncoherent allocation helpers, scatterlist mapping, SWIOTLB bounce integration, and exported `dma_iova_*` batching APIs.

## Important APIs, Types, And Functions
`struct iommu_dma_cookie` stores the IOVA domain, MSI page list, flush queues, flush counters, timer, flush-queue domain pointer, and options. `struct iommu_dma_msi_cookie` supports MSI-only unmanaged domains. Public functions include `iommu_get_dma_cookie()`, `iommu_get_msi_cookie()`, put functions, `iommu_setup_dma_ops()`, `iommu_dma_get_resv_regions()`, map/unmap/sync/allocation helpers, `iommu_dma_sw_msi()`, and `dma_iova_try_alloc/link/sync/unlink/destroy()`. Internal paths include flush queue management, domain initialization, IOVA allocation/free, SWIOTLB bounce mapping, scatterlist finalization/invalidation, and MSI page caching.

## Control Flow
DMA setup creates a cookie and initializes the IOVA domain on first device use, reserving PCI windows, firmware reserved regions, MSI regions, and choosing deferred-flush options. Map of a physical buffer checks deferred attach, alignment, DMA mask, SWIOTLB need, cache maintenance, IOVA allocation, and `iommu_map()`. Unmap resolves physical address for cache/SWIOTLB cleanup, unmaps IOMMU entries, syncs or queues TLB flushing, and frees IOVA. Scatterlist mapping reversibly rewrites SG offsets/lengths to page-granule-aligned form, handles P2PDMA bus addresses, allocates one contiguous IOVA span, maps the SG through the IOMMU, then compacts DMA-visible output segments. Allocations either build noncontiguous page arrays with remap/vmap support or contiguous/atomic mappings. MSI setup maps physical doorbell pages to cached IOVAs and writes the IOVA into MSI descriptors.

## State And Persistence
All state is runtime kernel memory. Cookies persist for domain lifetime; IOVA rcaches persist inside `iova_domain`; flush queues hold pending IOVA/page freelists until a domain-wide flush completes; MSI page lists cache doorbell mappings; `iommu_deferred_attach_enabled` is a static key enabled in kdump kernels; `iommu_dma_forcedac` is set by early param `iommu.forcedac`.

## Dependencies And Integration Points
The file integrates IOMMU core, DMA map ops, IOVA allocator, io page freelists, ACPI IORT and OF reserved regions, PCI host windows and P2PDMA, SWIOTLB, scatterlists, vmalloc/remap, cache maintenance hooks, MSI descriptors, tracepoints, kdump behavior, and generic page-table support (`iommupt_from_domain()`).

## Risks
Alignment and size calculations are security-sensitive for untrusted devices and SWIOTLB padding. Deferred flush queues rely on memory barriers and flush counters; ordering mistakes can free pages before IOTLB invalidation completes. Scatterlist in-place rewriting must be perfectly reversible on errors. DMA mask and 32-bit PCI workaround behavior can expose firmware/device bugs. MSI cookie allocation is monotonic for MSI-only domains. The `dma_iova_*` APIs require callers to sync and unlink correctly.

## Test Signals
Stress map/unmap with strict and DMA_FQ domains, per-CPU and single flush queues, untrusted PCI and kmalloc bounce paths, noncoherent cache maintenance, highmem/remap allocations, SG lists with unaligned entries and P2PDMA bus addresses, MSI remapping, reserved regions, deferred attach in kdump, forced DAC early param, and `dma_iova_*` partial failure cleanup.
