# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_plane.c

Purpose: Implements OMAP DRM universal planes, atomic validation/update/disable, framebuffer pinning, overlay assignment, and plane properties.

Important APIs/types/functions: `struct omap_plane_state` extends `drm_plane_state` with main and right overlays. `struct omap_plane` stores the DISPC plane ID. Public functions are `omap_plane_init`, `omap_plane_install_properties`, and `is_omap_plane_dual_overlay`.

Control flow: `prepare_fb` pins the framebuffer after GEM helper preparation; cleanup unpins. Atomic check obtains global overlay state, validates scaling and CRTC bounds, detects need for scaling caps, rejects unsupported rotation, handles too-wide planes by requesting a right overlay, and assigns/reassigns hardware overlays when caps, format, or dual-overlay needs change. Atomic update builds `omap_overlay_info` from DRM state and framebuffer scanout data, then programs and enables one or two DISPC overlays. Atomic disable resets rotation/zpos defaults and updates old overlay state so unused hardware gets disabled.

State and persistence: Plane state carries overlay pointers across commits. Plane properties include rotation when DMM is present, zorder, alpha, blend mode, and optional YCbCr encoding/range. Framebuffer pin state is managed outside the plane in framebuffer/GEM code.

Dependencies and integration: Uses DRM atomic helpers, GEM prepare helpers, blend/color property helpers, framebuffer scanout helpers, overlay allocator, CRTC timing/channel helpers, and DISPC overlay setup/format capability APIs.

Risks: The max-size checks are coarse and final scaling limits may still fail in DISPC setup. Dual-overlay splitting depends on framebuffer scanout update generating matching left/right info and zorder+1. Negative CRTC positions and clipping are rejected rather than supported. Rotation requires DMM/TILER-backed framebuffer support.

Test signals: Atomic plane commits for primary and overlay planes, scaling up/down limits, YUV odd-width dual-overlay cases, rotation/reflection with DMM, alpha/blend/zpos properties, invisible-plane release, format reallocation, and DISPC setup failure cleanup.
