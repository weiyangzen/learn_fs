<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/modedb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/modedb.c

## Purpose

`modedb.c` provides the fbdev standard video mode database and helpers for parsing mode strings, selecting valid modes, converting between `fb_var_screeninfo` and `fb_videomode`, maintaining per-framebuffer modelists, and choosing preferred display modes. The file was read as a complete 1209-line source.

## Important APIs, Types, and Functions

It defines static `modedb[]`, exported `vesa_modes[]`, and exported `dmt_modes[]`. Public APIs include `fb_find_mode`, conversion helpers, `fb_mode_is_equal`, `fb_find_best_mode`, `fb_find_nearest_mode`, `fb_match_mode`, `fb_add_videomode`, `fb_delete_videomode`, `fb_destroy_modelist`, `fb_videomode_to_modelist`, and `fb_find_best_display`.

## Control Flow

`fb_find_mode()` uses a caller database or built-in `modedb`, parses mode option suffixes for refresh, bpp, resolution, CVT/reduced blanking, interlace/progressive, and margins, then tries CVT, exact/near database matches, best-fit resolution, default mode, and finally all modes. List helpers compare exact timings, add non-duplicates, delete matching entries, and free list nodes.

## State and Persistence Behavior

Built-in arrays are static read-only. Dynamic modelists are caller-owned lists of `struct fb_modelist` allocated by `fb_add_videomode()` and freed by destroy/delete helpers. Conversion helpers mutate only caller-provided structs.

## Dependencies and Integration Points

It integrates with driver `fb_check_var`, EDID parsing in `fbmon.c`, CVT generation in `fbcvt.c`, sysfs modelist replacement, framebuffer registration, and fbcon resize/mode matching.

## Risks and Edge Cases

Mode string parsing is order-sensitive; malformed suffixes fall through to fallback modes. `fb_try_mode()` only calls driver validation if provided. Exact equality compares timings, sync, and vmode but not names/flags. Preferred display choice depends on EDID physical dimensions and preferred-detail flags.

## Test Signals

Test mode strings by name and resolution, `-bpp`, `@refresh`, `M`, `R`, `i`, `p`, and `m`, driver rejection, duplicate insertion, delete/destroy, nearest/best choices, EDID preferred selection, and conversion round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/modedb.c -->
