# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_encoder.h

Purpose: Declares the OMAP DRM encoder creation API.

Important APIs/functions: `omap_encoder_init(struct drm_device *dev, struct omap_dss_device *output)` creates a DRM encoder bound to one DSS output. The header forward-declares DRM and DSS structures to keep dependencies minimal.

Control flow: `omap_drv.c` calls this during modeset pipeline construction before bridge attachment and connector/CRTC creation.

State and persistence: No state is stored in the header; encoder state is implemented in `omap_encoder.c`.

Dependencies/integration: Used by the main driver through `omap_drv.h`; integrates with DRM mode setting and DSS output objects.

Risks and test signals: Interface is small but central to pipeline construction. Build and modeset probe failures are the main validation signals.
