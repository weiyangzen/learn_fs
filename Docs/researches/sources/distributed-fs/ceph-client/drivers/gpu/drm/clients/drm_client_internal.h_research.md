# sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_client_internal.h

Purpose: provides private declarations and stubs connecting `drm_client_setup.c` to optional fbdev and boot-log client implementations.

Important APIs/types: forward declares `struct drm_device` and `struct drm_format_info`. When `CONFIG_DRM_FBDEV_EMULATION` is enabled, declares `drm_fbdev_client_setup(struct drm_device *, const struct drm_format_info *)`; otherwise provides a no-op inline returning 0. When `CONFIG_DRM_CLIENT_LOG` is enabled, declares `drm_log_register(struct drm_device *)`; otherwise provides an empty inline.

Control flow: compile-time guards allow `drm_client_setup.c` to call optional clients without sprinkling callers with full implementation dependencies.

State and persistence: no state. It describes optional setup entry points.

Dependencies and integration points: consumed by DRM client library files and aligned with object selection in the clients Makefile.

Risks: stubs returning success can hide missing client support if callers assume setup had an effect. Declarations must match implementation signatures exactly because these functions are not public UAPI but are linked inside `drm_client_lib`.

Test signals: compile all config combinations and confirm `drm_client_setup()` behavior when defaults reference disabled clients.
