# sources/distributed-fs/ceph-client/include/drm/drm_modeset_helper.h

Purpose: declares small KMS helper entry points for common framebuffer metadata filling, legacy CRTC initialization, connector ordering, and mode-config suspend/resume.

Important APIs and types: `drm_helper_move_panel_connectors_to_head()` reorders panel connectors for user-visible preference. `drm_helper_mode_fill_fb_struct()` fills a `drm_framebuffer` from format info and an AddFB2 mode command. `drm_crtc_init()` initializes a CRTC with core function callbacks. `drm_mode_config_helper_suspend()` and `drm_mode_config_helper_resume()` implement common atomic suspend/resume state capture and restoration.

Control flow: drivers call these helpers from probe, framebuffer creation, or PM hooks. Framebuffer creation validates and resolves format/modifier metadata, then uses `drm_helper_mode_fill_fb_struct()` before `drm_framebuffer_init()`. Suspend captures the current atomic state into mode config; resume reapplies it.

State and persistence behavior: the header owns no state. Helpers mutate DRM object initialization fields, framebuffer metadata, connector list order, and `mode_config.suspend_state`.

Dependencies and integration points: forward-declares core KMS types and integrates with framebuffer UAPI parsing, CRTC setup, connector lists, and atomic suspend/resume helpers.

Risks: framebuffer metadata must preserve implied modifiers and plane offsets/pitches for GETFB2 correctness. Suspend/resume helpers assume atomic modeset support and valid mode-config state. Connector reordering affects userspace-visible enumeration and should be used only for intended panel priority.

Test signals: AddFB2 framebuffer metadata, CRTC init paths, panel connector ordering, atomic suspend/resume with active CRTCs, and cleanup after failed resume.
