# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/display.c

## Purpose

`display.c` implements OMAP DSS display registration, enumeration, refcounting, suspend/resume helpers, default display callbacks, and conversions between generic `videomode` and `omap_video_timings`. The complete 328-line source was read.

## Important APIs, Types, and Functions

Default callbacks are `omapdss_default_get_resolution()`, `omapdss_default_get_recommended_bpp()`, and `omapdss_default_get_timings()`. System-wide helpers are `dss_suspend_all_devices()`, `dss_resume_all_devices()`, and `dss_disable_all_devices()`. Registration/refcount APIs are `omapdss_register_display()`, `omapdss_unregister_display()`, `omap_dss_get_device()`, `omap_dss_put_device()`, `omap_dss_get_next_device()`, and `omap_dss_find_device()`. Timing conversion APIs are `videomode_to_omap_video_timings()` and `omap_video_timings_to_videomode()`.

## Control Flow

Panel drivers call `omapdss_register_display()` after filling an `omap_dss_device`; the function assigns a `displayN` alias using DT alias ID or a counter, reads an optional DT `label`, fills missing default callbacks, and appends the device to `panel_list` under `panel_list_mutex`. Enumeration gets a module/device reference for returned devices and drops the previous reference. Suspend disables active displays and marks them for resume; resume enables only devices marked `activate_after_resume`.

## State and Persistence Behavior

Global state is the display list, list mutex, and alias counter. Per-display state includes alias/name, callback pointers, panel timings, `state`, and `activate_after_resume`. There is no file-backed persistence; names and aliases live for the bound device lifetime.

## Dependencies and Integration Points

The file integrates with panel/output drivers, OF aliases and labels, module/device refcounting, DSS PM notifier in `core.c`, sysfs iteration in `display-sysfs.c`, and generic videomode helpers selected by Kconfig.

## Risks and Edge Cases

`omap_dss_get_next_device()` drops the previous device reference while holding the list mutex and warns if the previous device is no longer in the list. Mixed DT/non-DT assumptions are documented and can affect alias numbering. Default recommended BPP uses display type heuristics and may not match every panel. Suspend/resume ignores enable errors because helpers return 0.

## Test Signals

Signals include registration/unregistration ordering, DT alias/label naming, enumeration refcount correctness, suspend/resume of active and inactive displays, default BPP for all display types, timing conversion round trips, and concurrent display iteration during removal.
