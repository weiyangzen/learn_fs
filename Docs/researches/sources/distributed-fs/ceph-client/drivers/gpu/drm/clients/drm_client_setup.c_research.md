# sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_client_setup.c

Purpose: exposes the public helpers drivers call after `drm_dev_register()` to start the selected in-kernel DRM client.

Important APIs/functions: module parameter `active` is stored in `drm_client_default` and defaults to `CONFIG_DRM_CLIENT_DEFAULT`. `drm_client_setup()` checks `DRIVER_MODESET`, then starts fbdev emulation when `active=fbdev`, starts the boot logger when `active=log`, warns on unknown non-empty values, and otherwise does nothing. `drm_client_setup_with_fourcc()` maps a 4CC to format info and delegates. `drm_client_setup_with_color_mode()` maps an old driver color mode to a 4CC via `drm_driver_color_mode_format()` and is documented as not preferred for new drivers. All three setup helpers are exported.

Control flow: selection is simple string comparison gated by compile-time config. fbdev setup return errors are warned and swallowed because the top-level setup helper is void.

State and persistence: `drm_client_default` is a read-only module parameter after init. Registered clients are owned by the DRM device and destroyed through `drm_dev_unregister()`.

Dependencies and integration points: depends on DRM core feature checks, format helpers, driver color mode mapping, `drm_fbdev_client_setup()`, and `drm_log_register()`. Drivers integrate by selecting `DRM_CLIENT_SELECTION` and calling one of these helpers after registering the device.

Risks: unknown runtime `active` values only warn and create no client, so fbcon/log output may disappear silently in automated boots. The setup helper is safe with no connectors and relies on client hotplug retry behavior. It warns if mode-setting is absent but otherwise cannot validate driver readiness.

Test signals: boot with `drm_client_lib.active=fbdev`, `log`, empty, and unknown; driver without `DRIVER_MODESET`; no-connector initial setup followed by hotplug; and wrapper functions with explicit formats/color modes.
