# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panel.c

## Purpose

`drm_panel.c` implements the central DRM panel registry and panel lifecycle helpers. It lets panel drivers initialize, register, expose modes, attach optional backlights, and coordinate follower devices such as touchscreens that need to power sequence with the panel.

## Important APIs, Types, and Functions

- Global `panel_list` plus `panel_lock` form the registry used by firmware/device-tree lookup.
- `drm_panel_init()`, `drm_panel_add()`, and `drm_panel_remove()` initialize and register panel objects.
- `drm_panel_prepare()`, `drm_panel_unprepare()`, `drm_panel_enable()`, and `drm_panel_disable()` implement the standard power and visible-output lifecycle.
- `drm_panel_get_modes()` delegates mode discovery to panel ops.
- `drm_panel_get()` and `drm_panel_put()` kref device-managed panel allocations created by `__devm_drm_panel_alloc()`.
- `of_drm_find_panel()` and `of_drm_get_panel_orientation()` support Open Firmware lookup and rotation parsing.
- `drm_is_panel_follower()`, `drm_panel_add_follower()`, `drm_panel_remove_follower()`, and `devm_drm_panel_add_follower()` coordinate follower callbacks.
- `drm_panel_of_backlight()` resolves and stores a DT backlight phandle.

## Control Flow

Panel initialization sets list heads, follower lock, parent device, funcs, and connector type. Registration adds the panel to the global list under `panel_lock`. Prepare and enable are guarded by `panel->prepared` and `panel->enabled` flags. Prepare calls the panel's `prepare` op first, marks the panel prepared, then notifies followers via `panel_prepared`. Enable calls the panel's `enable` op, marks enabled, enables any associated backlight, then notifies followers via `panel_enabled`.

Disable and unprepare run the reverse order for follower notifications. Disable calls followers' `panel_disabling`, disables the backlight, calls panel `disable`, then clears `enabled`. Unprepare calls followers' `panel_unpreparing`, calls panel `unprepare`, then clears `prepared`. Warnings catch duplicate operations, especially shutdown-order bugs.

Follower registration resolves a `panel` firmware reference from the follower device. It gets a reference to the panel's device, links the follower under `follower_lock`, and immediately catches the follower up if the panel is already prepared or enabled. Removal calls disabling/unpreparing callbacks when needed, unlinks the follower, and drops the panel device reference.

## State and Persistence

State is in kernel memory: global registry membership, `prepared` and `enabled` booleans, a `backlight` pointer, panel reference count, and follower list. Device-managed panel allocations store the allocated container pointer and are freed through a devm action that calls `drm_panel_put()`. Backlight ownership is resolved through devm OF lookup and stored on the panel for lifecycle calls.

## Dependencies and Integration Points

The file integrates with panel driver `struct drm_panel_funcs`, `struct drm_connector` mode probing, backlight class devices, OF/fwnode firmware references, device properties, devm resource cleanup, and DRM bridge users indirectly through panel lookup APIs. Follower APIs are intended for devices whose power state must mirror panel state.

## Risks and Edge Cases

- `drm_panel_prepare()`, `enable()`, `disable()`, and `unprepare()` cannot report errors to callers; callback failures are logged and state changes may be skipped depending on where the failure occurs.
- Duplicate lifecycle calls are treated as warnings and no-ops.
- `of_drm_find_panel()` returns `-EPROBE_DEFER` when a device tree panel exists but is not registered yet.
- `drm_panel_remove_follower()` assumes `follower->panel` is valid and should only be used after successful add.
- Follower callbacks run under `follower_lock`, so they must avoid lock cycles with panel or device teardown paths.
- A missing or invalid connector type only warns in `drm_panel_init()`.

## Test Signals

Tests should cover add/remove lookup, deferred OF lookup, prepare/enable/disable/unprepare sequencing, duplicate lifecycle warnings, backlight enable/disable failure handling, follower add while panel is already active, follower removal while active, devm allocation/free, and OF rotation parsing for 0/90/180/270 plus invalid values.
