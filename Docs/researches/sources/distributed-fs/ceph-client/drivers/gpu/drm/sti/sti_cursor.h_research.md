# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_cursor.h

Purpose: Provides the constructor declaration for the STI DRM cursor plane.

Important API: `sti_cursor_create(struct drm_device *drm_dev, struct device *dev, int desc, void __iomem *baseaddr, unsigned int possible_crtcs)` allocates/registers a cursor plane at a compositor register offset with a CRTC mask.

Control/state: The implementation owns all cursor-private state; the header only exposes a `struct drm_plane *` factory so the compositor can attach the cursor to a CRTC without knowing the CLUT/pixmap internals.

Dependencies/integration: Forward declares DRM and device types, keeping the compositor include light. The `desc` value is expected to be `STI_CURSOR` from `sti_plane.h`, though the header itself does not include that enum.

Risks/test signals: Constructor callers must provide a valid register base and possible-CRTC mask. Compile-time integration and KMS plane enumeration verify the contract.
