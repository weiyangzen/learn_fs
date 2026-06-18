# sources/distributed-fs/ceph-client/include/drm/drm_panel.h

## Purpose
`drm_panel.h` defines the DRM panel abstraction used by display drivers to model fixed display panels, their power sequencing, mode discovery, optional backlight integration, orientation, timings, debugfs hooks, and dependent follower devices.

## Important APIs, types, and functions
Important types are `struct drm_panel`, `struct drm_panel_funcs`, `struct drm_panel_follower`, and `struct drm_panel_follower_funcs`. Panel callbacks include `prepare`, `enable`, `disable`, `unprepare`, mandatory `get_modes`, optional `get_orientation`, `get_timings`, and `debugfs_init`. The public API includes `drm_panel_init`, `drm_panel_get`, `drm_panel_put`, `drm_panel_add`, `drm_panel_remove`, `drm_panel_prepare`, `drm_panel_unprepare`, `drm_panel_enable`, `drm_panel_disable`, `drm_panel_get_modes`, and `devm_drm_panel_alloc`. OF helpers and follower helpers are conditionally compiled.

## Control flow
A panel driver initializes or devm-allocates an embedded `drm_panel`, provides callback operations, registers it, and supplies display modes to a connector. Display pipelines call prepare before video transmission, enable after scanout is active, disable before stopping scanout, and unprepare for power-down. Backlight can be controlled automatically when panel backlight helpers attach it. Followers receive notifications around prepared/enabled and disabling/unpreparing transitions.

## State and persistence
Runtime state includes parent device, optional backlight, connector type, registry/follower list links, follower mutex, `prepare_prev_first`, `prepared`, `enabled`, container pointer, and kref. The state is not persistent; it tracks object lifetime and current power/visibility sequencing.

## Dependencies and integration points
This header integrates with device tree, DRM connectors, backlight class devices, display timings, panel orientation properties, debugfs, DSI/bridge pipelines, and the DRM panel registry. Config stubs return `-ENODEV`, false, or no-op values when panel support is absent.

## Risks and test signals
Risks include unbalanced prepare/enable transitions, backlight control duplicated by drivers and helpers, follower lifetime races, missing `get_modes`, incorrect connector type, module/refcount leaks, and OF lookup behavior when CONFIG_OF or CONFIG_DRM_PANEL is disabled. Test signals include panel probe/remove, repeated DPMS cycles, automatic backlight sequencing, follower add/remove and callback ordering, orientation/timing retrieval, DSI `prepare_prev_first`, and config-off stub builds.
