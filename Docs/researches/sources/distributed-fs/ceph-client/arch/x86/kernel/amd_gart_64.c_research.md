# sources/distributed-fs/ceph-client/arch/x86/kernel/amd_gart_64.c

## Purpose
`amd_gart_64.c` implements the legacy AMD64 GART aperture as a DMA remapping IOMMU for PCI devices, mainly to support devices with limited DMA masks on systems with memory above 4 GiB. It allocates/remaps aperture pages, manages the GART allocation bitmap, installs DMA map operations, flushes GART TLBs through AMD northbridge helpers, and restores hardware state on resume.

## Important APIs, Types, and Functions
- Global remap state: `iommu_bus_base`, `iommu_size`, `iommu_pages`, `iommu_gatt_base`, `iommu_gart_bitmap`, `next_bit`, `need_flush`, `gart_unmapped_entry`, and `iommu_fullflush`.
- Allocation/flush helpers: `alloc_iommu()`, `free_iommu()`, `flush_gart()`, `iommu_full()`, `need_iommu()`, and `nonforced_iommu()`.
- DMA ops: `gart_map_phys()`, `gart_unmap_phys()`, `gart_map_sg()`, `gart_unmap_sg()`, `gart_alloc_coherent()`, and `gart_free_coherent()`.
- Scatter-gather helpers: `dma_map_area()`, `dma_map_sg_nonforce()`, `__dma_map_cont()`, and `dma_map_cont()`.
- Aperture/GATT setup: `check_iommu_size()`, `read_aperture()`, `enable_gart_translations()`, `init_amd_gatt()`, and `gart_iommu_init()`.
- Resume/shutdown: `set_up_gart_resume()`, `gart_fixup_northbridges()`, `gart_resume()`, `gart_syscore_ops`, and `gart_iommu_shutdown()`.
- Option parsing: `gart_parse_options()` handles size, fullflush, noagp, noaperture, force/allowed, and `memaper`.

## Control Flow
`gart_iommu_init()` runs when `aperture_64.c` detected a usable GART aperture and set `x86_init.iommu.iommu_init`. It checks AMD northbridge GART support, negotiates with the AGP AMD64 driver or creates a private GATT, rejects no-IOMMU/low-memory/no-aperture cases, maps the aperture into kernel page tables if needed, sizes the IOMMU portion, allocates the bitmap, reserves the AGP aperture tail for DMA remapping, marks those virtual pages not-present, flushes CPU caches, enables GART translations, creates a scratch unmapped entry, installs `gart_dma_ops`, disables SWIOTLB, and registers shutdown handling.

DMA mapping flow checks whether direct DMA is possible. If not, it allocates GART pages from the bitmap, fills GATT entries with encoded physical addresses, sets the global `need_flush` flag when wrapping or fullflush policy applies, flushes the GART, and returns a bus address in the aperture. Unmap clears GATT entries to the scratch page and releases bitmap bits. SG mapping coalesces compatible page-aligned entries when `iommu_merge` allows it and falls back to per-entry non-forced mappings if the merged path overflows.

## State and Persistence Behavior
The GATT table and bitmap persist for the boot. Hardware GART aperture registers are programmed in each AMD northbridge and restored during syscore resume if `set_up_gart_resume()` was called by aperture setup. DMA mappings persist until explicit unmap. `need_flush` is shared global state protected by `iommu_bitmap_lock`. `dma_ops` is globally redirected to GART ops once initialized.

## Dependencies and Integration Points
The file depends on AGP AMD64 support, AMD northbridge helpers (`amd_nb_has_feature()`, `node_to_amd_nb()`, `amd_flush_garts()`), aperture setup in `aperture_64.c`, DMA mapping core, scatterlist APIs, MTRR/cache attribute helpers, syscore resume, PCI config access, SWIOTLB policy, and x86 platform IOMMU shutdown hooks.

## Risks
- GART supports only physical addresses below 1 TiB; higher mappings fail.
- Running out of aperture space can produce DMA failures or, in legacy fallback comments, possible garbage DMA if callers cannot recover.
- Cache aliasing around the aperture is delicate; the code marks pages not-present and performs `wbinvd()` before enabling translations.
- Lazy flushing historically triggered device bugs, hence `iommu_fullflush` defaults to true.
- AGP driver coexistence changes aperture ownership and shutdown behavior.

## Test Signals
- Boot AMD64 GART-capable systems with memory above 4 GiB and limited DMA-mask PCI devices.
- Exercise `iommu=fullflush`, `nofullflush`, `noagp`, `noaperture`, `force`, `allowed`, and `memaper` options.
- Run DMA API debug with scatter-gather and coherent allocations through GART.
- Suspend/resume and verify GART aperture registers and translations are restored.
- Kdump/kexec tests should verify aperture handling with `aperture_64.c` reservations.
