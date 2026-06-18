# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_modeset_helper.c

## Purpose
This file provides small auxiliary KMS helper functions that do not fit in the larger helper modules. It reorders built-in panel connectors, fills framebuffer metadata from userspace create requests, supports legacy CRTC initialization with a default primary plane, and wraps common atomic suspend/resume sequencing.

## Important APIs, Types, and Functions
The exported helpers are `drm_helper_move_panel_connectors_to_head()`, `drm_helper_mode_fill_fb_struct()`, `drm_crtc_init()`, `drm_mode_config_helper_suspend()`, and `drm_mode_config_helper_resume()`. Static support data includes `safe_modeset_formats` (`XRGB8888` and `ARGB8888`) and minimal `primary_plane_funcs` using non-atomic plane functions.

## Control Flow
`drm_helper_move_panel_connectors_to_head()` builds a temporary panel list, takes `connector_list_lock`, moves LVDS/eDP/DSI connectors into the temporary list, and splices them to the head of the connector list so userspace sees built-in panels first. `drm_helper_mode_fill_fb_struct()` copies width, height, format, pitches, offsets, modifier, and flags into a `drm_framebuffer`.

`drm_crtc_init()` allocates a simple primary plane with safe formats, marks `format_default`, and passes it to `drm_crtc_init_with_planes()`, cleaning up the plane on failure. Suspend disables polling if enabled, suspends DRM clients, calls `drm_atomic_helper_suspend()`, and rolls back clients/polling on failure. Resume requires a saved suspend state, calls `drm_atomic_helper_resume()`, clears suspend state, resumes clients, and re-enables polling if initialized.

## State and Persistence Behavior
Connector list order is persistently changed within `dev->mode_config.connector_list`. Framebuffer metadata is stored in the caller-provided framebuffer. Legacy CRTC init allocates and registers a primary plane whose lifetime becomes tied to normal plane/CRTC cleanup. Suspend stores the atomic state in `dev->mode_config.suspend_state` until resume consumes it.

## Dependencies and Integration Points
The file depends on DRM atomic helper suspend/resume, DRM client suspend/resume, probe helper polling, plane allocation, framebuffer formats, and CRTC initialization. It is used by older drivers that have not implemented explicit primary planes, by drivers wanting built-in panels to enumerate first, and by drivers using standard atomic KMS suspend/resume.

## Risks
Connector reordering changes userspace-visible connector order and must be done only when panel priority is desired. `drm_crtc_init()` encodes legacy assumptions: no primary plane scaling/repositioning/subpixel support and primary plane always covers the enabled CRTC; atomic drivers should not use it. Suspend rollback must keep polling/client state consistent if atomic suspend fails. Resume returns `-EINVAL` if suspend state is missing, which catches double-resume or unmatched paths.

## Test Signals
Signals include connector ordering with LVDS/eDP/DSI moved before external connectors, framebuffer fields matching `drm_mode_fb_cmd2`, legacy CRTC init creating a primary plane with safe formats and cleaning it on failure, suspend disabling polling and saving atomic state, failed suspend restoring clients/polling, resume restoring atomic state and clearing `suspend_state`, and no polling enable when polling was never initialized.
