# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/omapfb_main.c

## Purpose
`omapfb_main.c` is the legacy OMAP1 framebuffer driver entrypoint. It binds platform device and panel registration, selects a controller, allocates framebuffer planes, exposes fbdev operations and OMAPFB ioctls, manages sysfs attributes, and handles suspend/resume/cleanup.

## Important APIs, Types, And Functions
- Module parameters/boot options set acceleration, VRAM sizes, virtual resolution, rotation, mirror, and manual-update default.
- `ctrl_init()`, `ctrl_cleanup()`, and `ctrl_change_mode()` mediate controller setup and plane reconfiguration.
- fbdev callbacks include open/release, blank, sync, check_var, set_par, pan_display, setcolreg/setcmap, ioctl, and optional mmap.
- OMAPFB ioctls handle mirror, sync, update mode, update window, plane setup/query, memory setup/query, color key, capabilities, and LCD/controller tests.
- Notifier APIs `omapfb_register_client()`, `omapfb_unregister_client()`, and `omapfb_notify_clients()` are exported.
- Probe flow is split between `omapfb_probe()`, `omapfb_register_panel()`, and `omapfb_do_probe()`.

## Control Flow
The platform driver registers a dummy `omapdss_dss` device for clocks, stores the platform device, and waits until a panel driver calls `omapfb_register_panel()`. Once both sides are present, `omapfb_do_probe()` validates platform data/resources, allocates `omapfb_device`, gets internal/external IRQs, selects the requested controller, initializes the panel, determines default virtual resolution and VRAM, initializes the controller, creates fb_info planes, sets DMA priority if configured, applies the first plane mode, enables the plane, sets auto/manual update mode, enables the panel, registers sysfs attributes, and registers each framebuffer.

`set_fb_var()` normalizes user mode requests against panel size, rotation, memory size, bpp/color mode, offsets, and timing fields. `ctrl_change_mode()` syncs pending controller work, computes the framebuffer offset from x/y offsets, calls controller `setup_plane()`, then applies optional rotate/scale. Manual updates validate/clamp windows and forward them only when the controller is in manual mode. Blank and PM use panel enable/disable plus controller suspend/resume.

## State And Persistence
The driver uses globals for the pending platform device, registered panel, and current fbdev singleton. Per-device state is in `omapfb_device`, with `rqueue_mutex` serializing controller operations and ioctl/fbdev transitions. Module parameters persist only for module lifetime.

## Dependencies And Integration Points
The file depends on Linux fbdev core, platform bus, sysfs, user-copy helpers, OMAP DMA priority APIs, OMAP1 CPU checks, private `omapfb.h`, and controller/panel registration. It is the primary consumer of `lcd_ctrl` and `lcd_panel` callbacks.

## Risks
Singleton global registration means only one panel/platform pairing is supported and `BUG_ON()` is used for duplicates. Some ioctl cases ignore return values, such as `OMAPFB_MIRROR` not assigning the helper result. Cleanup relies on numeric init-state fallthrough and assumes resources match that state. `set_fb_var()` adjusts user input in place and has many geometry/bpp edge cases. Manual update paths depend on controller-specific async completion. Remove has a FIXME for pending events.

## Test Signals
Signals include successful `/dev/fb*` registration, sysfs `caps_*`, `panel/name`, and `ctrl/name`, ioctl coverage for update mode/window/plane/memory, pan/display offset changes, blank/suspend/resume, first-pixel LCD test, and clean resource rollback on injected probe failures.
