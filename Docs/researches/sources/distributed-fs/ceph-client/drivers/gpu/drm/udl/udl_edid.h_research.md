<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_edid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_edid.h

Purpose: Declares the UDL EDID helper API.

Important APIs/types/functions: Exposes `udl_probe_edid(struct udl_device *)` and `udl_edid_read(struct drm_connector *)` with forward declarations for DRM connector, DRM EDID, and UDL device.

Control flow: Included by modeset code to perform connector detection and mode enumeration.

State and persistence: No state.

Dependencies and integration points: Lightweight interface between `udl_modeset.c` and `udl_edid.c`.

Risks and test signals: Header must stay in sync with implementation signatures; compile coverage catches drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_edid.h -->
