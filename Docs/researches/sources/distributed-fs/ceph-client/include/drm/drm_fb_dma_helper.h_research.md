# sources/distributed-fs/ceph-client/include/drm/drm_fb_dma_helper.h

Purpose: Declares helpers for using DMA-backed GEM objects as framebuffer scanout buffers, including address lookup, non-coherent synchronization, and scanout-buffer export.

Important APIs, types, and functions: Declares `drm_fb_dma_get_gem_obj()`, `drm_fb_dma_get_gem_addr()`, `drm_fb_dma_sync_non_coherent()`, and `drm_fb_dma_get_scanout_buffer()`. The helpers operate on DRM framebuffers, plane state, planes, DRM devices, DMA GEM objects, and scanout-buffer descriptors.

Control flow: Plane update paths retrieve the DMA GEM object for a framebuffer plane, compute the DMA address adjusted for framebuffer offsets and plane source state, optionally synchronize non-coherent mappings between old and new plane states, and provide scanout-buffer metadata to display helpers or bridges.

State and persistence: No independent state is stored. Helpers derive runtime DMA addresses and synchronization operations from framebuffer GEM objects and plane state.

Dependencies and integration points: Integrates with `drm_gem_dma_helper`, framebuffer objects, plane state, non-coherent DMA memory, and scanout helpers used by simple display drivers.

Risks and test signals: Risks include wrong plane index handling, offset/source coordinate miscalculation, cache coherency bugs on non-coherent platforms, and exporting scanout buffers unsupported by hardware. Test multi-plane framebuffers, nonzero offsets, panning/source rectangles, imported DMA buffers, non-coherent CPU writes, and scanout-buffer handoff to display pipelines.
