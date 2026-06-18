## sources/distributed-fs/ceph-client/drivers/video/fbdev/macmodes.c

Purpose: `macmodes.c` is a small exported fbdev helper library that translates between legacy MacOS video mode/color mode numbers and Linux `fb_var_screeninfo`/`fb_videomode` structures. It also maps Macintosh monitor-sense values to default Mac mode IDs and lets Mac-specific users search a Mac mode database via `fb_find_mode()`.

Important APIs and functions: exported functions are `mac_vmode_to_var()`, `mac_var_to_vmode()`, `mac_map_monitor_sense()`, and `mac_find_mode()`. The file's core data is `mac_modedb[]`, ordered to match the named Mac timing comments, `mac_modes[]`, mapping VMODE constants to mode database entries, and `mac_monitors[]`, mapping monitor sense codes to VMODE constants with a catch-all fallback.

Control flow: `mac_vmode_to_var()` linearly finds a VMODE, clears the destination var, applies one of the supported CMODE layouts (8, 16/15-bit, or 32/24-bit), then copies timing fields from the selected `fb_videomode`. `mac_var_to_vmode()` infers CMODE from bits-per-pixel, searches the ordered mode map for matching or closest larger resolution/pixclock/vmode, and returns the chosen VMODE. `mac_map_monitor_sense()` is a simple lookup with a final default entry. `mac_find_mode()` switches to the Mac mode database only when the option string begins with `mac`; otherwise it delegates to the standard fbdev database.

State and persistence: all mode and monitor tables are immutable static data. The library has no mutable state, no hardware side effects, and no persistence beyond exported symbols available to linked/modules users.

Dependencies and integration points: it depends on Linux fbdev core structures and `fb_find_mode()`, and is included by Mac/PPC fbdev drivers through `macmodes.h`. `matroxfb_base.c` uses it on PowerMac builds to convert requested `vmode`/`cmode` or NVRAM-derived values into startup fb settings.

Risks: several interlaced modes are intentionally disabled because timings are unknown, but monitor-sense mappings still contain VMODE values for those modes; callers that pass them to `mac_vmode_to_var()` get `-EINVAL`. `mac_var_to_vmode()` relies on table ordering and has a suspicious inner-loop comparison against the earlier `mode->pixclock` rather than `clk_mode->pixclock`, so changes to ordering could alter matching behavior. The helper does no EDID validation.

Test signals: test by converting every defined non-disabled VMODE with CMODE_8/16/32 and back where possible, checking monitor-sense fallback behavior, and booting PowerMac fbdev users with `vmode:`/`cmode:` parameters. Edge tests should cover interlaced monitor sense values, mode strings with and without `mac` prefix, and var requests that exceed all known Mac modes.
