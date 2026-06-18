# sources/distributed-fs/ceph-client/arch/arc/mm/dma.c

Purpose: supplies ARC architecture hooks for generic noncoherent DMA mapping.

Important APIs/functions: `arch_dma_prep_coherent()` evicts cache lines for pages becoming coherent DMA memory. `arch_sync_dma_for_device()` and `arch_sync_dma_for_cpu()` perform direction-specific cache maintenance. `arch_setup_dma_ops()` marks devices DMA-coherent when ARCv2 IOC is enabled and the device is declared coherent.

Control flow: prepare-coherent always writeback-invalidates the backing page. Device sync writes back for `DMA_TO_DEVICE`, invalidates for `DMA_FROM_DEVICE`, and writeback-invalidates for bidirectional. CPU sync invalidates for inbound/bidirectional traffic to cover speculative CPU prefetch. Setup logs coherent/noncoherent mode and toggles `dev->dma_coherent` for IOC-backed devices.

State and persistence: modifies `dev->dma_coherent`; otherwise uses cache state and function pointers owned by `cache.c`.

Dependencies and integration: depends on `dma_cache_*()` from cache code, generic `dma-map-ops`, ARC IOC policy `ioc_enable`, and device tree coherent property passed as `coherent`.

Risks: wrong direction handling can expose stale data or drop dirty CPU data. IOC aperture limitations mean marking a device coherent is only safe when hardware truly snoops the relevant memory. Highmem constraints are coordinated in cache discovery.

Test signals: DMA API debug, network/storage DMA tests, coherent versus noncoherent device tree variants, bidirectional buffer tests, and highmem/IOC platform coverage.
