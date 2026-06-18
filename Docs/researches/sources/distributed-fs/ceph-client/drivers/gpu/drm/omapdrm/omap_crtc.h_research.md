# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_crtc.h

Purpose: Declares the OMAP DRM CRTC public interface used by the driver core, encoders, planes, IRQ code, and DSS manager wrappers.

Important APIs/functions: The header exposes `omap_crtc_timings()`, `omap_crtc_channel()`, `omap_crtc_init()`, `omap_crtc_wait_pending()`, IRQ handlers for error/vblank/framedone, and `omap_crtc_flush()`. Forward declarations keep dependencies light while allowing callers to pass DRM and DSS objects.

Control flow: Driver modeset setup calls `omap_crtc_init()`. Encoder/output code obtains timing/channel data or invokes manager wrappers that eventually reach CRTC functions. IRQ dispatch calls error/vblank/framedone functions. Framebuffer dirty and manual-update paths call `omap_crtc_flush()`.

State and persistence: No state is stored here; it declares access to state owned by `omap_crtc.c`.

Dependencies/integration: Depends only on basic Linux types and forward declarations for DRM, videomode, DSS channel, and OMAP pipeline structs. Integrated by `omap_drv.h`, IRQ code, plane/framebuffer code, and DSS output wrappers.

Risks and test signals: Header changes affect many modules. ABI is internal but must remain consistent with CRTC implementation. Compile coverage across fbdev, IRQ, plane, and DSS output configurations is the main signal.
