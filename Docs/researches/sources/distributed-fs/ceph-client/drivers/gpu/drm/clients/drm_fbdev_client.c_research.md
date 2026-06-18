# sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_fbdev_client.c

Purpose: implements fbdev emulation as a `drm_client_dev`, letting DRM drivers expose legacy framebuffer/fbcon support through the generic DRM client lifecycle.

Important APIs/functions: `drm_fbdev_client_setup()` chooses a color mode from the preferred DRM format or device preferred depth, warns if the DRM device is not registered or already has `fb_helper`, allocates `drm_fb_helper`, prepares it, initializes a DRM client named `fbdev`, and registers the client. Client callbacks free/unprepare and `kfree()` the helper, unregister fully initialized framebuffer info or release partial clients, restore fbdev mode, handle hotplug, and suspend/resume fbdev. `drm_fbdev_client_hotplug()` initializes the helper lazily, disables unused functions for non-atomic drivers, runs initial config, and tears down on failure.

Control flow: setup only registers the client; actual framebuffer allocation may happen later on hotplug, so it is safe when no connectors exist yet. Restore and suspend/resume delegate to fb helper APIs.

State and persistence: `struct drm_fb_helper` holds fbdev state, framebuffer info, and embedded client. `dev->fb_helper` is set by fb helper initialization. The framebuffer persists until client unregister/device unregister.

Dependencies and integration points: depends on DRM client, fb helper, CRTC helper for legacy unused-output disable, format helpers, and device registration lifecycle. Started by `drm_client_setup()` when fbdev is selected.

Risks: setup returns allocation/init errors, but top-level `drm_client_setup()` only logs them. Color-mode derivation still maps through legacy bpp/depth assumptions. Non-atomic drivers get extra disable-unused behavior; atomic drivers rely on normal client modesets. Partial initialization path must release the DRM client without unregistering nonexistent fb info.

Test signals: fbcon on DRM drivers, no-connectors-at-setup then hotplug retry, non-atomic and atomic drivers, suspend/resume blanking, forced restore, preferred format/depth combinations, and failure injection in helper init/initial config.
