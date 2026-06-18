# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_plane.h

Purpose: Declares the OMAP plane creation and common property helpers, plus a query for dual-overlay plane state.

Important APIs/types/functions: `omap_plane_init`, `omap_plane_install_properties`, and `is_omap_plane_dual_overlay`.

Control flow: Driver setup calls `omap_plane_init` per DISPC plane; CRTC setup can call `omap_plane_install_properties` to share rotation/zorder properties; framebuffer/CRTC paths can query dual-overlay state.

State and persistence: No storage; declared functions manipulate DRM plane objects and private OMAP plane state.

Dependencies and integration: Consumed by OMAP driver, CRTC, framebuffer, and overlay paths. Relies on DRM plane and mode object types.

Risks: `is_omap_plane_dual_overlay` assumes the state is an OMAP plane state. Header forward declaration for `struct drm_plane_state` is implicit through including contexts.

Test signals: Build and atomic tests that call the dual-overlay query only for OMAP planes.
