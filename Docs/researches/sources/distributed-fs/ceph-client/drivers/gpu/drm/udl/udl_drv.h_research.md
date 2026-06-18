<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_drv.h

Purpose: Declares UDL driver constants, device/URB structures, helpers, and cross-file prototypes.

Important APIs/types/functions: `struct urb_node` connects an URB to its UDL device and free-list entry. `struct urb_list` tracks available URBs with a spinlock, waitqueue, counts, and buffer size. `struct udl_device` embeds `drm_device`, SKU pixel limit, primary plane, CRTC, encoder, connector, and URB pool. Prototypes cover modeset, EDID connector init, URB get/submit/sync/completion, init/drop, protocol rendering, and channel selection.

Control flow: Other UDL files share one concrete `struct udl_device`, with `to_udl()` converting from DRM device to driver container and `udl_to_usb_device()` resolving the USB device.

State and persistence: Describes all major UDL runtime state: DRM objects, pixel limit, and URB pool.

Dependencies and integration points: Includes Linux USB and DRM plane/CRTC/connector/framebuffer headers.

Risks and test signals: Structure lifetime spans USB disconnect and DRM unplug, so tests should exercise URB waiters, connector cleanup, and access through `to_udl()` after unplug paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_drv.h -->
