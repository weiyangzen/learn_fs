# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fb.c

Purpose: Implements OMAP DRM framebuffer creation, validation, pin/unpin for scanout, dirty handling, format support, and scanout address generation for linear and TILER-rotated buffers.

Important APIs/functions: `omap_framebuffer_create()` resolves GEM handles and calls `omap_framebuffer_init()`. `omap_framebuffer_init()` validates supported formats, plane pitch consistency, pitch alignment, and BO sizes before initializing a DRM framebuffer. `omap_framebuffer_pin()` and `_unpin()` pin all GEM planes and cache DMA addresses with a pin count. `omap_framebuffer_update_scanout()` fills `omap_overlay_info` for DISPC, computing source/destination dimensions, tiled orientation, rotation, stride, NV12 UV address, and optional right-half info for dual-overlay scanout. `omap_framebuffer_dirty()` flushes all CRTCs for manual displays.

Control flow: Userspace/fbdev creates framebuffers from GEM BOs. Plane atomic update pins framebuffers and asks update_scanout for DISPC programming. Dirty callbacks trigger CRTC manual update work.

State and persistence: `struct omap_framebuffer` embeds DRM framebuffer, pin count, format pointer, per-plane DMA addresses, and a mutex. State lives until framebuffer destroy; pin state is transient.

Dependencies/integration: Depends on DRM framebuffer/GEM helpers, OMAP GEM pin/sync/tiled address APIs, TILER orientation constants, OMAP CRTC flush, and DISPC overlay info contracts.

Risks and test signals: Non-tiled rotations are ignored with warning. Dual-overlay split uses linear address helpers and has special YUV even-width adjustment. Debug describe appears to print `fb->offsets[n]` instead of `offsets[i]`, which is a likely diagnostic bug. Test supported RGB/YUV formats, NV12 multi-plane, tiled rotations/reflections, dual-overlay wide modes, dirty updates, BO size rejection, and pin count balance.
