# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_framebuffer.c

Purpose: creates Komeda framebuffers, validates memory layout/alignment, computes pixel DMA addresses, and checks layer compatibility.

Important APIs/types/functions: `komeda_fb_create()`, `komeda_fb_check_src_coords()`, `komeda_fb_get_pixel_addr()`, `komeda_fb_is_layer_supported()`, plus framebuffer funcs destroy/create_handle. AFBC and non-AFBC size checks validate GEM objects, pitch alignment, payload offset, and plane sizes.

Control flow: DRM mode config calls `komeda_fb_create()`, which allocates `komeda_fb`, finds format caps, fills DRM framebuffer fields, runs AFBC or linear size checks, initializes DRM framebuffer, and records whether IOMMU virtual addresses are used. Later atomic validation uses source-coordinate and layer-support helpers; D71 update uses computed DMA addresses.

State and persistence: `komeda_fb` extends `drm_framebuffer` with selected format caps, `is_va`, aligned AFBC dimensions, AFBC minimum size, and AFBC payload offset. GEM object refs persist until framebuffer destroy.

Dependencies/integration: DRM GEM DMA/framebuffer helpers, overflow checking, Komeda format caps, device bus width, and D71 layer programming.

Risks: non-AFBC error paths can leak looked-up GEM refs if later plane validation fails before cleanup. `komeda_fb_get_pixel_addr()` returns a `dma_addr_t` but uses `-EINVAL` for invalid plane. AFBC size math is security-sensitive. Test signals: IGT framebuffer tests, malformed pitch/offset/size handles, AFBC tiled and non-tiled buffers, multi-plane YUV, IOMMU/no-IOMMU addressing, and kmemleak/refcount checks.
