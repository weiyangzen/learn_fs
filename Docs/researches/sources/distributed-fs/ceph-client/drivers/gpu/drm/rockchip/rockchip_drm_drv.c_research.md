# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_drv.c

## Purpose
Implements the top-level Rockchip DRM platform driver. It registers optional subdrivers, matches display components, creates the DRM device, initializes mode config/GEM/IOMMU/vblank/polling, and coordinates bind/unbind/shutdown/suspend/resume for the display subsystem.

## Important APIs, Types, And Functions
Public helper APIs include `rockchip_drm_dma_attach_device()`, `rockchip_drm_dma_detach_device()`, `rockchip_drm_dma_init_device()`, `rockchip_drm_encoder_set_crtc_endpoint_id()`, and `rockchip_drm_endpoint_is_subdriver()`. Major internal functions include `rockchip_drm_bind()`, `rockchip_drm_unbind()`, IOMMU init/cleanup, component match construction, platform probe/remove/shutdown, and module init/fini.

## Control Flow
Module init builds the subdriver table according to enabled Kconfig symbols, registers them, then registers the master platform driver. Platform probe validates `ports`, builds a component match list with preferred VOP ordering and all registered subdriver devices, and registers the component master. Bind removes conflicting framebuffers, allocates DRM device/private data, initializes mode config, binds all subcomponents, initializes IOMMU, vblank and polling, registers DRM, and starts DRM clients. Unbind reverses registration, polling, atomic state, components, IOMMU, and DRM reference.

## State And Persistence
Persistent module state is `rockchip_sub_drivers[]` and count. Per-DRM private state includes IOMMU domain, aperture allocator, DMA device, and GEM address management. Device links are created during match construction and removed on teardown.

## Dependencies And Integration Points
Integrates with Linux component framework, OF graph, DRM core/client/fbdev/GEM DMA helpers, IOMMU and ARM DMA-IOMMU compatibility, aperture helpers, and all Rockchip subdriver platform symbols.

## Risks
`MAX_ROCKCHIP_SUB_DRIVERS` must cover every optional subdriver. Component matching treats platform devices with no bound Rockchip driver as external bridges, so probe ordering matters. IOMMU attachment detaches legacy ARM DMA mappings and assumes all display components share a domain.

## Test Signals
Builds across Kconfig combinations, display-subsystem DT validation, preferred VOP ordering, component bind failure unwinding, IOMMU and non-IOMMU systems, framebuffer handoff removal, suspend/resume, shutdown atomic disable, and endpoint subdriver detection for bridges.
