# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_conn.c

## Purpose

`xen_drm_front_conn.c` implements virtual DRM connector support and advertises the framebuffer formats accepted by the Xen PV display frontend.

## Important APIs, Types, And Functions

Public APIs are `xen_drm_front_conn_init()` and `xen_drm_front_conn_get_formats()`. It supports RGB565, RGB888, XRGB/ARGB8888, XRGB/ARGB4444, XRGB/ARGB1555, and YUYV. Connector callbacks are `connector_detect()` and `connector_get_modes()`.

## Control Flow

Connector initialization installs helper funcs, marks the pipeline connected, enables connect/disconnect polling, and creates a `DRM_MODE_CONNECTOR_VIRTUAL`. Mode enumeration synthesizes one preferred 60 Hz mode from the backend-provided width and height with zero porch/sync fields. Detection reports disconnected after DRM unplug, otherwise follows `pipeline->conn_connected`.

## State And Persistence Behavior

Connection state is `pipeline->conn_connected`; fixed dimensions are stored in the pipeline by KMS setup. No EDID or persistent mode database exists.

## Dependencies And Integration Points

It depends on DRM atomic connector helpers, fourcc definitions, probe helpers, videomode conversion, and the Xen KMS pipeline struct. KMS uses the format list for simple display pipe initialization.

## Risks And Test Signals

Risks include simplistic timing generation, fixed 60 Hz behavior, no EDID, and connector status being used as an error signal after backend failures. Test connector polling, mode list dimensions, unplug behavior, and format acceptance/rejection in framebuffer creation.
