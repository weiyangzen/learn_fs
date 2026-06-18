<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-drv.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-drv.h

Purpose: Declares the aggregate i.MX8 DC DRM device, shared subdevice identification helper, KMS/CRTC/plane APIs, and subcomponent platform drivers.

Important APIs/types/functions: Defines `struct dc_drm_device`, `struct dc_subdev_info`, `to_dc_drm_device()`, `dc_subdev_get_id()`, CRTC/KMS/plane init APIs, platform-driver externs for all DC subblocks, and post-bind hooks.

Control flow: Header only; `dc_subdev_get_id()` linearly matches a resource start against a static mapping table.

State and persistence behavior: `struct dc_drm_device` stores the runtime graph of all display and pixel-engine subblocks for two displays.

Dependencies: DRM device/encoder, Linux platform resources, and the `dc-de`, `dc-kms`, and `dc-pe` headers.

Integration points: Included by almost every DC subdriver to publish discovered component pointers into the aggregate DRM object.

Risks: The aggregate arrays encode hardware topology and are not null-protected at most use sites. `dc_subdev_get_id()` couples driver logic to physical address maps.

Test signals: Build coverage plus probe on full device tree with all component arrays populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-drv.h -->
