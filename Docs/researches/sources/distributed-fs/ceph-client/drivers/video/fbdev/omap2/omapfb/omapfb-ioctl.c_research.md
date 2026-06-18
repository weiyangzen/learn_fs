# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb-ioctl.c

## Purpose
`omapfb-ioctl.c` implements legacy OMAP framebuffer ioctls for plane setup/query, framebuffer memory resizing/query, manual update windows, update mode control, color keying, vsync/go waits, panel tests, memory readback, VRAM compatibility reporting, tear-sync toggling, and display information queries.

## Important APIs, types, and functions
The main dispatcher is `omapfb_ioctl`. Supporting functions include `get_mem_idx`, `get_mem_region`, `omapfb_setup_plane`, `omapfb_query_plane`, `omapfb_setup_mem`, `omapfb_query_mem`, `omapfb_update_window`, exported `omapfb_set_update_mode`/`omapfb_get_update_mode`, color-key helpers, `omapfb_memory_read`, `omapfb_get_ovl_colormode`, and `omapfb_wait_for_go`.

## Control Flow
The dispatcher copies user data into a union, routes by ioctl command, calls display/overlay/memory helpers, and copies results back. Plane setup locks old/new memory regions in id order, optionally switches framebuffer memory region, disables or configures the first overlay, applies the manager, enables the overlay, and rolls back on failure. Memory setup syncs the display, locks the current region, rejects mapped or enabled users, and reallocates framebuffer memory. Update mode toggles auto-update for manual-update displays under the fbdev lock. Color keying finds the first overlay with a manager and updates manager transparency state.

## State and Persistence
State changes affect `struct omapfb_info` region pointers, framebuffer fixed info, memory region size/type, display update mode, overlay info/enabled state, manager color-key state, and static `omapfb_color_keys[2]`. These are runtime-only and tied to fbdev/DSS lifetimes.

## Dependencies and Integration Points
The file depends on fbdev core structs, user-copy helpers, OMAPFB UAPI structs, omapfb internal memory/overlay helpers, VRFB headers, OMAP DSS display/overlay/manager callbacks, vmalloc, and update worker helpers in `omapfb-main.c`.

## Risks
This is a broad user-facing ioctl surface. Plane setup only uses the first overlay and rollback may not undo every hardware side effect after manager apply or enable failure. `omapfb_memory_read` validates width/height and buffer size but `w * h * 3` can overflow before comparison. Static color-key cache is sized for two managers, while newer SoCs can have more. Some compatibility responses such as VRAM info are fabricated.

## Test Signals
Exercise every ioctl with valid and invalid user pointers, plane enable/disable and memory-region switching, memory resize while mapped/enabled, update windows at boundaries, manual/auto update transitions, color key set/get on each manager, wait-for-vsync/go, memory readback size and overflow cases, overlay color mode enumeration, tear-sync support checks, and concurrent ioctl/sysfs reconfiguration.
